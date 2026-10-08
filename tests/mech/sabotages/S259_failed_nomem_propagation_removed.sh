# S259 — [D110/ALLOC-PINS] D109's `cx.failed_nomem` PROPAGATION IS NEUTERED,
# SO THE LADDER CLASS OF K60 RETURNS
# (tests/core/alloc_check.c, tests/resource/run_resource_tests.sh Section 2b).
#
# `compile_driver`'s `setjmp` handler (`src/core/compile.c`) tests
# `cx.failed_nomem` FIRST, ahead of every rung's own eligibility test and
# the `[ART-SIZE]` ladder's blanket "this K is out" catch, so a genuine
# `pcrec_ctx_nomem`-routed allocation failure propagates immediately instead of
# being absorbed into a later internal attempt's success (D109). This
# sabotage neuters the test — `if (0 && cx.failed_nomem)` never fires — so
# the ladder's own catch-all runs unconditionally again and a forced
# allocation failure on a non-final `compile_driver` attempt can be
# silently absorbed, exactly K60's LADDER class (mechanism (B), 108/148
# measured absorptions before D109 fixed it).
SAB_ID="S259-failed-nomem-propagation-removed"
SAB_FILE="src/core/compile.c"
SAB_SUITES="resource"
SAB_DESC="compile_driver's recovery point never tests cx.failed_nomem (the arrival's label set drops NOMEM, so the walk never asks the nomem row), so a genuine pcrec_ctx_nomem-routed allocation failure falls through to the [ART-SIZE] ladder's blanket catch and can be silently absorbed into a later attempt's success -- K60's ladder class, D109's own fix undone"
SAB_DOC_FIGURE="tests/core/alloc_check.c's W4 witness (the size-term ladder) is D109's own repro: make alloc reads W4 absorbed 0 -> 108 under this plant (single-shot and sustained both). tests/resource/run_resource_tests.sh Section 2b (D110) is the make-test-reachable detector: it now asserts alloc_check's own rc and the absence of any SUCCEEDED THROUGH line, not only the signal grep. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S259."
SAB_COUNT=1
# RE-ANCHORED 2026-09-29 (lane k67, [OPT-RETRY-REUSE]): the propagation's
# exit gained the machine memo's free; the plant is unchanged.
# RE-AIMED 2026-10-08 (lane decfbB3, [DEC-FALLBACK] B3): the five tests are one
# walk over `fit_rungs[]`, and the propagation is row 1 (`nomem`, asked on the
# NOMEM label). Deleting row 1 is an EQUIVALENT mutant: row 2's `on` mask
# leaves NOMEM out, so a nomem arrival falls to `refuse`, whose action is
# PROPAGATE's (cleanup, return -1). D109's guard now lives in the LABEL: the
# plant drops `failed_nomem` from the arrival's label set, so the arrival reads
# `other`, row 1 is never asked, and on a ladder attempt row 2's trial catch
# absorbs it -- "never tests cx.failed_nomem", the K60 ladder class, as before.
# Re-verified with make alloc: W4 absorbs under the plant, 0 on the tree.
SAB_BEFORE='                       (cx->failed_nomem ? FIT_L_NOMEM : 0u) |'
SAB_AFTER='                       (0 && cx->failed_nomem ? FIT_L_NOMEM : 0u) |   /* SABOTAGE S259: the propagation never fires */'
