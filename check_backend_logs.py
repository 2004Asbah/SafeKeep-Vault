"""
Direct test of the registration endpoint to capture the actual error
"""
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from fastapi.testclient import TestClient
from main import app

def test_registration():
    client = TestClient(app)
    
    # Test registration with sample data
    test_data = {
        "ngo_name": "Test NGO",
        "email": "test@example.com",
        "password": "password123",
        "role": "admin"
    }
    
    print("Testing registration endpoint...")
    print(f"Request data: {test_data}")
    
    try:
        response = client.post("/auth/register", json=test_data)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 500:
            print("\n❌ 500 Error - Check backend console for detailed error")
        elif response.status_code == 200:
            print("\n✅ Registration successful!")
        else:
            print(f"\n⚠️ Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ Exception occurred: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_registration()
