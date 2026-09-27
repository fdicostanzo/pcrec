# S301 — [FINDINGS] B1 A READER SPELLS ITS OWN NONE ANSWER (src/core/findings.c,
# `pcrec_find_set_pick`): the set pick tests the rate pointer itself and
# returns its threaded rightmost member when there is none, instead of
# handing the NULL to the PICK primitive — the per-reader NONE rule D126 Q4
# forbids, the shape [OPT-REQRUN-ENC] grew in (R13: two readers of one
# question, two spellings of its NONE answer, rightmost against leftmost).
#
# THE PLANT IS BEHAVIOURALLY NEUTRAL ON PURPOSE. Its branch returns exactly
# what the primitive's own NONE answer returns for this reader's candidate
# order (index 0 = the rightmost), so no stamp, no emitted byte and no answer
# moves — which is precisely why such a branch is dangerous: it is invisible
# to every answer and identity check until the day the two spellings drift.
# The only detector is the STRUCTURAL rule (tests/findings/structural_check.py
# S1, via run_findings_tests.sh §5), and `corpus:0fail` beside a red
# `findings` arm is this row working.
SAB_ID="S301-findings-reader-local-none"
SAB_FILE="src/core/findings.c"
SAB_SUITES="findings"
SAB_DESC="pcrec_find_set_pick tests the rate pointer and returns its rightmost member itself when the byte-rate is NONE, instead of passing NULL to the PICK primitive whose NONE answer that is — a reader-local NONE rule (D126 Q4) that moves no byte today and is caught only by the findings structural check"
SAB_DOC_FIGURE="findings:1fail/16pass expected — §5 S1 reports pcrec_find_set_pick() testing '!rate'; every other findings check stays green. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S301."
# [MECH-REACH] the site answers: under -e utf8 (the default's NONE) the set
# pick is reached (a run-free two-member set) and returns the rightmost 'e'.
SAB_REACH='"$PCREC" --features all -p rx -e utf8 -o "$REACH_TMP/o.c" --pattern "[0-9]+x[0-9]+e[0-9]+" && grep -q "^#define RX_REQ_BYTE \"101\"" "$REACH_TMP/o.c" && grep -q "^#define RX_FINDINGS \"byte-rate=none\"" "$REACH_TMP/o.c" && echo REACH-FINDINGS-SET-PICK-NONE'
SAB_REACH_EXPECT="REACH-FINDINGS-SET-PICK-NONE"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (rightmost < 0) return -1;
    cand[n++] = (unsigned char)rightmost;'
SAB_AFTER='    if (rightmost < 0) return -1;
    if (!rate) return rightmost;   /* SABOTAGE S301: a reader-local NONE rule */
    cand[n++] = (unsigned char)rightmost;'
