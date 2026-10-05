#!/usr/bin/env python3
"""[START-SET] edge lane: print the route, sets and hat verdict of one pattern.
    classify.py PATTERN [flags=iu] [enc=utf8] [engine=vm] [xflags=-futf-check,...]
Env: PCREC, FSP, W.  A probe for choosing cells; nothing reads its output."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hat

b = {"pat": sys.argv[1]}
for kv in sys.argv[2:]:
    k, v = kv.split("=", 1)
    b[k] = v.split(",") if k == "xflags" else (int(v) if k == "frames" else v)
o = hat.classify(b, os.path.join(os.environ["W"], "cls"))
if o["status"] != "ok":
    print("REFUSED", o["err"]); sys.exit(0)
m = o["m"]
fmt = lambda s: "-" if s is None else ("%d" % len(s))
print("%-34s hat=%-11s eng=%s vmpf=%s dfapf=%s scan=%s handoff=%s |S|=%s null=%s" % (
    b["pat"], o["hat"], o["engine"], o["vmpf"], o["dfapf"], o["scan"], o["handoff"], fmt(o["S"]), o["nullable"]), end="")
if m:
    print(" seeded=%d nseeds=%d |E|=%d |E*|=%d |Tdfa|=%d S\\E=%s" % (m["seeded"], len(m["seeds"]), len(m["E"]), len(m["Estar"]), len(m["Tdfa"]),
          sorted(o["S"] - m["E"]) if o["S"] is not None else "-"))
else:
    print()
