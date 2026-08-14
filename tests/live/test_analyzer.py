from job_search import fetch_jobs
from normalizer import normalize_job
from job_analyzer import analyze_job


raw_jobs = fetch_jobs(
    search_term="marketing",
    remote_only=True,
)


if not raw_jobs:
    print("No jobs found.")
    raise SystemExit


job = normalize_job(raw_jobs[0])

print("JOB")
print("Title:", job.title)
print("Company:", job.company)
print("Location:", job.location)
print()

print("ANALYSIS")

analysis = analyze_job(job)

print("Role relevance:", analysis.role_relevance)
print(
    "Required experience:",
    analysis.required_experience_min,
    "-",
    analysis.required_experience_max,
)
print("Required skills:", analysis.required_skills)
print("Employment type:", analysis.employment_type)
print("Remote status:", analysis.remote_status)
print("Remote scope:", analysis.remote_scope)
print(
    "International eligibility:",
    analysis.international_eligibility,
)
print(
    "Visa sponsorship:",
    analysis.visa_sponsorship,
)

print()
print("Evidence:")
for item in analysis.evidence:
    print("-", item)

print()
print("Concerns:")
for item in analysis.concerns:
    print("-", item)