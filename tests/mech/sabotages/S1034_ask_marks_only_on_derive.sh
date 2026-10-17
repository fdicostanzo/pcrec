# S1034 — [WINDOW-E1] THE ASK MARKS ONLY WHEN IT DERIVES
# (src/core/findings.c, `pcrec_find_byte_rate`): the accessor tests whether
# the memo is filled where it should test whether the query was asked, so
# after the eager offer (which fills the memo on every attempt) no ask
# marks: every artifact stamps "" while its bytes still depend on the
# byte-rate (window_contract.md rev 3.1 X1).
#
# Detector: run_findings_tests.sh §15 C-PERT at the default arms (every
# consulted artifact's stamp drops to "" while its bytes move with the
# data), §4's stamp cells, and §12's refusal cell (the raise never runs).
SAB_ID="S1034-ask-marks-only-on-derive"
SAB_FILE="src/core/findings.c"
SAB_SUITES="findings"
SAB_DESC='pcrec_find_byte_rate guards its ask on the memo'\''s status instead of byte_rate_asked, so once the offer has derived no reader'\''s ask is recorded'
SAB_DOC_FIGURE='OWED: not yet run (lane e1build, 2026-10-17: the box was held by the kit'\''s R-23 heavy chain; mech owed at merge). Expected: findings red on §4 (every stamp ""), §12 (the all-dropped block compiles) and §15 C-PERT (FAIL moved at default/byte and default/utf8).'
SAB_REACH='"$PCREC" -p rx -o "$REACH_TMP/o.c" --pattern abc && grep -q "_FINDINGS \"byte-rate=default:" "$REACH_TMP/o.c" && echo REACH-E1-ASKING-COMPILE'
SAB_REACH_EXPECT="REACH-E1-ASKING-COMPILE"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (!fr->byte_rate_asked) {
        fr->byte_rate_asked = true;'
SAB_AFTER='    if (fr->byte_rate_status == PCREC_FIND_ST_UNDERIVED) {   /* SABOTAGE S1034 */
        fr->byte_rate_asked = true;'
