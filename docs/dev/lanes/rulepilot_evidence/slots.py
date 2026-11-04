#!/usr/bin/env python3
"""rulepilot: the inventory PER SLOT (pricing_rulepilot.md §2): for every slot, how many sites
have a real choice in it among their FORCEABLE default-route arms, and the row values seen.
The slot of a stamp is census_dry.py's STAMP_SLOT map (stamps are the path's proxy, as there).

usage: slots.py CENSUS_JSONL
"""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census_dry as cd  # noqa: E402

def main():
    rows = [json.loads(l) for l in open(sys.argv[1])]
    comp = [r for r in rows if not r["refused"]]
    choice = collections.Counter(); width = collections.defaultdict(list); vals = collections.defaultdict(collections.Counter)
    for r in comp:
        if len(r["arms"]) < 2:
            continue
        per = collections.defaultdict(set)
        for a in r["arms"]:
            for k, v in a["stamps"].items():
                per[cd.STAMP_SLOT[k]].add(v if k != "RX_DFA_PREFILTER_OFFSETS" else "offsets")
        for k in ("RX_DFA_SCAN", "RX_REQ_WHY", "RX_REQ_HANDOFF", "RX_DFA_PREFILTER", "RX_VM_START_SCAN",
                  "RX_VM_RESEED", "RX_DFA_START", "RX_DFA_MATCH"):
            for a in r["arms"]:
                vals[cd.STAMP_SLOT[k] + " " + k].update([a["stamps"].get(k, "-")])
        sl = set()
        for k in {k for a in r["arms"] for k in a["stamps"]}:
            if len({a["stamps"].get(k) for a in r["arms"]}) > 1:
                sl.add(cd.STAMP_SLOT[k])
        for s in sl:
            choice[s] += 1
            width[s].append(len(per[s]))
        if not sl:
            choice["(bytes only: kit within-site)"] += 1
    n2 = sum(1 for r in comp if len(r["arms"]) >= 2)
    print(f"compiling sites {len(comp)}; with >= 2 forceable default-route arms {n2}; single-path {len(comp) - n2}")
    print("sites with a FORCEABLE choice in the slot (distinct row values per such site: median, max):")
    for s, n in choice.most_common():
        w = sorted(width.get(s, [0]))
        print(f"  {s:32s} {n:4d}   values median {w[len(w) // 2]} max {w[-1]}")
    print("row values over all forceable arms (stamp: value count):")
    for k in sorted(vals):
        print(f"  {k}: " + ", ".join(f"{v} {c}" for v, c in vals[k].most_common()))

if __name__ == "__main__":
    main()
