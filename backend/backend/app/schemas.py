from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr


# ---------------------- AUTH ----------------------
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    role: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: int
    role: str
    model_config = ConfigDict(from_attributes=True)

# ---------------------- FARMER ----------------------
class FarmerBase(BaseModel):
    name: str
    location: str
    soil_type: str
    contact: str

class FarmerCreate(FarmerBase):
    pass

class FarmerOut(BaseModel):
    id: int
    name: str
    location: str
    soil_type: str
    contact: str
    phone: str = ""
    crops_grown: List[str] = []
    
    model_config = ConfigDict(from_attributes=True, extra='ignore')

# ---------------------- VENDOR ----------------------
class VendorBase(BaseModel):
    name: str
    shop_name: str
    location: str
    contact: str

class VendorCreate(VendorBase):
    pass

class VendorOut(BaseModel):
    id: int
    name: str
    shop_name: str = ""
    location: str
    contact: str
    
    model_config = ConfigDict(from_attributes=True, extra='ignore')

# ---------------------- CROP ----------------------
class CropBase(BaseModel):
    name: str
    soil_type: str
    season: str = "All"
    price_per_kg: float = 0.0
    farmer_id: int

class CropCreate(CropBase):
    pass

class CropOut(BaseModel):
    id: int
    name: str
    soil_type: str
    season: str = "All"
    price_per_kg: float = 0.0
    farmer_id: int
    
    model_config = ConfigDict(from_attributes=True, extra='ignore')

# ---------------------- MARKET ----------------------
class MarketListingBase(BaseModel):
    crop_id: int
    vendor_id: int
    quantity: float
    price: float

class MarketListingCreate(MarketListingBase):
    pass

class MarketListingOut(BaseModel):
    id: int
    crop_id: int
    vendor_id: int
    price: float
    quantity: float
    timestamp: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True, extra='ignore')

# ---------------------- ANALYTICS & ML ----------------------
class PricePredictRequest(BaseModel):
    crop_name: str
    current_state: str = "Stable"
    steps: int = 3

class DiseasePredictRequest(BaseModel):
    crop_name: str
    temperature: float
    humidity: float
    soil_type: str

class WeatherPredictRequest(BaseModel):
    location: str
    days: int = 3

class CropRecommendationRequest(BaseModel):
    location: str
    soil_type: str
    previous_crops: Optional[str] = None
    budget: float = 10000
    farm_size: float = 1.0

class DiseaseDetectionRequest(BaseModel):
    crop_name: str
    temperature: float = 25.0
    humidity: float = 60.0
    soil_type: str = "Loamy"

# ---------------------- TRANSACTION ----------------------
class TransactionBase(BaseModel):
    farmer_id: int
    vendor_id: int
    crop_id: int
    quantity: float = 0.0
    total_price: float = 0.0

class TransactionCreate(TransactionBase):
    pass

class TransactionOut(BaseModel):
    id: int
    farmer_id: int
    vendor_id: int
    crop_id: int
    quantity: float = 0.0
    total_price: float = 0.0
    
    model_config = ConfigDict(from_attributes=True, extra='ignore')

# ---------------------- NOTIFICATIONS ----------------------
class NotificationBase(BaseModel):
    title: str
    message: str
    type: str

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationOut(NotificationBase):
    id: int
    is_read: bool = False
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True, extra='ignore')

class Token(BaseModel):
    access_token: str
    token_type: str

# ---------------------- ML RESPONSE SCHEMAS ----------------------
class DiseasePredictionResult(BaseModel):
    disease: str
    confidence: float
    severity: str
    risk_level: str
    treatment_recommendation: str

class CropRecommendationResult(BaseModel):
    crop: str
    score: float
    confidence: str
    suitability_analysis: dict
    economic_analysis: dict
    growing_requirements: dict
    recommendation_reasons: List[str]