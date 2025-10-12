import os
import random
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List

import requests


def get_live_weather_data(location: str) -> Dict[str, Any]:
    """
    Get live weather data from OpenWeather API
    """
    try:
        api_key = os.getenv("WEATHER_API_KEY", "2216351c156b1776734cb65627fe60bb")
        
        # OpenWeather API call
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": location,
            "appid": api_key,
            "units": "metric"  # Get temperature in Celsius
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract relevant weather information
            current_temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"] * 3.6  # Convert m/s to km/h
            weather_condition = data["weather"][0]["main"]
            weather_description = data["weather"][0]["description"]
            
            # Map OpenWeather conditions to our states
            condition_map = {
                "Clear": "Sunny",
                "Clouds": "Cloudy", 
                "Rain": "Rainy",
                "Drizzle": "Rainy",
                "Thunderstorm": "Storm",
                "Snow": "Rainy",
                "Mist": "Cloudy",
                "Fog": "Cloudy",
                "Haze": "Cloudy"
            }
            
            current_state = condition_map.get(weather_condition, "Sunny")
            
            return {
                "temp": round(current_temp, 1),
                "humidity": humidity,
                "wind_speed": round(wind_speed, 1),
                "condition": current_state,
                "description": weather_description,
                "city": data.get("name", location),
                "country": data.get("sys", {}).get("country", "IN"),
                "success": True,
                "source": "OpenWeather API"
            }
        else:
            print(f"OpenWeather API failed with status: {response.status_code}")
            return get_fallback_weather(location)
            
    except Exception as e:
        print(f"Error fetching live weather for {location}: {e}")
        return get_fallback_weather(location)

def get_fallback_weather(location: str) -> Dict[str, Any]:
    """Fallback weather data when API fails"""
    location_weather = {
        "delhi": {"temp": 32.5, "humidity": 45, "condition": "Sunny", "wind_speed": 12},
        "mumbai": {"temp": 29.8, "humidity": 78, "condition": "Cloudy", "wind_speed": 18},
        "chennai": {"temp": 34.2, "humidity": 65, "condition": "Sunny", "wind_speed": 15},
        "kolkata": {"temp": 31.7, "humidity": 72, "condition": "Rainy", "wind_speed": 20},
        "bangalore": {"temp": 27.3, "humidity": 58, "condition": "Sunny", "wind_speed": 10},
    }
    
    location_key = location.lower().split(',')[0].strip()
    default_weather = {"temp": 30.0, "humidity": 60, "condition": "Sunny", "wind_speed": 15}
    
    weather_data = location_weather.get(location_key, default_weather)
    weather_data["source"] = "Fallback Data"
    weather_data["success"] = False
    weather_data["city"] = location
    return weather_data

# Mock historical weather data generator
def generate_historical_weather_data(location: str, days: int = 90) -> List[Dict[str, Any]]:
    """Generate realistic historical weather data for Markov chain training"""
    historical_data = []
    current_date = datetime.now() - timedelta(days=days)
    
    # Location-specific patterns
    location_patterns = {
        "delhi": {"base_temp": 25, "rain_prob": 0.1, "seasonal_variation": 8},
        "mumbai": {"base_temp": 28, "rain_prob": 0.3, "seasonal_variation": 5},
        "chennai": {"base_temp": 30, "rain_prob": 0.2, "seasonal_variation": 4},
        "kolkata": {"base_temp": 27, "rain_prob": 0.25, "seasonal_variation": 6},
        "bangalore": {"base_temp": 24, "rain_prob": 0.15, "seasonal_variation": 3},
    }
    
    location_key = location.lower().split(',')[0].strip()
    pattern = location_patterns.get(location_key, {"base_temp": 25, "rain_prob": 0.15, "seasonal_variation": 5})
    
    states = ["Sunny", "Cloudy", "Rainy", "Storm"]
    
    # Start with realistic initial state based on location
    if pattern["rain_prob"] > 0.25:
        current_state = random.choices(states, weights=[0.4, 0.3, 0.25, 0.05])[0]
    else:
        current_state = random.choices(states, weights=[0.6, 0.25, 0.13, 0.02])[0]
    
    for day in range(days):
        # Seasonal temperature adjustment
        month = current_date.month
        if month in [12, 1, 2]:  # Winter
            temp_adjust = -pattern["seasonal_variation"]
        elif month in [3, 4, 5]:  # Summer
            temp_adjust = pattern["seasonal_variation"]
        else:
            temp_adjust = 0
        
        # Markov-like state transitions for generating training data
        if current_state == "Sunny":
            next_state_probs = {"Sunny": 0.6, "Cloudy": 0.3, "Rainy": 0.09, "Storm": 0.01}
        elif current_state == "Cloudy":
            next_state_probs = {"Sunny": 0.3, "Cloudy": 0.4, "Rainy": 0.28, "Storm": 0.02}
        elif current_state == "Rainy":
            next_state_probs = {"Sunny": 0.2, "Cloudy": 0.3, "Rainy": 0.45, "Storm": 0.05}
        else:  # Storm
            next_state_probs = {"Sunny": 0.1, "Cloudy": 0.2, "Rainy": 0.5, "Storm": 0.2}
        
        # Adjust probabilities based on location patterns
        next_state_probs["Rainy"] += pattern["rain_prob"] * 0.3
        next_state_probs["Sunny"] -= pattern["rain_prob"] * 0.2
        # Normalize probabilities
        total = sum(next_state_probs.values())
        next_state_probs = {k: v/total for k, v in next_state_probs.items()}
        
        next_state = random.choices(
            states,
            weights=[next_state_probs[state] for state in states]
        )[0]
        
        # Generate weather parameters
        if next_state == "Sunny":
            temp = pattern["base_temp"] + random.uniform(2, 8) + temp_adjust
            humidity = random.randint(30, 60)
            rainfall = 0
            wind_speed = random.uniform(5, 15)
        elif next_state == "Cloudy":
            temp = pattern["base_temp"] + random.uniform(-2, 3) + temp_adjust
            humidity = random.randint(50, 80)
            rainfall = 0
            wind_speed = random.uniform(8, 20)
        elif next_state == "Rainy":
            temp = pattern["base_temp"] + random.uniform(-5, 2) + temp_adjust
            humidity = random.randint(70, 95)
            rainfall = random.uniform(5, 25)
            wind_speed = random.uniform(12, 25)
        else:  # Storm
            temp = pattern["base_temp"] + random.uniform(-8, -2) + temp_adjust
            humidity = random.randint(80, 98)
            rainfall = random.uniform(30, 60)
            wind_speed = random.uniform(25, 45)
        
        historical_data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "weather": next_state,
            "temperature": round(temp, 1),
            "humidity": humidity,
            "wind_speed": round(wind_speed, 1),
            "rainfall": round(rainfall, 1) if next_state in ["Rainy", "Storm"] else 0
        })
        
        current_state = next_state
        current_date += timedelta(days=1)
    
    return historical_data

def build_markov_transition_matrix(historical_data: List[Dict]) -> Dict[str, Dict[str, float]]:
    """
    Build a true Markov transition matrix from historical weather data
    """
    states = ["Sunny", "Cloudy", "Rainy", "Storm"]
    
    # Initialize transition counts
    transition_counts = defaultdict(lambda: defaultdict(int))
    state_counts = defaultdict(int)
    
    # Count transitions from historical data
    for i in range(len(historical_data) - 1):
        current_state = historical_data[i]["weather"]
        next_state = historical_data[i + 1]["weather"]
        
        if current_state in states and next_state in states:
            transition_counts[current_state][next_state] += 1
            state_counts[current_state] += 1
    
    # Build probability matrix with Laplace smoothing to avoid zero probabilities
    transition_matrix = {}
    for current_state in states:
        transition_matrix[current_state] = {}
        total_transitions = state_counts[current_state]
        
        # Laplace smoothing parameter
        alpha = 0.1
        
        for next_state in states:
            count = transition_counts[current_state].get(next_state, 0) + alpha
            total_with_smoothing = total_transitions + (alpha * len(states))
            probability = count / total_with_smoothing
            transition_matrix[current_state][next_state] = round(probability, 3)
    
    # Normalize probabilities to ensure they sum to 1
    for current_state in states:
        total_prob = sum(transition_matrix[current_state].values())
        for next_state in states:
            transition_matrix[current_state][next_state] = round(
                transition_matrix[current_state][next_state] / total_prob, 3
            )
    
    return transition_matrix

def predict_weather(location: str, days: int = 3) -> Dict[str, Any]:
    """
    True Markov chain weather prediction using historical data
    """
    # Get current weather
    current_weather = get_live_weather_data(location)
    current_state = current_weather["condition"]
    
    # Generate or fetch historical data for this location
    historical_data = generate_historical_weather_data(location, days=90)
    
    # Build Markov transition matrix from historical data
    transition_matrix = build_markov_transition_matrix(historical_data)
    
    print(f"Markov Transition Matrix for {location}:")
    for state, transitions in transition_matrix.items():
        print(f"  {state}: {transitions}")
    
    states = list(transition_matrix.keys())
    forecast = []
    detailed_forecast = []
    alerts = []
    
    # Add current weather as day 0
    detailed_forecast.append({
        "day": 0,
        "weather": current_state,
        "temperature": current_weather["temp"],
        "humidity": current_weather["humidity"],
        "rainfall_mm": 0,
        "wind_speed": current_weather["wind_speed"],
        "is_current": True,
        "description": current_weather.get("description", current_state),
        "markov_probability": 1.0  # Current state has 100% probability
    })
    
    # Markov chain prediction
    current_markov_state = current_state
    
    for day in range(1, days + 1):
        # Get transition probabilities for current state from Markov matrix
        if current_markov_state in transition_matrix:
            probabilities = [
                transition_matrix[current_markov_state]["Sunny"],
                transition_matrix[current_markov_state]["Cloudy"],
                transition_matrix[current_markov_state]["Rainy"],
                transition_matrix[current_markov_state]["Storm"]
            ]
        else:
            # Fallback if state not in matrix
            probabilities = [0.25, 0.25, 0.25, 0.25]
        
        # Use Markov chain to determine next state
        next_state = random.choices(states, weights=probabilities)[0]
        next_probability = probabilities[states.index(next_state)]
        
        # Calculate realistic parameters based on historical patterns for this state
        state_historical_data = [d for d in historical_data if d["weather"] == next_state]
        
        if state_historical_data:
            # Use historical averages for this state
            avg_temp = sum(d["temperature"] for d in state_historical_data) / len(state_historical_data)
            avg_humidity = sum(d["humidity"] for d in state_historical_data) / len(state_historical_data)
            avg_wind = sum(d["wind_speed"] for d in state_historical_data) / len(state_historical_data)
            avg_rainfall = sum(d.get("rainfall", 0) for d in state_historical_data) / len(state_historical_data)
            
            # Add some variation
            temp = avg_temp + random.uniform(-3, 3)
            humidity = max(30, min(98, avg_humidity + random.uniform(-10, 10)))
            wind_speed = max(0, avg_wind + random.uniform(-5, 5))
            rainfall = max(0, avg_rainfall + random.uniform(-5, 5)) if next_state in ["Rainy", "Storm"] else 0
        else:
            # Fallback calculations
            if next_state == "Sunny":
                temp = current_weather["temp"] + random.uniform(-2, 5)
                humidity = max(30, current_weather["humidity"] - random.uniform(5, 25))
                rainfall = 0
                wind_speed = random.uniform(5, 15)
            elif next_state == "Cloudy":
                temp = current_weather["temp"] + random.uniform(-3, 2)
                humidity = current_weather["humidity"] + random.uniform(0, 20)
                rainfall = 0
                wind_speed = random.uniform(8, 20)
            elif next_state == "Rainy":
                temp = current_weather["temp"] - random.uniform(2, 8)
                humidity = min(95, current_weather["humidity"] + random.uniform(15, 30))
                rainfall = random.uniform(5, 35)
                wind_speed = random.uniform(12, 25)
            else:  # Storm
                temp = current_weather["temp"] - random.uniform(4, 10)
                humidity = min(98, current_weather["humidity"] + random.uniform(20, 35))
                rainfall = random.uniform(30, 80)
                wind_speed = random.uniform(25, 45)
        
        forecast.append(next_state)
        detailed_forecast.append({
            "day": day,
            "weather": next_state,
            "temperature": round(temp, 1),
            "humidity": round(humidity),
            "rainfall_mm": round(rainfall, 1),
            "wind_speed": round(wind_speed, 1),
            "is_current": False,
            "description": next_state.lower(),
            "markov_probability": round(next_probability, 3),
            "transition_from": current_markov_state
        })
        
        # Generate alerts
        if next_state == "Storm":
            alerts.append({
                "day": day,
                "type": "warning",
                "alert": "⚠️ Severe Storm Warning",
                "message": f"High winds ({wind_speed} km/h) and heavy rain ({rainfall:.1f}mm) expected.",
                "severity": "high",
                "action": "Harvest mature crops, reinforce structures, secure equipment",
                "crop_impact": "High risk of physical damage to crops"
            })
        elif next_state == "Rainy" and rainfall > 25:
            alerts.append({
                "day": day,
                "type": "alert", 
                "alert": "🌧️ Heavy Rainfall Alert",
                "message": f"Expected rainfall: {rainfall:.1f}mm. Ensure proper drainage.",
                "severity": "medium",
                "action": "Clear drainage channels, postpone irrigation, protect low-lying areas",
                "crop_impact": "Risk of waterlogging in poorly drained fields"
            })
        elif temp > 35:
            alerts.append({
                "day": day,
                "type": "info",
                "alert": "🔥 High Temperature Alert",
                "message": f"Temperature: {temp:.1f}°C. Risk of heat stress.",
                "severity": "medium",
                "action": "Increase irrigation frequency, provide shade for sensitive crops",
                "crop_impact": "Potential for heat stress in vegetables and flowers"
            })
        elif temp < 15:
            alerts.append({
                "day": day,
                "type": "info",
                "alert": "❄️ Low Temperature Alert", 
                "message": f"Temperature: {temp:.1f}°C. Protect sensitive crops.",
                "severity": "low",
                "action": "Cover sensitive plants, reduce irrigation, use frost protection",
                "crop_impact": "Risk of cold damage to tropical crops"
            })
        
        # Update Markov state for next iteration
        current_markov_state = next_state
    
    # Calculate summary
    forecast_days = detailed_forecast[1:]
    total_rainfall = sum(day["rainfall_mm"] for day in forecast_days)
    rainy_days = len([day for day in forecast_days if day["rainfall_mm"] > 0])
    avg_temperature = sum(day["temperature"] for day in forecast_days) / len(forecast_days)
    
    return {
        "location": location,
        "current_weather": current_weather,
        "forecast": forecast,
        "detailed_forecast": detailed_forecast,
        "alerts": alerts,
        "markov_chain": {
            "transition_matrix": transition_matrix,
            "historical_data_points": len(historical_data),
            "prediction_method": "True Markov Chain"
        },
        "summary": {
            "current_temperature": current_weather["temp"],
            "current_humidity": current_weather["humidity"],
            "avg_forecast_temperature": round(avg_temperature, 1),
            "total_rainfall": round(total_rainfall, 1),
            "rainy_days": rainy_days
        },
        "data_source": current_weather.get("source", "Live Weather Data + Markov Chain"),
        "api_success": current_weather.get("success", False),
        "last_updated": datetime.now().isoformat()
    }

# Export the functions that can be imported
__all__ = ['get_live_weather_data', 'predict_weather']