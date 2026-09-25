#!/usr/bin/env python3
"""[K64] fix A's EMITTED-C CENSUS: which artifacts does the fix move?

Compiles every pattern of two populations with two compilers and compares the
emitted .c BYTE FOR BYTE (same abi, same -p, same -o basename in each side's
own directory, so nothing needs normalising):

  bench   pcrec-bench's capability patterns (read-only), under the bench's
          four configs: auto-caps, auto-nocaps, vm-caps, vm-nocaps.
  corpus  every `pattern` line of every tests/**/*.rxt (known_fail included),
          under `--features all` (the auto route) and `--features all
          --engine=vm` (the forced-VM route). Block directives are ignored —
          this is a population of pattern TEXTS, not a re-run of the corpus.

PREDICTION (the brief's): only forced-VM artifacts move, each from RX_REQ_WHY
"one-attempt" to "emitted", each framed (RX_VM_FRAMELESS 0) with no exact
hybrid in front; every auto-route artifact byte-identical. Any other mover is
printed as UNPREDICTED.

  BASE=<pcrec at the branch point> NEW=<pcrec with the fix> SCR=<scratch> \
      python3 k64_census.py
Writes $SCR/k64_census.json and prints the tables.
"""
import os, re, sys, glob, json, subprocess, collections
from concurrent.futures import ThreadPoolExecutor

BASE, NEW, SCR = os.environ["BASE"], os.environ["NEW"], os.environ["SCR"]
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
PATDIR = "/Users/fdicostanzo/pcrec-bench/bench/capability/patterns"
BENCH_CFG = {"auto-caps": ["--features", "all"],
             "auto-nocaps": ["--features", "all", "--no-captures"],
             "vm-caps": ["--features", "all", "--engine=vm"],
             "vm-nocaps": ["--features", "all", "--engine=vm", "--no-captures"]}
CORPUS_CFG = {"auto": ["--features", "all"],
              "vm": ["--features", "all", "--engine=vm"]}


def stamp(text, name):
    m = re.search(r'^#define RX_%s (.*)$' % name, text, re.M)
    return m.group(1).strip('"') if m else None


def emit(binp, pat, flags, d):
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, "a.c")
    try:
        r = subprocess.run([binp, "-p", "rx", "-o", out, "--pattern", pat] + flags,
                           capture_output=True, timeout=180)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    if r.returncode != 0:
        return None
    return open(out, "rb").read().decode("latin-1")


def one(job):
    i, pop, key, pat, cfg, flags = job
    b = emit(BASE, pat, flags, f"{SCR}/c/{i}/b")
    a = emit(NEW, pat, flags, f"{SCR}/c/{i}/a")
    rec = {"pop": pop, "key": key, "cfg": cfg}
    if b is None or a is None or "TIMEOUT" in (a, b):
        rec["identity"] = "refused" if b is None and a is None else \
            ("timeout" if "TIMEOUT" in (a, b) else "refusal-mismatch")
        return rec
    rec["identity"] = "identical" if a == b else "changed"
    for s in ("REQ_WHY", "ENGINE", "VM_PREFILTER", "VM_PREFILTER_LANG",
              "VM_FRAMELESS", "VM_START"):
        rec[s] = stamp(a, s)
    rec["REQ_WHY_base"] = stamp(b, "REQ_WHY")
    return rec


def jobs():
    n = 0
    for fn in sorted(os.listdir(PATDIR)):
        if not fn.endswith(".rx"):
            continue
        pat = open(os.path.join(PATDIR, fn), "rb").read().rstrip(b"\n") \
            .decode("utf-8", "surrogateescape")
        for cfg, flags in BENCH_CFG.items():
            n += 1
            yield (n, "bench", fn[:-3], pat, cfg, flags)
    seen = set()
    for path in sorted(glob.glob(f"{ROOT}/tests/**/*.rxt", recursive=True)):
        for ln in open(path, "rb").read().decode("utf-8", "surrogateescape").splitlines():
            if not ln.startswith("pattern "):
                continue
            pat = ln[len("pattern "):]
            if pat in seen:
                continue
            seen.add(pat)
            for cfg, flags in CORPUS_CFG.items():
                n += 1
                yield (n, "corpus", pat, pat, cfg, flags)


def predicted(r):
    return (r["cfg"] in ("vm-caps", "vm-nocaps", "vm") and
            r["REQ_WHY_base"] == "one-attempt" and r["REQ_WHY"] == "emitted" and
            r["VM_FRAMELESS"] == "0" and
            not (r["VM_PREFILTER"] == "hybrid" and r["VM_PREFILTER_LANG"] == "exact"))


def main():
    with ThreadPoolExecutor(max_workers=int(os.environ.get("PROCS", "4"))) as ex:
        res = list(ex.map(one, jobs()))
    json.dump(res, open(f"{SCR}/k64_census.json", "w"), indent=0)
    for pop in ("bench", "corpus"):
        rs = [r for r in res if r["pop"] == pop]
        print(f"== {pop}: {len(rs)} artifact-configs")
        print("  identity x cfg:", dict(collections.Counter((r["cfg"], r["identity"]) for r in rs)))
        ch = [r for r in rs if r["identity"] == "changed"]
        print(f"  changed: {len(ch)}; predicted {sum(predicted(r) for r in ch)}")
        for r in ch:
            tag = "predicted  " if predicted(r) else "UNPREDICTED"
            print(f"   {tag} {r['cfg']:10s} {r['REQ_WHY_base']}->{r['REQ_WHY']} "
                  f"frameless={r['VM_FRAMELESS']} pf={r['VM_PREFILTER']}/{r['VM_PREFILTER_LANG']} "
                  f"start={r['VM_START']}  {r['key'][:70]!r}")
        odd = [r for r in rs if r["identity"] in ("timeout", "refusal-mismatch")]
        for r in odd:
            print(f"   {r['identity'].upper()} {r['cfg']} {r['key'][:70]!r}")


if __name__ == "__main__":
    main()
