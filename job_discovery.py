import json

from job_search import fetch_jobs
from normalizer import normalize_job
from web_discovery import search_web
from web_normalizer import normalize_web_job
from search_strategy import build_search_queries
from requirements import JobRequirements


def discover_jobs(
    requirements: JobRequirements,
) -> list:
    """
    Discover jobs from multiple sources.

    Sources:
    - Arbeitnow
    - Web search

    Arbeitnow may be queried multiple times using the generated
    search queries.

    Web discovery is performed only once using a consolidated
    query to reduce LLM/API usage.

    Jobs from all sources are normalized and deduplicated.
    User-specific hard filtering happens later.
    """

    queries = build_search_queries(
        requirements
    )

    all_jobs = {}

    # -------------------------------------------------
    # 1. Arbeitnow discovery
    #
    # Multiple searches are acceptable here because
    # Arbeitnow is a normal HTTP API, not an LLM call.
    # -------------------------------------------------

    for query in queries:

        try:

            raw_jobs = fetch_jobs(
                search_term=query,
                remote_only=requirements.remote_required,
                visa_sponsorship=requirements.visa_required,
            )

        except Exception as error:

            print(
                f"Warning: Arbeitnow search failed: "
                f"{error}"
            )

            continue

        for raw_job in raw_jobs:

            url = raw_job.get(
                "url",
                "",
            )

            if not url:
                continue

            try:

                job = normalize_job(
                    raw_job
                )

                if job.url:
                    all_jobs[job.url] = job

            except Exception as error:

                print(
                    f"Warning: could not normalize "
                    f"Arbeitnow job: {error}"
                )

    # -------------------------------------------------
    # 2. Web discovery
    #
    # IMPORTANT:
    # Use ONE LLM/web-search call instead of one
    # call per search query.
    # -------------------------------------------------

    if queries:

        combined_query = (
            "Find real job listings matching the following "
            "search requirements. Search broadly and return "
            "the strongest actual job opportunities.\n\n"
            "Search queries:\n"
            + "\n".join(
                f"- {query}"
                for query in queries
            )
        )

        try:

            web_result = search_web(
                combined_query
            )

            data = json.loads(
                web_result
            )

        except Exception as error:

            print(
                f"Warning: web discovery failed: "
                f"{error}"
            )

            data = {
                "jobs": []
            }

        for raw_job in data.get(
            "jobs",
            [],
        ):

            try:

                job = normalize_web_job(
                    raw_job
                )

                if job.url:
                    all_jobs[job.url] = job

            except Exception as error:

                print(
                    f"Warning: could not normalize "
                    f"web job: {error}"
                )

    # -------------------------------------------------
    # 3. Return combined unique jobs
    # -------------------------------------------------

    return list(
        all_jobs.values()
    )