#!/usr/bin/env python3
"""HALF-PROTOTYPE (1): change (1) ALONE — the memo gains the open-loop
context, but the redirect trigger stays the SHIPPED one ("this key was already
seen in this closure and the state is a loop entry"), not "the loop is open".
"""
import subprocess, sys
path = sys.argv[1]
subprocess.run([sys.executable,
  "/home/duxevents/pcrec/docs/design/k18_measurements/prototypes/proto_a.py", path], check=True)
src = open(path).read()
old = """        if (st->loop) {
            int at = -1;
            for (int i = cl->depth - 1; i >= 0; i--)
                if (cl->open[i].loop == s) { at = i; break; }
            if (at >= 0) {
                if (k18_stats_on) {
                    k18_stats.redirects++;
                    if (at != cl->depth - 1) k18_stats.nonstack_top++;
                }
                cl->depth = at;                                   /* pop L and anything above it */
                cl->ctx = at ? cl->open[at - 1].ctx : 0;
                s = st->exit_is_t2 ? st->t2 : st->t1;
                continue;
            }
        }

        if (k18_stats_on) k18_stats.memo_probes++;
        if (!pmemo_add(cl->memo, s, cl->ctx)) break;"""
new = """        if (k18_stats_on) k18_stats.memo_probes++;
        if (!pmemo_add(cl->memo, s, cl->ctx)) {
            /* HALF-1: the SHIPPED trigger, lifted to the (state,ctx) key. */
            if (st->loop) {
                if (k18_stats_on) k18_stats.redirects++;
                s = st->exit_is_t2 ? st->t2 : st->t1;
                continue;
            }
            break;
        }"""
assert old in src, "anchor drift"
src = src.replace(old, new)
open(path, "w").write(src); print("half1 applied")
