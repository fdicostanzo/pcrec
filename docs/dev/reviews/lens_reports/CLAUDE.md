# docs/dev/reviews/lens_reports/ — the 2026-09-17 code review's per-lens reports

One file per lens of the code review chartered by
`docs/dev/reviews/code_review_criteria_draft.md` (RATIFIED by Frank
2026-09-17). Each is one opus lane's own voice, read-only over the
primary tier (`src/`, `cli/`, `lib/`), delivered REPORT-ONLY — no
refactoring in the review phase. The manager's synthesis
(`docs/dev/reviews/YYYY-MM-DD-code-review.md`) dedupes across them and
ranks per A4; these stay as the per-lens evidence.

Each report carries the charter's admissibility apparatus: A3's
check-coupling annex (what the finding's fix would stale), A4's
severity/effort/blast vocabulary, and a mandatory PROBED-AND-HELD list,
because a discipline that holds is a result worth as much as a finding.

## Files

- `lens8_error_cleanup.md` — **lens 8, error-path and cleanup
  consistency** (lane `lens8err`, base `main` @ `7d444f9e`). The
  `ctx_nomem`/`longjmp` discipline, arena ownership, partial-state
  cleanup, audited tree-wide rather than where K7 forced it. Verdict:
  the discipline holds nearly everywhere, and **one live hole is K7's
  own defect verbatim** — `Job.scr_test`/`scr_desc` (added by
  `[ART-SIZE]` after K7 closed) were never given the `Ctx`
  back-pointer, so `sb_grow`'s failure path `abort()`s and kills the
  caller's process, reachable on any VM compile that takes the cursor
  rung. Six further findings (a `libdirs` leak on `cli_parse`'s own
  failure at both call sites; `emit_state_legend` silently changing the
  emitted artifact on OOM; `rxt_source.c` running two disciplines for
  one event; unobserved write errors on the `-o -` path; a half-written
  `.c`/`.h` pair) plus a check-design finding: the discipline has ZERO
  sabotage rows, its one positive control
  (`tests/resource/run_resource_tests.sh` section 2) is SKIPPED on
  darwin and can pass on a budget refusal rather than an allocator
  failure. Thirteen PROBED-AND-HELD entries, headed by the 1:1
  `Ctx`/`setjmp` pairing with no failing allocation in any pre-`setjmp`
  window (R20's tier-1 class structurally closed), the complete
  `volatile` discipline across `setjmp` backed mechanically by
  `-Wclobbered`, zero `free()` of an arena-backed pointer across 76
  sites, and zero function-local statics (library re-entry is clean).

Maintenance: add a row per lens report as it lands; historical once the
synthesis is written, and never edited afterwards.
