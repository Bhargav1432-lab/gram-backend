from datetime import datetime

from app.database import Base
from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer,
                        String, Text)
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    user_type = Column(String)
    location = Column(String)
    phone = Column(String)
    soil_type = Column(String, nullable=True)
    farm_size = Column(String, nullable=True)
    experience = Column(Integer, nullable=True)
    business_type = Column(String, nullable=True)
    business_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Farmer(Base):
    __tablename__ = "farmers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String)
    soil_type = Column(String)
    contact = Column(String, unique=True)
    crops = relationship("Crop", back_populates="farmer")

class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    product_type = Column(String)
    location = Column(String)
    contact = Column(String, unique=True)
class Crop(Base):
    __tablename__ = "crops"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    soil_type = Column(String)
    farmer_id = Column(Integer, ForeignKey("farmers.id"))
    price = Column(Float)
    season = Column(String, default="All")  # Make sure this exists
    status = Column(String, default="Healthy")
    farmer = relationship("Farmer", back_populates="crops")
    
class MarketListing(Base):
    __tablename__ = "market_listings"
    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"))
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    price = Column(Float)
    quantity = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"))
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    crop_id = Column(Integer, ForeignKey("crops.id"))
    amount = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    message = Column(Text)
    type = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)