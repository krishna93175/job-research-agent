import json
import requests

from agents import function_tool


@function_tool
def search_jobs(
    role: str,
    remote_only: bool = False,
    visa_sponsorship: bool = False,
) -> str:
    """
    Search multiple related job queries and return concise job records.
    """

    url = url = "https://www.arbeitnow.com/api/job-board-api"

    search_terms = [
        role,
        f"{role} specialist",
        f"{role} coordinator",
        f"digital {role}",
        "digital marketing",
        "social media marketing",
        "content marketing",
        "growth marketing",
    ]

    all_jobs = {}

    for search_term in search_terms:

        params = {
            "search": search_term,
        }

        if remote_only:
            params["remote"] = "true"

        if visa_sponsorship:
            params["visa_sponsorship"] = "true"

        try:
            response = requests.get(
                url,
                params=params,
                timeout=15,
            )

            response.raise_for_status()

            data = response.json()

        except requests.RequestException:
            continue

        for job in data.get("data", []):

            job_url = job.get("url")

            if not job_url:
                continue

            if job_url not in all_jobs:
                all_jobs[job_url] = {
                    "title": job.get("title"),
                    "company": job.get("company_name"),
                    "location": job.get("location"),
                    "remote": job.get("remote"),
                    "visa_sponsorship": job.get(
                        "visa_sponsorship"
                    ),
                    "url": job_url,
                }

    results = list(all_jobs.values())

    if not results:
        return "No matching jobs were found."

    # Keep the first 25 concise records.
    results = results[:25]

    return json.dumps(results, indent=2)