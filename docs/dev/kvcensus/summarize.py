#!/usr/bin/env python3
"""kvcensus: fold the run (OUT/patterns.tsv.gz, OUT/sites.tsv.gz) into the
tables of docs/dev/kvcensus.md, printed as markdown, plus summary.json.

    OUT=build/kv/run BENCH=/home/pcrec/projects/pcrec-bench \\
    python3 docs/dev/kvcensus/summarize.py > build/kv/run/tables.md
"""
import collections, glob, gzip, json, os, sys, tomllib

OUT = os.environ.get("OUT", "build/kv/run")
BENCH = os.environ.get("BENCH", "/home/pcrec/projects/pcrec-bench")
NS_PER_B = 0.1885   # armread_report.md §1/§4: the DFA skip walk, Zen 4 7700X (c_byte 0.1884-0.1885)
NS_STEP = 1.4       # armread_report.md §2: an in-match DFA state step, ~1.4 ns/B above c_byte (DERIVED)


def load(name):
    """tolerates a run still being written (a gzip stream without its trailer)"""
    out = []
    try:
        for l in gzip.open(os.path.join(OUT, name), "rt"):
            out.append(json.loads(l))
    except (EOFError, json.JSONDecodeError):
        pass
    return out


P = load("patterns.tsv.gz")
S = load("sites.tsv.gz")
# a pattern whose machine reading FAILED an independent PCRE2 control is
# excluded from every language-derived table below and listed in section 7
BAD = {(p["id"], p["cfg"]) for p in P if p.get("c1f") or p.get("c2f") or p.get("c3f")}
for s_ in S:
    if (s_["id"], s_["cfg"]) in BAD:
        for k_ in ("exact", "span", "mixed", "whole", "a_best", "a_contig", "a_flags", "p0rel"):
            s_.pop(k_, None)
        s_["ctl_excluded"] = 1
for p_ in P:
    if (p_["id"], p_["cfg"]) in BAD:
        p_["excluded_lang"] = {k_: p_.pop(k_) for k_ in ("exact", "span", "whole", "whole_end") if k_ in p_}
C = collections.Counter
J = {}


def tab(head, rows):
    print("| " + " | ".join(head) + " |")
    print("|" + "|".join("---" if i == 0 else "---:" for i in range(len(head))) + "|")
    for r in rows:
        print("| " + " | ".join(str(x) for x in r) + " |")
    print()


def bucket(n):
    if n is None: return "n/a"
    if n == 0: return "0"
    if n == 1: return "1"
    if n == 2: return "2"
    if n <= 4: return "3-4"
    if n <= 8: return "5-8"
    if n <= 16: return "9-16"
    if n < 32: return "17-31"
    return "32 (cap)"


BK = ["0", "1", "2", "3-4", "5-8", "9-16", "17-31", "32 (cap)"]


def hist(vals):
    c = C(bucket(v) for v in vals)
    return [c.get(b, 0) for b in BK]


def q(vals, p):
    v = sorted(vals)
    return v[min(len(v) - 1, int(p * len(v)))] if v else None


# ---- §1 population -------------------------------------------------------------
print("### 1. Population (K35)\n")
rows = []
for pop in ("bench", "corpus"):
    for cfg in ("native", "utf8"):
        g = [p for p in P if p["pop"] == pop and p["cfg"] == cfg]
        ok = [p for p in g if p.get("status") == "ok"]
        ref = [p for p in g if p.get("status", "").startswith("refused")]
        err = [p for p in g if p.get("status", "").startswith("error")]
        lang = C(p.get("lang_src", "")[:4] for p in ok)
        rows.append((pop, cfg, len(g), len(ok), len(ref), len(err), lang.get("N", 0), lang.get("D", 0),
                     sum(v for k, v in lang.items() if k.startswith("none")),
                     sum(1 for p in ok if p.get("engine") == "vm"), sum(p.get("sites", 0) for p in ok)))
        J["pop_%s_%s" % (pop, cfg)] = rows[-1][2:]
tab(["pop", "cfg", "rows", "compiled", "refused", "error", "lang: own", "lang: --engine=dfa", "lang: none",
     "VM artifacts", "search sites"], rows)

print("Refusal reasons (first words of pcrec's diagnostic):\n")
rc = C()
for p in P:
    s = p.get("status", "")
    if s.startswith("refused"):
        t = s[len("refused: pcrec: "):]
        k = ("requires module" if "requires module" in t else "too large" if "too large" in t else
             "UCP/utf8" if "UCP" in t or "utf8" in t.lower() or "UTF" in t else
             "invalid" if "invalid" in t or "error" in t or "expected" in t or "unmatched" in t
             else " ".join(t.split()[:4]))
        rc[(p["pop"], p["cfg"], k)] += 1
tab(["pop", "cfg", "reason", "rows"], [(a, b, c, n) for (a, b, c), n in sorted(rc.items(), key=lambda x: -x[1])[:25]])
nolang = C((p["pop"], p["cfg"], p["lang_src"][5:40]) for p in P if p.get("status") == "ok" and p.get("lang_src", "").startswith("none"))
print("No language machine (anchored DFA absent under `--engine=dfa --no-captures -fno-scan-edge`):\n")
tab(["pop", "cfg", "why", "rows"], [(a, b, c, n) for (a, b, c), n in sorted(nolang.items(), key=lambda x: -x[1])[:15]])
print("Other (non-search) kit sites seen, per artifact:\n")
oc = C()
for p in P:
    for kv in (p.get("other_sites") or "").split(","):
        if "=" in kv:
            k, v = kv.split("="); oc[k] += int(v)
tab(["site", "instances"], sorted(oc.items(), key=lambda x: -x[1]))

# ---- §2 sites: origin, sent, need, proven today -----------------------------------
print("### 2. The search sites: origin, what is sent, what the kit proves today\n")
k = C((s["cfg"], s["site"], s["kind"], s["origin"]) for s in S)
tab(["cfg", "site", "consumer kind", "origin", "sites"], [(a, b, c, d, n) for (a, b, c, d), n in sorted(k.items())])
print("Offsets sent (span 0 / `preds` of a presence site; `R`/`O` = REQUIRED/OPTIONAL, `+k` a run):\n")
sh = C()
for s in S:
    if s["site"] == "PRE":
        continue
    sh[(s["site"], s["sent"] if len(s["sent"]) < 24 else s["sent"][:20] + "..")] += 1
tab(["site", "sent", "sites"], [(a, b, n) for (a, b), n in sorted(sh.items(), key=lambda x: -x[1])[:20]])
need = C()
for s in S:
    if s["site"] in ("PF", "OFS", "MLINE"):
        for t in s["sent"].split(","):
            need[(s["site"], t[-1:])] += 1
tab(["site", "term need", "terms"], [(a, b, n) for (a, b), n in sorted(need.items())])
pr = C((s["cfg"], s["site"], s.get("p0rel", "n/a")) for s in S)
print("`proven0` against the language's first-byte set S_0 at a START origin (`exact` = equal; `superset` = proves less "
      "than S_0 allows; a site whose span-0 set is strictly NARROWER than S_0 is reclassified `scan-restart`: the forward "
      "scan restarts where its start row stops self-looping and the reverse pass recovers the start):\n")
tab(["cfg", "site", "proven0 vs S_0", "sites"], [(a, b, c, n) for (a, b, c), n in sorted(pr.items())])
er = C((s["cfg"], s["kind"], s.get("esc_rel", "n/a")) for s in S if s["site"] in ("PF", "OFS"))
print("`proven0` against the forward machine's ESCAPE set E (the bytes that move its start row; read off the "
      "emitted table): `eq`; `wider` = proves less than E; `UNDER-esc` = narrower than E (a dropped restart):\n")
tab(["cfg", "kind", "proven0 vs E", "sites"], [(a, b, c, n) for (a, b, c), n in sorted(er.items())])
J["esc_under"] = sum(1 for s in S if s.get("esc_rel") in ("UNDER-esc", "differ"))
pp = C((s["site"], s["proven_prev"] < 256) for s in S)
tab(["site", "proven_prev states something", "sites"], [(a, b, n) for (a, b), n in sorted(pp.items())])


# ---- §3 exact prefix -----------------------------------------------------------------
print("### 3. The exact prefix from the origin\n")
st = [s for s in S if s["origin"] in ("start", "after-nl") and "exact" in s]
rows = []
for cfg in ("native", "utf8"):
    g = [s for s in st if s["cfg"] == cfg]
    rows.append([cfg, "exact", len(g)] + hist([s["exact"] for s in g]))
    rows.append([cfg, "span", len(g)] + hist([s["span"] for s in g]))
tab(["cfg", "length", "sites"] + BK, rows)
J["exact_hist"] = rows
mx = C((s["cfg"], s["mixed"]) for s in st)
print("MIXED (exact for a prefix, SUPERSET after it inside the span): sites with exact < span:\n")
tab(["cfg", "mixed", "sites"], [(a, b, n) for (a, b), n in sorted(mx.items())])
# utf8-specific mixed: the pattern's native byte reading is wholly exact, utf8 is not
nat = {(p["id"]): p for p in P if p["cfg"] == "native" and "exact" in p}
u8m = [p for p in P if p["cfg"] == "utf8" and "exact" in p and p["id"] in nat
       and nat[p["id"]]["exact"] == nat[p["id"]]["span"] and p["exact"] < p["span"]]
print("utf8-born mixing (`abc[α-ω]`-shaped): rows exact over the whole span in byte, mixed under `-e utf8`: "
      "**%d** patterns (%d of them bench). Examples:\n" % (len(u8m), sum(p["pop"] == "bench" for p in u8m)))
for p in u8m[:8]:
    print("- `%s` %s: byte exact %d/%d, utf8 exact %d/%d" % (bytes.fromhex(p["pat"])[:60].decode("utf8", "replace").replace("|", "\\|"),
          p["id"], nat[p["id"]]["exact"], nat[p["id"]]["span"], p["exact"], p["span"]))
print()
J["utf8_mixed"] = len(u8m)

# ---- §4 consumable_len ----------------------------------------------------------------
print("### 4. consumable_len per consumer kind\n")
print("(a) plain unseeded DFA (DFA_SCAN incl. offset-skip FUNC, and the hybrid's inner DFA HYB_PF): "
      "`a_best` = the largest N <= exact with one entry row after every string of S_0..S_N-1:\n")
rows = []
for cfg in ("native", "utf8"):
    for kind in ("DFA_SCAN", "HYB_PF"):
        for org in ("start", "scan-restart"):
            g = [s for s in S if s["cfg"] == cfg and s["kind"] == kind and s["origin"] == org]
            a = [s["a_best"] for s in g if "a_best" in s]
            why = C(s.get("a_why", "measured" if "a_best" in s else
                          "control-excluded" if s.get("ctl_excluded") else "no-language") for s in g)
            rows.append([cfg, kind, org, len(g), len(a)] + hist(a) +
                        [", ".join("%s %d" % kv for kv in sorted(why.items()) if kv[0] != "measured")])
tab(["cfg", "kind", "origin", "sites", "measured"] + BK + ["not measured"], rows)
J["a_hist"] = rows
cg = [s for s in S if "a_best" in s and s["origin"] == "start"]
print("Contiguous `delta_uniform` vs best entry: %d sites differ (a uniform position after a non-uniform one); "
      "position 0 uniform on %d of %d measured sites.\n" % (sum(s["a_best"] != s["a_contig"] for s in cg),
      sum(s.get("a_flags", "")[:1] == "1" for s in cg), len(cg)))
print("Which DFA_SCAN sites already prove what (a) could consume: today the kit proves offset 0 only (`proven0`); "
      "sites with a_best >= 2 have consumable bytes past offset 0: **%d** (native) / **%d** (utf8).\n" % (
      sum(1 for s in cg if s["cfg"] == "native" and s["a_best"] >= 2), sum(1 for s in cg if s["cfg"] == "utf8" and s["a_best"] >= 2)))
J["a_ge2"] = [sum(1 for s in cg if s["cfg"] == c and s["a_best"] >= 2) for c in ("native", "utf8")]
print("(b) VM literal prefix (VM_ATTEMPT, and the VM behind HYB_PF): strict = stops at a capture write; relaxed = a "
      "capture open whose value is the attempt start plus the bytes so far does not stop it:\n")
rows = []
for cfg in ("native", "utf8"):
    for kind in ("VM_ATTEMPT", "HYB_PF"):
        g = [s for s in S if s["cfg"] == cfg and s["kind"] == kind and "b_lit" in s]
        for col in ("b_lit", "b_cls", "b_rlit", "b_rcls"):
            rows.append([cfg, kind, col, len(g)] + hist([s[col] for s in g]))
tab(["cfg", "kind", "column", "sites"] + BK, rows)
J["b_over"] = sum(1 for s in S if s.get("b_over"))
print("(c) WHOLE-COVER (the exact prefix is the whole fixed-width sub-problem; no seed, view or class-indexed accept "
      "left): patterns, by population (a pattern with several sites counts once):\n")
rows = []
for pop in ("bench", "corpus"):
    for cfg in ("native", "utf8"):
        g = [p for p in P if p["pop"] == pop and p["cfg"] == cfg and "whole" in p]
        w = [p for p in g if p["whole"]]
        caps = [p for p in w if p.get("ncaps") not in ("1", "", None)]
        rows.append([pop, cfg, len(g), len(w), len(caps), hist([p["whole"] for p in w])[1:].__str__()])
tab(["pop", "cfg", "with language", "whole-cover", "of which carry captures", "width histogram 1..cap"], rows)
J["whole"] = rows
ws = C((s["cfg"], s["site"], s["kind"]) for s in S if s.get("whole") and s["origin"] == "start")
print("Whole-cover per SEARCH SITE (origin = the match start; the stream's first full-span candidate is the leftmost "
      "match):\n")
tab(["cfg", "site", "kind", "sites"], [(a, b, c, n) for (a, b, c), n in sorted(ws.items())])
J["whole_sites"] = sum(ws.values())
nos = C((p["pop"], p["cfg"]) for p in P if p.get("whole") and not p.get("sites"))
print("Whole-cover patterns with NO kit search site (anchored attempt / match-here only): %s\n" % dict(nos))
we = C((p["pop"], p["cfg"]) for p in P if p.get("whole_end"))
print("Whole-cover once a trailing END anchor (`$`/`\\z`/`\\Z`) is taken as pcrec's length compare: %s\n" % dict(we))
J["whole_end"] = dict((("%s/%s" % k), v) for k, v in we.items())

# ---- §5 context ------------------------------------------------------------------------
print("### 5. Context spans before / after the origin\n")
cx = C((p["pop"], p["cfg"], p.get("ctx")) for p in P if p.get("ctx"))
tab(["pop", "cfg", "context parse", "rows"], [(a, b, c, n) for (a, b, c), n in sorted(cx.items())])
ok = [p for p in P if p.get("ctx") == "ok"]
shp = C((p["cfg"], p.get("ctx_lead", ""), p.get("ctx_trail", "")) for p in ok)
tab(["cfg", "leading", "trailing", "rows"], [(a, b or "-", c or "-", n) for (a, b, c), n in sorted(shp.items(), key=lambda x: -x[1])[:20]])
rows = []
for pop in ("bench", "corpus"):
    for cfg in ("native", "utf8"):
        g = [p for p in ok if p["pop"] == pop and p["cfg"] == cfg]
        e = [p for p in g if p.get("ctx_expr")]
        rows.append([pop, cfg, len(g), sum("ctx_body_exact" in p for p in g), len(e),
                     sum(1 for p in e if p.get("ctx_a", 0) >= 1), sum(1 for p in e if p.get("ctx_a", 0) >= 2),
                     sum(1 for p in e if p.get("ctx_whole")),
                     sum(1 for p in g if p.get("ctx_seed_const") == 1), sum(1 for p in g if "ctx_seed_const" in p),
                     sum(p.get("ctx_ck", 0) for p in g), sum(p.get("ctx_ckf", 0) for p in g)])
tab(["pop", "cfg", "context rows", "body has a machine", "all items expressible", "(a) consumable >= 1",
     "(a) >= 2", "(c) whole-cover with context", "real seeded entry constant", "of checked",
     "PCRE2 rewrite cells", "differing"], rows)
J["ctx"] = rows

# ---- §6 savings bound ---------------------------------------------------------------------
print("### 6. Savings bound (no timing; armread Zen 4 constants)\n")
rows = []
for cfg in ("native", "utf8"):
    a = [s["a_best"] for s in S if s["cfg"] == cfg and "a_best" in s and s["origin"] == "start"]
    past0 = [max(0, x - 1) for x in a]
    rows.append([cfg, len(a), sum(a), q(a, 0.5), q(a, 0.9), "%.2f" % (sum(a) / max(1, len(a)) * NS_PER_B),
                 "%.2f" % (q(a, 0.9) * NS_PER_B if a else 0), "%.2f" % (q(a, 0.9) * (NS_PER_B + NS_STEP) if a else 0),
                 sum(past0)])
tab(["cfg", "DFA sites measured", "sum a_best (B/candidate)", "median", "p90", "mean ns/candidate @0.19",
     "p90 ns/candidate @0.19", "p90 ns/candidate @0.19+1.4", "bytes past offset 0"], rows)
J["savings"] = rows
regimes = {}
for t in glob.glob(os.path.join(BENCH, "bench", "*", "subbench.toml")):
    regimes[t.split(os.sep)[-2]] = list(tomllib.load(open(t, "rb")).get("regimes", {}))
wb = [p for p in P if p["pop"] == "bench" and p["cfg"] == "native" and p.get("whole")]
print("Whole-cover BENCH cells (native configuration; every regime the set declares):\n")
tab(["bench pattern", "width", "engine", "captures", "regimes"],
    [(p["id"], p["whole"], p.get("engine"), int(p.get("ncaps", "1")) - 1, ",".join(regimes.get(p["id"].split("/")[0], [])))
     for p in sorted(wb, key=lambda p: p["id"])])
wc = [p for p in P if p["pop"] == "bench" and p["cfg"] == "native" and p.get("ctx_whole")]
print("Bench patterns whole-cover ONCE their context joins the span:\n")
tab(["bench pattern", "items", "body width", "regimes"],
    [(p["id"], p.get("ctx_items"), p["ctx_whole"], ",".join(regimes.get(p["id"].split("/")[0], []))) for p in sorted(wc, key=lambda p: p["id"])])

# ---- §7 controls ---------------------------------------------------------------------------
print("### 7. Controls (PCRE2 10.46, independent of the machine reader)\n")
rows = []
for k, nm in (("c1", "exact-prefix samples are prefixes"), ("c2", "inexact counterexample pairs"),
              ("c3", "whole-cover samples match at width k / mutants do not")):
    rows.append([nm, sum(p.get(k, 0) for p in P), sum(p.get(k + "f", 0) for p in P),
                 sum(1 for p in P if p.get(k + "f"))])
rows.append(["leading \\b == its positional rewrite", sum(p.get("ctx_ck", 0) for p in P),
             sum(p.get("ctx_ckf", 0) for p in P), sum(1 for p in P if p.get("ctx_ckf"))])
rows.append(["proven0 narrower than the forward escape set (kit vs emitted table)", len([s for s in S if "esc_rel" in s]), J["esc_under"], ""])
rows.append(["VM prefix longer than the exact prefix", sum(1 for s in S if "b_lit" in s), J["b_over"], ""])
tab(["control", "checks", "failures", "patterns failing"], rows)
fl = [p for p in P if p.get("c1f") or p.get("c2f") or p.get("c3f") or p.get("ctx_ckf")]
for p in fl[:20]:
    print("- %s %s: c1f=%s c2f=%s c3f=%s ctxf=%s `%s` %s" % (p["id"], p["cfg"], p.get("c1f"), p.get("c2f"), p.get("c3f"),
          p.get("ctx_ckf"), bytes.fromhex(p["pat"])[:50].decode("utf8", "replace").replace("|", "\\|"),
          p.get("c1w") or p.get("c2w") or p.get("c3w") or ""))
print()
J["controls"] = rows
json.dump(J, open(os.path.join(OUT, "summary.json"), "w"), indent=1, default=str)
