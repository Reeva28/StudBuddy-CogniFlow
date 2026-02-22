"""
Test authentication endpoint directly
"""
import requests

url = "http://localhost:8000/api/v1/auth/token"
data = {
    "username": "test@example.com",
    "password": "testpassword"
}

print(f"Testing: POST {url}")
print(f"Data: {data}")
print()

try:
    response = requests.post(url, data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'response'):
        print(f"Response text: {e.response.text}")
