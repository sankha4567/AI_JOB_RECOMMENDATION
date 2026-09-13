"""
Reusable Streamlit UI components for the AI Job Recommender.
"""

import streamlit as st

from job_recommender.models import CandidateProfile, JobRecommendation


# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------

def _match_color(pct: int) -> str:
    """Return a hex colour based on match percentage."""
    if pct >= 75:
        return "#22c55e"   # green
    if pct >= 50:
        return "#f59e0b"   # amber
    return "#ef4444"       # red


# ---------------------------------------------------------------------------
# CSS injection (called once on app startup)
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
<style>
/* ---- Global ---- */
.block-container { padding-top: 2rem; }

/* ---- Skill badges ---- */
.badge-container { display: flex; flex-wrap: wrap; gap: 6px; margin: 4px 0 12px; }
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 500;
    line-height: 1.5;
}
.badge-blue  { background: #dbeafe; color: #1e40af; }
.badge-red   { background: #fee2e2; color: #991b1b; }
.badge-green { background: #dcfce7; color: #166534; }
.badge-gray  { background: #f1f5f9; color: #475569; }

/* ---- Candidate profile card ---- */
.profile-card {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border-radius: 16px;
    padding: 28px 32px;
    color: #f8fafc;
    margin-bottom: 24px;
}
.profile-name  { font-size: 1.6rem; font-weight: 700; margin-bottom: 4px; }
.profile-role  { font-size: 1rem; color: #94a3b8; margin-bottom: 16px; }
.profile-meta  { display: flex; flex-wrap: wrap; gap: 16px; font-size: 0.88rem; color: #cbd5e1; margin-bottom: 16px; }
.profile-meta span::before { margin-right: 4px; }

/* ---- Job card ---- */
.job-card {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 14px;
    background: #ffffff;
}
.job-title   { font-size: 1.1rem; font-weight: 600; color: #0f172a; }
.job-company { font-size: 0.9rem; color: #64748b; margin-bottom: 8px; }

/* ---- Match bar ---- */
.match-label { font-size: 0.8rem; color: #64748b; margin-bottom: 2px; }
.match-bar-bg { background: #f1f5f9; border-radius: 999px; height: 10px; }
.match-bar-fill {
    height: 10px;
    border-radius: 999px;
    transition: width 0.4s ease;
}

/* ---- Apply button ---- */
.apply-btn {
    display: inline-block;
    padding: 8px 20px;
    background: #6366f1;
    color: #fff !important;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    text-decoration: none;
    margin-top: 10px;
}
.apply-btn:hover { background: #4f46e5; }

/* ---- Step indicator ---- */
.step-row { display: flex; align-items: center; gap: 10px; padding: 6px 0; }
.step-dot  {
    width: 10px; height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
}
.step-done    { background: #22c55e; }
.step-active  { background: #6366f1; animation: pulse 1s infinite; }
.step-pending { background: #e2e8f0; }
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}
</style>
"""


def inject_css() -> None:
    """Inject global custom CSS into the Streamlit app (call once)."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Candidate profile card
# ---------------------------------------------------------------------------

def render_profile_card(profile: CandidateProfile) -> None:
    """Render a styled candidate profile card."""

    meta_parts: list[str] = []
    if profile.email:
        meta_parts.append(f"✉️ {profile.email}")
    if profile.phone:
        meta_parts.append(f"📞 {profile.phone}")
    if profile.location:
        meta_parts.append(f"📍 {profile.location}")
    if profile.experience:
        meta_parts.append(f"💼 {profile.experience} yrs experience")
    if profile.education:
        meta_parts.append(f"🎓 {profile.education}")

    meta_html = "".join(f"<span>{p}</span>" for p in meta_parts)

    skills_html = "".join(
        f'<span class="badge badge-blue">{s}</span>'
        for s in profile.skills
    )

    st.markdown(
        f"""
        <div class="profile-card">
            <div class="profile-name">{profile.name or "Candidate"}</div>
            <div class="profile-role">{profile.preferred_role or "Not specified"}</div>
            <div class="profile-meta">{meta_html}</div>
            <div class="badge-container">{skills_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Job recommendation card
# ---------------------------------------------------------------------------

def render_job_card(rec: JobRecommendation, index: int) -> None:
    """Render an expandable job recommendation card."""

    color = _match_color(rec.match_percentage)
    should_apply_icon = "✅" if rec.should_apply else "❌"
    header = f"#{index} · {rec.title} @ {rec.company} — {rec.match_percentage}% match"

    with st.expander(header, expanded=(index == 1)):
        # Match bar
        st.markdown(
            f"""
            <div class="match-label">Match Score</div>
            <div class="match-bar-bg">
                <div class="match-bar-fill"
                     style="width:{rec.match_percentage}%; background:{color};">
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")  # spacing

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**🏢 Company:** {rec.company}")
            st.markdown(f"**📍 Location:** {rec.location}")
        with col2:
            st.markdown(f"**Should Apply:** {should_apply_icon}")
            st.markdown(f"**Match:** `{rec.match_percentage}%`")

        st.markdown("**💡 Why this role matches you:**")
        st.info(rec.reason)

        if rec.missing_skills:
            st.markdown("**⚠️ Missing Skills:**")
            badges = "".join(
                f'<span class="badge badge-red">{s}</span>'
                for s in rec.missing_skills
            )
            st.markdown(
                f'<div class="badge-container">{badges}</div>',
                unsafe_allow_html=True,
            )

        if rec.learning_topics:
            st.markdown("**📚 Learning Topics to Close the Gap:**")
            for topic in rec.learning_topics:
                st.markdown(f"- {topic}")

        if rec.url:
            st.markdown(
                f'<a class="apply-btn" href="{rec.url}" target="_blank">Apply Now →</a>',
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# Progress stepper
# ---------------------------------------------------------------------------

STEPS = [
    "📄 Reading PDF",
    "🧠 Extracting Profile",
    "🔍 Searching Jobs",
    "⭐ Ranking Matches",
]


def render_progress_steps(current_step: int) -> None:
    """
    Render a vertical step indicator.

    Args:
        current_step: 0-based index of the step currently executing.
                      Pass ``len(STEPS)`` when all steps are done.
    """
    lines: list[str] = []
    for i, label in enumerate(STEPS):
        if i < current_step:
            dot_class = "step-done"
        elif i == current_step:
            dot_class = "step-active"
        else:
            dot_class = "step-pending"

        lines.append(
            f'<div class="step-row">'
            f'<div class="step-dot {dot_class}"></div>'
            f'<span>{label}</span>'
            f"</div>"
        )

    st.markdown(
        f'<div>{"".join(lines)}</div>',
        unsafe_allow_html=True,
    )
