# S995 — [WINDOW-E1] BYTE-RATE'S `unmeasured` CELL FLIPPED TO ABSENT
# (src/core/findings.c, `find_queries[]`): the frequency kind no longer
# ARRIVES when nothing measured answers it, against D162 add. 2 (the
# frequency kind always arrives) and add. 3's refinement (a fact a pcrec
# reader uses is sent ALWAYS).
#
# Detector: run_findings_tests.sh §14 C-E1-1's `-e utf8` cells (expected
# PRESENT/PRIOR_NONE, got ABSENT) and C-E1-5 (the ARRIVES rows against the
# readers found by grep).
SAB_ID="S995-byte-rate-unmeasured-absent"
SAB_FILE="src/core/findings.c"
SAB_SUITES="findings"
SAB_DESC='find_queries[]'\''s byte-rate row says ABSENT in its unmeasured column, so an authored or absent byte-rate is listed ABSENT to the kit'
SAB_DOC_FIGURE='OWED: not yet run (lane e1build, 2026-10-17: the box was held by the kit'\''s R-23 heavy chain; mech owed at merge). Expected: findings red on §14 C-E1-1 (none/utf8, none/byte, copy/*, ...) and C-E1-5.'
SAB_REACH='"$PCREC" -p rx -e utf8 -o "$REACH_TMP/o.c" --pattern abc && grep -q "_FINDINGS \"byte-rate=none\"" "$REACH_TMP/o.c" && echo REACH-E1-PRIOR-NONE'
SAB_REACH_EXPECT="REACH-E1-PRIOR-NONE"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    [PCREC_FQ_BYTE_RATE]  = { { "byte-rate",  1, PCREC_FIND_UNMEASURED_ARRIVES },'
SAB_AFTER='    [PCREC_FQ_BYTE_RATE]  = { { "byte-rate",  1, PCREC_FIND_UNMEASURED_ABSENT },   /* SABOTAGE S995 */'
