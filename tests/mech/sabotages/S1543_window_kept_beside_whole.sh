# S1543 (lane r30b, 2026-10-29; [MEMFN] R-30, memfn/docs/requests.md): THE WINDOW NOT DROPPED. implied_by never answers, so the pre-check's run window is
# defined and asked again beside the whole run that implies it (the form before R-30;
# answer-neutral: the window is a necessary fact). tests/memfn/run_presence.sh section D
# reads the artifact: the window's `rx_reqrun(` ask is back.
SAB_ID="S1543-window-kept-beside-whole"
SAB_FILE="memfn/src/precheck.c"
SAB_SUITES="memfnfinder"
SAB_DESC="the R-30 implication never holds, so a pre-check asks its run window beside the whole run that implies it"
SAB_DOC_FIGURE="OWED: read the figure from a run: bash tests/mech/run_sabotage_matrix.sh S1543."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if ((art->levers & KIT_LEVER_PRES_WINDOW) || i == s->ret_pred || !func_run(pi))'
SAB_AFTER='    if (1 || (art->levers & KIT_LEVER_PRES_WINDOW) || i == s->ret_pred || !func_run(pi))   /* SABOTAGE S1543 */'
SAB_REACH='"$PCREC" --features all -e byte -p rx -o "$REACH_TMP/o.c" --pattern "(x?)([a-z]+)+eeeeeeee~#~#~#~#\\1" && grep -qF "rx_reqrun_whole(subject, subject_length, search_from)" "$REACH_TMP/o.c" && ! grep -qF "rx_reqrun(" "$REACH_TMP/o.c" && echo REACH-R30-WINDOW-DROPPED'
SAB_REACH_EXPECT="REACH-R30-WINDOW-DROPPED"
