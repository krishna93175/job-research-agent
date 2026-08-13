import re
from dataclasses import dataclass, field

from models import Job, JobRequirements, CandidateProfile


@dataclass
class ScoreComponent:
    name: str
    points: float
    max_points: float
    status: str
    reason: str


@dataclass
class MatchScore:
    total_score: int
    max_score: int
    confidence: str
    components: list[ScoreComponent] = field(
        default_factory=list
    )


def normalize_text(value: str | None) -> str:
    """Normalize text for matching."""

    if not value:
        return ""

    value = value.lower()

    value = re.sub(
        r"[^a-z0-9+#.\s]",
        " ",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


def job_text(job: Job) -> str:
    """Combine searchable job information."""

    return normalize_text(
        " ".join(
            [
                job.title or "",
                job.company or "",
                job.location or "",
                job.description or "",
                " ".join(job.tags or []),
                " ".join(job.job_types or []),
            ]
        )
    )


def score_role(
    job: Job,
    requirements: JobRequirements,
) -> ScoreComponent:

    maximum = 30

    if not requirements.role:
        return ScoreComponent(
            "Role",
            0,
            0,
            "NOT_APPLICABLE",
            "No role requirement was specified.",
        )

    role = normalize_text(
        requirements.role
    )

    title = normalize_text(
        job.title
    )

    searchable = job_text(job)

    if role == title:
        return ScoreComponent(
            "Role",
            maximum,
            maximum,
            "MATCH",
            "Job title exactly matches the requested role.",
        )

    if role in title:
        return ScoreComponent(
            "Role",
            27,
            30,
            "MATCH",
            "Requested role appears directly in the job title.",
        )

    role_words = [
        word
        for word in role.split()
        if len(word) > 2
    ]

    if not role_words:
        return ScoreComponent(
            0,
            0,
            "NOT_APPLICABLE",
            "Role could not be evaluated.",
        )

    matched = sum(
        word in searchable
        for word in role_words
    )

    ratio = matched / len(role_words)

    if ratio >= 0.75:
        points = 24
        status = "MATCH"

    elif ratio >= 0.5:
        points = 15
        status = "PARTIAL"

    else:
        points = 0
        status = "MISMATCH"

    return ScoreComponent(
        "Role",
        points,
        maximum,
        status,
        f"{matched}/{len(role_words)} role terms matched.",
    )


def score_location(
    job: Job,
    requirements: JobRequirements,
) -> ScoreComponent:

    maximum = 15

    if not requirements.location:
        return ScoreComponent(
            "Location",
            0,
            0,
            "NOT_APPLICABLE",
            "No location requirement was specified.",
        )

    required = normalize_text(
        requirements.location
    )

    location = normalize_text(
        job.location
    )

    if not location:
        return ScoreComponent(
            "Location",
            0,
            maximum,
            "UNKNOWN",
            "Job location is not provided.",
        )

    if (
        required in location
        or location in required
    ):
        return ScoreComponent(
            "Location",
            maximum,
            maximum,
            "MATCH",
            "Job location matches the requested location.",
        )

    return ScoreComponent(
        "Location",
        0,
        maximum,
        "MISMATCH",
        "Job location does not match the requested location.",
    )


def score_remote(
    job: Job,
    requirements: JobRequirements,
) -> ScoreComponent:

    maximum = 15

    if not requirements.remote_required:
        return ScoreComponent(
            "Remote",
            0,
            0,
            "NOT_APPLICABLE",
            "Remote work was not required.",
        )

    if job.remote is True:
        return ScoreComponent(
            "Remote",
            maximum,
            maximum,
            "MATCH",
            "Job is marked as remote.",
        )

    return ScoreComponent(
        "Remote",
        0,
        maximum,
        "MISMATCH",
        "Job is not marked as remote.",
    )


def score_skills(
    job: Job,
    requirements: JobRequirements,
) -> ScoreComponent:

    maximum = 20

    if not requirements.skills:
        return ScoreComponent(
            "Skills",
            0,
            0,
            "NOT_APPLICABLE",
            "No required skills were specified.",
        )

    searchable = job_text(job)

    matched = []
    missing = []

    for skill in requirements.skills:

        normalized_skill = normalize_text(
            skill
        )

        if not normalized_skill:
            continue

        if normalized_skill in searchable:
            matched.append(skill)
        else:
            missing.append(skill)

    total_skills = (
        len(matched)
        + len(missing)
    )

    if total_skills == 0:
        return ScoreComponent(
            "Skills",
            0,
            0,
            "NOT_APPLICABLE",
            "No valid skills were specified.",
        )

    points = round(
        maximum
        * len(matched)
        / total_skills
    )

    if not missing:
        status = "MATCH"
        reason = (
            "All requested skills appear "
            "in the listing."
        )

    elif not matched:
        status = "UNKNOWN"
        reason = (
            "None of the requested skills "
            "were found in the available "
            "listing text."
        )

    else:
        status = "PARTIAL"
        reason = (
            f"Matched: {', '.join(matched)}. "
            f"Not found: {', '.join(missing)}."
        )

    return ScoreComponent(
        "Skills",
        points,
        maximum,
        status,
        reason,
    )


def score_employment(
    job: Job,
    requirements: JobRequirements,
) -> ScoreComponent:

    maximum = 10

    if not requirements.employment_types:
        return ScoreComponent(
            "Employment",
            0,
            0,
            "NOT_APPLICABLE",
            "No employment type was specified.",
        )

    if not job.job_types:
        return ScoreComponent(
            "Employment",
            0,
            maximum,
            "UNKNOWN",
            "Job employment type is not provided.",
        )

    job_types = normalize_text(
        " ".join(job.job_types)
    )

    matched = any(
        normalize_text(
            employment_type
        ) in job_types
        for employment_type
        in requirements.employment_types
    )

    if matched:
        return ScoreComponent(
            "Employment",
            maximum,
            maximum,
            "MATCH",
            "Requested employment type is listed.",
        )

    return ScoreComponent(
        "Employment",
        0,
        maximum,
        "MISMATCH",
        "Requested employment type was not found.",
    )


def score_experience(
    job: Job,
    requirements: JobRequirements,
    analysis=None,
    candidate_profile: CandidateProfile | None = None,
) -> ScoreComponent:
    """
    Compare the candidate's actual experience with the
    experience required by the analyzed job.

    JobRequirements experience fields represent the user's
    requested job range, while CandidateProfile represents
    the candidate's actual experience.
    """

    maximum = 10

    # No experience requirement from the user and no
    # candidate profile available.
    if (
        candidate_profile is None
        and requirements.min_experience_years is None
        and requirements.max_experience_years is None
    ):
        return ScoreComponent(
            "Experience",
            0,
            0,
            "NOT_APPLICABLE",
            "No experience information was specified.",
        )

    # AI analysis is required to know the job's experience
    # requirement.
    if analysis is None:
        return ScoreComponent(
            "Experience",
            0,
            maximum,
            "UNKNOWN",
            "Job experience requirements have not yet been analyzed.",
        )

    required_min = analysis.required_experience_min
    required_max = analysis.required_experience_max

    # The job does not state an experience requirement.
    if (
        required_min is None
        and required_max is None
    ):
        return ScoreComponent(
            "Experience",
            0,
            maximum,
            "UNKNOWN",
            "The job listing does not state a required experience range.",
        )

    # -------------------------------------------------
    # Candidate's actual experience
    # -------------------------------------------------

    if (
        candidate_profile is not None
        and candidate_profile.experience_years is not None
    ):
        candidate_experience = (
            candidate_profile.experience_years
        )

        # Candidate has less experience than the
        # job's stated minimum.
        if (
            required_min is not None
            and candidate_experience < required_min
        ):
            return ScoreComponent(
                "Experience",
                0,
                maximum,
                "MISMATCH",
                (
                    f"Job requires at least {required_min} "
                    f"years of experience, while the candidate "
                    f"has {candidate_experience} years."
                ),
            )

        # Candidate exceeds an explicitly stated maximum.
        if (
            required_max is not None
            and candidate_experience > required_max
        ):
            return ScoreComponent(
                "Experience",
                maximum,
                maximum,
                "MATCH",
                (
                    f"Candidate has {candidate_experience} "
                    f"years of experience, which exceeds the "
                    f"job's stated maximum of {required_max} years."
                ),
            )

        return ScoreComponent(
            "Experience",
            maximum,
            maximum,
            "MATCH",
            (
                f"Candidate has {candidate_experience} years "
                f"of experience and meets the job requirement "
                f"({required_min}–{required_max} years)."
            ),
        )

    # -------------------------------------------------
    # Fallback to requested experience range
    # -------------------------------------------------

    candidate_min = requirements.min_experience_years
    candidate_max = requirements.max_experience_years

    if (
        candidate_min is not None
        and required_max is not None
        and candidate_min > required_max
    ):
        return ScoreComponent(
            "Experience",
            0,
            maximum,
            "MISMATCH",
            (
                f"Requested experience starts at {candidate_min} "
                f"years, while the job requires at most "
                f"{required_max} years."
            ),
        )

    if (
        candidate_max is not None
        and required_min is not None
        and candidate_max < required_min
    ):
        return ScoreComponent(
            "Experience",
            0,
            maximum,
            "MISMATCH",
            (
                f"Requested experience ends at {candidate_max} "
                f"years, while the job requires at least "
                f"{required_min} years."
            ),
        )

    return ScoreComponent(
        "Experience",
        maximum,
        maximum,
        "MATCH",
        "The available experience information is compatible "
        "with the job requirement.",
    )


def score_visa(
    job: Job,
    requirements: JobRequirements,
    analysis=None,
) -> ScoreComponent:

    maximum = 10

    if not requirements.visa_required:
        return ScoreComponent(
            "Visa",
            0,
            0,
            "NOT_APPLICABLE",
            "Visa sponsorship was not required.",
        )

    if analysis is None:
        return ScoreComponent(
            "Visa",
            0,
            maximum,
            "UNKNOWN",
            "Visa sponsorship has not yet been analyzed.",
        )

    visa = analysis.visa_sponsorship

    if visa == "confirmed":
        return ScoreComponent(
            "Visa",
            maximum,
            maximum,
            "MATCH",
            "The listing confirms visa sponsorship.",
        )

    if visa == "no":
        return ScoreComponent(
            "Visa",
            0,
            maximum,
            "MISMATCH",
            "The listing states that visa sponsorship is not available.",
        )

    return ScoreComponent(
        "Visa",
        0,
        maximum,
        "UNKNOWN",
        "Visa sponsorship is not confirmed.",
    )


def score_salary(
    job: Job,
    requirements: JobRequirements,
    analysis=None,
) -> ScoreComponent:

    maximum = 10

    if requirements.salary_min is None:
        return ScoreComponent(
            "Salary",
            0,
            0,
            "NOT_APPLICABLE",
            "No minimum salary was specified.",
        )

    if analysis is None:
        return ScoreComponent(
            "Salary",
            0,
            maximum,
            "UNKNOWN",
            "Salary has not yet been analyzed.",
        )

    salary_max = analysis.salary_max

    if salary_max is None:
        return ScoreComponent(
            "Salary",
            0,
            maximum,
            "UNKNOWN",
            "The job listing does not provide a comparable salary maximum.",
        )

    if salary_max >= requirements.salary_min:
        return ScoreComponent(
            "Salary",
            maximum,
            maximum,
            "MATCH",
            (
                f"Job salary reaches the requested minimum "
                f"of {requirements.salary_min}."
            ),
        )

    return ScoreComponent(
        "Salary",
        0,
        maximum,
        "MISMATCH",
        (
            f"Job salary does not reach the requested "
            f"minimum of {requirements.salary_min}."
        ),
    )


def calculate_confidence(
    components: list[ScoreComponent],
) -> str:

    applicable = [
        component
        for component in components
        if component.max_points > 0
    ]

    if not applicable:
        return "Low"

    unknown_count = sum(
        component.status == "UNKNOWN"
        for component in applicable
    )

    if unknown_count == 0:
        return "High"

    if unknown_count <= 2:
        return "Medium"

    return "Low"


def score_job(
    job: Job,
    requirements: JobRequirements,
    analysis=None,
    candidate_profile: CandidateProfile | None = None,
) -> MatchScore:

    components = [
        score_role(
            job,
            requirements,
        ),
        score_location(
            job,
            requirements,
        ),
        score_remote(
            job,
            requirements,
        ),
        score_skills(
            job,
            requirements,
        ),
        score_employment(
            job,
            requirements,
        ),
        score_experience(
            job,
            requirements,
            analysis,
            candidate_profile,
        ),
        score_visa(
            job,
            requirements,
            analysis,
        ),
        score_salary(
            job,
            requirements,
            analysis,
        ),
    ]

    applicable = [
        component
        for component in components
        if component.max_points > 0
    ]

    raw_points = sum(
        component.points
        for component in applicable
    )

    raw_maximum = sum(
        component.max_points
        for component in applicable
    )

    if raw_maximum == 0:
        total_score = 0
    else:
        total_score = round(
            raw_points
            / raw_maximum
            * 100
        )

    return MatchScore(
        total_score=total_score,
        max_score=100,
        confidence=calculate_confidence(
            components
        ),
        components=components,
    )


def rank_jobs(
    jobs: list[Job],
    requirements: JobRequirements,
    analyses: dict[str, object] | None = None,
) -> list[tuple[Job, MatchScore]]:

    analyses = analyses or {}

    scored = []

    for job in jobs:

        analysis = analyses.get(
            job.url
        )

        result = score_job(
            job,
            requirements,
            analysis,
        )

        scored.append(
            (
                job,
                result,
            )
        )

    return sorted(
        scored,
        key=lambda item: item[1].total_score,
        reverse=True,
    )