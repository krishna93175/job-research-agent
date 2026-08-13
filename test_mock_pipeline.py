from models import Job, JobRequirements
from deduplicator import deduplicate_jobs
from requirements_filter import filter_jobs


# -------------------------------------------------
# Mock jobs from multiple discovery sources
# -------------------------------------------------

jobs = [
    # Valid job from Arbeitnow
    Job(
        title="Junior Data Analyst",
        company="Company A",
        location="India",
        remote=True,
        remote_scope=None,
        visa_sponsorship=None,
        url="https://company-a.com/jobs/data-analyst",
        source="Arbeitnow",
        description="Full-time remote Junior Data Analyst role.",
        tags=["Data Analyst"],
        job_types=["full-time"],
    ),

    # Same job discovered through web search
    # This should be removed by deduplication.
    Job(
        title="Junior Data Analyst",
        company="Company A",
        location="India",
        remote=True,
        remote_scope=None,
        visa_sponsorship=None,
        url="https://company-a.com/jobs/data-analyst",
        source="Company Careers",
        description="Full-time remote Junior Data Analyst role.",
        tags=["Data Analyst"],
        job_types=["full-time"],
    ),

    # Wrong location
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
        tags=["Data Analyst"],
        job_types=["full-time"],
    ),

    # Correct location but not remote
    Job(
        title="Data Analyst",
        company="Company C",
        location="India",
        remote=False,
        remote_scope=None,
        visa_sponsorship=None,
        url="https://company-c.com/jobs/data-analyst",
        source="Arbeitnow",
        description="Full-time Data Analyst role.",
        tags=["Data Analyst"],
        job_types=["full-time"],
    ),

    # Wrong role
    Job(
        title="Marketing Analyst",
        company="Company D",
        location="India",
        remote=True,
        remote_scope=None,
        visa_sponsorship=None,
        url="https://company-d.com/jobs/marketing-analyst",
        source="Company Careers",
        description="Full-time remote Marketing Analyst role.",
        tags=["Marketing"],
        job_types=["full-time"],
    ),
]


# -------------------------------------------------
# Requirements
# -------------------------------------------------

requirements = JobRequirements(
    role="data analyst",
    location="India",
    remote_required=True,
    hybrid_allowed=False,
    employment_types=["full-time"],
)


# -------------------------------------------------
# Step 1 — Before deduplication
# -------------------------------------------------

print("JOBS BEFORE DEDUPLICATION:")
print(len(jobs))


# -------------------------------------------------
# Step 2 — Deduplicate
# -------------------------------------------------

unique_jobs = deduplicate_jobs(
    jobs
)

print()
print("JOBS AFTER DEDUPLICATION:")
print(len(unique_jobs))

for index, job in enumerate(
    unique_jobs,
    start=1,
):
    print(
        f"{index}. "
        f"{job.title} — "
        f"{job.company} — "
        f"{job.source}"
    )


# -------------------------------------------------
# Step 3 — Apply hard requirements
# -------------------------------------------------

filtered_jobs = filter_jobs(
    unique_jobs,
    requirements,
)

print()
print("JOBS AFTER FILTERING:")
print(len(filtered_jobs))

for index, job in enumerate(
    filtered_jobs,
    start=1,
):
    print(
        f"{index}. "
        f"{job.title} — "
        f"{job.company} — "
        f"{job.location} — "
        f"Remote: {job.remote}"
    )


# -------------------------------------------------
# Step 4 — Assertions
# -------------------------------------------------

assert len(jobs) == 5, (
    "Expected 5 mock jobs."
)

assert len(unique_jobs) == 4, (
    "Expected 4 jobs after deduplication."
)

assert len(filtered_jobs) == 1, (
    "Expected exactly 1 job after filtering."
)

assert filtered_jobs[0].company == "Company A", (
    "The surviving job should be Company A."
)

print()
print("MOCK PIPELINE TEST: PASSED")