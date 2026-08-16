# docs/dev/ — development-process documents

Documents that track execution against the design, not the product itself.
Append-only where noted; the restart/status-recovery record for the project.

## Files

- `plan.md` — the ACTIVE milestone/step tracker mirroring APPROACH §9;
  STATE:completed rows do not live here. Machine-greppable step states
  (`STATE:not-started|started|completed|blocked|deferred`); format and grep
  recipes documented at the top of the file. Expand a milestone into
  substeps only when work on it begins.
- `plan_completed.md` — archive of completed plan rows, grouped by
  completion date, text preserved verbatim (split from plan.md 2026-08-13).
  A row cited elsewhere as "docs/dev/plan.md [ID]" lives here once it is
  STATE:completed; `grep -c "STATE:completed" docs/dev/plan_completed.md`
  counts them.
- `dev_journal.md` — append-only dated journal, newest at bottom. Append an
  entry after every significant work session; this is the primary
  restart/status-recovery record.
- `decisions.md` — ADR-lite decision log (D1, D2, ...): decision, why,
  revisit-when. Add an entry whenever a choice would surprise a future reader.
- `known_issues.md` — confirmed bugs in pcrec ITSELF that are deferred rather
  than fixed immediately; each has a minimal repro and a scheduled milestone.
  Open as of 2026-08-16: K2 (cosmetic), K7 (a resource bug that
  also ABORTS the caller's process under a memory limit), K9 (the public
  API takes no pattern length, so a pattern containing NUL compiles as its
  prefix and reports success — rx_info.pattern_len at the M4 freeze is the
  fix's API half) and K23 (exact-minimum ambiguous-decomposition boundary
  exhausts the step budget on a 100-byte ordinary input; found by the D27
  blinded quantifier corpus 2026-08-16; regression in
  tests/known_fail/d27_nested_min_boundary.rxt; owned [M4.6]). K22
  (CLOSED 2026-08-16 by the F-1 ruling, decisions.md D47 ADDENDUM: hang
  half fixed by the interim product guard; the compile-these-shapes half
  re-homed as plan row [ENG-CLAMP]'s charter, not a bug). K18 (FIXED 2026-08-15, k18-rewrite lane: the
  empty-iteration exit lost when the ε re-arrival passes THROUGH an
  already-seen state rather than landing ON a loop entry — K17's structurally
  distinct sibling. The closure memo is now keyed on (state, open-loop
  context) and the redirect on "this loop is OPEN on my path", per
  design/k18_memo_design.md's A2; 1,459 live guard cases in tests/base/ on
  four axes, blast radius 8 of 622 corpus patterns, 251/251 changed cells
  toward the oracle. Its precondition status for M4.6's hybrid is
  DISCHARGED). K17 (FIXED 2026-08-14 same day as found —
  R21 panel E-1; the K1 one-shot guard removed from clo_visit, 120
  family tests, 294/294 changed cells toward the oracle), K10 (FIXED 2026-08-12 by MOD-0.6's K10 slice: `RF_CLASS_INVALID` removed
  from the `{U+` row, `[\N{U+41}]` now promises module `unicode-props`;
  guarded by `check_class_syntax_reach` and seven offset pins — see
  docs/dev/known_issues.md), K11 (FIXED 2026-08-11 by MOD-0.1's returned-claims epilogue: doorways
  return a tagged ExtResult, one epilogue renders refusals, call sites end in
  internal-error walls — the stub-build repro now exits 1 cleanly at both
  sites; the cls_set range-check hazard stays assigned to the first
  scalar-returning module),
  K12 (FIXED 2026-08-11 by MOD-0.1's endpoint-rule slice: the five-step §16
  order in p_class, SET-shape certified from the measured class_expect column
  through the returned-claims epilogue; body-dependent rows like `\p` keep
  their module promise until unicode-props' first WIDE producer lands —
  MOD-0.6 landed recogniser-only and deliberately kept this boundary, see
  design_notes_mod06.md §8.2 — a pinned, deliberate boundary), K13 (FIXED 2026-08-11 at [FIX-3]: the twelve
  rows answered the CLASS position with module `backrefs` for constructs it
  can never implement — `[\8]` is the literal `8`, `[\k]` the literal `k`;
  now octal/literal fallback per RF_CLASS_BASE) and K14 (FIXED 2026-08-11 in
  MOD-0.1's first slice: pcrec named a module for constructs its own
  compliance survey calls architecturally OUT-OF-SCOPE — now a ROADMAP_NEVER
  column per-row and per-VerbName, a no-promise diagnostic, and a
  both-directions prose⇔column check). Failing regressions live in
  tests/known_fail/ (excluded from `make test`).
- `upstream_issues.md` — suspected bugs and divergences in OTHER engines
  (PCRE2, python re) found by our differential tooling; the citable
  rationale behind oracle exclusions. Add an entry whenever tooling
  implicates another engine.
- `reviews/` — compiled checkpoint critic reviews (D6), one file per
  checkpoint: findings, triage dispositions, reflection.
- `wake.md` — untracked (gitignored) hand-off brief for session start/resume;
  lives in this directory but is not committed. Committed docs win on any
  disagreement with it.

Maintenance: update this file when files are added/removed or their roles
change.
