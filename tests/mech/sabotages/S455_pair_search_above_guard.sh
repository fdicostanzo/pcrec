#!/usr/bin/env bash
# S455 ([OPT-LITSCAN] S4 C3, lane c3build) -- THE PAIR ARM SEARCHES BOTH
# STREAMS ONCE ABOVE ITS LOOP GUARD.
#
# r1's own wording ("searched once before the loop"), which r2's R2-S1
# refuted: the K27 guard is the loop's condition, so a search above it has
# none. `(?i)select` (k* = 4) on a subject shorter than 5 calls
# `memchr(subject + pos + 4, c, n - pos - 4)` with a wrapped length, and on
# (NULL, 0) memchr(NULL + 4, ...). Answers often survive (the loop then
# exits); the detectors are structural and sanitizer: reqcube_check.py's
# "no memchr above the while" check, and under make ubsan/asan the [K27]
# pair-arm NULL driver and reqcube.rxt's short-subject block. (Design's
# provisional S454.)
SAB_ID="S455-pair-search-above-guard"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="codegen"
SAB_DESC="the pair arm's two searches are hoisted above the block's 'while (pos + maxk < n)' guard, so a subject shorter than the run makes memchr read with a wrapped length and a NULL subject reaches memchr"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/c3build_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S455."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(?i)select" && grep -q "^#define RX_REQ_RUN \"53454c454354@4/dfdfdfdfdfdf\"" "$REACH_TMP/o.c" && grep -q "ha < pos + 4" "$REACH_TMP/o.c" && echo REACH-PAIR-ARM'
SAB_REACH_EXPECT="REACH-PAIR-ARM"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_sb_puts(c, "    size_t ha = 0, hb = 0;\n"
                     "    int fresh = 1;\n");'
SAB_AFTER='    pcrec_sb_printf(c, "    size_t ha, hb;\n    int fresh = 0;\n"   /* SABOTAGE S455 */
                     "    { const void *q = memchr(subject + %s, %d, %s); ha = q ? (size_t)((const unsigned char *)q - subject) : n; }\n"
                     "    { const void *q = memchr(subject + %s, %d, %s); hb = q ? (size_t)((const unsigned char *)q - subject) : n; }\n",
                     at, a, len, at, b, len);'
