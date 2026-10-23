#!/usr/bin/env python3
"""docs/dev/lanes/s3_evidence/pick_588.py -- job 588's MOVER SAMPLE pick (lane s3, the S3 review's
item E): about 24 cover movers beside §6's eight cells, drawn deterministically from the corpus's
mover list and written to sample_588.tsv (committed; job 588 reads it, never re-picks).

    python3 -I pick_588.py --new BIN --tree DIR --out sample_588.tsv [--seed N] [--want N] [--jobs N]

THE MOVER LIST is census.py's own rule on its own enumeration: every distinct corpus pattern
(scripts/emit_sweep.py's enumerate_corpus) whose default artifact (`-p rx --features all`) reads
`#define RX_DFA_SCAN "cover"` on NEW; §6's eight cells (kit_proof/measure/cells.tsv) are excluded.

THE STRATA, read from NEW's own text (the E-find statement, the line declaring `rx_mf<N>_s`):
  B   LIBC (`memchr(` in the statement) or WALK (an in-place walk). D-hors replaces B, so a D-hors
      artifact's form is read from its `--memfn=no-wf-hors` compile, where B is rendered
  D   hors (the file-scope `_sh[256]` table) or one
  C   run (a run compare: `rx_w<W>(` or `memcmp(` in the statement) or norun
  engine  default only: `--engine=vm` never reads cover (C1: cover is a DFA-route row), so the vm
      stratum is EMPTY by construction and is reported as such, not sampled
A pattern is a candidate only where gen_sample_588.py can generate its `real` class (python `re`
reads it and a generated match verifies): the sample is timed against python's answers.

THE PICK: random.Random(seed) over each stratum's candidates (sorted first, so the pick depends on
the seed and the corpus alone), round robin over the non-empty strata in sorted order, one at a time,
until WANT are picked or the candidates run out. The header records every stratum's population.
"""
import argparse
import concurrent.futures
import importlib.util
import os
import random
import subprocess
import sys

here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("gsp", os.path.join(here, "gen_sample_588.py"))
gsp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gsp)

COVER = b'#define RX_DFA_SCAN "cover"'


def compile_c(bin_, pat, *flags):
    r = subprocess.run([bin_, "-p", "rx", "--features", "all", *flags, "-o", "-", "--pattern", pat],
                       capture_output=True, timeout=60)
    return r.stdout if r.returncode == 0 else b""


def statement(text):
    return b"\n".join(l for l in text.split(b"\n") if b"_s = (const unsigned char *)" in l and b"rx_mf" in l)


def classify(task):
    bin_, pat = task
    text = compile_c(bin_, pat)
    if COVER not in text:
        return pat, None
    st = statement(text)
    hors = b"_sh[256]" in text
    bst = statement(compile_c(bin_, pat, "--memfn=no-wf-hors")) if hors else st
    form = "LIBC" if b"memchr(" in bst else "WALK"
    run = b"rx_w" in st or b"memcmp(" in st
    return pat, (form, "hors" if hors else "one", "run" if run else "norun")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20261023)
    ap.add_argument("--want", type=int, default=24)
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(a.tree, "scripts"))
    import emit_sweep  # noqa: E402
    cells = set()
    for ln in open(os.path.join(a.tree, "docs/design/kit_proof/measure/cells.tsv")):
        if ln.strip() and not ln.startswith("#"):
            cells.add(ln.rstrip("\n").split("\t")[1].encode())
    pats = sorted(set(p for _, _, p in emit_sweep.enumerate_corpus(a.new, a.tree, 60)) - cells)
    strata, movers = {}, 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for pat, st in ex.map(classify, [(a.new, p) for p in pats], chunksize=16):
            if st is None:
                continue
            movers += 1
            strata.setdefault(st, {"movers": 0, "cand": []})
            strata[st]["movers"] += 1
            rx = gsp.compiles(pat)
            if rx is not None and gsp.match_of(pat, rx, random.Random(0)) is not None:
                strata[st]["cand"].append(pat)
    rng = random.Random(a.seed)
    keys = sorted(strata)
    for k in keys:
        strata[k]["gen"] = len(strata[k]["cand"])
        strata[k]["cand"].sort()
        rng.shuffle(strata[k]["cand"])
    picked = []
    while len(picked) < a.want and any(strata[k]["cand"] for k in keys):
        for k in keys:
            if strata[k]["cand"] and len(picked) < a.want:
                picked.append((k, strata[k]["cand"].pop(0)))
    with open(a.out, "w", encoding="utf-8") as f:
        f.write("# docs/dev/lanes/s3_evidence/sample_588.tsv -- job 588's MOVER SAMPLE (not the §6 bar),\n"
                "# written by pick_588.py (its header is the rule); do not edit by hand.\n"
                "# corpus patterns %d (§6's cells excluded), cover movers %d, seed %d, want %d, picked %d\n"
                "# engine vm: 0 movers (C1, cover is a DFA-route row): no vm stratum\n"
                % (len(pats), movers, a.seed, a.want, len(picked)))
        for k in keys:
            f.write("# stratum %s/%s/%s: movers %d, generatable %d, picked %d\n"
                    % (k + (strata[k]["movers"], strata[k]["gen"], sum(1 for s, _ in picked if s == k))))
        f.write("#id\tstratum\tpattern\n")
        for i, (k, p) in enumerate(picked):
            f.write("smp%02d\t%s\t%s\n" % (i + 1, "/".join(k), emit_sweep.encode_escape(p)))
    print("pick_588: %d corpus patterns, %d cover movers in %d strata, %d picked -> %s"
          % (len(pats), movers, len(keys), len(picked), a.out))


if __name__ == "__main__":
    main()
