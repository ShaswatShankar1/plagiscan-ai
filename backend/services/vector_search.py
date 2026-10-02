import re
from typing import List, Tuple
from sqlalchemy.orm import Session
from models.domain import Document, DocumentChunk
from pgvector.sqlalchemy import Vector
import logging

logger = logging.getLogger(__name__)

# Load model cautiously
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    logger.error(f"Failed to load sentence-transformers: {e}")
    model = None

def intelligent_chunk_text(text: str, max_words=40) -> List[str]:
    """
    Intelligent chunking that preserves sentences but groups them until max_words.
    Handles paragraphs and text without punctuation.
    """
    if not text or not text.strip():
        return []
        
    # First split by explicit line breaks to respect paragraphs
    paragraphs = [p for p in text.split('\n') if p.strip()]
    
    chunks = []
    
    for para in paragraphs:
        # Split paragraph into sentences by punctuation
        sentences = re.split(r'(?<=[.!?])\s+', para.strip())
        
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            word_count = len(sentence.split())
            
            # If the sentence itself is massive, we might just have to add it anyway
            if word_count > max_words and not current_chunk:
                chunks.append(sentence)
                continue
            
            if current_length + word_count > max_words and current_chunk:
                # Flush the current chunk
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = word_count
            else:
                current_chunk.append(sentence)
                current_length += word_count
                
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
    # Filter out empty or micro chunks
    return [c for c in chunks if len(c.split()) >= 3 and len(c) > 10]

def index_document(db: Session, title: str, content: str) -> Document:
    if not model:
        raise RuntimeError("Embedding model not loaded")
        
    if not title or not title.strip() or not content or not content.strip():
        raise ValueError("Title and content cannot be empty")
        
    doc = Document(title=title, content=content)
    db.add(doc)
    db.flush()
    
    chunks = intelligent_chunk_text(content)
    if not chunks:
        # Save empty document anyway?
        db.commit()
        return doc
        
    try:
        embeddings = model.encode(chunks, batch_size=32)
        
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
    except Exception as e:
        db.rollback()
        raise e

def find_similar_chunks(db: Session, query_text: str, limit: int = 5):
    """
    Find semantic matches. Returns (DocumentChunk, Document, actual_similarity_score).
    Similarity = 1.0 - cosine_distance.
    """
    if not model:
        raise RuntimeError("Embedding model not loaded")
        
    query_embedding = model.encode([query_text])[0]
    
    # Distance is 0 to 2
    distance_col = DocumentChunk.embedding.cosine_distance(query_embedding).label('distance')
    
    # Grab the closest chunks, ordered by distance
    results = db.query(DocumentChunk, Document, distance_col)\
        .join(Document, DocumentChunk.document_id == Document.id)\
        .order_by(distance_col)\
        .limit(limit)\
        .all()
        
    processed_results = []
    for chunk, doc, dist in results:
        # pgvector cosine distance: similarity = 1 - distance
        sim = 1.0 - dist
        # Clamp to [0, 1] just in case of float inaccuracies
        sim = max(0.0, min(1.0, sim))
        processed_results.append((chunk, doc, sim))
        
    return processed_results
