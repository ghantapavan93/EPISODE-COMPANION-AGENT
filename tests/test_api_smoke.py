import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.server import app, get_db

class TestApiSmoke(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Override dependency to avoid real DB connection
        app.dependency_overrides[get_db] = lambda: MagicMock()

    def tearDown(self):
        app.dependency_overrides = {}

    def _get_mock_metadata(self):
        return {
            "trace_id": "test-trace",
            "latency_ms": 10.0,
            "stage_latency": {},
            "used_chunks": 1,
            "expanded_query": "test",
            "quality_checks": {},
            "source_papers": [],
            "tokens_in": 10,
            "tokens_out": 10,
            "model": "test-model",
            "question_type": "test",
            "suggested_followups": [],
            "error": None,
            "details": None,
        }

    @patch("backend.server.orchestrator")
    def test_plain_english_mode(self, mock_orchestrator):
        # Setup mock return value
        mock_orchestrator.route_request.return_value = {
            "episode_id": "test-ep",
            "mode": "plain_english",
            "answer": "tl;dr: It works.\n\nKey Ideas:\n- Test\n\nWhy this matters:\n- Quality",
            "metadata": self._get_mock_metadata()
        }

        payload = {
            "user_id": "test_user",
            "message": "What is this?",
            "mode": "plain_english"
        }
        response = self.client.post("/companion/query", json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["mode"], "plain_english")
        self.assertIn("tl;dr", data["answer"])
        
        # Verify orchestrator was called with correct mode
        args, kwargs = mock_orchestrator.route_request.call_args
        self.assertEqual(kwargs["mode"], "plain_english")

    @patch("backend.server.orchestrator")
    def test_founder_mode(self, mock_orchestrator):
        mock_orchestrator.route_request.return_value = {
            "episode_id": "test-ep",
            "mode": "founder_takeaway",
            "answer": "Big Idea: Test.\n\nProduct Directions:\n- Build it\n\nRisks & Unknowns:\n- None",
            "metadata": self._get_mock_metadata()
        }

        payload = {
            "user_id": "test_user",
            "message": "Idea?",
            "mode": "founder_takeaway"
        }
        response = self.client.post("/companion/query", json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["mode"], "founder_takeaway")
        self.assertIn("Big Idea", data["answer"])

    @patch("backend.server.orchestrator")
    def test_engineer_mode(self, mock_orchestrator):
        mock_orchestrator.route_request.return_value = {
            "episode_id": "test-ep",
            "mode": "engineer_angle",
            "answer": "Core Principle: Math.\n\nArchitecture:\n- Layers\n\nInference Pipeline:\n- Fast",
            "metadata": self._get_mock_metadata()
        }

        payload = {
            "user_id": "test_user",
            "message": "How to build?",
            "mode": "engineer_angle"
        }
        response = self.client.post("/companion/query", json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["mode"], "engineer_angle")
        self.assertIn("Core Principle", data["answer"])

    @patch("backend.server.orchestrator")
    def test_inferred_mode(self, mock_orchestrator):
        """Test that omitting mode lets the backend infer it (mocked here)."""
        mock_orchestrator.route_request.return_value = {
            "episode_id": "test-ep",
            "mode": "plain_english",  # Inferred by orchestrator
            "answer": "Inferred answer.",
            "metadata": self._get_mock_metadata()
        }

        payload = {
            "user_id": "test_user",
            "message": "Just a general question",
            # mode is omitted
        }
        response = self.client.post("/companion/query", json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["mode"], "plain_english")
        
        # Verify orchestrator was called with mode=None
        args, kwargs = mock_orchestrator.route_request.call_args
        self.assertIsNone(kwargs["mode"])

    @patch("backend.server.orchestrator")
    def test_speech_endpoint(self, mock_orchestrator):
        """Test the speech stub endpoint."""
        mock_orchestrator.route_request.return_value = {
            "episode_id": "test-ep",
            "mode": "plain_english",
            "answer": "Speech answer.",
            "metadata": self._get_mock_metadata()
        }

        # Create a dummy file for upload
        files = {"audio": ("test.wav", b"fake audio content", "audio/wav")}
        params = {"user_id": "test_user"}
        
        response = self.client.post("/companion/speech", params=params, files=files)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["answer"], "Speech answer.")
        
        # Verify orchestrator was called (the stub uses a placeholder transcript)
        args, kwargs = mock_orchestrator.route_request.call_args
        self.assertIn("placeholder transcript", kwargs["text"])

if __name__ == "__main__":
    unittest.main()

