# S1027 — [WINDOW-E1] THE OFFER DERIVES THROUGH THE RAISING PATH
# (src/core/findings.c, `find_byte_rate_answer`): the status split folded
# back, so an underivable answering block refuses EVERY compile that offers
# it — and every attempt offers — including the ones that ask nothing,
# which compile today (window_contract.md §3.3 rule 9, §3.7.4a: B1).
#
# Detector: run_findings_tests.sh §12's cell (the `l1none` fixture under
# `-fno-req-byte '^abc'` compiles and stamps ""), §14's `l1none/utf8` cell;
# G1-E1's `l1none` cells at the census (1,905 / 3,246 / 5,367 compiles).
SAB_ID="S1027-offer-raises"
SAB_FILE="src/core/findings.c"
SAB_SUITES="findings"
SAB_DESC='find_byte_rate_answer raises the ask path'\''s refusal, so the analysis object'\''s offer refuses a compile whose answering block counts nothing even when no reader asks'
SAB_DOC_FIGURE='OWED: not yet run (lane e1build, 2026-10-17: the box was held by the kit'\''s R-23 heavy chain; mech owed at merge). Expected: findings red on §12 (the quiet l1none compile refuses) and §14 (l1none/utf8).'
SAB_REACH='mkdir -p "$REACH_TMP/L1" && printf "%s\n" "analysis l1none" "    cpfreq" "        question q" "        reader r" "        analyzer authored" "        encoding utf8" "        serves byte-rate when utf8 via encode-latin1" "        row U+20AC 7" "        provenance" "            source authored" "            retrieved 2026-09-28" > "$REACH_TMP/L1/l1none.rxt" && "$PCREC" -p rx -e utf8 -I "$REACH_TMP/L1" --analysis l1none -fno-req-byte -o "$REACH_TMP/o.c" --pattern "^abc" && grep -q "_FINDINGS \"\"" "$REACH_TMP/o.c" && echo REACH-E1-UNDERIVABLE-QUIET'
SAB_REACH_EXPECT="REACH-E1-UNDERIVABLE-QUIET"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    PcrecFindStatus st = find_derive_byte_rate_status(cx, fr);
    *payload = fr->byte_rate_have ? fr->byte_rate : NULL;'
SAB_AFTER='    PcrecFindStatus st = find_derive_byte_rate_status(cx, fr);
    find_raise_byte_rate(cx, fr, st);   /* SABOTAGE S1027: the offer raises */
    *payload = fr->byte_rate_have ? fr->byte_rate : NULL;'
