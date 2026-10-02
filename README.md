# PlagiScan AI

Detect Structural Similarity. Identify Potential Overlaps.

An integrated platform to check for textual similarity using statistical and semantic comparison against a corpus, and rewrite flagged passages using local or remote LLMs while preserving semantic intent.

## Architecture
- **Frontend**: Next.js 16.3.8, React 19.2.8, Tailwind CSS, Shadcn UI
- **Backend API**: FastAPI (Python)
- **Detection Pipeline**: 
  1. TF-IDF (scikit-learn)
  2. Fuzzy matching (difflib)
  3. Semantic embeddings (sentence-transformers: `all-MiniLM-L6-v2`)
  4. pgvector (PostgreSQL vector similarity)
- **AI Paraphrasing**: Hooks up to local Ollama or external providers.

**Flow:**
Next.js frontend → FastAPI → Detection engine → PostgreSQL + pgvector → Sentence Transformers

## Project Structure
- `/frontend`: Next.js web application
- `/backend`: FastAPI service for plagiarism detection and NLP Tasks
- `/docker-compose.yml`: Spawns Postgres with pgvector

## Important Distinction: Detection vs. Rewriting
- **Similarity Detection**: The system identifies text strings that closely match a known corpus through statistical analysis, fuzzy matches, and semantic embeddings. This flags *potential overlap*.
- **AI Rewriting**: The app offers assistance to rewrite passages using AI. **Note: Using AI rewriting does not automatically make text "non-plagiarized" or academically acceptable.** It merely creates variations of the text. Always cite original sources ethically.

## Running Locally
### 1. Prerequisites
- Node.js 18+ and npm
- Python 3.10+
- Docker and Docker Compose (required for pgvector)
- Git

### 2. Backend Setup
```bash
docker-compose up -d

cd backend
python -m venv venv
# Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
This runs the detection logic on `http://127.0.0.1:8000/api`.

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` to view the application workspace.

### Core Testing
1. Navigate to `/analyze`.
2. Paste text that matches some of the test corpus.
3. Click "Analyze".
4. Results are dynamically fetched from the Python Backend (`PlagiarismEngine`).
