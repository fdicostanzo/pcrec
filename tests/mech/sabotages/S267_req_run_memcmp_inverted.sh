# S267 — [OPT-REQPOS] tier 2b THE RUN PRE-CHECK'S MEMCMP SENSE IS INVERTED
# (src/gen/emit_dfa.c, `emit_exact_compare`, P4): the emitted test reads
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
SAB_REACH='"$PCREC" --features all -p rx -fno-offset-skip -o "$REACH_TMP/o.c" --pattern "a=b" && grep -q "^#define RX_REQ_RUN \"613d62@1\"" "$REACH_TMP/o.c" && grep -qF "rx_reqrun(subject, subject_length, search_from)" "$REACH_TMP/o.c" && grep -qF "if (!memcmp(subject + cand, \"a=b\", 3)) return cand;" "$REACH_TMP/o.c" && echo REACH-REQ-RUN-COMPARE-EMITTED'
SAB_REACH_EXPECT="REACH-REQ-RUN-COMPARE-EMITTED"
# [OPT-LITSCAN] S1 step 6 (lane s1step6, 2026-09-26): the run pre-check is now
# a call of a file-scope `rx_reqrun` block written by the offset-skip block's
# emitter, whose compare is this same P4 at `cand`, so the probe greps the
# block's compare and its call. `-fno-offset-skip` because since S1's run
# rows `a=b`'s default artifact elides the pre-check as dominated (tuning.md
# §2.29) — the probe's old default-flag grep had stopped reaching the site at
# S1 step 5 and nothing had noticed. The plant is unchanged; the loop's
# `subject_length <= search_from` arm and two-conjunct guard it once left
# intact are now the block's `pos + L-1 < n` / `cand + L-1 >= n` guards, which
# it leaves intact the same way.
# [OPT-LITSCAN] S1 re-anchor (lane s1build, 2026-09-25): the compare is now
# P4, `emit_exact_compare`, the ONE emitter of a constant-length literal
# compare, and both of the loop's formats call it. The plant moves there with
# its intent unchanged — the SENSE of the run compare is inverted — and the
# two-format rationale above now holds by construction (one site, both
# shapes), so SAB_COUNT drops from 2 to 1. Since S1's run rows the same
# primitive also writes the `<p>_ofsskip` run term, which this plant inverts
# too; that widens what the row deletes and does not change what it isolates.
SAB_COUNT=1
SAB_BEFORE='    pcrec_sb_printf(c, "!memcmp(%s, \"", base);'
SAB_AFTER='    pcrec_sb_printf(c, "memcmp(%s, \"", base);   /* SABOTAGE S267 */'
