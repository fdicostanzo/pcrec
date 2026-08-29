# S72 — [M6.2 wave B] THE REVERSE SKIP'S BLIND `sfound` WRITER, RESTORED.
#
# assertions_design.md §3.8.3.1 states an INVARIANT rather than a patch, and
# this row is why: there is more than one writer of `sfound`, and the second
# one is easy to miss.
#
#     INVARIANT: no `sfound` may be recorded at `pp == startpos` except
#     through the context-indexed accept.
#
# The loop-top writer is obvious. The reverse SKIP's is not — and it is worse
# than a first reading suggests, because `emit_dfa.c`'s `if (!views &&
# rd->st[K].up[UPC_PLAIN].accept)` is a COMPILE-TIME condition on whether to EMIT the line.
# What lands in the artifact under it is a BARE, UNCONDITIONAL `sfound = pp;`
# inside the skip block, with no runtime test to fail. So on any pattern where
# that block is emitted, every skip that stops exactly at `startpos` records a
# match start whose leading `\b`/`\B` was never evaluated against
# `s[startpos-1]` at all.
#
# The sabotage drops `!views` from that condition, which is exactly the edit
# someone would make while "restoring a lost optimization" — the line looks
# like a compensating accept the views path forgot.
#
# WHAT IT COSTS TO MISS: on `\Bx.*y\b`-shaped patterns a reverse skip landing
# on the boundary reports a match start the assertion forbids. The corpus can
# see some of that and the structural check sees ALL of it, which is the point
# of checking the invariant rather than the one site somebody remembered.
SAB_ID="S72-reverse-skip-blind-sfound"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="codegen harness"
SAB_HARNESS_TARGET="tests/assertions/wordb_basic.rxt"   # wordb.rxt split 2026-08-21; both-ends/interior wildcard forms live here
SAB_DESC="the reverse self-loop skip emits its bare unconditional 'sfound = pp;' under a word context too, so a skip stopping at pp == startpos records a match start whose leading \\b/\\B was never evaluated against s[startpos-1] (assertions_design.md S3.8.3.1's second writer)"
SAB_DOC_FIGURE="tests/codegen/run_codegen_tests.sh: [M6.2-WORDB rule 2] reports an sfound writer not conditioned on an accept read"
SAB_COUNT=1
# RE-ANCHORED 2026-08-29 ([ENG-ABS]): the stay-table NAME is now derived from
# `f->dir->c.name` rather than spelled "reverse" — a THIRD direction (the
# anchored match-here machine) made the literal wrong, and it emitted a
# reference to a table that does not exist in `<prefix>_match`. The anchor
# still carries the preceding `while (...)` line for the reason below.
# RE-ANCHORED 2026-08-26 ([ENG-FORM]): the reverse skip is the DIRECTION
# object's `dir_rev_skip` method now. The guard's two-line body is now
# CHARACTER-IDENTICAL to the forward object's, so the anchor carries the
# preceding `while (rewind_position > ...)` line: without it SAB_BEFORE would
# match twice and the row's SAB_COUNT=1 would fail rather than plant.
SAB_BEFORE='    sb_printf(c, "%s    while (rewind_position > search_from &&"
                 " %s_%s_stay%d[subject[rewind_position - 1]]) rewind_position--;\n",
              ind, f->p, f->dir->c.name, K);
    if (!f->views && f->d->st[K].up[UPC_PLAIN].accept)'
SAB_AFTER='    sb_printf(c, "%s    while (rewind_position > search_from &&"
                 " %s_%s_stay%d[subject[rewind_position - 1]]) rewind_position--;\n",
              ind, f->p, f->dir->c.name, K);
    if (f->d->st[K].up[UPC_PLAIN].accept)   /* SABOTAGE S72 */'
