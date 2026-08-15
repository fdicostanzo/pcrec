#!/usr/bin/env python3
"""Instrument the UNMODIFIED clo_visit with prototype A's counters.

MEASUREMENT ARTIFACT. Without this, "prototype A expands N states" is a number
with no denominator: the shipped compiler's own walk has never been counted, so
any inflation figure would be A's absolute cost dressed up as a ratio. This
build changes no behaviour at all — it only counts — so `base` and `basestats`
must emit byte-identical C, which is itself a check that the instrumentation is
inert.

Counter names match proto_a.py's so the same k18_stats.py reads both.
"""
import sys

path = sys.argv[1]
src = open(path).read()

src = src.replace('#include <stdlib.h>\n#include <string.h>',
                  '#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>')

src = src.replace("""typedef struct {
    Nfa      *nfa;
    uint32_t *seen;""",
"""typedef struct {
    long closures, expansions, visits, redirects, memo_probes;
    int  max_depth, max_ctx;
    long nonstack_top;
} K18Stats;
static K18Stats k18_stats;
static int k18_stats_on = -1;

typedef struct {
    Nfa      *nfa;
    uint32_t *seen;""")

old_visit = """    for (;;) {
        if (s < 0) return;
        if (cl->prune && cl->accept) return;
        if (cl->seen[s] == cl->gen) {"""
new_visit = """    for (;;) {
        if (s < 0) return;
        if (cl->prune && cl->accept) return;
        if (k18_stats_on) k18_stats.visits++;
        if (cl->seen[s] == cl->gen) {"""
assert old_visit in src, "clo_visit anchor drift"
src = src.replace(old_visit, new_visit)

old_red = """            const NState *ls = &cl->nfa->st[s];
            if (ls->loop) {
                s = ls->exit_is_t2 ? ls->t2 : ls->t1;
                continue;
            }
            return;"""
new_red = """            const NState *ls = &cl->nfa->st[s];
            if (ls->loop) {
                if (k18_stats_on) k18_stats.redirects++;
                s = ls->exit_is_t2 ? ls->t2 : ls->t1;
                continue;
            }
            return;"""
assert old_red in src
src = src.replace(old_red, new_red)

src = src.replace("""        cl->seen[s] = cl->gen;
        const NState *st = &cl->nfa->st[s];""",
"""        cl->seen[s] = cl->gen;
        if (k18_stats_on) k18_stats.expansions++;
        const NState *st = &cl->nfa->st[s];""")

src = src.replace("""    marks_next(mk);
    Clo cl = { nfa, mk->mark, mk->gen,""",
"""    marks_next(mk);
    if (k18_stats_on) k18_stats.closures++;
    Clo cl = { nfa, mk->mark, mk->gen,""")

src = src.replace("""    int *pre = arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(int));

    int root = nfa->start;""",
"""    int *pre = arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(int));

    if (k18_stats_on < 0) k18_stats_on = getenv("PCREC_K18_STATS") ? 1 : 0;
    if (k18_stats_on) memset(&k18_stats, 0, sizeof k18_stats);

    int root = nfa->start;""")

src = src.replace("""            d->st[si].tr[c] = tgt;
        }
    }
}""",
"""            d->st[si].tr[c] = tgt;
        }
    }

    if (k18_stats_on)
        fprintf(stderr,
                "K18STATS nfa=%d dfa=%d closures=%ld visits=%ld expansions=%ld "
                "redirects=%ld nonstacktop=%ld maxdepth=%d ctxs=%d\\n",
                nfa->n, d->n, k18_stats.closures, k18_stats.visits,
                k18_stats.expansions, k18_stats.redirects,
                k18_stats.nonstack_top, k18_stats.max_depth, k18_stats.max_ctx);
}""")

open(path, "w").write(src)
print("proto basestats applied to", path)
