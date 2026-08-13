from job_search import fetch_jobs
import json


jobs = fetch_jobs(
    search_term="marketing",
    remote_only=True,
)


if not jobs:
    print("No jobs returned.")
else:
    print("Number of jobs:", len(jobs))
    print("\nFields returned by the API:\n")

    for key in jobs[0].keys():
        print("-", key)

    print("\nFirst job:\n")
    print(json.dumps(jobs[0], indent=2))