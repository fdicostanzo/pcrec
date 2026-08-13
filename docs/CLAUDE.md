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
  exclusions, how to add a per-module test directory, and (added [TT-1])
  "Tiered testing": the measured per-section runtimes behind `make
  test-corpus`/`test-cli`/etc., the touched-path -> sections guidance table,
  `make smoke`'s measured composition and floor check, and the opt-in
  `make hooks` pre-push gate. `make test` itself is unchanged by any of this
  — still the full suite, still the merge/close standard.
- `extension_design.md` — ADOPTED (D34: Part II is the redesign of record)
  and progressively BUILT through MOD-0.1..0.3 (the first producers landed
  2026-08-12): how a regex feature plugs into pcrec — one table, a NAME per row as the unit of
  enable/disable, two PORTS per row, and a RECOGNISE-then-PRODUCE seam. Written
  from scratch rather than as an amendment to D32/D33, and **partly REFUTED by
  the R13 panel**; the refutations are inline. Read the PANEL OUTCOME block at
  the top before any section. **PART II (§11-§18)** is the post-ruling redesign
  (D34): per-port recognition, always-live recognisers, lexical-mode rows for
  `\Q`/`\E`/`(?#)`, the `want`×`may` ask contract, the measured endpoint rule
  — itself reviewed the same session by R14
  (`reviews/2026-08-11-r14-part2.md`), which refuted its two central factual
  claims; corrections inline marked R14, and §18 holds the post-R14 state
  plus the five decisions left for Frank. Read BOTH panel-outcome blocks
  before any section.
- `design_notes_mod06.md` — MOD-0.6 (module `unicode-props`) phase-1 design
  note: the \p/\P syntax-port shape and its CLAIM/REFUSE dispatch rule
  (bound to options=0, R10 disposition 3), the K10 row fix, the streaming
  normalisation algorithm and its 48-significant-character boundary
  (measured, not assumed — tests/probes/probe_uprops.c), the in-class
  tail-sweep extension design, and the phase-2 test plan. ACCEPTED by the
  manager 2026-08-12; phase 2 (code) built from it — see
  tests/registry/CLAUDE.md and src/parse/CLAUDE.md's `mod_uprops.c` entry
  for what actually landed.
- `design_notes_mod07.md` — MOD-0.7 (`--explain` rewrite) phase-1 design
  note: the measured refutation of the plan row's own cure (the
  declared-vs-live agreement clause is swap-blind — both sides read
  `r->module`), the query→doorway mapping (one shared router, two callers),
  selection = prefix ∪ candidates, the election/promise/attribution clauses
  and their honest limits, exit 3 for dissent, §13's six manager rulings and
  §14's V1-V7 failing-direction measurements. ACCEPTED and built 2026-08-12
  — see cli/CLAUDE.md and src/parse/CLAUDE.md's `syntax_dump.c` entry for
  what landed.
- `reviews/` — compiled checkpoint critic reviews (D6), one file per
  checkpoint: findings, triage dispositions, reflection.
- `measurements/` — archived probe OUTPUT reports (D35, 2026-08-12):
  stable-named (`<probe>.txt`, diffable across re-runs) verbatim probe
  output with a source-information header (date, repo commit, libpcre2 and
  gcc versions), written by `scripts/measure.sh`. Evidence for reviews,
  never an oracle — no check reads them. See the directory's own CLAUDE.md.
- `known_issues.md` — confirmed bugs in pcrec ITSELF that are deferred rather
  than fixed immediately; each has a minimal repro and a scheduled milestone.
  Open at R11 close: K2 (cosmetic), K7 (a resource bug that also ABORTS the
  caller's process under a memory limit), K9 (the public API takes no pattern
  length, so a pattern containing NUL compiles as its prefix and reports
  success), K10 (FIXED 2026-08-12 by MOD-0.6's K10 slice: `RF_CLASS_INVALID` removed
  from the `{U+` row, `[\N{U+41}]` now promises module `unicode-props`;
  guarded by `check_class_syntax_reach` and seven offset pins — see
  docs/known_issues.md), K11 (FIXED 2026-08-11 by MOD-0.1's returned-claims epilogue: doorways
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

Maintenance: update this file when files are added/removed or their roles change.
