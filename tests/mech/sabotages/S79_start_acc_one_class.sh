# S79 — [M6.2 wave C] `start_acc` NARROWED BACK TO ONE CLASS'S BIT (§3.6.1
# row 1, and row 2 with it).
#
# The memchr prefilter is the one scan-avoidance mechanism that CANNOT be
# intersected: it seeks a byte VALUE, not a bitmap it could mask. Its guard is
# instead the flag that disables it outright when the start state can accept —
# and under a class-indexed accept that flag has to mean "accepts on ANY
# class", the OR over the state's accept row. If it reads one class's bit, a
# pattern whose start state accepts on SOME classes keeps its prefilter and
# the memchr jumps straight past accepting positions.
#
# The bitmap prefilter (§3.6.1 row 2) rides the SAME flag, so this one row
# guards both — which is why the corpus carries a memchr-shaped cell AND a
# bitmap-shaped one, rather than assuming a single-byte first set is
# representative.
#
# THE MEASURED CELL is §3.6.1's own, through the find-all loop:
#
#     \bx*   'a x'  ->  [(0,0), (1,1), (2,3), (3,3)]
#
# `\bx*`'s start state accepts (an empty `x*` at a word boundary) and three of
# those four matches are empty ones at positions a `memchr('x')` jumps over. A
# narrowed `start_acc` reports only (2,3) — it LOSES THREE OF FOUR MATCHES.
# The `(?m)` twin `(?m)x*$` is the same shape on the newline half of the axis:
# its start state accepts wherever the next byte is a line break.
#
# WHY THE SABOTAGE IS THE `UPC_PLAIN` READ SPECIFICALLY. That is not an
# arbitrary way to break it — it is the pre-wave line, `fd->st[fs].accept`,
# transcribed into the new field. The realistic mistake is a mechanical
# refactor that renames the field and keeps the single read.
SAB_ID="S79-start-acc-one-class"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness mlinediff"
SAB_HARNESS_TARGET="tests/assertions/multiline.rxt"
SAB_DESC="the prefilter's start_acc gate reads only the UPC_PLAIN accept bit instead of the OR over the class axis, so a pattern whose start state accepts on SOME classes keeps its memchr/bitmap prefilter and skips past its own empty matches (\\bx* on 'a x' loses three of four; (?m)x*\$ loses its line-end matches)"
SAB_DOC_FIGURE="tests/assertions/multiline.rxt section 8's find-all cells and tests/assertions/wordb.rxt's \\bx* cells go red"
SAB_COUNT=1
SAB_BEFORE='    bool start_acc = state_acc_any(&fd->st[fs]);'
SAB_AFTER='    bool start_acc = fd->st[fs].up[UPC_PLAIN].accept;   /* SABOTAGE S79 */'
