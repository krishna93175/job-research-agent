from requirements import JobRequirements


def build_search_queries(
    requirements: JobRequirements,
) -> list[str]:
    """
    Build multiple targeted search queries from job requirements.

    The queries are ordered from highest-precision to broader
    discovery queries.
    """

    queries = []

    role = requirements.role

    if not role:
        return queries

    location = requirements.location

    # -------------------------------------------------
    # Build important requirement terms
    # -------------------------------------------------

    experience_terms = []

    if (
        requirements.max_experience_years is not None
        and requirements.max_experience_years <= 2
    ):
        experience_terms.extend(
            [
                "junior",
                "entry level",
            ]
        )

    elif (
        requirements.min_experience_years is not None
        or requirements.max_experience_years is not None
    ):
        min_years = (
            requirements.min_experience_years
            if requirements.min_experience_years is not None
            else ""
        )

        max_years = (
            requirements.max_experience_years
            if requirements.max_experience_years is not None
            else ""
        )

        experience_terms.append(
            f"{min_years}-{max_years} years experience"
        )

    elif any(
        keyword.lower() == "junior"
        for keyword in requirements.keywords
    ):
        experience_terms.extend(
            [
                "junior",
                "entry level",
            ]
        )

    # -------------------------------------------------
    # Remote
    # -------------------------------------------------

    remote_term = (
        "remote"
        if requirements.remote_required
        else ""
    )

    # -------------------------------------------------
    # Skills
    # -------------------------------------------------

    skills_term = ""

    if requirements.skills:
        skills_term = " ".join(
            requirements.skills[:4]
        )

    # -------------------------------------------------
    # Employment
    # -------------------------------------------------

    employment_term = ""

    if requirements.employment_types:
        employment_term = (
            requirements.employment_types[0]
        )

    # -------------------------------------------------
    # Location
    # -------------------------------------------------

    location_term = (
        location
        if location
        else ""
    )

    # -------------------------------------------------
    # 1. Highest precision query
    # -------------------------------------------------

    high_precision_parts = [
        remote_term,
        " ".join(experience_terms),
        role,
        skills_term,
        employment_term,
        "jobs",
        location_term,
    ]

    high_precision_query = " ".join(
        part
        for part in high_precision_parts
        if part
    )

    queries.append(
        high_precision_query
    )

    # -------------------------------------------------
    # 2. Role + remote + location + experience
    # -------------------------------------------------

    if experience_terms:

        query = " ".join(
            part
            for part in [
                remote_term,
                " ".join(experience_terms),
                role,
                "jobs",
                location_term,
            ]
            if part
        )

        queries.append(
            query
        )

    # -------------------------------------------------
    # 3. Role + skills + location
    # -------------------------------------------------

    if skills_term:

        query = " ".join(
            part
            for part in [
                remote_term,
                role,
                skills_term,
                "jobs",
                location_term,
            ]
            if part
        )

        queries.append(
            query
        )

    # -------------------------------------------------
    # 4. Role + remote + location
    # -------------------------------------------------

    if remote_term:

        queries.append(
            " ".join(
                part
                for part in [
                    remote_term,
                    role,
                    "jobs",
                    location_term,
                ]
                if part
            )
        )

    # -------------------------------------------------
    # 5. Basic role + location fallback
    # -------------------------------------------------

    queries.append(
        " ".join(
            part
            for part in [
                role,
                "jobs",
                location_term,
            ]
            if part
        )
    )

    # -------------------------------------------------
    # Remove duplicates
    # -------------------------------------------------

    unique_queries = []

    for query in queries:

        query = " ".join(
            query.split()
        ).strip()

        if (
            query
            and query not in unique_queries
        ):
            unique_queries.append(
                query
            )

    return unique_queries