#!/usr/bin/env python3
"""A2 as-is, plus a counter for the invariant §3 setup (ii) asserts: the open
stack contains NO REPEATS. Also records the max depth reached against the
`openst` array's own capacity (nfa->n + 2)."""
import subprocess, sys
path = sys.argv[1]
subprocess.run([sys.executable,
  "/home/duxevents/pcrec/docs/design/k18_measurements/prototypes/proto_a2.py", path], check=True)
src = open(path).read()
src = src.replace("static K18Stats k18_stats;",
                  "static K18Stats k18_stats;\nstatic long k18_dup;")
old = """                    cl->open[cl->depth].loop = s;
                    cl->ctx = lctx_intern(cl->ctxs, cl->ctx, s);"""
new = """                    for (int i = 0; i < cl->depth; i++)
                        if (cl->open[i].loop == s) { k18_dup++; break; }
                    cl->open[cl->depth].loop = s;
                    cl->ctx = lctx_intern(cl->ctxs, cl->ctx, s);"""
assert old in src
src = src.replace(old, new)
old2 = """                clo_visit(cl, st->t1);              /* t1 = exit (lazy) */
                cl->open[cl->depth].loop = s;"""
new2 = """                clo_visit(cl, st->t1);              /* t1 = exit (lazy) */
                for (int i = 0; i < cl->depth; i++)
                    if (cl->open[i].loop == s) { k18_dup++; break; }
                cl->open[cl->depth].loop = s;"""
assert old2 in src
src = src.replace(old2, new2)
src = src.replace('"K18STATS nfa=%d dfa=%d', '"K18STATS dup=%ld nfa=%d dfa=%d')
src = src.replace("nfa->n, d->n, k18_stats.closures,", "k18_dup, nfa->n, d->n, k18_stats.closures,")
open(path, "w").write(src); print("a2dup applied")
