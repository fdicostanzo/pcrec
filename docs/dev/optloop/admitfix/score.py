#!/usr/bin/env python3
"""Scores I-102's grid and the G2 population at the [B84] pin pair.

For every cell: the median at all four pins (25b1984f batch-1 BEFORE,
8d716693 batch-1 AFTER, b1885a83 batch-2 AFTER = I-102's BEFORE, 6ef76820 the
admission fix), the D119 verdict against b1885a83 (|Δ| > before-IQR), the
same against this pin pair's own scale-matched NULL BAND (nullband.json;
|Δ| > max(IQR, band edge on the Δ's own side)), and the fix's REQ_WHY on the
cell's build config (nullctl.json).  Also the 29-cell G2 list itself, each
row cited to the batch-1 ledger table it was counted from.

Reads $SCR/{cells,nullctl,nullband}.json; writes $SCR/score.json and prints
Markdown tables."""
import os, json
SCR = os.environ["SCR"]
C = json.load(open(f"{SCR}/cells.json")); ID = json.load(open(f"{SCR}/nullctl.json"))
NB = json.load(open(f"{SCR}/nullband.json"))["bands"]
CFG = {"auto-caps": "auto-caps", "auto-nocaps": "auto-nocaps", "vm-caps": "vm-caps", "vm-in-caps": "vm-caps"}
T4 = ("auto-caps", "auto-nocaps", "vm-caps", "vm-in-caps")
AC, AN = "auto-caps", "auto-nocaps"
THR, SRCH = "large-subject-throughput", "short-subject-search"
RS = {THR: "thr", SRCH: "srch"}

# THE 29 (cycle1_ledger_reading.md §6 G2: "8 carve-out rows, 8 of §2.1, 13
# of §2.2" -- the §-numbers are the BATCH-1 LEDGER's
# (pcrec-bench docs/dev/ledgers/2026-09-23-optloop1-batch1-after-8d716693.md),
# not the reading's: its §1.2 carve-out table, §2.1 (non-named regressions,
# before >= 100 ns) and §2.2 (floor-conversion cells, before < 100 ns),
# each row whose pattern is one of G2's nine).
G2 = [(p, r, t, "B1 §1.2 carve-out") for p in ("uuid-near-miss", "ipv4-near-miss")
      for r in (THR, SRCH) for t in (AC, AN)]
G2 += [(p, r, t, "B1 §2.1") for p, r, t in (
    ("logparse-atomic-removed", SRCH, AN), ("wild-validator-ipv4-owasp", SRCH, AN),
    ("winpath-near-miss", SRCH, AC), ("winpath-near-miss", SRCH, AN),
    ("wild-datetime-moment-iso8601", SRCH, AN), ("logparse-atomic-removed", SRCH, AC),
    ("logparse-atomic", SRCH, AC), ("logparse-atomic", SRCH, AN))]
G2 += [(p, THR, t, "B1 §2.2") for p, t in (
    ("winpath-near-miss", AC), ("winpath-near-miss", AN),
    ("email-nested-plus", AN), ("email-nested-plus", AC),
    ("wild-datetime-moment-iso8601", AN), ("logparse-atomic-removed", AN),
    ("wild-datetime-moment-iso8601", AC), ("logparse-atomic", AC),
    ("wild-validator-ipv4-owasp", AN), ("logparse-atomic-removed", AC),
    ("logparse-atomic", AN), ("wild-validator-email-owasp", AN),
    ("wild-validator-email-owasp", AC))]
assert len(G2) == 29 and len(set(g[:3] for g in G2)) == 29

def scale(ns): return ">=1us" if ns >= 1000 else ("100ns-1us" if ns >= 100 else "<100ns")
def cell(pin, p, r, t): return C.get(f"{pin}|{t}|{p}|{r}")
def score(p, r, t):
    b, a = cell("b1885a83", p, r, t), cell("6ef76820", p, r, t)
    row = {"pattern": p, "regime": RS[r], "testee": t,
           "req_why": ID.get(f"{p}|{CFG[t]}", {}).get("req_why"),
           "m": {pin: (cell(pin, p, r, t) or {}).get("median") for pin in ("25b1984f", "8d716693", "b1885a83", "6ef76820")}}
    if a["median"] is None:
        row.update(verdict="GIVE-UP", nb_verdict="GIVE-UP", failing=a["failing"]); return row
    d = 100 * (a["median"] - b["median"]) / b["median"]
    band = NB[f"{r}|{scale(b['median'])}"]; edge = band["max"] if d > 0 else band["min"]
    iqrp = 100 * b["iqr"] / b["median"]
    v = "within" if abs(d) <= iqrp else ("improve" if d < 0 else "REGRESS")
    nb = "within" if abs(d) <= max(iqrp, abs(edge)) else ("improve" if d < 0 else "REGRESS")
    rec = None
    if row["m"]["25b1984f"]:
        rec = 100 * (a["median"] - row["m"]["25b1984f"]) / row["m"]["25b1984f"]
    row.update(d=d, iqr_pct=iqrp, band_edge=edge, verdict=v, nb_verdict=nb, vs_b1_before=rec)
    return row

GRID = {"(a)": [("wild-validator-email-owasp", THR, t) for t in T4],
        "(b)": [(p, THR, t) for p in ("winpath-near-miss", "email-nested-plus") for t in T4],
        "(c)": [("wild-codegrammar-json-array-begin", THR, t) for t in T4],
        "(d)": [(p, r, t) for p in ("uuid-near-miss", "ipv4-near-miss") for r in (THR, SRCH) for t in (AC, AN)],
        "(f)": [("nested-comment-rec", THR, t) for t in T4],
        "(g)": [("wild-secrets-github-pat", THR, t) for t in ("vm-caps", "vm-in-caps")],
        "(h)": [(p, THR, t) for p in ("router-prefix-order", "keyword-prefix-order") for t in T4]}
G2P = sorted({g[0] for g in G2})
SUPER = [(p, r, t) for p in G2P for r in (THR, SRCH) for t in T4]
out = {"grid": {k: [score(*c) for c in v] for k, v in GRID.items()},
       "g2_29": [dict(score(p, r, t), source=s) for p, r, t, s in G2],
       "g2_superset": [score(*c) for c in SUPER]}
json.dump(out, open(f"{SCR}/score.json", "w"), indent=1)

def fmt(x, nd=1): return "—" if x is None else f"{x:,.{nd}f}"
def md(rows, extra=False):
    print("| pattern | regime | testee | REQ_WHY | b1885a83 ns | 6ef76820 ns | Δ% | IQR% | null edge | verdict (IQR / band)" + (" | vs batch-1 BEFORE 25b1984f |" if extra else " |"))
    print("|---|---|---|---|---|---|---|---|---|---|" + ("---|" if extra else ""))
    for x in rows:
        if x["verdict"] == "GIVE-UP":
            print(f"| {x['pattern']} | {x['regime']} | {x['testee']} | {x['req_why']} | {fmt(x['m']['b1885a83'])} | GIVE-UP ×{len(x['failing'])} | — | — | — | **GIVE-UP**" + (" | — |" if extra else " |")); continue
        print(f"| {x['pattern']} | {x['regime']} | {x['testee']} | {x['req_why']} | {fmt(x['m']['b1885a83'])} | {fmt(x['m']['6ef76820'])} | {x['d']:+.2f} | {x['iqr_pct']:.2f} | {x['band_edge']:+.2f} | {x['verdict']} / {x['nb_verdict']}"
              + (f" | {x['vs_b1_before']:+.2f}% |" if extra else " |"))
for k, v in out["grid"].items(): print("\n###", k); md(v)
print("\n### G2 29"); md(out["g2_29"], True)
from collections import Counter
for name in ("g2_29", "g2_superset"):
    print(name, "IQR:", dict(Counter(x["verdict"] for x in out[name])), "band:", dict(Counter(x["nb_verdict"] for x in out[name])))
print("\n### superset regressions (band)")
md([x for x in out["g2_superset"] if x["nb_verdict"] in ("REGRESS", "GIVE-UP")], True)
