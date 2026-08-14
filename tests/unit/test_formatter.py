from models import Job, JobRequirements
from analyzer import JobAnalysis
from match_scorer import score_job
from ranker import rank_jobs
from formatter import (
    format_ranked_jobs,
    print_formatted_jobs,
)


requirements = JobRequirements(
    role="data analyst",
    location="India",
    remote_required=True,
    hybrid_allowed=False,
    min_experience_years=1,
    max_experience_years=1,
    employment_types=["full-time"],
    skills=["Excel", "SQL"],
    salary_min=None,
    salary_max=None,
    salary_currency=None,
    applicant_country="India",
    visa_required=False,
    keywords=[],
)


job = Job(
    title="Junior Data Analyst",
    company="Company A",
    location="India",
    remote=True,
    remote_scope="fully remote",
    url="https://example.com/job-a",
    source="Company Careers",
    description=(
        "Junior Data Analyst requiring "
        "Excel and SQL."
    ),
    tags=[
        "Data Analyst",
        "Remote",
    ],
    job_types=[
        "full-time",
    ],
)


analysis = JobAnalysis(
    role_relevance="strong",
    required_experience_min=0,
    required_experience_max=2,
    required_skills=[
        "Excel",
        "SQL",
    ],
    preferred_skills=[
        "Power BI",
    ],
    employment_type="full-time",
    remote_status="remote",
    remote_scope="fully remote",
    international_eligibility="unclear",
    visa_sponsorship="not_confirmed",
    salary_min=None,
    salary_max=None,
    salary_currency=None,
    evidence=[
        "The listing states 0–2 years of experience.",
        "Excel and SQL are listed as requirements.",
        "The position is full-time and fully remote.",
    ],
    concerns=[
        "Visa sponsorship is not confirmed.",
        "Salary information is not provided.",
    ],
)


score = score_job(
    job,
    requirements,
    analysis,
)


# Create a RankedJob manually for this test.
from ranker import RankedJob


ranked_job = RankedJob(
    rank=1,
    job=job,
    score=score,
    analysis=analysis,
)


formatted = format_ranked_jobs(
    [ranked_job]
)


print_formatted_jobs(
    formatted
)