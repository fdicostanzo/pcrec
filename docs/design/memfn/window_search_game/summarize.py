#!/usr/bin/env python3
"""summarize.py OUTDIR -- the tables window_search_game.md cites, from
run_game.py's TSVs. Pure arithmetic over committed counts; prints markdown."""
import collections
import csv
import sys

D = sys.argv[1]


def rows(f):
    return list(csv.DictReader(open("%s/%s" % (D, f)), delimiter="\t", quoting=csv.QUOTE_NONE))


SPANS, INFO, CH, SIM, SF = (rows(f) for f in
                            ("spans.tsv", "spaninfo.tsv", "choices.tsv", "sim.tsv", "spanforms.tsv"))
SETS = ["capability", "loglines", "syntax", "corpus"]
POL = ["P1-rare-pos", "P2-rare-span", "P3-pair", "P4-selfprice", "P5-dfa", "P5-vm"]


def h(t):
    print("\n### " + t + "\n")


def table(head, body):
    print("| " + " | ".join(head) + " |")
    print("|" + "---|" * len(head))
    for b in body:
        print("| " + " | ".join(str(x) for x in b) + " |")


# ---- A. expressibility ------------------------------------------------------
h("A. What the contract can express (per set)")
info = collections.defaultdict(list)
for r in INFO:
    info[(r["set"], r["name"])].append(r)
body = []
notes_ct = collections.defaultdict(collections.Counter)
for s in SETS:
    P = [r for r in SPANS if r["set"] == s]
    c = collections.Counter()
    for r in P:
        c["n"] += 1
        if not r["status"].startswith("ok"):
            c["unparsed"] += 1
            continue
        for n in r["notes"].split(","):
            if n != "-":
                notes_ct[s][n] += 1
        if r["anch_start"] == "True":
            c["anchored"] += 1
            continue
        sp = info[(s, r["name"])]
        if not sp:
            c["nospan"] += 1
            continue
        b = [x for x in sp if x["mb"] != "inf"]
        u = [x for x in sp if x["mb"] == "inf"]
        inner = [x for x in b if x["mb"] != "0"]
        if inner:
            c["bounded_inner"] += 1
        if u:
            c["has_unbounded"] += 1
        best = min(sp, key=lambda x: float(x["min_pos_rate"]))
        if best["mb"] == "inf":
            c["rarest_pos_unbounded"] += 1
        bestj = min(sp, key=lambda x: float(x["joint_rate"]))
        if bestj["mb"] == "inf":
            c["rarest_span_unbounded"] += 1
        if not b:
            c["no_bounded"] += 1
        if len(b) >= 2:
            c["ge2_bounded"] += 1
        ovs = [int(x["ov"]) for x in inner]
        if ovs and max(ovs) > 0:
            c["inner_ov_gt0"] += 1
    body.append([s, c["n"], c["unparsed"], c["anchored"], c["nospan"], c["no_bounded"],
                 c["bounded_inner"], c["inner_ov_gt0"], c["ge2_bounded"], c["has_unbounded"],
                 c["rarest_pos_unbounded"], c["rarest_span_unbounded"]])
table(["set", "patterns", "unparsed", "anchored ^", "no span", "no bounded span",
       "bounded inner span", "inner ov>0", ">=2 bounded spans", "has unbounded span",
       "rarest POSITION is in an unbounded span", "rarest SPAN (joint) is unbounded"], body)
h("A2. Loss notes (patterns carrying each)")
allk = sorted({k for s in SETS for k in notes_ct[s]})
table(["note"] + SETS, [[k] + [notes_ct[s][k] for s in SETS] for k in allk])

# k-set control
ag = dis = pats = bad = 0
for r in SPANS:
    if r["kset_agree"] not in ("-", "0/0"):
        a, d = map(int, r["kset_agree"].split("/"))
        ag += a
        dis += d
        pats += 1
        bad += d > 0
h("A3. Control: extractor prefix classes vs pcrec's k-set walk sizes")
print("%d patterns with a fixed prefix span; %d positions agree, %d differ (%d patterns)." % (pats, ag, dis, bad))
for r in SPANS:
    if r["kset_agree"] not in ("-", "0/0") and int(r["kset_agree"].split("/")[1]) > 0:
        print("- `%s/%s` %s (notes %s)" % (r["set"], r["name"], r["kset_agree"], r["notes"]))

# ---- B. policy agreement -----------------------------------------------------
h("B. Which span each policy picks (patterns with >=1 bounded span, unanchored)")
ch = collections.defaultdict(dict)
for r in CH:
    ch[(r["set"], r["name"])][r["policy"]] = r["form"]


def spanof(form):
    if form.startswith(("one#", "pair#")):
        return form.split("{")[0].split("#")[1]
    return form


body = []
for s in SETS:
    keys = [k for k in ch if k[0] == s and "P1-rare-pos" in ch[k]]
    row = [s, len(keys)]
    for p in POL[1:]:
        same_span = sum(1 for k in keys if spanof(ch[k][p]) == spanof(ch[k]["P1-rare-pos"]))
        row.append("%d" % same_span)
    dec = collections.Counter()
    for k in keys:
        for p in POL:
            if ch[k][p] == "decline":
                dec[p] += 1
    row.append(" ".join("%s:%d" % (p.split("-")[0] + p[2:].replace("-", ""), dec[p]) for p in POL if dec[p]) or "-")
    inner = collections.Counter()
    for k in keys:
        for p in POL:
            f = ch[k][p]
            if "mb=" in f and "mb=0," not in f:
                inner[p] += 1
    row.append(" ".join("%s:%d" % (p.split("-")[0], inner[p]) for p in POL))
    body.append(row)
table(["set", "patterns", "P2 same span as P1", "P3", "P4", "P5-dfa", "P5-vm", "declines",
       "picks an INNER span (mb>0)"], body)

h("B2. Span flips between the consumer-blind and consumer-priced policies")
flips = collections.Counter()
ex = []
for k, d in ch.items():
    if "P4-selfprice" not in d:
        continue
    a, b, c = d["P4-selfprice"], d["P5-dfa"], d["P5-vm"]
    if spanof(a) != spanof(b):
        flips["P4!=P5-dfa"] += 1
        ex.append((k, a, b, c))
    if spanof(a) != spanof(c):
        flips["P4!=P5-vm"] += 1
        ex.append((k, a, b, c))
    if spanof(b) != spanof(c):
        flips["P5-dfa!=P5-vm"] += 1
print(dict(flips))
seen = set()
for k, a, b, c in ex[:40]:
    if k in seen:
        continue
    seen.add(k)
    print("- `%s/%s`: P4 `%s` / P5-dfa `%s` / P5-vm `%s`" % (k[0], k[1], a, b, c))

# ---- C. counted consequences ---------------------------------------------------
h("C. Counted consequences on the throughput subjects (sum over the common population)")
sim = collections.defaultdict(dict)
for r in SIM:
    sim[(r["set"], r["name"], r["subject"])][r["policy"]] = r
body = []
for subj in sorted({k[2] for k in sim}):
    for s in SETS:
        ks = [k for k in sim if k[0] == s and k[2] == subj and
              all(sim[k].get(p, {}).get("stops", "-") != "-" for p in POL[:3] + ["SHIPPED"])]
        if not ks:
            continue
        for p in POL + ["P5-dfa-subjprior", "SHIPPED"]:
            tot = collections.Counter()
            m = 0
            for k in ks:
                r = sim[k].get(p)
                if r is None or r["stops"] == "-":
                    continue
                m += 1
                for f in ("stops", "surv", "win_bytes", "starts", "work_dfa", "work_vm"):
                    tot[f] += float(r[f])
            body.append([subj, s, len(ks), p, m, "%.0f" % tot["stops"], "%.0f" % tot["surv"],
                         "%.0f" % tot["win_bytes"], "%.0f" % tot["starts"],
                         "%.3g" % tot["work_dfa"], "%.3g" % tot["work_vm"]])
table(["subject", "set", "pop", "policy", "with form", "stops", "survivors", "window bytes",
       "VM starts", "work(dfa)", "work(vm)"], body)

# ---- D. Frank's question -------------------------------------------------------
h("D. Span vs span: does the ranking flip once the window is priced?")
sf = collections.defaultdict(list)
for r in SF:
    sf[(r["set"], r["name"], r["subject"])].append(r)
flip = collections.Counter()
exd = []
pred_err = []
for k, fs in sf.items():
    for r in fs:
        if int(r["stops"]) > 0:
            pred = float(r["est_surv"]) * 262144
            pred_err.append((int(r["surv"]) + 1) / (pred + 1))
    spans = {r["span"] for r in fs}
    if len(spans) < 2:
        continue
    flip["n"] += 1
    by_stop = min(fs, key=lambda r: (int(r["stops"]), int(r["mb"])))
    by_est = min(fs, key=lambda r: (float(r["est_stop"]), int(r["mb"])))
    by_scan = min(fs, key=lambda r: float(r["work_scan"]))
    by_dfa = min(fs, key=lambda r: float(r["work_dfa"]))
    by_vm = min(fs, key=lambda r: float(r["work_vm"]))
    if by_est["span"] != by_stop["span"]:
        flip["prior-vs-measured stops"] += 1
    if by_scan["span"] != by_dfa["span"]:
        flip["scan-only vs dfa-priced"] += 1
    if by_scan["span"] != by_vm["span"]:
        flip["scan-only vs vm-priced"] += 1
    if by_dfa["span"] != by_vm["span"]:
        flip["dfa vs vm"] += 1
    # similar stops, very different windows
    for a in fs:
        for b in fs:
            if a["span"] >= b["span"] or a["kind"] != b["kind"]:
                continue
            sa, sb = int(a["stops"]), int(b["stops"])
            if max(sa, sb) == 0 or min(sa, sb) == 0 or max(sa, sb) > 2 * min(sa, sb):
                continue
            wa, wb = int(a["mb"]) + int(a["L"]), int(b["mb"]) + int(b["L"])
            if max(wa, wb) >= 3 * min(wa, wb) or abs(int(a["ov"]) - int(b["ov"])) >= 4:
                exd.append((k, a, b))
print("pattern x subject cells with >=2 bounded spans: %d" % flip["n"])
table(["ranking compared", "argmin span differs"],
      [[x, flip[x]] for x in ("prior-vs-measured stops", "scan-only vs dfa-priced",
                              "scan-only vs vm-priced", "dfa vs vm")])
pred_err.sort()
if pred_err:
    q = lambda f: pred_err[min(len(pred_err) - 1, int(f * len(pred_err)))]
    print("\nmeasured/predicted survivors (+1 smoothed), %d forms: p10 %.3g, p50 %.3g, p90 %.3g, max %.3g"
          % (len(pred_err), q(.1), q(.5), q(.9), pred_err[-1]))
h("D2. Similar stop counts (<=2x), very different windows (width >=3x or overshoot gap >=4)")
print("%d form pairs" % len(exd))
body = []
for k, a, b in exd[:30]:
    body.append(["%s/%s %s" % (k[0], k[1], k[2].split("__")[1]),
                 "%s s=%s v=%s wb=%s" % (a["form"], a["stops"], a["surv"], a["win_bytes"]),
                 "%s s=%s v=%s wb=%s" % (b["form"], b["stops"], b["surv"], b["win_bytes"]),
                 "%s / %s" % (a["work_dfa"], b["work_dfa"]), "%s / %s" % (a["work_vm"], b["work_vm"])])
table(["cell", "form A (stops, survivors, window bytes)", "form B", "work dfa A/B", "work vm A/B"], body)

# ---- E. [wingame2] P6 `refine` -----------------------------------------------
def rows_opt(f):
    try:
        return rows(f)
    except FileNotFoundError:
        return []


REF = rows_opt("refine.tsv")
REL = rows_opt("relcontrol.tsv")
if REF:
    def num(x):
        return float(x) if x not in ("-", "") else 0.0

    def fmtw(w):
        return "%.3g" % w

    h("E0. Control: relative distance from (move-back, overshoot, length) vs a direct walk of the items")
    ag = sum(r["agree"] == "1" for r in REL)
    print("%d span pairs (earlier span bounded): %d agree, %d differ." % (len(REL), ag, len(REL) - ag))

    P6POL = ["P5-dfa", "P5-vm", "P6-dfa", "P6-vm", "SHIPPED"]
    sim6 = collections.defaultdict(dict)
    for r in SIM:
        sim6[(r["set"], r["name"], r["subject"])][r["policy"]] = r
    h("E1. What P6 picks (original 327 patterns | witnesses)")
    chp = collections.defaultdict(lambda: collections.Counter())
    for r in CH:
        if not r["policy"].startswith("P6"):
            continue
        f = r["form"]
        k = "plan" if f.startswith("local") else "decline" if f == "decline" else \
            "form" if f.startswith(("one#", "pair#")) else "none"
        chp[(r["set"] == "wit2", r["policy"])][k] += 1
    table(["population", "policy", "plan (A via B)", "single-span form", "decline", "no bounded span"],
          [["witnesses" if w else "327 patterns", p, c["plan"], c["form"], c["decline"], c["none"]]
           for (w, p), c in sorted(chp.items())])

    h("E2. Cells where P6 chose a plan: P6 against P5 and the consumer meeting every byte (work, one DFA step = 1)")
    body = []
    tot = collections.Counter()
    for k, d in sorted(sim6.items()):
        for cons in ("dfa", "vm"):
            p6 = d.get("P6-" + cons)
            p5 = d.get("P5-" + cons)
            if p6 is None or not p6["form"].startswith("local") or p5 is None:
                continue
            n = int(float(p6["stops"] if False else 0)) or None
            w6, w5 = num(p6["work_" + cons]), num(p5["work_" + cons])
            sh = d.get("SHIPPED")
            body.append([("wit" if k[0] == "wit2" else k[0]) + "/" + k[1], k[2].split("__")[1], cons,
                         p6["form"].split(":")[1].split("<-")[0] + " via " + p6["form"].split("<-")[1][:24],
                         p6["stops"], p6["surv"], fmtw(w6), p5["form"][:24], fmtw(w5),
                         "%.2f" % (w5 / w6) if w6 else "-",
                         fmtw(num(sh["work_" + cons])) if sh and sh["stops"] != "-" else "-"])
            if k[0] != "wit2":
                tot[cons + "_p6"] += w6
                tot[cons + "_p5"] += w5
                tot[cons + "_n"] += 1
    table(["pattern", "subject", "cons", "P6 plan", "B stops", "A windows", "work P6", "P5 pick", "work P5",
           "P5/P6", "work SHIPPED"], body)
    print("\nOriginal-population plan cells only: " + "; ".join(
        "%s: %d cells, sum P5 %s vs P6 %s" % (c, tot[c + "_n"], fmtw(tot[c + "_p5"]), fmtw(tot[c + "_p6"]))
        for c in ("dfa", "vm")))

    h("E3. Frank's setting (refine_pair exists: a tightest span A plus a rarer span B) -- every variant, work per consumer")
    pat = collections.defaultdict(lambda: collections.defaultdict(dict))
    for r in REF:
        pat[(r["set"], r["name"])][r["subject"]][(r["consumer"], r["variant"])] = r
    VAR = ["nosearch", "P5", "P6", "local", "local-loose", "fwd", "fwd-gate", "nosearch-gate"]
    for cons in ("dfa", "vm"):
        body = []
        for k, subs in sorted(pat.items()):
            gaps = {next(iter(v.values()))["gap"] for v in subs.values()}
            if gaps == {"-"} or k[0] != "wit2":
                continue
            for sid, d in sorted(subs.items()):
                if (cons, "fwd") not in d:
                    continue
                row = [k[1], d[(cons, "fwd")]["gap"], d[(cons, "local")]["region"] if (cons, "local") in d else "-",
                       sid.split("__")[1].replace("loglines_", "log")]
                for v in VAR:
                    row.append(fmtw(num(d[(cons, v)]["work"])) if (cons, v) in d else "-")
                body.append(row)
        print("\nConsumer **%s** (work; one DFA step = 1):\n" % cons)
        table(["witness", "gap", "region", "subject"] + VAR, body)

    h("E4. Local-search detail (witnesses with a bounded gap, exact region): counts per B stop")
    body = []
    for k, subs in sorted(pat.items()):
        if k[0] != "wit2":
            continue
        for sid, d in sorted(subs.items()):
            r = d.get(("dfa", "local"))
            if r is None:
                continue
            rl = d.get(("dfa", "local-loose"))
            st = int(r["stops"])
            body.append([k[1], sid.split("__")[1].replace("loglines_", "log"), r["region"],
                         rl["region"] if rl else "-", st, r["bsurv"],
                         "%.2f" % (num(r["local_pos"]) / st) if st else "-", r["surv"],
                         "%.1f" % (num(r["win_bytes"]) / num(r["surv"])) if num(r["surv"]) else "-",
                         "%.1f" % (num(r["starts"]) / num(r["surv"])) if num(r["surv"]) else "-"])
    table(["witness", "subject", "region (exact)", "region (loose)", "B stops", "B survivors",
           "local positions per B stop", "A windows", "window bytes each", "starts each"], body)

    h("E5. Presence gate in front of the forward search: fwd, fwd-gate, nosearch, nosearch-gate (all refine cells with a B)")
    gt = collections.Counter()
    body = []
    for k, subs in sorted(pat.items()):
        for sid, d in sorted(subs.items()):
            for cons in ("dfa", "vm"):
                if (cons, "fwd-gate") not in d:
                    continue
                w = {v: num(d[(cons, v)]["work"]) for v in ("nosearch", "fwd", "fwd-gate", "nosearch-gate")}
                gt[("wit" if k[0] == "wit2" else "pop", cons, "gate pays vs fwd" if w["fwd-gate"] < w["fwd"] else "gate loses vs fwd")] += 1
                best = min(w, key=lambda v: w[v])
                gt[("wit" if k[0] == "wit2" else "pop", cons, "best: " + best)] += 1
    table(["population", "consumer", "outcome", "cells"],
          [[a, b, c, n] for (a, b, c), n in sorted(gt.items())])
