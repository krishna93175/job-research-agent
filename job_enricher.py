import re
from html import unescape
from urllib.parse import urlparse

import requests

from models import Job


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/151.0.0.0 Safari/537.36"
)


def clean_html_text(html: str) -> str:
    """
    Convert HTML into reasonably clean plain text.

    This intentionally uses lightweight HTML processing so
    the enrichment layer does not require another dependency.
    """

    if not html:
        return ""

    # Remove scripts and styles.
    html = re.sub(
        r"<script\b[^>]*>.*?</script>",
        " ",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    html = re.sub(
        r"<style\b[^>]*>.*?</style>",
        " ",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Replace common structural tags with spaces.
    html = re.sub(
        r"<(?:br|/p|/div|/li|/section|/article|/h[1-6])\s*/?>",
        "\n",
        html,
        flags=re.IGNORECASE,
    )

    # Remove remaining HTML tags.
    html = re.sub(
        r"<[^>]+>",
        " ",
        html,
    )

    # Decode HTML entities.
    text = unescape(html)

    # Normalize whitespace.
    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n\s*\n+",
        "\n",
        text,
    )

    return text.strip()


def extract_relevant_text(
    text: str,
    max_characters: int = 12000,
) -> str:
    """
    Keep the most useful portion of a job page.

    The purpose is to provide the analyzer with enough
    information without sending an enormous webpage
    to the LLM.
    """

    if not text:
        return ""

    # Remove excessive blank lines.
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    ).strip()

    # Look for common job-description sections.
    section_patterns = [
        r"(about the role.*)",
        r"(job description.*)",
        r"(description.*)",
        r"(responsibilities.*)",
        r"(what you.ll do.*)",
        r"(requirements.*)",
        r"(qualifications.*)",
        r"(skills.*)",
        r"(experience.*)",
        r"(benefits.*)",
        r"(salary.*)",
        r"(compensation.*)",
    ]

    sections = []

    lower_text = text.lower()

    for pattern in section_patterns:

        match = re.search(
            pattern,
            lower_text,
            flags=re.IGNORECASE | re.DOTALL,
        )

        if match:
            start = match.start()

            # Keep a reasonable amount around the
            # detected section.
            section = text[
                max(0, start - 200):
                start + 5000
            ]

            sections.append(
                section
            )

    if sections:

        combined = "\n\n".join(
            sections
        )

        # Remove duplicates while preserving order.
        lines = combined.splitlines()

        seen = set()
        unique_lines = []

        for line in lines:

            normalized = line.strip().lower()

            if not normalized:
                continue

            if normalized in seen:
                continue

            seen.add(normalized)
            unique_lines.append(
                line.strip()
            )

        combined = "\n".join(
            unique_lines
        )

        return combined[
            :max_characters
        ].strip()

    # Fallback: return the beginning of the page.
    return text[
        :max_characters
    ].strip()


def fetch_job_page(
    url: str,
    timeout: int = 15,
) -> str:
    """
    Fetch an individual job page and extract its text.

    Returns an empty string if the page cannot be fetched.
    """

    if not url:
        return ""

    try:

        response = requests.get(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": (
                    "text/html,"
                    "application/xhtml+xml,"
                    "application/xml;q=0.9,"
                    "*/*;q=0.8"
                ),
            },
            timeout=timeout,
            allow_redirects=True,
        )

        response.raise_for_status()

        content_type = (
            response.headers
            .get(
                "content-type",
                ""
            )
            .lower()
        )

        if (
            "text/html" not in content_type
            and "application/xhtml+xml"
            not in content_type
        ):
            return ""

        text = clean_html_text(
            response.text
        )

        return extract_relevant_text(
            text
        )

    except Exception as error:

        print(
            f"Warning: could not fetch job page "
            f"{url}: {error}"
        )

        return ""


def enrich_job(
    job: Job,
) -> Job:
    """
    Fetch the actual job page and enrich the Job
    description.

    The original discovery description is preserved
    if page fetching fails.
    """

    if not job.url:
        return job

    page_text = fetch_job_page(
        job.url
    )

    if not page_text:
        return job

    # Preserve the original snippet while adding
    # the actual job-page content.
    original_description = (
        job.description or ""
    ).strip()

    if original_description:

        combined = (
            "DISCOVERY SNIPPET:\n"
            + original_description
            + "\n\n"
            "JOB PAGE CONTENT:\n"
            + page_text
        )

    else:

        combined = (
            "JOB PAGE CONTENT:\n"
            + page_text
        )

    # Prevent uncontrolled growth.
    job.description = combined[
        :14000
    ]

    return job