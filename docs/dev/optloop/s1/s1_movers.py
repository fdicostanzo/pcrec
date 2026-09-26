#!/usr/bin/env python3
"""[OPT-LITSCAN] S1 build — the mechanism's movers, BY ID, against the census.

litscan_s1.md §7.2 step 5: "each sub-commit's program-region movers must
equal §6's classes, by id". This emits every artifact of census_b.py's own
populations (reqpos_census.py's bench_pop/corpus_pop, the same ids, the same
configs: bench caps/nocaps, corpus caps, all `--features all`) from BASE and
from NEW, compares them byte for byte after the abi-digit normalization
s1_identity.py applies, and joins each artifact's verdict against the class
census_b.tsv (run over a probe build of the SAME base) recorded for it.

  BASE=<pcrec> NEW=<pcrec> CENSUS=<census_b.tsv at BASE> SCR=<scratch>
  BENCH=<pcrec-bench root> CORPUS=<tree whose tests/ is the corpus>
  PCREC=<pcrec for --list-source> [EXTRA="-f..." (NEW only)]
  [BOTH="-f..." (both sides)] [ABI_FROM=35 ABI_TO=36]
  [EXPECT="A,E,rowb"]  python3 s1_movers.py

EXPECT names the population predicted to move: a comma list of census
classes, plus `rowb` for "the run row's predicate holds". Prints, per
population, the changed/identical split crossed with predicted/not, and
lists every UNPREDICTED mover and every predicted non-mover by id. Exit 0
iff both lists are empty.
"""
import os, sys, re, subprocess, collections
from concurrent.futures import ThreadPoolExecutor
sys.dont_write_bytecode = True
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "c2"))
from reqpos_census import bench_pop, corpus_pop  # noqa: E402
E = os.environ
EXTRA = E.get("EXTRA", "").split()   # NEW only
BOTH = E.get("BOTH", "").split()     # both sides (a deny-flag arm's control)
EXPECT = set(E.get("EXPECT", "A,E,rowb").split(","))
ABI_FROM, ABI_TO = E.get("ABI_FROM"), E.get("ABI_TO")


def norm(text):
    if not ABI_FROM:
        return text
    text = re.sub(rb'(abi )%s\b' % ABI_FROM.encode(), rb'\g<1>' + ABI_TO.encode(), text)
    text = re.sub(rb'(\.abi *= *)%s\b' % ABI_FROM.encode(), rb'\g<1>' + ABI_TO.encode(), text)
    return text


def emit(binp, pat, extra, d):
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, "a.c")
    try:
        r = subprocess.run([binp, "-p", "rx", "--features", "all", "-o", out] + extra
                           + ["--pattern", pat], capture_output=True, timeout=180)
    except subprocess.TimeoutExpired:
        return b"TIMEOUT"
    return open(out, "rb").read() if r.returncode == 0 else None


def one(job):
    i, key, pat, extra = job
    b = emit(E["BASE"], pat, extra + BOTH, f"{E['SCR']}/m/{i}/b")
    a = emit(E["NEW"], pat, extra + BOTH + EXTRA, f"{E['SCR']}/m/{i}/a")
    if b is None and a is None:
        return key, "refused"
    if b is None or a is None or b"TIMEOUT" in (a, b):
        return key, "odd"
    return key, "identical" if norm(b) == a else "changed"


def main():
    cls = {}
    for ln in open(E["CENSUS"]):
        if ln.startswith("#") or ln.startswith("pop\t"):
            continue
        f = ln.rstrip("\n").split("\t")
        cls[(f[0], f[1], f[2])] = (f[3], f[4] == "1")
    jobs, n = [], 0
    for pname, rows, cfgs in (("bench", bench_pop(), [("caps", []), ("nocaps", ["--no-captures"])]),
                              ("corpus", corpus_pop(), [("caps", [])])):
        for rid, pat in rows:
            for cname, extra in cfgs:
                n += 1
                jobs.append((n, (pname, rid, cname), pat.decode("utf-8", "surrogateescape"), extra))
    with ThreadPoolExecutor(max_workers=int(E.get("PROCS", "4"))) as ex:
        res = dict(ex.map(one, jobs))
    bad = 0
    for pname in ("bench", "corpus"):
        tab = collections.Counter()
        unpred, missed = [], []
        for key, v in res.items():
            if key[0] != pname or v == "refused":
                continue
            c, rowb = cls.get(key, ("?", False))
            pred = c in EXPECT or ("rowb" in EXPECT and rowb)
            tab[(v, pred, c + ("+rowb" if rowb else ""))] += 1
            if v != "identical" and not pred:
                unpred.append((key, v, c))
            if v == "identical" and pred:
                missed.append((key, c))
        print(f"== {pname}")
        for (v, pred, c), k in sorted(tab.items()):
            print(f"   {k:6d}  {v:9s} predicted={int(pred)}  class={c}")
        for key, v, c in unpred:
            print(f"   UNPREDICTED {v} class={c} {key[2]} {key[1]!r}")
        for key, c in missed:
            print(f"   PREDICTED-NOT-MOVED class={c} {key[2]} {key[1]!r}")
        bad += len(unpred) + len(missed)
    print(f"mismatches: {bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
