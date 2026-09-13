# 🎯 AI Job Recommender

> Upload your resume. Get AI-ranked job matches with explanations — powered by **Gemini**, **LangChain**, and **ChromaDB**.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.63-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C?style=flat&logo=chainlink&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-1.0-orange?style=flat)
![Gemini](https://img.shields.io/badge/Gemini-2.0--flash-4285F4?style=flat&logo=google&logoColor=white)

---

## ✨ Features

- 📄 **PDF Upload** — drag-and-drop your resume directly in the browser
- 🧠 **AI Profile Extraction** — Gemini parses your skills, experience, and preferred role automatically
- 🔍 **Semantic Job Search** — MMR vector search finds diverse, relevant listings across 1000+ jobs
- ⭐ **Intelligent Ranking** — LLM ranks and explains each match with a realistic fit percentage
- 🎯 **Gap Analysis** — missing skills and learning topics surfaced per job
- 🔗 **Direct Apply Links** — one-click to the original job posting
- 📥 **Export Results** — download recommendations as JSON

---

## 🏗️ Architecture

```
Resume PDF
    │
    ▼
┌─────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│  PDF Reader │────▶│ Profile Extractor│────▶│    Job Recommender   │
│  (pypdf)    │     │   (Gemini LLM)   │     │   (Gemini LLM)       │
└─────────────┘     └──────────────────┘     └──────────┬───────────┘
                                                         │
                                             ┌───────────▼───────────┐
                                             │      Vector Store      │
                                             │  (ChromaDB + MiniLM)  │
                                             └───────────────────────┘
                                                         ▲
                                             ┌───────────┴───────────┐
                                             │     Job Indexer        │
                                             │  (Arbeitnow API)       │
                                             └───────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Google Gemini 2.0 Flash via `langchain-google-genai` |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace) |
| **Vector DB** | ChromaDB with MMR (Maximal Marginal Relevance) search |
| **Orchestration** | LangChain |
| **UI** | Streamlit |
| **Data Models** | Pydantic v2 + pydantic-settings |
| **Job Source** | [Arbeitnow](https://www.arbeitnow.com/) public API |

---

## 📁 Project Structure

```
ai-job-recommender/
├── src/
│   └── job_recommender/
│       ├── config.py               # pydantic-settings — validated config
│       ├── models.py               # Pydantic data models
│       ├── exceptions.py           # Custom exception hierarchy
│       ├── core/
│       │   ├── pdf_reader.py       # PDF text extraction (path + bytes)
│       │   ├── extractor.py        # LLM-based profile extraction
│       │   ├── recommender.py      # Retrieve + rank jobs via LLM
│       │   └── vector_store.py     # ChromaDB CRUD + search wrapper
│       ├── services/
│       │   ├── job_api.py          # Arbeitnow API client
│       │   └── job_indexer.py      # Fetch → embed → upsert pipeline
│       ├── prompts/
│       │   └── templates.py        # LLM prompt strings
│       └── ui/
│           ├── streamlit_app.py    # Main Streamlit entry point
│           └── components.py       # Reusable UI components
├── scripts/
│   └── sync_jobs.py                # CLI: index jobs into ChromaDB
├── chroma_db/                      # Persisted vector store
├── .env                            # API keys (not committed)
├── pyproject.toml
└── requirements.txt
```

---

## ⚡ Quick Start

### 1. Clone & install

```bash
git clone https://github.com/your-username/ai-job-recommender.git
cd ai-job-recommender

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -e .
```

### 2. Set up environment variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

> Get a free API key at [Google AI Studio](https://aistudio.google.com/app/apikey).

### 3. Index job listings *(first time only)*

```bash
python scripts/sync_jobs.py
```

This fetches ~1300 jobs from the Arbeitnow API and stores them in ChromaDB. Takes ~3–5 minutes.

```
23:44:58  INFO  job_recommender.services.job_api — Fetching job listings — page 1 / 10
...
23:45:23  INFO  job_recommender.services.job_api — Fetched 1300 total jobs.
23:45:58  INFO  SYNC COMPLETE  Added=1300  Updated=0  Skipped=0  DB total=1300
```

### 4. Launch the UI

```bash
streamlit run src/job_recommender/ui/streamlit_app.py
```

Open **http://localhost:8501** in your browser, upload your resume PDF, and click **Analyse & Recommend**.

---

## 🔄 How It Works

```
1. PDF Upload
   └── User uploads resume PDF via Streamlit

2. Profile Extraction
   └── Resume text → Gemini LLM → structured CandidateProfile
       { name, email, skills, experience, preferred_role, ... }

3. Semantic Retrieval
   └── Profile → search query → MMR vector search → top 20 diverse job docs

4. LLM Ranking
   └── (Profile + 20 jobs) → Gemini LLM → top 10 ranked JobRecommendations
       { match_percentage, reason, missing_skills, learning_topics, should_apply }

5. UI Render
   └── Profile card + expandable job cards with match bars + Apply Now links
```

---

## ⚙️ Configuration

All settings are configurable via environment variables or `.env`:

| Variable | Default | Description |
|---|---|---|
| `GOOGLE_API_KEY` | *(required)* | Google AI API key |
| `LLM_MODEL` | `gemini-2.0-flash` | Gemini model name |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | HuggingFace embedding model |
| `CHROMA_PATH` | `chroma_db` | ChromaDB persistence directory |
| `TOP_K_RESULTS` | `20` | Jobs retrieved per search |
| `FETCH_K_RESULTS` | `50` | Candidates for MMR selection |
| `MAX_PAGES` | `10` | API pages to fetch during sync |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "feat: add my feature"`
4. Push and open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.
