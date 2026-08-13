from models import Job, JobRequirements

from requirements_filter import filter_jobs


requirements = JobRequirements(
    role="data analyst",
    location="India",
    remote_required=True,
    hybrid_allowed=False,
    min_experience_years=None,
    max_experience_years=None,
    employment_types=["full-time"],
    skills=["Excel", "SQL"],
    salary_min=None,
    salary_max=None,
    salary_currency=None,
    applicant_country="India",
    visa_required=False,
    keywords=[],
)


jobs = [
    Job(
        title="Junior Data Analyst",
        company="Company A",
        location="India",
        remote=True,
        remote_scope=None,
        url="https://example.com/1",
        source="Company Careers",
        description=(
            "Analyze business data using "
            "Excel and SQL."
        ),
        tags=["Data", "Analytics"],
        job_types=["full-time"],
    ),

    Job(
        title="Data Analyst",
        company="Company B",
        location="India",
        remote=False,
        remote_scope=None,
        url="https://example.com/2",
        source="LinkedIn",
        description=(
            "Data analysis using Excel and SQL."
        ),
        tags=[],
        job_types=["full-time"],
    ),

    Job(
        title="Marketing Specialist",
        company="Company C",
        location="India",
        remote=True,
        remote_scope=None,
        url="https://example.com/3",
        source="LinkedIn",
        description=(
            "Digital marketing and social media."
        ),
        tags=["Marketing"],
        job_types=["full-time"],
    ),

    Job(
        title="Junior Data Analyst",
        company="Company D",
        location="India",
        remote=True,
        remote_scope=None,
        url="https://example.com/4",
        source="LinkedIn",
        description=(
            "Analyze data using Excel and SQL."
        ),
        tags=[],
        job_types=["part-time"],
    ),
]


matched_jobs = filter_jobs(
    jobs,
    requirements,
)


print(
    "JOBS BEFORE FILTERING:",
    len(jobs),
)

print(
    "JOBS AFTER FILTERING:",
    len(matched_jobs),
)

print()

for number, job in enumerate(
    matched_jobs,
    start=1,
):
    print(
        f"{number}. "
        f"{job.title} — "
        f"{job.company}"
    )