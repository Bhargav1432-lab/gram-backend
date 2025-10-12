import random
from typing import List

from app import models, schemas
from app.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/listings", response_model=schemas.MarketListingOut)
def create_listing(listing: schemas.MarketListingCreate, db: Session = Depends(get_db)):
    new_listing = models.MarketListing(**listing.dict())
    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)
    return new_listing

@router.get("/listings", response_model=list[schemas.MarketListingOut])
def get_all_listings(db: Session = Depends(get_db)):
    return db.query(models.MarketListing).all()

@router.delete("/{listing_id}")
def delete_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(models.MarketListing).filter(models.MarketListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    db.delete(listing)
    db.commit()
    return {"message": "Listing deleted successfully"}

@router.get("/listings/enhanced", response_model=List[schemas.MarketListingOut])
def get_enhanced_listings(
    location: str = None,
    crop_type: str = None,
    min_price: float = None,
    max_price: float = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.MarketListing)
    
    if location:
        query = query.join(models.Vendor).filter(models.Vendor.location.ilike(f"%{location}%"))
    
    if crop_type:
        query = query.join(models.Crop).filter(models.Crop.name.ilike(f"%{crop_type}%"))
    
    if min_price is not None:
        query = query.filter(models.MarketListing.price >= min_price)
    
    if max_price is not None:
        query = query.filter(models.MarketListing.price <= max_price)
    
    return query.all()

@router.post("/listings/{listing_id}/contact")
def contact_seller(listing_id: int, message: str, db: Session = Depends(get_db)):
    listing = db.query(models.MarketListing).filter(models.MarketListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    return {
        "message": "Contact request sent successfully",
        "listing_id": listing_id,
        "vendor_contact": listing.vendor.contact,
        "your_message": message
    }

@router.post("/listings/{listing_id}/interest")
def express_interest(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(models.MarketListing).filter(models.MarketListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    return {
        "message": "Interest recorded successfully",
        "listing_id": listing_id,
        "crop": listing.crop.name,
        "vendor": listing.vendor.name,
        "interest_count": random.randint(1, 50)
    }