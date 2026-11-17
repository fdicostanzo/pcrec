# formsi report - review r35 F15 (cards.py asserts arm I emits no span loop)

## Summary
`memfn/tests/span_forms/cards.py` now fails loudly if any arm-I artifact (`--memfn=no-span-loop`) contains a span loop, and fails as vacuous if no non-I artifact does (reach control). No other change.

## Fix
- Loop text (window.c `wf_loop`, same head G2's `parse_loops` reads): `_j = LO; for (; <prefix>_j < END; <prefix>_j++) if (!`, matched by `LOOP_RE`. Confirmed on built artifacts: `[0-9a-f]{32}` at `--harness=span-head=0` has 1, at head 64 and under the deny 0.
- `loop_audit` (pure) and `check_deny(rundir, cl)` run over every distinct (pattern, arm, layer) artifact; wired into `dry` (failures join the red list, exit 1) and `run` (before any timing; the empty results file is removed and the run stops).
- Selftest: two new cases (a looping arm I fails; a clean arm I passes with reach kept).
- This tree has no `--window-search-width` flag: WIDTH_FLAG=none.

## Validation
- `cards.py selftest`: 39 checks, 0 failed (was 37).
- `WIDTH_FLAG=none cards.py dry --quick`: 1374 cells built and gated, 0 failures; deny check: 42 arm-I artifacts loop-free, 54 non-I artifacts with a loop (reach), 0 failures.
- Sabotage by hand (scratch driver, arm I redirected to `span-head=0`, i.e. the deny ignored): 10 failures, e.g. `DENY IGNORED: arm I emits a span loop: dig24 I off`; exit 1.
- `make strict`: clean.

## STATE AT HANDOFF
Committed on lane/memfn-forms. No rulings file existed. OWED: none
