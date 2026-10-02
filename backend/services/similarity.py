import re
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Sample Internal Corpus
CORPUS = [
    {"id": "doc1", "title": "Intro to ML", "content": "Machine learning algorithms can identify patterns in large datasets. This is highly useful for predictive analytics."},
    {"id": "doc2", "title": "Wikipedia: AI", "content": "Artificial intelligence is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by animals including humans."},
    {"id": "doc3", "title": "Data Science Basics", "content": "A neural network is a network or circuit of biological neurons, or, in a modern sense, an artificial neural network."},
    {"id": "doc4", "title": "SEO Guide", "content": "Search engine optimization represents the process of improving the quality and quantity of website traffic to a website or a web page from search engines."}
]

def chunk_text(text, chunk_size=3):
    """Splits text into chunks of sentences."""
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    for i in range(0, len(sentences), chunk_size):
        chunks.append(" ".join(sentences[i:i+chunk_size]))
    return chunks

class PlagiarismEngine:
    def __init__(self):
        # Build TF-IDF for the corpus
        self.vectorizer = TfidfVectorizer()
        self.corpus_texts = [doc['content'] for doc in CORPUS]
        if self.corpus_texts:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus_texts)
            
    def analyze(self, text: str):
        chunks = chunk_text(text, 2)
        matches = []
        
        total_similarity = 0
        
        for chunk in chunks:
            if not chunk.strip(): continue
            
            # Semantic/Fuzzy Match via TFIDF
            vec = self.vectorizer.transform([chunk])
            sim_scores = cosine_similarity(vec, self.tfidf_matrix)[0]
            
            best_idx = sim_scores.argmax()
            best_score = sim_scores[best_idx]
            
            # Exact Match approximation via difflib
            best_doc_text = self.corpus_texts[best_idx]
            exact_ratio = SequenceMatcher(None, chunk.lower(), best_doc_text.lower()).ratio()
            
            # Combine thresholds
            if best_score > 0.3 or exact_ratio > 0.6:
                match_type = "exact" if exact_ratio > 0.8 else ("fuzzy" if exact_ratio > 0.6 else "semantic")
                score = max(best_score, exact_ratio)
                
                matches.append({
                    "id": f"match-{len(matches)+1}",
                    "text_segment": chunk,
                    "matched_text": best_doc_text[:200] + "...",
                    "similarity_score": round(score * 100, 1),
                    "match_type": match_type,
                    "source_name": CORPUS[best_idx]["title"]
                })
                total_similarity += score
                
        # Calculate overall percentage based on matched chunks
        if len(chunks) == 0:
            return 0.0, 100.0, [], 0
            
        coverage = len(matches) / len(chunks) if chunks else 0
        avg_score = total_similarity / len(matches) if matches else 0
        
        overall_similarity = round(coverage * avg_score * 100, 1)
        originality = round(100.0 - overall_similarity, 1)
        
        unique_sources = len(set([m["source_name"] for m in matches]))
        
        return overall_similarity, originality, matches, unique_sources
