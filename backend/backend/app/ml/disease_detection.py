import io
from typing import Dict, List

import numpy as np
from PIL import Image


class DiseaseDetectionModel:
    def __init__(self):
        self.class_names = [
            'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
            'Blueberry___healthy', 'Cherry___Powdery_mildew', 'Cherry___healthy',
            'Corn___Cercospora_leaf_spot', 'Corn___Common_rust', 'Corn___Northern_Leaf_Blight', 'Corn___healthy',
            'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy',
            'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy',
            'Pepper_bell___Bacterial_spot', 'Pepper_bell___healthy', 'Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy',
            'Raspberry___healthy', 'Soybean___healthy', 'Squash___Powdery_mildew',
            'Strawberry___Leaf_scorch', 'Strawberry___healthy', 'Tomato___Bacterial_spot', 'Tomato___Early_blight',
            'Tomato___Late_blight', 'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot',
            'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot',
            'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus', 'Tomato___healthy'
        ]
    
    def preprocess_image(self, image_bytes):
        """Preprocess image for model prediction"""
        image = Image.open(io.BytesIO(image_bytes))
        image = image.resize((224, 224))
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)
        return image_array
    
    def predict_disease(self, image_bytes, crop_type=None):
        """Predict disease from image with enhanced logic"""
        try:
            # Mock prediction (replace with actual trained model)
            processed_image = self.preprocess_image(image_bytes)
            
            # Mock prediction probabilities
            np.random.seed(hash(image_bytes) % 10000)
            probabilities = np.random.dirichlet(np.ones(len(self.class_names)), size=1)[0]
            
            # Filter by crop type if provided
            if crop_type:
                crop_specific_classes = [cls for cls in self.class_names if crop_type.lower() in cls.lower()]
                if crop_specific_classes:
                    # Enhance probabilities for crop-specific classes
                    for i, cls in enumerate(self.class_names):
                        if cls in crop_specific_classes:
                            probabilities[i] *= 2
                    probabilities = probabilities / np.sum(probabilities)  # Renormalize
            
            top_idx = np.argmax(probabilities)
            confidence = probabilities[top_idx]
            predicted_disease = self.class_names[top_idx]
            
            # Determine disease severity
            if 'healthy' in predicted_disease.lower():
                severity = "No Disease"
                risk_level = "Low"
                treatment = "No treatment needed. Maintain current practices."
            else:
                if confidence > 0.8:
                    severity = "High"
                    risk_level = "Critical"
                    treatment = "Immediate treatment required. Use recommended fungicides/pesticides."
                elif confidence > 0.6:
                    severity = "Medium"
                    risk_level = "High"
                    treatment = "Treatment recommended. Monitor closely."
                else:
                    severity = "Low"
                    risk_level = "Medium"
                    treatment = "Early stage detected. Preventive measures advised."
            
            # Get top 3 predictions
            top_indices = np.argsort(probabilities)[-3:][::-1]
            top_predictions = [
                {
                    "disease": self.class_names[i],
                    "confidence": round(float(probabilities[i]) * 100, 2),
                    "status": "Healthy" if 'healthy' in self.class_names[i].lower() else "Diseased"
                }
                for i in top_indices
            ]
            
            return {
                "primary_prediction": {
                    "disease": predicted_disease,
                    "confidence": round(confidence * 100, 2),
                    "severity": severity,
                    "risk_level": risk_level,
                    "treatment_recommendation": treatment
                },
                "alternative_predictions": top_predictions[1:],
                "is_healthy": 'healthy' in predicted_disease.lower(),
                "confidence_score": round(confidence * 100, 2)
            }
            
        except Exception as e:
            return {
                "error": f"Prediction failed: {str(e)}",
                "primary_prediction": {
                    "disease": "Unknown",
                    "confidence": 0,
                    "severity": "Unknown",
                    "risk_level": "Unknown",
                    "treatment_recommendation": "Consult agricultural expert"
                }
            }

# Initialize the model
disease_model = DiseaseDetectionModel()

def get_treatment_recommendation(disease, risk_level, crop_name):
    """Get specific treatment recommendations based on disease and risk"""
    treatments = {
        "High": {
            "general": "Immediate action required. Isolate affected plants, apply recommended fungicides.",
            "fungal": "Apply systemic fungicide. Improve air circulation. Remove infected leaves.",
            "bacterial": "Apply copper-based bactericide. Avoid overhead watering.",
            "viral": "Remove and destroy infected plants. Control insect vectors."
        },
        "Medium": {
            "general": "Monitor closely. Apply preventive treatments. Improve growing conditions.",
            "fungal": "Apply contact fungicide. Reduce humidity around plants.",
            "bacterial": "Apply biological controls. Improve sanitation.",
            "viral": "Remove severely infected plants. Use insect nets."
        },
        "Low": {
            "general": "Maintain good agricultural practices. Regular monitoring.",
            "fungal": "Ensure proper spacing. Water at base of plants.",
            "bacterial": "Use disease-free seeds. Practice crop rotation.",
            "viral": "Use resistant varieties. Control weeds."
        }
    }
    
    disease_type = "fungal" if any(x in disease.lower() for x in ['mildew', 'blight', 'rust', 'scab']) else \
                  "bacterial" if 'bacterial' in disease.lower() else \
                  "viral" if 'virus' in disease.lower() else "general"
    
    return treatments[risk_level][disease_type]