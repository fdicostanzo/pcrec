#!/usr/bin/env python3
"""[WORD-FOLD] renders the population tables `wordfold_census.md` cites,
from `wf_census.json` (the run-length census), `wf_stamps.json` (engine
routes for the qualifying population) and `wf_offsetk.json` (the (?i)
offset-k degradation walk). Read-only; writes `wf_summary.txt`.
"""
import json, sys, collections

CENSUS = json.load(open("wf_census.json"))
STAMPS = json.load(open("wf_stamps.json"))
OFFK = json.load(open("wf_offsetk.json"))

out = []
def p(*a):
    s = " ".join(str(x) for x in a)
    out.append(s)


def length_table(pop, rows):
    ge4 = [r for r in rows if int(r["best_len"]) >= 4]
    ge8 = [r for r in rows if int(r["best_len"]) >= 8]
    def split(rs):
        ex = [r for r in rs if int(r["n_cube_ns"]) == 0]
        cn = [r for r in rs if int(r["n_cube_ns"]) > 0]
        return len(rs), len(ex), len(cn)
    n = len(rows)
    p("%s: N=%d" % (pop, n))
    p("  >=4 bytes: %d (all-exact %d, has-cube-nonsingleton %d)" % split(ge4))
    p("  >=8 bytes: %d (all-exact %d, has-cube-nonsingleton %d)" % split(ge8))


for pop in ("bench", "corpus", "corpus_utf8"):
    length_table(pop, CENSUS[pop])

p("")
p("caseless population (pattern text contains '(?i)' or '(?i:'):")
for pop in ("bench", "corpus"):
    rows = CENSUS[pop]
    cl = [r for r in rows if int(r.get("is_caseless", 0)) == 1]
    cl4 = [r for r in cl if int(r["best_len"]) >= 4]
    p("  %s: %d caseless patterns, %d with a run >= 4" % (pop, len(cl), len(cl4)))

p("")
p("engine route, qualifying population (best_len >= 4):")
for pop in ("bench", "corpus"):
    rows = STAMPS[pop]
    eng = collections.Counter(r.get("RX_ENGINE") for r in rows)
    p("  %s: %s" % (pop, dict(eng)))
    vm = [r for r in rows if r.get("RX_ENGINE") == "vm"]
    fl = collections.Counter(r.get("RX_VM_FRAMELESS") for r in vm)
    p("    vm-route RX_VM_FRAMELESS dist: %s" % dict(fl))
    cns = [r for r in rows if int(r["n_cube_ns"]) > 0]
    p("    cube-nonsingleton rows (%d):" % len(cns))
    for r in cns:
        p("      %-55s len=%-3s engine=%-4s frameless=%s" %
          (r["id"], r["best_len"], r.get("RX_ENGINE"), r.get("RX_VM_FRAMELESS")))

p("")
p("(?i) offset-k walk (D7 fast-path population only, k0 read as unconstrained):")
rows = OFFK["rows"]
ok = [r for r in rows if r["status"] == "ok"]
ref = [r for r in rows if r["status"] != "ok"]
inv = [r for r in ok if r["any_invariant"] == "1"]
noinv = [r for r in ok if r["any_invariant"] == "0"]
p("  caseless patterns probed: %d (refused/bot-anchored, out of scope: %d)" % (len(rows), len(ref)))
p("  walk producible: %d" % len(ok))
p("  has >=1 case-invariant offset: %d" % len(inv))
p("  fully degraded (no invariant offset anywhere): %d" % len(noinv))
p("  fully-degraded ids:")
for r in noinv:
    p("    " + r["id"])

open("wf_summary.txt", "w").write("\n".join(out) + "\n")
print("wrote wf_summary.txt (%d lines)" % len(out), file=sys.stderr)
