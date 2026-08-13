from dataclasses import dataclass

from models import (
    Job,
    JobRequirements,
    CandidateProfile,
)
from match_scorer import MatchScore, score_job


@dataclass
class RankedJob:
    rank: int
    job: Job
    score: MatchScore
    analysis: object | None = None


def rank_jobs(
    jobs: list[Job],
    requirements: JobRequirements,
    analyses: dict[str, object] | None = None,
    candidate_profile: CandidateProfile | None = None,
) -> list[RankedJob]:
    """
    Score and rank jobs from highest to lowest match.

    `analyses` is keyed by job URL.
    """

    analyses = analyses or {}

    scored_jobs = []

    for job in jobs:

        analysis = analyses.get(
            job.url
        )

        score = score_job(
            job,
            requirements,
            analysis,
            candidate_profile,
        )

        scored_jobs.append(
            (
                job,
                score,
                analysis,
            )
        )

    # Highest score first.
    #
    # If scores are equal, prefer higher confidence.
    confidence_order = {
        "High": 3,
        "Medium": 2,
        "Low": 1,
    }

    scored_jobs.sort(
        key=lambda item: (
            item[1].total_score,
            confidence_order.get(
                item[1].confidence,
                0,
            ),
        ),
        reverse=True,
    )

    ranked = []

    for index, (
        job,
        score,
        analysis,
    ) in enumerate(
        scored_jobs,
        start=1,
    ):
        ranked.append(
            RankedJob(
                rank=index,
                job=job,
                score=score,
                analysis=analysis,
            )
        )

    return ranked