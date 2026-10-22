# S1421 (D172 S2 commit 6, lane wsc7) -- THE KIT RENDERER'S `hit - member`
# SUBTRACTION DROPPED (memfn/src/ofsskip.c `memchr_body`): the stream scans
# for the run's scan member at its offset `k` (the window family's reply
# member, the run window's statement's), but the candidate it returns is the
# hit itself instead of `hit - k`, so the block takes each hit of the member
# as the run's START and compares the run there. On every run whose member is
# not its first byte the compare never lines up, the block returns `n`, and
# the search entry answers NOMATCH on a subject that contains the run.
#
# SUCCESSOR of S293 (retired at wsc7): S293 planted `OfsTest.scan_k` in
# `ofs_test_run`, whose reader `ofs_pred_of` was deleted by D172 S2 commit 6;
# the run pre-check's candidate offset now comes from the reply's member
# through the part's `plan_pos`, and the arithmetic that turns a hit into a
# candidate is the kit's. Same witness, same intent: the run's scan member
# offset not subtracted.
#
# ANSWER-DETECTABLE: tests/base/k66_precheck_whole_run.rxt under `-e byte`
# scans its whole run on `~` at offset 8, so its `m` cell loses its match.
SAB_ID="S1421-reqrun-member-offset-dropped"
SAB_FILE="memfn/src/ofsskip.c"
SAB_SUITES="prechecks harness"
SAB_HARNESS_TARGET="tests/base/k66_precheck_whole_run.rxt"
SAB_DESC="the kit's memchr stream returns the hit as the candidate instead of hit - k, so each rx_reqrun block takes a hit of the run's scan member as the run's start and never finds a run whose member is not its first byte: a false NOMATCH on every matching subject of such a pattern"
SAB_DOC_FIGURE="Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1421."
# [MECH-REACH] the probe: `a=b` (member `=` at 1) under -fno-offset-skip
# emits its rx_reqrun block with the `- 1` candidate arithmetic.
SAB_REACH='"$PCREC" --features all -p rx -fno-offset-skip -o "$REACH_TMP/o.c" --pattern "a=b" && grep -qF "cand = (size_t)((const unsigned char *)q - subject) - 1;" "$REACH_TMP/o.c" && grep -qF "rx_reqrun(subject, subject_length, search_from)" "$REACH_TMP/o.c" && echo REACH-REQRUN-MEMBER-SUBTRACTED'
SAB_REACH_EXPECT="REACH-REQRUN-MEMBER-SUBTRACTED"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        kit_out(o, "        cand = (size_t)((const unsigned char *)q - subject) - %d;\n", k);'
SAB_AFTER='        kit_out(o, "        cand = (size_t)((const unsigned char *)q - subject) - %d;\n", 0 * k);   /* SABOTAGE S1421 */'
