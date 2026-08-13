import json
import os
import re

from urllib.parse import urlparse

from dotenv import load_dotenv
from tavily import TavilyClient

from llm_client import generate_json


load_dotenv()


WEB_SEARCH_INSTRUCTIONS = """
You are a job-search result extraction agent.

You receive search results returned by a web-search API.

Identify only actual individual job opportunities.

Reject:

- company career homepages
- generic company jobs pages
- job-category pages
- search-result pages
- career advice
- news articles
- salary articles
- job-search guides

Return ONLY valid JSON.

Use exactly this structure:

{
    "jobs": [
        {
            "title": "...",
            "company": "...",
            "location": "...",
            "location_evidence": "...",
            "remote": true,
            "remote_evidence": "...",
            "remote_scope": "...",
            "employment_type": "...",
            "description": "...",
            "url": "...",
            "source": "..."
        }
    ]
}

Rules:

- Return only actual individual job listings.
- Never invent jobs.
- Never invent companies.
- Never invent URLs.
- Use only information supplied by the search result.
- Prefer direct individual vacancy URLs.
- Preserve India-specific location information.
- Preserve remote scope.
- Preserve employment type when explicitly stated.
- Preserve useful job-description information.
- If information is missing, use null.
- Return no more than 6 jobs.
"""


# ============================================================
# URL CLEANING
# ============================================================

def clean_url(url: str) -> str:
    """
    Extract a plain HTTP/HTTPS URL from a string.

    Handles:
    - plain URLs
    - Markdown links
    - URLs embedded in text
    - escaped Markdown formatting
    """

    if not url:
        return ""

    url = str(url).strip()

    # Remove escaped Markdown characters.
    url = url.replace("\\(", "(")
    url = url.replace("\\)", ")")
    url = url.replace("\\[", "[")
    url = url.replace("\\]", "]")

    # Remove formatting/newline artifacts.
    url = url.replace("\\\n", "")
    url = url.replace("\n", "")
    url = url.replace("\r", "")

    # Find the first HTTP/HTTPS URL.
    match = re.search(
        r"https?://[^\s<>\[\]\"']+",
        url,
        flags=re.IGNORECASE,
    )

    if not match:
        return ""

    result = match.group(0).strip()

    # Remove trailing punctuation.
    result = result.rstrip(
        ".,;:!?)}>'\""
    )

    return result


# ============================================================
# SOURCE DETECTION
# ============================================================

def get_source_from_url(
    url: str,
) -> str:
    """
    Determine the job source from the URL.

    The LLM is NOT trusted for this field.
    """

    url_lower = url.lower()

    if "greenhouse.io" in url_lower:
        return "Greenhouse"

    if "lever.co" in url_lower:
        return "Lever"

    if "ashbyhq.com" in url_lower:
        return "Ashby"

    if "linkedin." in url_lower:
        return "LinkedIn"

    if "indeed." in url_lower:
        return "Indeed"

    if "workday" in url_lower:
        return "Workday"

    if "internshala." in url_lower:
        return "Internshala"

    if "naukri." in url_lower:
        return "Naukri"

    if "glassdoor." in url_lower:
        return "Glassdoor"

    if "cutshort." in url_lower:
        return "Cutshort"

    if "jobgether." in url_lower:
        return "Jobgether"

    if "arbeitnow." in url_lower:
        return "Arbeitnow"

    return "Web"


# ============================================================
# INDIVIDUAL JOB URL DETECTION
# ============================================================

def is_likely_job_listing_url(
    url: str,
) -> bool:
    """
    Determine whether a URL appears to be an
    individual job listing rather than a generic
    company/category/search page.
    """

    if not url:
        return False

    url = clean_url(url)

    if not url:
        return False

    parsed = urlparse(url)

    hostname = parsed.netloc.lower()
    path = parsed.path.rstrip("/")

    # --------------------------------------------------------
    # Greenhouse
    #
    # Example:
    # https://job-boards.greenhouse.io/company/jobs/8620471002
    # --------------------------------------------------------

    if "greenhouse.io" in hostname:

        parts = [
            part
            for part in path.split("/")
            if part
        ]

        if "jobs" not in parts:
            return False

        jobs_index = parts.index("jobs")

        if jobs_index + 1 >= len(parts):
            return False

        job_id = parts[
            jobs_index + 1
        ]

        return job_id.isdigit()

    # --------------------------------------------------------
    # Lever
    #
    # Example:
    # https://jobs.lever.co/company/<uuid>
    # --------------------------------------------------------

    if "jobs.lever.co" in hostname:

        parts = [
            part
            for part in path.split("/")
            if part
        ]

        if len(parts) < 2:
            return False

        job_id = parts[1]

        uuid_pattern = re.compile(
            r"^[0-9a-fA-F]{8}-"
            r"[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{12}$"
        )

        return bool(
            uuid_pattern.match(
                job_id
            )
        )

    # --------------------------------------------------------
    # Ashby
    #
    # Example:
    # https://jobs.ashbyhq.com/company/<uuid>
    # --------------------------------------------------------

    if "jobs.ashbyhq.com" in hostname:

        parts = [
            part
            for part in path.split("/")
            if part
        ]

        if len(parts) < 2:
            return False

        job_id = parts[1]

        uuid_pattern = re.compile(
            r"^[0-9a-fA-F]{8}-"
            r"[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{12}$"
        )

        return bool(
            uuid_pattern.match(
                job_id
            )
        )

    # --------------------------------------------------------
    # Generic job websites
    # --------------------------------------------------------

    normalized = (
        hostname + path
    ).lower()

    # Generic/category/search pages that should not
    # be treated as individual jobs.
    blocked_patterns = [
        "/job-search",
        "/jobs/search",
        "/search/",
        "/search?",
        "/remote-jobs",
        "/jobs?",
    ]

    for pattern in blocked_patterns:

        if pattern in normalized:
            return False

    # Generic company job pages.
    if normalized.endswith("/jobs"):
        return False

    if normalized.endswith("/careers"):
        return False

    # Individual listing patterns.
    individual_patterns = [
        "/job/",
        "/jobs/",
        "/job-",
        "/vacancy/",
        "/vacancies/",
        "/position/",
        "/positions/",
        "/apply/",
    ]

    for pattern in individual_patterns:

        if pattern in normalized:
            return True

    return False


# ============================================================
# TAVILY SEARCH
# ============================================================

def _search_tavily(
    client: TavilyClient,
    query: str,
    max_results: int = 2,
) -> list:
    """
    Execute a small Tavily search.

    The result count is intentionally low because
    Groq currently has an 8,000 TPM limit.
    """

    try:

        response = client.search(
            query=query,
            search_depth="basic",
            max_results=max_results,
            topic="general",
            include_answer=False,
            include_raw_content=False,
        )

        return response.get(
            "results",
            [],
        )

    except Exception as error:

        print(
            f"Warning: Tavily search failed "
            f"for '{query}': {error}"
        )

        return []


# ============================================================
# WEB DISCOVERY
# ============================================================

def search_web(
    query: str,
) -> str:
    """
    Search for individual job listings.

    Uses a small search matrix to keep the LLM
    request within the Groq token limit.
    """

    api_key = os.getenv(
        "TAVILY_API_KEY"
    )

    if not api_key:

        raise RuntimeError(
            "TAVILY_API_KEY is not configured."
        )

    client = TavilyClient(
        api_key=api_key
    )

    # --------------------------------------------------------
    # Search matrix
    #
    # We deliberately keep this small.
    # --------------------------------------------------------

    search_queries = [
        query,

        # Lever
        f'site:jobs.lever.co '
        f'"Data Analyst" "India"',

        # Ashby
        f'site:jobs.ashbyhq.com '
        f'"Data Analyst" "India"',

        # Greenhouse
        f'site:job-boards.greenhouse.io '
        f'"Data Analyst" "India"',
    ]

    # --------------------------------------------------------
    # Collect unique Tavily results.
    # --------------------------------------------------------

    all_results = []

    seen_urls = set()

    for search_query in search_queries:

        results = _search_tavily(
            client,
            search_query,
            max_results=2,
        )

        for result in results:

            url = clean_url(
                result.get(
                    "url",
                    "",
                )
            )

            if not url:
                continue

            url_key = (
                url.rstrip("/")
                .lower()
            )

            if url_key in seen_urls:
                continue

            seen_urls.add(
                url_key
            )

            # Store the canonical URL directly
            # on the original Tavily result.
            result["url"] = url

            all_results.append(
                result
            )

    # --------------------------------------------------------
    # Keep individual job pages only.
    # --------------------------------------------------------

    valid_results = []

    for result in all_results:

        url = clean_url(
            result.get(
                "url",
                "",
            )
        )

        if not is_likely_job_listing_url(
            url
        ):
            continue

        result["url"] = url

        valid_results.append(
            result
        )

    if not valid_results:

        return json.dumps(
            {
                "jobs": []
            },
            ensure_ascii=False,
        )

    # --------------------------------------------------------
    # Prepare a compact LLM input.
    #
    # IMPORTANT:
    # Keep content at 700 characters.
    # This prevents another Groq 413 error.
    # --------------------------------------------------------

    search_results = []

    for result in valid_results[:8]:

        content = result.get(
            "content",
            "",
        )

        content = str(
            content
        )

        if len(content) > 700:
            content = content[:700]

        search_results.append(
            {
                "title": result.get(
                    "title"
                ),
                "url": clean_url(
                    result.get(
                        "url",
                        "",
                    )
                ),
                "content": content,
            }
        )

    # --------------------------------------------------------
    # Extraction prompt.
    # --------------------------------------------------------

    extraction_prompt = f"""
Extract actual individual job listings from
these web-search results.

SEARCH QUERY:
{query}

SEARCH RESULTS:
{json.dumps(
    search_results,
    ensure_ascii=False,
    indent=2,
)}

Rules:

- Use only information supported by the results.
- Do not invent jobs.
- Do not invent companies.
- Do not invent URLs.
- Do not invent employment types.
- Preserve India-specific location evidence.
- Preserve remote evidence.
- Preserve remote geographic scope.
- Preserve employment type if explicitly stated.
- Preserve relevant description information.
- Reject generic company pages.
- Reject category pages.
- Reject search-result pages.
- Return at most 6 jobs.

Return only the required JSON object.
"""

    # --------------------------------------------------------
    # LLM extraction.
    # --------------------------------------------------------

    try:

        data = generate_json(
            system_prompt=WEB_SEARCH_INSTRUCTIONS,
            user_prompt=extraction_prompt,
            groq_model="openai/gpt-oss-120b",
        )

    except Exception as error:

        print(
            f"Warning: Groq extraction failed: "
            f"{error}"
        )

        return json.dumps(
            {
                "jobs": []
            },
            ensure_ascii=False,
        )

    # --------------------------------------------------------
    # Build mapping of original Tavily URLs.
    #
    # These URLs are authoritative.
    # --------------------------------------------------------

    original_results_by_url = {}

    for result in valid_results:

        original_url = clean_url(
            result.get(
                "url",
                "",
            )
        )

        if not original_url:
            continue

        key = (
            original_url
            .rstrip("/")
            .lower()
        )

        original_results_by_url[
            key
        ] = result

    # --------------------------------------------------------
    # Final validation.
    # --------------------------------------------------------

    cleaned_jobs = []

    final_urls = set()

    for job in data.get(
        "jobs",
        [],
    ):

        # ----------------------------------------------------
        # LLM URL
        # ----------------------------------------------------

        llm_url = clean_url(
            job.get(
                "url",
                "",
            )
        )

        if not llm_url:
            continue

        llm_key = (
            llm_url
            .rstrip("/")
            .lower()
        )

        # ----------------------------------------------------
        # Find corresponding original Tavily result.
        # ----------------------------------------------------

        original_result = (
            original_results_by_url.get(
                llm_key
            )
        )

        # ----------------------------------------------------
        # If exact URL matching failed, compare
        # hostname + path.
        # ----------------------------------------------------

        if original_result is None:

            llm_parsed = urlparse(
                llm_url
            )

            for (
                original_key,
                result,
            ) in original_results_by_url.items():

                original_parsed = urlparse(
                    original_key
                )

                if (
                    llm_parsed.netloc.lower()
                    ==
                    original_parsed.netloc.lower()
                    and
                    llm_parsed.path.rstrip("/")
                    ==
                    original_parsed.path.rstrip("/")
                ):

                    original_result = result
                    break

        # We cannot safely return a job without
        # knowing its original source URL.
        if original_result is None:
            continue

        # ----------------------------------------------------
        # ALWAYS use the original Tavily URL.
        # ----------------------------------------------------

        canonical_url = clean_url(
            original_result.get(
                "url",
                "",
            )
        )

        if not canonical_url:
            continue

        canonical_key = (
            canonical_url
            .rstrip("/")
            .lower()
        )

        if canonical_key in final_urls:
            continue

        # ----------------------------------------------------
        # Verify it is an individual listing.
        # ----------------------------------------------------

        if not is_likely_job_listing_url(
            canonical_url
        ):
            continue

        title = job.get(
            "title"
        )

        if not title:
            continue

        final_urls.add(
            canonical_key
        )

        # ----------------------------------------------------
        # Source is determined from the URL.
        # Never trust the LLM's source field.
        # ----------------------------------------------------

        source = get_source_from_url(
            canonical_url
        )

        cleaned_jobs.append(
            {
                "title": title,

                "company": job.get(
                    "company"
                ),

                "location": job.get(
                    "location"
                ),

                "location_evidence": job.get(
                    "location_evidence"
                ),

                "remote": job.get(
                    "remote"
                ),

                "remote_evidence": job.get(
                    "remote_evidence"
                ),

                "remote_scope": job.get(
                    "remote_scope"
                ),

                "employment_type": job.get(
                    "employment_type"
                ),

                "description": job.get(
                    "description",
                    "",
                ),

                # Canonical URL from Tavily.
                "url": canonical_url,

                # Deterministic source.
                "source": source,
            }
        )

    return json.dumps(
        {
            "jobs": cleaned_jobs
        },
        ensure_ascii=False,
    )