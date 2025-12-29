from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock, patch

client = TestClient(app)

def test_orchestrator_api_flow():
    print("Starting Orchestrator API Verification...")
    
    # Mock the actual agent calls to avoid needing real Chroma/LLM
    with patch('orchestrator.Orchestrator.route_request') as mock_route:
        mock_route.return_value = {"answer": "Mocked Answer", "metadata": {"agent": "mock"}}
        
        # 1. Test /query with episode_id (Explicit)
        print("\n1. Testing /query with explicit episode_id...")
        response = client.post("/query", json={
            "query": "What is this about?",
            "user_id": "user_api_test"
        }, params={"episode_id": "test_episode_1"})
        
        assert response.status_code == 200
        print(f"Response: {response.json()}")
        mock_route.assert_called_with(user_id="user_api_test", text="What is this about?", episode_id="test_episode_1")
        
        # 2. Test /query without episode_id (Implicit/Chat)
        print("\n2. Testing /query without episode_id...")
        response = client.post("/query", json={
            "query": "General question",
            "user_id": "user_api_test"
        })
        
        assert response.status_code == 200
        print(f"Response: {response.json()}")
        mock_route.assert_called_with(user_id="user_api_test", text="General question", episode_id=None)

    print("\nVerification Complete: API endpoints are correctly wired to Orchestrator.")

if __name__ == "__main__":
    test_orchestrator_api_flow()
