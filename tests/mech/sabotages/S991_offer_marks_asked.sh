# S991 — [WINDOW-E1] THE OFFER IS AN ASK (src/core/findings.c,
# `pcrec_find_offer`): building the kit's analysis object marks the query
# ASKED, so every compile stamps `byte-rate=...` whether or not a reader
# consumed it — the stamp's CONSULTED meaning (D167 add. 2) lost to OFFERED,
# an abi event E-1 must not be (window_contract.md §3.7.3).
#
# Detector: run_findings_tests.sh §4's "nothing asked" cell (`-fno-req-byte
# '^abc'` must stamp ""), §6 #22 (t_quiet) and §14 C-E1-4's offered-not-asked
# population; G1-E1's deny arms at the census.
SAB_ID="S991-offer-marks-asked"
SAB_FILE="src/core/findings.c"
SAB_SUITES="findings"
SAB_DESC='pcrec_find_offer sets byte_rate_asked: the eager offer, which every attempt makes, becomes an ask, so a compile no reader consumed stamps byte-rate=default:... where "" is the CONSULTED answer'
SAB_DOC_FIGURE='OWED: not yet run (lane e1build, 2026-10-17: the box was held by the kit'\''s R-23 heavy chain; mech owed at merge). Expected: findings red on §4 '\''nothing asked'\'' and §6 [#22].'
SAB_REACH='"$PCREC" -p rx -fno-req-byte -o "$REACH_TMP/o.c" --pattern "^abc" && grep -q "_FINDINGS \"\"" "$REACH_TMP/o.c" && echo REACH-E1-QUIET-COMPILE'
SAB_REACH_EXPECT="REACH-E1-QUIET-COMPILE"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    f.shaped = find_queries[query].q.version > 0;'
SAB_AFTER='    fr->byte_rate_asked = true;   /* SABOTAGE S991: the offer is an ask */
    f.shaped = find_queries[query].q.version > 0;'
