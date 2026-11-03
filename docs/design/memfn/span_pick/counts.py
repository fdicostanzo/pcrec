#!/usr/bin/env python3
"""span_pick rev 2: re-count the populations rev 2 quotes, from R-33's raw sweep.
    python3 -I counts.py SWEEP.jsonl"""
import collections
import json
import sys

pf = pf2 = ofs = ofs_k0 = 0
arow = collections.Counter()
runs = rdiff = 0
fdrows = collections.Counter()
for line in open(sys.argv[1]):
    rec = json.loads(line)
    for s in rec["sites"]:
        if s.get("deleg") == "PF" and s.get("alts") is not None:
            pf += 1
            pf2 += len(s["alts"]) >= 2
        if s.get("form") == 2 and s.get("handoff") == 0 and s.get("alts"):
            ofs += 1
            ofs_k0 += s.get("site_kind") == 0
        tr = s.get("trace") or {}
        ends = tr.get("ends", [])
        a = [ch for tb, ch in ends if tb == "wfA" and ch not in (None, "none", "-")]
        ents = [al["entry"] for al in s.get("alts") or []]
        for e, r in zip(ents, a):
            arow[({1: "NONE", 2: "PARKED", 3: "RESEED"}.get(e, e), r)] += 1
        for tb, ch in ends:
            if tb == "fd" and ch not in (None, "none", "-"):
                fdrows[ch] += 1
        wr = s.get("wr") or {}
        if wr.get("rc") == 0 and wr.get("run_stated"):
            runs += 1
            rdiff += wr.get("has_stop") and wr.get("stop") != wr.get("run_member")
print("PF sites", pf, "with >=2 alternatives", pf2)
print("FUNC/handoff-0 window sites", ofs, "site_kind UNSTATED", ofs_k0)
print("entry x Table A row", dict(arow))
print("replies stating a run", runs, "stop != run member", rdiff)
print("fd rows", dict(fdrows))
