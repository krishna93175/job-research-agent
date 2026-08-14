from models import Job

from analyzer import build_analysis_prompt


job = Job(
    title="Junior Data Analyst",
    company="Example Company",
    location="India",
    remote=True,
    remote_scope=None,
    url="https://example.com/job",
    source="Company Careers",
    description="""
    We are looking for a Junior Data Analyst to join our
    remote team.

    Responsibilities include analyzing business data,
    preparing reports, and creating dashboards.

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


prompt = build_analysis_prompt(
    job,
    requested_role="data analyst",
)


print("ANALYZER PROMPT")
print("=" * 60)
print(prompt)