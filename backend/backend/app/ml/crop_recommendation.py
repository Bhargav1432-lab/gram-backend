import random
from datetime import datetime
from typing import Dict, List


class AdvancedCropRecommender:
    def __init__(self):
        self.crop_database = self._initialize_crop_database()
    
    def _initialize_crop_database(self):
        """Initialize comprehensive crop database"""
        return [
            {
                "name": "Wheat",
                "suitable_soil": ["loam", "clay loam", "silty loam"],
                "suitable_seasons": ["winter", "rabi"],
                "temperature_range": (10, 25),
                "rainfall_range": (50, 100),
                "ph_range": (6.0, 7.5),
                "water_requirements": "medium",
                "duration_days": 120,
                "market_demand": "high",
                "profit_margin": "medium",
                "risk_factor": "low"
            },
            {
                "name": "Rice",
                "suitable_soil": ["clay", "clay loam", "silty clay"],
                "suitable_seasons": ["monsoon", "kharif"],
                "temperature_range": (20, 35),
                "rainfall_range": (100, 200),
                "ph_range": (5.0, 6.5),
                "water_requirements": "high",
                "duration_days": 150,
                "market_demand": "high",
                "profit_margin": "medium",
                "risk_factor": "medium"
            },
            {
                "name": "Cotton",
                "suitable_soil": ["sandy loam", "loam", "clay loam"],
                "suitable_seasons": ["summer", "kharif"],
                "temperature_range": (25, 40),
                "rainfall_range": (50, 120),
                "ph_range": (6.0, 8.0),
                "water_requirements": "medium",
                "duration_days": 180,
                "market_demand": "high",
                "profit_margin": "high",
                "risk_factor": "high"
            },
            {
                "name": "Sugarcane",
                "suitable_soil": ["loam", "clay loam", "silty loam"],
                "suitable_seasons": ["monsoon", "winter"],
                "temperature_range": (20, 35),
                "rainfall_range": (150, 250),
                "ph_range": (6.5, 7.5),
                "water_requirements": "high",
                "duration_days": 300,
                "market_demand": "medium",
                "profit_margin": "medium",
                "risk_factor": "medium"
            },
            {
                "name": "Groundnut",
                "suitable_soil": ["sandy loam", "loam"],
                "suitable_seasons": ["summer", "kharif"],
                "temperature_range": (25, 35),
                "rainfall_range": (50, 125),
                "ph_range": (5.5, 7.0),
                "water_requirements": "low",
                "duration_days": 110,
                "market_demand": "high",
                "profit_margin": "high",
                "risk_factor": "low"
            },
            {
                "name": "Maize",
                "suitable_soil": ["sandy loam", "loam", "clay loam"],
                "suitable_seasons": ["summer", "kharif"],
                "temperature_range": (18, 32),
                "rainfall_range": (60, 110),
                "ph_range": (5.5, 7.5),
                "water_requirements": "medium",
                "duration_days": 100,
                "market_demand": "high",
                "profit_margin": "medium",
                "risk_factor": "low"
            },
            {
                "name": "Pulses",
                "suitable_soil": ["sandy loam", "loam"],
                "suitable_seasons": ["winter", "summer"],
                "temperature_range": (20, 30),
                "rainfall_range": (40, 80),
                "ph_range": (6.0, 7.5),
                "water_requirements": "low",
                "duration_days": 90,
                "market_demand": "high",
                "profit_margin": "medium",
                "risk_factor": "low"
            },
            {
                "name": "Soybean",
                "suitable_soil": ["loam", "clay loam"],
                "suitable_seasons": ["monsoon", "kharif"],
                "temperature_range": (20, 30),
                "rainfall_range": (60, 100),
                "ph_range": (6.0, 7.0),
                "water_requirements": "medium",
                "duration_days": 100,
                "market_demand": "high",
                "profit_margin": "high",
                "risk_factor": "low"
            },
            {
                "name": "Millets",
                "suitable_soil": ["sandy", "sandy loam"],
                "suitable_seasons": ["summer", "kharif"],
                "temperature_range": (25, 35),
                "rainfall_range": (30, 70),
                "ph_range": (6.0, 7.5),
                "water_requirements": "low",
                "duration_days": 85,
                "market_demand": "medium",
                "profit_margin": "medium",
                "risk_factor": "low"
            }
        ]
    
    def get_current_season(self, location: str) -> str:
        """Determine current season based on location and month"""
        month = datetime.now().month
        # Simplified season mapping for India
        if month in [6, 7, 8, 9]:
            return "monsoon"
        elif month in [10, 11, 12, 1]:
            return "winter"
        else:
            return "summer"
    
    def calculate_crop_score(self, crop: Dict, location: str, soil_type: str, 
                           previous_crops: List[str], budget: float) -> float:
        """Calculate suitability score for a crop"""
        score = 0
        
        # Soil compatibility (30% weight)
        if soil_type.lower() in [s.lower() for s in crop["suitable_soil"]]:
            score += 30
        
        # Season compatibility (25% weight)
        current_season = self.get_current_season(location)
        if current_season in crop["suitable_seasons"]:
            score += 25
        
        # Market factors (20% weight)
        if crop["market_demand"] == "high":
            score += 15
        elif crop["market_demand"] == "medium":
            score += 10
        
        if crop["profit_margin"] == "high":
            score += 5
        
        # Risk factors (15% weight)
        if crop["risk_factor"] == "low":
            score += 15
        elif crop["risk_factor"] == "medium":
            score += 10
        else:
            score += 5
        
        # Crop rotation (10% weight)
        if crop["name"] not in previous_crops:
            score += 10
        
        return score
    
    def recommend_crops(self, location: str, soil_type: str, previous_crops: List[str] = None,
                       budget: float = 10000, farm_size: float = 1.0) -> List[Dict]:
        """Generate advanced crop recommendations"""
        if previous_crops is None:
            previous_crops = []
        
        scored_crops = []
        
        for crop in self.crop_database:
            score = self.calculate_crop_score(crop, location, soil_type, previous_crops, budget)
            
            # Calculate estimated profit
            base_profit = {
                "high": 50000,
                "medium": 30000,
                "low": 15000
            }
            
            estimated_profit = base_profit[crop["profit_margin"]] * farm_size
            investment_required = estimated_profit * 0.3  # Rough estimate
            
            if investment_required <= budget:  # Within budget
                scored_crops.append({
                    "crop": crop["name"],
                    "score": round(score, 2),
                    "confidence": "High" if score > 70 else "Medium" if score > 50 else "Low",
                    "suitability_analysis": {
                        "soil_match": soil_type.lower() in [s.lower() for s in crop["suitable_soil"]],
                        "season_match": self.get_current_season(location) in crop["suitable_seasons"],
                        "market_demand": crop["market_demand"],
                        "risk_level": crop["risk_factor"]
                    },
                    "economic_analysis": {
                        "estimated_profit_per_hectare": estimated_profit,
                        "investment_required": round(investment_required, 2),
                        "return_on_investment": round((estimated_profit - investment_required) / investment_required * 100, 2),
                        "breakeven_period": f"{crop['duration_days']} days"
                    },
                    "growing_requirements": {
                        "duration_days": crop["duration_days"],
                        "water_needs": crop["water_requirements"],
                        "temperature_range": f"{crop['temperature_range'][0]}-{crop['temperature_range'][1]}°C",
                        "ideal_ph": f"{crop['ph_range'][0]}-{crop['ph_range'][1]}"
                    },
                    "recommendation_reasons": self.generate_recommendation_reasons(crop, score, soil_type, location)
                })
        
        # Sort by score and return top 5
        scored_crops.sort(key=lambda x: x["score"], reverse=True)
        return scored_crops[:5]
    
    def generate_recommendation_reasons(self, crop: Dict, score: float, soil_type: str, location: str) -> List[str]:
        """Generate specific reasons for recommendation"""
        reasons = []
        current_season = self.get_current_season(location)
        
        if soil_type.lower() in [s.lower() for s in crop["suitable_soil"]]:
            reasons.append(f"Ideal for {soil_type} soil type")
        
        if current_season in crop["suitable_seasons"]:
            reasons.append(f"Perfect for {current_season} season")
        
        if crop["market_demand"] == "high":
            reasons.append("High market demand with stable prices")
        
        if crop["risk_factor"] == "low":
            reasons.append("Low risk crop with reliable yield")
        
        if crop["profit_margin"] == "high":
            reasons.append("High profit potential")
        
        if crop["water_requirements"] == "low":
            reasons.append("Water-efficient crop")
        
        return reasons

# Initialize the recommender
crop_recommender = AdvancedCropRecommender()

def get_optimization_suggestions(soil_type: str, farm_size: float) -> List[str]:
    """Get soil-specific optimization suggestions"""
    suggestions = []
    
    if "clay" in soil_type.lower():
        suggestions.extend([
            "Add organic matter to improve drainage",
            "Consider raised beds for better root growth",
            "Use cover crops to enhance soil structure"
        ])
    
    if "sandy" in soil_type.lower():
        suggestions.extend([
            "Apply frequent but light irrigation",
            "Use mulch to retain moisture",
            "Add compost to improve water retention"
        ])
    
    if "loam" in soil_type.lower():
        suggestions.append("Maintain current soil management practices")
    
    if farm_size > 5:
        suggestions.append("Consider crop diversification to spread risk")
    elif farm_size < 2:
        suggestions.append("Focus on high-value crops for maximum profit")
    
    return suggestions