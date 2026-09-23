# S267 — [OPT-REQPOS] tier 2b THE RUN PRE-CHECK'S MEMCMP SENSE IS INVERTED
# (src/gen/emit_dfa.c, `emit_req_run_check`): the emitted test reads
# `memcmp(...)` where it should read `!memcmp(...)`, so the scan loop breaks out
# exactly where the necessary run is NOT present and keeps scanning exactly
# where it IS.
#
# S265's PLANT ONE GRAIN OVER, AND ANSWER-DETECTABLE FOR THE SAME REASON. The
# run check's sound direction removes only work the artifact would have done and
# thrown away; a flipped compare removes work that would have SUCCEEDED, so
# every corpus pattern carrying a run stops matching every subject that contains
# one. `corpus` is therefore the primary detector here, unlike its two
# structural siblings S263 and S266.
#
# BOTH EMITTED SHAPES ARE PLANTED AT ONCE, and that is deliberate rather than
# convenient: the window guard has a one-conjunct form at scan index 0 and a
# two-conjunct form above it, written as two `printf` formats, and the compare's
# sense is the same claim in both. A plant that reached only one of them would
# leave half the population correct and would read as a smaller failure rather
# than as a wrong mechanism — so `SAB_COUNT` is 2 and the anchor is the fragment
# the two formats share.
#
# WHAT IT ALSO CERTIFIES, and the reason the plant is a one-character edit
# rather than a deletion: the `subject_length <= search_from` arm above the loop
# and the window guard's own conjuncts are LEFT INTACT. A plant that removed
# the whole run check would be invisible (the sound direction, which is S265's
# recorded lesson); a plant that removed only the empty-window arm would be a
# NULL dereference rather than a wrong answer; a plant that moved the compare's
# OFFSET would be a different row. This one isolates the SENSE, which is the
# half tests/codegen/run_prechecks.sh §4.1b asserts separately from the run's
# own bytes and from the offset.
SAB_ID="S267-req-run-memcmp-inverted"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness prechecks"
SAB_DESC="the necessary-RUN whole-window pre-check emits 'memcmp(...)' where it should emit '!memcmp(...)', so both engines' search entries accept a scan hit exactly when the run every match must contain is ABSENT there and keep scanning when it is present — an inversion that turns every matching subject of every run-bearing pattern into a no-match, and unlike its two batch-2 siblings it has an ordinary answer-level detector for exactly that reason"
SAB_DOC_FIGURE="tests/harness/run.sh over the full .rxt corpus is the primary detector: every 'm' case of every pattern carrying a necessary run reports nomatch, so 'cases failed' moves from 0 to a large count (the run population is 406 of 2,814 corpus patterns that compile at default axes, measured 2026-09-22 by the lane's own base-vs-tip mover census). tests/codegen/run_prechecks.sh §4.1b is the structural detector and names the sense directly ('the compare's sense is not !memcmp(...) — it may be inverted') on each of the seven §4.1 witnesses. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S267."
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree `a=b`
# stamps a three-byte run and emits the negated memcmp this row inverts.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "a=b" && grep -q "^#define RX_REQ_RUN \"613d62@1\"" "$REACH_TMP/o.c" && grep -qF "&& !memcmp(subject + rp_c - 1, \"a=b\", 3)) break;" "$REACH_TMP/o.c" && echo REACH-REQ-RUN-COMPARE-EMITTED'
SAB_REACH_EXPECT="REACH-REQ-RUN-COMPARE-EMITTED"
SAB_COUNT=2
SAB_BEFORE='&& !memcmp(%s + rp_c'
SAB_AFTER='&& memcmp(%s + rp_c'
