# S602 — [ART-POSS-ARMS]: ARM B RECOMPUTES A GROUP ALREADY IN PROGRESS
# (src/opt/possessify.c; docs/design/poss_arms.md rev 2.1 §8.2's plant row,
# lane possbuild).
#
# The capture fact's in-progress guard (§3.1, R-4) ends a reference cycle.
# PCREC_MAX_POSS_REF_DEPTH still ends every chain without it, so a LINEAR
# cycle like `(a\2)(b\1)x+\1` stays sound and cheap; a BRANCHING cycle
# explores 2^64 paths first. Witness `(a\2\3)(b\1)(c\1)x+\1`: its compile
# times out (a termination row, not an answer row).
# Detectors (§8.1 item 5): the oracle-side .rxt cells in
# tests/possessify/possessify.rxt (harness) and the exhaustive possdiff
# (possdiff). REACH (§8.1 item 2) is SAB_REACH_POP: the witness is in the
# swept population.
SAB_ID="S602-poss-b-in-progress-recomputed"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="harness possdiff"
SAB_HARNESS_TARGET="tests/possessify/possessify.rxt"
SAB_DESC='arm B recomputes a group whose value is in progress (a reference cycle), bounded only by the depth limit'
SAB_DOC_FIGURE="PREDICTED: harness on tests/possessify/possessify.rxt fails the witness block; possdiff diverges (or, for a termination/R-5 row, refuses) on it. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S602."
# [MECH-REACH] the site answers at HEAD: the stamp on a pattern whose verdict
# runs through the planted line.
SAB_REACH='"$PCREC" --features all --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern '\''(a\2\3)(b\1)(c\1)x+\1'\'' && grep -q "^#define RX_VM_POSS_ARMS 0x4u$" "$REACH_TMP/o.c" && echo REACH-S602'
SAB_REACH_EXPECT="REACH-S602"
SAB_REACH_POP='tests/possessify/possessify.rxt|^pattern \(a\\2\\3\)\(b\\1\)\(c\\1\)x\+\\1$|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (F->state[g] == CF_BUSY) return false;'
SAB_AFTER='    /* SABOTAGE S602: an in-progress group is recomputed */'
