# PlagiScan AI

Detect Plagiarism. Improve Originality.

An integrated platform to check for textual similarity using statistical and semantic comparison against a corpus, and rewrite flagged passages using local or remote LLMs while preserving semantic intent.

## Architecture
- **Frontend**: Next.js 15, React, Tailwind CSS, Shadcn UI
- **Backend**: FastAPI (Python), scikit-learn, difflib, sentence-transformers
- **Database (Docker)**: Postgres with pgvector for embedding search
- **AI Paraphrasing**: Hooks up to local Ollama (Llama 3, Phi-3, etc.) or external providers (OpenAI, etc.)

## Project Structure
- `/frontend`: Next.js web application
- `/backend`: FastAPI service for plagiarism detection and NLP Tasks
- `/worker`: Future background processes for async large-document analysis
- `/database`: Schema descriptions or configurations (DB relies on docker-compose for Postgres)

## Running Locally
### 1. Prerequisites
- Node.js 18+ and npm
- Python 3.10+
- Docker and Docker Compose (if utilizing pgvector for full vector search in the future)

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
This runs the plagiarism detection logic and API on `http://127.0.0.1:8000/api`.

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` to view the application workspace.

### Core Testing
1. Navigate to `/analyze`.
2. Paste text that matches some of the test corpus (e.g. "Artificial intelligence is intelligence demonstrated by machines").
3. Click "Analyze".
4. Results are dynamically fetched from the Python Backend (`PlagiarismEngine`), providing real exact and fuzzy matches!
5. Using the "Rewrite with AI" feature requires a running Ollama deployment at `http://localhost:11434` or appropriately configured API Route.

## Features
- **Multi-Layer Detection**: Scans with n-grams, fuzzy similarity string ratios, and semantic matching.
- **AI Rewriting**: In-place replacement of flagged content to reduce plagiarism risk via local transformers.
- **Modern Dashboard**: Visually compare before/after stats.
