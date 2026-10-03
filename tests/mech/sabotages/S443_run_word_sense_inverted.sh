# S443 ([OPT-LITSCAN] S4 C1, lane s4build) -- THE OVERLAP ROW'S SENSE IS
# INVERTED.
#
# S267's twin for the run compare's `overlap` row: each word compare is
# emitted `!=` where it must be `==`, so a run at an overlap length (3, 5-7,
# 9-15) is "present" exactly where no word matches. Every matching subject of
# such a run reads nomatch on both engines (the VM's literal run, the
# offset-skip run term, the run pre-check). Detector: the harness, on the
# L-sweep (tests/litscan/litrun.rxt) and every corpus run at those lengths.
SAB_ID="S443-run-word-sense-inverted"
SAB_FILE="src/gen/runcmp.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/litrun.rxt"
SAB_DESC="the run compare's overlap row emits each word compare with != instead of ==, so a run at length 3, 5-7 or 9-15 is accepted exactly where it is absent"
SAB_DOC_FIGURE="Read the current figure from a run."
SAB_REACH='"$PCREC" --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern "xyz(a|ab)c" && grep -qF "rx_w2(subject + scan_position + 1) == rx_w2(\"yz\")" "$REACH_TMP/o.c" && echo REACH-OVERLAP-ROW-EMITTED'
SAB_REACH_EXPECT="REACH-OVERLAP-ROW-EMITTED"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_printf(c, ") == %s_w%d(\"", p, w);'
SAB_AFTER='        pcrec_sb_printf(c, ") != %s_w%d(\"", p, w);   /* SABOTAGE S443 */'
