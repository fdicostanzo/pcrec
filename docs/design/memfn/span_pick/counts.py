#!/usr/bin/env python3
"""span_pick rev 3: re-count the populations the note quotes, from R-33's raw sweep, split by ARM
(RTE = the default compile; DEF = the 43-pattern `--memfn=no-window-search,no-window-skip` recompile,
not a distinct site; review r2 R4).
    python3 -I counts.py SWEEP.jsonl"""
import collections
import json
import sys

C = collections.defaultdict(collections.Counter)
ENT = {1: "NONE", 2: "PARKED", 3: "RESEED"}
for line in open(sys.argv[1]):
    rec = json.loads(line)
    c = C["DEF" if rec.get("arm") == "DEF" else "RTE"]
    for s in rec["sites"]:
        alts = s.get("alts") or []
        if s.get("deleg") == "PF" and s.get("alts") is not None:
            c["PF sites"] += 1
            c["PF sites with >=2 alternatives"] += len(alts) >= 2
            ents = sorted(ENT.get(a["entry"], a["entry"]) for a in alts)
            c["PF alternatives " + "+".join(ents)] += 1
            for a in alts:
                if a["entry"] == 3:
                    n = sum(sp["core_len"] for sp in a["spans"] if sp.get("core"))
                    c["PF RESEED core positions " + ("1" if n == 1 else ">=2")] += 1
        if s.get("form") == 2 and s.get("handoff") == 0 and alts:
            c["FUNC/handoff-0 window sites"] += 1
            c["  of which site_kind UNSTATED"] += s.get("site_kind") == 0
        tr = s.get("trace") or {}
        ends = tr.get("ends", [])
        a = [ch for tb, ch in ends if tb == "wfA" and ch not in (None, "none", "-")]
        for e, r in zip([al["entry"] for al in alts], a):
            c["Table A %s %s" % (ENT.get(e, e), r)] += 1
            c["alternatives %s" % ENT.get(e, e)] += 1
        for tb, ch in ends:
            if tb == "fd" and ch not in (None, "none", "-"):
                c["fd row " + ch] += 1
        wr = s.get("wr") or {}
        if wr.get("rc") == 0 and wr.get("run_stated"):
            c["replies stating a run"] += 1
            c["  stop != run member"] += bool(wr.get("has_stop") and wr.get("stop") != wr.get("run_member"))
keys = sorted(set(C["RTE"]) | set(C["DEF"]))
print("%-46s %7s %5s %7s" % ("count", "RTE", "DEF", "total"))
for k in keys:
    print("%-46s %7d %5d %7d" % (k, C["RTE"][k], C["DEF"][k], C["RTE"][k] + C["DEF"][k]))
