from models import Job, JobRequirements
import job_discovery


# -------------------------------------------------
# Mock Arbeitnow results
# -------------------------------------------------

mock_arbeitnow_jobs = [
    {
        "title": "Junior Data Analyst",
        "company_name": "Company A",
        "location": "India",
        "remote": True,
        "url": "https://company-a.com/jobs/data-analyst",
        "description": "Full-time remote Junior Data Analyst role.",
        "tags": ["Data Analyst"],
        "job_types": ["full-time"],
    },
    {
        "title": "Data Analyst",
        "company_name": "Company C",
        "location": "India",
        "remote": False,
        "url": "https://company-c.com/jobs/data-analyst",
        "description": "Full-time Data Analyst role.",
        "tags": ["Data Analyst"],
        "job_types": ["full-time"],
    },
]


# -------------------------------------------------
# Mock web-discovery response
# -------------------------------------------------

mock_web_result = """
{
    "jobs": [
        {
            "title": "Junior Data Analyst",
            "company": "Company A",
            "location": "India",
            "remote": true,
            "remote_evidence": "Full-time remote position.",
            "url": "https://company-a.com/jobs/data-analyst",
            "source": "Company Careers"
        },
        {
            "title": "Data Analyst",
            "company": "Company B",
            "location": "Germany",
            "remote": true,
            "remote_evidence": "Fully remote position.",
            "url": "https://company-b.com/jobs/data-analyst",
            "source": "Company Careers"
        },
        {
            "title": "Marketing Analyst",
            "company": "Company D",
            "location": "India",
            "remote": true,
            "remote_evidence": "Fully remote position.",
            "url": "https://company-d.com/jobs/marketing-analyst",
            "source": "Company Careers"
        }
    ]
}
"""


# -------------------------------------------------
# Mock external functions
# -------------------------------------------------

def mock_fetch_jobs(
    search_term,
    remote_only=False,
    visa_sponsorship=False,
):
    return mock_arbeitnow_jobs


def mock_search_web(
    query,
):
    return mock_web_result


# Replace the external discovery functions
# only inside this test.
job_discovery.fetch_jobs = mock_fetch_jobs
job_discovery.search_web = mock_search_web


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
# Run actual job_discovery.discover_jobs()
# -------------------------------------------------

jobs = job_discovery.discover_jobs(
    requirements
)


# -------------------------------------------------
# Display results
# -------------------------------------------------

print("DISCOVERED UNIQUE JOBS:")
print(len(jobs))

for index, job in enumerate(
    jobs,
    start=1,
):
    print(
        f"{index}. "
        f"{job.title} — "
        f"{job.company} — "
        f"{job.location} — "
        f"Remote: {job.remote} — "
        f"Source: {job.source}"
    )


# -------------------------------------------------
# Verify integration behavior
# -------------------------------------------------

# Company A appears twice across two sources,
# so it should only appear once.
company_a_jobs = [
    job
    for job in jobs
    if job.company == "Company A"
]

assert len(company_a_jobs) == 1, (
    "Company A duplicate was not removed."
)


# The total unique jobs should be:
#
# Company A
# Company B
# Company C
# Company D
#
# = 4
assert len(jobs) == 4, (
    "Expected exactly 4 unique jobs."
)


# Verify the URL was normalized correctly.
company_a = company_a_jobs[0]

assert company_a.url == (
    "https://company-a.com/jobs/data-analyst"
), "Company A URL was not normalized correctly."


print()
print("JOB DISCOVERY INTEGRATION TEST: PASSED")