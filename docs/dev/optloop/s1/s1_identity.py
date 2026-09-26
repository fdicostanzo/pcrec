#!/usr/bin/env python3
"""[OPT-LITSCAN] S1 build — the per-commit IDENTITY GATE over emitted C.

k66_census.py's populations and emit path, re-aimed at S1's §7.2 commit
ladder: every commit before the mechanism must move ZERO artifacts, and the
mechanism's movers must equal litscan_s1.md §6's classes BY ID.

  bench   pcrec-bench's capability patterns (read-only), four configs:
          auto-caps, auto-nocaps, vm-caps, vm-nocaps.
  corpus  every distinct `pattern` line of every tests/**/*.rxt, under
          `--features all` and `--features all --engine=vm`.

The comparison is byte-for-byte after ONE normalization, applied only when
`ABI_FROM`/`ABI_TO` are set: the abi digit's own lines (the header
comment's `abi N`, `<P>_ABI`, `rx_info.abi`) are rewritten from the base's
number to the new one, so an abi event's same-length substitution does not
count as a program change. Everything else — stamps, comments, code — is
compared raw. A changed artifact is reported with the stamps S1's classes
are read off (RX_DFA_PREFILTER, _OFFSETS, RX_REQ_WHY, RX_REQ_RUN) on BOTH
sides, so the mover list can be joined against census_b.tsv by key.

  BASE=<pcrec> NEW=<pcrec> SCR=<scratch> [EXTRA="-fno-..."] \\
      [ABI_FROM=35 ABI_TO=36] [POPS=bench,corpus] python3 s1_identity.py
Writes $SCR/s1_identity.json and prints the tallies and the mover list.
"""
import os, re, glob, json, subprocess, collections
from concurrent.futures import ThreadPoolExecutor

BASE, NEW, SCR = os.environ["BASE"], os.environ["NEW"], os.environ["SCR"]
EXTRA = os.environ.get("EXTRA", "").split()
POPS = os.environ.get("POPS", "bench,corpus").split(",")
ABI_FROM, ABI_TO = os.environ.get("ABI_FROM"), os.environ.get("ABI_TO")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
PATDIR = "/Users/fdicostanzo/pcrec-bench/bench/capability/patterns"
BENCH_CFG = {"auto-caps": ["--features", "all"],
             "auto-nocaps": ["--features", "all", "--no-captures"],
             "vm-caps": ["--features", "all", "--engine=vm"],
             "vm-nocaps": ["--features", "all", "--engine=vm", "--no-captures"]}
CORPUS_CFG = {"auto": ["--features", "all"],
              "vm": ["--features", "all", "--engine=vm"]}
STAMPS = ("DFA_PREFILTER", "DFA_PREFILTER_OFFSETS", "REQ_WHY", "REQ_RUN",
          "ENGINE", "VM_PREFILTER")


def stamp(text, name):
    m = re.search(r'^#define RX_%s (.*)$' % name, text, re.M)
    return m.group(1).strip('"') if m else None


def norm(text):
    if not ABI_FROM:
        return text
    # the three abi-digit sites, each a same-length rewrite of one token
    text = re.sub(r'(abi )%s\b' % ABI_FROM, r'\g<1>%s' % ABI_TO, text)
    text = re.sub(r'^(#define RX_ABI )%s\b' % ABI_FROM, r'\g<1>%s' % ABI_TO,
                  text, flags=re.M)
    text = re.sub(r'(\.abi *= *)%s\b' % ABI_FROM, r'\g<1>%s' % ABI_TO, text)
    return text


def emit(binp, pat, flags, d):
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, "a.c")
    try:
        r = subprocess.run([binp, "-p", "rx", "-o", out, "--pattern", pat]
                           + flags + EXTRA, capture_output=True, timeout=180)
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
    rec["identity"] = "identical" if norm(b) == a else "changed"
    for s in STAMPS:
        rec["b_" + s], rec["a_" + s] = stamp(b, s), stamp(a, s)
    return rec


def jobs():
    n = 0
    if "bench" in POPS:
        for fn in sorted(os.listdir(PATDIR)):
            if not fn.endswith(".rx"):
                continue
            pat = open(os.path.join(PATDIR, fn), "rb").read().rstrip(b"\n") \
                .decode("utf-8", "surrogateescape")
            for cfg, flags in BENCH_CFG.items():
                n += 1
                yield (n, "bench", fn[:-3], pat, cfg, flags)
    if "corpus" in POPS:
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


def main():
    with ThreadPoolExecutor(max_workers=int(os.environ.get("PROCS", "4"))) as ex:
        res = list(ex.map(one, jobs()))
    json.dump(res, open(f"{SCR}/s1_identity.json", "w"), indent=0)
    for pop in POPS:
        rs = [r for r in res if r["pop"] == pop]
        print(f"== {pop}: {len(rs)} artifact-configs")
        print("  identity:", dict(collections.Counter(r["identity"] for r in rs)))
        ch = [r for r in rs if r["identity"] == "changed"]
        tr = collections.Counter(
            (r["b_DFA_PREFILTER"], r["a_DFA_PREFILTER"], r["b_REQ_WHY"], r["a_REQ_WHY"])
            for r in ch)
        for (bp, ap, bw, aw), k in sorted(tr.items(), key=lambda x: -x[1]):
            print(f"   {k:5d}  prefilter {bp}->{ap}  req_why {bw}->{aw}")
        for r in rs:
            if r["identity"] in ("timeout", "refusal-mismatch"):
                print(f"   {r['identity'].upper()} {r['cfg']} {r['key'][:70]!r}")


if __name__ == "__main__":
    main()
