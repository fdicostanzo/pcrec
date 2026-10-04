#!/usr/bin/env python3
"""Regenerates pcrec-bench capability@0.1's short subjects into OUTDIR/cap/
WITHOUT writing into the bench checkout (no __pycache__, no manifest
rewrite), each verified against the bench's own manifest sha256 — the
capability twin of ../shape/regen_bench_subjects.py, for the A1 cell
(logparse-atomic short search). usage: regen_cap_subjects.py BENCH_CAPABILITY_DIR OUTDIR"""
import hashlib, os, sys
sys.dont_write_bytecode = True
src, out = sys.argv[1], sys.argv[2]
sys.path.insert(0, src)
import gen_subjects as gs  # noqa: E402
rows = open(os.path.join(src, "manifest.tsv"), encoding="utf-8").read().splitlines()[1:]
m = {r.split("\t")[0]: r.split("\t")[2] for r in rows}
os.makedirs(os.path.join(out, "cap"), exist_ok=True)
ok = bad = 0
for sid, _d, body in gs.build():
    open(os.path.join(out, "cap", sid + ".bin"), "wb").write(body)
    if m.get(sid) == hashlib.sha256(body).hexdigest(): ok += 1
    else: bad += 1
print("verified %d, MISMATCHED %d" % (ok, bad))
sys.exit(1 if bad or not ok else 0)
