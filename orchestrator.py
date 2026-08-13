from requirement_parser import parse_requirements
from job_discovery import discover_jobs
from requirements_filter import filter_jobs

from match_scorer import score_job
from analyzer import analyze_job
from ranker import rank_jobs

from job_enricher import enrich_job

from formatter import (
    format_ranked_jobs,
    print_formatted_jobs,
)


def run_job_search(
    user_query: str,
    analysis_limit: int = 5,
):
    """
    Run the complete job-research pipeline.

    The pipeline is designed to work for arbitrary
    roles, locations, experience levels, skills,
    employment types, and other requirements.
    """

    # -------------------------------------------------
    # 1. Parse user requirements
    # -------------------------------------------------

    requirements, candidate_profile = parse_requirements(
        user_query
    )

    print()
    print("PARSED REQUIREMENTS")
    print(requirements)

    print()
    print("CANDIDATE PROFILE")
    print(candidate_profile)

    # -------------------------------------------------
    # 2. Discover jobs
    #
    # job_discovery.py already:
    # - builds search queries
    # - searches the job source
    # - normalizes jobs
    # - removes duplicates
    #
    # Therefore we do not repeat those operations here.
    # -------------------------------------------------

    jobs = discover_jobs(
        requirements
    )

    print()
    print(
        f"Jobs discovered: "
        f"{len(jobs)}"
    )

    if not jobs:

        return {
            "requirements": requirements,
            "candidate_profile": candidate_profile,
            "jobs": [],
            "message": (
                "No jobs were discovered "
                "for the requested criteria."
            ),
        }

    # -------------------------------------------------
    # 3. Apply hard requirements
    # -------------------------------------------------

    filtered_jobs = filter_jobs(
        jobs,
        requirements,
    )

    print(
        f"Jobs after filtering: "
        f"{len(filtered_jobs)}"
    )

    if not filtered_jobs:

        return {
            "requirements": requirements,
            "candidate_profile": candidate_profile,
            "jobs": [],
            "message": (
                "Jobs were found, but none "
                "satisfied the required constraints."
            ),
        }

    # -------------------------------------------------
    # 4. Preliminary scoring
    #
    # This uses deterministic scoring and does not
    # require an AI analysis for every job.
    # -------------------------------------------------

    preliminary = []

    for job in filtered_jobs:

        try:

            score = score_job(
                job,
                requirements,
                analysis=None,
            )

            preliminary.append(
                (
                    job,
                    score,
                )
            )

        except Exception as error:

            print(
                f"Warning: preliminary scoring "
                f"failed for {job.title}: {error}"
            )

    if not preliminary:

        return {
            "requirements": requirements,
            "candidate_profile": candidate_profile,
            "jobs": [],
            "message": (
                "Jobs were found, but none "
                "could be scored."
            ),
        }

    # -------------------------------------------------
    # 5. Sort preliminary results
    # -------------------------------------------------

    preliminary.sort(
        key=lambda item: item[1].total_score,
        reverse=True,
    )

    # -------------------------------------------------
    # 6. Select only the strongest candidates
    #
    # This prevents unnecessary AI/API usage.
    # -------------------------------------------------

    candidates = preliminary[
        :analysis_limit
    ]

    print()
    print(
        f"Jobs selected for AI analysis: "
        f"{len(candidates)}"
    )

    # -------------------------------------------------
    # 7. Enrich selected jobs
    #
    # Only fetch actual job pages for the strongest
    # candidates. This prevents unnecessary HTTP
    # requests and keeps the pipeline efficient.
    # -------------------------------------------------

    enriched_candidates = []

    print()

    print(
        f"Fetching job pages for "
        f"{len(candidates)} selected jobs..."
    )

    for job, preliminary_score in candidates:

        try:

            print(
                f"Fetching: "
                f"{job.title} — {job.company}"
            )

            enriched_job = enrich_job(
                job
            )

            enriched_candidates.append(
                (
                    enriched_job,
                    preliminary_score,
                )
            )

        except Exception as error:

            print(
                f"Warning: enrichment failed for "
                f"{job.title}: {error}"
            )

            # Keep the original job.
            enriched_candidates.append(
                (
                    job,
                    preliminary_score,
                )
            )


    # -------------------------------------------------
    # 8. Analyze enriched jobs
    # -------------------------------------------------

    analyses = {}

    for job, preliminary_score in enriched_candidates:

        try:

            analysis = analyze_job(
                job,
                requirements.role,
            )

            analyses[job.url] = analysis

        except Exception as error:

            print(
                f"Warning: analysis failed for "
                f"{job.title}: {error}"
            )


    # -------------------------------------------------
    # 9. Final ranking
    # -------------------------------------------------

    analyzed_jobs = [
        job
        for job, _score in enriched_candidates
    ]

    ranked_jobs = rank_jobs(
        analyzed_jobs,
        requirements,
        analyses,
    )
    # -------------------------------------------------
    # 10. Format final results
    # -------------------------------------------------

    formatted_jobs = format_ranked_jobs(
        ranked_jobs
    )

    return {
        "requirements": requirements,
        "candidate_profile": candidate_profile,
        "jobs": formatted_jobs,
        "message": None,
    }


def print_results(
    result: dict,
):
    """
    Print final job-search results.
    """

    if result.get("message"):

        print()
        print(result["message"])
        return

    print_formatted_jobs(
        result["jobs"]
    )