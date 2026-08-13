import json

from models import Job, JobRequirements
from normalizer import normalize_job
from web_normalizer import normalize_web_job
from deduplicator import deduplicate_jobs


def discover_jobs(
    raw_jobs: list[dict],
    web_result: str | None = None,
) -> list[Job]:
    """
    Combine jobs from multiple discovery sources,
    normalize them, and remove duplicates.

    This function does not apply user-specific filtering.
    Filtering happens later in the pipeline.
    """

    jobs: list[Job] = []

    # -------------------------
    # Arbeitnow jobs
    # -------------------------

    for raw_job in raw_jobs:

        try:
            job = normalize_job(raw_job)
            jobs.append(job)

        except Exception as error:
            print(
                f"Warning: could not normalize "
                f"Arbeitnow job: {error}"
            )

    # -------------------------
    # Web-discovered jobs
    # -------------------------

    if web_result:

        try:
            data = json.loads(web_result)

            for raw_job in data.get(
                "jobs",
                [],
            ):

                try:
                    job = normalize_web_job(
                        raw_job
                    )

                    jobs.append(job)

                except Exception as error:
                    print(
                        f"Warning: could not normalize "
                        f"web job: {error}"
                    )

        except json.JSONDecodeError as error:
            print(
                f"Warning: invalid web-search JSON: "
                f"{error}"
            )

    # -------------------------
    # Deduplication
    # -------------------------

    return deduplicate_jobs(jobs)