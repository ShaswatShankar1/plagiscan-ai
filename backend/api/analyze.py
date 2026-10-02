from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import logging

from core.database import get_db
import services.vector_search as vec_search
from services.similarity import evaluate_match_signals

logger = logging.getLogger(__name__)

router = APIRouter()

class AnalyzeRequest(BaseModel):
    text: str

class SimilarityMatch(BaseModel):
    id: str
    text_segment: str
    matched_text: str
    similarity_score: float
    match_type: str
    source_name: str

class AnalyzeResponse(BaseModel):
    similarity: float
    originality: float
    matches: List[SimilarityMatch]
    total_sources: int
    risk: str

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_document(request: AnalyzeRequest, db: Session = Depends(get_db)):
    text = request.text
    
    if not text or len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
        
    if len(text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Input text is too short to analyze.")
        
    if not vec_search.model:
        raise HTTPException(status_code=503, detail="Similarity embedding engine is currently unavailable.")

    logger.info(f"Starting analysis for text length {len(text)}")

    chunks = vec_search.intelligent_chunk_text(text)
    
    if not chunks:
        # Failsafe if chunking parsed nothing (e.g. all punctuation)
        return {"similarity": 0.0, "originality": 100.0, "matches": [], "total_sources": 0, "risk": "Low"}
    
    all_matches = []
    unique_sources = set()
    
    # Track the highest matched similarity per chunk for document-level aggregation
    chunk_top_scores = []
    
    for i, chunk in enumerate(chunks):
        try:
            # 1. Semantic Candidate Extraction (limit strictly to avoid overwhelming)
            results = list(vec_search.find_similar_chunks(db, chunk, limit=3))
        except Exception as e:
            logger.error(f"Database error finding chunks: {e}")
            raise HTTPException(status_code=500, detail="Database failure during similarity search.")
        
        best_chunk_score = 0.0
        
        for candidate_chunk, candidate_doc, semantic_sim in results:
            
            db_text = candidate_chunk.chunk_text
            
            # 2. Multi-Signal Evidence Evaluation
            combined_score_float, match_type = evaluate_match_signals(chunk, db_text, semantic_sim)
            percent_score = round(combined_score_float * 100.0, 1)
            
            # Record the highest score for this specific query chunk
            if percent_score > best_chunk_score:
                best_chunk_score = percent_score
                
            # 3. Match Filtering (only include if it is distinctly similar)
            # Threshold: >= 45% prevents noisy background matches
            if percent_score >= 45.0:
                
                # Check if we already have this exact segment matched to avoid flooding
                # (A better system would merge them into one match with multiple sources, but this fits the UI)
                duplicate = any(m["text_segment"] == chunk and m["source_name"] == candidate_doc.title for m in all_matches)
                
                if not duplicate:
                    all_matches.append({
                        "id": f"match-{i}-{len(all_matches)}",
                        "text_segment": chunk,
                        "matched_text": db_text[:250] + ("..." if len(db_text) > 250 else ""),
                        "similarity_score": percent_score,
                        "match_type": match_type,
                        "source_name": candidate_doc.title or "Unknown Document"
                    })
                    unique_sources.add(candidate_doc.id)
                    
                    # If we found a very strong match for this chunk, stop checking candidates for it to save UI spam
                    if percent_score > 85.0:
                        break
                        
        chunk_top_scores.append(best_chunk_score)

    # 4. Overall Document Score Calculation
    # We weight chunks by their length approximation (word count).
    total_weights = 0
    weighted_score = 0
    
    for chunk, best_score in zip(chunks, chunk_top_scores):
        weight = len(chunk.split())
        total_weights += weight
        weighted_score += best_score * weight
        
    overall_similarity = round(weighted_score / total_weights, 1) if total_weights > 0 else 0.0
    overall_similarity = max(0.0, min(100.0, overall_similarity))
    
    originality = round(100.0 - overall_similarity, 1)
    
    # 5. Risk Classification
    if overall_similarity > 70.0:
        risk = "Very High"
    elif overall_similarity > 40.0:
        risk = "High"
    elif overall_similarity > 20.0:
        risk = "Moderate"
    else:
        risk = "Low"
        
    logger.info(f"Analysis complete. Score: {overall_similarity}%. Matches: {len(all_matches)}")
        
    return {
        "similarity": overall_similarity,
        "originality": originality,
        "matches": all_matches,
        "total_sources": len(unique_sources),
        "risk": risk
    }

class CorpusRequest(BaseModel):
    title: str
    content: str

@router.post("/corpus")
async def add_to_corpus(request: CorpusRequest, db: Session = Depends(get_db)):
    """Indexes a document into pgvector for similarity searches."""
    if not request.title or not request.content:
        raise HTTPException(status_code=400, detail="Title and content are required.")
        
    try:
        doc = vec_search.index_document(db, request.title, request.content)
        return {"message": "Document successfully indexed.", "document_id": doc.id}
    except ValueError as val_e:
        raise HTTPException(status_code=400, detail=str(val_e))
    except Exception as e:
        logger.error(f"Failed to add to corpus: {e}")
        raise HTTPException(status_code=500, detail="Failed to process document into database.")
