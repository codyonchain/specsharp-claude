"""Test Cost DNA without affecting production"""

import requests
import json
from app.core.security import create_access_token

def test_cost_dna():
    """Test the new Cost DNA endpoint"""
    
    # Create a test token
    test_token = create_access_token(data={"sub": "test@example.com"})
    
    test_data = {
        "square_footage": 50000,
        "occupancy_type": "healthcare",
        "location": "Manchester, NH",
        "project_classification": "addition",
        "description": "Hospital addition with surgical suite and imaging center",
        "total_cost": 28500000
    }
    
    headers = {
        "Authorization": f"Bearer {test_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/api/v1/cost-dna/generate",
            json=test_data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Cost DNA generated successfully!")
                print(json.dumps(data["cost_dna"], indent=2))
            else:
                print("❌ Failed to generate Cost DNA:", data.get("error"))
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Testing Cost DNA endpoint...")
    test_cost_dna()