#!/usr/bin/env python3
"""origsurvey: condition densities per R17-b ALPHA cell x subject (no clock).
usage: python3 -I survey.py SLOT25C_DIR DEFAULT_RXT"""
import re, sys, os
slot, rxt = sys.argv[1], sys.argv[2]
prior = {}
for ln in open(rxt):
    m = re.match(r'\s+row ([0-9a-f]{2}) (\d+)\s*$', ln)
    if m: prior[int(m.group(1), 16)] = int(m.group(2))
assert sum(prior.values()) == 1000000, sum(prior.values())
SUBJ = ["short", "prose64k", "digits64k", "prose1m", "mix64k"]
data = {s: open(f"{slot}/alpha/subj/{s}", "rb").read() for s in SUBJ}
def B(chars): return {ord(c) for c in chars}
AZ = B("abcdefghijklmnopqrstuvwxyz"); UP = B("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
DG = B("0123456789"); WORD = AZ | UP | DG | B("_")
NW = set(range(256)) - WORD
# cell -> (origin set, [(label, kind, spec)]); kind 'set' = byte set, 'bi' = (setA,setB) bigram,
# 'lit' = literal bytes, 'alt' = list of literals, 'bw' = word-edge handled specially.
CELLS = {
 "dig":     (DG, [("x (end byte)", "set", B("x")), ("[0-9]x (end bigram)", "bi", (DG, B("x")))]),
 "email":   (AZ, [("@ (inner)", "set", B("@")), (". (REQ_BYTE)", "set", B(".")), (".com (REQ_RUN, end)", "lit", b".com"),
                  ("[a-z]@[a-z] (inner trigram)", "tri", (AZ, B("@"), AZ))]),
 "word-eq": (AZ | UP | B("_"), [("= (end byte)", "set", B("=")), ("[A-Za-z_]= (end bigram)", "bi", (AZ | UP | B("_"), B("=")))]),
 "hex-run": (B("0123456789abcdef"), []),
 "bounded": (AZ, [("\\W (boundary far side)", "set", NW), ("[a-z]\\W (run exit bigram)", "bi", (AZ, NW))]),
 "dfa-hat": (B("fnt"), [("tr|fa|nu (2-byte prefix)", "alt", [b"tr", b"fa", b"nu"]),
                         ("true|false|null (whole)", "alt", [b"true", b"false", b"null"])]),
 "vm-hat":  (B("ab"), [("c (end byte, REQ_BYTE)", "set", B("c")), ("[ab]c (end bigram)", "bi", (B("ab"), B("c")))]),
 "vm-hat-1":(B("q"), [("d (end byte, REQ_BYTE)", "set", B("d")), ("q[bc] (start bigram)", "bi", (B("q"), B("bc")))]),
}
def ppm(c, n): return round(1e6 * c / n) if n else 0
def count(d, kind, spec):
    if kind == "set": return sum(1 for b in d if b in spec)
    if kind == "bi": a, b = spec; return sum(1 for i in range(len(d) - 1) if d[i] in a and d[i+1] in b)
    if kind == "tri": a, b, c = spec; return sum(1 for i in range(len(d) - 2) if d[i] in a and d[i+1] in b and d[i+2] in c)
    if kind == "lit": return len(re.findall(re.escape(spec), d))
    if kind == "alt": return len(re.findall(b"|".join(re.escape(x) for x in spec), d))
def runs(d, spec):
    """landings of a run-consuming scan: maximal runs of bytes in spec"""
    return len(re.findall(b"[" + b"".join(b"\\x%02x" % b for b in sorted(spec)) + b"]+", d))
def prior_of(kind, spec):
    if kind == "set": return sum(prior[b] for b in spec)
    if kind in ("bi", "tri"):
        p = 1.0
        for s in spec: p *= sum(prior[b] for b in s) / 1e6
        return round(p * 1e6)
    if kind == "alt":
        t = 0.0
        for lit in spec:
            q = 1.0
            for b in lit: q *= prior[b] / 1e6
            t += q
        return round(t * 1e6)
    return None
PAT = {"dig": rb"[0-9]+x", "email": rb"[a-z]+@[a-z]+\.com", "word-eq": rb"[A-Za-z_]+=", "hex-run": rb"[a-f0-9]+",
       "bounded": rb"[a-z]+\b", "dfa-hat": rb"\b(?:true|false|null)\b", "vm-hat": rb"[ab]+c", "vm-hat-1": rb"q[bc]+d"}
print("## subjects: bytes / prior-check")
for s in SUBJ: print(s, len(data[s]))
for cell, (O, conds) in CELLS.items():
    print(f"\n### {cell}  origin |S|={len(O)} prior_ppm={sum(prior[b] for b in O)}  pattern {PAT[cell].decode()}")
    print("matches(find-all):", {s: len(list(re.finditer(PAT[cell], data[s]))) for s in SUBJ})
    print(f"{'condition':34s} {'prior':>8s} " + " ".join(f"{s:>10s}" for s in SUBJ))
    print(f"{'ORIGIN S (hits ppm)':34s} {sum(prior[b] for b in O):8d} " + " ".join(f"{ppm(count(data[s],'set',O),len(data[s])):10d}" for s in SUBJ))
    print(f"{'ORIGIN S landings (maximal runs)':34s} {'':>8s} " + " ".join(f"{runs(data[s],O):10d}" for s in SUBJ))
    for lab, kind, spec in conds:
        p = prior_of(kind, spec)
        print(f"{lab:34s} {('' if p is None else p):>8} " + " ".join(f"{ppm(count(data[s],kind,spec),len(data[s])):10d}" for s in SUBJ))
        print(f"{'   landings (runs / occurrences)':34s} {'':>8s} " + " ".join(f"{(runs(data[s],spec) if kind=='set' else count(data[s],kind,spec)):10d}" for s in SUBJ))

# ---- section 2: per time.log row verdict (needs counts.txt, time.log beside this script) ----
here = os.path.dirname(os.path.abspath(__file__))
uses = {}
for ln in open(f"{here}/counts.txt"):
    f = ln.split(); kv = dict(x.split("=") for x in f[4:])
    uses[(f[0], f[1], f[2])] = int(kv["uses"])
rows = []
for ln in open(f"{here}/time.log"):
    f = ln.split()
    if len(f) == 10 and f[1] in ("off", "on"):
        rows.append((f[0], f[1], f[2], f[3], float(f[7]), f[9]))
def landings(cell, s):
    O, conds = CELLS[cell]; d = data[s]
    o = runs(d, O)
    cl = {}
    for lab, kind, spec in conds:
        if kind == "alt" and len(spec) > 1 and "whole" in lab: continue
        cl[lab] = runs(d, spec) if kind == "set" else count(d, kind, spec)
    return o, cl
def bratio(cell, s):
    O, conds = CELLS[cell]; d = data[s]; o = count(d, "set", O); best = 0
    for lab, kind, spec in conds:
        if kind == "alt" and "whole" in lab: continue
        c = count(d, kind, spec)
        if c: best = max(best, o / c)
    return best
print("\n## per row (layer off; on-layer verdict beside)")
print("cell subj mode  new-deny_ns  verdict(off/on)  uses  Sruns  best_cond:landings  ratio  class")
tot = {}; ons = {(r[0], r[2], r[3]): r for r in rows if r[1] == "on"}
for c, l, s, m, nd, v in rows:
    if l != "off": continue
    u = uses[(c, s, m)]; o, cl = landings(c, s)
    pos = {k: x for k, x in cl.items() if x > 0}
    if pos: bk = min(pos, key=pos.get); bv = pos[bk]; ratio = o / bv if bv else float("inf")
    else: bk, bv, ratio = "-", 0, 0.0
    if u == 0: cls = "GATED(site not reached)"
    elif m == "first" and u <= 10: cls = "ORIGIN-OK(first match within %d landings)" % u
    elif not conds_exist(c) if False else not CELLS[c][1]: cls = "ORIGIN-OK(no other necessary condition)"
    elif ratio >= 4: cls = "WRONG-ORIGIN"
    elif bratio(c, s) >= 4: cls = "BYTE-DENSITY-ONLY(landings ratio %.1f)" % ratio
    else: cls = "ORIGIN-OK(ratio<4)"
    on = ons[(c, s, m)][5]
    print(f"{c:9s} {s:9s} {m:5s} {nd:+12.1f}  {v}/{on}  {u}  {o}  {bk}:{bv}  {ratio:.1f}  {cls}")
    if v == "REGRESSION":
        k = cls.split("(")[0]; tot[k] = tot.get(k, 0) + nd; tot[("n", k)] = tot.get(("n", k), 0) + 1
print("\n## REGRESSION loss ns (off layer) by class:", {k: round(x, 1) for k, x in tot.items()})
print("## excluding prose1m rows:")
ex = {}
for c, l, s, m, nd, v in rows:
    if l != "off" or v != "REGRESSION" or s == "prose1m": continue
    u = uses[(c, s, m)]; o, cl = landings(c, s); pos = [x for x in cl.values() if x > 0]
    r = o / min(pos) if pos else 0
    k = ("GATED" if u == 0 else "SHORT" if (m == "first" and u <= 10) else "NOCOND" if not CELLS[c][1] else "WRONG" if r >= 4 else "BYTEONLY" if bratio(c, s) >= 4 else "OK")
    ex[k] = ex.get(k, 0) + nd; ex[("n", k)] = ex.get(("n", k), 0) + 1
print({k: round(x, 1) for k, x in ex.items()})
