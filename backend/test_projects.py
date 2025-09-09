import requests

# Test without header
response = requests.get("http://localhost:8001/api/v2/scope/projects")
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")

# Check if it's hitting the right endpoint
response2 = requests.get("http://localhost:8001/api/v2/health")
print(f"\nHealth check: {response2.text[:200]}")
