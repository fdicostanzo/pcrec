#!/usr/bin/env python3
"""[MATCH-SPLIT] STEP-0 counts (docs/design/match_split_requirements.md section 6.4) over
survey.py's ms_rows.tsv.gz.  Every denominator is printed (K35).  Verbatim output: summary.txt.

    python3 analyze.py ms_rows.tsv.gz > summary.txt
"""
import collections, csv, gzip, sys

csv.field_size_limit(sys.maxsize)
C = collections.Counter
rows = list(csv.DictReader(gzip.open(sys.argv[1], "rt"), delimiter="\t"))
ORDER = ["S", "G", "LS", "E", "LE", "F"]


def pat(r):
    return bytes.fromhex(r["pattern_hex"]).decode("latin-1")


def sub(r):
    if r["pop"] == "corpus":
        return "corpus-d27" if r["adv"] == "True" else "corpus"
    return r["pop"]


def route(r):
    e, v, s = r["ENGINE"], r["VM_PREFILTER"], r["DFA_SCAN"]
    if e == "dfa":
        if s == "attempt":
            return "dfa-attempt[%s]" % (r["start_max"] or "?")
        return "dfa-" + s
    if v == "hybrid":
        if s == "attempt":
            return "hybrid-attempt[%s]" % (r["start_max"] or "?")
        return "hybrid-" + s
    return "vm-only"


def attempt_n(r):
    return r["start_max"] == "subject_length"


def pin_only(r):
    cl = r["mix"].split("+")
    return r["mix"] not in ("-",) and "F" not in cl and len(cl) >= 2


def hdr(t):
    print("\n" + "=" * 100 + "\n" + t + "\n" + "=" * 100)


def table(counter_rows, cols, rowlabels=None):
    w = max([len(str(x)) for x in rowlabels] + [8]) if rowlabels else 8
    print("%-*s " % (w, "") + " ".join("%12s" % c for c in cols))
    for lab in rowlabels:
        print("%-*s " % (w, lab) + " ".join("%12d" % counter_rows.get((lab, c), 0) for c in cols))


POPS = ["bench", "corpus", "corpus-d27", "catalog", "idioms", "planted"]
real = [r for r in rows if r["pop"] != "planted"]
ok = [r for r in real if r["status"] == "ok" and not r["refused"]]

hdr("0. DENOMINATORS (K35).  Source: build/ms/out/ms_rows.tsv.gz; ok = parsed by msprobe AND compiled by pcrec")
print("%-12s %7s %9s %9s %9s %9s %9s" % ("population", "rows", "probe-ref", "comp-ref", "ok", "byte", "utf8"))
for p in POPS:
    rs = [r for r in rows if sub(r) == p]
    pr = sum(r["status"] != "ok" for r in rs)
    cr = sum(r["status"] == "ok" and bool(r["refused"]) for r in rs)
    oo = [r for r in rs if r["status"] == "ok" and not r["refused"]]
    print("%-12s %7d %9d %9d %9d %9d %9d" % (p, len(rs), pr, cr, len(oo),
          sum(r["enc"] == "byte" for r in oo), sum(r["enc"] == "utf8" for r in oo)))
print("%-12s %7d %9d %9d %9d" % ("TOTAL(real)", len(real), sum(r["status"] != "ok" for r in real),
      sum(r["status"] == "ok" and bool(r["refused"]) for r in real), len(ok)))
print("\nrefusal reasons (pcrec's own diagnostics, first 60 bytes), all populations:")
for k, v in C(r["refused"][:70] for r in real if r["refused"]).most_common(10):
    print("  %5d  %s" % (v, k))
print("\nrecipe control: rows msprobe REFUSED to parse that pcrec's own compile ACCEPTED: %d (0 = the probe's parse recipe never rejects what the compiler takes)" % sum(
    1 for r in real if r["status"] != "ok" and not r["refused"]))
print("rows msprobe parsed that pcrec's compile then refused (size caps, module gates): %d" % sum(1 for r in real if r["status"] == "ok" and r["refused"]))
print("\nEvery table below counts the `ok` patterns of its population (the `ok` column above).")
print("corpus-d27 = composition_d27.rxt and the d27/ and matrix.rxt adversarial files, reported separately.")

hdr("1. (a) MIX LABEL per population  (classes among LIVE paths: S ^/\\A, G \\G, LS (?m)^ leading, E $ \\Z \\z, LE (?m)$ trailing, F free)")
labels = sorted({r["mix"] for r in ok}, key=lambda m: (-sum(1 for r in ok if r["mix"] == m), m))
cnt = C((r["mix"], sub(r)) for r in ok)
table(cnt, POPS[:5], labels)
print("%-8s " % "TOTAL" + " ".join("%12d" % sum(1 for r in ok if sub(r) == p) for p in POPS[:5]))
print("\nplanted (C4 witnesses, not a population):", len([r for r in rows if r["pop"] == "planted"]))

hdr("2. (a) MIX LABEL x TODAY'S ROUTE (all populations; route = ENGINE + VM_PREFILTER + DFA_SCAN [+ emitted start_max])")
routes = sorted({route(r) for r in ok})
cnt = C((r["mix"], route(r)) for r in ok)
rt = sorted(routes, key=lambda x: -sum(1 for r in ok if route(r) == x))
table(cnt, rt[:9], labels)
print("\n(route columns beyond the 9 largest:", ", ".join("%s=%d" % (x, sum(1 for r in ok if route(r) == x)) for x in rt[9:]), ")")
for p in POPS[:5]:
    sel = [r for r in ok if sub(r) == p]
    cnt = C((r["mix"], route(r)) for r in sel)
    labs = sorted({r["mix"] for r in sel}, key=lambda m: -sum(1 for r in sel if r["mix"] == m))
    rts = sorted({route(r) for r in sel}, key=lambda x: -sum(1 for r in sel if route(r) == x))[:8]
    print("\n-- %s (n=%d)" % (p, len(sel)))
    table(cnt, rts, labs[:14])

hdr("3. (b) THE PIN-ONLY POPULATION (no free arm; >= 2 classes): 4a is what opens next")
po = [r for r in ok if pin_only(r)]
print("pin-only patterns: %d of %d ok\n" % (len(po), len(ok)))
cnt = C((r["mix"], sub(r)) for r in po)
table(cnt, POPS[:5], sorted({r["mix"] for r in po}, key=lambda m: -sum(1 for r in po if r["mix"] == m)))
print("\nby today's route (all populations):")
cnt = C((r["mix"], route(r)) for r in po)
table(cnt, sorted({route(r) for r in po}, key=lambda x: -sum(1 for r in po if route(r) == x)),
      sorted({r["mix"] for r in po}, key=lambda m: -sum(1 for r in po if r["mix"] == m)))
print("\nthe S+E/LS+E/S+LE/LS+LE sub-population on the ATTEMPT route with start_max = subject_length (the gratuitous forward scan):")
core = [r for r in po if attempt_n(r)]
print("  %d of %d pin-only" % (len(core), len(po)))
print("\nEVERY pin-only pattern of bench, catalog, idioms (and corpus where <= 60):")
for p in ("bench", "catalog", "idioms", "corpus", "corpus-d27"):
    sel = [r for r in po if sub(r) == p]
    print("\n-- %s: %d pin-only" % (p, len(sel)))
    for r in sorted(sel, key=lambda r: (r["mix"], r["id"]))[: (60 if p.startswith("corpus") else 999)]:
        print("  %-7s %-24s %-52s %s" % (r["mix"], route(r), pat(r)[:52].replace("\n", "\\n"), r["id"][:48]))
print("\nK106's trim shape  ^\\s+|\\s+$  and the family around it (idioms + catalog + bench + corpus rows whose pattern text contains both a leading ^/(?m)^ arm and a trailing $ arm and no free arm):")
for r in po:
    if r["mix"] in ("S+E", "LS+E", "S+LE", "LS+LE") and sub(r) != "corpus-d27":
        if sub(r) == "corpus" and False:
            continue
print("  (see the per-population lists above; the idioms list carries the named shapes)")

hdr("4. (c) ATTEMPT with start_max = subject_length, split by mix  (OPT-ATTEMPT-SPLIT's own precondition)")
att = [r for r in ok if attempt_n(r)]
print("DFA or hybrid artifacts on the attempt route with start_max = subject_length: %d of %d ok" % (len(att), len(ok)))
print("  of which engine=dfa: %d, hybrid: %d" % (sum(r["ENGINE"] == "dfa" for r in att), sum(r["ENGINE"] == "vm" for r in att)))
print("  other attempt routes (start_max = 0 / search_from): %d" % sum(1 for r in ok if r["DFA_SCAN"] == "attempt" and not attempt_n(r)))
cnt = C((r["mix"], sub(r)) for r in att)
table(cnt, POPS[:5], sorted({r["mix"] for r in att}, key=lambda m: -sum(1 for r in att if r["mix"] == m)))
print("\nTOTAL %-6s" % "", " ".join("%12d" % sum(1 for r in att if sub(r) == p) for p in POPS[:5]))
vmonly = [r for r in ok if route(r) == "vm-only"]
print("\nVM-only route (own attempt loop; start_max not stamped): %d patterns, by mix:" % len(vmonly))
cnt = C((r["mix"], sub(r)) for r in vmonly)
table(cnt, POPS[:5], sorted({r["mix"] for r in vmonly}, key=lambda m: -sum(1 for r in vmonly if r["mix"] == m))[:12])

hdr("5. (d) QUADRATIC-RISK population: an END path whose first consuming atom sits in an unbounded repeat (lu_E), by route")
q = [r for r in ok if r["lu_E"] == "1"]
print("patterns with an E/LE path led by an unbounded repeat: %d of %d ok" % (len(q), len(ok)))
cnt = C((r["mix"], route(r)) for r in q)
table(cnt, sorted({route(r) for r in q}, key=lambda x: -sum(1 for r in q if route(r) == x)),
      sorted({r["mix"] for r in q}, key=lambda m: -sum(1 for r in q if r["mix"] == m)))
qa = [r for r in q if "attempt" in route(r) or route(r) == "vm-only"]
print("\nof those, on a route that tries each start (dfa/hybrid attempt, or VM-only): %d" % len(qa))
print("  and mixed with another class (not E-only, so NOT served by rev-end alone): %d" % sum(1 for r in qa if r["mix"] not in ("E", "LE")))
print("\nthe mixed ones, listed (bench, catalog, idioms, corpus non-D27):")
for r in sorted([r for r in qa if r["mix"] not in ("E", "LE") and sub(r) != "corpus-d27"], key=lambda r: (sub(r), r["mix"])):
    print("  %-10s %-7s %-24s %s" % (sub(r), r["mix"], route(r), pat(r)[:60].replace("\n", "\\n")))
print("\n(work counts on constructed subjects: qwork.py -> qwork.txt)")

hdr("6. (e) DENSITY GAIN: today's start-set (mass under the shipped byte prior) vs the FREE part's, byte encoding only")
dens = [r for r in ok if r["fr_ss_mass"] not in ("", None) and r["ss_mass"] not in ("", None) and r["enc"] == "byte"]
print("patterns with a pinned class AND a free part that compiled AND both start-sets known (byte): %d" % len(dens))
withfree = [r for r in ok if r["mix"] != "F" and "F" in r["mix"].split("+")]
print("  (mixed patterns with a free class: %d; of those the free text compiled: %d; free text unsupported/refused: %d)" % (
    len(withfree), sum(1 for r in withfree if r["fr_refused"] == "" and r["fr_ENGINE"]), sum(1 for r in withfree if not r["fr_ENGINE"])))
buckets = C()
for r in dens:
    a, b = int(r["ss_mass"]), int(r["fr_ss_mass"])
    ratio = (a / b) if b else float("inf")
    key = "free set EMPTY mass" if b == 0 else ">=10x narrower" if ratio >= 10 else ">=2x narrower" if ratio >= 2 else "within 2x" if ratio > 0.5 else "free is WIDER"
    buckets[(key, r["mix"])] += 1
labs = ["free set EMPTY mass", ">=10x narrower", ">=2x narrower", "within 2x", "free is WIDER"]
table(buckets, sorted({r["mix"] for r in dens}), labs)
print("\nroute change when the free part is compiled alone (whole -> free):")
ch = C((route(r), "%s/%s" % (r["fr_ENGINE"], ("attempt" if r["fr_DFA_SCAN"] == "attempt" else r["fr_DFA_SCAN"] or "-"))) for r in withfree if r["fr_ENGINE"])
for (a, b), v in ch.most_common(14):
    print("  %5d  %-26s -> %s" % (v, a, b))
print("\nfree part on the attempt loop still (start_max):", C(r["fr_start_max"] for r in withfree if r["fr_DFA_SCAN"] == "attempt"))
print("free part prefilter:", C(r["fr_DFA_PREFILTER"] for r in withfree if r["fr_ENGINE"]).most_common(6))
print("whole  part prefilter (same patterns):", C(r["DFA_PREFILTER"] for r in withfree if r["fr_ENGINE"]).most_common(6))

hdr("7. (g) THE DECLINE POPULATION (3.2), by the predicates available WITHOUT the primitive")
mixed_e = [r for r in ok if "F" in r["mix"].split("+") and ("E" in r["mix"].split("+") or "LE" in r["mix"].split("+"))]
print("E/LE + F patterns: %d" % len(mixed_e))
n1 = [r for r in mixed_e if not set(r["mix"].split("+")) & {"S", "G", "LS"} and route(r).split("[")[0] in ("dfa-unanchored", "hybrid-unanchored", "dfa-rev-end", "hybrid-rev-end")]
print("  N1 (route already the free class's own, no START class; the END arm adds only a per-call walk): %d" % len(n1))
ew = lambda r: r["en_end_window"] if r["en_end_window"] else r["f_end_window"]    # the END part's own fact
unb = [r for r in mixed_e if ew(r) == "none"]
print("  N2-candidates (E arm UNBOUNDED -> the END walk may not die near n; F class present => find-all re-walks): %d  [needs the primitive for stay_len]" % len(unb))
print("  END arm BOUNDED (the END part compiled alone has an end_window: walk <= a few bytes): %d" % sum(1 for r in mixed_e if ew(r) != "none"))
print("  N3 (E arm whose START is a landmark, e.g. `//.*$`) [counted here by: END part's end_window none and no E path led by an unbounded repeat]: %d" % sum(
    1 for r in mixed_e if ew(r) == "none" and r["lu_E"] != "1"))
print("  N4 short-call, N5 size-cap ladder: need the regime / the size term -- not countable compile-side; STATED.")
print("  S+F patterns (START + FREE; no END): %d  -- OPT-ATTEMPT-SPLIT's member" % sum(1 for r in ok if r["mix"] == "S+F"))
print("  S+F on attempt[subject_length]: %d" % sum(1 for r in ok if r["mix"] == "S+F" and attempt_n(r)))

hdr("8. FLAGS (section 6.2)")
print("dead anchored paths (dead>0):          %d  %s" % (sum(int(r["dead"] or 0) > 0 for r in ok), dict(C(sub(r) for r in ok if int(r["dead"] or 0) > 0))))
print("line anchor away from the edge (landmark, ml_landmark>0): %d" % sum(int(r["ml_landmark"] or 0) > 0 for r in ok))
print("anchors inside lookarounds (unclassified): %d  by kind %s" % (sum(bool(r["look_pin"]) for r in ok), C(k for r in ok for k in r["look_pin"].split(",") if k)))
print("\\K present on a pinned pattern (reported start != attempt start): %d of %d pinned" % (
    sum(int(r["kreset"] or 0) > 0 for r in ok if r["mix"] not in ("F", "-")), sum(1 for r in ok if r["mix"] not in ("F", "-"))))
print("backref/call/var present (unparse limited): %d" % sum(bool(r["ref"]) for r in ok))
red = [r for r in ok if r["red"] and r["red"] != "capped"]
print("redundant pin (structural; a LOWER BOUND -- pin-erased atom sequence equals a free path's):")
print("   ", C(x for r in red for x in r["red"].split(",") if x))
print("   patterns whose path enumeration exceeded the cap (redundancy unknown):", sum(r["red"] == "capped" for r in ok))
print("nullable by class (some live path of the class is the empty path):")
print("   ", C(x for r in ok for x in r["z_by_class"].split(",") if x))
print("both pins on one path (e.g. ^...$): %d of %d pinned" % (sum(r["both"] == "1" for r in ok), sum(1 for r in ok if r["mix"] not in ("F", "-"))))
print("no live path at all (mix '-'): %d" % sum(r["mix"] == "-" for r in ok), dict(C(sub(r) for r in ok if r["mix"] == "-")))
print("captures present (VM hat): %d" % sum(r["ENGINE"] == "vm" for r in ok if r["mix"] not in ("F", "-")), "of pinned")

hdr("9. CONTROLS")
print("C1 single-class agreement (plumbing; shares a source with the facts -- labelled so):")
dis = []
def c1(label, sel, pred, what):
    s = [r for r in ok if sel(r)]
    bad = [r for r in s if not pred(r)]
    print("  %-34s %5d rows, %4d disagree   [%s]" % (label, len(s), len(bad), what))
    dis.extend((label, r) for r in bad)
c1("S-only  start_anchor=anchored", lambda r: r["mix"] == "S", lambda r: r["f_start_anchor"] == "anchored", "shipped fact")
c1("S-only  attempt => start_max=0", lambda r: r["mix"] == "S" and r["DFA_SCAN"] == "attempt", lambda r: r["start_max"] == "0", "emitted start_max")
c1("G-only  start_anchor=gstart", lambda r: r["mix"] == "G", lambda r: r["f_start_anchor"] == "gstart", "shipped fact")
c1("G-only  attempt => start_max=search_from", lambda r: r["mix"] == "G" and r["DFA_SCAN"] == "attempt", lambda r: r["start_max"] == "search_from", "emitted start_max")
c1("E-only  end_pin derived (eol|z)", lambda r: r["mix"] == "E", lambda r: r["f_end_pin"] in ("eol", "z"), "shipped fact")
c1("E-only  shipped ew_walk copy view 1|2", lambda r: r["mix"] == "E", lambda r: r["view"] in ("1", "2"), "probe copy of ew_walk")
c1("LE-only end_pin declined, ew view 3", lambda r: r["mix"] == "LE", lambda r: r["f_end_pin"] == "none" and r["view"] == "3", "fact + probe copy")
c1("LS-only start_anchor=unanchored", lambda r: r["mix"] == "LS", lambda r: r["f_start_anchor"] == "unanchored", "shipped fact")
c1("F-only  start_anchor=unanchored", lambda r: r["mix"] == "F", lambda r: r["f_start_anchor"] == "unanchored", "shipped fact")
c1("F-only  end_pin none", lambda r: r["mix"] == "F", lambda r: r["f_end_pin"] == "none", "shipped fact")
c1("any mix with E: ew view != 0 <=> end_pin derived", lambda r: True, lambda r: (r["view"] in ("1", "2")) == (r["f_end_pin"] in ("eol", "z")), "probe copy vs fact, ALL ok rows")
print("\nC1 disagreements (listed, never hidden):")
for lab, r in dis[:60]:
    print("  %-40s %-7s %-26s %s" % (lab[:40], r["mix"], route(r), pat(r)[:60].replace("\n", "\\n")))
if len(dis) > 60:
    print("  ... %d more" % (len(dis) - 60))
print("\nC-RT unparse of the whole tree compiles to the same route (stamps + start_anchor + end_pin):")
print("  ", C(r["rt"] if not r["rt"].startswith("unparse") else r["rt"] for r in ok).most_common())
for r in ok:
    if r["rt"] == "differs":
        print("   differs:", pat(r)[:50], r["rt_diff"][:90])
print("\nC4 planted classes: run `c4check.py` (35 witnesses) and with --plant ml_edge / look_end (must be red); see report.")
print("\nC5 REACH: every mix label of the taxonomy and its population (ok rows; D27 separated):")
alllabels = ["S", "G", "LS", "E", "LE", "F", "S+G", "S+LS", "S+E", "S+LE", "S+F", "G+LS", "G+E", "G+F", "LS+E", "LS+LE", "LS+F", "E+LE", "E+F", "LE+F", "S+E+F", "LS+LE+F", "S+LS+E+F", "-"]
for lab in alllabels:
    n = sum(1 for r in ok if r["mix"] == lab)
    n27 = sum(1 for r in ok if r["mix"] == lab and sub(r) == "corpus-d27")
    nb = sum(1 for r in ok if r["mix"] == lab and r["pop"] in ("bench", "catalog", "idioms"))
    print("  %-10s %5d  (d27 %4d, bench+catalog+idioms %4d)%s" % (lab, n, n27, nb, "   <-- UNREACHED (empty)" if n == 0 else ""))
extra = sorted({r["mix"] for r in ok} - set(alllabels))
print("  labels present that the taxonomy list above did not name:", extra)
print("\nC6 the -o basename trap: not applicable -- no two artifacts are compared byte-wise; every comparison is on")
print("   stamp/fact VALUES from `--emit-facts`, and the one emitted-text read (`start_max`) is a single `-o -` compile.")
