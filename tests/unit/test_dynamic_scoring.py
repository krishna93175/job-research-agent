from models import Job, JobRequirements
from analyzer import JobAnalysis
from match_scorer import score_job


job = Job(
    title="Junior Data Analyst",
    company="Example Company",
    location="India",
    remote=True,
    remote_scope="fully remote",
    url="https://example.com/job",
    source="Company Careers",
    description=(
        "Junior Data Analyst role requiring "
        "Excel and SQL."
    ),
    tags=["Data Analyst", "Remote"],
    job_types=["full-time"],
)


analysis = JobAnalysis(
    role_relevance="strong",
    required_experience_min=0,
    required_experience_max=2,
    required_skills=["Excel", "SQL"],
    preferred_skills=["Power BI"],
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


users = [
    (
        "User 1 - Remote Data Analyst",
        JobRequirements(
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
        ),
    ),
    (
        "User 2 - Marketing Specialist",
        JobRequirements(
            role="marketing specialist",
            location="India",
            remote_required=True,
            hybrid_allowed=False,
            min_experience_years=None,
            max_experience_years=None,
            employment_types=["full-time"],
            skills=["SEO"],
            salary_min=None,
            salary_max=None,
            salary_currency=None,
            applicant_country="India",
            visa_required=False,
            keywords=[],
        ),
    ),
    (
        "User 3 - Data Analyst + Visa",
        JobRequirements(
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
            visa_required=True,
            keywords=[],
        ),
    ),
]


for name, requirements in users:

    result = score_job(
        job,
        requirements,
        analysis,
    )

    print("=" * 60)
    print(name)
    print("=" * 60)

    print(
        f"Score: "
        f"{result.total_score}/100"
    )

    print(
        f"Confidence: "
        f"{result.confidence}"
    )

    for component in result.components:

        print(
            f"{component.name}: "
            f"{component.points}/"
            f"{component.max_points} "
            f"[{component.status}]"
        )

    print()