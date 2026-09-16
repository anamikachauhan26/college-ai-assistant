# WCE College AI Assistant

A RAG-based (Retrieval-Augmented Generation) chatbot that answers student questions about Walchand College of Engineering using real content scraped from the official college website — notices, admissions, fees, academic regulations, and per-branch curriculum details.

Instead of manually searching through dozens of PDFs and notices, students can just ask a question in plain language and get a grounded, sourced answer.

---

## How it works

```
College website (notices, pages, PDFs)
        │
        ▼
   Scraper (requests + BeautifulSoup + pypdf)
        │
        ▼
   Chunking (splits text into ~300-word pieces)
        │
        ▼
   Embedding (Gemini embedding model → vectors)
        │
        ▼
   ChromaDB (vector database, stores chunks + embeddings)
        │
        ▼
   Retrieval (finds the most relevant chunks for a question)
        │
        ▼
   Generation (Gemini LLM answers using only retrieved context)
        │
        ▼
   FastAPI backend  →  Chat UI (streamed, word-by-word)
```

**Why RAG instead of just asking an LLM directly?** A general-purpose LLM has no knowledge of this specific college's notices, fees, or curriculum. RAG solves this by retrieving the actual relevant text and feeding it to the model as context before it answers — so responses are grounded in real facts, with sources, instead of guesses.

---

## Tech stack

| Layer | Tool | Why |
|---|---|---|
| LLM (generation) | Gemini (`gemini-flash-latest`) | Free tier, fast, good quality |
| Embeddings | Gemini (`gemini-embedding-001`) | Converts text to vectors for semantic search |
| Vector DB | ChromaDB | Local, free, no server setup needed |
| Backend | FastAPI | Async, clean, standard for AI-serving APIs |
| Frontend | Plain HTML/CSS/JS | Chat UI with streaming, no framework overhead |
| Scraping | requests + BeautifulSoup + pypdf | Sitemap-based page discovery, HTML parsing, PDF text extraction |
| Testing | pytest | Unit tests with mocked external API calls |
| CI/CD | GitHub Actions | Auto-runs tests on every push |

---

## Project structure

```
college-ai-assistant/
├── data/                  # Scraped text content (gitignored recommended for real data)
├── chroma_db/             # Vector database (gitignored)
├── frontend/
│   └── index.html         # Chat UI
├── scrape.py               # Sitemap + notice board scraper
├── scrape_pages.py          # Admissions/fees/academics/branch pages scraper
├── ingest.py                # Chunks + embeds + stores documents in ChromaDB
├── rag.py                   # Retrieval + prompt building + generation logic
├── main.py                  # FastAPI backend (/ask and /ask-stream endpoints)
├── test_app.py               # pytest tests (chunking + API endpoint, mocked)
├── requirements.txt
├── .env                      # API key (never committed)
└── .github/workflows/ci.yml  # CI pipeline
```

---

## Setup — running this locally

### 1. Clone and enter the project
```bash
git clone <your-repo-url>
cd college-ai-assistant
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Get a Gemini API key
Go to [Google AI Studio](https://aistudio.google.com), sign in, click "Get API key" → "Create API key." Free, no card required.

### 5. Add your key
Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_key_here
```

### 6. Scrape data (or use your own `.txt` files in `/data`)
```bash
python scrape.py
python scrape_pages.py
```

### 7. Build the vector database
```bash
python ingest.py
```

### 8. Run the backend
```bash
uvicorn main:app --reload
```

### 9. Run the frontend (in a separate terminal)
```bash
cd frontend
python -m http.server 5500
```
Open `http://localhost:5500` in your browser.

---

## Running tests

```bash
pytest
```
Tests mock the live Gemini API call so they run instantly and don't depend on network access or API quota.

---

## Known limitations

- **Some fee PDFs are scanned images**, not real embedded text — `pypdf` can't extract text from these. A fix would involve OCR (e.g., Tesseract + `pdf2image`), not yet implemented.
- **No authentication** — anyone can ask anything; there's no per-student personalization (e.g., individual attendance/fee status).
- **Not all college pages are ingested** — a curated subset (admissions, fees, academics, a few branches) was scraped deliberately rather than the entire site, to keep the dataset focused and clean.
- **Retrieval is pure vector search** — no hybrid keyword search yet, so exact terms (specific codes, dates) can occasionally be missed in favor of semantically-similar-but-wrong content.

---

## For anyone learning from this project

This project is a hands-on implementation of **RAG (Retrieval-Augmented Generation)**, one of the most common patterns for building AI applications on private/custom data. If you're studying this to learn, here's where to go deeper:

- **RAG fundamentals**: [Google's RAG overview](https://cloud.google.com/use-cases/retrieval-augmented-generation) — the concept explained plainly.
- **Embeddings**: search "sentence embeddings explained" — understanding how text becomes vectors is the core intuition behind all semantic search.
- **Vector databases**: [ChromaDB docs](https://docs.trychroma.com/) — try running queries directly against a Chroma collection to see similarity search in action.
- **Prompt engineering**: [Anthropic's prompt engineering guide](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview) — the same core principles (clear instructions, context grounding) apply across LLM providers.
- **Evaluating RAG systems**: look up **RAGAS**, an open-source framework for measuring retrieval and answer quality — the natural next step beyond "it looks like it works."
- **Web scraping ethics**: always check a site's `robots.txt` and only scrape publicly accessible pages — this project only touches the college's own already-public site content.

