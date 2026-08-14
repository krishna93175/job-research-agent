import json

from discovery import discover_jobs


arbeitnow_jobs = [
    {
        "title": "Junior Data Analyst",
        "company": "Example Company",
        "location": "India",
        "remote": True,
        "url": "https://linkedin.com/jobs/view/123",
        "description": "Data analysis role.",
    },
]


web_result = json.dumps(
    {
        "jobs": [
            {
                "title": "Junior Data Analyst",
                "company": "Example Company",
                "location": "India",
                "remote": True,
                "remote_evidence": "Fully remote",
                "url": "https://example.com/careers/data-analyst",
                "source": "Company Careers",
            },
            {
                "title": "Marketing Analyst",
                "company": "Other Company",
                "location": "India",
                "remote": True,
                "remote_evidence": "Remote position",
                "url": "https://other.com/jobs/marketing-analyst",
                "source": "Company Careers",
            },
        ]
    }
)


jobs = discover_jobs(
    arbeitnow_jobs,
    web_result,
)


print("UNIQUE JOBS:", len(jobs))
print()


for number, job in enumerate(
    jobs,
    start=1,
):
    print(f"{number}. {job.title}")
    print(f"   Company: {job.company}")
    print(f"   Location: {job.location}")
    print(f"   Remote: {job.remote}")
    print(f"   Source: {job.source}")
    print(f"   URL: {job.url}")
    print()