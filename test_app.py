from fastapi.testclient import TestClient
from main import app
from ingest import chunk_text

client = TestClient(app)

def test_chunking_produces_chunks():
    text = " ".join(["word"] * 1000)
    chunks = chunk_text(text, chunk_size=300, overlap=50)
    assert len(chunks) > 1

def test_ask_endpoint_returns_answer():
    response = client.post("/ask", json={"question": "What are the exam dates?"})
    assert response.status_code == 200
    assert "answer" in response.json()
    assert "sources" in response.json()