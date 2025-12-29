from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

@patch("main.ingest_episode")
def test_ingest_endpoint(mock_ingest):
    mock_ingest.return_value = {"episode_id": "test_ep", "chunks_count": 5}
    
    response = client.post("/ingest", json={
        "episode_id": "test_ep",
        "text": "This is a test episode content."
    })
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["data"]["episode_id"] == "test_ep"

@patch("main.agent.get_answer")
def test_query_endpoint(mock_get_answer):
    mock_get_answer.return_value = {
        "episode_id": "test_ep",
        "mode": "plain_english",
        "answer": "This is a test answer.",
        "metadata": {}
    }
    
    response = client.post("/episodes/test_ep/plain_english", json={
        "query": "What is this?"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "This is a test answer."
    assert data["mode"] == "plain_english"

def test_invalid_mode():
    # Assuming the agent raises ValueError for invalid mode, 
    # but here we are mocking so we need to simulate the error if we want to test exception handling
    # or we test the validation logic in unit test for agent.
    # Let's test the API response if agent raises error.
    with patch("main.agent.get_answer", side_effect=ValueError("Invalid mode")):
        response = client.post("/episodes/test_ep/invalid_mode", json={"query": "test"})
        assert response.status_code == 400
