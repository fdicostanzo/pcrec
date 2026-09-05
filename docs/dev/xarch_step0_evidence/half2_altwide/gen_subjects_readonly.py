#!/usr/bin/env python3
# Read-only use of pcrec-bench's own subject-generation tooling (per the
# xarch0 brief: "reproduce the subject GENERATION from their tooling
# read-only"). Writes NOTHING into pcrec-bench -- calls build() directly
# and writes the bytes out here instead of letting main() write into their
# tree with its hardcoded OUT/MANIFEST paths.
import os
import sys
import hashlib

BENCH_ALTWIDE = "/Users/fdicostanzo/pcrec-bench/bench/altwide"
sys.path.insert(0, BENCH_ALTWIDE)
import gen_throughput_subjects as gts  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else "."

subjects = gts.build()
os.makedirs(OUT, exist_ok=True)
for sid, desc, text in subjects:
    b = text.encode("latin-1")
    p = os.path.join(OUT, sid + ".bin")
    with open(p, "wb") as f:
        f.write(b)
    print("%s\t%d\t%s\t%s" % (sid, len(b), hashlib.sha256(b).hexdigest(), desc))
