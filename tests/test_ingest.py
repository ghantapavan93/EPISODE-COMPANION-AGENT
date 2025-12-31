import pytest
from unittest.mock import MagicMock, patch
from ingest import ingest_episode

@patch("ingest.Chroma")
@patch("ingest.GoogleGenerativeAIEmbeddings")
@patch("ingest.RecursiveCharacterTextSplitter")
def test_ingest_episode(mock_splitter, mock_embeddings, mock_chroma):
    # Mock splitter
    mock_splitter_instance = MagicMock()
    mock_splitter.return_value = mock_splitter_instance
    mock_splitter_instance.create_documents.return_value = [
        MagicMock(page_content="chunk1", metadata={}),
        MagicMock(page_content="chunk2", metadata={})
    ]
    
    # Mock Chroma
    mock_vector_store = MagicMock()
    mock_chroma.return_value = mock_vector_store
    mock_vector_store.add_documents.return_value = ["id1", "id2"]
    
    result = ingest_episode("test_ep", "some text content")
    
    assert result["episode_id"] == "test_ep"
    assert result["chunks_count"] == 2
    assert result["ids"] == ["id1", "id2"]
    
    # Verify calls
    mock_splitter_instance.create_documents.assert_called_once()
    mock_vector_store.add_documents.assert_called_once()
