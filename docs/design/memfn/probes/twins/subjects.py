#!/usr/bin/env python3
"""memfn twins: materialize the pcrec-bench subjects the twins time, into
OUTDIR, READING the bench checkout (never writing it: no .pyc, no files).

    python3 subjects.py OUTDIR [BENCH_ROOT]   # default ../pcrec-bench (from the repo root)

Writes OUTDIR/cap-short.bin (the capability set's 75 short subjects, each
as <u32 little-endian length><bytes>), OUTDIR/cap-t-64k.bin, cap-t-1m.bin
(copies of bench/capability/throughput/), syn-t-64k.bin, syn-t-1m.bin (the
syntax set's throughput texts, regenerated from censustext.py at the seeds
its generator uses). Every subject's sha256 is checked against the bench's
committed manifest; any mismatch exits 1.
"""
import hashlib
import os
import shutil
import struct
import sys

sys.dont_write_bytecode = True


def manifest(path):
    m = {}
    for line in open(path, encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if f[0] != "id":
            m[f[0]] = f[2]
    return m


def main():
    out = sys.argv[1]
    bench = sys.argv[2] if len(sys.argv) > 2 else os.path.join("..", "pcrec-bench")
    cap = os.path.join(bench, "bench", "capability")
    syn = os.path.join(bench, "bench", "syntax")
    os.makedirs(out, exist_ok=True)
    bad = 0

    sys.path.insert(0, cap)
    import gen_subjects as gs  # noqa: E402
    m = manifest(os.path.join(cap, "manifest.tsv"))
    with open(os.path.join(out, "cap-short.bin"), "wb") as f:
        for sid, _desc, body in gs.build():
            bad += hashlib.sha256(body).hexdigest() != m.get(sid)
            f.write(struct.pack("<I", len(body)) + body)
    sys.path.pop(0)

    m = manifest(os.path.join(cap, "manifest_throughput.tsv"))
    for sid in ("t-64k", "t-1m"):
        src = os.path.join(cap, "throughput", sid + ".bin")
        bad += hashlib.sha256(open(src, "rb").read()).hexdigest() != m[sid]
        shutil.copyfile(src, os.path.join(out, "cap-" + sid + ".bin"))

    sys.path.insert(0, syn)
    import censustext as ct  # noqa: E402
    m = manifest(os.path.join(syn, "manifest_throughput.tsv"))
    for sid, n, seed in (("t-64k", 65536, 20260905), ("t-1m", 1048576, 20260907)):
        body = ct.text(seed, n)
        bad += hashlib.sha256(body).hexdigest() != m[sid]
        with open(os.path.join(out, "syn-" + sid + ".bin"), "wb") as f:
            f.write(body)

    print("subjects: -> %s, sha256 mismatches %d" % (out, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
