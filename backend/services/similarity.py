import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

def calculate_tfidf_similarity(text1: str, text2: str) -> float:
    """
    Calculates TF-IDF cosine similarity between exactly two strings.
    Returns value in [0.0, 1.0].
    """
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        # Clamp to [0, 1]
        return max(0.0, min(1.0, float(score)))
    except ValueError:
        # Happens if strings only contain stop words or are empty
        return 0.0

def calculate_fuzzy_similarity(text1: str, text2: str) -> float:
    """
    Calculates raw sequence matching ratio.
    Returns value in [0.0, 1.0].
    """
    return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def evaluate_match_signals(query_chunk: str, matched_chunk: str, semantic_similarity: float):
    """
    Combines three signals (Semantic, TF-IDF, Fuzzy) to categorize and weight the match.
    
    Returns:
        tuple(float, str) -> (combined_similarity_score [0,1], match_type)
    """
    
    tfidf_sim = calculate_tfidf_similarity(query_chunk, matched_chunk)
    fuzzy_sim = calculate_fuzzy_similarity(query_chunk, matched_chunk)
    
    # Is it basically exact?
    if query_chunk.strip().lower() in matched_chunk.strip().lower() or matched_chunk.strip().lower() in query_chunk.strip().lower():
        # High confidence exact
        return 1.0, "Exact"
        
    if fuzzy_sim >= 0.95:
        return max(fuzzy_sim, semantic_similarity), "Exact"
        
    if fuzzy_sim >= 0.70:
        # Weighted combination favoring the fuzzy match
        combined = (0.50 * fuzzy_sim) + (0.35 * semantic_similarity) + (0.15 * tfidf_sim)
        return min(combined, 1.0), "Fuzzy"
        
    # Otherwise it's semantic.
    # If the vector model thinks it's a semantic match, we base the score heavily on that,
    # but use tfidf/fuzzy to slightly adjust it (penalize if completely textually unrelated, OR reward if there's some shared vocab).
    combined = (0.75 * semantic_similarity) + (0.15 * tfidf_sim) + (0.10 * fuzzy_sim)
    
    return min(combined, 1.0), "Semantic"
