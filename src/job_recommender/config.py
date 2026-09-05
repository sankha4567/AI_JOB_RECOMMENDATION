import os
from dotenv import load_dotenv

load_dotenv()

# ==============================
# Gemini Configuration
# ==============================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

LLM_MODEL = "gemini-3.5-flash"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ==============================
# Chroma Configuration
# ==============================

CHROMA_PATH = "chroma_db"

COLLECTION_NAME = "ai_jobs"

TOP_K_RESULTS = 20

FETCH_K_RESULTS = 50

# ==============================
# Resume
# ==============================

UPLOAD_FOLDER = "uploads"

RESUME_PATH = os.path.join(
    UPLOAD_FOLDER,
    "resume.pdf"
)

# ==============================
# Cache
# ==============================

CACHE_FOLDER = "jobs_cache"

JOB_CACHE = os.path.join(
    CACHE_FOLDER,
    "jobs.json"
)

# ==============================
# Job API
# ==============================

JOBS_PER_PAGE = 100

MAX_PAGES = 10

REQUEST_TIMEOUT = 30