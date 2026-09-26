#!/usr/bin/env python3
"""[K66] the whole-run compare's EMITTED-C CENSUS: which artifacts does it move?

k65_census.py's instrument, re-aimed: same two populations, same configs,
same byte-for-byte comparison; only the PREDICTION and the per-mover facts
differ.

  bench   pcrec-bench's capability patterns (read-only), under the bench's
          four configs: auto-caps, auto-nocaps, vm-caps, vm-nocaps.
  corpus  every `pattern` line of every tests/**/*.rxt (known_fail included),
          under `--features all` and `--features all --engine=vm`.

PREDICTION: a mover is exactly an artifact with NO DFA scan (RX_ENGINE "vm",
RX_VM_PREFILTER "none") that emits the pre-check (RX_REQ_WHY "emitted") and
whose necessary run is longer than the 8-byte window RX_REQ_RUN stamps (so
the stamp's window is full, 16 hex digits). Its change is ONE inserted
whole-run compare block (a `memcmp` of more than 8 bytes) plus, where the
K65 `rq_set[]` array listed a byte of the whole run outside the window, that
array shrinking or disappearing. The stamps do not move. Every other artifact
is byte-identical; any other mover is printed as UNPREDICTED.

  BASE=<pcrec at the branch point> NEW=<pcrec with the fix> SCR=<scratch> \\
      python3 k66_census.py
Writes $SCR/k66_census.json and prints the tables.
"""
import os, re, glob, json, difflib, subprocess, collections
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
STAMPS = ("REQ_WHY", "REQ_RUN", "REQ_BYTE", "ENGINE", "VM_PREFILTER",
          "VM_FRAMELESS", "VM_START")
WHOLE = re.compile(r'!memcmp\(subject \+ rp_c[^,]*, "(.*)", (\d+)\)\) break;')


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
    for s in STAMPS:
        rec[s] = stamp(a, s)
    rec["stamps_moved"] = [s for s in STAMPS if stamp(b, s) != rec[s]]
    run = rec["REQ_RUN"] or "none"
    rec["window_full"] = run != "none" and len(run.split("@")[0]) == 16
    al, bl = a.splitlines(), b.splitlines()
    rec["dlines"] = len(al) - len(bl)
    # strip the ONE whole-run block (13 lines, `{` .. `}`) out of the new text
    hits = [k for k, x in enumerate(al) for m in [WHOLE.search(x)]
            if m and int(m.group(2)) > 8]
    rec["whole_len"] = None
    if len(hits) == 1:
        k = hits[0]
        rec["whole_len"] = int(WHOLE.search(al[k]).group(2))
        rec["whole_run"] = WHOLE.search(al[k]).group(1)
        al = al[:k - 8] + al[k + 5:]
    rq = lambda t: next((m.group(1) for m in
                         [re.search(r'rq_set\[\] = \{ (.*) \};', t)] if m), None)
    rec["rq_base"], rec["rq_new"] = rq(b), rq(a)
    # the base's rq_set block rewritten to the new one (or removed): what
    # remains must then be byte-identical
    if rec["rq_base"] != rec["rq_new"]:
        k = next(n for n, x in enumerate(bl) if "rq_set[] = {" in x)
        if rec["rq_new"] is None:
            bl = bl[:k - 1] + bl[k + 5:]
        else:
            bl = bl[:k] + [x for x in a.splitlines() if "rq_set[] = {" in x] + bl[k + 1:]
    rec["residue_identical"] = al == bl
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
    return (r["ENGINE"] == "vm" and r["VM_PREFILTER"] == "none" and
            r["REQ_WHY"] == "emitted" and r["window_full"] and
            not r["stamps_moved"] and (r["whole_len"] or 0) > 8 and
            r["residue_identical"])


def main():
    with ThreadPoolExecutor(max_workers=int(os.environ.get("PROCS", "4"))) as ex:
        res = list(ex.map(one, jobs()))
    json.dump(res, open(f"{SCR}/k66_census.json", "w"), indent=0)
    for pop in ("bench", "corpus"):
        rs = [r for r in res if r["pop"] == pop]
        print(f"== {pop}: {len(rs)} artifact-configs")
        print("  identity x cfg:", dict(collections.Counter((r["cfg"], r["identity"]) for r in rs)))
        ch = [r for r in rs if r["identity"] == "changed"]
        print(f"  changed: {len(ch)}; predicted {sum(predicted(r) for r in ch)}")
        for r in ch:
            tag = "predicted  " if predicted(r) else "UNPREDICTED"
            print(f"   {tag} {r['cfg']:10s} +{r['dlines']} whole={r['whole_len']} "
                  f"rq={r['rq_base']}->{r['rq_new']} frameless={r['VM_FRAMELESS']} "
                  f"start={r['VM_START']}  {r['key'][:60]!r}")
        # the converse: every artifact that can carry the whole run, did
        cand = [r for r in rs if r["identity"] == "identical" and
                r.get("ENGINE") == "vm" and r.get("VM_PREFILTER") == "none" and
                r.get("REQ_WHY") == "emitted" and r.get("window_full")]
        print(f"  full-window no-DFA emitted but identical (run exactly 8): {len(cand)}")
        for r in cand:
            print(f"   same    {r['cfg']:10s} {r['REQ_RUN']} {r['key'][:60]!r}")
        odd = [r for r in rs if r["identity"] in ("timeout", "refusal-mismatch")]
        for r in odd:
            print(f"   {r['identity'].upper()} {r['cfg']} {r['key'][:70]!r}")


if __name__ == "__main__":
    main()
