# S1720 ([INLINE-C] stage 2, review 2026-10-27-r1-ic2 F3) -- THE SEGMENT
# BLOCK KEEPS THE WHOLE `<PREFIX>_` NAMESPACE again, the shape the review
# found: the matcher's own helpers (`<PREFIX>_CUT`, `_CHARGE_WORK`, `_R_*`,
# `_SLOT_*`, `_NSLOTS`) stay live where a user's code is compiled. Witness:
# tests/code/run_code_tests.sh arm 7, whose public set is read from the .h
# and from match_api.md §6.3.2's inventory, not from the emitter's rule.
SAB_ID="S1720-code-keep-by-prefix"
SAB_FILE="src/gen/emit_code.c"
SAB_SUITES="code"
SAB_DESC="the code segment block keeps every <PREFIX>_ macro live instead of exactly the catalogued contract stamps, so the matcher's internal helpers reach the user's code"
SAB_REACH='"$PCREC" --allow-code=c -o "$REACH_TMP/o.c" --pattern '\''a(?C`c: return RX_PASS;`)b'\'' && grep -c "^#undef RX_CUT" "$REACH_TMP/o.c"'
SAB_REACH_EXPECT='1'
SAB_COUNT=1
SAB_BEFORE='    { "\x01Q_",           KEEP_STAMP  },   /* <PREFIX>_<a catalogued stamp> */'
SAB_AFTER='    { "\x01Q_",           KEEP_PREFIX },   /* SABOTAGE S1720 */'
