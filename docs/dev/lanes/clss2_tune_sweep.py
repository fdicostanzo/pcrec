#!/usr/bin/env python3
"""docs/dev/lanes/clss2_tune_sweep.py -- [CLS-TREE] S2's mover census at the
size-leaning `--tune` positions (lane clss2, 2026-09-30).

`scripts/cls_identity.py` compares at the DEFAULT position only, and S2's
kit byte forms fire at `--tune=-2`/`-1` only. This census compiles every
corpus `pattern` line (`--features all`) at -2 and -1, on the default route
and forced `--engine=vm`, with a BASE compiler and a CANDIDATE compiler whose
abi digit was normalized to the base's, and classifies every pair:

  same         byte-identical
  kit          moved, and the candidate carries a kit form the base lacks
               (`_class_kit<N>` or `_scankit<N>`); AND the candidate built
               with `-fno-cls-kit` must be byte-identical to the base built
               with `-fno-cls-kit` (the deny restores the pre-S2 artifact)
  wcls         moved, no byte kit form, but a wide-class matcher moved (the
               one-interval <= U+00FF `byte-range` row, predicted)
  UNEXPLAINED  anything else (a finding)

Usage: clss2_tune_sweep.py BASE_BIN CAND_BIN TREE [--jobs N] [--out TSV]
Exit 0 iff no UNEXPLAINED pair and no deny-restore failure.
"""
import argparse
import concurrent.futures
import glob
import os
import re
import subprocess
import tempfile


def patterns(tree):
    seen = []
    have = set()
    for f in sorted(glob.glob(os.path.join(tree, "tests", "**", "*.rxt"), recursive=True)):
        with open(f, "rb") as fh:
            for line in fh:
                if line.startswith(b"pattern "):
                    p = line[len(b"pattern "):].rstrip(b"\n")
                    if p and p not in have:
                        have.add(p)
                        seen.append(p)
    return seen


def emit(binp, pat, args, d):
    out = os.path.join(d, "out.c")
    try:
        r = subprocess.run([binp, "-p", "rx", "--features", "all"] + args
                           + ["-o", out, "--pattern", pat],
                           capture_output=True, timeout=60)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0:
        return b"REFUSED"
    with open(out, "rb") as fh:
        return fh.read()


KIT = re.compile(rb"_class_kit[0-9]+\(|_scankit[0-9]+\(")
WCLS = re.compile(rb"static inline int rx_wcls[0-9]+\(")


def one(job):
    base, cand, pat, tune, eng = job
    with tempfile.TemporaryDirectory() as d:
        args = ["--tune=%d" % tune] + (["--engine=vm"] if eng == "vm" else [])
        a = emit(base, pat, args, d)
        b = emit(cand, pat, args, d)
        if a == b:
            return (pat, tune, eng, "same", "")
        if a is None or b is None or a == b"REFUSED" or b == b"REFUSED":
            return (pat, tune, eng, "UNEXPLAINED",
                    "refusal/timeout asymmetry" if a != b else "")
        if KIT.search(b) and not KIT.search(a):
            ad = emit(base, pat, args + ["-fno-cls-kit"], d)
            bd = emit(cand, pat, args + ["-fno-cls-kit"], d)
            if ad == bd:
                return (pat, tune, eng, "kit", "deny restores")
            # a wide one-interval class can move under the deny too
            if WCLS.search(bd or b""):
                return (pat, tune, eng, "kit", "deny restores but for a wide class")
            return (pat, tune, eng, "UNEXPLAINED", "kit mover whose -fno-cls-kit build differs")
        if WCLS.search(b):
            return (pat, tune, eng, "wcls", "")
        return (pat, tune, eng, "UNEXPLAINED", "moved without a kit form")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("cand")
    ap.add_argument("tree")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--out")
    a = ap.parse_args()
    pats = patterns(a.tree)
    jobs = [(a.base, a.cand, p, t, e) for p in pats for t in (-2, -1) for e in ("auto", "vm")]
    counts = {}
    rows = []
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        for r in ex.map(one, jobs):
            rows.append(r)
            counts[r[3]] = counts.get(r[3], 0) + 1
    if a.out:
        with open(a.out, "w", encoding="utf-8", errors="surrogateescape") as fh:
            fh.write("pattern\ttune\tengine\tclass\tnote\n")
            for p, t, e, c, n in rows:
                if c != "same":
                    fh.write("%s\t%d\t%s\t%s\t%s\n" % (p.decode("utf-8", "surrogateescape"), t, e, c, n))
    print("patterns %d, pairs %d: %s" % (len(pats), len(rows), counts))
    bad = [r for r in rows if r[3] == "UNEXPLAINED"]
    for p, t, e, c, n in bad[:40]:
        print("UNEXPLAINED --tune=%d %s %r: %s" % (t, e, p, n))
    print("RESULT: %s" % ("PASS" if not bad else "FAIL (%d unexplained)" % len(bad)))
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
