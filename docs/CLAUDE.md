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
- `pcre2_compliance.md` — construct-by-construct compliance against PCRE2's
  syntax reference, with a status vocabulary that separates verified from
  believed and clean-rejection from miscompile. Periodically re-surveyed;
  its `REJECTED` rows are backed by tests/reject/ rather than asserted.
- `testing.md` — .rxt test-file format, harness usage, env vars, oracle
  exclusions, and how to add a per-module test directory.
- `extension_design.md` — PROPOSED (not adopted, not built): how a regex
  feature plugs into pcrec — one table, a NAME per row as the unit of
  enable/disable, two PORTS per row, and a RECOGNISE-then-PRODUCE seam. Written
  from scratch rather than as an amendment to D32/D33, and **partly REFUTED by
  the R13 panel**; the refutations are inline and the holes they left are marked
  `[OPEN]` for Frank. Read the PANEL OUTCOME block at the top before any section.
- `reviews/` — compiled checkpoint critic reviews (D6), one file per
  checkpoint: findings, triage dispositions, reflection.
- `known_issues.md` — confirmed bugs in pcrec ITSELF that are deferred rather
  than fixed immediately; each has a minimal repro and a scheduled milestone.
  Open at R11 close: K2 (cosmetic), K7 (a resource bug that also ABORTS the
  caller's process under a memory limit), K9 (the public API takes no pattern
  length, so a pattern containing NUL compiles as its prefix and reports
  success), K10 (tier 2, LIVE — `[\N{U+41}]` refused where libpcre2 recognises
  it), K11 (LATENT — `pcrec_ext_escape`'s two call sites are UB the moment
  that doorway returns; `[a\qb]` SIGSEGVs the compiler itself in a stub build)
  K12 (`[0-\d]` promises a module where PCRE2 says the range is permanently
  invalid; pcrec is correct today only because `\d` is unimplemented, and
  MOD-0.2 removes that guard) and K13 (twelve rows answer the CLASS position
  with module `backrefs` for constructs it can never implement — `[\8]` is the
  literal `8`, `[\k]` the literal `k`) and K14 (pcrec names a module for
  constructs its own compliance survey calls architecturally OUT-OF-SCOPE —
  `(*COMMIT)` answers "requires module 'verbs'", which D26 defines as a defect
  in as many words). Failing regressions live in tests/known_fail/ (excluded
  from `make test`).
- `upstream_issues.md` — suspected bugs and divergences in OTHER engines
  (PCRE2, python re) found by our differential tooling; the citable
  rationale behind oracle exclusions. Add an entry whenever tooling
  implicates another engine.

Maintenance: update this file when files are added/removed or their roles change.
