# S407 — [K75] THE FIND-ALL LOOP'S NON-EMPTY ARM LOSES ITS ALIGNMENT (the C leg).
#
# `tests/harness/driver.c`'s `count` mode is `docs/spec/match_api.md` §3.1's
# find-all loop transcribed, and behind every `.rxt` `mc` line. K75 changed its
# non-empty arm from `end` to `<prefix>_next_pos(end - 1)`; this row plants the
# old arm back, so a match ending before a STRAY continuation byte parks the
# loop on it and K50's guard refuses the next search (the count stops short and
# the harness reports a give-up).
#
# THE DETECTOR is `tests/rxtsource/run_rxtsource_tests.sh`'s mc/ill-formed-utf8
# check, which runs `mc_illformed_utf8.rxtin` through `run.sh` (this driver) AND
# `verify_rxt.py` and demands both agree with the fixture's libpcre2-derived
# counts. It is the ONLY reader of this loop's non-empty arm on an ill-formed
# subject: every well-formed `mc` count (and the encseam/backref/assertions
# find-all drivers, which are byte-encoded) reads `next_pos(end - 1) == end`, so
# the plant is invisible to them by the same identity that makes the change safe.
# SAB_REACH_POP asserts the fixture still holds the stray-byte cells.
SAB_ID="S407-findall-nonempty-arm-unaligned-c"
SAB_FILE="tests/harness/driver.c"
SAB_SUITES="rxtsource"
SAB_DESC="the harness driver's find-all loop resumes after a NON-EMPTY match at its raw end instead of <prefix>_next_pos(end - 1), so a match ending before a stray continuation byte leaves the loop on a position K50 refuses and the count is lost (K75)"
SAB_REACH_POP="tests/rxtsource/fixtures/mc_illformed_utf8.rxtin|^mc .a.*\\\\x80|6"
SAB_COUNT=1
SAB_BEFORE='                  ? RXFN(_next_pos)(buf, len, (size_t)fa[0][1] - 1)   /* [K75] */'
SAB_AFTER='                  ? (size_t)fa[0][1]   /* SABOTAGE S407 */'
