import re
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from models.domain import Document, DocumentChunk
from pgvector.sqlalchemy import Vector

# In a real app we'd load this once in memory at startup
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    model = None

def chunk_text(text: str, max_words=30):
    """Simple sentence chunker"""
    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    # Further group them if needed - simplified for example to just per-sentence
    return [s for s in sentences if len(s.split()) > 3]

def index_document(db: Session, title: str, content: str):
    """Chunks a document, generates embeddings, and saves to pgvector"""
    if not model:
        raise RuntimeError("Embedding model not loaded")
        
    doc = Document(title=title, content=content)
    db.add(doc)
    db.flush()
    
    chunks = chunk_text(content)
    if not chunks:
        return doc
        
    # Generate embeddings in batch
    embeddings = model.encode(chunks)
    
    db_chunks = []
    for chunk, emb in zip(chunks, embeddings):
        db_chunk = DocumentChunk(
            document_id=doc.id,
            chunk_text=chunk,
            embedding=emb.tolist()
        )
        db_chunks.append(db_chunk)
        
    db.add_all(db_chunks)
    db.commit()
    
    return doc

def find_similar_chunks(db: Session, text: str, threshold=0.75, limit=5):
    """Finds matches using pgvector cosine distance (<=>)"""
    if not model:
        raise RuntimeError("Embedding model not loaded")
        
    query_embedding = model.encode([text])[0]
    
    # Cosine distance operator is <=>. Distance = 1 - cosine_similarity
    # So similarity = 1 - distance. We want distance < (1 - threshold)
    max_distance = 1.0 - threshold
    
    results = db.query(DocumentChunk, Document)\
        .join(Document, DocumentChunk.document_id == Document.id)\
        .filter(DocumentChunk.embedding.cosine_distance(query_embedding) < max_distance)\
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))\
        .limit(limit)\
        .all()
        
    return results
