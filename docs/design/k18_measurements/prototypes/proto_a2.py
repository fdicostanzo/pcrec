#!/usr/bin/env python3
"""Prototype A2 — prototype A with an EMPTY-CONTEXT FAST PATH.

MEASUREMENT ARTIFACT, but this is the shape the design note recommends.

A's measured problem is not its algorithm. On the fuzz-found pattern
`(1{0,30}?[^]abc][^abc]){8,8}0+|a` prototype A and the shipped compiler expand
the IDENTICAL number of states (11,714,704) over the identical number of
closures (332,476) with maxdepth=1 and only 2 contexts — and A still took 1.52 s
against the shipped 0.22 s. The whole difference is that A replaced one
generation-stamped array access with a hash probe, 15.7 million times.

So: when the open-loop stack is EMPTY the memo key (state, 0) carries no more
information than `state` does, and the original per-state stamp array is an
exact, faster representation of it. A2 keeps that array for ctx 0 and uses the
hash only for the contexts that actually need distinguishing. Since a closure
walk is at ctx 0 whenever it is not inside a loop body — which on the existing
corpus is 353 of 555 patterns entirely, and the large majority of visits in the
rest — the fast path carries nearly all the traffic.

This changes NO answers. A2 and A must agree byte for byte on emitted output;
that is checked, not assumed.
"""
import subprocess
import sys

path = sys.argv[1]
subprocess.run([sys.executable,
                __file__.replace("proto_a2.py", "proto_a.py"), path], check=True)

src = open(path).read()

# the ctx-0 memo is a per-state generation stamp again: one array store, no hash
old = """        if (k18_stats_on) k18_stats.memo_probes++;
        if (!pmemo_add(cl->memo, s, cl->ctx)) break;
        if (k18_stats_on) k18_stats.expansions++;"""
new = """        if (k18_stats_on) k18_stats.memo_probes++;
        if (cl->ctx == 0) {
            /* FAST PATH: an empty open-loop stack makes (state,0) and `state`
             * the same key, so the shipped compiler's own array is an exact
             * representation of the memo -- and one store instead of a hash
             * probe. This is where nearly all the traffic goes. */
            if (cl->seen0[s] == cl->gen) break;
            cl->seen0[s] = cl->gen;
        } else if (!pmemo_add(cl->memo, s, cl->ctx)) {
            break;
        }
        if (k18_stats_on) k18_stats.expansions++;"""
assert old in src, "proto A anchor drift"
src = src.replace(old, new)

src = src.replace("""    uint32_t *emit;    /* GLOBAL per-state dedup for N_CLASS output */""",
"""    uint32_t *emit;    /* GLOBAL per-state dedup for N_CLASS output */
    uint32_t *seen0;   /* per-state memo for the empty context */""")

src = src.replace("""                    bool prune, Marks *mk, PMemo *memo, LCtxTab *ctxs,
                    OpenEnt *openst, int *out, int *nout, bool *accept)""",
"""                    bool prune, Marks *mk, Marks *mk0, PMemo *memo,
                    LCtxTab *ctxs, OpenEnt *openst,
                    int *out, int *nout, bool *accept)""")

src = src.replace("""    marks_next(mk);
    pmemo_next(memo);
    if (k18_stats_on) k18_stats.closures++;
    Clo cl = { nfa, memo, ctxs, mk->mark, mk->gen, openst, 0, 0,
               out, 0, false, eol_ok, bot_ok, prune };""",
"""    marks_next(mk);
    marks_next(mk0);
    pmemo_next(memo);
    if (k18_stats_on) k18_stats.closures++;
    Clo cl = { nfa, memo, ctxs, mk->mark, mk0->mark, mk->gen, openst, 0, 0,
               out, 0, false, eol_ok, bot_ok, prune };""")

# marks_next is called on both, so the two generations advance in lockstep and
# cl->gen is valid for both arrays.
src = src.replace("""                      Marks *mk, int *scratch,
                      PMemo *memo, LCtxTab *ctxs, OpenEnt *openst)""",
"""                      Marks *mk, int *scratch,
                      Marks *mk0, PMemo *memo, LCtxTab *ctxs, OpenEnt *openst)""")

src = src.replace(
    "closure(nfa, pre, npre, bot_ok, false, prune, mk, memo, ctxs, openst, scratch, &nout, &accept);",
    "closure(nfa, pre, npre, bot_ok, false, prune, mk, mk0, memo, ctxs, openst, scratch, &nout, &accept);")
src = src.replace(
    "closure(nfa, pre, npre, bot_ok, true, prune, mk, memo, ctxs, openst, scratch2, &nout2, &accept2);",
    "closure(nfa, pre, npre, bot_ok, true, prune, mk, mk0, memo, ctxs, openst, scratch2, &nout2, &accept2);")

src = src.replace("""    PMemo memo; pmemo_init(&memo, (size_t)nfa->n);""",
"""    Marks marks0 = {
        arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(uint32_t)), 0, nfa->n
    };
    PMemo memo; pmemo_init(&memo, (size_t)nfa->n);""")

for a, b in (("&marks, scratch, &memo, &ctxs, openst",
              "&marks, scratch, &marks0, &memo, &ctxs, openst"),):
    src = src.replace(a, b)

open(path, "w").write(src)
print("proto A2 applied to", path)
