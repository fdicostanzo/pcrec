#!/usr/bin/env python3
"""span_pick rev 2: census of the hand row ONE-STREAM over R-33's raw sweep, and smp20's prices
under rev 2's formula. Reuses R-33's committed sim.py (candidate builder, mass) unchanged.

    python3 -I onestream.py SIMDIR SWEEP.jsonl
"""
import collections
import importlib.util
import json
import sys

spec = importlib.util.spec_from_file_location("sim", sys.argv[1] + "/sim.py")
sim = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sim)
PPM = 1_000_000
rates = json.load(open(sys.argv[2] + ".rates.json"))


def row(alt, rate):
    """ONE-STREAM: entry NONE; the A-mass answer (least prior mass, lower offset on a tie) has
    k >= 2 members; some one-member candidate's prior mass <= the A-mass answer's FLAT mass
    (k x 1e6 / 256, floored). Returns (today, row_pick or None, cands)."""
    cands = sim.plans(alt, rate, "A", sim.CONST)
    if not cands:
        return None, None, cands
    today = min(cands, key=lambda p: (p["mass"], p["off"]))
    if today["k"] < 2:
        return today, None, cands
    flat = today["k"] * PPM // 256
    ones = [p for p in cands if p["k"] == 1 and p["mass"] <= flat]
    if not ones:
        return today, None, cands
    return today, min(ones, key=lambda p: (p["mass"], p["off"])), cands


movers = collections.OrderedDict()
holds_none = collections.Counter()
nunits = 0
for line in open(sys.argv[2]):
    rec = json.loads(line)
    for u in sim.units(rec):
        rate = (rates.get(u["rate"]) or {}).get("rate")
        for ai, alt in enumerate(u["alts"]):
            if alt["entry"] != 1:          # NONE only
                continue
            nunits += 1
            today, pick, cands = row(alt, rate)
            if today is None:
                holds_none["no-cand"] += 1
                continue
            if pick is None:
                holds_none["k1" if today["k"] < 2 else "no-one-byte-under-flat"] += 1
                continue
            key = (rec["pat"], u["kind"])
            movers.setdefault(key, []).append((rec["src"], rec["id"], rec["arm"], u["kind"],
                                               sim.setstr(today["set"]), today["off"], today["mass"],
                                               sim.setstr(pick["set"]), pick["off"], pick["mass"],
                                               today["k"] * PPM // 256))
print("NONE alternatives:", nunits, dict(holds_none))
print("row holds on", sum(len(v) for v in movers.values()), "units,", len(movers), "distinct (pattern, kind)")
for (pat, kind), v in movers.items():
    src = sorted(set("%s/%s/%s" % (s, i, a) for s, i, a, *_ in v))
    t = v[0]
    print("%-34r %-10s today @%d %s m%d -> @%d %s m%d (flat %d)  [%s]" % (
        pat, kind, t[5], t[4], t[6], t[8], t[7], t[9], t[10], ", ".join(src[:4]) + (" +%d" % (len(src) - 4) if len(src) > 4 else "")))

# smp20 under rev 2's formula (Zen 1 plan_cost.def constants, c_hit 20 c per candidate returned)
rt = rates["a322116b1b87f9f6"]["rate"]
C_SCAN, C_HIT, C_VER, C_ENTER = 0.06, 20.0, 2.5, 20.0


def price(m_stop, streams, others, c_hit):
    vr, pr = 0.0, 1.0
    for mo in sorted(others):
        vr += pr * C_VER
        pr *= mo / PPM
    return streams * C_SCAN * PPM + m_stop * c_hit + m_stop * vr + m_stop * pr * C_ENTER


for model in ("P", "F"):
    if model == "P":
        mx, ms, md = rt[ord('x')] + rt[ord('X')], rt[ord('/')], rt[ord('1')]
    else:
        mx, ms, md = 2 * PPM / 256, PPM / 256, PPM / 256
    for ch in (C_HIT, 2 * C_HIT):
        pair = price(mx, 2, [ms] + [md] * 4, ch)
        one = price(ms, 1, [mx] + [md] * 4, C_HIT)
        print("smp20 %s c_hit(PAIR)=%g: {x,X} PAIR %.1f  '/' memchr %.1f  ratio pair/one %.4f" % (model, ch, pair, one, pair / one))
