# closea — plan close-out paperwork + `ongoing` / `ready` states (2026-11-10)

## STATE AT HANDOFF

STATE: delivered (branch lane/closea, commit e934bf9fa plus the report commit). Validation COMPLETE, no runs owed.

Green (worktree): `make test-plan-lint` (342 rows, 0 violations; selftest 41 plants, 18/18 rules, including plants for `STATE:ongoing` missing `why ongoing:` / `review:` and `STATE:ready` missing `ready:`), `make test-doc-lint` (7 checks), `bash tests/doc_lint/run_doc_index.sh` (DONE rc=0, 60 dangling baseline unchanged), `make strict`, `make test-claudemd-size`, `scripts/entry --selftest` (68 checks, 0 failures). `scripts/entry --work | head` shows `## ready` first.

### New states (step 1)
- `scripts/plan_lint.py`: states, Active-only placement (PL13), attributes `why ongoing:` / `review:` (ongoing only, both required), `ready:` (ready only, required), `waits:` (any row); order filed, status, those, next|trigger, refs; plants added under PL10.
- `scripts/entry`: `--work` is now ready, started, blocked, not-started, then ongoing, with `## <state>` headers (it used `## <section>`); level 1 also prints the new fields; selftest fixture grew a ready and an ongoing row plus an order check. `scripts/doc_profiles.py`, `docs/dev/doc_format.md`, `tests/plan_lint/CLAUDE.md`, plan.md Policy updated.
- Note: `--work` now includes started rows (the brief's order), so it is long; `-s SECTION` and `--state S` still filter.

### Rows restated
- ongoing (own `why ongoing:` + `review:`): OPTLOOP, MEMFN, OPT-SIMD, IR-FORM.
- ready: VAR (M9; pattern half 809aab12, gate 9ae59f5d4), ANCH-AT (was blocked; trigger fired c44649a69 / f77ed1130; status and next rewritten), INLINE-C (stage 4 then 5; stage 3 b156d8f18; stage 4's first act is the census brief, a judgment call: it is internal prep, not an outside wait).
- kept started with `waits:`: VLOOKBEHIND (owner answers Q1/Q2 + build go), RUN-POS-SET (kit R-38 Part D + build go), DATA-PLAN (UPROP-MORE; A before B).

### Closed (step 2), moved verbatim (de-indented, `completed:` + DONE status line) to plan_completed.md "Completed 2026-11-10"
Every cited SHA verified with `git cat-file -e` and `merge-base --is-ancestor HEAD`:
- OPT-LITSCAN: 0bb87eda, c9dec3e4, a588c668, 8562ff3a, c13a1a2c, f116cff5; residual F5 size-floor witness filed as Candidate [LITSCAN-SIZEFLOOR].
- NULLABLE-ANCH: 02db3811, e6b6c25f (bench re-read of the two cells rides OPTLOOP).
- MEMFN-ROWCON: 37462a8e8 (N4 + G2 floors; the row's narrowed scope matches); HELD items filed as Deferred [ROWCON-TABLE-ENGINE] and [ROWCON-SNAPSHOT], each with its trigger.
- REGIME-CORPUS: b39a69c2e (steps 1-2; hand-off is [REGIME-EVAL]'s).
- LOSS-REVIEW: 4cd82e8de; remaining candidates already live in docs/dev/optloop/lossreview/fixes.md (stated in the done line).
- BENCH-UTF8: NOT closed; status now "pcrec side built; awaiting bench-dev confirmation (asked 2026-11-10)".

### Stale status lines rewritten (step 3)
MEASURE-SET (zen4-grid3@1 692ec83b7; next now M1/M2/M3), DOC-INDEX (T1 81449f5a0, 1.0 582a0b49f + 092516b60, T1b 39da816d7; next T2 + CITE-FORMS), XARCH-DEV (U2+U3 cf578177e landed, abi 98; its fired `trigger:` became `next:`).

### Declined / left alone
- UCP, REGIME, the five quiet optimization rows, FEAT-FAMILIES, ENGINE-WHY, FIND-MINW, COND-FAMILY untouched (step 4).
- Found, not edited: another row's `trigger:` still reads "[OPT-LITSCAN] S4 lands" (the FINDINGS-C6 HELD row, plan.md around the `trigger: [OPT-LITSCAN] S4 lands` line); S4 has landed, so that trigger has fired. It is outside this lane's scope; the manager should rule it.
- Did not touch GATE-RUNS / QORDER / REQ-EMPTYCAT closes (not in this brief).
