#!/usr/bin/env python3
"""[DEC-FALLBACK] STEP 0: turn census_<variant>.tsv into markdown tables.
usage: summarize.py SCRATCH VARIANT... > results.md"""
import ast, collections, sys

scratch = sys.argv[1]
KEYS = ("ENGINE", "ENGINE_SEL", "UNROLL_K_WHY", "VM_PREFILTER", "VM_PREFILTER_WHY", "VM_PREFILTER_LANG_WHY")

def load(v):
    rows = []
    for l in open("%s/census_%s.tsv" % (scratch, v)):
        s, k, st, pr = l.rstrip("\n").split("\t")
        rows.append((s, ast.literal_eval(k), ast.literal_eval(st), ast.literal_eval(pr)))
    return rows

def transitions(pr):
    """one label per attempt AFTER the first: how the compile got there."""
    out, pend = [], None
    for p in pr:
        if p.startswith("att="):
            if pend is not None or out or False:
                pass
            continue
    # walk in order: fail -> (sel1|rung)? -> att
    evs, cur = [], None
    for p in pr:
        if p.startswith("fail"):
            cur = "size-term-trial-or-other-fail"
        elif p.startswith("sel1"):
            cur = "sel1:" + ("collapse" if "collapse=1" in p else "drop")
        elif p.startswith("rung="):
            cur = p[5:]
        elif p.startswith("att=") and cur is not None:
            evs.append(cur); cur = None
    return evs

def collapse_fate(r):
    """For each rung=prefilter-collapse: what the NEXT attempt's outcome says."""
    s, key, st, pr = r
    res = []
    for i, p in enumerate(pr):
        if p == "rung=prefilter-collapse":
            nxt = next((q for q in pr[i + 1:] if q.startswith("fail")), None)
            if nxt is None:
                res.append("next-ok:" + st.get("VM_PREFILTER_LANG", "?"))
            else:
                pc = nxt.split("pcoll=")[1].split()[0]
                res.append("next-refused:pcoll=" + pc)
    return res

def sel1_fate(r):
    """For each [SEL-1] collapse retry: the NEXT attempt's failure label (if any)."""
    s, key, st, pr = r
    res = []
    for i, p in enumerate(pr):
        if p.startswith("sel1 collapse=1"):
            nxt = next((q for q in pr[i + 1:] if q.startswith("fail")), None)
            res.append("next-ok:" + st.get("ENGINE_SEL", "?") if nxt is None else "next-failed:" + nxt[5:])
    return res

def table(counter, head):
    print("| %s | n |" % head); print("|---|---:|")
    for k, n in sorted(counter.items(), key=lambda x: (-x[1], str(x[0]))):
        print("| %s | %d |" % (k, n))
    print()

for v in sys.argv[2:]:
    rows = load(v)
    ok = [r for r in rows if r[0] == "ok"]
    print("## variant `%s` — %d cases, %d compiled, %d refused\n" % (v, len(rows), len(ok), len(rows) - len(ok)))
    print("### (ENGINE, ENGINE_SEL, UNROLL_K_WHY, VM_PREFILTER, VM_PREFILTER_WHY, VM_PREFILTER_LANG_WHY), compiled cases\n")
    c = collections.Counter(" / ".join(r[2].get(k, "-") for k in KEYS) for r in ok)
    table(c, "tuple")
    print("### ENGINE_SEL alone\n")
    table(collections.Counter((r[2].get("ENGINE", "-"), r[2].get("ENGINE_SEL", "-")) for r in ok), "(ENGINE, ENGINE_SEL)")
    print("### attempts per compile (all cases; 'refused' includes parse errors)\n")
    att = collections.Counter((r[0], sum(1 for p in r[3] if p.startswith("att="))) for r in rows)
    table(att, "(status, attempts)")
    print("### attempt-creating transitions, multi-attempt compiles (signature -> final ENGINE_SEL / status)\n")
    sig = collections.Counter()
    for r in rows:
        t = transitions(r[3])
        if t:
            sig[(" > ".join(t), r[0], r[2].get("ENGINE_SEL", "-"))] += 1
    table(sig, "transitions / status / final ENGINE_SEL")
    print("### size-cap collapse rung: fate of the attempt it bought (§4.1)\n")
    cf = collections.Counter()
    for r in rows:
        for f in collapse_fate(r):
            cf[(f, r[0])] += 1
    table(cf, "fate / compile status") if cf else print("(rung never taken)\n")
    sf = collections.Counter(f for r in rows for f in sel1_fate(r))
    print("### [SEL-1] collapse retry: fate of the attempt it bought\n")
    table(sf, "fate") if sf else print("(rung never taken)\n")
    tot = sum(a * n for (s, a), n in att.items())
    print("total attempts %d over %d compiles; attempts beyond the first: %d\n" % (tot, len(rows), tot - len(rows)))
