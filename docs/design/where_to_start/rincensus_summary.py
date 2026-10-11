#!/usr/bin/env python3
"""Reads rincensus.py's rows and writes the census tables (rincensus_summary.txt).  No pcrec run, no clock.

    rincensus_summary.py ROWS.tsv.gz WALKSURVEY_RESULTS_DIR > OUT.txt

Weights (bench only): walk_survey's K12 formula applied to ANY pattern -- est ms = sum over default-config
cells of bench_ns * m_gap / T, K1-owned cells excluded -- an UPPER estimate (uniform per-byte cost; m_gap is the
forward machine's bytes stepped before each match start).  Control: the same function over walk_survey's own K12
patterns must give its 15.786 ms; this script asserts it.
"""
import collections, csv, gzip, importlib.util, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("PCREC", "build/pcrec"); os.environ.setdefault("CORPUS", "."); os.environ.setdefault("BENCH", "")
os.environ.setdefault("OUT", "build/rc")
_spec = importlib.util.spec_from_file_location("rincensus", os.path.join(HERE, "rincensus.py"))
RC = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(RC)

ROWS, WSDIR = sys.argv[1], sys.argv[2]
rows = list(csv.DictReader(gzip.open(ROWS, "rt"), delimiter="\t"))
W, CELLS = RC.weights(WSDIR)
k12 = [r["pid"] for r in csv.DictReader(open(os.path.join(WSDIR, "k12_bench.tsv")), delimiter="\t") if r["k12"] == "1"]
ctl = sum(W.get(p, 0) for p in k12)
assert abs(ctl - 15.786) < 0.01, ctl
OUTL = []


def P(*a):
    OUTL.append(" ".join(str(x) for x in a))


def family(r):
    if r["pop"] == "bench":
        return r["id"].split("/")[0]
    if r["pop"] == "corpus":
        parts = r["id"].split("/")
        return "tests/" + parts[1] if len(parts) > 2 else r["id"].split(":")[0]
    return "catalog"


def is_ipv6_sfx(r):
    return r["id"] == "loglines/ipv6" or r["id"].startswith("altwide/sfx-")


def elig(r, v, F):
    return r.get("stage_" + v) == "ok" and float(r.get("ratio_" + v) or 0) >= F


def done_by_end(r):
    """SERVED: the start is already recovered exactly without a reverse-pass search (REVEND / START-LANDING rows)."""
    return r.get("dfa_scan") == "rev-end" or r.get("dfa_start") in ("end-minus-width", "landing")


def keyed(r):
    """KEYED: today's forward scan is already an EXACT row at the landmark's offset (offset-set / run-pinned), the rows
    above rev-inner in where_to_start.md's table; reverse-inner would add nothing there."""
    return r.get("dfa_pf", "").startswith(("offset-set", "run-pinned"))


def live_row(r):
    return not done_by_end(r) and not keyed(r)


POPS = ["bench", "corpus", "catalog"]
VNAME = {"max_peel": "STRICT (maximal literal runs, mandatory group repeats peeled)",
         "max": "strict, no peeling", "sub_peel": "GENEROUS (common L may be any contiguous sub-run, peeled)",
         "sub": "generous, no peeling"}
P("rincensus_summary: provenance rows=%s; weights control: walk_survey K12 total %.3f ms (24 patterns) reproduced" % (ROWS, ctl))
P()
P("Readings of `ONE common L`: STRICT = L is a maximal literal run of the flattened spine and the SAME run in every branch;")
P("GENEROUS = L may be any contiguous sub-run of the branches' maximal runs (altwide/sfx-* needs this: its `ing` is the tail of each")
P("branch's whole-word literal).  `peel` splices the first iteration of a mandatory single-alternative group repeat")
P("(loglines/ipv6 needs this: `(?:H:){4,7}` = `H:(?:H:){3,6}`).  `pair` = the ruled text (every branch passes G2 with its own P_i);")
P("`comp` = pair AND the branches compose (all strong arms disj/ffree/empty, or all fixed at the SAME width; rincensus_report.md section 2).")
P()


def routeof(pop, route):
    return [r for r in rows if r["pop"] == pop and r.get("route") == route]


def count(pop, vv, F, comp=False, outside=False, live=0, route="dfa"):
    n = 0
    for r in routeof(pop, route):
        if not elig(r, vv, F):
            continue
        if comp and r["comp_" + vv] != "1":
            continue
        if outside and is_ipv6_sfx(r):
            continue
        if live == 1 and done_by_end(r):
            continue
        if live == 2 and not live_row(r):
            continue
        n += 1
    return n


P("## 1. The funnel (DFA route, STRICT reading; cumulative: a pattern counts at a stage if its best candidate reached it)")
P()
hdr = ["population", "patterns", "compiled", "parsed", "DFA route", "unanchored", "landmark", "common L", "P non-empty", "G1", "G2", "G3 F=1", "G3 F=2", "G3 F=8"]
P("| " + " | ".join(hdr) + " |"); P("|" + "---|" * len(hdr))
v = "max_peel"
for pop in POPS:
    R = [r for r in rows if r["pop"] == pop]
    comp = [r for r in R if r["outcome"] != "refused"]
    parsed = [r for r in comp if r["outcome"] != "unparsed"]
    dfa = [r for r in parsed if r["route"] == "dfa"]
    un = [r for r in dfa if r["outcome"] != "anchored"]
    st = lambda r: r.get("stage_" + v, "")
    lm = [r for r in un if st(r) not in ("no-landmark", "")]
    cl = [r for r in lm if st(r) != "no-common-L"]
    pn = [r for r in cl if st(r) != "P-empty"]
    g1 = [r for r in pn if st(r) in ("G2", "ok")]
    g2 = [r for r in g1 if st(r) == "ok"]
    P("| %s | %d | %d | %d | %d | %d | %d | %d | %d | %d | %d | %d | %d | %d |" % (
        pop, len(R), len(comp), len(parsed), len(dfa), len(un), len(lm), len(cl), len(pn), len(g1), len(g2),
        sum(elig(r, v, 1) for r in un), sum(elig(r, v, 2) for r in un), sum(elig(r, v, 8) for r in un)))
P()
P("unparsed by reason (all routes): " + "; ".join(
    "%s: %s" % (pop, dict(collections.Counter(r.get("why", "") for r in rows if r["pop"] == pop and r["outcome"] == "unparsed")))
    for pop in POPS))
P("`refused` = pcrec itself refuses the pattern (not compiled under --features all).")
P()
P("## 2. ELIGIBLE counts, DFA route (the decision tables)")
P("pair = the ruled text; comp = pair AND composition-safe.  `outside` = excluding loglines/ipv6 and altwide/sfx-*.")
P("`not served` = also excluding patterns whose start is already exact without a reverse search (RX_DFA_SCAN rev-end, RX_DFA_START")
P("end-minus-width / landing).  `live` = also excluding patterns whose forward scan is already an EXACT row at the landmark (offset-set /")
P("run-pinned): reverse-inner has nothing to add there.  G3 at F = 1 and F = 2 (F = 8 last column, live outside only).")
P()
for F in (2, 1):
    P("### F = %d" % F)
    P()
    P("| population | reading | eligible pair / comp | outside | outside, not served | outside, LIVE | LIVE at F=8 |")
    P("|---|---|---|---|---|---|---|")
    for pop in POPS:
        for vv in ("max", "max_peel", "sub", "sub_peel"):
            P("| %s | %s | %d / %d | %d | %d | %d | %d |" % (
                pop, vv, count(pop, vv, F), count(pop, vv, F, comp=True), count(pop, vv, F, outside=True),
                count(pop, vv, F, outside=True, live=1), count(pop, vv, F, outside=True, live=2), count(pop, vv, 8, outside=True, live=2)))
    P()
# the generous reading must contain the strict one (control)
for pop in POPS:
    a = {r["id"] for r in routeof(pop, "dfa") if elig(r, "max_peel", 2)}
    b = {r["id"] for r in routeof(pop, "dfa") if elig(r, "sub_peel", 2)}
    assert a <= b, (pop, sorted(a - b)[:5])
P()
P("control: STRICT eligible set is a subset of GENEROUS for every population (asserted).")
P()


def detail(v):
    P("## DETAIL for the %s reading (variant %s), DFA route" % (VNAME[v], v))
    P()
    P("### by arm, F = 2 (F = 1 in brackets); arm = first-match arm admitting the pattern (fixed, disj, ffree; several branches: the weakest any branch needs)")
    P("`ffree needed` = the pattern is composition-safe only through the factor-free arm (single branch: the sole arm; several branches: no all-disj and no equal-fixed-width composition exists): it exists only because of D151 add. 5.")
    P()
    P("| population | eligible | fixed | disj | ffree first-match | ffree needed | single branch | several branches | equal P_i | mixed P_i | comp-safe |")
    P("|---|---|---|---|---|---|---|---|---|---|---|")
    for pop in POPS:
        E = [r for r in routeof(pop, "dfa") if elig(r, v, 2)]
        E1 = [r for r in routeof(pop, "dfa") if elig(r, v, 1)]
        arm = collections.Counter(r["arm_" + v] for r in E)
        only = [r for r in E if r["nff_" + v] == "1"]
        P("| %s | %d (%d) | %d | %d | %d | %d | %d | %d | %d | %d | %d |" % (
            pop, len(E), len(E1), arm["fixed"], arm["disj"], arm["ffree"], len(only),
            sum(int(r["nbr_" + v]) == 1 for r in E), sum(int(r["nbr_" + v]) > 1 for r in E),
            sum(r["uniform_" + v] == "1" for r in E), sum(r["uniform_" + v] == "0" for r in E), sum(r["comp_" + v] == "1" for r in E)))
    P()
    P("### by family (DFA route, F = 2, not served by rev-end/landing in brackets)")
    for pop in POPS:
        E = [r for r in routeof(pop, "dfa") if elig(r, v, 2)]
        fam = collections.Counter(family(r) for r in E)
        famlive = collections.Counter(family(r) for r in E if not done_by_end(r))
        P("%s: %d eligible; " % (pop, len(E)) + ", ".join("%s %d (%d)" % (k, n, famlive[k]) for k, n in sorted(fam.items(), key=lambda kv: -kv[1])))
    P()
    P("### OUTSIDE loglines/ipv6 and altwide/sfx-* (every one listed for bench and catalog; corpus by family)")
    P()
    P("(F = 1 list: every bench pattern eligible at F >= 1, ratio shown; ratio < 2 rows are F=1-only)")
    P("| id | L | ratio | arm | arms | br | comp | served | keyed | LIVE | dfa_scan / dfa_start / prefilter / handoff | weight ms |"); P("|---|---|---|---|---|---|---|---|---|---|---|---|")
    bl = sorted([r for r in routeof("bench", "dfa") if elig(r, v, 1) and not is_ipv6_sfx(r)], key=lambda r: -W.get(r["id"], 0))
    for r in bl:
        if W.get(r["id"], 0) < 0.0005 and float(r["ratio_" + v]) < 2:
            continue                                  # F = 1-only rows with no measured weight: counted in the tables, not listed
        P("| %s | `%s` | %s | %s | %s | %s | %s | %s | %s | %s | %s / %s / %s / %s | %.4f |" % (
            r["id"], r["L_" + v], r["ratio_" + v], r["arm_" + v], r["arms_all_" + v], r["nbr_" + v], r["comp_" + v],
            "y" if done_by_end(r) else "n", "y" if keyed(r) else "n", "**y**" if live_row(r) else "n",
            r["dfa_scan"], r["dfa_start"], r["dfa_pf"], r["handoff"], W.get(r["id"], 0)))
    P()
    P("catalog (realistic_patterns.txt), eligible at F >= 1:")
    for r in sorted([r for r in routeof("catalog", "dfa") if elig(r, v, 1)], key=lambda r: r["id"]):
        P("  %s L=`%s` ratio %s arm %s (%s) served=%s keyed=%s LIVE=%s" % (r["id"], r["L_" + v], r["ratio_" + v], r["arm_" + v], r["arms_all_" + v],
                                                                         done_by_end(r), keyed(r), live_row(r)))
    P()
    for F in (2, 1):
        P("corpus, eligible at F = %d, LIVE, by family: " % F + ", ".join(
            "%s %d" % kv for kv in collections.Counter(family(r) for r in routeof("corpus", "dfa")
                                                       if elig(r, v, F) and live_row(r)).most_common(30)))
    P()
    P("### bench weights (upper estimates, ms; walk_survey's K12 formula on any pattern)")
    bE = [r for r in routeof("bench", "dfa") if elig(r, v, 2)]
    P("(F = 2 line first, then F = 1 and F = 8)")
    w_all = sum(W.get(r["id"], 0) for r in bE)
    w_ip = sum(W.get(r["id"], 0) for r in bE if is_ipv6_sfx(r))
    w_out_live = sum(W.get(r["id"], 0) for r in bE if not is_ipv6_sfx(r) and live_row(r))
    w_ffo = sum(W.get(r["id"], 0) for r in bE if r["nff_" + v] == "1")
    P("eligible (F = 2): %d patterns, %.3f ms; ipv6 + sfx-*: %.3f ms; OUTSIDE them: %.3f ms (%.3f ms LIVE: not served, not keyed);"
      " ffree-only members: %.3f ms" % (len(bE), w_all, w_ip, w_all - w_ip, w_out_live, w_ffo))
    for F in (1, 8):
        bF = [r for r in routeof("bench", "dfa") if elig(r, v, F)]
        P("  F = %d: %d patterns, %.3f ms (ipv6 + sfx-* %.3f ms; outside %.3f ms, of which LIVE %.3f ms)" % (
            F, len(bF), sum(W.get(r["id"], 0) for r in bF), sum(W.get(r["id"], 0) for r in bF if is_ipv6_sfx(r)),
            sum(W.get(r["id"], 0) for r in bF if not is_ipv6_sfx(r)), sum(W.get(r["id"], 0) for r in bF if not is_ipv6_sfx(r) and live_row(r))))
    P("top-weighted eligible: " + ", ".join("%s %.3f" % (r["id"], W.get(r["id"], 0)) for r in sorted(bE, key=lambda r: -W.get(r["id"], 0))[:10]))
    P()


detail("max_peel")
detail("sub_peel")
P("## OFF-ROUTE (stage 2) populations, same gates, F = 2")
for pop in POPS:
    for route in ("hybrid", "vm-only"):
        P("%s %s: strict %d, generous %d" % (pop, route, count(pop, "max_peel", 2, route=route), count(pop, "sub_peel", 2, route=route)))
P()
P("## Declines (DFA route, parsed, unanchored; best candidate's furthest gate), STRICT and GENEROUS")
for pop in POPS:
    U = [r for r in routeof(pop, "dfa") if r["outcome"] not in ("refused", "unparsed", "anchored")]
    for vv in ("max_peel", "sub_peel"):
        P("%s %s: %s" % (pop, vv, dict(collections.Counter(r["stage_" + vv] for r in U))))
        P("   G2 declines by the factor-free arm's reason: " + str(dict(collections.Counter(r["ffwhy_" + vv] for r in U if r["stage_" + vv] == "G2"))))
print("\n".join(OUTL))
