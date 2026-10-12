#!/usr/bin/env python3
"""gen_subjects.py BENCHCOPY OUTDIR -- regenerate the bench throughput
subjects the window-search game simulates over, from a `git archive` COPY of
pcrec-bench (never the live checkout: importing its generators would write
__pycache__ there). Each subject's sha256 is checked against the bench's own
committed manifest_throughput.tsv -- the control that these are the bytes the
bench measures, not a look-alike.

    git -C ../pcrec-bench archive HEAD bench pcrecbench | tar -x -C BENCHCOPY
"""
import hashlib
import importlib
import os
import sys

sys.dont_write_bytecode = True


def manifest(bench, s):
    rows = {}
    for ln in open(os.path.join(bench, s, "manifest_throughput.tsv")):
        f = ln.rstrip("\n").split("\t")
        if f[0] != "id":
            rows[f[0]] = f[2]
    return rows


def load(bench, s, mod):
    sys.path.insert(0, os.path.join(bench, s))
    sys.path.insert(0, os.path.dirname(os.path.abspath(bench)))
    m = importlib.import_module(mod)
    sys.path.pop(0)
    sys.path.pop(0)
    return m


def main(bench, out):
    os.makedirs(out, exist_ok=True)
    got = []
    ct = load(bench, "capability", "captext")
    got.append(("capability", "t-256k", ct.text(256 * 1024, 0xC0FFEE2)))
    st = load(bench, "syntax", "censustext")
    got.append(("syntax", "t-256k", st.text(20260906, 262144)))
    lg = load(bench, "loglines", "gen_throughput_subjects")
    for sid, _desc, body in lg.build():
        if sid in ("t-256k-fail", "t-256k-hit"):
            got.append(("loglines", sid, body))
    bad = 0
    for s, sid, body in got:
        want = manifest(bench, s)[sid]
        have = hashlib.sha256(body).hexdigest()
        ok = want == have
        bad += not ok
        with open(os.path.join(out, "%s__%s.bin" % (s, sid)), "wb") as f:
            f.write(body)
        print("%s\t%s\t%d\t%s" % (s, sid, len(body), "sha-ok" if ok else "SHA-MISMATCH"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
