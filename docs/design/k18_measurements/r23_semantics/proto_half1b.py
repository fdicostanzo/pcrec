#!/usr/bin/env python3
"""HALF-1 with a hugely oversized open-loop stack + a hard depth guard, so the
variant can be MEASURED instead of crashing. The crash itself is the finding:
without the open-set redirect trigger the stack has no no-repeat invariant and
overruns `openst`'s nfa->n+2 sizing."""
import subprocess, sys
path = sys.argv[1]
subprocess.run([sys.executable,
  "/tmp/claude-1001/-home-duxevents-pcrec/60beed03-a1ef-4a00-ba48-76e468397d0d/scratchpad/r23/semantics/proto_half1.py", path], check=True)
src = open(path).read()
src = src.replace("(size_t)(nfa->n + 2) * sizeof(OpenEnt)",
                  "(size_t)(nfa->n + 2) * 20000 * sizeof(OpenEnt)")
src = src.replace("""                    cl->open[cl->depth].loop = s;
                    cl->ctx = lctx_intern(cl->ctxs, cl->ctx, s);""",
"""                    if (cl->depth > k18_maxstack) k18_maxstack = cl->depth;
                    cl->open[cl->depth].loop = s;
                    cl->ctx = lctx_intern(cl->ctxs, cl->ctx, s);""")
src = src.replace("static K18Stats k18_stats;", "static K18Stats k18_stats;\nstatic int k18_maxstack;")
src = src.replace('"K18STATS nfa=%d', '"K18STATS maxstack=%d nfa=%d')
src = src.replace("nfa->n, d->n, k18_stats.closures,", "k18_maxstack, nfa->n, d->n, k18_stats.closures,")
open(path,"w").write(src); print("half1b applied")
