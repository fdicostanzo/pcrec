#!/usr/bin/env python3
"""[LOSS-REVIEW] lrdfa: the trailing population with route stamps.

Reads gaprep3's gap_rows.json (the 2026-10-11 instance's per-cell table, stamps
compiled at main e878687b == main f2fcffb4 for src/) and causes.tsv; prints one
row per trailing (set, pattern, regime) cell: trailing vs jit or any scalar
peer (D119 roles from gapconfig). Usage: population.py GAP_ROWS CAUSES > out.tsv
"""
import json, sys, csv
sys.path.insert(0, sys.argv[3] if len(sys.argv) > 3 else '.')
gap = json.load(open(sys.argv[1]))
causes = {}
for line in open(sys.argv[2]):
    if line.startswith('#') or line.startswith('set\t') or not line.strip():
        continue
    s, p, g = line.rstrip('\n').split('\t')[:3]
    causes[(s, p)] = g
SCALAR = ("libpcre2:interp-caps", "libpcre2:dfa-nocaps", "re2:default-caps",
          "re2:longest-caps", "oniguruma:default-caps", "tre:default-caps")
PEER = "libpcre2:jit-caps"
SIMD = ("rust:default-caps",)
keys = ["RX_ENGINE", "RX_ENGINE_SEL", "RX_DFA_SCAN", "RX_DFA_PREFILTER", "RX_DFA_START",
        "RX_DFA_MATCH", "RX_VM_PREFILTER", "RX_VM_START_SCAN", "RX_REQ_BYTE", "RX_REQ_RUN",
        "RX_REQ_WHY", "RX_REQ_HANDOFF", "RX_DFA_SCAN_EDGE", "RX_END_WINDOW", "RX_NCAPS"]
print("\t".join(["set", "pattern", "regime", "tier", "group", "n", "auto_ns", "best_nonsimd", "best_ns",
                 "ratio_best", "lost_ns", "jit_ratio", "rust_ratio", "matches"] + keys))
for r in gap:
    cmp = r.get("cmp", {})
    behind = [(c, v) for c, v in cmp.items() if v.get("verdict") == "behind" and (c == PEER or c in SCALAR)]
    rust = cmp.get("rust:default-caps", {})
    rust_behind = rust.get("verdict") == "behind"
    if not behind and not rust_behind:
        continue
    auto = r["auto_caps"]
    if behind:
        c, v = min(behind, key=lambda cv: cv[1]["ns"])
    else:
        c, v = "rust:default-caps(SIMD-only)", rust
    st = r.get("stamps", {})
    jr = cmp.get(PEER, {}).get("ratio")
    print("\t".join(str(x) for x in [r["sb"], r["pattern"], r["regime"], v.get("tier"),
          causes.get((r["sb"], r["pattern"]), "?"), r.get("n"), round(auto), c, round(v["ns"]),
          round(v["ratio"], 2), round(auto - v["ns"]), round(jr, 2) if jr else "-",
          round(rust.get("ratio"), 2) if rust.get("ratio") else "-", r.get("matches", "-")]
          + [st.get(k, "-") for k in keys]))
