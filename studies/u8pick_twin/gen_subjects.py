#!/usr/bin/env python3
"""Regenerate pcrec-bench's seven utf8 throughput subjects READ-ONLY.

usage: gen_subjects.py BENCH_UTF8_DIR OUTDIR

Imports the bench's own utf8text (no bytecode written into the bench
checkout), rebuilds each text with the bench's (id, size, seed, script)
table and checks every sha256 against the bench's committed
manifest_throughput.tsv.  The bench is never written to.
"""
import hashlib
import os
import sys

sys.dont_write_bytecode = True
bench, out = sys.argv[1], sys.argv[2]
sys.path.insert(0, bench)
import utf8text as ut  # noqa: E402

SIZES = (
    ("t-64k", 64 * 1024, 0x7f8a001, "mix"),
    ("t-256k", 256 * 1024, 0x7f8a002, "mix"),
    ("t-1m", 1024 * 1024, 0x7f8a003, "mix"),
    ("t-64k-lat", 64 * 1024, 0x7f8a010, "lat"),
    ("t-64k-cyr", 64 * 1024, 0x7f8a011, "cyr"),
    ("t-64k-cjk", 64 * 1024, 0x7f8a012, "cjk"),
    ("t-64k-asc", 64 * 1024, 0x7f8a013, "asc"),
)
want = {}
with open(os.path.join(bench, "manifest_throughput.tsv"), encoding="utf-8") as f:
    next(f)
    for ln in f:
        c = ln.rstrip("\n").split("\t")
        want[c[0]] = c[2]
os.makedirs(out, exist_ok=True)
bad = 0
for sid, n, seed, script in SIZES:
    body = ut.text(n, seed, script)
    sha = hashlib.sha256(body).hexdigest()
    ok = sha == want[sid]
    bad += not ok
    with open(os.path.join(out, sid + ".bin"), "wb") as f:
        f.write(body)
    print(sid, len(body), "sha-match" if ok else "SHA MISMATCH")
sys.exit(1 if bad else 0)
