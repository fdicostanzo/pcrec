#!/usr/bin/env bash
# S458 ([K82], lane k82fix) -- A TIE LEADS.
#
# The row's PICK lists the run's scan cube FIRST so a tie keeps the run alone:
# under NONE an exact scan member and the set pick are both one byte, and a
# second pass over an equally rare byte buys nothing (G1's own `<=` argument).
# This plant names the set pick the reader's `rightmost`, so ties go to it and
# every NONE artifact with an exact scan member and a non-empty set grows a
# lead. Detector: run_prechecks.sh §5.11's `é@` (-e utf8) row, lead "-".
SAB_ID="S458-set-leads-tie-leads"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks"
SAB_DESC="the set-leads row's PICK sends a tie to the set pick, so an equally rare byte (every exact scan member under NONE) is memchr'd in front of the run for nothing"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/k82fix_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S458."
SAB_REACH='"$PCREC" --features all -p rx -e utf8 -o "$REACH_TMP/o.c" --pattern "é@" && grep -q "^#define RX_REQ_RUN \"c3a940@2\"" "$REACH_TMP/o.c" && ! grep -q "!memchr(subject + search_from, 64," "$REACH_TMP/o.c" && echo REACH-TIE-NO-LEAD'
SAB_REACH_EXPECT="REACH-TIE-NO-LEAD"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return pcrec_find_pick(pcrec_find_byte_rate(s->cx), cand, care, 2, 0) == 1;'
SAB_AFTER='    return pcrec_find_pick(pcrec_find_byte_rate(s->cx), cand, care, 2, 1) == 1;   /* SABOTAGE S458 */'
