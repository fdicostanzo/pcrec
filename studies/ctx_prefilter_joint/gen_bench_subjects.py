#!/usr/bin/env python3
"""gen_bench_subjects.py OUTDIR -- regenerate, IN MEMORY, the bench's
syntax@0.1 throughput texts (pcrec-bench is read-only and its subjects/
throughput/ trees are gitignored, so they exist only if a bench checkout
generated them): imports bench/syntax/censustext.py with bytecode writing
OFF, draws t-64k and t-256k with the seeds gen_throughput_subjects.py
declares, and REFUSES unless each sha256 equals manifest_throughput.tsv.
Writes only under OUTDIR (session scratch)."""
import hashlib
import os
import sys

sys.dont_write_bytecode = True
BENCH = os.environ.get("PCREC_BENCH", "/Users/fdicostanzo/pcrec-bench")
SYN = os.path.join(BENCH, "bench", "syntax")
sys.path.insert(0, SYN)
import censustext as ct  # noqa: E402

RUNS = (("t-64k", 65536, 20260905), ("t-256k", 262144, 20260906))
want = {}
for line in open(os.path.join(SYN, "manifest_throughput.tsv")).read().splitlines()[1:]:
    f = line.split("\t")
    want[f[0]] = f[2]
os.makedirs(sys.argv[1], exist_ok=True)
for sid, n, seed in RUNS:
    body = ct.text(seed, n)
    got = hashlib.sha256(body).hexdigest()
    if got != want[sid]:
        sys.exit("sha256 mismatch for %s: %s != %s" % (sid, got, want[sid]))
    open(os.path.join(sys.argv[1], "syntax-" + sid + ".bin"), "wb").write(body)
    print("syntax-%s.bin ok %s" % (sid, got[:12]))
