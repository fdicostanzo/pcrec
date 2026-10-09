#!/usr/bin/env python3
"""Summarize census.py's rows.tsv into the tables locate_finish.md cites.

    python3 studies/locate_finish/analyze.py studies/locate_finish/results/rows.tsv.gz \
        > studies/locate_finish/results/summary.txt

Every population is printed twice: ROWS (every bench pattern / corpus block)
and DISTINCT (corpus deduplicated on (pattern bytes, encoding, -i)); the bench
is already distinct.  The four controls run first and the script exits 1 if
any of them disagrees, so a summary is never printed over a broken census.
"""
import collections
import gzip
import re
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

# ---- CONTROL C3: the borrowed probe's end pin vs the SHIPPED end_window fact,
# TWO-SIDED (panel LF-C10; the one-sided form let the converse go unread).
# The probe is a copy of src/facts/endwin.c's walk (the probe's own header
# says so), so this control is only as independent as that copy is; what it
# adds is the shipped fact's FULL decline list, read from endwin.c:
#   (1) cwmax unbounded   (2) multi-byte encoding   (3) \G anywhere
#   (4) multiline `$`     (+) not end-anchored (the walk itself)
# FORWARD  shipped end_window numeric => probe view in {$, \z}.
# CONVERSE probe pinned (view 1/2) AND probe cwmax finite => shipped numeric,
#   EXCEPT the declared exceptions below.  Each exception is classified from
#   a column that is NOT the shipped fact's own answer (the row's encoding,
#   the probe's gstart), in the order endwin.c tests them (encoding before
#   \G); the shipped decline reason (f_end_window_why) is then read ONLY to
#   confirm each declared exception is the reason the shipped fact gave.
#   (1) and (4) and `not end-anchored` cannot arise in the converse's premise
#   (finite cwmax, view 1/2 excludes ML=3 and none=0), so they are not
#   exceptions; a row declined for any of them is a disagreement.
#   A row outside the declared exceptions that the shipped fact declines is a
#   disagreement; so is a declared exception whose shipped reason differs.
PINNED = lambda r: r["view"] in ("1", "2")
FINITE = lambda r: r["cwmax"] != "-1"
DECL = (("multibyte", lambda r: r["enc"] == "utf8", "decline:enc-multibyte"),
        ("gstart",    lambda r: r["gstart"] == "1", "decline:gstart"))
c3f = collections.Counter()
for r in comp:
    ew = r["f_end_window"]
    if ew and ew != "none":
        c3f["fact-window, probe-pinned" if PINNED(r) else "fact-window, probe-NOT"] += 1
dis3f = c3f["fact-window, probe-NOT"]
print("CONTROL C3  forward: shipped end_window numeric => probe view in {$,\\z}")
for k, v in sorted(c3f.items()):
    print(f"  {k}: {v}")
print(f"  disagreements: {dis3f}")

# FORWARD-WIDTH  shipped end_window numeric => the shipped walk found a FINITE
# width, so the probe's cwmax must be finite too, EXCEPT where the pattern
# calls a group: the probe runs parse -> altcls -> discharge_atomic ->
# lower_enc and never the call expansion/callgraph the compiler runs before
# its facts (measured: pcrec_cwmax of an unexpanded A_CALL is unbounded), so
# it reads `^(a|b)\g<1>$` as unbounded where the shipped fact says 3.  The
# exception is classified from the PATTERN TEXT (a call spelling), not from
# either instrument's answer.
CALLRE = re.compile(rb"\(\?(?:&|P>|R\)|[+-]?[0-9]+\))|\\g[<']")
c3w = collections.Counter()
c3wx = []
for r in comp:
    ew = r["f_end_window"]
    if not (ew and ew != "none"):
        continue
    if FINITE(r):
        c3w["fact-window, probe cwmax finite"] += 1
    elif CALLRE.search(bytes.fromhex(r["pattern_hex"])):
        c3w["fact-window, probe cwmax unbounded, pattern calls a group (declared: probe never expands calls)"] += 1
        c3wx.append(r)
    else:
        c3w["fact-window, probe cwmax unbounded, NO call spelling"] += 1
print("CONTROL C3  forward-width: shipped end_window numeric => probe cwmax finite")
for k, v in sorted(c3w.items()):
    print(f"  {k}: {v}")
print(f"  declared exception probe-blind-calls: {len(c3wx)} rows, {len({dkey(r) for r in c3wx})} distinct; "
      f"by population {dict(sorted(collections.Counter(r['pop'] for r in c3wx).items()))}")
seen = []
for r in c3wx:
    pat = bytes.fromhex(r["pattern_hex"])
    if pat not in seen and len(seen) < 3:
        seen.append(pat)
for p in seen:
    print(f"    e.g. {p[:60]!r}")
dis3w = c3w["fact-window, probe cwmax unbounded, NO call spelling"]
print(f"  disagreements: {dis3w}")

c3c = collections.Counter()
c3x = collections.defaultdict(list)       # exception name -> rows
dis3c = []
for r in comp:
    if not (PINNED(r) and FINITE(r)):
        continue
    ew = r["f_end_window"]
    if ew and ew != "none":
        c3c["probe-pinned+finite, fact-window"] += 1
        continue
    exc = next((n for n, p, _ in DECL if p(r)), None)
    if exc is None:
        c3c["probe-pinned+finite, fact-declined, UNDECLARED"] += 1
        dis3c.append(r)
        continue
    want = next(w for n, _, w in DECL if n == exc)
    if r["f_end_window_why"] != want:
        c3c["probe-pinned+finite, fact-declined, declared " + exc + " but shipped reason differs"] += 1
        dis3c.append(r)
        continue
    c3c["probe-pinned+finite, fact-declined, declared exception " + exc] += 1
    c3x[exc].append(r)
print("CONTROL C3  converse: probe pinned (view 1/2) AND cwmax finite => shipped end_window numeric")
for k, v in sorted(c3c.items()):
    print(f"  {k}: {v}")
for n, _, w in DECL:
    rs = c3x[n]
    print(f"  declared exception {n} (shipped reason {w}): {len(rs)} rows, "
          f"{len({dkey(r) for r in rs})} distinct; by population "
          f"{dict(sorted(collections.Counter(r['pop'] for r in rs).items()))}")
    if not rs:
        print(f"    (zero hits: the exception is declared but nothing reaches it)")
    seen = []
    for r in rs:
        pat = bytes.fromhex(r["pattern_hex"])
        if pat not in seen and len(seen) < 3:
            seen.append(pat)
    for p in seen:
        print(f"    e.g. {p[:60]!r}")
for r in dis3c[:10]:
    print(f"    DISAGREES {r['pop']} {r['id']} enc={r['enc']} view={r['view']} cwmax={r['cwmax']} "
          f"gstart={r['gstart']} why={r['f_end_window_why']!r} {bytes.fromhex(r['pattern_hex'])[:60]!r}")
print(f"  disagreements: {len(dis3c)}")
bad += (dis3f > 0) + (dis3w > 0) + (len(dis3c) > 0)

# ---- CONTROL C4: the census's exact/superset classifier for hybrids (census.py
# classify(): RX_VM_PREFILTER_LANG == exact, kinds fact without atomic and
# lookaround => F-vm-span, else F-vm-cand) vs the INDEPENDENT stamp
# RX_VM_RESEED, which is "exact" iff the RETRY row `exact` fired, whose
# predicate is Vm.mrl_win = fit.prefilter && !atomic && !look && !collapsed
# (src/gen/emit_vm.c pcrec_vm_prefilter_window).  The stamp is written in the
# same gate as RX_VM_PREFILTER_LANG (emit_vm.c, after vm_plan_reseed) and the
# `exact` row is FIRST in the RETRY slot of cand_rows[] with deny mask 0
# (src/gen/emit_dfa.c), so an exact hybrid cannot stamp another row and a
# non-exact one cannot stamp `exact`: NO structural exception is declared.
# The classifier reads the lang stamp and the kinds fact; the reseed stamp is
# the retry-row selection's own output, a different consumer of the fit.
hyb = [r for r in comp if r["VM_PREFILTER"] == "hybrid"]
c4 = collections.Counter()
for r in hyb:
    c4[(r["fin"] == "F-vm-span", r["VM_RESEED"] == "exact")] += 1
print("CONTROL C4  census classifier (F-vm-span) vs stamp RX_VM_RESEED == \"exact\", every hybrid")
print("                                  reseed==exact   reseed!=exact")
for cl, nm in ((True, "classifier exact (F-vm-span)"), (False, "classifier superset (F-vm-cand)")):
    print(f"  {nm:<32} {c4[(cl, True)]:>12}   {c4[(cl, False)]:>12}")
dis4 = c4[(True, False)] + c4[(False, True)]
print(f"  superset rows by the stamp they carry: "
      f"{dict(sorted(collections.Counter(r['VM_RESEED'] for r in hyb if r['fin'] != 'F-vm-span').items()))}")
print(f"  hybrids by reason they are not exact (lang!=exact / atomic kind / lookaround kind): "
      f"{sum(r['VM_PREFILTER_LANG'] != 'exact' for r in hyb)} / "
      f"{sum('atomic' in kinds(r) for r in hyb)} / {sum('lookaround' in kinds(r) for r in hyb)}"
      f"  (kind-name spellings live: both > 0)")
nohyb = sum(1 for r in comp if r["VM_PREFILTER"] != "hybrid" and r["VM_RESEED"])
print(f"  hybrids with no RX_VM_RESEED stamp: {sum(1 for r in hyb if not r['VM_RESEED'])}; "
      f"non-hybrids carrying one: {nohyb}")
dis4 += nohyb + sum(1 for r in hyb if not r["VM_RESEED"])
print(f"  disagreements: {dis4}")
bad += dis4 > 0
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
