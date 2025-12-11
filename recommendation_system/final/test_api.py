"""
Simple test script for the API endpoints.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("\n" + "="*60)
    print("Testing Health Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
def test_customer_recommendations():
    """Test customer recommendations."""
    print("\n" + "="*60)
    print("Testing Customer Recommendations")
    print("="*60)
    
    payload = {
        "customer_id": 1,
        "top_k": 5
    }
    
    response = requests.post(
        f"{BASE_URL}/recommend/customer",
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\nRecommendations for Customer {data['customer_id']}:")
        for i, rec in enumerate(data['recommendations'], 1):
            print(f"{i}. {rec['name']} - ${rec['price']:.2f} (Score: {rec['score']:.4f})")
    else:
        print(f"Error: {response.text}")

def test_owner_recommendations():
    """Test owner recommendations."""
    print("\n" + "="*60)
    print("Testing Owner Recommendations")
    print("="*60)
    
    payload = {
        "owner_id": 1,
        "top_k": 5
    }
    
    response = requests.post(
        f"{BASE_URL}/recommend/raw_materials",
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\nRecommendations for Owner {data['owner_id']}:")
        for i, rec in enumerate(data['recommendations'], 1):
            print(f"{i}. {rec['name']} - ${rec['unit_cost']:.2f} (Score: {rec['score']:.4f})")
            print(f"   Reason: {rec['reason']}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    try:
        test_health()
        test_customer_recommendations()
        test_owner_recommendations()
        
        print("\n" + "="*60)
        print("All tests completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the API server.")
        print("Make sure the server is running with: uvicorn main:app --reload")
    except Exception as e:
        print(f"\nError: {e}")
