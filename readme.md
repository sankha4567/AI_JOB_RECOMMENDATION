# AI Job Recommender

An AI-powered job recommendation system that analyzes a candidate's PDF resume, extracts a structured professional profile using Google Gemini, retrieves semantically relevant job opportunities using ChromaDB and Sentence Transformers, and uses an LLM to rank and explain the best job matches.

The project is implemented in Python using a modular RAG-based architecture.

---

## Overview

Traditional job search systems often rely heavily on keyword matching. This project takes a semantic-search approach.

The system:

1. Reads a candidate's PDF resume.
2. Extracts the resume text.
3. Uses Google Gemini to convert the resume into a structured candidate profile.
4. Fetches job listings from the Arbeitnow Job Board API.
5. Normalizes the external job data into a common internal model.
6. Stores job descriptions as vector embeddings in ChromaDB.
7. Uses semantic search with Maximal Marginal Relevance (MMR) to retrieve relevant jobs.
8. Sends the candidate profile and retrieved jobs to Gemini.
9. Generates ranked job recommendations with match percentages, explanations, and missing skills.

---

## Architecture

```text
                         ┌─────────────────────┐
                         │   Candidate Resume  │
                         │       PDF File      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    PDF Reader       │
                         │    PyPDFLoader      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  Gemini Profile     │
                         │     Extraction      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ CandidateProfile    │
                         │                     │
                         │ • Skills            │
                         │ • Experience        │
                         │ • Education         │
                         │ • Preferred Role    │
                         │ • Location          │
                         └──────────┬──────────┘
                                    │
                                    │ Semantic Query
                                    ▼
┌──────────────────┐      ┌─────────────────────┐
│ Arbeitnow Job    │─────►│     Job API         │
│ Board API        │      │ Fetch & Normalize    │
└──────────────────┘      └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     ChromaDB         │
                         │                     │
                         │ Sentence Transformer│
                         │ Embeddings           │
                         └──────────┬──────────┘
                                    │
                             MMR Retrieval
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Retrieved Jobs      │
                         │ Top Relevant Jobs    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Gemini LLM        │
                         │ Job Ranking &        │
                         │ Recommendation      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Recommendations     │
                         │                     │
                         │ • Match %           │
                         │ • Reason            │
                         │ • Missing Skills     │
                         │ • Company            │
                         │ • Location           │
                         └─────────────────────┘
```

---

## Key Features

### Resume Analysis

- Reads resumes in PDF format.
- Extracts text using `PyPDFLoader`.
- Converts unstructured resume content into a structured candidate profile.
- Extracts:
  - Name
  - Email
  - Phone
  - Location
  - Preferred role
  - Experience
  - Education
  - Skills

### AI-Powered Profile Extraction

Google Gemini analyzes the extracted resume text and returns structured candidate information.

The extracted information is validated using Pydantic models before being used by the recommendation pipeline.

### Real Job Data

The system retrieves jobs from the Arbeitnow Job Board API rather than relying on a static dataset.

Job information is normalized into a common internal `Job` model containing:

- Job ID
- Job title
- Company
- Location
- Description
- Skills / tags
- Job URL

### Semantic Job Search

Jobs are embedded using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The embeddings are stored in ChromaDB.

Instead of relying only on exact keyword matching, the system searches for jobs that are semantically related to the candidate's:

- Preferred role
- Skills
- Experience
- Education
- Location

### MMR Retrieval

The recommender uses Maximal Marginal Relevance (MMR) retrieval.

This helps retrieve relevant jobs while reducing excessive similarity between returned results.

The current configuration retrieves:

```text
Initial candidates: 50
Final recommendations retrieved: 20
```

### LLM-Based Ranking

The retrieved jobs and candidate profile are passed to Google Gemini.

Gemini evaluates the retrieved jobs and produces:

- Match percentage
- Explanation for the match
- Missing skills
- Ranked recommendations

The recommendations are validated against Pydantic models before being displayed.

### Incremental Job Synchronization

The project includes a job synchronization pipeline.

Before inserting a job into ChromaDB, the system generates a SHA-256 hash from the normalized job content.

This allows the indexer to determine whether a job is:

- New
- Updated
- Unchanged

This avoids unnecessarily replacing unchanged jobs.

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python |
| LLM | Google Gemini |
| LLM Framework | LangChain |
| PDF Processing | PyPDF / PyPDFLoader |
| Embeddings | Sentence Transformers |
| Vector Database | ChromaDB |
| Data Validation | Pydantic |
| Job Data | Arbeitnow Job Board API |
| Configuration | python-dotenv |
| HTTP Client | Requests |

---

## Project Structure

```text
AI_JOB_RECOMMENDATION/
│
├── src/
│   └── job_recommender/
│       │
│       ├── app.py
│       │
│       ├── config.py
│       │
│       ├── job_api.py
│       │
│       ├── models.py
│       │
│       ├── pdf_utils.py
│       │
│       ├── profile_extractor.py
│       │
│       ├── prompts.py
│       │
│       ├── recommender.py
│       │
│       ├── sync_jobs.py
│       │
│       └── vector_store.py
│
├── uploads/
│   └── resume.pdf
│
├── chroma_db/
│   └── Local vector database
│
├── jobs_cache/
│   └── Cached job data
│
├── .env
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Module Responsibilities

### `app.py`

Main application entry point.

Responsible for:

- Reading the resume.
- Extracting the candidate profile.
- Calling the recommendation engine.
- Printing the recommendations.

---

### `config.py`

Central configuration module.

Contains:

- Gemini API configuration
- LLM model configuration
- Embedding model
- ChromaDB configuration
- Resume path
- Job cache configuration
- API pagination settings
- Request timeout

---

### `pdf_utils.py`

Handles PDF processing.

The `PDFReader` utility:

```python
PDFReader.extract_text(pdf_path)
```

extracts text from all available PDF pages.

---

### `profile_extractor.py`

Responsible for AI-powered resume analysis.

Pipeline:

```text
Resume Text
     ↓
ChatPromptTemplate
     ↓
Google Gemini
     ↓
JSON Response
     ↓
Pydantic Validation
     ↓
CandidateProfile
```

---

### `job_api.py`

Responsible for communicating with the external job API.

It:

- Fetches job listings.
- Handles pagination.
- Handles rate limiting.
- Normalizes API responses.
- Converts external jobs into the internal `Job` model.

---

### `models.py`

Contains the application's Pydantic models.

#### `CandidateProfile`

Represents the candidate extracted from the resume.

```python
CandidateProfile
```

#### `Job`

Represents a normalized job listing.

```python
Job
```

#### `JobRecommendation`

Represents an individual recommendation.

```python
JobRecommendation
```

#### `RecommendationResponse`

Represents the final recommendation response.

```python
RecommendationResponse
```

---

### `vector_store.py`

Provides the ChromaDB abstraction.

Responsibilities include:

- Creating embeddings.
- Adding jobs.
- Updating jobs.
- Deleting jobs.
- Checking whether a job exists.
- Retrieving job metadata.
- Similarity search.
- MMR search.

---

### `sync_jobs.py`

Responsible for building and maintaining the job vector database.

Pipeline:

```text
Arbeitnow API
      ↓
Fetch Jobs
      ↓
Normalize Jobs
      ↓
Create LangChain Documents
      ↓
Generate SHA-256 Hash
      ↓
Check ChromaDB
      ↓
┌───────────┬───────────┬───────────┐
│   New     │  Updated  │ Unchanged │
│   Job     │   Job     │   Job     │
└─────┬─────┴─────┬─────┴─────┬─────┘
      ↓           ↓           ↓
     Add        Update       Skip
```

---

### `recommender.py`

Core recommendation engine.

The recommendation pipeline is:

```text
CandidateProfile
      ↓
Build Semantic Query
      ↓
MMR Search in ChromaDB
      ↓
Retrieve Relevant Jobs
      ↓
Gemini Ranking Prompt
      ↓
JSON Response
      ↓
Pydantic Validation
      ↓
RecommendationResponse
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/sankha4567/AI_JOB_RECOMMENDATION.git
cd AI_JOB_RECOMMENDATION
```

### 2. Create a Virtual Environment

#### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

For editable installation of the `src` package:

```bash
pip install -e .
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_gemini_api_key
```

The application loads environment variables using `python-dotenv`.

Never commit the `.env` file to Git.

---

## Resume Setup

The current application expects the resume at:

```text
uploads/resume.pdf
```

Therefore, create the directory if necessary:

```text
uploads/
└── resume.pdf
```

Place the candidate's PDF resume at that location.

---

## Build the Job Vector Database

Before generating recommendations, jobs need to be synchronized into ChromaDB.

Run:

```bash
python -m job_recommender.sync_jobs
```

This process:

1. Fetches jobs from the external API.
2. Normalizes job information.
3. Converts jobs into LangChain documents.
4. Generates content hashes.
5. Adds new jobs to ChromaDB.
6. Updates changed jobs.
7. Skips unchanged jobs.

The local vector database is stored in:

```text
chroma_db/
```

---

## Run the Application

After the vector database has been populated:

```bash
python -m job_recommender.app
```

The application will:

```text
Read Resume
     ↓
Extract Candidate Profile
     ↓
Search Similar Jobs
     ↓
Rank Jobs with Gemini
     ↓
Display Recommendations
```

---

## Example Output

```text
======================================================================
AI JOB RECOMMENDER
======================================================================

Reading Resume...

Extracting Candidate Profile...

======================================================================
Candidate Profile
======================================================================

Name            : John Doe
Email           : john@example.com
Phone           : +91XXXXXXXXXX
Preferred Role  : Full Stack Developer
Experience      : 2 Years
Education       : B.Tech Computer Science
Location        : Bangalore

Skills
  • Python
  • JavaScript
  • React
  • Node.js
  • SQL
  • Docker

Searching Similar Jobs...

======================================================================
TOP JOB RECOMMENDATIONS
======================================================================

1. Full Stack Developer

Company : Example Company
Location: Berlin
Match   : 87%

Reason  : Strong alignment with the candidate's full-stack development
          experience and JavaScript ecosystem.

Missing Skills
   - Kubernetes

----------------------------------------------------------------------
```

---

## Recommendation Strategy

The system uses a two-stage retrieval and ranking approach.

### Stage 1 — Semantic Retrieval

The candidate profile is transformed into a semantic search query:

```text
Preferred Role
Skills
Experience
Education
Location
```

This query is passed to ChromaDB.

The vector database retrieves semantically relevant jobs using MMR.

---

### Stage 2 — LLM Ranking

The retrieved jobs are passed to Gemini together with the candidate profile.

Gemini then:

```text
Candidate Profile
       +
Retrieved Jobs
       ↓
    Gemini
       ↓
Ranked Jobs
       +
Match Percentage
       +
Reason
       +
Missing Skills
```

This separates:

- **retrieval** — finding potentially relevant jobs
- **reasoning/ranking** — determining which retrieved jobs are the strongest matches

---

## Why ChromaDB?

ChromaDB provides local vector storage for the job listings.

Instead of performing a simple text search such as:

```text
"React Developer"
```

the system represents job descriptions as embeddings and searches based on semantic similarity.

For example:

```text
Candidate:
React + Node.js + TypeScript

Job:
JavaScript + React + Express + TypeScript
```

can still be considered relevant even when the wording is not identical.

---

## Why MMR?

Standard similarity search can return several jobs that are almost identical.

MMR attempts to balance:

```text
Relevance
+
Diversity
```

This allows the recommendation system to retrieve relevant jobs while reducing redundant results.

---

## Data Synchronization

Each normalized job document receives a SHA-256 content hash.

Example:

```text
Job Data
   ↓
Normalized Document
   ↓
SHA-256
   ↓
Content Hash
```

During synchronization:

```text
Does Job ID exist?
        │
   ┌────┴────┐
   │         │
  No        Yes
   │         │
  Add     Compare Hash
             │
       ┌─────┴─────┐
       │           │
     Same        Different
       │           │
      Skip       Update
```

This provides a simple incremental indexing strategy.

---

## Configuration

Important configuration values are centralized in `config.py`.

Current configuration includes:

```text
LLM_MODEL
EMBEDDING_MODEL
CHROMA_PATH
COLLECTION_NAME
TOP_K_RESULTS
FETCH_K_RESULTS
UPLOAD_FOLDER
CACHE_FOLDER
MAX_PAGES
REQUEST_TIMEOUT
```

The current retrieval configuration is:

```text
TOP_K_RESULTS = 20
FETCH_K_RESULTS = 50
```

---

## RAG Pipeline

This project can be viewed as a Retrieval-Augmented Generation pipeline:

```text
                    KNOWLEDGE SOURCE
                          │
                          ▼
                 Arbeitnow Job API
                          │
                          ▼
                   Job Normalization
                          │
                          ▼
                    Job Documents
                          │
                          ▼
                  Sentence Embeddings
                          │
                          ▼
                       ChromaDB
                          │
                          │
Candidate Resume          │
      │                   │
      ▼                   │
PDF Text Extraction       │
      │                   │
      ▼                   │
Gemini Profile Extraction │
      │                   │
      ▼                   │
Candidate Profile         │
      │                   │
      └───────┬───────────┘
              ▼
       Semantic Query
              │
              ▼
          MMR Retrieval
              │
              ▼
       Relevant Job Set
              │
              ▼
          Gemini LLM
              │
              ▼
     Ranked Recommendations
```

---

## Project Design Principles

### Separation of Responsibilities

The application separates different responsibilities into independent modules:

```text
PDF Processing
      ↓
Profile Extraction
      ↓
Job Retrieval
      ↓
Vector Storage
      ↓
Recommendation
      ↓
Application
```

This makes the system easier to extend and maintain.

### Structured Data Validation

Pydantic models are used to validate:

- Candidate profiles
- Jobs
- Recommendations
- Final recommendation responses

This reduces the risk of passing arbitrary LLM output through the application.

### External Data Normalization

External job API responses are converted into the project's own `Job` model.

This means the recommendation layer does not need to know the exact structure of the external API.

---

## Current Limitations

The current version is intentionally focused on the core recommendation pipeline.

### CLI Application

The current implementation is command-line based.

There is currently no:

- Streamlit UI
- React frontend
- REST API
- Authentication system
- User database

### Single Resume Path

The application currently reads:

```text
uploads/resume.pdf
```

rather than providing an interactive file-upload interface.

### Job Source

The current implementation uses the Arbeitnow Job Board API as its job source.

### Local Vector Database

ChromaDB is configured with a local persistence directory:

```text
chroma_db/
```

### LLM-Generated Match Percentage

The match percentage is generated by the LLM rather than being calculated using a deterministic mathematical scoring formula.

Therefore, the percentage should be interpreted as an AI-generated assessment rather than a statistically calibrated probability.

---

## Future Improvements

Possible extensions include:

- Streamlit web interface
- FastAPI backend
- Multiple resume uploads
- User authentication
- Persistent user profiles
- Job filtering by location
- Job filtering by experience level
- Salary-based filtering
- Remote/hybrid/on-site filtering
- Deterministic skill-match scoring
- Hybrid keyword + vector retrieval
- Job deduplication across multiple APIs
- Additional job APIs
- Scheduled job synchronization
- Recommendation history
- Saved jobs
- Application tracking
- Skill-gap learning recommendations
- Recommendation evaluation metrics
- Automated tests
- Docker deployment
- CI/CD pipeline

---

## Security

API keys and secrets should be stored in environment variables.

Example:

```env
GOOGLE_API_KEY=your_api_key
```

Do not commit:

```text
.env
```

to source control.

The repository's `.gitignore` already excludes environment files, virtual environments, generated ChromaDB data, cache data, IDE files, and Python build artifacts.

---

## Dependencies

The project uses the following major packages:

```text
langchain
langchain-community
langchain-google-genai
langchain-chroma
langchain-huggingface
sentence-transformers
chromadb
pydantic
python-dotenv
pypdf
requests
```

Install them using:

```bash
pip install -r requirements.txt
```

---

## Development Workflow

A typical development workflow is:

```text
1. Activate virtual environment
        ↓
2. Configure GOOGLE_API_KEY
        ↓
3. Add resume.pdf
        ↓
4. Synchronize jobs
        ↓
5. Build/update ChromaDB
        ↓
6. Run recommendation application
        ↓
7. Inspect ranked recommendations
```

Commands:

```bash
.venv\Scripts\activate

pip install -r requirements.txt

pip install -e .

python -m job_recommender.sync_jobs

python -m job_recommender.app
```

---

## License

No license has currently been specified for this repository.

If this project is intended to be publicly reusable, add an appropriate license such as MIT before presenting it as an open-source project.

---

## Author

**Sankha**

GitHub: `sankha4567`

---

## Project Summary

AI Job Recommender demonstrates a practical RAG architecture for personalized job discovery.

The core system combines:

```text
PDF Processing
+
LLM Structured Extraction
+
External Job API
+
Sentence Embeddings
+
ChromaDB
+
MMR Retrieval
+
LLM Ranking
+
Pydantic Validation
```

The result is an end-to-end AI pipeline that transforms an unstructured resume into a structured candidate profile, retrieves semantically relevant real-world job listings, and produces explainable job recommendations.