#!/usr/bin/env python3
"""R23-semantics REFERENCE walk: NO memo (prototype C) AND per-frame restore of
the open-loop stack ENTRIES. The most conservative reading of the design's own
rule -- nothing is ever suppressed, and each frame sees the stack it pushed.
Its only job is to be something A2 can be checked AGAINST: any pattern where
A2 and REF emit different C is either an unsound memo or the S3 corruption."""
import subprocess, sys
path = sys.argv[1]
subprocess.run([sys.executable,
  "/home/duxevents/pcrec/docs/design/k18_measurements/prototypes/proto_c.py", path], check=True)
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
assert old in src
src = src.replace(old, new)
old = """done:
    cl->depth = save_depth;
    cl->ctx = save_ctx;
}"""
new = """done:
    cl->depth = save_depth;
    cl->ctx = save_ctx;
    if (save_open) {
        memcpy(cl->open, save_open, (size_t)save_depth * sizeof(OpenEnt));
        free(save_open);
    }
}"""
assert old in src
src = src.replace(old, new)
src = src.replace("300000000L", "20000000L")   # smaller budget: exit 97 fast
open(path, "w").write(src); print("proto REF applied")
