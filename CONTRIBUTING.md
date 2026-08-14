# Contributing to AI Job Research Agent

Thank you for your interest in contributing to the AI Job Research Agent.

This project is an open-source, modular AI-assisted job research system designed to discover, normalize, filter, enrich, analyze, score, and rank job opportunities based on a user's natural-language requirements.

The project is intended to be useful both as a practical job-research tool and as an open learning project. Contributions that improve reliability, architecture, testing, documentation, extensibility, and developer experience are welcome.

---

## Table of Contents

- [Before You Start](#before-you-start)
- [Development Setup](#development-setup)
- [Project Architecture](#project-architecture)
- [Important Design Principles](#important-design-principles)
- [Working on the Codebase](#working-on-the-codebase)
- [Testing Strategy](#testing-strategy)
- [Adding or Modifying Job Sources](#adding-or-modifying-job-sources)
- [Working with the LLM Layer](#working-with-the-llm-layer)
- [Changing Requirements and Filtering](#changing-requirements-and-filtering)
- [Changing Scoring and Ranking](#changing-scoring-and-ranking)
- [Job-Page Enrichment](#job-page-enrichment)
- [Error Handling](#error-handling)
- [Security and API Keys](#security-and-api-keys)
- [Documentation](#documentation)
- [Code Style](#code-style)
- [Commit Guidelines](#commit-guidelines)
- [Pull Requests](#pull-requests)
- [Bug Reports](#bug-reports)
- [Feature Requests](#feature-requests)
- [Adding a New LLM Provider](#adding-a-new-llm-provider)
- [Adding a New Discovery Source](#adding-a-new-discovery-source)
- [Contributor Checklist](#contributor-checklist)
- [Design Philosophy](#design-philosophy)

---

# Before You Start

Please read the main [README](README.md) before making substantial changes.

The README documents:

- project purpose
- architecture
- installation
- configuration
- discovery
- normalization
- filtering
- scoring
- ranking
- AI analysis
- enrichment
- testing
- limitations

For a substantial architectural change, open an issue before implementing it. This makes it possible to discuss the proposed design and avoid duplicate or incompatible work.

For a small bug fix, documentation improvement, test improvement, or narrowly scoped enhancement, you can generally proceed directly with a pull request.

---

# Development Setup

## 1. Fork the Repository

If you are contributing from your own GitHub account, fork the repository:

```text
https://github.com/krishna93175/job-research-agent
```

Then clone your fork:

```bash
git clone https://github.com/YOUR_USERNAME/job-research-agent.git
cd job-research-agent
```

Add the upstream repository if you want to keep your fork synchronized:

```bash
git remote add upstream https://github.com/krishna93175/job-research-agent.git
```

Verify:

```bash
git remote -v
```

---

## 2. Create a Virtual Environment

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

---

## 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Copy the example environment file:

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Add the API credentials required for the live integrations you intend to use.

Never commit `.env`.

---

# Project Architecture

The project follows a staged pipeline:

```text
User Query
    |
    v
Requirement Parser
    |
    +--------------------+
    |                    |
    v                    v
JobRequirements     CandidateProfile
    |
    v
Search Strategy
    |
    v
Job Discovery
    |
    +----------+-----------+
    |          |           |
    v          v           v
Arbeitnow   Web Search   Other Sources
    |          |           |
    +----------+-----------+
               |
               v
          Normalization
               |
               v
          Deduplication
               |
               v
        Requirements Filter
               |
               v
       Candidate Selection
               |
               v
        Job-Page Enrichment
               |
               v
          AI Analysis
               |
               v
        Match Scoring
               |
               v
             Ranker
               |
               v
           Formatter
               |
               v
          Final Results
```

## Core modules

### `requirement_parser.py`
Converts natural-language requests into `JobRequirements` and `CandidateProfile`. It uses an LLM, so deterministic tests should mock the LLM response.

### `requirements.py`
Defines structured requirement and candidate data models. Changes here can affect many components.

### `search_strategy.py`
Builds deterministic search queries from role, location, remote, experience, skills, employment type, and keywords.

### `job_discovery.py`
Coordinates discovery from multiple sources and returns normalized jobs.

### `job_search.py`
Contains retrieval logic for the relevant job-search API/source.

### `web_discovery.py`
Handles web-based job discovery and extraction.

### `normalizer.py`
Normalizes source-specific job records into the common job representation.

### `web_normalizer.py`
Normalizes web-discovered jobs, including incomplete metadata and wrapped URLs.

### `url_cleaner.py`
Extracts plain HTTP/HTTPS URLs from Markdown-formatted or otherwise wrapped strings.

### `deduplicator.py`
Removes duplicate opportunities found across multiple sources.

### `requirements_filter.py`
Applies hard requirements such as role, location, remote status, employment type, skills, salary, experience, and visa requirements.

### `match_scorer.py`
Calculates compatibility scores from job and candidate evidence.

### `matcher.py`
Contains matching-related logic.

### `job_relevance.py`
Handles relevance-oriented evaluation. Relevance should not silently replace hard requirements.

### `ranker.py`
Ranks candidates after filtering and scoring.

### `job_enricher.py`
Attempts to retrieve additional information from job pages.

### `analyzer.py` / `job_analyzer.py`
Perform AI-assisted analysis from available evidence.

### `llm_client.py`
Provides the LLM interaction and fallback layer.

### `orchestrator.py`
Coordinates the complete workflow.

### `formatter.py`
Formats final results for presentation.

---

# Important Design Principles

## 1. Evidence over assumptions

Do not manufacture facts that are not supported by the available job evidence.

## 2. Unknown is not false

For example:

```text
SQL explicitly required
    -> positive evidence

SQL explicitly not required
    -> contradiction

SQL not mentioned
    -> unknown
```

Missing evidence should not automatically be treated as a negative result.

## 3. Deterministic logic where possible

Prefer ordinary Python logic for:

- URL cleaning
- normalization
- deduplication
- filtering
- score calculations
- query construction
- validation

Use an LLM when semantic reasoning actually adds value.

## 4. Cost-aware AI usage

The intended pipeline is:

```text
Discover
   ↓
Normalize
   ↓
Deduplicate
   ↓
Hard Filter
   ↓
Select Candidates
   ↓
Enrich
   ↓
AI Analysis
```

Do not send every discovered job to an expensive model if deterministic filtering can eliminate irrelevant jobs first.

## 5. Keep components replaceable

Discovery sources, LLM providers, enrichment mechanisms, and ranking strategies should remain modular.

## 6. Preserve uncertainty

If a source does not provide a field, keep it unknown rather than guessing.

---

# Working on the Codebase

Before modifying a module, identify:

1. Its responsibility.
2. Its callers.
3. Its tests.
4. Its external dependencies.
5. Its downstream consumers.
6. Whether it affects filtering, scoring, or ranking.

For larger changes, map the data flow before implementing the change.

---

# Testing Strategy

The repository separates tests into two categories.

## Credential-free tests

These are appropriate for GitHub Actions and should be deterministic and reproducible.

Examples include:

```text
test_url_cleaner.py
test_requirements.py
test_requirements_filter.py
test_deduplicator.py
test_strategy.py
test_web_normalizer.py
test_match_scorer.py
test_ranker.py
test_formatter.py
test_job_discovery_integration.py
test_job_enricher.py
test_orchestrator_mock.py
```

The exact CI list is defined in:

```text
.github/workflows/tests.yml
```

## Live integration tests

These may require credentials, network access, live search results, or provider quotas:

```text
test_discovery.py
test_tavily_search.py
test_tavily_domains.py
test_tavily_india.py
test_groq_analyzer.py
test_web.py
test_orchestrator.py
```

They should generally be run locally rather than being required for credential-free CI.

---

# Mocking External Services

Do not call a live LLM from a deterministic unit test merely to construct test fixtures.

For example:

```python
import requirement_parser

def mock_generate_json(system_prompt, user_prompt):
    return {
        "job_requirements": {
            # deterministic test data
        },
        "candidate_profile": {
            # deterministic test data
        },
    }

requirement_parser.generate_json = mock_generate_json
```

This avoids API costs, credentials, rate limits, and nondeterministic failures.

Mocks should represent realistic provider responses and still exercise the application logic being tested.

---

# Running Tests

Examples:

```powershell
python test_url_cleaner.py
python test_strategy.py
python test_requirements.py
python test_requirements_filter.py
python test_match_scorer.py
python test_ranker.py
python test_orchestrator_mock.py
```

Run the relevant tests after modifying a component.

Before opening a pull request, run the credential-free tests locally.

Run live integration tests separately when credentials and network access are available.

---

# Adding or Modifying Job Sources

A new source should generally follow:

```text
External Source
      |
      v
Source Fetcher
      |
      v
Raw Source Data
      |
      v
Normalizer
      |
      v
Common Job Model
      |
      v
Existing Pipeline
```

Provide available fields such as:

- title
- company
- location
- remote status
- remote scope
- URL
- employment type
- description
- source
- evidence
- salary
- visa information

Do not assume every source provides every field.

---

# Adding a New Discovery Source

When adding a source:

1. Understand its API/public interface.
2. Check its rate limits and terms.
3. Isolate retrieval from normalization.
4. Normalize into the common `Job` model.
5. Add deterministic tests using mocked responses.
6. Add live integration coverage when useful.
7. Document credentials and setup requirements.
8. Consider deduplication behavior.

Do not make downstream modules depend directly on a source-specific schema.

---

# Working with the LLM Layer

LLM calls are less deterministic and potentially more expensive than ordinary code.

When modifying LLM behavior:

- keep prompts explicit
- request structured output where appropriate
- validate returned structures
- handle malformed output
- handle provider failures
- respect token/context limits
- avoid unnecessary calls
- preserve fallback behavior

---

# Prompt Changes

Prompts are part of application behavior.

When changing a prompt:

1. Explain why.
2. Test common inputs.
3. Test ambiguous inputs.
4. Test missing-information cases.
5. Validate structured output.
6. Check for hallucinated information.
7. Consider token usage.

Do not optimize a prompt around only one example query.

---

# Changing Requirements and Filtering

Requirement changes can alter which jobs are returned.

Distinguish:

- hard requirements
- soft preferences
- candidate attributes
- job attributes
- unknown information

For example:

```text
Candidate has 1 year of experience.
```

is a candidate attribute.

```text
Job requires 1 year of experience.
```

is a job requirement.

These must not be conflated.

---

# Changing Scoring and Ranking

Changes to:

```text
match_scorer.py
matcher.py
job_relevance.py
ranker.py
```

should be accompanied by tests.

When changing scoring:

1. Identify the signal being changed.
2. Explain the proposed change.
3. Explain its expected ranking effect.
4. Add or update tests.
5. Check edge cases.
6. Verify missing evidence is handled consistently.

Avoid arbitrary weights without justification.

---

# Job-Page Enrichment

External job pages can return:

```text
200 OK
403 Forbidden
404 Not Found
429 Too Many Requests
Timeout
JavaScript-only pages
Bot protection
Changed page structure
```

Enrichment failures should generally reduce available evidence rather than destroy an otherwise valid discovery result.

---

# Error Handling

External failures are normal.

Avoid silently swallowing exceptions:

```python
except Exception:
    pass
```

unless the behavior is explicitly intentional.

When catching an exception, provide useful context where appropriate.

A failure in one external source should not unnecessarily destroy results from other sources.

---

# Security and API Keys

Never commit:

```text
.env
API keys
access tokens
private credentials
service-account credentials
```

Use `.env.example` to document configuration without exposing secrets.

If a credential is accidentally committed:

1. Revoke or rotate it immediately.
2. Remove it from the working tree.
3. Review Git history if necessary.
4. Do not assume deleting the file is sufficient.

Never post credentials in issues, pull requests, logs, or screenshots.

---

# Documentation

Update documentation when behavior changes.

Examples:

| Change | Documentation |
|---|---|
| New environment variable | `.env.example` + README |
| New discovery source | README + contributor docs |
| New LLM provider | README + configuration docs |
| New architecture component | README |
| New testing requirement | README / `CONTRIBUTING.md` |
| Breaking behavior | README + PR description |

Documentation should describe behavior that actually exists, not planned functionality.

---

# Code Style

Prefer:

- clear names
- focused functions
- type hints where useful
- explicit control flow
- small reusable functions
- comments for non-obvious decisions

Avoid:

- unnecessary abstractions
- duplicated logic
- provider-specific code in generic modules
- arbitrary magic numbers
- silent exception swallowing
- hard-coded credentials
- unrelated large refactors

The project currently uses a relatively flat module structure. Do not introduce a large package restructuring without a clear architectural reason.

---

# Commit Guidelines

Use concise commit messages describing the change.

Good examples:

```text
Add mocked requirement parser test
Fix remote location matching
Improve job URL normalization
Add GitHub Actions CI
Handle blocked job pages
Improve ranking confidence
Add contributor documentation
```

Avoid vague messages such as:

```text
update
fix
changes
stuff
```

Keep commits logically separated where practical.

---

# Pull Requests

Before opening a pull request:

- [ ] The change has a clear purpose.
- [ ] Relevant tests pass.
- [ ] New behavior has tests.
- [ ] Documentation is updated where necessary.
- [ ] No credentials or secrets are included.
- [ ] `git diff --check` passes.
- [ ] The PR description explains the change.
- [ ] Breaking changes are clearly identified.

A useful PR should explain:

### What changed?

Describe the implementation.

### Why?

Explain the problem or use case.

### How?

Describe important technical decisions.

### Testing

List the commands/tests that were run.

Example:

```text
Tests:
- python test_strategy.py
- python test_requirements.py
- python test_orchestrator_mock.py
```

---

# Bug Reports

Include:

- operating system
- Python version
- command used
- expected behavior
- actual behavior
- traceback
- whether the test was live or mocked
- relevant configuration details
- reproduction steps

Never include API keys.

If a credential appears in a log or screenshot, revoke it before publishing the report.

---

# Feature Requests

A useful feature request should explain:

1. What problem does it solve?
2. Who benefits?
3. How could it fit the current architecture?
4. Are there alternatives?
5. Does it require a new external service?
6. Does it introduce API cost or credentials?
7. How would it be tested?

Discuss large architectural changes before implementation.

---

# Adding a New LLM Provider

Use the existing LLM abstraction where possible.

Avoid scattering provider-specific calls throughout unrelated modules.

Conceptually:

```text
Application
    |
    v
LLM Abstraction
    |
    +--> Provider A
    |
    +--> Provider B
    |
    +--> Provider C
```

Consider:

- authentication
- structured output
- error handling
- rate limits
- token/context limits
- provider availability
- fallback behavior
- cost
- testability

Live provider calls should not be required for ordinary unit tests.

---

# Contributor Workflow

A typical workflow is:

```text
Fork
  |
  v
Clone
  |
  v
Create branch
  |
  v
Make focused change
  |
  v
Run tests
  |
  v
Review diff
  |
  v
Commit
  |
  v
Push branch
  |
  v
Open Pull Request
  |
  v
CI
  |
  v
Review
  |
  v
Merge
```

Create a descriptive branch:

```bash
git checkout -b fix-remote-filtering
```

or:

```bash
git checkout -b add-new-job-source
```

Avoid unrelated cleanup in the same branch as a focused change.

---

# Contributor Checklist

## Code

- [ ] The change is focused.
- [ ] Existing behavior was considered.
- [ ] No unnecessary refactoring was introduced.
- [ ] No secrets are included.

## Tests

- [ ] Relevant deterministic tests pass.
- [ ] New behavior has test coverage.
- [ ] Live integration tests were run when appropriate.
- [ ] Tests do not unnecessarily depend on live providers.

## Documentation

- [ ] README updated if user-facing behavior changed.
- [ ] `.env.example` updated if configuration changed.
- [ ] Architecture documentation updated if necessary.
- [ ] Breaking changes documented.

## Git

- [ ] `git diff --check` passes.
- [ ] Commit messages are descriptive.
- [ ] Only relevant files are included in the PR.

---

# Design Philosophy

The project is guided by these principles:

## Evidence over assumptions

Make decisions from available evidence.

## Deterministic logic where possible

Use normal code for problems that do not require semantic reasoning.

## AI where it adds value

Use AI for interpretation, extraction, and reasoning rather than basic data manipulation.

## Cost awareness

Avoid expensive LLM calls when deterministic filtering can eliminate irrelevant jobs first.

## Modularity

Keep discovery, normalization, filtering, enrichment, analysis, scoring, and ranking separable.

## Replaceability

External providers should be replaceable without rewriting the entire application.

## Reproducibility

Tests should be deterministic whenever possible.

## Transparency

Make uncertainty and unavailable information explicit.

## Accessibility for new contributors

A developer should be able to understand a module and contribute without first understanding the entire codebase.

---

# Questions and Discussion

If you are unsure where a change belongs, open an issue or discussion before making a large architectural change.

For small fixes, documentation improvements, and focused tests, a pull request is usually sufficient.

The project is intended to grow through experimentation, review, and incremental improvement. Contributions that make the system more reliable, understandable, extensible, or useful are welcome.
