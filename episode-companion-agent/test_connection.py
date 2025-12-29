import requests
import json

url = "http://localhost:8000/episodes/ai_daily_2025_11_18/query?mode=plain_english"
headers = {"Content-Type": "application/json"}
data = {"query": "What is the main topic?"}

try:
    print(f"Sending request to {url}...")
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
