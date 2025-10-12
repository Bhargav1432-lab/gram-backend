import os
import random
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

import numpy as np
import requests


def get_live_crop_prices(crop_name: str) -> Dict[str, Any]:
    """
    Get live crop prices from Data.gov.in API
    """
    try:
        api_key = os.getenv("DATA_GOV_API_KEY", "579b464db66ec23bdd000001da2ea06ba07e499a467c30725e2a683f")
        
        # Map crop names to API commodity names
        crop_mapping = {
            "wheat": "Wheat",
            "rice": "Rice",
            "cotton": "Cotton", 
            "sugarcane": "Sugarcane",
            "groundnut": "Groundnut",
            "maize": "Maize",
            "paddy": "Paddy",
            "pulses": "Arhar"
        }
        
        api_crop = crop_mapping.get(crop_name.lower(), crop_name)
        
        # Data.gov.in API for agricultural prices
        url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        params = {
            "api-key": api_key,
            "format": "json",
            "filters[commodity]": api_crop,
            "limit": 10,
            "sort[timestamp]": "desc"
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            records = data.get("records", [])
            
            if records:
                # Get the latest price record
                latest_record = records[0]
                current_price = float(latest_record.get("modal_price", 0))
                market = latest_record.get("market", "Unknown")
                state = latest_record.get("state", "Unknown")
                
                # Calculate trend from recent records
                if len(records) > 1:
                    previous_price = float(records[1].get("modal_price", current_price))
                    change = current_price - previous_price
                    change_percent = (change / previous_price) * 100 if previous_price > 0 else 0
                    
                    if change_percent > 2:
                        trend = "increase"
                    elif change_percent < -2:
                        trend = "decrease"
                    else:
                        trend = "stable"
                else:
                    change_percent = 0
                    trend = "stable"
                
                return {
                    "current": current_price,
                    "trend": trend,
                    "change": round(change_percent, 2),
                    "market": market,
                    "state": state,
                    "source": "Data.gov.in",
                    "success": True,
                    "all_records": records  # Return all records for transition matrix
                }
        
        # Fallback to mock data if API fails
        print(f"API failed for {crop_name}, using fallback data")
        return get_fallback_prices(crop_name)
        
    except Exception as e:
        print(f"Error fetching live prices for {crop_name}: {e}")
        return get_fallback_prices(crop_name)


def get_fallback_prices(crop_name: str) -> Dict[str, Any]:
    """Fallback price data when API fails"""
    fallback_prices = {
        "wheat": {"current": 28.5, "trend": "increase", "change": 1.2},
        "rice": {"current": 42.3, "trend": "stable", "change": 0.3},
        "cotton": {"current": 68.7, "trend": "decrease", "change": -2.1},
        "sugarcane": {"current": 3.8, "trend": "increase", "change": 0.2},
        "groundnut": {"current": 58.9, "trend": "increase", "change": 3.4},
        "maize": {"current": 22.1, "trend": "stable", "change": 0.1},
        "paddy": {"current": 19.5, "trend": "decrease", "change": -0.8},
        "pulses": {"current": 85.2, "trend": "increase", "change": 4.7}
    }
    
    default_data = fallback_prices.get(crop_name.lower(), {"current": 30.0, "trend": "stable", "change": 0.0})
    default_data["source"] = "Fallback Data"
    default_data["success"] = False
    default_data["all_records"] = []  # Empty records for fallback
    return default_data


def calculate_price_state(price_change_percent: float) -> str:
    """Determine price state based on percentage change"""
    if price_change_percent > 2.0:
        return "Increase"
    elif price_change_percent < -2.0:
        return "Decrease"
    else:
        return "Stable"


def build_transition_matrix(records: List[Dict]) -> Dict[str, Dict[str, float]]:
    """
    Build a Markov transition matrix from historical price records
    """
    states = ["Increase", "Decrease", "Stable"]
    
    # Initialize transition counts
    transition_counts = {state: {target: 0 for target in states} for state in states}
    state_counts = {state: 0 for state in states}
    
    # Extract prices and calculate transitions
    prices = []
    for record in records:
        try:
            price = float(record.get('modal_price', 0))
            if price > 0:  # Valid price
                prices.append(price)
        except (ValueError, TypeError):
            continue
    
    # Calculate state transitions
    if len(prices) >= 2:
        for i in range(len(prices) - 1):
            current_price = prices[i]
            next_price = prices[i + 1]
            
            # Calculate percentage change
            if current_price > 0:
                change_percent = ((next_price - current_price) / current_price) * 100
                
                current_state = calculate_price_state(
                    ((prices[i-1] - prices[i]) / prices[i]) * 100 if i > 0 else 0
                )
                next_state = calculate_price_state(change_percent)
                
                transition_counts[current_state][next_state] += 1
                state_counts[current_state] += 1
    
    # Build probability matrix
    transition_matrix = {}
    for current_state in states:
        transition_matrix[current_state] = {}
        total_transitions = state_counts[current_state]
        
        if total_transitions > 0:
            # Calculate probabilities based on actual transitions
            for next_state in states:
                count = transition_counts[current_state][next_state]
                probability = count / total_transitions
                transition_matrix[current_state][next_state] = probability
        else:
            # Default probabilities if no data (shouldn't happen with real data)
            if current_state == "Increase":
                transition_matrix[current_state] = {"Increase": 0.4, "Stable": 0.4, "Decrease": 0.2}
            elif current_state == "Decrease":
                transition_matrix[current_state] = {"Increase": 0.2, "Stable": 0.4, "Decrease": 0.4}
            else:
                transition_matrix[current_state] = {"Increase": 0.3, "Stable": 0.4, "Decrease": 0.3}
    
    return transition_matrix


def calculate_volatility(records: List[Dict]) -> float:
    """Calculate price volatility from historical records"""
    prices = []
    for record in records:
        try:
            price = float(record.get('modal_price', 0))
            if price > 0:
                prices.append(price)
        except (ValueError, TypeError):
            continue
    
    if len(prices) < 2:
        return 0.1  # Default low volatility
    
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] > 0:
            returns.append((prices[i] - prices[i-1]) / prices[i-1])
    
    if returns:
        volatility = np.std(returns)
        return max(0.05, min(0.3, volatility))  # Cap volatility between 5% and 30%
    
    return 0.1


def predict_price(crop_name: str, current_state: str = "Stable", steps: int = 3) -> Dict[str, Any]:
    """
    Enhanced price prediction with REAL dynamic transition matrix from historical data
    """
    # Get live current prices from API with all records
    live_data = get_live_crop_prices(crop_name)
    current_price = live_data["current"]
    market_trend = live_data["trend"]
    market_change = live_data["change"]
    all_records = live_data.get("all_records", [])
    
    states = ["Increase", "Decrease", "Stable"]
    
    # Build dynamic transition matrix from actual historical data
    if len(all_records) >= 3:  # Need at least 3 records for meaningful transitions
        transition_matrix = build_transition_matrix(all_records)
        print(f"Dynamic transition matrix for {crop_name}: {transition_matrix}")
    else:
        # Fallback to trend-based matrix if insufficient data
        print(f"Insufficient historical data for {crop_name}, using trend-based matrix")
        if market_trend == "increase":
            transition_matrix = {
                "Increase": {"Increase": 0.6, "Stable": 0.25, "Decrease": 0.15},
                "Stable": {"Increase": 0.5, "Stable": 0.3, "Decrease": 0.2},
                "Decrease": {"Increase": 0.4, "Stable": 0.35, "Decrease": 0.25},
            }
        elif market_trend == "decrease":
            transition_matrix = {
                "Increase": {"Increase": 0.3, "Stable": 0.4, "Decrease": 0.3},
                "Stable": {"Increase": 0.25, "Stable": 0.35, "Decrease": 0.4},
                "Decrease": {"Increase": 0.2, "Stable": 0.3, "Decrease": 0.5},
            }
        else:
            transition_matrix = {
                "Increase": {"Increase": 0.4, "Stable": 0.4, "Decrease": 0.2},
                "Stable": {"Increase": 0.35, "Stable": 0.4, "Decrease": 0.25},
                "Decrease": {"Increase": 0.3, "Stable": 0.4, "Decrease": 0.3},
            }
    
    # Calculate market volatility for realistic price changes
    volatility = calculate_volatility(all_records)
    
    predictions = []
    price_predictions = [current_price]
    state_sequence = [current_state]
    
    # Use the actual current state based on recent market change
    actual_current_state = calculate_price_state(market_change)
    current_state = actual_current_state
    
    for step in range(steps):
        # Get transition probabilities for current state
        if current_state in transition_matrix:
            probabilities = [
                transition_matrix[current_state]["Increase"],
                transition_matrix[current_state]["Decrease"],
                transition_matrix[current_state]["Stable"]
            ]
        else:
            # Fallback if state not found
            probabilities = [0.33, 0.33, 0.34]
        
        # Determine next state based on actual transition probabilities
        next_state = random.choices(states, weights=probabilities)[0]
        
        # Calculate realistic price change based on state and volatility
        if next_state == "Increase":
            # Base increase with volatility adjustment
            base_change = random.uniform(0.005, 0.03) + (volatility * 0.5)
            # Adjust based on current trend momentum
            if market_trend == "increase":
                base_change += 0.01
            price_change = base_change
        elif next_state == "Decrease":
            # Base decrease with volatility adjustment
            base_change = random.uniform(-0.03, -0.005) - (volatility * 0.5)
            # Adjust based on current trend momentum
            if market_trend == "decrease":
                base_change -= 0.01
            price_change = base_change
        else:  # Stable
            # Small random fluctuations around zero
            price_change = random.uniform(-0.01, 0.01) * volatility
        
        # Apply price change
        new_price = price_predictions[-1] * (1 + price_change)
        price_predictions.append(round(new_price, 2))
        predictions.append(next_state)
        state_sequence.append(next_state)
        current_state = next_state
    
    # Calculate overall metrics
    total_price_change = price_predictions[-1] - current_price
    price_change_percent = (total_price_change / current_price) * 100 if current_price > 0 else 0
    
    # Determine overall trend and recommendation
    if price_change_percent > 8:
        overall_trend = "Strong Bullish"
        recommendation = "Excellent time to sell"
        confidence = "high"
    elif price_change_percent > 3:
        overall_trend = "Bullish"
        recommendation = "Good time to sell"
        confidence = "medium"
    elif price_change_percent < -5:
        overall_trend = "Bearish"
        recommendation = "Consider waiting to sell"
        confidence = "medium"
    elif price_change_percent < -2:
        overall_trend = "Mild Bearish"
        recommendation = "Hold current position"
        confidence = "low"
    else:
        overall_trend = "Neutral"
        recommendation = "Maintain current strategy"
        confidence = "low"
    
    # Calculate transition matrix statistics
    matrix_quality = "high" if len(all_records) >= 5 else "medium" if len(all_records) >= 3 else "low"
    
    return {
        "crop": crop_name,
        "current_price": current_price,
        "current_state": actual_current_state,
        "market_trend": market_trend,
        "recent_change_percent": market_change,
        "forecast_steps": steps,
        "predicted_trends": predictions,
        "predicted_prices": price_predictions[1:],
        "state_sequence": state_sequence,
        "overall_trend": overall_trend,
        "price_change_percent": round(price_change_percent, 2),
        "total_price_change": round(total_price_change, 2),
        "recommendation": recommendation,
        "confidence": confidence,
        "volatility": round(volatility * 100, 2),  # As percentage
        "transition_matrix": transition_matrix,
        "matrix_quality": matrix_quality,
        "historical_records_used": len(all_records),
        "data_source": live_data.get("source", "API Data"),
        "market": live_data.get("market", "National Average"),
        "api_success": live_data.get("success", False),
        "last_updated": datetime.now().isoformat()
    }


# Example usage and testing
if __name__ == "__main__":
    # Test the function
    result = predict_price("wheat", steps=5)
    print("Price Prediction Result:")
    print(f"Crop: {result['crop']}")
    print(f"Current Price: ₹{result['current_price']}/kg")
    print(f"Current State: {result['current_state']}")
    print(f"Market Trend: {result['market_trend']}")
    print(f"Historical Records Used: {result['historical_records_used']}")
    print(f"Transition Matrix Quality: {result['matrix_quality']}")
    print(f"Price Volatility: {result['volatility']}%")
    print("\nTransition Matrix:")
    for state, transitions in result['transition_matrix'].items():
        print(f"  {state}: {transitions}")
    print(f"\nPredicted Prices: {result['predicted_prices']}")
    print(f"Predicted Trends: {result['predicted_trends']}")
    print(f"Overall Trend: {result['overall_trend']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Confidence: {result['confidence']}")