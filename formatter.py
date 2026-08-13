from dataclasses import dataclass, field

from ranker import RankedJob


@dataclass
class FormattedJob:
    rank: int
    title: str
    company: str
    location: str
    remote: bool
    source: str
    url: str

    score: int
    confidence: str

    why_it_matches: list[str] = field(
        default_factory=list
    )

    concerns: list[str] = field(
        default_factory=list
    )


def format_ranked_job(
    ranked_job: RankedJob,
) -> FormattedJob:
    """
    Convert a RankedJob into a user-facing
    structured result.

    This function does not invent information.
    It uses only information already present
    in the score and analysis objects.
    """

    job = ranked_job.job
    score = ranked_job.score
    analysis = ranked_job.analysis

    why_it_matches = []
    concerns = []

    for component in score.components:

        if component.status == "MATCH":
            why_it_matches.append(
                component.reason
            )

        elif component.status == "PARTIAL":
            why_it_matches.append(
                component.reason
            )

        elif component.status == "UNKNOWN":
            concerns.append(
                component.reason
            )

        elif component.status == "MISMATCH":
            concerns.append(
                component.reason
            )

    # Add analyzer evidence and concerns.
    if analysis is not None:

        for evidence in analysis.evidence:

            if evidence not in why_it_matches:
                why_it_matches.append(
                    evidence
                )

        for concern in analysis.concerns:

            if concern not in concerns:
                concerns.append(
                    concern
                )

    return FormattedJob(
        rank=ranked_job.rank,
        title=job.title,
        company=job.company,
        location=job.location,
        remote=job.remote,
        source=job.source,
        url=job.url,
        score=score.total_score,
        confidence=score.confidence,
        why_it_matches=why_it_matches,
        concerns=concerns,
    )


def format_ranked_jobs(
    ranked_jobs: list[RankedJob],
) -> list[FormattedJob]:
    """
    Format a complete ranked job list.
    """

    return [
        format_ranked_job(job)
        for job in ranked_jobs
    ]


def print_formatted_jobs(
    formatted_jobs: list[FormattedJob],
) -> None:
    """
    Print formatted jobs in a readable form.
    """

    print()
    print("=" * 70)
    print("JOB MATCH RESULTS")
    print("=" * 70)

    if not formatted_jobs:

        print()
        print("No matching jobs found.")
        return

    for job in formatted_jobs:

        print()
        print(
            f"{job.rank}. "
            f"{job.title} — "
            f"{job.company}"
        )

        print(
            f"   Match: "
            f"{job.score}/100"
        )

        print(
            f"   Confidence: "
            f"{job.confidence}"
        )

        print(
            f"   Location: "
            f"{job.location}"
        )

        print(
            f"   Remote: "
            f"{job.remote}"
        )

        print(
            f"   Source: "
            f"{job.source}"
        )

        print()

        if job.why_it_matches:

            print("   Why it matches:")

            for reason in job.why_it_matches:

                print(
                    f"   - {reason}"
                )

        if job.concerns:

            print()

            print("   Concerns:")

            for concern in job.concerns:

                print(
                    f"   - {concern}"
                )

        print()

        print(
            f"   Apply: {job.url}"
        )

        print("-" * 70)