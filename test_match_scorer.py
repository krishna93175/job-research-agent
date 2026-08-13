from models import Job, JobRequirements

from match_scorer import score_job


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


job = Job(
    title="Junior Data Analyst",
    company="Example Company",
    location="India",
    remote=True,
    remote_scope=None,
    url="https://example.com/job",
    source="Company Careers",
    description=(
        "Analyze business data using "
        "Excel and SQL."
    ),
    tags=["Data", "Analytics"],
    job_types=["full-time"],
)


result = score_job(
    job,
    requirements,
)


print("JOB")
print(
    f"{job.title} — {job.company}"
)

print()

print(
    f"SCORE: "
    f"{result.total_score}/"
    f"{result.max_score}"
)

print(
    f"CONFIDENCE: "
    f"{result.confidence}"
)

print()

print("BREAKDOWN")

for component in result.components:

    print(
        f"{component.name}: "
        f"{component.points}/"
        f"{component.max_points} "
        f"[{component.status}]"
    )

    print(
        f"  {component.reason}"
    )