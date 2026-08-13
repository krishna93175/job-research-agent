# AI Job Research Agent

> An open-source AI-powered job research agent that discovers, filters, enriches, analyzes, and ranks job opportunities against a user's requirements and candidate profile.

This project is designed to be **usable, understandable, extensible, and modifiable by other developers**. It is also a practical learning and engineering project for Python, APIs, web search, LLM integration, structured AI outputs, ranking, testing, Git/GitHub, and open-source development.

## Table of Contents

- [What Is This Project?](#what-is-this-project)
- [Why Does This Project Exist?](#why-does-this-project-exist)
- [What the Agent Does](#what-the-agent-does)
- [Example](#example)
- [Features](#features)
- [Architecture](#architecture)
- [Detailed Components](#detailed-components)
- [Design Principles](#design-principles)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Requirements](#requirements)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the Project](#running-the-project)
- [Understanding the Output](#understanding-the-output)
- [Testing](#testing)
- [Error Handling](#error-handling)
- [Known Limitations](#known-limitations)
- [Security](#security)
- [Extending the Project](#extending-the-project)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Learning Goals](#learning-goals)
- [Open Source Philosophy](#open-source-philosophy)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## What Is This Project?

The **AI Job Research Agent** accepts a natural-language job request and turns it into a structured research workflow.

Instead of simply performing a keyword search, it attempts to understand:

- role
- location
- remote/hybrid preference
- experience
- employment type
- required skills
- salary requirements
- applicant country
- visa requirements
- keywords and other constraints

It then discovers jobs from multiple sources, normalizes and deduplicates them, applies deterministic filters, selects promising candidates, enriches those candidates with job-page information where possible, analyzes them with an LLM, and produces ranked results.

The architecture deliberately separates **deterministic software logic** from **AI-based semantic analysis**.

---

## Why Does This Project Exist?

Job searching normally requires repeated manual work:

1. Search several platforms.
2. Open listings.
3. Check role relevance.
4. Check location and remote eligibility.
5. Check experience.
6. Check skills.
7. Check employment type.
8. Check international eligibility and visa information.
9. Compare suitable jobs.

This project attempts to automate that research process while remaining transparent and modifiable.

It is also an open-source engineering project. Other developers should be able to inspect the implementation, run it, replace providers, add job sources, improve prompts, change ranking logic, add tests, or build a UI on top of the existing pipeline.

---

## What the Agent Does

```text
Natural-Language User Request
            |
            v
    Requirement Parser
            |
            +--------------------+
            |                    |
            v                    v
   Job Requirements      Candidate Profile
            |
            v
      Search Strategy
            |
            v
       Job Discovery
        /         \
       /           \
      v             v
 Arbeitnow       Web Search
                    |
                    v
            Tavily Discovery
                    |
                    v
       Normalization + Deduplication
                    |
                    v
          Hard Requirement Filtering
                    |
                    v
          Preliminary Deterministic
                 Scoring
                    |
                    v
            Candidate Selection
                    |
                    v
          Job-Page Enrichment
                    |
                    v
             AI Job Analysis
                    |
                    v
              Final Ranking
                    |
                    v
           Formatted Results
```

---

## Example

A user can provide:

```text
Find remote junior data analyst jobs in India,
full-time, with Excel and SQL.
I have 1 year of experience.
```

The parser can produce:

```text
Role: Data Analyst
Location: India
Remote: Required
Employment: Full-time
Skills: Excel, SQL
Candidate experience: 1 year
Keywords: remote, junior, data analyst
```

The system then discovers jobs, filters them, enriches promising listings, analyzes them, and ranks them.

A typical result contains:

```text
1. Junior Data Analyst — Example Company

Match: 82/100
Confidence: High
Location: India
Remote: True
Source: Lever

Why it matches:
- Requested role appears in the job title.
- Location matches the request.
- Remote work is supported.
- SQL is listed as a required skill.

Concerns:
- Salary is not provided.
- Visa sponsorship is not confirmed.

Apply:
https://example.com/job
```

Actual results vary because job availability and web-search results are dynamic.

---

# Features

## Natural-language requirements

Users do not need to manually fill a form. The system extracts role, location, remote preference, experience, employment type, skills, salary, applicant country, visa requirements, and keywords.

## Candidate profile extraction

The candidate's experience and skills are represented separately from job requirements. For example, `I have 1 year of experience` becomes candidate experience, not an automatic one-year minimum requirement for every job.

## Multi-source discovery

Current discovery combines **Arbeitnow** and **Tavily-powered web search**. Web search can discover direct listings hosted on platforms such as Greenhouse, Lever, and Ashby.

## Search-query generation

The search strategy generates multiple queries from structured requirements, for example:

```text
remote junior data analyst jobs India
remote data analyst Excel SQL jobs India
remote data analyst jobs India
```

## Normalization

Different sources expose different field names and formats. The normalization layer converts them into the project's common `Job` model.

## URL cleaning

Markdown-wrapped and embedded URLs are converted into usable application URLs when possible.

## Deduplication

Repeated results from different searches are deduplicated, primarily using the job URL.

## Hard filtering

Clear constraints such as location and required remote status are applied before expensive AI analysis.

### Missing skill evidence is not automatically a mismatch

A short search snippet that does not mention SQL does not prove that SQL is not required. Therefore missing skill evidence is handled differently from an explicit contradiction, and detailed skill assessment is deferred to analysis.

## Preliminary scoring

Jobs are deterministically scored before LLM analysis. Only the strongest candidates proceed to expensive enrichment and AI analysis.

## Job-page enrichment

For selected candidates, the system attempts to retrieve the actual job page and extract useful sections such as responsibilities, qualifications, requirements, skills, experience, salary, and compensation.

## AI analysis

The analyzer extracts structured information including role relevance, required/preferred skills, experience, employment type, remote status, international eligibility, visa sponsorship, salary, evidence, and concerns.

## Final ranking

The analyzed jobs are ranked using the richer structured information.

---

# Architecture

The core pipeline is:

```text
User Query
  -> Requirement Parser
  -> Candidate Profile + Job Requirements
  -> Search Strategy
  -> Job Discovery
  -> Normalization / Deduplication
  -> Hard Filtering
  -> Preliminary Scoring
  -> Top Candidate Selection
  -> Job-Page Enrichment
  -> AI Analysis
  -> Final Ranking
  -> Formatting
```

The project is intentionally modular. Search, enrichment, analysis, scoring, and formatting can be changed independently.

---

# Detailed Components

## 1. Requirement Parser

Converts natural language into `JobRequirements` and `CandidateProfile` objects.

## 2. Candidate Profile

Stores information about the person searching, including experience, skills, education, current country, desired locations, and desired employment types.

## 3. Search Strategy

Builds search queries but does not execute searches. This keeps query construction independent from search providers.

## 4. Job Discovery

Coordinates Arbeitnow and web discovery, normalizes returned jobs, and deduplicates them.

## 5. Web Discovery

Uses Tavily to search for real job opportunities and an LLM to convert search results into structured job data. It attempts to avoid generic career advice, news, salary articles, and non-vacancy pages.

## 6. Job Normalization

Converts source-specific dictionaries into the common `Job` model.

Typical fields include:

```text
title
company
location
remote
remote_scope
url
source
description
visa_sponsorship
remote_evidence
tags
job_types
source_evidence
```

## 7. Deduplication

Uses job URLs as the primary identity key so the same vacancy found through multiple queries is not returned repeatedly.

## 8. Hard Requirement Filtering

Rejects jobs that clearly violate explicit constraints such as location or mandatory remote work.

## 9. Preliminary Scoring

Ranks surviving jobs deterministically so expensive AI processing is reserved for the strongest candidates.

## 10. Candidate Selection

`analysis_limit` controls how many jobs proceed to enrichment and AI analysis.

Example:

```python
run_job_search(query, analysis_limit=5)
```

## 11. Job-Page Enrichment

`job_enricher.py` attempts to fetch a selected job page, remove scripts/styles/HTML, decode text, identify relevant job sections, and add the resulting text to `Job.description`.

The extractor looks for sections such as:

```text
About the Role
Job Description
Responsibilities
What You'll Do
What We're Looking For
Requirements
Qualifications
Skills
Experience
Benefits
Salary
Compensation
```

If a page cannot be retrieved, the original discovery data is retained.

## 12. AI Job Analysis

The analyzer produces a structured `JobAnalysis` and is instructed not to invent missing information. It distinguishes remote/hybrid/onsite/unclear and confirmed/not-confirmed/unclear states where appropriate.

## 13. Final Ranking

The ranking stage combines deterministic and AI-derived information to produce the final ordered jobs.

## 14. Result Formatting

The formatter creates human-readable results containing score, confidence, location, remote status, source, reasons, concerns, and an application URL.

---

# Design Principles

## Do not let the LLM do everything

Use deterministic logic for reliable tasks such as deduplication, basic filtering, query generation, normalization, and preliminary scoring. Use LLMs for semantic interpretation.

## Unknown is different from No

If SQL is not present in a short snippet, that does not prove SQL is not required. Likewise, if visa sponsorship is not mentioned, that does not prove sponsorship is unavailable. The system tries to preserve uncertainty explicitly.

## Minimize unnecessary API usage

The architecture narrows a large result set before expensive LLM calls:

```text
Many jobs -> filtering -> preliminary scoring -> small candidate set -> enrichment -> LLM analysis
```

## Separate acquisition from analysis

Discovery, normalization, filtering, enrichment, analysis, and ranking are separate stages so they can be tested and replaced independently.

## Fail gracefully

External services can return 403s, timeouts, incomplete data, invalid responses, or rate limits. A failure involving one job should not unnecessarily terminate the entire workflow.

---

# Project Structure

```text
job-research-agent/
|
|-- analyzer.py
|-- formatter.py
|-- job_discovery.py
|-- job_enricher.py
|-- job_search.py
|-- match_scorer.py
|-- models.py
|-- normalizer.py
|-- orchestrator.py
|-- ranker.py
|-- requirement_parser.py
|-- requirements.py
|-- requirements_filter.py
|
|-- web_discovery.py
|-- web_normalizer.py
|
|-- search/
|   `-- search_strategy.py
|
|-- llm/
|   `-- llm_client.py
|
|-- test_url_cleaner.py
|-- test_tavily_search.py
|-- test_tavily_domains.py
|-- test_job_discovery_integration.py
|-- test_job_enricher.py
|-- test_orchestrator_mock.py
|-- test_orchestrator.py
|
|-- .env.example
|-- .gitignore
|-- README.md
`-- LICENSE
```

The exact structure may evolve as the project develops.

---

# Technology Stack

### Programming

- Python
- Dataclasses
- Type hints
- Standard Python libraries

### Web / Data

- Tavily
- Requests
- HTTP APIs
- JSON
- HTML-to-text processing
- Regular expressions

### AI

- Groq
- OpenAI-compatible LLM interfaces
- Structured JSON generation

### Engineering

- Modular architecture
- Deterministic filtering
- Multi-stage ranking
- LLM-based semantic extraction
- Job-page enrichment
- Integration testing

---

# Requirements

Recommended:

- Python 3.10+
- Git
- Internet access
- Tavily API key
- Groq API key
- OpenAI API key if the configured fallback layer uses it

Provider configuration may evolve over time.

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/job-research-agent.git
cd job-research-agent
```

Replace `YOUR_USERNAME` with the repository owner or your fork.

## 2. Create a virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
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

If a dependency is missing during development, install it into the active virtual environment.

---

# Environment Variables

Create `.env` from `.env.example`.

Example:

```env
TAVILY_API_KEY=your_tavily_api_key
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
```

Never commit the real `.env` file or API keys. Keep credentials in local environment variables and keep `.env` ignored by Git.

---

# Running the Project

The complete workflow can be executed through the orchestrator:

```python
from orchestrator import run_job_search

result = run_job_search(
    "Find remote junior data analyst jobs in India, "
    "full-time, with Excel and SQL. "
    "I have 1 year of experience."
)

print(result)
```

The repository also contains an end-to-end test workflow:

```powershell
python test_orchestrator.py
```

---

# Understanding the Output

A normal run can contain stages such as:

```text
PARSED REQUIREMENTS
...

CANDIDATE PROFILE
...

Jobs discovered: 180
Jobs after filtering: 2
Jobs selected for AI analysis: 1

Fetching job pages for 1 selected jobs...
Fetching: Junior Data Analyst — Example Company

1. Junior Data Analyst — Example Company
   Match: 82/100
   Confidence: High
   Location: India
   Remote: True
   Source: Lever
```

Exact results vary because job availability and web search results are dynamic.

---

# Testing

Run focused tests individually:

```powershell
python test_url_cleaner.py
python test_tavily_search.py
python test_tavily_domains.py
python test_job_discovery_integration.py
python test_job_enricher.py
python test_orchestrator_mock.py
python test_orchestrator.py
```

### What they cover

- `test_url_cleaner.py` — URL normalization
- `test_tavily_search.py` — Tavily discovery and structured extraction
- `test_tavily_domains.py` — job-hosting/ATS discovery behavior
- `test_job_discovery_integration.py` — discovery and normalization integration
- `test_job_enricher.py` — direct job-page extraction
- `test_orchestrator_mock.py` — controlled orchestration behavior
- `test_orchestrator.py` — end-to-end workflow

For a release or fresh setup, run the suite from a clean terminal and investigate failures individually.

---

# Error Handling

## HTTP 403

Some websites block automated requests. The enrichment layer catches the failure and keeps the existing discovery data.

## Search API failure

A source failure is handled without unnecessarily terminating the complete workflow.

## LLM failure

LLM providers can return rate-limit, token-limit, validation, or service errors. The shared provider layer and surrounding pipeline are designed to handle failures without treating every external error as a program crash.

## Missing fields

Missing information remains missing rather than being fabricated.

## Incomplete snippets

Search snippets may be too short for meaningful analysis, which is why selected jobs are passed through page enrichment before AI analysis when possible.

---

# Known Limitations

This is an active open-source learning project, not a perfect job database.

### Job-page access

Some websites block automated requests or require browser execution. Enrichment cannot guarantee access to every vacancy.

### Search quality

Search engines and aggregators may return duplicate, expired, incomplete, generic, or non-direct listings. The system attempts to prioritize better sources but cannot guarantee perfect source quality.

### Job freshness

The system does not guarantee that every listing is still accepting applications. Users should verify the vacancy on the original employer or job platform.

### AI analysis

LLM analysis can be wrong. The analyzer is designed to use evidence and preserve uncertainty, but it should not replace human verification.

### International eligibility

Remote does not automatically mean globally remote. Country restrictions may not be obvious in a search result.

### Visa sponsorship

Absence of a sponsorship statement does not prove sponsorship is unavailable. The system uses `not_confirmed` when appropriate.

---

# Security

This repository is intended to be public/open source, so credential handling is critical.

Never commit:

```text
.env
```

or real API credentials inside source code, tests, documentation, or examples.

Use `.env.example` for variable names only.

Before publishing, check:

```powershell
git status
git ls-files
```

Make sure `.env` is not tracked and no credentials appear in tracked files.

If a real secret has ever been committed to a public repository, treat it as compromised and rotate/revoke it.

---

# Extending the Project

The architecture is intended to allow independent extensions.

A new source can follow:

```text
External Source
      |
      v
    Fetch
      |
      v
 Raw Job Data
      |
      v
 Normalize
      |
      v
  Job Model
      |
      v
Existing Pipeline
```

A new ranking method can operate on the existing normalized jobs without rewriting discovery.

A new LLM provider can be introduced behind the shared LLM interface without changing the job-discovery layer.

---

# Adding a New Job Source

A new provider should ideally have source-specific fetching and normalization code. Do not force the rest of the application to understand the provider's proprietary schema.

For example, if a source returns:

```json
{
  "job_name": "Data Analyst",
  "city": "Bangalore",
  "employment": "Full Time"
}
```

its adapter should convert this into the project's standard `Job` representation.

---

# Replacing the LLM Provider

The AI layer is separated from discovery, filtering, normalization, enrichment, and ranking.

This makes it possible to experiment with different LLMs or providers without rewriting the rest of the application.

---

# Improving Ranking

The ranking architecture separates:

```text
Preliminary deterministic score
```

from:

```text
Final AI-assisted analysis
```

Future ranking work could incorporate:

- skill similarity
- experience compatibility
- salary preferences
- location preferences
- company preferences
- source quality
- evidence quality
- confidence penalties
- semantic similarity / embeddings
- resume-to-job similarity

---

# Roadmap

## Discovery

- [ ] Add more job APIs
- [ ] Add more direct company career sources
- [ ] Improve ATS detection
- [ ] Improve direct-listing prioritization
- [ ] Improve duplicate detection

## Enrichment

- [ ] Improve Greenhouse extraction
- [ ] Improve Lever extraction
- [ ] Improve Ashby extraction
- [ ] Improve Workday extraction
- [ ] Add browser-based retrieval where appropriate
- [ ] Improve structured section extraction

## Matching

- [ ] Better skill matching
- [ ] Better experience compatibility
- [ ] Resume-to-job matching
- [ ] Candidate-specific ranking preferences
- [ ] Semantic skill similarity
- [ ] Salary normalization

## International Jobs

- [ ] Better country eligibility detection
- [ ] Better visa sponsorship detection
- [ ] Remote-country restriction detection
- [ ] Work authorization analysis

## User Experience

- [ ] CLI interface
- [ ] Web interface
- [ ] Saved searches
- [ ] Job history
- [ ] Job alerts
- [ ] CSV/JSON export
- [ ] Resume upload
- [ ] Personalized dashboards

## Engineering

- [ ] More automated tests
- [ ] Improved logging/observability
- [ ] Docker support
- [ ] CI/CD
- [ ] Contribution guidelines
- [ ] Plugin/source architecture
- [ ] Better configuration management

---

# Contributing

Contributions are welcome.

Useful contribution areas include:

- New job sources
- Better job-page extraction
- Better ranking algorithms
- Tests
- Prompt improvements
- Documentation
- Bug fixes
- Output formats
- International eligibility detection
- Error handling
- Performance improvements

Suggested workflow:

```bash
git checkout -b feature/my-improvement
```

Make the change, run relevant tests, then:

```bash
git add .
git commit -m "Add my improvement"
git push
```

For larger architectural changes, open an issue first to discuss the approach.

---

# Learning Goals

This project is intentionally being developed as a practical learning project.

### Python

- Modular application structure
- Dataclasses
- Type hints
- Exception handling
- API clients
- Module organization

### AI Engineering

- LLM integration
- Prompt engineering
- Structured JSON generation
- Provider abstraction
- Token management
- Fallback providers
- AI-assisted ranking

### Agent Architecture

- Multi-stage workflows
- Tool/API integration
- Deterministic + probabilistic components
- Context management
- Candidate selection
- External data acquisition
- Failure recovery

### Web and Data

- Search APIs
- HTTP requests
- HTML extraction
- URL processing
- Normalization
- Deduplication

### Software Engineering

- Modular architecture
- Integration tests
- Mock testing
- Debugging
- API rate-limit handling
- Configuration management
- Git/GitHub workflows

### Open Source

- Documentation
- Repository organization
- Contribution workflows
- Reproducibility
- Public code quality
- Credential security

The goal is to demonstrate not only an AI feature, but the engineering process required to build and maintain an AI-powered application.

---

# Open Source Philosophy

The project is intended to remain open source and accessible to developers who want to learn from it, modify it, or build on it.

You are encouraged to:

- Fork it
- Experiment with it
- Replace components
- Add new sources
- Try different LLMs
- Improve prompts
- Build a UI
- Improve ranking
- Add tests
- Submit pull requests

The architecture is deliberately modular so that a contributor can work on one area without first understanding the entire codebase.

For example:

```text
Search contributor
    -> search/
    -> web_discovery.py
    -> job_discovery.py

AI contributor
    -> analyzer.py
    -> llm/

Matching contributor
    -> match_scorer.py
    -> ranker.py
    -> requirements_filter.py

Web extraction contributor
    -> job_enricher.py
    -> web_normalizer.py
```

---

# Disclaimer

This project is a research and learning tool.

It does not guarantee:

- job availability
- application success
- accuracy of job descriptions
- salary accuracy
- visa sponsorship
- international applicant eligibility
- continued availability of listings

Always verify important information on the original employer or job-platform listing before applying.

The agent should be treated as an assistant for job research, not as a replacement for human verification.

---

# Author

**G. Krishna Gopal**

This project explores the intersection of:

- Artificial intelligence
- Software engineering
- Data
- Automation
- Research
- Career technology

It is being developed both as an open-source tool and as a practical way to build engineering skills through a real, evolving application.

---

# License

This project is intended to use the **MIT License**.

The MIT License permits use, modification, distribution, and derivative work subject to the license terms and preservation of the applicable copyright notice.

See [`LICENSE`](LICENSE) for the complete license text.

---

# New User Quick Start

If you are new to the project, you do not need to understand the entire architecture before running it.

Recommended path:

```text
1. Read this README
        |
        v
2. Clone the repository
        |
        v
3. Create a virtual environment
        |
        v
4. Configure .env
        |
        v
5. Run the tests
        |
        v
6. Run test_orchestrator.py
        |
        v
7. Read orchestrator.py
        |
        v
8. Explore individual modules
        |
        v
9. Modify one component
        |
        v
10. Add a test
        |
        v
11. Submit an improvement
```

The best way to understand the project is to follow the pipeline from beginning to end:

```text
User Request
    -> Requirement Parser
    -> Search Strategy
    -> Job Discovery
    -> Normalization
    -> Filtering
    -> Scoring
    -> Enrichment
    -> AI Analysis
    -> Ranking
    -> Results
```

Every stage exists for a specific reason and can be independently improved.

---

**If you find the project useful, fork it, experiment with it, open an issue, or contribute improvements.**
