"""
AI Job Recommender — Streamlit UI entry point.

Run with:
    streamlit run src/job_recommender/ui/streamlit_app.py
"""

import json
import logging

import streamlit as st

from job_recommender.core.extractor import ProfileExtractor
from job_recommender.core.pdf_reader import PDFReader
from job_recommender.core.recommender import JobRecommender
from job_recommender.exceptions import (
    JobRecommendationError,
    ProfileExtractionError,
    ResumeParseError,
)
from job_recommender.models import CandidateProfile, RecommendationResponse
from job_recommender.ui.components import (
    STEPS,
    inject_css,
    render_job_card,
    render_profile_card,
    render_progress_steps,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Page configuration (must be the first Streamlit call)
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AI Job Recommender",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/artificial-intelligence.png",
        width=64,
    )
    st.title("AI Job Recommender")
    st.caption("Powered by Gemini · LangChain · ChromaDB")
    st.divider()

    st.markdown("### How it works")
    st.markdown(
        """
1. **Upload** your resume PDF
2. **AI extracts** your skills & profile
3. **Vector search** finds relevant jobs
4. **Gemini ranks** matches with explanations
        """
    )

    st.divider()
    st.markdown("### About")
    st.markdown(
        "This app uses semantic search across thousands of job listings "
        "and large-language model reasoning to surface the best-fit roles for you."
    )

    st.divider()
    st.markdown("### 🗄️ Job Database")

    # Show current job count
    try:
        from job_recommender.core.vector_store import VectorStore
        _vs = VectorStore()
        _count = _vs.count()
        if _count > 0:
            st.success(f"✅ {_count:,} jobs indexed")
        else:
            st.warning("⚠️ Database is empty")
    except Exception:
        st.error("Could not connect to DB")
        _count = 0

    if st.button("🔄 Sync Jobs from API", use_container_width=True,
                 help="Fetches latest jobs from Arbeitnow and indexes them into ChromaDB. Takes ~3–5 min."):
        from job_recommender.services.job_indexer import JobIndexer
        with st.spinner("Syncing jobs… this takes 3–5 minutes ⏳"):
            try:
                result = JobIndexer().sync()
                st.success(
                    f"✅ Sync complete!  "
                    f"Added **{result.added}** · Updated **{result.updated}** · "
                    f"Skipped **{result.skipped}**  \n"
                    f"Total in DB: **{result.total_in_db:,}**"
                )
                st.rerun()
            except Exception as exc:
                st.error(f"Sync failed: {exc}")


# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------

st.markdown("## 🎯 Find Your Perfect Job Match")
st.markdown(
    "Upload your resume and let AI do the heavy lifting — "
    "no keyword matching, just semantic understanding."
)
st.write("")

# ---- Upload widget ----
uploaded_file = st.file_uploader(
    "Drag & drop your resume (PDF)",
    type=["pdf"],
    help="Only PDF files are supported. Your file is processed in-memory and never stored.",
)

if uploaded_file is None:
    st.info("👆 Upload your resume PDF to get started.", icon="📄")
    st.stop()

# ---- Trigger analysis ----
col_btn, col_spacer = st.columns([1, 4])
with col_btn:
    analyze_clicked = st.button(
        "🚀 Analyse & Recommend",
        type="primary",
        use_container_width=True,
    )

if not analyze_clicked:
    st.stop()

# ---------------------------------------------------------------------------
# Processing pipeline
# ---------------------------------------------------------------------------

st.divider()
st.markdown("### ⚙️ Processing your resume…")

step_placeholder = st.empty()
status_placeholder = st.empty()


def update_step(step: int, message: str = "") -> None:
    with step_placeholder.container():
        render_progress_steps(step)
    if message:
        status_placeholder.caption(message)


# ---- Step 0: Read PDF ----
update_step(0, "Reading your PDF…")

try:
    pdf_bytes: bytes = uploaded_file.read()
    resume_text: str = PDFReader.extract_text_from_bytes(
        pdf_bytes, filename=uploaded_file.name
    )
except ResumeParseError as exc:
    st.error(f"**Could not read your PDF:** {exc}")
    st.stop()

# ---- Step 1: Extract profile ----
update_step(1, "Extracting your candidate profile with AI…")

try:
    extractor = ProfileExtractor()
    profile: CandidateProfile = extractor.extract(resume_text)
except ProfileExtractionError as exc:
    st.error(f"**Profile extraction failed:** {exc}")
    st.stop()

# ---- Step 2: Retrieve jobs ----
update_step(2, "Searching job database for relevant listings…")

try:
    recommender = JobRecommender()
    # We split retrieval from ranking so we can update the step indicator
    jobs = recommender._retrieve_jobs(profile)  # noqa: SLF001 (intentional internal use)
except Exception as exc:
    st.error(f"**Job retrieval failed:** {exc}")
    st.stop()

if not jobs:
    update_step(len(STEPS))
    st.warning(
        "⚠️ The job database appears to be empty. "
        "Please run `sync-jobs` first to index job listings.",
        icon="🗄️",
    )
    st.stop()

# ---- Step 3: Rank matches ----
update_step(3, "Ranking and explaining the best matches with Gemini…")

try:
    response: RecommendationResponse = recommender.recommend(profile)
except JobRecommendationError as exc:
    st.error(f"**Ranking failed:** {exc}")
    st.stop()

# Done
update_step(len(STEPS))
status_placeholder.empty()

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

st.divider()

# ---- Candidate profile card ----
st.markdown("### 👤 Your Profile")
render_profile_card(profile)

# ---- Recommendations ----
st.markdown(f"### 💼 Top Job Matches ({len(response.recommendations)} found)")

if not response.recommendations:
    st.warning("No recommendations were returned. Try re-running the analysis.")
    st.stop()

for i, rec in enumerate(response.recommendations, start=1):
    render_job_card(rec, i)

# ---- Download results ----
st.divider()
st.markdown("### 📥 Download Results")

results_payload = {
    "profile": profile.model_dump(),
    "recommendations": [r.model_dump() for r in response.recommendations],
}

st.download_button(
    label="⬇️ Download as JSON",
    data=json.dumps(results_payload, indent=2),
    file_name="job_recommendations.json",
    mime="application/json",
    use_container_width=False,
)
