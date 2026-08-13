from job_search import fetch_jobs
from normalizer import normalize_job
from filters import filter_jobs
from role_filter import filter_marketing_jobs


raw_jobs = fetch_jobs(
    search_term="marketing",
    remote_only=True,
)


jobs = [
    normalize_job(job)
    for job in raw_jobs
]


remote_jobs = filter_jobs(
    jobs,
    remote_required=True,
)


marketing_jobs = filter_marketing_jobs(
    remote_jobs
)


print(f"Raw jobs found: {len(raw_jobs)}")
print(f"Remote jobs: {len(remote_jobs)}")
print(f"Marketing-relevant jobs: {len(marketing_jobs)}")


for job in marketing_jobs[:10]:
    print()
    print(f"Title: {job.title}")
    print(f"Company: {job.company}")
    print(f"Location: {job.location}")
    print(f"Remote: {job.remote}")
    print(f"Tags: {job.tags}")
    print(f"URL: {job.url}")