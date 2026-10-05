#!/usr/bin/env python3
"""memfn R4b (R-1): materialize the subjects tb_r4b times, into OUTDIR,
READING the pcrec-bench checkout (never writing it: no .pyc, no files).

    python3 subjects_r4b.py OUTDIR [BENCH_ROOT]   # default ../pcrec-bench

Resolves bench subject names to bytes exactly as
docs/dev/optloop/s4/alpha_k82.sh's build step does (lines 22-60 there):
the capability and syntax sets' gen_throughput_subjects.py, run with its
output redirected into OUTDIR, each subject sha256-checked against the
set's COMMITTED manifest_throughput.tsv; the capability short subjects
from gen_subjects.build(), sha256-checked against manifest.tsv. Writes

    OUTDIR/cap/t-64k.bin t-256k.bin t-1m.bin     (cap:t-*)
    OUTDIR/syn/t-64k.bin t-256k.bin t-1m.bin     (syn:t-*)
    OUTDIR/short.bin    all 75 short subjects, <u32 little-endian len><bytes>...

Any sha256 mismatch prints SHA-MISMATCH and exits 1 (off-pin: stop).
"""
import contextlib
import hashlib
import importlib.util
import io
import os
import struct
import sys

sys.dont_write_bytecode = True


def load(bench, setname, mod):
    d = os.path.join(bench, "bench", setname)
    sys.path.insert(0, d)
    spec = importlib.util.spec_from_file_location(setname + "_" + mod, os.path.join(d, mod + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def committed(bench, setname, mf):
    man = {}
    for ln in open(os.path.join(bench, "bench", setname, mf), encoding="utf-8"):
        f = ln.rstrip("\n").split("\t")
        if len(f) >= 3 and f[0] != "id":
            man[f[0]] = f[2]
    return man


def main():
    out = sys.argv[1]
    bench = sys.argv[2] if len(sys.argv) > 2 else os.path.join("..", "pcrec-bench")
    bad = 0
    for tag, setname in (("cap", "capability"), ("syn", "syntax")):
        d = os.path.join(out, tag)
        os.makedirs(d, exist_ok=True)
        g = load(bench, setname, "gen_throughput_subjects")
        with contextlib.redirect_stdout(io.StringIO()):
            g.OUT, g.MANIFEST = d, os.path.join(d, "manifest_throughput.tsv")
            g.main()
        for sid, sha in committed(bench, setname, "manifest_throughput.tsv").items():
            p = os.path.join(d, sid + ".bin")
            ok = os.path.exists(p) and hashlib.sha256(open(p, "rb").read()).hexdigest() == sha
            print("%s:%s %s" % (tag, sid, "OK" if ok else "SHA-MISMATCH"))
            bad += not ok
    g = load(bench, "capability", "gen_subjects")
    man = committed(bench, "capability", "manifest.tsv")
    ns = 0
    lens = []
    with open(os.path.join(out, "short.bin"), "wb") as f:
        for sid, _desc, body in g.build():
            ok = man.get(sid) == hashlib.sha256(body).hexdigest()
            bad += not ok
            if not ok:
                print("short:%s SHA-MISMATCH" % sid)
            f.write(struct.pack("<I", len(body)) + body)
            ns += 1
            lens.append(len(body))
    print("short: %d subjects, %d..%d B" % (ns, min(lens), max(lens)))
    print("subjects: -> %s, sha256 mismatches %d" % (out, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
