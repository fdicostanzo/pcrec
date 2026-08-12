# S23 — xskip's `#`-comment terminator widens from 0x0A ONLY to any byte in
# the skip set (09,0A,0B,0C,0D,20,85), contradicting the measured NEWLINE
# CONVENTION rule ([MOD-0.5d]: "a `#`-comment runs to the next 0x0A ONLY —
# 0x0D and even the skipped 0x85 do NOT terminate it; the terminator is the
# NEWLINE convention (NEWLINE_LF, DD-11), not the skip set"). MOD-0.5e.
SAB_ID="S23-xskip-comment-any-skip-byte"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/modifiers/xmode.rxt"
SAB_DESC="xskip: '#'-comment scan stops at any xskip_byte(), not just 0x0a"
SAB_DOC_FIGURE="measured MOD-0.5e: 1 harness case (tests/modifiers/xmode.rxt, the trailing-comment block -- the embedded SPACE in 'trailing comment' is itself a skip-set byte, so this does not need an embedded-newline byte the .rxt format cannot express)"
SAB_COUNT=1
SAB_BEFORE="        if (c == '#') {
            cx->pos++;
            while ((c = peekc(cx)) >= 0 && c != 0x0a) cx->pos++;
            continue;
        }"
SAB_AFTER="        if (c == '#') {
            cx->pos++;
            while ((c = peekc(cx)) >= 0 && !xskip_byte(c)) cx->pos++;
            continue;
        }"
