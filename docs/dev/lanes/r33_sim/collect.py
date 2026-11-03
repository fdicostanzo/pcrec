#!/usr/bin/env python3
"""docs/dev/lanes/r33_sim/collect.py -- R-33's collector: TODAY's answer per search site, as compiled.

    python3 -I collect.py --probe BIN --tree TREE --bench BENCHDIR --out OUT.jsonl
                          [--sources corpus,bench,s588] [--skip N] [--limit N] [--jobs N]

BIN is build.sh's probe compiler (the traced pcrec with probe.c wrapping the kit's entries). Each
pattern is compiled ONCE per arm, `--features all -p rx` (job 588's and pick_588.py's flags), with
PCREC_MF_ROUTE_TRACE=1; its stderr is parsed here into one JSON line per (source, id, arm):

  sites[]   one per kit define/emit: probe.c's `R33` record (the stated facts; for a window site and
            each window-stating FUNC part, mf_wdecide's reply = today's stop, set, plan, path), plus
              trace  the kit's own MFTRACE selection records for that define (every `END` chosen row
                     by table, FDROUTE, WPATH), the records BEFORE the R33 line since the previous one
              deleg  pcrec's MFROUTED record right AFTER it (the delegated-site id: COVER, OFS, PF..)
  rate      a digest of the art's byte-rate table (the tables themselves go to OUT.rates.json)

Arms: every pattern its default compile (RTE); job 588's patterns also DEF
(`--memfn=no-window-search,no-window-skip`, measure_588.sh's flags_of). Sources: corpus = every distinct
.rxt pattern (scripts/emit_sweep.py's enumerate_corpus, its escapes); bench = every [[patterns]] file
of pcrec-bench/bench/*/subbench.toml (READ-ONLY; compiled with the same flags, no per-subbench encoding:
labelled in the report); s588 = kit_proof/measure/cells.tsv + s3_evidence/sample_588.tsv + pair_588.tsv.
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
import subprocess
import sys
import tomllib

DEF_FLAGS = ["--memfn=no-window-search,no-window-skip"]


def load_emit_sweep(tree):
    sys.path.insert(0, os.path.join(tree, "scripts"))
    import emit_sweep  # noqa: E402
    return emit_sweep


def src_corpus(tree, es, plain_bin):
    seen, out = set(), []
    for rel, kind, pat in es.enumerate_corpus(plain_bin, tree, 60):
        pat = bytes(pat)
        if pat in seen:
            continue
        seen.add(pat)
        out.append(("corpus", "c%05d" % len(out), pat, rel))
    return out


def src_bench(bench):
    out = []
    for sb in sorted(os.listdir(os.path.join(bench, "bench"))):
        toml = os.path.join(bench, "bench", sb, "subbench.toml")
        if not os.path.exists(toml):
            continue
        for p in tomllib.load(open(toml, "rb")).get("patterns", []):
            f = os.path.join(bench, "bench", sb, p["file"])
            if os.path.exists(f):
                out.append(("bench", "%s/%s" % (sb, p["name"]), open(f, "rb").read(), ",".join(p.get("tags", []))))
    return out


def src_588(tree, es):
    ev = os.path.join(tree, "docs/dev/lanes/s3_evidence")
    out = []
    for line in open(os.path.join(tree, "docs/design/kit_proof/measure/cells.tsv"), encoding="utf-8"):
        if line.strip() and not line.startswith("#"):
            cid, pat = line.rstrip("\n").split("\t")[:2]
            out.append(("s588", cid, pat.encode(), "§6 cell"))
    for fn in ("sample_588.tsv", "pair_588.tsv"):
        for line in open(os.path.join(ev, fn), encoding="utf-8"):
            if line.startswith("#") or not line.strip():
                continue
            f = line.rstrip("\n").split("\t")
            out.append(("s588", f[0], bytes(es.decode_escape(f[2])), f[1]))
    return out


def summarize(trace):
    """The kit's selections for one define: each END's chosen row by table (phase define/run)."""
    ends, fdroute, wpath = [], None, None
    for t in trace:
        f = t.split()
        kv = dict(x.split("=", 1) for x in f[2:] if "=" in x)
        if f[1] == "END" and kv.get("phase") in ("define", "run"):
            ends.append([kv.get("table"), kv.get("chosen")])
        elif f[1] == "FDROUTE":
            fdroute = kv.get("row")
        elif f[1] == "WPATH":
            wpath = {"path": kv.get("path"), "arm": kv.get("arm"), "fd": kv.get("fd")}
    return {"ends": ends, "fdroute": fdroute, "wpath": wpath}


def parse(stderr, rates):
    sites, pending, art_rate = [], [], {}
    for raw in stderr.decode("utf-8", "replace").splitlines():
        if raw.startswith("R33RATE "):
            head, _, tab = raw.partition(" rate=")
            art = int(head.split("art=")[1].split()[0])
            h = hashlib.sha256(tab.encode()).hexdigest()[:16]
            rates.setdefault(h, {"head": head, "rate": None if tab == "none" else [int(x) for x in tab.split(",")]})
            art_rate[art] = h
        elif raw.startswith("R33 "):
            s = json.loads(raw[4:])
            s["trace"] = summarize(pending)
            s["rate"] = art_rate.get(s["art"])
            pending = []
            sites.append(s)
        elif raw.startswith("MFTRACE ") and not raw.startswith("MFTRACE REACH"):
            pending.append(raw)
        elif raw.startswith("MFROUTED\t") or raw.startswith("MFPRESDROP\t"):
            f = raw.split("\t")
            if sites and "deleg" not in sites[-1] and f[0] == "MFROUTED":
                sites[-1]["deleg"] = f[1]
                sites[-1]["routed_row"] = f[3] if len(f) > 3 else "-"
            elif sites:
                sites[-1].setdefault("pres", []).append(f[1:])
    return sites


def run_one(task):
    probe, src, pid, pat, note, arm, flags = task
    env = dict(os.environ, PCREC_MF_ROUTE_TRACE="1")
    try:
        r = subprocess.run([probe, "--features", "all", "-p", "rx", *flags, "-o", "-", "--pattern", pat],
                           capture_output=True, timeout=120, env=env)
        rc, err = r.returncode, r.stderr
    except subprocess.TimeoutExpired:
        rc, err = "timeout", b""
    rates = {}
    sites = parse(err, rates)
    return {"src": src, "id": pid, "arm": arm, "note": note, "pat_hex": pat.hex(),
            "pat": pat.decode("latin-1"), "rc": rc, "sites": sites}, rates


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", required=True)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--bench", default="/home/pcrec/projects/pcrec-bench")
    ap.add_argument("--out", required=True)
    ap.add_argument("--sources", default="corpus,bench,s588")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--skip", type=int, default=0)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--count-only", action="store_true")
    a = ap.parse_args()
    es = load_emit_sweep(a.tree)
    plain = os.path.join(a.tree, "build/pcrec")
    items = []
    srcs = a.sources.split(",")
    if "s588" in srcs:
        items += src_588(a.tree, es)
    if "bench" in srcs:
        items += src_bench(a.bench)
    if "corpus" in srcs:
        items += src_corpus(a.tree, es, plain)
    items = items[a.skip:]
    if a.limit:
        items = items[:a.limit]
    tasks = []
    for src, pid, pat, note in items:
        tasks.append((a.probe, src, pid, pat, note, "RTE", []))
        if src == "s588":
            tasks.append((a.probe, src, pid, pat, note, "DEF", DEF_FLAGS))
    if a.count_only:
        print("compiles %d (patterns %d)" % (len(tasks), len(items)))
        return
    allrates, n = {}, 0
    with open(a.out, "w") as out, concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        for rec, rates in ex.map(run_one, tasks):
            allrates.update(rates)
            out.write(json.dumps(rec) + "\n")
            n += 1
            if n % 500 == 0:
                print("r33 collect: %d/%d" % (n, len(tasks)), flush=True)
    json.dump(allrates, open(a.out + ".rates.json", "w"))
    print("== r33 collect COMPLETE: %d compiles" % n, flush=True)


if __name__ == "__main__":
    main()
