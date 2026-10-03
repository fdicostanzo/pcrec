#!/usr/bin/env python3
"""Renders c3_summary.txt from c3_census.tsv (read from the current dir).

Floor: one constant over the ranking key, sum popcount(K) >= FLOOR_BITS (16 =
two exact bytes, today's exact floor in bits). Every PROTO position is a byte
(K 0xFF, 8 bits) or a two-member cube (7 bits), so every run is scannable.
"""
import collections, sys
FLOOR_BITS = 16
rows = [l.rstrip("\n").split("\t") for l in open("c3_census.tsv")]
hdr, rows = rows[0], rows[1:]
H = {h: i for i, h in enumerate(hdr)}
def g(r, k): return r[H[k]]

def parse(v):
    if v in ("none", "-"): return None
    t, _, k = v.partition("/")
    tb = bytes.fromhex(t); kb = bytes.fromhex(k) if k else b"\xff" * len(tb)
    return tb, kb
def info(run): return sum(bin(x).count("1") for x in run[1])
def masked(run): return run is not None and any(x != 0xff for x in run[1])
def show(run):
    return "".join(chr(t) if 32 < t < 127 else "\\x%02x" % t for t in run[0]) + \
        ("/" + run[1].hex() if masked(run) else "")

C = collections.Counter(); ex = collections.defaultdict(list)
for r in rows:
    if g(r, "status") != "ok": continue
    pop = g(r, "pop"); pat = bytes.fromhex(g(r, "pattern_hex")).decode("latin-1")
    base = parse(g(r, "base_req_whole_run")); prot = parse(g(r, "proto_req_whole_run"))
    adm = prot is not None and info(prot) >= FLOOR_BITS
    cl = "-i" in g(r, "args") or "(?i" in pat
    C[(pop, "ok")] += 1
    if cl: C[(pop, "caseless")] += 1
    if base is None and not adm:
        C[(pop, "A0 none->none")] += 1
        if prot is not None: C[(pop, "A0b none->masked-below-floor")] += 1
    elif base is None and adm:
        C[(pop, "A1 none->masked (old additive movers)")] += 1
        if any(k == 0xdf for k in prot[1]): C[(pop, "A1 with a K=df position")] += 1
        if g(r, "base_req_byte") != "none": C[(pop, "A1 with a nonempty set (req_byte!=none: S2 class)")] += 1
        ex[(pop, "A1")].append((pat, show(prot), info(prot), g(r, "base_req_byte")))
    elif not masked(prot):
        if prot == base: C[(pop, "B exact->identical exact")] += 1
        else:
            C[(pop, "B! exact->DIFFERENT exact (identity claim broken)")] += 1
            ex[(pop, "B!")].append((pat, show(base), show(prot) if prot else None))
    else:
        C[(pop, "C exact->masked (NEW movers, single ranking)")] += 1
        if len(base[0]) == 2: C[(pop, "C base exact run is a 2-run")] += 1
        if cl: C[(pop, "C caseless")] += 1
        if cl and len(base[0]) == 2: C[(pop, "C caseless AND base 2-run (the C4 shadow count)")] += 1
        if not any(k == 0xdf for k in prot[1]): C[(pop, "C no K=df position (hull/non-letter pair only)")] += 1
        if base[0] in bytes(t for t in prot[0]) and False: pass
        if g(r, "base_run_pin") not in ("none", "-", ""): C[(pop, "C base run_pin != none (pin lost)")] += 1
        if "run" in g(r, "base_RX_DFA_PREFILTER"): C[(pop, "C base DFA_PREFILTER is a run row")] += 1
        C[(pop, "C base REQ_WHY=" + g(r, "base_RX_REQ_WHY"))] += 1
        ex[(pop, "C")].append((pat, show(base), show(prot), info(prot), g(r, "base_run_pin"), g(r, "base_RX_DFA_PREFILTER")))

out = []
for k in sorted(C): out.append("%-8s %-62s %5d" % (k[0], k[1], C[k]))
for key in sorted(ex):
    out.append("\n== examples %s %s (%d) ==" % (key[0], key[1], len(ex[key])))
    for e in ex[key][:60]: out.append("  " + " | ".join(str(x) for x in e))
open("c3_summary.txt", "w").write("\n".join(out) + "\n")
print("\n".join(out[:60]))
