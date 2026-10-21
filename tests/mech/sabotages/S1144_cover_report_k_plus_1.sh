#!/usr/bin/env bash
# S1144 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- emit_cover reports [c, c + k + 1)
# kit_proof.md §6.3 S1144: `foobar` on "foobarx": PCRE2 (0,6), the plant (0,7).
SAB_ID='S1144-cover_report_k_plus_1'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='kitproof'
SAB_DESC='emit_cover reports [c, c + k + 1)'
SAB_DOC_FIGURE='@FIG@'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'foobar'"'"''
SAB_REACH_EXPECT='REACH-COVER'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                        dfa_fragf(cx, "scan_position + %d", cv->end.k), "    ");'
SAB_AFTER='                        dfa_fragf(cx, "scan_position + %d", cv->end.k + 1), "    ");   /* SABOTAGE S1144 */'
