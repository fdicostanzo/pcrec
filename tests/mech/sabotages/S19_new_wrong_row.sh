# S19 — add a brand-new registry row for a FABRICATED construct (\j, which
# PCRE2 does not define) naming a plausible-looking module, with no
# hand-written reject-table entry for it anywhere (tests/reject/CLAUDE.md's
# SR-4 table, row 4 — "a NEW row with a plausible wrong module and no
# hand-written entry"). Documented result: 0 hand-written fail, 0 iterated
# fail. This is the row SR-4's own text calls "the honest limit": iteration
# reads the same table the parser renders from, so a WRONG-BUT-INTERNALLY-
# CONSISTENT row is invisible to everything in this repository except PC-3.
#
# THE BLIND SPOT IS CLOSED, 2026-08-12 (MOD-0.8c slice 1). This row's header
# said the matrix "should report this one UNDETECTED" and that PC-3 was "out
# of scope for this matrix". Both sentences are retired, and they were wrong
# in two different ways:
#
#   1. It had ALREADY stopped being undetected. Measured at 11352be BEFORE
#      this change, with `reject` as its only arm: reject 1fail/486pass. The
#      reject suite's exact iterated-row count (100 != 101) trips — which
#      tests/reject/CLAUDE.md records, and which R8/C4-10 flags as the weakest
#      kind of catch, since its own failure message invites bumping the number.
#      A "documented expected UNDETECTED" that had quietly become DETECTED is
#      the staleness this whole directory exists to prevent, sitting in the
#      directory that exists to prevent it.
#
#   2. PC-3 is in scope now that there is a `pc3` arm. MEASURED: pc3
#      1fail/154pass — libpcre2 has no `\j`, so the fabricated RS_MODULE row
#      fails check_rows' "a row naming a construct PCRE2 does not have"
#      clause. That is a real external answer, not a count moving, and it is
#      the payoff R18/R19 asked for when they recorded this blind spot.
#
# Full measured row: reject 1fail/486pass, registry 1fail/169pass
# (+compliance-FAIL, the SR-4 drift detector), pc3 1fail/154pass.
SAB_ID="S19-new-wrong-row"
SAB_FILE="src/parse/registry.c"
SAB_SUITES="reject registry pc3"
SAB_DESC="add ESC('j', \"\\\\j\", misc, ...) for a construct PCRE2 does not define; no hand-written pin exists"
SAB_DOC_FIGURE="tests/reject/CLAUDE.md: 0/0 -- was 'expected UNDETECTED'; RETIRED 2026-08-12, see header (reject 1, registry 1, pc3 1)"
SAB_COUNT=1
SAB_BEFORE="ESC('o', \"\\\\o{101}\", misc, ANY_ENGINE, \"character with the given octal code\", QF_YES, \"char 0x41\"),"
SAB_AFTER="ESC('o', \"\\\\o{101}\", misc, ANY_ENGINE, \"character with the given octal code\", QF_YES, \"char 0x41\"),
ESC('j', \"\\\\j\", misc, ANY_ENGINE, \"fabricated: PCRE2 does not define this escape (MECH-1 sabotage for the SR-4 blind spot)\", QF_NO, \"err 103\"),"
