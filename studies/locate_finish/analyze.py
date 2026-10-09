#!/usr/bin/env python3
"""Summarize census.py's rows.tsv into the tables locate_finish.md cites.

    python3 studies/locate_finish/analyze.py studies/locate_finish/results/rows.tsv.gz \
        > studies/locate_finish/results/summary.txt

Every population is printed twice: ROWS (every bench pattern / corpus block)
and DISTINCT (corpus deduplicated on (pattern bytes, encoding, -i)); the bench
is already distinct.  The three controls run first and the script exits 1 if
any of them disagrees, so a summary is never printed over a broken census.
"""
import collections
import gzip
import sys

rows = []
with (gzip.open(sys.argv[1], "rt") if sys.argv[1].endswith(".gz") else open(sys.argv[1])) as fh:
    hdr = fh.readline().rstrip("\n").split("\t")
    for ln in fh:
        rows.append(dict(zip(hdr, ln.rstrip("\n").split("\t"))))


def kinds(r):
    return set(r["f_kinds"].split(",")) - {""}


def dkey(r):
    return (r["pattern_hex"], r["enc"], r["icase"])


def count(pop, pred):
    sel = [r for r in rows if r["pop"] == pop and pred(r)]
    return len(sel), len({dkey(r) for r in sel})


def show(title, pred):
    b, _ = count("bench", pred)
    c, cd = count("corpus", pred)
    print(f"  {title:<62} bench {b:>4}   corpus {c:>5} ({cd:>5} distinct)")


comp = [r for r in rows if r["ENGINE"]]
bad = 0

# ---- CONTROL C1: the stamp says the artifact carries a reverse pass; the TEXT
# says whether any `rx_reverse_` identifier is there.  Shares no source with the
# stamp writer (it reads the emitted C).
def stamp_rev(r):
    return r["DFA_SCAN"] == "unanchored" and r["DFA_START"] == "reverse-pass"

c1 = collections.Counter()
for r in comp:
    if r["t_ok"] != "ok":
        c1["text-refused"] += 1
        continue
    c1[(stamp_rev(r), r["t_rev"] == "1")] += 1
print("CONTROL C1  stamp(DFA_SCAN=unanchored & DFA_START=reverse-pass) vs text(any rx_reverse_ identifier)")
for k, v in sorted(c1.items(), key=str):
    print(f"  {k}: {v}")
dis1 = c1[(True, False)] + c1[(False, True)]
print(f"  disagreements: {dis1}")
bad += dis1 > 0

# ---- CONTROL C2: RX_VM_PREFILTER "hybrid" vs the inlined `rx_prefilter(` in the text.
c2 = collections.Counter()
for r in comp:
    if r["t_ok"] != "ok":
        continue
    c2[(r["VM_PREFILTER"] == "hybrid", r["t_pref"] == "1")] += 1
dis2 = c2[(True, False)] + c2[(False, True)]
print("CONTROL C2  stamp(VM_PREFILTER=hybrid) vs text(rx_prefilter( )")
for k, v in sorted(c2.items(), key=str):
    print(f"  {k}: {v}")
print(f"  disagreements: {dis2}")
bad += dis2 > 0

# ---- CONTROL C3: the borrowed probe's end pin vs the SHIPPED end_window fact.
# A numeric end_window means the shipped walk found every alternative pinned
# (and \G absent): the probe must say view 1/2 there.  (The converse is not a
# disagreement: end_window also needs a finite width.)
c3 = collections.Counter()
for r in comp:
    ew = r["f_end_window"]
    if ew and ew != "none":
        c3["fact-window, probe-pinned" if r["view"] in ("1", "2") else "fact-window, probe-NOT"] += 1
dis3 = c3["fact-window, probe-NOT"]
print("CONTROL C3  shipped end_window numeric => probe view in {$,\\z}")
for k, v in sorted(c3.items()):
    print(f"  {k}: {v}")
print(f"  disagreements: {dis3}")
bad += dis3 > 0
if bad:
    print("CONTROLS FAILED — no tables printed")
    sys.exit(1)

print()
print("POPULATION")
show("rows", lambda r: True)
show("compiled (ENGINE stamp present)", lambda r: bool(r["ENGINE"]))
show("refused or timed out", lambda r: not r["ENGINE"])

print()
print("T1  TODAY's (locator, finisher), every compiled artifact (locate_finish.md §3.1)")
pairs = collections.Counter((r["loc"], r["fin"]) for r in comp)
for (lo, fi) in sorted(pairs):
    show(f"{lo} x {fi}", lambda r, lo=lo, fi=fi: r["loc"] == lo and r["fin"] == fi)

print()
print("T2  hybrids by the inlined prefilter's own locator (does it carry reverse tables?)")
for lo in ("P-fwdrev", "P-pinned", "P-candloop", "P-empty"):
    show(f"{lo} (any language)", lambda r, lo=lo: r["loc"] == lo)
    show(f"{lo}  exact language (F-vm-span)", lambda r, lo=lo: r["loc"] == lo and r["fin"] == "F-vm-span")

EP = lambda r: r["endpin"] == "1" and bool(r["ENGINE"])
BND = lambda r: r["f_end_window"] not in ("", "none")

print()
print("T3  END-PINNED artifacts ($ / \\Z / \\z outside (?m), no \\G; the borrowed probe) by today's pair")
show("end-pinned, compiled", EP)
for (lo, fi) in sorted({(r["loc"], r["fin"]) for r in comp if EP(r)}):
    show(f"{lo} x {fi}", lambda r, lo=lo, fi=fi: EP(r) and r["loc"] == lo and r["fin"] == fi)
    show(f"   ... of which width-bounded (W1 serves today)",
         lambda r, lo=lo, fi=fi: EP(r) and r["loc"] == lo and r["fin"] == fi and BND(r))

print()
print("T4  STAGE 1 (rev-end x DFA finisher): end-pinned, DFA route, forward+reverse locator")
S1 = lambda r: EP(r) and r["loc"] in ("L-fwdrev",)
show("admitted (L-fwdrev)", S1)
show("   unbounded (class U)", lambda r: S1(r) and not BND(r))
show("   bounded (class B, W1 today)", lambda r: S1(r) and BND(r))
show("end-pinned on L-pinned (must be 0: P1 needs a PLAIN accept at s0)", lambda r: EP(r) and r["loc"] == "L-pinned")
show("end-pinned on L-candloop (R2 declines: no reverse machine)", lambda r: EP(r) and r["loc"] == "L-candloop")

print()
print("T5  STAGE 2 (rev-end x VM finisher): end-pinned hybrids whose prefilter carries reverse tables")
S2 = lambda r: EP(r) and r["loc"] == "P-fwdrev"
show("admitted (P-fwdrev)", S2)
show("   exact language (F-vm-span: window identity => NEUTRAL)", lambda r: S2(r) and r["fin"] == "F-vm-span")
show("   superset language (F-vm-cand: CAND + RETRY)", lambda r: S2(r) and r["fin"] == "F-vm-cand")
show("   unbounded", lambda r: S2(r) and not BND(r))
show("   bounded (W1 at the VM entry today)", lambda r: S2(r) and BND(r))
show("end-pinned hybrids on P-candloop (no reverse tables)", lambda r: EP(r) and r["loc"] == "P-candloop")

print()
print("T6  END-PINNED VM-ONLY artifacts (no prefilter): the relaxed-reverse population")
V = lambda r: EP(r) and r["fin"] == "F-vm-search"
show("end-pinned VM-only", V)
for k in ("bref", "linked_call", "var"):
    show(f"   kinds has {k}", lambda r, k=k: V(r) and k in kinds(r))
show("   none of bref/linked_call/var (other decline reason)",
     lambda r: V(r) and not (kinds(r) & {"bref", "linked_call", "var"}))
show("   start-anchored (one attempt; nothing to locate)", lambda r: V(r) and r["f_start_anchor"] != "unanchored")
show("   start-UNanchored (any kind)", lambda r: V(r) and r["f_start_anchor"] == "unanchored")
show("   start-UNanchored, bref, unbounded", lambda r: V(r) and r["f_start_anchor"] == "unanchored"
     and "bref" in kinds(r) and not BND(r))


def listing(title, pred):
    seen = {}
    for r in rows:
        if pred(r) and dkey(r) not in seen:
            seen[dkey(r)] = r
    print(f"  {title}: {len(seen)} distinct")
    for k in sorted(seen, key=lambda k: (seen[k]["pop"], seen[k]["id"])):
        r = seen[k]
        pat = bytes.fromhex(r["pattern_hex"])
        print(f"    {r['pop']:<6} {r['id']:<48} {r['enc']:<4} {r['fin']:<11} "
              f"ew={r['f_end_window']:<5} kinds={r['f_kinds'] or '-':<24} {pat[:56]!r}")


print()
print("T6a the distinct start-unanchored members of T5 and T6")
listing("stage 2 (P-fwdrev, end-pinned)", lambda r: S2(r) and r["f_start_anchor"] == "unanchored")
listing("VM-only end-pinned, start-unanchored", lambda r: V(r) and r["f_start_anchor"] == "unanchored")

print()
print("T7  bench members of the T4-T6 populations (start-unanchored only)")
for name, pred in (("stage 1", S1), ("stage 2", S2), ("VM-only", V)):
    ids = sorted(r["id"] for r in rows if r["pop"] == "bench" and pred(r)
                 and r["f_start_anchor"] == "unanchored")
    print(f"  {name}: {len(ids)}")
    for i in ids:
        print(f"    {i}")

print()
print("T8  D-2's population: RX_DFA_START \"reverse-pass\" with no reverse machine (ATTEMPT / empty locators)")
D2 = lambda r: bool(r["ENGINE"]) and r["DFA_START"] == "reverse-pass" and r["DFA_SCAN"] in ("attempt", "empty")
show("all", D2)
for eng in ("dfa", "vm"):
    for scan in ("attempt", "empty"):
        show(f"   {eng} / {scan}", lambda r, e=eng, s=scan: D2(r) and r["ENGINE"] == e and r["DFA_SCAN"] == s)
