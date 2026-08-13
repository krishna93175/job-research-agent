from models import Job
from requirements import JobRequirements, CandidateProfile


def calculate_match_score(
    job: Job,
    requirements: JobRequirements,
    candidate: CandidateProfile,
) -> tuple[int, list[str], list[str]]:
    """
    Calculate a deterministic preliminary match score.

    Returns:
        score
        strengths
        concerns
    """

    score = 0
    strengths = []
    concerns = []

    # ---------------------------------------------------------
    # 1. Remote compatibility
    # ---------------------------------------------------------

    if requirements.remote_required:

        if job.remote:
            score += 25
            strengths.append("Remote work is confirmed.")
        else:
            concerns.append(
                "The job is not confirmed as remote."
            )

    else:
        score += 10

    # ---------------------------------------------------------
    # 2. Location
    # ---------------------------------------------------------

    if requirements.location:

        requested_location = requirements.location.lower()
        job_location = job.location.lower()

        if requested_location in job_location:
            score += 20
            strengths.append(
                "Job location matches the requested location."
            )
        elif requirements.remote_required and job.remote:
            score += 10
            strengths.append(
                "Remote job reduces the location mismatch."
            )
        else:
            concerns.append(
                "Job location does not clearly match the request."
            )

    # ---------------------------------------------------------
    # 3. Experience
    # ---------------------------------------------------------

    if candidate.experience_years is not None:

        if requirements.min_experience_years is not None:

            if (
                candidate.experience_years
                >= requirements.min_experience_years
            ):
                score += 15
                strengths.append(
                    "Candidate meets the minimum experience requirement."
                )
            else:
                concerns.append(
                    "Candidate may not meet the minimum experience requirement."
                )

        else:
            score += 10

    # ---------------------------------------------------------
    # 4. Skills
    # ---------------------------------------------------------

    if candidate.skills:

        job_text = (
            f"{job.title} "
            f"{job.description} "
            f"{' '.join(job.tags)}"
        ).lower()

        matched_skills = []

        for skill in candidate.skills:

            if skill.lower() in job_text:
                matched_skills.append(skill)

        if matched_skills:

            skill_score = min(
                25,
                len(matched_skills) * 10,
            )

            score += skill_score

            strengths.append(
                "Matching skills: "
                + ", ".join(matched_skills)
            )

        else:
            concerns.append(
                "No candidate skills were clearly identified in the listing."
            )

    # ---------------------------------------------------------
    # 5. Employment type
    # ---------------------------------------------------------

    if requirements.employment_types:

        requested_types = [
            item.lower()
            for item in requirements.employment_types
        ]

        job_types = [
            item.lower()
            for item in job.job_types
        ]

        if any(
            requested in job_type
            for requested in requested_types
            for job_type in job_types
        ):
            score += 15
            strengths.append(
                "Employment type appears compatible."
            )
        else:
            concerns.append(
                "Employment type is not confirmed as compatible."
            )

    # ---------------------------------------------------------
    # Cap score
    # ---------------------------------------------------------

    score = min(score, 100)

    return score, strengths, concerns