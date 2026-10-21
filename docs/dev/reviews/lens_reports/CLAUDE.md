# docs/dev/reviews/lens_reports/ — the 2026-09-17 code review's per-lens reports

One file per lens of the code review chartered by `docs/dev/reviews/code_review_criteria_draft.md` (ratified by Frank 2026-09-17). Each is one opus lane's own voice, read-only over the primary tier (`src/`, `cli/`, `lib/`), REPORT-ONLY (no refactoring in the review phase). The manager's synthesis (`docs/dev/reviews/YYYY-MM-DD-code-review.md`) dedupes and ranks per A4; on any disagreement the synthesis wins.

## Standing rules

- Maintenance: add a row per lens report as it lands; historical once the synthesis is written, and never edited afterwards.
- Every report carries the charter's admissibility apparatus: A1 (cite and argue against any ruled record it contradicts, or drop), A2 (a duplication finding names the shared abstraction: signature, call sites, what varies), A3 (check-coupling annex: sabotage/codegen/abi anchors bound to code a fix would move), A4 (severity/effort/blast vocabulary), A5 (cite the metric artifact under `tools/review/out/`), and a PROBED-AND-HELD list.
- Standing do-nots recorded here: do not merge the nine `atomic.c` predicates (extract only their traversal, lens 1 §5); do not unit-test a rung's emitted shape (duplicates oracle coverage, lens 5); a unit test needs a helper's own total input domain against an independent oracle, never fabricated input at sample size zero (`decisions.md` [M4.7a]); moving a verbatim same-file block costs zero sabotage-anchor re-aims but RE-INDENTING breaks them (emitvm_second_pass §3.5); the non-emitting passes of `pcrec_emit_vm` must NOT move to `src/opt/` (`src/core/internal.h` rules the split); a proxy metric counting a shape's symptom goes stale once the symptom is hand-fixed (lens 10).

## Files

- lens1_semantic_duplication.md — LENS 1 (lane lens1dup): 12 ranked extracts X1-X12, rejected detector groups, lens-11 join table, unreviewed remainder.
- lens2_domain_tool_separation.md — LENS 2 (lens2sep): text-emission mechanism map, the one kit proposal (emitters are `core/sb.c`'s customers).
- lens3_config_centralization.md — LENS 3 (lens3cfg): magic numbers / config, anchored to D90 (`limits.def`); F3/F5 FIX-NOW items.
- lens4_clarity_archaeology.md — LENS 4 + LENS 7 (lens4clar): clarity and archaeology migration inventory.
- lens5_unit_seams.md — LENS 5 (lens5unit): the existing unit tier, `tests/lib/unit_cc.sh`/`san_scripts.txt` shape, allocation-failure injector, saturating-add agreement check.
- lens6_dependency_rxt_cut.md — LENS 6 (lens6dep): dependency hierarchy, the rxt cut, call-level layer matrix, `src/gen/enc/` misfiling.
- lens8_error_cleanup.md — LENS 8 (lens8err): `ctx_nomem`/`longjmp` discipline audit; `Job.scr_test`/`scr_desc` hole.
- lens9_public_surface.md — LENS 9 (lens9pub): public-surface findings P1-P8 (unprefixed exports, D104).
- lens10_emission_kit_charter.md — LENS 10 (lens10kit): emission-kit unification WAVE 1 charter, stage plan, stage 0 long-prefix sweep.
- lens10_evidence/ — lens10kit's five read-only measurement scripts (own CLAUDE.md; not built or read by any check).
- lens11_function_altitude.md — LENS 11 (lens11alt): function-altitude rubric over the 31 functions at 100+ lines, F1-F15.
- emitvm_second_pass.md — the `src/gen/emit_vm.c` second pass (emitpass2): 15-layer map, anchor counts, extraction verdicts.
- emitvm_evidence/ — its six reproduction scripts (own CLAUDE.md).
- synthesis_collation.md — lane `collate`: mechanical collation of all twelve reports (findings table, overlap clusters, rulings-for-Frank, FIX-NOW, probed-and-held, follow-on register); resolves nothing.

## Pointers

`docs/dev/reviews/code_review_criteria_draft.md`; `docs/dev/reviews/YYYY-MM-DD-code-review.md` (synthesis); `tools/review/out/`; decisions D58, D77, D90, D104.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/docs__dev__reviews__lens_reports.md
