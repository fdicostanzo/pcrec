#!/usr/bin/env bash
# S1135 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- the cover report writes caps[0] and returns without the dead-group fill (K78), so a group the pattern never sets is left unwritten
# kit_proof.md §6.3 S1135: bench `syntax/rec-define` on "12:34": group 1 left unwritten (the driver pre-fills the array, so an unwritten slot reads its sentinel, not PCREC_UNSET).
SAB_ID='S1135-cover_report_skips_fill'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='kitproof'
SAB_DESC='the cover report writes caps[0] and returns without the dead-group fill (K78), so a group the pattern never sets is left unwritten'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh); the measured figure is the matrix run of lane z2build'"'"'s heavy chain (docs/dev/lanes/z2build_report.md), owed at the slot.'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'(?(DEFINE)(?<d>\d{2}))(?&d):(?&d)'"'"''
SAB_REACH_EXPECT='REACH-COVER'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    emit_search_success(cx, c, "scan_position",
                        dfa_fragf(cx, "scan_position + %d", cv->end.k), "    ");'
SAB_AFTER='    pcrec_sb_printf(c, "    if (capture_spans) { capture_spans[0][0] = (ptrdiff_t)scan_position;"
                    " capture_spans[0][1] = (ptrdiff_t)(scan_position + %d); }\n    return 1;\n",
                    cv->end.k);   /* SABOTAGE S1135 */'
