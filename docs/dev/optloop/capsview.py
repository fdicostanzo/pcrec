"""[capsview] the caps-vs-caps re-ranking of cycle 1's matrix (Frank's ruling
2026-09-22: "we need to consider capture vs capture engines ... apples vs
apples"). Reads the SAME reproduction data cycle1_analysis.md's own scripts
wrote to the shared scratchpad (rank.json's per-testee ns dict, stamps.json's
RX_* stamps for the auto-caps/auto-nocaps compiles) -- nothing recompiled,
nothing re-measured. Emits docs/dev/optloop/capsview_data.json, the single
source every table in cycle1_caps_view.md is rendered from.

Re-point SP before re-running; it is the authoring session's scratchpad, not
a repo path (docs/dev/optloop/CLAUDE.md's own standing note on these scripts).
"""
import json, math, re, collections

SP = "/tmp/claude-501/-Users-fdicostanzo-pcrec/c7ec5900-bab2-4d19-b2df-f72f9b26896b/scratchpad"

rows = json.load(open(SP + "/rank.json"))
stamps = json.load(open(SP + "/stamps.json"))

rk = [r for r in rows if r["class"] == "ranked"]
assert len(rk) == 125, len(rk)

# §0's engine sets, restricted per this brief:
#   CAPS competitors: every capture engine except pcre2-jit (rule 1) and
#     vectorscan/pcre2-dfa (they are nocaps-only testees here, not captures).
#   CAPS scalar competitors: the above minus rust (rule 4's own carve-out).
#   NOCAPS competitors: pcre2-dfa only -- vectorscan excluded as a target
#     per §0 rule 2, stated explicitly in the NOCAPS table.
CAPS_ENGINES = ["pcre2-interp", "onig", "re2", "re2-longest", "rust", "tre"]
CAPS_SCALAR_ENGINES = ["pcre2-interp", "onig", "re2", "re2-longest", "tre"]
NOCAPS_ENGINES = ["pcre2-dfa"]


def best_of(ns, engines):
    cand = {e: ns[e] for e in engines if e in ns}
    if not cand:
        return None, None
    bk = min(cand, key=cand.get)
    return bk, cand[bk]


def score_of(w, ratio):
    if ratio is None or ratio <= 1.0:
        return 0.0
    return w * math.log2(ratio)


def stamp_for(pattern, variant, key):
    e = stamps.get(pattern, {}).get(variant)
    if not e or e.get("rc") != 0:
        return "REFUSED"
    return e.get("stamps", {}).get(key, "-").strip('"')


# ---------- 1. CAPS table ----------
caps_rows = []
caps_nodata = []
for r in rk:
    ns = r["ns"]
    if "auto-caps" not in ns:
        caps_nodata.append(r)
        continue
    ac = ns["auto-caps"]
    bk, bns = best_of(ns, CAPS_ENGINES)
    sbk, sbns = best_of(ns, CAPS_SCALAR_ENGINES)
    ratio = (ac / bns) if bns else None
    sratio = (ac / sbns) if sbns else None
    caps_rows.append(dict(
        family=r["family"], pattern=r["pattern"], regime=r["regime"], w=r["w"],
        auto_caps_ns=ac, best_cap_engine=bk, best_cap_ns=bns, ratio=ratio,
        score=score_of(r["w"], ratio),
        best_scalar_cap_engine=sbk, best_scalar_cap_ns=sbns, scalar_ratio=sratio,
        orig_variant=r["pcrec_best"], orig_ratio=r["ratio"],
    ))
caps_rows.sort(key=lambda x: -x["score"])

# ---------- 2. NOCAPS table ----------
nocaps_rows = []
nocaps_nodata = []
for r in rk:
    ns = r["ns"]
    anc = ns["auto-nocaps"]
    bk, bns = best_of(ns, NOCAPS_ENGINES)
    if bns is None:
        nocaps_nodata.append(r)
        continue
    ratio = anc / bns
    nocaps_rows.append(dict(
        family=r["family"], pattern=r["pattern"], regime=r["regime"], w=r["w"],
        auto_nocaps_ns=anc, best_nocaps_engine=bk, best_nocaps_ns=bns, ratio=ratio,
        score=score_of(r["w"], ratio),
    ))
nocaps_rows.sort(key=lambda x: -x["score"])

# ---------- 3. DELTA table ----------
# §1 rows where auto-nocaps was the winning variant AND the row scored 0
# (ratio<=1), but auto-caps loses to a capture engine in the caps table.
caps_by_pr = {(c["pattern"], c["regime"]): c for c in caps_rows}
delta_rows = []
for r in rk:
    if r["pcrec_best"] != "auto-nocaps" or r["ratio"] > 1.0:
        continue
    c = caps_by_pr.get((r["pattern"], r["regime"]))
    if c is None or c["ratio"] is None or c["ratio"] <= 1.0:
        continue
    delta_rows.append(dict(
        family=r["family"], pattern=r["pattern"], regime=r["regime"],
        auto_caps_ns=c["auto_caps_ns"], auto_nocaps_ns=r["ns"]["auto-nocaps"],
        best_cap_engine=c["best_cap_engine"], best_cap_ns=c["best_cap_ns"],
        ratio=c["ratio"],
        rx_engine=stamp_for(r["pattern"], "auto-caps", "RX_ENGINE"),
        rx_engine_sel=stamp_for(r["pattern"], "auto-caps", "RX_ENGINE_SEL"),
        rx_engine_why=stamp_for(r["pattern"], "auto-caps", "RX_ENGINE_WHY"),
    ))
delta_rows.sort(key=lambda x: -x["ratio"])

# ---------- 4. Mechanisms re-scored under the caps view ----------
MECH = {
    "M1 [OPT-REQBYTE]": [
        ("tag-depth3-bound", "large-subject-throughput"),
        ("dup-param-detect", "large-subject-throughput"),
        ("tag-pair-match", "large-subject-throughput"),
        ("wild-secrets-username-password-pair", "large-subject-throughput"),
        ("wild-logparse-winpath-grok", "large-subject-throughput"),
    ],
    "M2 [OPT-ANCHOR-VM]": [
        ("bracket-array-define", "large-subject-throughput"),
        ("bracket-array-define", "short-subject-search"),
    ],
    "M3 [OPT-FIRSTSET]": [
        ("wild-secrets-aws-access-key-id", "large-subject-throughput"),
        ("wild-secrets-aws-access-key-id", "short-subject-search"),
        ("wild-codegrammar-json-constant", "large-subject-throughput"),
        ("wild-waf-crs-942140-dbnames", "large-subject-throughput"),
    ],
    "M4 [OPT-ENDWIN]": [
        ("wild-semdiv-dollar-trailing-newline-pcre2", "large-subject-throughput"),
    ],
    "M5 [OPT-ATTEMPT-SPLIT]": [
        ("wild-waf-crs-942360-concat-sqli", "large-subject-throughput"),
        ("wild-waf-crs-942360-concat-sqli", "short-subject-search"),
    ],
}
mech_out = {}
explained_pr = set()
for name, members in MECH.items():
    total = 0.0
    detail = []
    for p, reg in members:
        explained_pr.add((p, reg))
        c = caps_by_pr.get((p, reg))
        if c is None:
            detail.append(dict(pattern=p, regime=reg, note="no auto-caps data"))
            continue
        total += c["score"]
        detail.append(dict(pattern=p, regime=reg, score=c["score"], ratio=c["ratio"],
                            best_cap_engine=c["best_cap_engine"]))
    mech_out[name] = dict(total_score=total, rows=detail)

# ---------- new population: caps-losing rows no §3 mechanism explains ----------
new_pop = [c for c in caps_rows if c["ratio"] and c["ratio"] > 1.0
           and (c["pattern"], c["regime"]) not in explained_pr]
new_pop.sort(key=lambda x: -x["score"])
bucket = collections.defaultdict(list)
ns_by_pr = {(r["pattern"], r["regime"]): r["ns"] for r in rk}
for c in new_pop:
    why = stamp_for(c["pattern"], "auto-caps", "RX_ENGINE_WHY")
    eng = stamp_for(c["pattern"], "auto-caps", "RX_ENGINE")
    if why == "-":
        key = "engine=%s, no WHY stamp (not VM-forced by a construct)" % eng
    else:
        # normalize "capture group at pattern offset N" -> one bucket; keep
        # the other WHY reasons distinct (each is a different construct).
        key = re.sub(r" at pattern offset \d+$", "", why)
    ns = ns_by_pr[(c["pattern"], c["regime"])]
    c["caps_over_nocaps"] = (ns["auto-caps"] / ns["auto-nocaps"]) if "auto-nocaps" in ns else None
    bucket[key].append(c)

# ---------- 5. totals ----------
caps_win = len([c for c in caps_rows if c["ratio"] is None or c["ratio"] <= 1.0])
caps_lose = len([c for c in caps_rows if c["ratio"] and c["ratio"] > 1.0])
nocaps_win = len([c for c in nocaps_rows if c["ratio"] <= 1.0])
nocaps_lose = len([c for c in nocaps_rows if c["ratio"] > 1.0])

out = dict(
    caps_rows=caps_rows, caps_nodata=[dict(pattern=r["pattern"], regime=r["regime"]) for r in caps_nodata],
    nocaps_rows=nocaps_rows, nocaps_nodata=[dict(pattern=r["pattern"], regime=r["regime"]) for r in nocaps_nodata],
    delta_rows=delta_rows,
    mech=mech_out,
    new_population=[dict(pattern=c["pattern"], regime=c["regime"], score=c["score"],
                          ratio=c["ratio"], best_cap_engine=c["best_cap_engine"],
                          family=c["family"]) for c in new_pop],
    new_population_buckets={k: [dict(pattern=c["pattern"], regime=c["regime"],
                                      ratio=c["ratio"], score=c["score"],
                                      caps_over_nocaps=c.get("caps_over_nocaps"),
                                      best_cap_engine=c["best_cap_engine"]) for c in v]
                             for k, v in bucket.items()},
    totals=dict(
        caps_total=len(caps_rows), caps_win_or_tie=caps_win, caps_lose=caps_lose,
        caps_nodata=len(caps_nodata),
        nocaps_total=len(nocaps_rows), nocaps_win_or_tie=nocaps_win, nocaps_lose=nocaps_lose,
        nocaps_nodata=len(nocaps_nodata),
        delta_count=len(delta_rows),
    ),
)
json.dump(out, open("docs/dev/optloop/capsview_data.json", "w"), indent=1)
print("caps: total=%d win/tie=%d lose=%d nodata=%d" % (len(caps_rows), caps_win, caps_lose, len(caps_nodata)))
print("nocaps: total=%d win/tie=%d lose=%d nodata=%d" % (len(nocaps_rows), nocaps_win, nocaps_lose, len(nocaps_nodata)))
print("delta rows:", len(delta_rows))
print("mechanism totals:", {k: round(v["total_score"], 4) for k, v in mech_out.items()})
print("new population (unexplained caps losses):", len(new_pop), "total score",
      round(sum(c["score"] for c in new_pop), 4))
print("buckets:", {k: len(v) for k, v in bucket.items()})
