from web_normalizer import normalize_web_job


sample_jobs = [
    {
        "title": "Junior Data Analyst",
        "company": "Blu Careers",
        "location": "Mumbai, Maharashtra, India",
        "remote": True,
        "remote_evidence": (
            "This is a full-time remote role for a "
            "Junior Data Analyst."
        ),
        "url": (
            "[https://in.linkedin.com/jobs/view/"
            "junior-data-analyst-at-blu-careers-4231015087]"
            "(https://in.linkedin.com/jobs/view/"
            "junior-data-analyst-at-blu-careers-4231015087)"
        ),
        "source": "LinkedIn",
    },
    {
        "title": "Junior Data Analyst",
        "company": "Stier Solutions Inc",
        "location": "Telangana, India",
        "remote": True,
        "remote_evidence": (
            "fully remote capacity"
        ),
        "url": (
            "https://in.linkedin.com/jobs/view/"
            "junior-data-analyst-at-stier-solutions-inc-4386857976"
        ),
        "source": "LinkedIn",
    },
]


print("NORMALIZED JOBS")
print()


for number, data in enumerate(
    sample_jobs,
    start=1,
):

    job = normalize_web_job(data)

    print(f"{number}. {job.title}")
    print(f"   Company: {job.company}")
    print(f"   Location: {job.location}")
    print(f"   Remote: {job.remote}")
    print(f"   Remote evidence: {job.remote_evidence}")
    print(f"   Source: {job.source}")
    print(f"   URL: {job.url}")
    print()