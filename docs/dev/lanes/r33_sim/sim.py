#!/usr/bin/env python3
"""docs/dev/lanes/r33_sim/sim.py -- R-33's SIMULATION of the inner-first "find the span" pick.

    python3 -I sim.py IN.jsonl OUTDIR [--key A|B] [--h-hit C] [--walk C]

Reads collect.py's records (TODAY's answer per site, as compiled) and, for every DECISION UNIT (a
window site's stated alternatives, or a pre-check's window-stating FUNC part), simulates the
owner's ordering (R-33, memfn/docs/requests.md):

  1. fixed facts: the frame (form/op/handoff, read from the site), the alternatives as stated;
  2. candidates: per alternative, every stated offset after the kit's own C-meet (the AND of every
     covering span's set; window.c `merge`) that is CORE and not the full set (the same domain as
     A-mass's `mass_domain`), with its set;
  3. per candidate, LOCAL rules: method by member count (1 = memchr, one stream; 2 = two-stream
     PAIR; 3+ = table walk, NOT a stream); verify = every OTHER stated, non-full offset the
     alternative's plan may read (a PARKED one: its verify-YES facts only), tested in ascending mass
     with early exit (expected tests = 1 + p1 + p1 p2 + ..., p = mass / 1e6, positions INDEPENDENT:
     an ASSUMPTION), then the matcher entered on a pass (probability p1 p2 ...);
  4. the position picked LAST over the complete per-candidate plans, on a fact-derived key; then the
     alternative one level up (plain least score; today's MARGIN 2x factor is NOT applied).

THE KEY, in cycles per 1e6 subject bytes (mass = kit_set_sum semantics: ppm summed over the set's
members under the art's byte-rate, uniform cardinality without one):
  KEY A (the request's words): mass x streams x H_HIT + mass x VERIFY_PER_HIT;
         a walk: 1e6 x C_WALK + mass x VERIFY_PER_HIT;
         VERIFY_PER_HIT = E[tests] x C_VERIFY + P(pass) x C_ENTER.
  KEY B: KEY A + streams x 1e6 x C_SCAN (every memchr stream also pays its per-byte scan).
CONSTANTS and their basis (labelled; nothing here is a new measurement):
  H_HIT   20 c per stream hit (a memchr return + restart)   ASSUMPTION (no measurement on file)
  C_WALK  1.16 c per byte, the table walk                   plan_cost.def C_BITMAP, MEASURED Zen 1
  C_SCAN  0.06 c per byte per memchr stream                 plan_cost.def C_MEMCHR, MEASURED Zen 1
  C_VERIFY 2.5 c per tested offset                          plan_cost.def C_VERIFY, UNMEASURED DEFAULT
  C_ENTER 20 c per matcher entry                            plan_cost.def C_ENTER, MEASURED x ASSUMED Zen 1
Ties: the candidate equal to today's stop is preferred, then the lower offset (marked `tie`).
Not modelled (labelled in the output): Horspool (D-hors) as a method, C-pin's whole-run compare,
the walk's per-hit exit, SIMD forms, the PARKED alternative's reseed obligation at a non-k0 stop.
"""
import argparse
import collections
import json
import os

PPM = 1_000_000
CONST = {"H_HIT": 20.0, "C_WALK": 1.16, "C_SCAN": 0.06, "C_VERIFY": 2.5, "C_ENTER": 20.0}
ENTRY = {0: "UNSTATED", 1: "NONE", 2: "PARKED", 3: "RESEED"}
METHOD_OF_ROW = {
    "D1": "memchr", "D1w": "memchr", "D1c": "memchr-back", "PAIR": "pair", "R7w": "walk",
    "fn-memchr": "memchr", "fn-pair": "pair", "pf_memchr": "memchr", "pf_memchr_bounded": "memchr",
    "pf_memchr_back": "memchr-back", "pf_walk": "walk", "pf_walk_bounded": "walk",
}


def setbits(hexs):
    b = bytes.fromhex(hexs)
    return frozenset(x for x in range(256) if b[x >> 3] >> (x & 7) & 1)


def mass(rate, s):
    if rate is None:
        return len(s) * PPM // 256
    return sum(rate[b] for b in s)


def merge(alt):
    pos = {}
    for sp in alt["spans"]:
        for j, h in enumerate(sp["sets"]):
            off = sp["start"] + j
            st = setbits(h)
            p = pos.setdefault(off, {"set": frozenset(range(256)), "core": False,
                                     "yset": frozenset(range(256)), "yes": False, "ycore": False})
            p["set"] = p["set"] & st
            incore = sp["core_lo"] <= j < sp["core_lo"] + sp["core_len"]
            if incore:
                p["core"] = True
            if sp["verify"] == 1:                         # MF_VERIFY_YES
                p["yes"] = True
                p["yset"] = p["yset"] & st
                if incore:
                    p["ycore"] = True
    return pos


def method_of(k):
    return "memchr" if k == 1 else "pair" if k == 2 else "walk"


def score(key, c, m, k, etests, ppass, method=None):
    """The key for a plan of `k` members found by `method` (default: the local rule's by k).
    TODAY's plan is scored with TODAY's method: a walk, a D-hors shift, a generic loop and a
    loop-only fn arm are all priced as the walk (an ASSUMPTION for the last three)."""
    ver = m * (etests * c["C_VERIFY"] + ppass * c["C_ENTER"])
    method = method or method_of(k)
    if method in ("memchr", "memchr-back", "pair"):
        streams = 2 if method == "pair" else 1
        s = m * streams * c["H_HIT"] + ver
        if key == "B":
            s += streams * PPM * c["C_SCAN"]
        return s
    return PPM * c["C_WALK"] + ver


def plans(alt, rate, key, c):
    """Every candidate stop of one alternative with its complete plan. On a PARKED alternative the
    plan reads only the verify-YES facts (window.c `rd_set`: the parked machine's own; a stop
    elsewhere would oblige a re-seed, C-pin's case, not modelled), so its candidates are the
    verify-YES core positions over their YES sets and its verify the other YES positions."""
    pos = merge(alt)
    full = frozenset(range(256))
    parked = alt["entry"] == 2
    sk, ck = ("yset", "ycore") if parked else ("set", "core")
    out = []
    for off, p in sorted(pos.items()):
        if parked and not p["yes"]:
            continue
        if not p[ck] or p[sk] == full or not p[sk]:
            continue
        m = mass(rate, p[sk])
        others = sorted(mass(rate, q[sk]) for o, q in pos.items()
                        if o != off and (q["yes"] or not parked) and q[sk] != full)
        et, pr = 0.0, 1.0
        for mo in others:
            et += pr
            pr *= min(mo, PPM) / PPM
        k = len(p[sk])
        out.append({"off": off, "set": p[sk], "k": k, "mass": m, "method": method_of(k),
                    "verify": len(others), "etests": round(et, 4), "ppass": pr,
                    "score": score(key, c, m, k, et, pr)})
    return out


def today_method(site, part_ix=None):
    t = site["trace"]
    ends = t["ends"]
    tab = collections.defaultdict(list)
    for tb, ch in ends:
        if ch not in (None, "none", "-"):
            tab[tb].append(ch)
    frame = tab["wfE"][0] if tab["wfE"] else "?"
    if part_ix is not None:
        fns = tab["fn"]
        # The fn BODY walks do not carry the part's index: the i-th chosen BODY row is ASSUMED to
        # be part i's; a part past the count is `unobserved` (not compared on method).
        return frame, (METHOD_OF_ROW.get(fns[part_ix], fns[part_ix]) if part_ix < len(fns) else "unobserved"), "fn"
    if "D-hors" in tab["wfD"]:
        return frame, "hors", "D-hors"
    if t["fdroute"]:
        return frame, METHOD_OF_ROW.get(t["fdroute"], t["fdroute"]), t["fdroute"]
    if frame == "E-func":
        fns = tab["fn"]
        return frame, (METHOD_OF_ROW.get(fns[0], fns[0]) if fns else "loop"), (fns[0] if fns else "-")
    if frame == "E-find":
        return frame, "loop", "-"
    return frame, "generic", "-"


def units(rec):
    """Each decision unit of one compile: (kind, alts, wr, today-frame, today-method, deciding rows)."""
    for si, s in enumerate(rec["sites"]):
        deleg = s.get("deleg", "?")
        if s.get("alts"):
            frame, meth, mrow = today_method(s)
            arows = [ch for tb, ch in s["trace"]["ends"] if tb == "wfA"]
            mrow_m = [ch for tb, ch in s["trace"]["ends"] if tb == "wfM"]
            yield {"kind": deleg, "si": si, "alts": s["alts"], "wr": s["wr"], "frame": frame,
                   "today_method": meth, "method_row": mrow, "arows": arows, "mrow": mrow_m,
                   "rate": s.get("rate")}
        pi = 0
        for p in s.get("preds", []):
            if "part" in p:
                frame, meth, mrow = today_method(s, pi)
                yield {"kind": deleg + ":part", "si": si, "alts": p["part"]["alts"], "wr": p["wr"],
                       "frame": "E-func", "today_method": meth, "method_row": mrow, "arows": [],
                       "mrow": [], "rate": s.get("rate")}
                pi += 1


def setstr(s):
    s = sorted(s)
    if len(s) > 4:
        return "{%d bytes}" % len(s)
    return "{" + ",".join(chr(b) if 0x21 <= b < 0x7f else "\\x%02x" % b for b in s) + "}"


def simulate(u, rates, key, c):
    rate = (rates.get(u["rate"]) or {}).get("rate")
    wr = u["wr"]
    allp = []
    for ai, alt in enumerate(u["alts"]):
        for p in plans(alt, rate, key, c):
            p["alt"] = ai
            p["entry"] = ENTRY.get(alt["entry"], "?")
            allp.append(p)
    today = None
    if wr.get("rc") == 0 and wr.get("has_stop"):
        tset = setbits(wr["stop_set"])
        for p in allp:
            if p["alt"] == wr["alt"] and p["off"] == wr["stop"]:
                today = dict(p, method=u["today_method"],
                             score=score(key, c, p["mass"], p["k"], p["etests"], p["ppass"], u["today_method"]))
        today_d = {"alt": wr["alt"], "off": wr["stop"], "set": tset, "k": len(tset),
                   "path": wr["path"], "in_domain": today is not None}
    else:
        today_d = {"alt": wr.get("alt"), "off": None, "set": None, "k": 0,
                   "path": wr.get("path", "rc=%s" % wr.get("rc")), "in_domain": False}
    if not allp:
        return today_d, None, today, allp
    best = min(allp, key=lambda p: (p["score"], 0 if (today and p["alt"] == today["alt"] and p["off"] == today["off"]) else 1, p["off"]))
    best["tie"] = sum(1 for p in allp if p["score"] == best["score"]) > 1
    return today_d, best, today, allp


def classify(u, td, best):
    if best is None:
        return "agree" if td["off"] is None else "differ-stop"
    if td["off"] is None:
        return "differ-floor"
    if td["off"] != best["off"] or td["set"] != best["set"]:
        return "differ-alt" if td["alt"] != best["alt"] and len(u["alts"]) > 1 else "differ-stop"
    if u["today_method"] in ("hors", "unobserved"):
        return "agree-stop(%s)" % u["today_method"]
    if u["today_method"] != best["method"] and not (u["today_method"] == "memchr-back" and best["method"] == "memchr"):
        return "differ-method"
    return "agree"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("outdir")
    ap.add_argument("--key", default="A")
    ap.add_argument("--h-hit", type=float, default=CONST["H_HIT"])
    ap.add_argument("--walk", type=float, default=CONST["C_WALK"])
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    c = dict(CONST, H_HIT=a.h_hit, C_WALK=a.walk)
    rates = json.load(open(a.inp + ".rates.json"))
    os.makedirs(a.outdir, exist_ok=True)
    tag = a.tag or "key%s" % a.key
    rows, summ = [], collections.Counter()
    for line in open(a.inp):
        rec = json.loads(line)
        for u in units(rec):
            td, best, today, allp = simulate(u, rates, a.key, c)
            verdict = classify(u, td, best)
            kind = u["kind"]
            summ[(rec["src"], rec["arm"], kind, verdict)] += 1
            gap = (today["score"] / best["score"]) if (today and best and best["score"]) else None
            rows.append({
                "src": rec["src"], "id": rec["id"], "arm": rec["arm"], "pat": rec["pat"], "kind": kind,
                "si": u["si"], "verdict": verdict, "frame": u["frame"], "arows": "/".join(u["arows"]),
                "mrow": "/".join(u["mrow"]), "today_path": td["path"],
                "today_alt": td["alt"], "today_off": td["off"],
                "today_set": setstr(td["set"]) if td["set"] is not None else "-",
                "today_k": td["k"], "today_method": u["today_method"], "today_row": u["method_row"],
                "today_score": round(today["score"], 1) if today else None,
                "today_mass": today["mass"] if today else None,
                "sim_alt": best["alt"] if best else None, "sim_entry": best["entry"] if best else None,
                "sim_off": best["off"] if best else None,
                "sim_set": setstr(best["set"]) if best else "-", "sim_k": best["k"] if best else 0,
                "sim_method": best["method"] if best else "floor",
                "sim_mass": best["mass"] if best else None,
                "sim_etests": best["etests"] if best else None,
                "sim_score": round(best["score"], 1) if best else None,
                "tie": best.get("tie") if best else None,
                "gap": round(gap, 3) if gap else None,
                "ncand": len(allp),
                "cands": ";".join("a%d@%d%s k%d m%d %s s%.0f" % (p["alt"], p["off"], setstr(p["set"]), p["k"],
                                                               p["mass"], p["method"], p["score"]) for p in allp[:12]),
            })
    cols = list(rows[0].keys()) if rows else []
    with open(os.path.join(a.outdir, "units_%s.tsv" % tag), "w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join("" if r[k] is None else str(r[k]).replace("\t", "\\t").replace("\n", "\\n")
                              for k in cols) + "\n")
    with open(os.path.join(a.outdir, "summary_%s.tsv" % tag), "w") as f:
        f.write("src\tarm\tkind\tverdict\tn\n")
        for (s, arm, k, v), n in sorted(summ.items()):
            f.write("%s\t%s\t%s\t%s\t%d\n" % (s, arm, k, v, n))
    print("== r33 sim %s: %d units" % (tag, len(rows)))


if __name__ == "__main__":
    main()
