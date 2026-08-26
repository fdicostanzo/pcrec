# S74 — [M6.2 wave B] MECHANISM 4's REVERSE TERMINATION BOUNDARY REMOVED.
#
# THE LOST MATCH assertions_design.md §3.8.3.1 says the first draft of this
# design would have shipped, and the row that proves the differential sweep's
# arm split is real rather than decorative.
#
# The reverse walk breaks at `rewind_position == search_from` BEFORE reading `subject[search_from-1]`,
# so a LEADING `\b`/`\B` at the match start is evaluated with no left context
# — the walk silently assuming start-of-subject. The cure is a context-indexed
# accept attached to that break, seeded from `subject[search_from-1]`. This sabotage
# takes it back out and restores the blind scalar read.
#
# WHY IT IS ON THIS LIST RATHER THAN LEFT TO THE CORPUS TO NOTICE:
#
#   `\b` IS SAFE BY ACCIDENT. Its blind assumption (no left context means
#   non-word) coincides with the cases the forward pass lets through, so a
#   leading-`\b` population reports CLEAN against an implementation that
#   throws matches away. `\B` inverts it, and only at `search_from > 0`.
#
# So the population this sabotage is visible on is narrow and specific —
# LEADING `\B` at `search_from > 0` — and a suite that did not deliberately carry
# it would run green. tests/assertions/wordb_basic.rxt carries it as `ms`/`ns`
# cells; the named one is `\Bfoo` on "xfoo" at search_from 1, which is (1,4) and
# becomes "no match" under this edit.
#
# It is also the failure the wave's own FORWARD fix makes reachable: before
# mechanism 4's forward half, the forward pass never found the match for the
# reverse walk to lose.
#
# TWO INSTRUMENTS SEE IT, and they see different halves. The harness sees the
# LOST MATCHES on the narrow population above. `[M6.2-WORDB rule 2b]` sees
# something the corpus cannot state: with the context read gone there is no
# `subject[search_from - 1]` in the emitted reverse loop at all, so the rule that pins
# WHERE that read sits (R30 N9 — attached to the boundary break, never peeled
# below a loop whose other exit is a dead state) has nothing to locate and
# says so. That is this row's second job: it is the measured failing
# direction for rule 2b, which otherwise would be a check with none.
SAB_ID="S74-reverse-termination-blind"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness assertions"
SAB_HARNESS_TARGET="tests/assertions/wordb_basic.rxt"   # wordb.rxt split 2026-08-21; the named \Bfoo-on-"xfoo"-at-search_from-1 cell lives here
SAB_DESC="the reverse walk's termination boundary drops its context-indexed accept and reads the blind scalar one, so a LEADING \\B at search_from > 0 loses its match (assertions_design.md S3.8.3.1); leading-\\b patterns and every trailing-assertion pattern stay green, which is why the sweep is split into arms"
SAB_DOC_FIGURE="tests/assertions/wordb_basic.rxt: the leading-\\B ms/ns cells at search_from > 0 fail; every \\b cell and every trailing-assertion cell stays green"
SAB_COUNT=1
# RE-ANCHORED 2026-08-26 ([OPT-3] STEP 2): the boundary's context-indexed
# accept now takes its INDEX EXPRESSION from `premul_ix` (built into `ixbuf`
# from a `cls` local) rather than spelling `%s * %d + ...` inline, so the
# anchor spans the whole `sb_printf` and its argument list — the two must move
# together or the format and the args disagree. The EDIT is unchanged in kind:
# the context-indexed read is dropped and the blind scalar one is left, which
# is the LOST MATCH for a leading \B at search_from > 0 this row exists for.
# RE-ANCHORED 2026-08-26 ([ENG-FORM]): the reverse boundary's context-indexed
# accept is the DIRECTION object's `dir_rev_bound_accept` method now -- one
# site, called from axis E's `by_class` tail, rather than a branch inside
# `emit_unanchored`. The `(void)cls` the old planting needed is gone with the
# `cls` buffer it silenced.
SAB_BEFORE='    sb_printf(c, "%s    if (search_from"
                 " ? %s_reverse_accepts_class(%s_reverse_is_accepting_by_class, %s,\n"
                 "%s                          %s_reverse_byte_class[subject[search_from - 1]])\n"
                 "%s                 : %s_reverse_accepts(%s_reverse_is_accepting, %s))"
                 " %s = %s;\n",
              f->dir->bind, f->p, f->p, f->src,
              f->dir->bind, f->p,
              f->dir->bind, f->p, f->p, f->src, f->dir->recv, f->dir->posv);'
SAB_AFTER='    /* SABOTAGE S74: the context read is dropped and the boundary takes
     * the blind scalar accept. */
    sb_printf(c, "%s    if (%s_reverse_accepts(%s_reverse_is_accepting, %s)) %s = %s;\n",
              f->dir->bind, f->p, f->p, f->src, f->dir->recv, f->dir->posv);'
