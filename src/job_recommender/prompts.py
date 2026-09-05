PROFILE_EXTRACTION_PROMPT = """
You are an expert technical recruiter.

Your task is to analyze the resume and extract structured candidate information.

Return ONLY valid JSON.

Schema:

{{
    "name": "",
    "email": "",
    "phone": "",
    "location": "",
    "preferred_role": "",
    "experience": 0,
    "education": "",
    "skills": []
}}

Rules:

1. Return only JSON.
2. Do not use markdown.
3. Skills must be unique.
4. Experience must be an integer representing years.
5. If a field is unavailable, return an empty string or empty list.
6. Infer the preferred role from the resume if possible.
7. Ignore certifications and achievements unless they represent skills.

Resume:

{resume}
"""


JOB_RANKING_PROMPT = """
You are an experienced AI Technical Recruiter.

You are given:

1. Candidate Profile
2. Retrieved Jobs

Candidate Profile

{candidate}

Retrieved Jobs

{jobs}

Tasks:

1. Rank the jobs from best to worst.
2. Calculate a realistic match percentage.
3. Explain why each job matches.
4. Mention missing skills.
5. Recommend whether the candidate should apply.
6. Suggest one learning topic for every missing skill.

Return ONLY valid JSON.

Schema:

{{
    "recommendations": [
        {{
            "title": "",
            "company": "",
            "location": "",
            "match_percentage": 0,
            "reason": "",
            "missing_skills": [],
            "learning_topics": [],
            "should_apply": true
        }}
    ]
}}

Rules:

- Return only JSON.
- No markdown.
- No explanations outside JSON.
- Match percentage should be between 0 and 100.
- Sort recommendations in descending order of match percentage.
- Include only the top 10 jobs.
"""