#!/usr/bin/env python3
import json

timings = json.load(open("timings.json"))
patterns = json.load(open("patterns.json"))

AUTO = {"caps": "pcrec_751b9c6d_auto-caps-simdna", "nocaps": "pcrec_751b9c6d_auto-nocaps-simdna"}
VM = {"caps": ["pcrec_751b9c6d_vm-caps-simdna", "pcrec_751b9c6d_vm-in-caps-simdna"],
      "nocaps": ["pcrec_751b9c6d_vm-caps-simdna", "pcrec_751b9c6d_vm-in-caps-simdna"]}
# NOTE: no forced-nocaps VM testee exists in this roster; the vm/vm-in testees
# are caps-only. So the nocaps auto can only be compared against caps-forced
# VM numbers as an approximate cross-class signal, which we do NOT do here
# (D119/I-99: never compare across capture classes). nocaps auto is reported
# on its own with no non-auto pcrec comparator available in this roster.

rows = []
for cap in ("caps", "nocaps"):
    for pattern, regimes in timings.get(cap, {}).items():
        for regime, testees in regimes.items():
            auto_id = AUTO[cap]
            if auto_id not in testees or "median_ns" not in testees[auto_id]:
                continue
            auto_ns = testees[auto_id]["median_ns"]
            auto_status = testees[auto_id]["status"]
            best_vm = None
            best_vm_id = None
            if cap == "caps":
                for vid in VM[cap]:
                    if vid in testees and "median_ns" in testees[vid] and testees[vid]["status"] == "measured":
                        ns = testees[vid]["median_ns"]
                        if best_vm is None or ns < best_vm:
                            best_vm = ns
                            best_vm_id = vid
            ratio = (auto_ns / best_vm) if best_vm else None
            rows.append({
                "cap": cap,
                "pattern": pattern,
                "regime": regime,
                "auto_ns": auto_ns,
                "auto_status": auto_status,
                "best_vm_ns": best_vm,
                "best_vm_id": best_vm_id,
                "ratio_auto_over_vm": ratio,  # >1 means forced VM is faster
                "family": patterns.get(pattern, {}).get("family"),
                "text": patterns.get(pattern, {}).get("text"),
            })

json.dump(rows, open("wins.json", "w"), indent=1)

# Summarize: caps-class wins where forced VM beats auto by >5%
wins = [r for r in rows if r["cap"] == "caps" and r["ratio_auto_over_vm"] and r["ratio_auto_over_vm"] > 1.05]
wins.sort(key=lambda r: -r["ratio_auto_over_vm"])
print(f"total caps rows: {sum(1 for r in rows if r['cap']=='caps')}")
print(f"caps rows where forced VM beats auto by >5%: {len(wins)}")
for r in wins:
    print(f"{r['ratio_auto_over_vm']:.3f}x  {r['pattern']:30s} {r['regime']:26s} fam={r['family']:12s} auto={r['auto_ns']:.1f}ns best_vm={r['best_vm_ns']:.1f}ns ({r['best_vm_id']})")
