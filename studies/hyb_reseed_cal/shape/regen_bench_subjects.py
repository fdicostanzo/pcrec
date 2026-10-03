#!/usr/bin/env python3
"""Regenerate pcrec-bench syntax@0.1's short (42) and throughput (3)
subjects into OUTDIR WITHOUT writing into the bench checkout (no
__pycache__, no manifest rewrite), and verify each against the bench's own
manifest sha256. usage: regen_bench_subjects.py BENCH_SYNTAX_DIR OUTDIR"""
import hashlib, os, sys
sys.dont_write_bytecode = True
src, out = sys.argv[1], sys.argv[2]
sys.path.insert(0, src)
import gen_subjects as gs, gen_throughput_subjects as gt  # noqa: E402
def man(name):
    rows = open(os.path.join(src, name)).read().splitlines()[1:]
    return {r.split("\t")[0]: r.split("\t")[2] for r in rows}
os.makedirs(os.path.join(out, "subj"), exist_ok=True)
os.makedirs(os.path.join(out, "thr"), exist_ok=True)
ok = bad = 0
m = man("manifest.tsv")
for sid, _d, body in gs.build():
    open(os.path.join(out, "subj", sid + ".bin"), "wb").write(body)
    if m.get(sid) == hashlib.sha256(body).hexdigest(): ok += 1
    else: bad += 1
m = man("manifest_throughput.tsv")
for sid, nbytes, seed, _t in gt.RUNS:
    body = gt.ct.text(seed, nbytes)
    open(os.path.join(out, "thr", sid + ".bin"), "wb").write(body)
    if m.get(sid) == hashlib.sha256(body).hexdigest(): ok += 1
    else: bad += 1
print("verified %d, MISMATCHED %d" % (ok, bad))
sys.exit(1 if bad else 0)
