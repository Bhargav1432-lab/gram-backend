import os
import shutil
from pathlib import Path

from app import schemas
from app.database import get_db
from app.ml.crop_recommendation import (crop_recommender,
                                        get_optimization_suggestions)
from app.ml.disease_detection import (disease_model,
                                      get_treatment_recommendation)
from app.ml.disease_model import predict_crop_disease
from app.ml.price_model import predict_price
from app.ml.weather_model import get_live_weather_data, predict_weather
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/price-predict")
def price_predict(request: schemas.PricePredictRequest):
    try:
        result = predict_price(request.crop_name, request.current_state, request.steps)
        return {
            "forecast": result,
            "live_data": result.get("api_success", False),
            "data_source": result.get("data_source", "Unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Price prediction error: {str(e)}")

@router.post("/disease-predict")
def disease_predict(request: schemas.DiseasePredictRequest):
    try:
        result = predict_crop_disease(request.crop_name, request.temperature, request.humidity, request.soil_type)
        return {"disease_risk": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Disease prediction error: {str(e)}")

@router.post("/weather-alerts")
def weather_alerts(request: schemas.WeatherPredictRequest):
    try:
        result = predict_weather(request.location, request.days)
        return {
            "alerts": result,
            "live_data": result.get("api_success", False),
            "data_source": result.get("data_source", "Unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather prediction error: {str(e)}")

@router.post("/disease-detection-image")
async def disease_detection_image(
    file: UploadFile = File(...),
    crop_name: str = Form(...),
    temperature: float = Form(25.0),
    humidity: float = Form(60.0),
    soil_type: str = Form("Loamy")
):
    try:
        file_location = UPLOAD_DIR / f"{crop_name}_{file.filename}"
        
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Read image for ML processing
        image_bytes = await file.read()
        
        # Get image-based prediction
        image_prediction = disease_model.predict_disease(image_bytes, crop_name)
        
        # Get environmental risk assessment
        environmental_risk = predict_crop_disease(crop_name, temperature, humidity, soil_type)
        
        # Combine predictions
        combined_risk = "Low"
        if (image_prediction["primary_prediction"]["risk_level"] in ["Critical", "High"] or 
            environmental_risk["predicted_disease_risk"] in ["High", "Higher"]):
            combined_risk = "High"
        elif (image_prediction["primary_prediction"]["risk_level"] == "Medium" or 
              environmental_risk["predicted_disease_risk"] == "Medium"):
            combined_risk = "Medium"
        
        return {
            "filename": file.filename,
            "saved_path": str(file_location),
            "image_analysis": image_prediction,
            "environmental_analysis": environmental_risk,
            "combined_disease_risk": combined_risk,
            "recommendation": get_treatment_recommendation(
                image_prediction["primary_prediction"]["disease"],
                combined_risk,
                crop_name
            )
        }
    
    except Exception as e:
        return {"error": f"Error processing image: {str(e)}"}

@router.get("/crop-recommendations")
def get_crop_recommendations(
    location: str,
    soil_type: str,
    previous_crops: str = None,
    budget: float = 10000,
    farm_size: float = 1.0
):
    try:
        previous_crops_list = []
        if previous_crops:
            previous_crops_list = [crop.strip() for crop in previous_crops.split(",")]
        
        recommendations = crop_recommender.recommend_crops(
            location=location,
            soil_type=soil_type,
            previous_crops=previous_crops_list,
            budget=budget,
            farm_size=farm_size
        )
        
        # Get current weather for additional insights
        current_weather = get_live_weather_data(location)
        
        return {
            "recommendations": recommendations,
            "location_analysis": {
                "location": location,
                "current_season": crop_recommender.get_current_season(location),
                "current_weather": current_weather.get("condition", "Unknown"),
                "temperature": current_weather.get("temp", 25.0)
            },
            "optimization_suggestions": get_optimization_suggestions(soil_type, farm_size)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crop recommendation error: {str(e)}")

@router.get("/dashboard/{farmer_id}")
def dashboard(farmer_id: int, db: Session = Depends(get_db)):
    try:
        # Get farmer data
        from app import models
        farmer = db.query(models.Farmer).filter(models.Farmer.id == farmer_id).first()
        if not farmer:
            raise HTTPException(status_code=404, detail="Farmer not found")
        
        weather = predict_weather(farmer.location, 3)
        price = predict_price("Wheat", "Stable", 3)
        disease = predict_crop_disease("Wheat", 27.0, 65.0, farmer.soil_type)
        
        # Get crop recommendations
        crop_recommendations = crop_recommender.recommend_crops(
            farmer.location, 
            farmer.soil_type, 
            [], 
            10000, 
            1.0
        )
        
        return {
            "farmer_id": farmer_id,
            "location": farmer.location,
            "soil_type": farmer.soil_type,
            "weather_forecast": weather,
            "price_prediction": price,
            "disease_forecast": disease,
            "crop_recommendations": crop_recommendations,
            "overall_risk_score": calculate_overall_risk(weather, disease),
            "farming_suggestions": generate_farming_suggestions(weather, crop_recommendations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")

@router.get("/comprehensive-analysis/{farmer_id}")
def comprehensive_analysis(farmer_id: int, db: Session = Depends(get_db)):
    """Complete analysis combining all ML models"""
    try:
        # Get farmer data
        from app import models
        farmer = db.query(models.Farmer).filter(models.Farmer.id == farmer_id).first()
        if not farmer:
            raise HTTPException(status_code=404, detail="Farmer not found")
        
        # Get all predictions
        weather_pred = predict_weather(farmer.location, 7)
        price_pred = predict_price("Wheat", "Stable", 5)  # Default crop
        disease_risk = predict_crop_disease("Wheat", 25.0, 65.0, farmer.soil_type)
        crop_recommendations = crop_recommender.recommend_crops(
            farmer.location, 
            farmer.soil_type, 
            [], 
            10000, 
            1.0
        )
        
        return {
            "farmer_id": farmer_id,
            "location": farmer.location,
            "soil_type": farmer.soil_type,
            "comprehensive_analysis": {
                "weather_forecast": weather_pred,
                "price_predictions": price_pred,
                "disease_risk_assessment": disease_risk,
                "crop_recommendations": crop_recommendations,
                "overall_risk_score": calculate_overall_risk(weather_pred, disease_risk),
                "farming_suggestions": generate_farming_suggestions(weather_pred, crop_recommendations)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis error: {str(e)}")

def calculate_overall_risk(weather_pred, disease_risk):
    """Calculate overall farming risk score"""
    risk_factors = 0
    
    # Weather risks
    for alert in weather_pred.get("alerts", []):
        if alert["severity"] == "high":
            risk_factors += 2
        elif alert["severity"] == "medium":
            risk_factors += 1
    
    # Disease risks
    if disease_risk["predicted_disease_risk"] in ["High", "Higher"]:
        risk_factors += 2
    elif disease_risk["predicted_disease_risk"] == "Medium":
        risk_factors += 1
    
    if risk_factors >= 3:
        return "High"
    elif risk_factors >= 2:
        return "Medium"
    else:
        return "Low"

def generate_farming_suggestions(weather_pred, crop_recommendations):
    """Generate actionable farming suggestions"""
    suggestions = []
    
    # Weather-based suggestions
    for alert in weather_pred.get("alerts", []):
        if "rain" in alert["alert"].lower():
            suggestions.append("Prepare drainage systems for expected rainfall")
        if "storm" in alert["alert"].lower():
            suggestions.append("Secure farm structures and harvest ripe crops")
        if "temperature" in alert["alert"].lower():
            suggestions.append("Adjust irrigation schedule for temperature changes")
    
    # Crop-based suggestions
    if crop_recommendations:
        top_crop = crop_recommendations[0]
        suggestions.append(f"Consider planting {top_crop['crop']} for optimal returns")
    
    return suggestions[:5]  # Return top 5 suggestions