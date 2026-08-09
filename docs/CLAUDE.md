# docs/ — project working documents

Process and status documents for pcrec. The architecture itself lives in
../APPROACH.md; these files track execution against it.

## Files

- `plan.md` — milestone/step tracker mirroring APPROACH §9. Machine-greppable
  step states (`STATE:not-started|started|completed|blocked|deferred`); format
  and grep recipes documented at the top of the file. Expand a milestone into
  substeps only when work on it begins.
- `dev_journal.md` — append-only dated journal, newest at bottom. Append an
  entry after every significant work session; this is the primary
  restart/status-recovery record.
- `decisions.md` — ADR-lite decision log (D1, D2, ...): decision, why,
  revisit-when. Add an entry whenever a choice would surprise a future reader.
- `testing.md` — .rxt test-file format, harness usage, env vars, oracle
  exclusions, and how to add a per-module test directory.
- `reviews/` — compiled checkpoint critic reviews (D6), one file per
  checkpoint: findings, triage dispositions, reflection.
- `known_issues.md` — confirmed bugs in pcrec ITSELF that are deferred rather
  than fixed immediately; each has a minimal repro and a scheduled milestone.
  Failing regressions live in tests/known_fail/ (excluded from `make test`).
- `upstream_issues.md` — suspected bugs and divergences in OTHER engines
  (PCRE2, python re) found by our differential tooling; the citable
  rationale behind oracle exclusions. Add an entry whenever tooling
  implicates another engine.

Maintenance: update this file when files are added/removed or their roles change.
