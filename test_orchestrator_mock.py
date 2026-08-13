from models import Job
import orchestrator


# -------------------------------------------------
# Mock jobs
# -------------------------------------------------

mock_jobs = [
    Job(
        title="Junior Data Analyst",
        company="Company A",
        location="India",
        remote=True,
        remote_scope=None,
        visa_sponsorship=None,
        url="https://company-a.com/jobs/data-analyst",
        source="Company Careers",
        description=(
            "Full-time remote Junior Data Analyst role. "
            "Requires Excel and SQL."
        ),
        tags=["Data Analyst", "Remote"],
        job_types=["full-time"],
    ),
    Job(
        title="Data Analyst",
        company="Company B",
        location="Germany",
        remote=True,
        remote_scope=None,
        visa_sponsorship=None,
        url="https://company-b.com/jobs/data-analyst",
        source="Company Careers",
        description="Full-time remote Data Analyst role.",
        tags=["Data Analyst", "Remote"],
        job_types=["full-time"],
    ),
    Job(
        title="Marketing Analyst",
        company="Company C",
        location="India",
        remote=True,
        remote_scope=None,
        visa_sponsorship=None,
        url="https://company-c.com/jobs/marketing-analyst",
        source="Company Careers",
        description="Full-time remote Marketing Analyst role.",
        tags=["Marketing", "Remote"],
        job_types=["full-time"],
    ),
]


# -------------------------------------------------
# Mock requirements parser
# -------------------------------------------------

def mock_parse_requirements(user_query):
    from requirements import JobRequirements
    from models import CandidateProfile

    requirements = JobRequirements(
        role="data analyst",
        location="India",
        remote_required=True,
        hybrid_allowed=False,
        min_experience_years=0,
        max_experience_years=2,
        employment_types=["full-time"],
        skills=["Excel", "SQL"],
        salary_min=None,
        salary_max=None,
        salary_currency=None,
        applicant_country=None,
        visa_required=False,
        keywords=["junior"],
    )

    candidate_profile = CandidateProfile(
        experience_years=1,
        skills=["Excel", "SQL"],
        education=[],
        current_country="India",
        desired_locations=["India"],
        desired_employment_types=["full-time"],
    )

    return requirements, candidate_profile


# -------------------------------------------------
# Mock search strategy
# -------------------------------------------------

def mock_generate_search_queries(requirements):
    return [
        "junior data analyst jobs India",
    ]


# -------------------------------------------------
# Mock discovery
# -------------------------------------------------

def mock_discover_jobs(requirements):
    return mock_jobs


# -------------------------------------------------
# Mock analysis
# -------------------------------------------------

def mock_analyze_job(job, requested_role=None):
    from analyzer import JobAnalysis

    if job.company == "Company A":
        return JobAnalysis(
            role_relevance="strong",
            required_experience_min=0,
            required_experience_max=2,
            required_skills=["Excel", "SQL"],
            preferred_skills=[],
            employment_type="full-time",
            remote_status="remote",
            remote_scope=None,
            international_eligibility="unclear",
            visa_sponsorship="not_confirmed",
            salary_min=None,
            salary_max=None,
            salary_currency=None,
            evidence=[
                "The position is a Junior Data Analyst role.",
                "The listing requires Excel and SQL.",
                "The position is full-time and remote.",
                "The listing states 0–2 years of experience.",
            ],
            concerns=[
                "Visa sponsorship is not confirmed.",
                "Salary information is not provided.",
            ],
        )

    return JobAnalysis(
        role_relevance="weak",
        required_experience_min=None,
        required_experience_max=None,
        required_skills=[],
        preferred_skills=[],
        employment_type="full-time",
        remote_status="remote",
        remote_scope=None,
        international_eligibility="unclear",
        visa_sponsorship="not_confirmed",
        salary_min=None,
        salary_max=None,
        salary_currency=None,
        evidence=[],
        concerns=[],
    )


# -------------------------------------------------
# Replace external/LLM functions
# -------------------------------------------------

orchestrator.parse_requirements = mock_parse_requirements
orchestrator.generate_search_queries = mock_generate_search_queries
orchestrator.discover_jobs = mock_discover_jobs
orchestrator.analyze_job = mock_analyze_job


# -------------------------------------------------
# Run orchestrator
# -------------------------------------------------

result = orchestrator.run_job_search(
    "Find remote junior data analyst jobs in India."
)


# -------------------------------------------------
# Inspect results
# -------------------------------------------------

print()
print("ORCHESTRATOR MOCK RESULTS")

print(
    "Requirements:",
    result["requirements"],
)

print(
    "Jobs returned:",
    len(result["jobs"]),
)

for index, job in enumerate(
    result["jobs"],
    start=1,
):
    print()
    print(
        f"{index}. "
        f"{job.title} — "
        f"{job.company}"
    )

    print(
        "Score:",
        job.score,
    )

    print(
        "Confidence:",
        job.confidence,
    )


# -------------------------------------------------
# Assertions
# -------------------------------------------------

assert result["message"] is None, (
    "Orchestrator unexpectedly returned an error."
)

assert len(result["jobs"]) == 1, (
    "Expected exactly one job after filtering."
)

assert result["jobs"][0].company == "Company A", (
    "Company A should be the surviving job."
)


print()
print("ORCHESTRATOR MOCK TEST: PASSED")