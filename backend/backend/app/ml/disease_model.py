def predict_crop_disease(crop_name: str, temperature: float, humidity: float, soil_type: str):
    risk = "Low"
    if humidity > 80 and temperature > 30:
        risk = "High"
    elif 60 < humidity <= 80 and 25 < temperature <= 30:
        risk = "Medium"

    if "clay" in soil_type.lower():
        risk = "Higher"
    elif "sandy" in soil_type.lower() and risk == "High":
        risk = "Moderate"

    return {
        "crop": crop_name,
        "temperature": temperature,
        "humidity": humidity,
        "soil_type": soil_type,
        "predicted_disease_risk": risk,
        "suggested_action": "Spray antifungal" if risk in ["High", "Higher"] else "Normal monitoring"
    }