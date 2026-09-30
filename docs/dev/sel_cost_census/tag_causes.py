#!/usr/bin/env python3
import json

rows = json.load(open("wins.json"))
meta = json.load(open("engine_meta.json"))
patterns = json.load(open("patterns.json"))

ANCHOR1 = {"anc-caret", "anc-a-uc", "anc-g-uc"}
CLSRUN = {"cls-w", "mod-a", "cls-posix", "unp-p-lc"}
HYBRID = {"lka-pos", "lka-verb", "lka-neg", "lka-nonatomic", "lkb-pos", "lkb-neg",
          "grp-cap", "grp-named", "grp-named-quote", "asr-k-uc",
          "rec-back", "rec-py", "rec-g-angle", "rec-fwd",
          "qnt-poss-plus", "qnt-poss-quest", "grp-atomic-alt"}

def tag(r):
    pid = r["pattern"]
    regime = r["regime"]
    if regime == "match-compliance":
        return "D-OS4-regime-artifact"
    if pid in ANCHOR1:
        return "A-anchored-one-attempt"
    if pid in CLSRUN:
        return "B-classrun-dfa-vs-vm"
    if pid in HYBRID:
        return "C-hybrid-prefilter-pricing"
    return "other"

out_rows = []
for r in rows:
    if r["cap"] != "caps":
        continue
    em = meta["caps"].get(r["pattern"], {})
    out_rows.append({
        **r,
        "cause": tag(r),
        "auto_engine": em.get("engine"),
        "dfa_prefilter": em.get("dfa_prefilter"),
        "dfa_scan": em.get("dfa_scan"),
        "req_why": em.get("req_why"),
        "ncaps": em.get("ncaps"),
    })

import csv
with open("census_full.tsv", "w", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["cap", "pattern", "family", "regime", "auto_ns", "best_vm_id", "best_vm_ns",
                "ratio_auto_over_vm", "cause", "auto_engine", "dfa_prefilter", "dfa_scan", "req_why", "ncaps"])
    for r in sorted(out_rows, key=lambda r: (r["regime"], -(r["ratio_auto_over_vm"] or 0))):
        w.writerow([r["cap"], r["pattern"], r["family"], r["regime"], f"{r['auto_ns']:.2f}",
                    r["best_vm_id"] or "", f"{r['best_vm_ns']:.2f}" if r["best_vm_ns"] else "",
                    f"{r['ratio_auto_over_vm']:.4f}" if r["ratio_auto_over_vm"] else "",
                    r["cause"], r["auto_engine"], r["dfa_prefilter"], r["dfa_scan"], r["req_why"], r["ncaps"]])

# Bucket summaries excluding match-compliance
from collections import defaultdict
buckets = defaultdict(list)
for r in out_rows:
    if r["regime"] == "match-compliance":
        continue
    buckets[r["cause"]].append(r)

for cause, lst in sorted(buckets.items()):
    wins = [r for r in lst if r["ratio_auto_over_vm"] and r["ratio_auto_over_vm"] > 1.03]
    losses = [r for r in lst if r["ratio_auto_over_vm"] and r["ratio_auto_over_vm"] < 1/1.03]
    print(f"{cause}: {len(lst)} cells (non-match-compliance), forced-VM wins {len(wins)}, auto wins {len(losses)}")
    if wins:
        rs = [r["ratio_auto_over_vm"] for r in wins]
        print(f"   forced-VM-win ratio range: {min(rs):.2f}x - {max(rs):.2f}x")
    if losses:
        rs = [1/r["ratio_auto_over_vm"] for r in losses]
        print(f"   auto-win ratio range: {min(rs):.2f}x - {max(rs):.2f}x")
