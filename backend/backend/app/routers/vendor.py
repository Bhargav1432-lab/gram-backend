from app import models, schemas
from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/all", response_model=list[schemas.VendorOut])
def get_all_vendors(db: Session = Depends(get_db)):
    vendors = db.query(models.Vendor).all()
    vendor_list = []
    for vendor in vendors:
        vendor_list.append(schemas.VendorOut(
            id=vendor.id,
            name=vendor.name,
            shop_name=vendor.product_type or "",
            location=vendor.location or "",
            contact=vendor.contact
        ))
    return vendor_list

@router.post("/", response_model=schemas.VendorOut)
def create_vendor(vendor: schemas.VendorCreate, db: Session = Depends(get_db)):
    new_vendor = models.Vendor(
        name=vendor.name,
        product_type=vendor.shop_name,
        location=vendor.location,
        contact=vendor.contact
    )
    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)
    return schemas.VendorOut(
        id=new_vendor.id,
        name=new_vendor.name,
        shop_name=new_vendor.product_type or "",
        location=new_vendor.location or "",
        contact=new_vendor.contact
    )

@router.get("/{vendor_id}", response_model=schemas.VendorOut)
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return schemas.VendorOut(
        id=vendor.id,
        name=vendor.name,
        shop_name=vendor.product_type or "",
        location=vendor.location or "",
        contact=vendor.contact
    )

@router.delete("/{vendor_id}")
def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    db.delete(vendor)
    db.commit()
    return {"message": "Vendor deleted successfully"}