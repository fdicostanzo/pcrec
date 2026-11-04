#!/usr/bin/env python3
"""Dry-run census for pricing_bakeoff.md rev 1 §3.1 (lane bakeoff2).

COMPILE-ONLY, PUBLIC FLAGS ONLY (L-ROW and L-VALID are not built), default build
of main's build/pcrec, one sequential nice'd compile at a time under gnutimeout 30.
It exercises the rev 1 walk (B8): route-pair SEEDS, then deny flags of the PRICED
slots only (LOCATE, PRESENCE, FIRST/NEXT, RETRY, the two public kit denies);
RECOVER and FINISH are never walked (they follow the upstream choice).
Arm identity = sha256 of the emitted .c with its one `#include "<out>.h"` line
removed (every arm is written under the same output name).

The path label here is the STAMP set (a proxy: the trace build's CANDROW records
are the rev 1 label, B9); slot signatures are read off the stamps that differ.

usage: census_dry.py OUTDIR [N_RWQUEST] [N_RXT]
"""
import csv, hashlib, json, os, re, subprocess, sys, collections

P = "/home/pcrec/projects/pcrec"
PCREC = P + "/build/pcrec"
SALT = b"bakeoff2-dryrun-2026-10-31"
CAP = 64
# rev 1 §3.1: the deny walk runs from the DEFAULT route only; each route-pair seed adds its
# own default arm (the route stratum). FULL_ROUTE_WALK=1 walks under every seed (the cost probe).
FULL_ROUTE_WALK = os.environ.get("FULL_ROUTE_WALK") == "1"

SEEDS = [[], ["--engine=dfa"], ["--engine=vm"], ["-fno-prefilter"],
         ["--engine=vm", "-fprefilter"]]
# (slot, flag) for the priced slots; kit flags are joined into one --memfn= string
DENIES = [("LOCATE", "-fno-rev-end"), ("LOCATE", "memfn:no-window-search"),
          ("PRESENCE", "memfn:no-fd-pres-g1"), ("PRESENCE", "memfn:no-pres-set-lead"),
          ("PRESENCE", "memfn:no-fd-pres-pick"),
          ("NEXT", "-fno-run-prefilter"), ("NEXT", "-fno-offset-skip"),
          ("FIRST/NEXT", "-fno-req-handoff"), ("NEXT", "-fno-start-set"),
          ("RETRY", "-fno-hyb-reseed"),
          ("KIT", "memfn:no-fd-d1"), ("KIT", "memfn:no-window-skip")]
STAMP_SLOT = {"RX_DFA_SCAN": "LOCATE", "RX_REQ_WHY": "PRESENCE",
              "RX_REQ_HANDOFF": "FIRST", "RX_DFA_PREFILTER": "NEXT",
              "RX_DFA_PREFILTER_OFFSETS": "NEXT", "RX_VM_START_SCAN": "NEXT",
              "RX_VM_RESEED": "RETRY", "RX_ENGINE": "ROUTE",
              "RX_VM_PREFILTER": "ROUTE", "RX_DFA_START": "RECOVER(dep)",
              "RX_DFA_MATCH": "FINISH(dep)"}
NO_DENY_NEXT = {"memchr", "memchr-bounded", "byte-class", "byte-class-bounded"}

def h(s):
    return hashlib.sha256(SALT + s.encode("utf-8", "surrogateescape")).hexdigest()

def argv_for(base, denies):
    plain = [d for d in denies if not d.startswith("memfn:")]
    kit = [d[6:] for d in denies if d.startswith("memfn:")]
    a = list(base) + plain
    if kit:
        a.append("--memfn=" + ",".join(kit))
    return a

NCOMP = [0]
def compile_(out, pat, popts, extra):
    NCOMP[0] += 1
    o = os.path.join(out, "arm.c")
    for f in (o, o[:-2] + ".h"):
        if os.path.exists(f):
            os.unlink(f)
    argv = ["gnutimeout", "30", "nice", PCREC, "-p", "rx", "--features", "all",
            "-o", o] + popts + extra + ["--pattern", pat]
    p = subprocess.run(argv, capture_output=True)
    if p.returncode != 0:
        return None
    c = open(o, "rb").read().splitlines()
    body = [l for l in c if not l.startswith(b'#include "arm.h"')]
    stamps = {}
    for l in open(o[:-2] + ".h", "rb").read().splitlines() + c:
        m = re.match(rb'#define (RX_[A-Z_]+) "(.*)"$', l)
        if m and m.group(1).decode() in STAMP_SLOT:
            stamps[m.group(1).decode()] = m.group(2).decode()
    return hashlib.sha256(b"\n".join(body)).hexdigest()[:16], stamps

def walk(out, pat, popts):
    """Per seed, a breadth-first walk over deny sets. A child d|{f} whose bytes
    equal its parent's marks f INERT for that parent's subtree (a deny that moved
    nothing is not retried below it); only a child with NEW bytes is expanded.
    The cap is CAP compiles per pattern (CHOSEN), shared across the seeds in seed
    order; a pattern that reaches it is counted as truncated."""
    arms = {}            # sha -> dict(stamps, how=[argv...])
    ncomp = 0; trunc = False; refused_seeds = 0
    for seed in SEEDS:
        if ncomp >= CAP:
            trunc = True; break
        r = compile_(out, pat, popts, argv_for(seed, [])); ncomp += 1
        if r is None:
            refused_seeds += 1
            continue
        sha, st = r
        if sha in arms and seed:
            arms[sha]["how"].append(argv_for(seed, []))
            continue                     # the seed reproduces an arm already walked
        arms.setdefault(sha, dict(stamps=st, how=[], route=bool(seed)))["how"].append(argv_for(seed, []))
        if seed and not FULL_ROUTE_WALK:
            continue                     # a route seed contributes its own default arm only
        q = [(frozenset(), sha, frozenset())]; seen = {frozenset()}
        while q and not trunc:
            d, psha, inert = q.pop(0)
            kids = []; inert_here = set()
            for _, fl in DENIES:
                if fl in d or fl in inert:
                    continue
                nd = d | {fl}
                if nd in seen:
                    continue
                seen.add(nd)
                if ncomp >= CAP:
                    trunc = True; break
                r = compile_(out, pat, popts, argv_for(seed, sorted(nd))); ncomp += 1
                if r is None:
                    continue
                csha, cst = r
                if csha == psha:
                    inert_here.add(fl); continue
                new = csha not in arms
                arms.setdefault(csha, dict(stamps=cst, how=[], route=bool(seed)))["how"].append(argv_for(seed, sorted(nd)))
                if new:
                    kids.append((nd, csha))
            for nd, csha in kids:
                q.append((nd, csha, inert | frozenset(inert_here)))
        if trunc:
            break
    return arms, ncomp, trunc, refused_seeds

def popts_for(flags):
    po = []; prefix = ""
    for f in [] if flags in ("-", "") else flags.split(","):
        if f == "i": po.append("-i")
        elif f == "m": prefix += "(?m)"
        elif f == "s": prefix += "(?s)"
        elif f == "utf": po += ["-e", "utf8"]
        elif f == "ucp": po.append("--ucp")
    return po, prefix

def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    nrw = int(sys.argv[2]) if len(sys.argv) > 2 else 177
    nrx = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    pats = []
    rq = list(csv.DictReader(open(P + "/docs/dev/lanes/rwquest/questions.tsv", encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE))
    rq.sort(key=lambda r: h(r["id"]))
    for r in rq[:nrw]:
        po, pre = popts_for(r["flags"])
        pats.append(("rwquest", r["id"], r["class"], pre + r["pattern"], po))
    files = []
    for d, _, fs in os.walk(P + "/tests"):
        for fn in fs:
            if fn.endswith(".rxt"):
                files.append(os.path.join(d, fn))
    rx = []
    for f in sorted(files, key=lambda f: h(os.path.relpath(f, P)))[:40]:
        so = subprocess.run(["gnutimeout", "30", "nice", PCREC, "--list-source", f],
                            capture_output=True).stdout.decode("utf-8", "surrogateescape")
        for line in so.splitlines():
            x = line.split("\t")
            if len(x) >= 5 and x[0] == "pattern" and "\n" not in x[4]:
                rx.append((os.path.relpath(f, P), x[4]))
    rx = sorted(set(rx), key=lambda t: h(t[1]))[:nrx]
    for f, p in rx:
        pats.append(("rxt", f, "-", p, []))
    rows = []
    with open(os.path.join(out, "census.jsonl"), "w") as js:
        for src, pid, cls, pat, po in pats:
            arms, ncomp, trunc, ref = walk(out, pat, po)
            keys = set()
            for a in arms.values():
                keys |= set(a["stamps"])
            differ = sorted({STAMP_SLOT[k] for k in keys
                             if len({a["stamps"].get(k) for a in arms.values()}) > 1})
            dflt = [a for a in arms.values() if not a["route"]]
            differ_default = sorted({STAMP_SLOT[k] for k in keys
                                     if len({a["stamps"].get(k) for a in dflt}) > 1})
            unl = len(arms) > 1 and not differ
            nosearch_blocked = any(a["stamps"].get("RX_DFA_PREFILTER") in NO_DENY_NEXT for a in arms.values())
            vm_exact = any(a["stamps"].get("RX_VM_RESEED") in ("exact", "clamped") for a in arms.values())
            rec = dict(src=src, id=pid, cls=cls, pattern=pat, narms=len(arms), ncomp=ncomp,
                       trunc=trunc, refused=ref == len(SEEDS), differ=differ, differ_default=differ_default, unlabelled=unl,
                       nosearch_needs_lrow=nosearch_blocked, retry_contract_row=vm_exact,
                       nroute=sum(a["route"] for a in arms.values()),
                       arms=[dict(sha=s, stamps=a["stamps"], how=a["how"][0], route=a["route"]) for s, a in arms.items()])
            js.write(json.dumps(rec) + "\n"); js.flush()
            rows.append(rec)
    summarize(out, rows)

def q(v, f):
    v = sorted(v)
    return v[min(len(v) - 1, int(f * len(v)))] if v else 0

def summarize(out, rows):
    L = []
    for src in ("rwquest", "rxt", "all"):
        rs = [r for r in rows if src == "all" or r["src"] == src]
        comp = [r for r in rs if not r["refused"]]
        qual = [r for r in comp if r["narms"] >= 2]
        na = [r["narms"] for r in qual]
        L.append(f"{src}: patterns {len(rs)}, compile {len(comp)}, refused {len(rs)-len(comp)}, "
                 f"QUALIFY (>=2 byte-distinct arms) {len(qual)} ({100*len(qual)/max(1,len(comp)):.0f}% of compiling); "
                 f"arms per qualifying site median {q(na,.5)} p90 {q(na,.9)} max {max(na) if na else 0}; "
                 f"total arms {sum(na)} (of them route-seed arms {sum(r['nroute'] for r in qual)}; "
                 f"default-route arms per site median {q([r['narms']-r['nroute'] for r in qual],.5)} "
                 f"p90 {q([r['narms']-r['nroute'] for r in qual],.9)}); qualifying on the default route alone "
                 f"{sum(1 for r in qual if r['narms']-r['nroute']>=2)}; truncated at cap {sum(r['trunc'] for r in rs)}; "
                 f"compiles {sum(r['ncomp'] for r in rs)}")
        sig = collections.Counter("+".join(r["differ"]) if r["differ"] else "(bytes only)" for r in qual)
        L.append(f"  differing-slot signatures: " + "; ".join(f"{k} {v}" for k, v in sig.most_common()))
        sigd = collections.Counter("+".join(r["differ_default"]) if r["differ_default"] else "(bytes only)"
                                   for r in qual if r["narms"] - r["nroute"] >= 2)
        L.append(f"  default-route signatures: " + "; ".join(f"{k} {v}" for k, v in sigd.most_common()))
        slot = collections.Counter(s for r in qual for s in r["differ"])
        L.append(f"  sites with a difference in slot: " + "; ".join(f"{k} {v}" for k, v in slot.most_common()))
        L.append(f"  sites with an arm on a no-deny NEXT row (no-search unreachable without L-ROW): "
                 f"{sum(r['nosearch_needs_lrow'] for r in comp)}; with RETRY exact/clamped (L-ROW must refuse): "
                 f"{sum(r['retry_contract_row'] for r in comp)}")
        if src == "rwquest":
            byc = collections.Counter(r["cls"] for r in qual)
            L.append("  qualifying by class: " + "; ".join(f"{k} {v}" for k, v in sorted(byc.items())))
    L.append(f"TOTAL compiles {NCOMP[0]}")
    open(os.path.join(out, "summary.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))

if __name__ == "__main__":
    main()
