#!/usr/bin/env bash
# S1149 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- the span slice passes every zero-width node through (kit_proof.md §5.2's revision-2.1 sentence as written): an in-span A_CTX neither narrows S_d nor ends exact_len
# kit_proof.md §6.3 S1149: `a(?=b)[a-z]`'s S_1 states [a-z] where libpcre2's set is {b} (C8 producers-disagree, so `cover` declines); `\w(?=\d)\w`, `[a-z0-9_ ]\b[a-z ]` state too much.
SAB_ID='S1149-slice_ctx_passthrough'
SAB_FILE='src/facts/kset.c'
SAB_SUITES='kitproof'
SAB_DESC='the span slice passes every zero-width node through (kit_proof.md §5.2'"'"'s revision-2.1 sentence as written): an in-span A_CTX neither narrows S_d nor ends exact_len'
SAB_DOC_FIGURE='@FIG@'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'a(?=b)[a-z]'"'"''
SAB_REACH_EXPECT='REACH-COVER'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                nr[k] = r[k] & (uint8_t)((in ? st->cls[k] : 0) | (out ? ~st->cls[k] : 0));'
SAB_AFTER='                nr[k] = r[k]; (void)in; (void)out;   /* SABOTAGE S1149 */'
