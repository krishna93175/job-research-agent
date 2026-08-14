# Pull Request

## Summary

Describe what this pull request changes.

## Motivation

What problem does this change solve?

Why is the change needed?

## Changes

List the main changes made in this pull request.

-
-
-

## Architecture Impact

Which parts of the system are affected?

- [ ] Requirement parsing
- [ ] Search strategy
- [ ] Job discovery
- [ ] Normalization
- [ ] URL handling
- [ ] Deduplication
- [ ] Requirements filtering
- [ ] Job enrichment
- [ ] AI analysis
- [ ] Matching/scoring
- [ ] Ranking
- [ ] Formatting/output
- [ ] LLM provider integration
- [ ] Web discovery
- [ ] Testing/CI
- [ ] Documentation
- [ ] No significant architectural impact

Explain any important architectural decisions or trade-offs.

## Testing

List the tests you ran.

Example:

python test_requirements.py
python test_requirements_filter.py
python test_orchestrator_mock.py

### Test Type

- [ ] Deterministic/local tests
- [ ] Mocked tests
- [ ] Live integration tests
- [ ] GitHub Actions / CI
- [ ] Manual testing

## External Services

Does this change interact with an external service?

- [ ] No
- [ ] Yes

If yes, identify the service and explain any relevant rate limits, credentials, or failure behavior.

## Documentation

Does this change require documentation updates?

- [ ] No
- [ ] README updated
- [ ] CONTRIBUTING.md updated
- [ ] `.env.example` updated
- [ ] Other documentation updated

## Breaking Changes

- [ ] This change is backward compatible.
- [ ] This change introduces a breaking change.

If there is a breaking change, describe what users need to do differently.

## Security

- [ ] No secrets or credentials are included.
- [ ] No new security-sensitive behavior was introduced.
- [ ] Security implications have been considered.

## Performance and Cost

Could this change affect:

- API requests
- LLM calls or token usage
- execution time
- memory usage
- CI duration
- external-service costs

- [ ] No significant impact expected.
- [ ] Impact exists and is documented below.

Explain any expected impact:

## Reviewer Notes

Highlight anything reviewers should pay particular attention to.

## Checklist

Before requesting review, confirm:

- [ ] I have reviewed my own changes.
- [ ] The pull request has a clear purpose.
- [ ] Relevant tests pass.
- [ ] New behavior has appropriate test coverage.
- [ ] I have run `git diff --check`.
- [ ] Documentation has been updated where necessary.
- [ ] I have not committed API keys, passwords, tokens, or other secrets.
- [ ] I have kept unrelated changes out of this pull request.
- [ ] I have considered backward compatibility.