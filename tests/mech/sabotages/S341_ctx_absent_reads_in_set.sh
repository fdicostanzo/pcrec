# S341 ([UCP] U2; RE-AIMED by [DD-11.5] P2c, lane ctxbuild, 2026-10-19) -- THE
# ABSENT INDEX IS NOT GATED ON THE ROW.
#
# THE CLAIM (docs/design/ctx_span.md §4.2.3, re-check R1): the closure's N_CTX
# arm takes "absent" (index 2) for a side ONLY where the node's row of
# src/core/ctxfn.def reads absent on that side. A four-cell row (`\b`, a
# one-character lookaround) reads none, so it computes the neighbour's
# membership bit under every atom of the `pos == n` view, exactly as before
# the 9-cell table existed.
#
# THE SABOTAGE drops the gate on the NEXT side: every row reads "absent" when
# `right_abs` holds, i.e. at the end view under every atom. A copied row then
# reads `out` there, so the end view's closure stops equalling the eol view's
# and an `endvar` interns where none did: `(?:\w*?)*\b` under -e utf8 (the
# K50 gate makes the view live) gains a `_forward_end_view` table. Answers do
# not move (the end view is read only at `pos == n`); the bytes do.
# Detector: tests/assertions/run_assertions_tests.sh §1c (the R1 cell, with
# its absent-reading control `(?:\w*?)*(?m)$`). Measured by lane ctxbuild by
# hand with BOTH sides ungated: 88 of 2,451 corpus assertion patterns move
# under -e utf8, 0 at byte (the light probe in ctxbuild_report.md).
#
# RE-AIMED from [UCP] U2's plant (s0 closed under the last atom), which moved
# to S1151 unchanged: ctx_span.md §4.5.4 re-aims this id to R1's plant.
SAB_ID="S341-ctx-absent-reads-in-set"
SAB_FILE="src/ir/dfa.c"
SAB_SUITES="assertions"
SAB_DESC="the closure's N_CTX arm reads the next side as absent wherever right_abs holds, whatever the row, so a four-cell row (\\b) reads out at the end view and an endvar interns"
SAB_DOC_FIGURE="HAND-MEASURED by lane ctxbuild 2026-10-19 (plant applied, tree rebuilt, the R1 cell run from the section by hand): 'FAIL: R1: witness (?:\\w*?)*\\b emits 1 forward end view(s)'. The matrix figure is owed at the post-window slot: bash tests/mech/run_sabotage_matrix.sh S341."
SAB_REACH='"$PCREC" --features all -e utf8 -p rx -o "$REACH_TMP/o0.c" --pattern "(?:\\w*?)*\\b" >/dev/null 2>&1 && grep -c "define RX_ENGINE \"dfa\"" "$REACH_TMP/o0.c"'
SAB_REACH_EXPECT="1"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                unsigned q = (cl->right_abs && ctxfn_reads_absent_next(st->ctxfn))'
SAB_AFTER='                unsigned q = (cl->right_abs /* SABOTAGE S341 */)'
