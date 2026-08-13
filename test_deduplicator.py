from models import Job
from deduplicator import deduplicate_jobs


jobs = [
    Job(
        title="Junior Data Analyst",
        company="Example Company",
        location="India",
        remote=True,
        remote_scope=None,
        url="https://linkedin.com/jobs/view/123",
        source="LinkedIn",
        description="",
    ),

    # Same job, different URL.
    Job(
        title="Junior Data Analyst",
        company="Example Company",
        location="India",
        remote=True,
        remote_scope=None,
        url="https://example.com/careers/data-analyst",
        source="Company Careers",
        description="",
    ),

    # Different company — must remain.
    Job(
        title="Junior Data Analyst",
        company="Another Company",
        location="India",
        remote=True,
        remote_scope=None,
        url="https://another.com/jobs/456",
        source="Company Careers",
        description="",
    ),

    # Different title — must remain.
    Job(
        title="Senior Data Analyst",
        company="Example Company",
        location="India",
        remote=True,
        remote_scope=None,
        url="https://example.com/careers/senior-data-analyst",
        source="Company Careers",
        description="",
    ),
]


print("JOBS BEFORE DEDUPLICATION:")
print(len(jobs))

print()

unique_jobs = deduplicate_jobs(jobs)

print("JOBS AFTER DEDUPLICATION:")
print(len(unique_jobs))

print()

for number, job in enumerate(
    unique_jobs,
    start=1,
):
    print(
        f"{number}. "
        f"{job.title} — "
        f"{job.company} — "
        f"{job.source}"
    )