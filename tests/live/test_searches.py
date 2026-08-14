from job_search import fetch_jobs


search_terms = [
    "marketing",
    "digital marketing",
    "marketing specialist",
    "marketing coordinator",
    "social media",
    "content marketing",
    "growth marketing",
]


for term in search_terms:

    jobs = fetch_jobs(
        search_term=term,
        remote_only=True,
    )

    print()
    print("=" * 60)
    print(f"SEARCH: {term}")
    print(f"RESULTS: {len(jobs)}")
    print("=" * 60)

    for job in jobs[:5]:
        print(
            f"{job.get('title')} | "
            f"{job.get('company_name')} | "
            f"{job.get('location')}"
        )