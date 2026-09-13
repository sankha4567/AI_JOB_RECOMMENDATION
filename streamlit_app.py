# Root-level entry point for Streamlit Cloud deployment.
#
# Streamlit Cloud runs:  streamlit run streamlit_app.py
# Set this file as the "Main file path" in Streamlit Cloud settings.
#
# The package is installed via the first line in requirements.txt (-e .)
# so all imports from job_recommender.* resolve correctly.

import runpy

runpy.run_module(
    "job_recommender.ui.streamlit_app",
    run_name="__main__",
    alter_sys=True,
)
