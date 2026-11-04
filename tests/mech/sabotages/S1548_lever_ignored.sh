# S1548 (lane r30b, 2026-10-29; [MEMFN] R-30, memfn/docs/requests.md): THE TEST-ONLY LEVER IGNORED. mf_lever accepts `pres-window` and sets nothing, so the
# answer-identity sweep's internal arm silently compiles the new form and compares it
# with itself. Section D's lever arm finds no `rx_reqrun(` ask under the lever.
SAB_ID="S1548-lever-ignored"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC="mf_lever accepts the pres-window lever and sets nothing, so the old form it promises is never produced"
SAB_DOC_FIGURE="OWED: read the figure from a run: bash tests/mech/run_sabotage_matrix.sh S1548."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            art->levers |= kit_levers[i].bit;'
SAB_AFTER='            (void)kit_levers[i].bit;   /* SABOTAGE S1548 */'
SAB_REACH='"$(dirname "$PCREC")/pcrec-harness" --harness=pres-window --features all -e byte -p rx -o "$REACH_TMP/o.c" --pattern "(x?)([a-z]+)+eeeeeeee~#~#~#~#\\1" && grep -qF "rx_reqrun(subject, subject_length, search_from)" "$REACH_TMP/o.c" && echo REACH-R30-LEVER-OLD-FORM'
SAB_REACH_EXPECT="REACH-R30-LEVER-OLD-FORM"
