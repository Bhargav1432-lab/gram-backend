from app import database, models, schemas
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(tags=["Crops"])  # REMOVED prefix here

@router.post("/", response_model=schemas.CropOut)     
def add_crop(crop: schemas.CropCreate, db: Session = Depends(database.get_db)):
    db_crop = models.Crop(
        name=crop.name,
        soil_type=crop.soil_type,
        farmer_id=crop.farmer_id,
        price=crop.price_per_kg,
        season=crop.season,
        status="Healthy"
    )
    db.add(db_crop)
    db.commit()
    db.refresh(db_crop)
    return schemas.CropOut(
        id=db_crop.id,
        name=db_crop.name,
        soil_type=db_crop.soil_type,
        season=db_crop.season,
        price_per_kg=db_crop.price,
        farmer_id=db_crop.farmer_id
    )

@router.get("/", response_model=list[schemas.CropOut])
def get_all_crops(db: Session = Depends(database.get_db)):
    crops = db.query(models.Crop).all()
    crop_list = []
    for crop in crops:
        crop_list.append(schemas.CropOut(
            id=crop.id,
            name=crop.name,
            soil_type=crop.soil_type,
            season=crop.season,
            price_per_kg=crop.price,
            farmer_id=crop.farmer_id
        ))
    return crop_list

@router.get("/{crop_id}", response_model=schemas.CropOut)
def get_crop(crop_id: int, db: Session = Depends(database.get_db)):
    crop = db.query(models.Crop).filter(models.Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return schemas.CropOut(
        id=crop.id,
        name=crop.name,
        soil_type=crop.soil_type,
        season=crop.season,
        price_per_kg=crop.price,
        farmer_id=crop.farmer_id
    )

@router.put("/{crop_id}", response_model=schemas.CropOut)
def update_crop(crop_id: int, updated_crop: schemas.CropCreate, db: Session = Depends(database.get_db)):    
    crop = db.query(models.Crop).filter(models.Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    crop.name = updated_crop.name
    crop.soil_type = updated_crop.soil_type
    crop.price = updated_crop.price_per_kg
    crop.season = updated_crop.season

    db.commit()
    db.refresh(crop)
    return schemas.CropOut(
        id=crop.id,
        name=crop.name,
        soil_type=crop.soil_type,
        season=crop.season,
        price_per_kg=crop.price,
        farmer_id=crop.farmer_id
    )

@router.delete("/{crop_id}")
def delete_crop(crop_id: int, db: Session = Depends(database.get_db)):
    crop = db.query(models.Crop).filter(models.Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    db.delete(crop)
    db.commit()
    return {"message": "Crop deleted successfully"}