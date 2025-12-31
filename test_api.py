import requests
import json

# Test the API
try:
    response = requests.post(
        'http://localhost:8000/episodes/ai_daily_2025_11_18/query?mode=plain_english',
        json={'query': 'What is this episode about?'}
    )
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text}')
except Exception as e:
    print(f'Error: {e}')
