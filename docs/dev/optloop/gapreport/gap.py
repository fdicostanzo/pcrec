#!/usr/bin/env python3
"""[OPT-GAPREPORT] step 3: cells.json (+ stamps) -> the per-cell gap table.

D144 addendum 2's metric, applied uniformly:
  * pcrec side = the shipped DEFAULT, engine auto: `auto-caps` against a
    capturing comparator, best of `auto-caps`/`auto-nocaps` against a
    non-capturing one (the bench's own I-99/I-100 classes: rust-default,
    vectorscan and pcre2-dfa are NO-class).  Forced-engine arms are carried
    as EXPLANATION columns only.
  * MEASURED records only: a testee whose rank row is `inconclusive-spread`
    (or absent: excluded / refused / unsupported) is not a side.
  * scale tier by the smaller side's per-subject mean (median_ns / n):
      A >= 1000 ns   ratio, null band x1.10
      B 100..1000 ns ratio, null band x1.15
      C < 100 ns     ns-scale: absolute delta per call, NULL when the delta
                     is under 41% of the comparator's per-call figure
    The bands are the CROSS-WINDOW program-identical null bands measured by
    cycle2_batch2_reading.md §1 (+8.77% us-scale throughput, +11.16% search,
    +41.09% below 100 ns) -- every comparison here spans two windows (pcrec
    measured 2026-10-01/02, every comparator in September).

    python3 gap.py cells.json stamps_main.json [stamps_fc.json] > gap_rows.json
"""
import json
import math
import sys

from gapconfig import CAPS_NO, CAPS_YES, TIERS, realism

def med(c, t):
    x = c["t"].get(t)
    if not x or x.get("status") != "measured" or "median_ns" not in x:
        return None
    return x["median_ns"]


def compare(pc, comp, n):
    lo = min(pc, comp) / n
    r = pc / comp
    tier, mode, param = next((t, m, p) for floor, t, m, p in TIERS if lo >= floor)
    if mode == "delta":
        d = (pc - comp) / n
        null = abs(d) < param * (comp / n)
        verdict = "null" if null else ("behind" if d > 0 else "ahead")
        return {"tier": tier, "ratio": r, "delta_ns_call": d, "verdict": verdict}
    verdict = ("behind" if r > param else "ahead" if r < 1 / param else "null")
    return {"tier": tier, "ratio": r, "verdict": verdict}


def main():
    cells = json.load(open(sys.argv[1]))
    st_main = json.load(open(sys.argv[2]))["stamps"] if len(sys.argv) > 2 else {}
    st_fc = json.load(open(sys.argv[3]))["stamps"] if len(sys.argv) > 3 else {}
    rows = []
    for key, c in sorted(cells["cells"].items()):
        sb, pat, regime, form, fact = key.split("\t")
        n = c["n"]
        caps = med(c, "pcrec:auto-caps")
        nocaps = med(c, "pcrec:auto-nocaps")
        best = min(x for x in (caps, nocaps) if x is not None) if (caps or nocaps) else None
        row = {"sb": sb, "pattern": pat, "regime": regime, "form": form,
               "fact": fact, "n": n, "realism": realism(sb),
               "auto_caps": caps, "auto_nocaps": nocaps,
               "pcrec_status": {t: v.get("status") for t, v in c["t"].items()
                                if t.startswith("pcrec:")},
               "forced": {t: med(c, t) for t in c["t"]
                          if t.startswith("pcrec:") and t not in
                          ("pcrec:auto-caps", "pcrec:auto-nocaps")},
               "cmp": {}}
        for t in sorted(CAPS_YES | CAPS_NO):
            m = med(c, t)
            if m is None:
                continue
            side = caps if t in CAPS_YES else best
            if side is None:
                continue
            row["cmp"][t] = dict(compare(side, m, n), ns=m)
        sbk = "email" if sb == "email-specimen" else sb
        smain = st_main.get(sbk, {}).get(pat)
        sfc = st_fc.get(sbk, {}).get(pat)
        row["stamps"] = smain
        if smain and sfc:
            row["moved_since_pin"] = smain.get("code_sha") != sfc.get("code_sha")
            row["stamp_diff"] = {k: (sfc.get(k), smain.get(k)) for k in
                                 sorted(set(smain) | set(sfc))
                                 if k not in ("code_sha", "c_bytes", "ABI")
                                 and sfc.get(k) != smain.get(k)}
        rows.append(row)
    json.dump(rows, sys.stdout, indent=0, sort_keys=True)


if __name__ == "__main__":
    main()
