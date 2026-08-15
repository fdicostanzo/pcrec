#!/usr/bin/env python3
"""R23-semantics probe: prototype A2 with the open-loop stack ARRAY restored,
not just its depth.

A2's clo_visit saves `depth`/`ctx` at frame entry and restores them at `done:`.
A redirect can set `cl->depth = at` with `at < save_depth` (the re-arrived loop
was pushed by an ANCESTOR frame) and the continuation then PUSHES over
`open[at .. save_depth)`.  Restoring only `depth` leaves those entries holding
the wrong loop ids for the caller, whose redirect scan reads them.

This variant additionally saves and restores the ENTRIES.  It is deliberately
naive (a malloc per frame) because its only job is to be a correctness oracle
for A2, not to be fast.  If A2 and this variant emit the same C everywhere,
the hypothesis is refuted.
"""
import subprocess
import sys
import os

path = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
PROTO = "/home/duxevents/pcrec/docs/design/k18_measurements/prototypes/proto_a2.py"
subprocess.run([sys.executable, PROTO, path], check=True)

src = open(path).read()

old = """static void clo_visit(Clo *cl, int s)
{
    int save_depth = cl->depth;
    int save_ctx = cl->ctx;"""
new = """static void clo_visit(Clo *cl, int s)
{
    int save_depth = cl->depth;
    int save_ctx = cl->ctx;
    OpenEnt *save_open = NULL;
    if (save_depth > 0) {
        save_open = malloc((size_t)save_depth * sizeof(OpenEnt));
        if (!save_open) abort();
        memcpy(save_open, cl->open, (size_t)save_depth * sizeof(OpenEnt));
    }"""
assert old in src, "anchor drift (clo_visit head)"
src = src.replace(old, new)

old2 = """done:
    cl->depth = save_depth;
    cl->ctx = save_ctx;
}"""
new2 = """done:
    cl->depth = save_depth;
    cl->ctx = save_ctx;
    if (save_open) {
        memcpy(cl->open, save_open, (size_t)save_depth * sizeof(OpenEnt));
        free(save_open);
    }
}"""
assert old2 in src, "anchor drift (clo_visit tail)"
src = src.replace(old2, new2)

open(path, "w").write(src)
print("proto A2-FIX applied to", path)
