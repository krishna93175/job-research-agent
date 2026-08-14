# AI Job Research Agent

> An open-source, modular AI agent for discovering, filtering, enriching, analyzing, scoring, and ranking job opportunities against structured job requirements and a candidate profile.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/krishna93175/job-research-agent)](https://github.com/krishna93175/job-research-agent/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/krishna93175/job-research-agent)](https://github.com/krishna93175/job-research-agent/issues)
[![Tests](https://github.com/krishna93175/job-research-agent/actions/workflows/tests.yml/badge.svg)](https://github.com/krishna93175/job-research-agent/actions/workflows/tests.yml)

## Why this project exists

Job research is often repetitive and fragmented:

1. Search across multiple sources.
2. Open and inspect individual listings.
3. Verify role, location, and remote eligibility.
4. Check experience and skills.
5. Check employment type and other constraints.
6. Investigate missing or unclear information.
7. Compare and rank the strongest opportunities.

This project turns that process into a modular pipeline combining **deterministic software with LLM-based semantic analysis**.

It is **not intended to be a perfect job database or an autonomous application bot**. External job sources change, listings can be incomplete, and some pages may be inaccessible. The system is instead designed as an open-source job-research agent that makes its evidence, filtering, analysis, and ranking process inspectable.

The project is also intended as an **open learning and contribution platform**. Developers can inspect the architecture, run the system locally, replace providers, add job sources, modify ranking logic, improve prompts, add tests, or build new interfaces on top of the existing pipeline.

---

## What it does

A user can provide a request such as:

```text
Find remote junior data analyst jobs in India,
full-time, with Excel and SQL.
I have 1 year of experience.
```

The system converts that request into structured information such as:

```text
Job requirements
----------------
Role: Data Analyst
Location: India
Remote: Required
Employment: Full-time
Skills: Excel, SQL
Experience range: 0–2 years

Candidate profile
-----------------
Experience: 1 year
Skills: Excel, SQL
Current country: India
```

It then:

```text
Natural-language request
          |
          v
Requirement parsing
          |
          +--------------------+
          |                    |
          v                    v
Job requirements       Candidate profile
          |
          v
Search-query generation
          |
          v
Multi-source discovery
       /       \
      /         \
Arbeitnow    Tavily web search
      \         /
       \       /
        v     v
Normalization
          |
          v
Deduplication
          |
          v
Hard requirement filtering
          |
          v
Deterministic preliminary scoring
          |
          v
Top candidate selection
          |
          v
Job-page enrichment
          |
          v
Structured AI analysis
          |
          v
Final ranking
          |
          v
Human-readable results
```

The architecture deliberately keeps deterministic operations separate from AI reasoning.

---

# Core design idea

## Don't let the LLM do everything

The project uses normal Python logic where deterministic behavior is more reliable:

- URL cleaning
- normalization
- deduplication
- query generation
- hard filtering
- preliminary scoring
- orchestration
- result formatting

LLMs are used where semantic interpretation is useful:

- interpreting natural-language requirements
- extracting structured job information
- analyzing role relevance
- distinguishing required vs. preferred qualifications
- interpreting incomplete job evidence
- producing evidence and concerns

This separation makes the system easier to debug, test, replace, and extend.

## Unknown is different from No

A major design principle is preserving uncertainty.

For example:

- If a listing explicitly says `SQL required` → SQL evidence exists.
- If a listing explicitly says `SQL not required` → there is contradictory evidence.
- If the available snippet says nothing about SQL → SQL status is unknown.

Likewise:

- `visa sponsorship confirmed`
- `visa sponsorship unavailable`
- `visa sponsorship not mentioned`

are different states.

The system should not turn missing information into a false negative.

---

# Current capabilities

### Natural-language requirements

The requirement parser can extract information such as:

- role
- location
- remote/hybrid preference
- experience
- employment type
- skills
- salary range
- applicant country
- visa requirements
- keywords

### Candidate profiles

Candidate information is represented separately from job requirements.

For example:

```text
I have 1 year of experience.
```

describes the candidate's experience. It does not automatically mean that every job must require exactly one year.

The candidate model can contain:

- experience
- skills
- education
- current country
- desired locations
- desired employment types

### Multi-source discovery

The current discovery layer combines:

- Arbeitnow
- Tavily-powered web search

Tavily can surface direct vacancies hosted on platforms such as:

- Greenhouse
- Lever
- Ashby

The discovery layer is designed to prefer actual job listings rather than generic career advice or job-search articles.

### Search strategy

Structured requirements are converted into multiple search queries.

For example:

```text
remote junior data analyst jobs India
remote data analyst Excel SQL jobs India
remote data analyst jobs India
data analyst jobs India
```

Multiple queries increase recall while later stages handle deduplication and filtering.

### Normalization

Different sources expose different schemas.

The normalizer converts them into the common `Job` model so downstream code does not need to understand every source's proprietary fields.

### URL cleaning

The project handles URLs that may arrive wrapped in Markdown or surrounded by other text.

The goal is to produce a usable application URL before the job enters the rest of the pipeline.

### Deduplication

Jobs discovered through multiple searches or providers are deduplicated, primarily using their normalized URL.

### Hard filtering

Explicit constraints are applied before expensive AI processing.

Examples include:

- requested location
- mandatory remote status
- employment type
- other clearly verifiable requirements

### Preliminary scoring

Surviving jobs receive deterministic preliminary scores.

Only the strongest candidates proceed to the expensive enrichment and AI stages.

This is both a ranking strategy and an API-cost strategy.

### Job-page enrichment

Selected jobs can be fetched directly when possible.

The enrichment layer attempts to extract useful job-page content such as:

- responsibilities
- requirements
- qualifications
- skills
- experience
- salary
- compensation
- benefits

If a website blocks automated access, the pipeline keeps the discovery data instead of treating the whole search as a failure.

### AI job analysis

The analyzer returns structured information including:

- role relevance
- required experience
- required skills
- preferred skills
- employment type
- remote status
- remote scope
- international eligibility
- visa sponsorship
- salary
- evidence
- concerns

The analyzer is explicitly instructed not to invent missing information.

### Final ranking

The ranking stage uses the richer information available after analysis to produce the final ordered results.

---

# Architecture

The system can be understood as six logical layers.

## 1. Input and interpretation

```text
User request
    |
    v
Requirement parser
    |
    +--> JobRequirements
    |
    +--> CandidateProfile
```

The parser turns natural language into objects that the rest of the application can work with.

## 2. Discovery

```text
JobRequirements
      |
      v
Search strategy
      |
      +--> Arbeitnow
      |
      +--> Tavily web search
```

Discovery is intentionally separated from matching.

## 3. Data normalization

```text
Raw source data
      |
      v
Source normalizer
      |
      v
Common Job model
      |
      v
Deduplication
```

This prevents provider-specific schemas from leaking into the rest of the application.

## 4. Candidate reduction

```text
Normalized jobs
      |
      v
Hard filters
      |
      v
Preliminary scoring
      |
      v
Top candidates
```

This stage should be inexpensive and deterministic.

## 5. AI-assisted enrichment and analysis

```text
Top candidates
      |
      v
Job-page enrichment
      |
      v
Structured AI analysis
```

Only a small number of jobs should reach this stage.

## 6. Ranking and presentation

```text
Analyzed jobs
      |
      v
Final ranking
      |
      v
Formatter
      |
      v
Human-readable results
```

---

# Project structure

The repository keeps the application modules flat, while tests are organized by execution type:

```text
job-research-agent/
|
|-- analyzer.py
|-- deduplicator.py
|-- discovery.py
|-- filters.py
|-- formatter.py
|-- inspect_api.py
|-- job_analyzer.py
|-- job_discovery.py
|-- job_enricher.py
|-- job_relevance.py
|-- job_search.py
|-- llm_client.py
|-- match_scorer.py
|-- matcher.py
|-- models.py
|-- normalizer.py
|-- orchestrator.py
|-- ranker.py
|-- requirement_parser.py
|-- requirements.py
|-- requirements_filter.py
|-- search_strategy.py
|-- tools.py
|-- url_cleaner.py
|-- web_discovery.py
|-- web_normalizer.py
|
|-- tests/
|   |-- unit/
|   |-- integration/
|   `-- live/
|
|-- .github/
|   |-- ISSUE_TEMPLATE/
|   `-- workflows/
|       `-- tests.yml
|
|-- .env.example
|-- .gitignore
|-- CONTRIBUTING.md
|-- LICENSE
|-- README.md
`-- requirements.txt

The project is intentionally modular even though the current repository is flat. The modules are separated by responsibility rather than being placed into a package hierarchy prematurely.

---

# Important modules

| Module | Responsibility |
|---|---|
| `orchestrator.py` | Coordinates the complete job-search workflow |
| `requirement_parser.py` | Converts user requests into requirements and candidate data |
| `requirements.py` | Defines structured requirement/profile models |
| `search_strategy.py` | Builds discovery queries |
| `job_discovery.py` | Combines discovery sources |
| `job_search.py` | Handles job-source/API retrieval |
| `web_discovery.py` | Performs Tavily-based web discovery and structured extraction |
| `normalizer.py` | Normalizes source-specific job data |
| `web_normalizer.py` | Normalizes web-discovered job data |
| `deduplicator.py` | Removes duplicate jobs |
| `requirements_filter.py` | Applies hard requirements |
| `match_scorer.py` | Performs preliminary/final matching calculations |
| `job_enricher.py` | Retrieves and extracts job-page content |
| `analyzer.py` | Produces structured AI job analysis |
| `llm_client.py` | Provides the shared LLM interface/fallback layer |
| `ranker.py` | Produces final ranking |
| `formatter.py` | Formats results for humans |
| `models.py` | Defines common dataclasses |
| `tests/unit/` | Deterministic component-level tests |
| `tests/integration/` | Deterministic multi-component and pipeline tests |
| `tests/live/` | Tests requiring external services, APIs, or live network access |

---

# Technology stack

## Core

- Python 3.10+
- Python dataclasses
- Type hints
- Standard library modules

## Web and data

- `requests`
- Tavily
- HTTP APIs
- JSON
- HTML/text extraction
- Regular expressions

## AI

- OpenAI Agents SDK
- Groq
- OpenAI
- Structured JSON generation
- LLM provider fallback logic

## Engineering

- Modular pipeline architecture
- Deterministic filtering
- Multi-stage ranking
- Job-page enrichment
- Mock and integration testing
- Environment-based configuration
- Git/GitHub

---

# Installation

## Prerequisites

You need:

- Python 3.10 or newer
- Git
- Internet access
- A Tavily API key
- A Groq API key
- An OpenAI API key if your configured fallback path uses OpenAI

The project depends on external services, so API availability and provider limits can affect live searches.

## 1. Clone the repository

```bash
git clone https://github.com/krishna93175/job-research-agent.git
cd job-research-agent
```

If you are contributing through a fork, replace the URL with your fork.

## 2. Create a virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Copy the example file:

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Then edit `.env`:

```env
TAVILY_API_KEY=your_tavily_api_key
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
```

Never commit the real `.env` file.

---

# Dependency manifest

The repository includes `requirements.txt` so a new developer does not need to reconstruct the development environment manually.

Current direct dependencies include:

```text
python-dotenv
requests
tavily-python
groq
openai
openai-agents
```

The dependency list should be updated whenever the project introduces a new third-party dependency.

For reproducible development, a future improvement is to add pinned or constrained dependency versions after the project establishes a tested release environment.

---

# Running the project

The main workflow is exposed through the orchestrator.

Example:

```python
from orchestrator import run_job_search

result = run_job_search(
    "Find remote junior data analyst jobs in India, "
    "full-time, with Excel and SQL. "
    "I have 1 year of experience."
)

print(result)
```

---

# Understanding the output

A typical workflow reports stages similar to:

```text
PARSED REQUIREMENTS

JobRequirements(
    role='Data Analyst',
    location='India',
    remote_required=True,
    ...
)

CANDIDATE PROFILE

CandidateProfile(
    experience_years=1,
    skills=['Excel', 'SQL'],
    ...
)

Jobs discovered: 180
Jobs after filtering: 2
Jobs selected for AI analysis: 1

Fetching job pages for 1 selected jobs...

1. Junior Data Analyst — Example Company
   Match: 82/100
   Confidence: High
   Location: India
   Remote: True
   Source: Lever

   Why it matches:
   - Requested role matches.
   - Location matches.
   - Remote work is supported.

   Concerns:
   - Salary is not provided.
   - Visa sponsorship is not confirmed.

   Apply: https://example.com/job
```

Live output will vary because job listings, search results, external APIs, and job-page availability change over time.

---

# Testing

The test suite is organized by execution type.

## Unit tests

Deterministic component-level tests live under `tests/unit/`.

Examples:

```powershell
python -m tests.unit.test_analyzer_parser
python -m tests.unit.test_analyzer_static
python -m tests.unit.test_deduplicator
python -m tests.unit.test_dynamic_scoring
python -m tests.unit.test_formatter
python -m tests.unit.test_job_enricher
python -m tests.unit.test_match_scorer
python -m tests.unit.test_ranker
python -m tests.unit.test_requirements
python -m tests.unit.test_requirements_filter
python -m tests.unit.test_scorer_with_analysis
python -m tests.unit.test_strategy
python -m tests.unit.test_url
python -m tests.unit.test_url_cleaner
python -m tests.unit.test_web_normalizer
```

The unit suite covers:

- requirements parsing
- requirements filtering
- deduplication
- scoring
- ranking
- formatter behavior
- analyzer parsing
- analyzer behavior
- URL normalization
- web normalization
- enrichment
- strategy behavior

## Integration tests

Deterministic multi-component tests live under `tests/integration/`.

The integration suite covers:

- discovery merging
- job discovery integration
- mock pipeline execution

## Live tests

Tests under `tests/live/` exercise external services such as LLMs, search providers, and live web discovery.

These tests may require:

- API credentials
- internet access
- available provider quota
- currently available external services

Live results can vary because external job listings, search results, and provider responses are dynamic.

## CI

GitHub Actions runs the deterministic unit and integration tests on pushes and pull requests.

Live tests are intentionally excluded from CI because external API availability, credentials, quotas, and live search results are not deterministic.

## Recommended validation for contributors

After changing code:

1. Run the focused unit test for the changed module.
2. Run the relevant integration test.
3. Run the complete deterministic test suite before opening a pull request.
4. If API-dependent behavior changed, run the relevant live test separately.
5. Review the Git diff before committing.

A passing deterministic test suite provides evidence that the tested local code paths remain consistent. It does not guarantee that live providers or job listings will behave identically.

---

# Error handling and failure modes

External services are unreliable. The project is designed to degrade where possible rather than treating every external failure as a fatal application error.

## HTTP 403

Some job websites block automated requests.

When a selected job page cannot be fetched, enrichment should preserve the information already obtained during discovery.

## Timeouts

Search and job-page requests can time out.

The discovery layer attempts to continue with other available sources when a provider fails.

## LLM rate limits and token limits

LLM providers can reject requests because of:

- tokens-per-minute limits
- request limits
- context size
- provider availability
- validation errors

The architecture reduces unnecessary LLM usage by filtering and preliminarily scoring jobs before AI analysis.

## Missing information

Missing information is retained as missing.

The analyzer should not invent:

- salary
- visa sponsorship
- experience
- international eligibility
- skills
- employment type

when the listing does not support those claims.

---

# Limitations

This is an active open-source engineering project, not a guaranteed job database.

### Job freshness

A discovered vacancy may have closed after it was indexed.

Always verify the application page before applying.

### Search quality

Search engines and aggregators may return:

- duplicate listings
- expired listings
- generic career pages
- search/category pages
- incomplete listings
- inaccurate snippets

The pipeline attempts to reduce these problems but cannot guarantee perfect source quality.

### Automated page access

Some websites:

- block automated clients
- require JavaScript
- require browser execution
- use bot protection
- return incomplete HTML

The enrichment layer cannot guarantee access to every vacancy.

### Remote does not mean globally remote

A listing marked `Remote` may still restrict workers to:

- a particular country
- a region
- a time zone
- a legal entity's employment countries

International eligibility therefore requires separate evidence.

### AI analysis is not authoritative

LLM analysis can be wrong.

The analyzer is designed to preserve evidence and uncertainty, but users should verify important information against the original job listing.

### API costs and limits

Tavily, Groq, OpenAI, and other external services have their own quotas, rate limits, pricing, and availability.

---

# Security

Because this is a public repository, credential handling is critical.

Never commit:

```text
.env
```

or actual API keys inside:

- Python source
- tests
- documentation
- screenshots
- example output
- configuration files

Use:

```text
.env.example
```

for variable names only.

Before pushing changes, check:

```powershell
git status
git diff --cached
```

If a real API key is ever committed to a public repository, treat it as compromised and rotate/revoke it immediately.

---

# Extending the project

The project is designed so contributors can improve individual stages without rewriting the whole application.

## Add a new job source

A new source should ideally follow:

```text
External source
      |
      v
Source-specific fetcher
      |
      v
Raw job data
      |
      v
Source-specific normalizer
      |
      v
Common Job model
      |
      v
Existing pipeline
```

The rest of the system should not need to understand a provider's proprietary schema.

For example, if a provider returns:

```json
{
  "job_name": "Data Analyst",
  "city": "Bangalore",
  "employment": "Full Time"
}
```

its adapter should convert that into the project's standard `Job` representation.

## Add a new LLM provider

The analysis layer is separated from discovery, filtering, normalization, enrichment, and ranking.

A contributor should be able to add or replace an LLM provider behind the shared interface rather than rewriting the entire pipeline.

## Change the ranking system

The ranking architecture intentionally separates:

```text
Preliminary deterministic score
```

from:

```text
Final AI-assisted analysis
```

Potential future signals include:

- skill similarity
- experience compatibility
- salary preferences
- location preferences
- source quality
- evidence quality
- confidence penalties
- semantic similarity
- resume-to-job similarity

## Build a user interface

The current orchestration layer can be used as the backend of a future:

- CLI
- web application
- desktop application
- API
- dashboard

The project does not currently require a UI, which keeps the core research pipeline relatively easy to inspect and modify.

---

# Contributing

Contributions are welcome.

Useful contribution areas include:

- new job sources
- ATS-specific extraction
- better job-page enrichment
- improved ranking
- better skill matching
- better international eligibility detection
- tests
- prompt improvements
- provider integrations
- documentation
- error handling
- performance improvements
- output formats
- UI development

## Suggested workflow

Fork the repository and create a branch:

```bash
git checkout -b feature/my-improvement
```

Make a focused change.

Run the relevant tests.

Review your diff:

```bash
git diff
```

Commit:

```bash
git add .
git commit -m "Add my improvement"
```

Push your branch:

```bash
git push -u origin feature/my-improvement
```

Then open a pull request.

For substantial architectural changes, open an issue first so the proposed approach can be discussed before significant implementation work begins.

---

# Learning and engineering goals

This project is intentionally also a practical learning project.

## Python

- modular application design
- dataclasses
- type hints
- exception handling
- API clients
- module organization

## AI engineering

- LLM integration
- prompt design
- structured JSON output
- provider abstraction
- token management
- fallback providers
- AI-assisted ranking

## Agent architecture

- multi-stage workflows
- tool/API integration
- deterministic + probabilistic components
- context management
- candidate selection
- external data acquisition
- failure recovery

## Web and data engineering

- search APIs
- HTTP requests
- HTML extraction
- URL processing
- normalization
- deduplication

## Software engineering

- modular architecture
- integration testing
- mock testing
- debugging
- rate-limit handling
- configuration management
- Git/GitHub workflows

## Open source

- documentation
- repository organization
- reproducibility
- contribution workflows
- credential security
- public code quality

The goal is not only to demonstrate an AI feature, but to demonstrate the engineering required to build, test, document, and maintain an AI-powered application.

---

# Open-source philosophy

This project is intended to remain open source and accessible.

You are encouraged to:

- fork it
- study it
- modify it
- replace components
- add new sources
- experiment with LLM providers
- improve prompts
- improve ranking
- add tests
- build a UI
- submit pull requests

The architecture is deliberately modular so that a contributor can work on one part without first understanding every part of the system.

For example:

```text
Discovery contributor
    |
    +-- job_discovery.py
    +-- web_discovery.py
    +-- job_search.py
    +-- search_strategy.py

AI contributor
    |
    +-- analyzer.py
    +-- llm_client.py

Matching contributor
    |
    +-- requirements_filter.py
    +-- match_scorer.py
    +-- ranker.py

Enrichment contributor
    |
    +-- job_enricher.py

Testing contributor
    |
    +-- tests/
        +-- unit/
        +-- integration/
        +-- live/
```

---

# Roadmap

The roadmap is intentionally open-ended.

## Core functionality

- [x] Requirement parsing
- [x] Candidate profile extraction
- [x] Multi-source job discovery
- [x] Job normalization
- [x] Duplicate detection
- [x] Hard requirement filtering
- [x] Preliminary job scoring
- [x] Job-page enrichment
- [x] AI-powered job analysis
- [x] Final ranking
- [x] Structured result formatting

## Discovery and matching

- [x] Tavily-based web discovery
- [x] India-focused discovery support
- [x] Remote-job filtering
- [x] Employment-type filtering
- [x] Experience matching
- [x] Skill matching
- [x] Location matching
- [x] International eligibility handling
- [x] Visa sponsorship uncertainty handling
- [x] Evidence-aware job analysis

## Engineering

- [x] Modular architecture
- [x] Unit testing
- [x] Integration testing
- [x] Mock pipeline testing
- [x] Deterministic CI testing
- [ ] More automated tests
- [ ] Better logging and observability
- [ ] Docker support
- [ ] Source/plugin architecture
- [ ] Better configuration management
- [ ] Contribution templates

## Future improvements

- [ ] More job sources
- [ ] Improved job-page extraction
- [ ] Better search-query generation
- [ ] More robust ranking calibration
- [ ] Persistent job storage
- [ ] Job freshness detection
- [ ] Historical search tracking
- [ ] User preference persistence
- [ ] Web interface
- [ ] API interface

# Project status

This repository should be considered an **active v1 open-source engineering project**.

The core research pipeline is implemented and tested, but the project is still evolving. External job sources, search behavior, LLM providers, and job-page structures can change independently of the codebase.

The goal is to improve the architecture incrementally while keeping the project understandable and useful to contributors.

---

# Disclaimer

This project is provided for research, experimentation, and educational purposes.

It does not guarantee:

- that a job is still open
- that a listing is accurate
- that a candidate is eligible
- that remote work is available in a particular country
- that visa sponsorship will be provided
- that an AI-generated analysis is correct

Always verify important information on the original employer or job-platform listing before making an application or employment decision.

---

# License

This project is licensed under the [MIT License](LICENSE).

You are free to use, modify, distribute, and build upon the project subject to the terms of the license.
