import pytest
from fastapi.testclient import TestClient
from main import app
from core.database import Base, engine, get_db
from sqlalchemy.orm import sessionmaker

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    doc_request = {
        "title": "Test Document",
        "content": "The quick brown fox jumps over the lazy dog. Artificial intelligence is intelligence demonstrated by machines. Machine learning algorithms identify patterns in large datasets."
    }
    client.post("/api/corpus", json=doc_request)
    yield
    Base.metadata.drop_all(bind=engine)

def test_original_text():
    res = client.post("/api/analyze", json={"text": "Bananas are excellent sources of potassium and grow mostly in tropical climates."})
    assert res.status_code == 200
    data = res.json()
    assert data["similarity"] < 25.0
    assert data["risk"] in ["Low", "Moderate"]

def test_exact_corpus_sentence():
    res = client.post("/api/analyze", json={"text": "Artificial intelligence is intelligence demonstrated by machines."})
    assert res.status_code == 200
    data = res.json()
    assert data["similarity"] > 85.0
    match_types = [m["match_type"] for m in data["matches"]]
    assert "Exact" in match_types

def test_slightly_modified_corpus_sentence():
    res = client.post("/api/analyze", json={"text": "Artificial intelligence is demonstrated primarily by intelligent machines."})
    assert res.status_code == 200
    data = res.json()
    assert data["similarity"] > 50.0

def test_semantically_similar_sentence():
    res = client.post("/api/analyze", json={"text": "AI refers to synthetic cognitive abilities shown by computers."})
    assert res.status_code == 200
    data = res.json()
    assert data["similarity"] > 30.0

def test_empty_text():
    res = client.post("/api/analyze", json={"text": ""})
    assert res.status_code == 400

def test_very_short_text():
    res = client.post("/api/analyze", json={"text": "Hello."})
    assert res.status_code == 400

def test_multiple_paragraphs():
    text = (
        "The quick brown fox jumps over the lazy dog.\n\n"
        "Completely original statement here about space exploration and NASA.\n\n"
        "Machine learning algorithms identify patterns in large datasets."
    )
    res = client.post("/api/analyze", json={"text": text})
    assert res.status_code == 200
    data = res.json()
    assert len(data["matches"]) >= 2
    assert 20.0 <= data["similarity"] <= 85.0
