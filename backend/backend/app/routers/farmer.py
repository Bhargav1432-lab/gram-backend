from typing import List

from app import models, schemas
from app.database import get_db
from app.ml.crop_recommendation import crop_recommender
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()

# READ all farmers - MUST COME BEFORE /{farmer_id}
@router.get("/all", response_model=List[schemas.FarmerOut])
def get_all_farmers(db: Session = Depends(get_db)):
    farmers = db.query(models.Farmer).all()
    farmer_list = []
    for farmer in farmers:
        farmer_list.append(schemas.FarmerOut(
            id=farmer.id,
            name=farmer.name,
            location=farmer.location,
            soil_type=farmer.soil_type,
            contact=farmer.contact,
            phone="",
            crops_grown=[]
        ))
    return farmer_list

# CREATE farmer
@router.post("/", response_model=schemas.FarmerOut)
def create_farmer(farmer: schemas.FarmerCreate, db: Session = Depends(get_db)):
    new_farmer = models.Farmer(**farmer.dict())
    db.add(new_farmer)
    db.commit()
    db.refresh(new_farmer)
    return schemas.FarmerOut(
        id=new_farmer.id,
        name=new_farmer.name,
        location=new_farmer.location,
        soil_type=new_farmer.soil_type,
        contact=new_farmer.contact,
        phone="",
        crops_grown=[]
    )

# READ single farmer
@router.get("/{farmer_id}", response_model=schemas.FarmerOut)
def get_farmer(farmer_id: int, db: Session = Depends(get_db)):
    farmer = db.query(models.Farmer).filter(models.Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return schemas.FarmerOut(
        id=farmer.id,
        name=farmer.name,
        location=farmer.location,
        soil_type=farmer.soil_type,
        contact=farmer.contact,
        phone="",
        crops_grown=[]
    )

# DELETE farmer
@router.delete("/{farmer_id}")
def delete_farmer(farmer_id: int, db: Session = Depends(get_db)):
    farmer = db.query(models.Farmer).filter(models.Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    db.delete(farmer)
    db.commit()
    return {"message": "Farmer deleted successfully"}

# CROP SUGGESTIONS
@router.get("/{farmer_id}/recommendations")
def get_crop_recommendations(farmer_id: int, db: Session = Depends(get_db)):
    farmer = db.query(models.Farmer).filter(models.Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    recommendations = crop_recommender.recommend_crops(
        location=farmer.location,
        soil_type=farmer.soil_type,
        previous_crops=[],
        budget=10000,
        farm_size=1.0
    )

    return {
        "farmer_id": farmer.id,
        "farmer_name": farmer.name,
        "location": farmer.location,
        "soil_type": farmer.soil_type,
        "recommended_crops": recommendations
    }
    
    