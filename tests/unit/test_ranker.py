from models import Job, JobRequirements
from analyzer import JobAnalysis
from ranker import rank_jobs


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


job_1 = Job(
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
    tags=["Data Analyst", "Remote"],
    job_types=["full-time"],
)


job_2 = Job(
    title="Marketing Analyst",
    company="Company B",
    location="India",
    remote=True,
    remote_scope="fully remote",
    url="https://example.com/job-b",
    source="Company Careers",
    description=(
        "Marketing Analyst requiring "
        "SEO and Google Analytics."
    ),
    tags=["Marketing", "Remote"],
    job_types=["full-time"],
)


job_3 = Job(
    title="Data Analyst",
    company="Company C",
    location="Germany",
    remote=True,
    remote_scope="fully remote",
    url="https://example.com/job-c",
    source="Company Careers",
    description=(
        "Data Analyst requiring "
        "Excel and SQL."
    ),
    tags=["Data Analyst", "Remote"],
    job_types=["full-time"],
)


analysis_1 = JobAnalysis(
    role_relevance="strong",
    required_experience_min=0,
    required_experience_max=2,
    required_skills=[
        "Excel",
        "SQL",
    ],
    preferred_skills=[],
    employment_type="full-time",
    remote_status="remote",
    remote_scope="fully remote",
    international_eligibility="unclear",
    visa_sponsorship="not_confirmed",
    salary_min=None,
    salary_max=None,
    salary_currency=None,
    evidence=[],
    concerns=[],
)


analysis_2 = JobAnalysis(
    role_relevance="weak",
    required_experience_min=None,
    required_experience_max=None,
    required_skills=[
        "SEO",
        "Google Analytics",
    ],
    preferred_skills=[],
    employment_type="full-time",
    remote_status="remote",
    remote_scope="fully remote",
    international_eligibility="unclear",
    visa_sponsorship="not_confirmed",
    salary_min=None,
    salary_max=None,
    salary_currency=None,
    evidence=[],
    concerns=[],
)


analysis_3 = JobAnalysis(
    role_relevance="strong",
    required_experience_min=0,
    required_experience_max=2,
    required_skills=[
        "Excel",
        "SQL",
    ],
    preferred_skills=[],
    employment_type="full-time",
    remote_status="remote",
    remote_scope="fully remote",
    international_eligibility="unclear",
    visa_sponsorship="not_confirmed",
    salary_min=None,
    salary_max=None,
    salary_currency=None,
    evidence=[],
    concerns=[],
)


jobs = [
    job_2,
    job_3,
    job_1,
]


analyses = {
    job_1.url: analysis_1,
    job_2.url: analysis_2,
    job_3.url: analysis_3,
}


ranked = rank_jobs(
    jobs,
    requirements,
    analyses,
)


print("RANKED JOBS")
print("=" * 60)

for item in ranked:

    print(
        f"{item.rank}. "
        f"{item.job.title} — "
        f"{item.job.company}"
    )

    print(
        f"   Score: "
        f"{item.score.total_score}/100"
    )

    print(
        f"   Confidence: "
        f"{item.score.confidence}"
    )

    print(
        f"   Location: "
        f"{item.job.location}"
    )

    print(
        f"   Remote: "
        f"{item.job.remote}"
    )

    print()