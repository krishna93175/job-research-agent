import re

from models import Job, JobRequirements


def normalize_text(value: str | None) -> str:
    """
    Normalize text for matching.
    """

    if not value:
        return ""

    value = str(value).lower()

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


def text_contains(
    text: str,
    value: str,
) -> bool:
    """
    Check whether a normalized value appears
    in normalized text.
    """

    text = normalize_text(text)
    value = normalize_text(value)

    if not value:
        return True

    return value in text


def job_text(job: Job) -> str:
    """
    Combine searchable job fields into one string.
    """

    return " ".join(
        [
            job.title or "",
            job.company or "",
            job.location or "",
            job.description or "",
            " ".join(job.tags or []),
            " ".join(job.job_types or []),
        ]
    )


def role_text(job: Job) -> str:
    """
    Return fields that are useful for determining
    the actual job role.

    Role matching should prioritize the title and
    structured tags rather than arbitrary mentions
    inside the description.
    """

    return normalize_text(
        " ".join(
            [
                job.title or "",
                " ".join(job.tags or []),
            ]
        )
    )


def matches_role(
    job: Job,
    requirements: JobRequirements,
) -> bool:
    """
    Determine whether the job matches the requested role.

    Role matching is intentionally strict. A job should
    not match merely because the requested role is mentioned
    somewhere in its description.
    """

    if not requirements.role:
        return True

    role = normalize_text(
        requirements.role
    )

    if not role:
        return True

    searchable = role_text(job)

    if not searchable:
        return True

    # Exact phrase match.
    if role in searchable:
        return True

    # For multi-word roles, require every meaningful
    # role word to appear in the title/tags.
    role_words = [
        word
        for word in role.split()
        if len(word) > 2
    ]

    if not role_words:
        return True

    return all(
        word in searchable
        for word in role_words
    )


def matches_location(
    job: Job,
    requirements: JobRequirements,
) -> bool:
    """
    Apply location requirement.

    If a location is explicitly requested, the job
    must contain that location.

    Unknown location is not automatically rejected.
    """

    if not requirements.location:
        return True

    location = normalize_text(
        requirements.location
    )

    job_location = normalize_text(
        job.location
    )

    if not job_location:
        return True

    return (
        location in job_location
        or job_location in location
    )


def matches_remote(
    job: Job,
    requirements: JobRequirements,
) -> bool:
    """
    Apply remote/hybrid requirements.
    """

    if requirements.remote_required:
        return job.remote is True

    return True


def normalize_employment_type(
    value: str,
) -> str:
    """
    Normalize common employment-type labels.
    """

    value = normalize_text(value)

    replacements = {
        "full time": "full-time",
        "fulltime": "full-time",
        "part time": "part-time",
        "parttime": "part-time",
        "contractor": "contract",
        "contract position": "contract",
        "internship": "intern",
        "intern": "intern",
        "temporary": "temporary",
        "freelance": "freelance",
    }

    return replacements.get(
        value,
        value,
    )


def extract_known_employment_types(
    job: Job,
) -> set[str]:
    """
    Extract only recognizable employment-type values
    from structured fields and the listing text.

    Arbeitnow's job_types can also contain seniority
    categories such as 'berufserfahren'. Those are
    deliberately ignored here.
    """

    found: set[str] = set()

    candidates = list(
        job.job_types or []
    )

    # Include title/description because some listings
    # explicitly state "full-time", "Vollzeit", etc.
    searchable = normalize_text(
        " ".join(
            [
                job.title or "",
                job.description or "",
            ]
        )
    )

    for candidate in candidates:
        normalized = normalize_employment_type(
            candidate
        )

        if normalized in {
            "full-time",
            "part-time",
            "contract",
            "intern",
            "temporary",
            "freelance",
        }:
            found.add(normalized)

    # Common English terms.
    if (
        "full time" in searchable
        or "full-time" in searchable
        or "fulltime" in searchable
    ):
        found.add("full-time")

    if (
        "part time" in searchable
        or "part-time" in searchable
        or "parttime" in searchable
    ):
        found.add("part-time")

    # Common German term used by Arbeitnow listings.
    if "vollzeit" in searchable:
        found.add("full-time")

    if "teilzeit" in searchable:
        found.add("part-time")

    if "freelance" in searchable:
        found.add("freelance")

    if "internship" in searchable:
        found.add("intern")

    return found


def matches_employment_type(
    job: Job,
    requirements: JobRequirements,
) -> bool:
    """
    Apply employment-type requirements.

    Unknown employment information does not automatically
    reject a job.

    Known conflicting employment types do reject the job.
    """

    if not requirements.employment_types:
        return True

    required_types = {
        normalize_employment_type(
            employment_type
        )
        for employment_type in requirements.employment_types
    }

    known_types = extract_known_employment_types(
        job
    )

    # No reliable employment information.
    # Do not reject solely because the source omitted it.
    if not known_types:
        return True

    return bool(
        required_types.intersection(
            known_types
        )
    )


def matches_skills(
    job: Job,
    requirements: JobRequirements,
) -> bool:
    """
    Apply required-skill filtering.

    Skills are treated as a soft signal during the
    discovery/filtering stage.

    Discovery results often contain only short snippets,
    so missing skill evidence must NOT reject a job.

    Detailed skill matching is performed later by the
    AI analyzer.
    """

    if not requirements.skills:
        return True

    # Build the available evidence directly here.
    searchable = normalize_text(
        " ".join(
            [
                job.title or "",
                job.description or "",
                " ".join(job.tags or []),
                " ".join(job.source_evidence or []),
            ]
        )
    )

    # --------------------------------------------------------
    # No usable skill information.
    #
    # Unknown != mismatch.
    # --------------------------------------------------------

    if not searchable:
        return True

    # --------------------------------------------------------
    # Do NOT reject jobs merely because Excel/SQL/etc.
    # are absent from the short discovery snippet.
    #
    # The AI analyzer will perform detailed skill matching.
    # --------------------------------------------------------

    return True


def matches_salary(
    job: Job,
    requirements: JobRequirements,
) -> bool:
    """
    Salary filtering placeholder.

    The current Job model does not reliably contain
    structured salary information.
    """

    return True


def matches_experience(
    job: Job,
    requirements: JobRequirements,
) -> bool:
    """
    Experience filtering placeholder.

    Experience should eventually use structured data
    extracted by the analyzer rather than guessing from
    incomplete job descriptions.
    """

    return True


def matches_visa(
    job: Job,
    requirements: JobRequirements,
) -> bool:
    """
    Apply visa requirement only when the job explicitly
    provides structured sponsorship information.
    """

    if not requirements.visa_required:
        return True

    if job.visa_sponsorship is None:
        return True

    return job.visa_sponsorship is True


def job_matches_requirements(
    job: Job,
    requirements: JobRequirements,
) -> bool:
    """
    Apply all currently supported hard filters.
    """

    checks = [
        matches_role(
            job,
            requirements,
        ),
        matches_location(
            job,
            requirements,
        ),
        matches_remote(
            job,
            requirements,
        ),
        matches_employment_type(
            job,
            requirements,
        ),
        matches_skills(
            job,
            requirements,
        ),
        matches_salary(
            job,
            requirements,
        ),
        matches_experience(
            job,
            requirements,
        ),
        matches_visa(
            job,
            requirements,
        ),
    ]

    return all(checks)


def filter_jobs(
    jobs: list[Job],
    requirements: JobRequirements,
) -> list[Job]:
    """
    Return jobs that satisfy the current hard
    requirements.
    """

    return [
        job
        for job in jobs
        if job_matches_requirements(
            job,
            requirements,
        )
    ]