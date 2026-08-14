from models import Job
from analyzer import analyze_job


job = Job(
    title="Junior Data Analyst",
    company="Example Company",
    location="India",
    remote=True,
    remote_scope=None,
    visa_sponsorship=None,
    url="https://example.com/job",
    source="Company Careers",
    description="""
    We are looking for a Junior Data Analyst to join our
    remote team.

    Requirements:
    - 0–2 years of experience
    - Strong Excel skills
    - SQL knowledge
    - Good analytical and communication skills

    Power BI experience is preferred.

    This is a full-time remote position.
    """,
    tags=["Data Analyst", "Remote"],
    job_types=["full-time"],
)


analysis = analyze_job(
    job,
    requested_role="data analyst",
)


print("ROLE RELEVANCE:", analysis.role_relevance)
print(
    "EXPERIENCE:",
    analysis.required_experience_min,
    "-",
    analysis.required_experience_max,
)
print(
    "REQUIRED SKILLS:",
    analysis.required_skills,
)
print(
    "PREFERRED SKILLS:",
    analysis.preferred_skills,
)
print(
    "EMPLOYMENT:",
    analysis.employment_type,
)
print(
    "REMOTE:",
    analysis.remote_status,
)
print(
    "VISA:",
    analysis.visa_sponsorship,
)
print(
    "EVIDENCE:",
    analysis.evidence,
)
print(
    "CONCERNS:",
    analysis.concerns,
)


assert analysis.role_relevance in {
    "strong",
    "moderate",
    "weak",
    "unclear",
}

assert analysis.remote_status in {
    "remote",
    "hybrid",
    "onsite",
    "unclear",
}

print()
print("GROQ ANALYZER TEST: PASSED")