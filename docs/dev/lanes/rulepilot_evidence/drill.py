#!/usr/bin/env python3
"""rulepilot: the search's DRILL on synthetic ground truth (docs/design/pricing_rulepilot.md §6).

Builds datasets in search.py's input shape, the real job's shape (139 sites, the real pick vocabulary, 3
log-spaced lengths x 2 density regimes, 3 launches, the base launched three times, a measured
per-launch noise of 1.5 %), and runs the SAME search.run on them. Four truths:

  (a) PLANTED  a 2-rule truth: "if req_run_len >= 3 -> no-offset-skip; elif dflt_presence ->
               k:no-fd-pres-g1; else default"; every other arm 1.3-2.5x slower.   MUST PASS at <= 2.
  (b) BEYOND   the best pick is a 4-way parity of four BOOL pieces (no 3-rule list can say it);
               wrong picks 1.6-2.5x slower.                                        MUST FAIL.
  (c) NOISE    every arm's cost iid 1.0-2.0x, unrelated to every piece.             MUST NOT PASS.
  (d) NULL     every arm the same program in truth, noise only.                    MUST PASS at 0
               (a control on the tail bar: noise alone must not read as a loss).

usage: drill.py [SEED]      prints each drill's search report and one verdict line per drill
"""
import os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import search
from pieces import PIECES

# the REAL pick vocabulary (inventory/vocabulary.tsv: the default + every census deny set), so the
# drill's over-fit is the real search's over-fit
PICKS = [l.split("\t")[0] for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                    "inventory", "vocabulary.tsv")).read().splitlines()[1:]]
LENS = [64, 8192, 1048576]
DENS = ["miss", "dense"]
N_SITES, LAUNCHES, NOISE = 139, 3, 0.015
STRATA = ["FIRST+NEXT", "NEXT", "LOCATE+NEXT", "FIRST+PRESENCE", "(bytes only)", "FIRST+NEXT+PRESENCE"]

def pieces_of(rng):
    v = {}
    for n, (t, _, _) in PIECES.items():
        v[n] = rng.randint(0, 1) if t == "BOOL" else rng.choice([0, 0, 1, 2, 3, 4, 5, 6, 8, 10])
    return v

def site(rng, i, truth):
    pv = pieces_of(rng)
    # pick -> arm: about half the picks move the bytes on a site, as the census reads
    picks = {"default": "a0"}; n = 1
    want = truth("pick", pv, rng)
    for p in PICKS[1:]:
        if p == want or rng.random() < 0.45:
            picks[p] = "a%d" % n; n += 1
        else:
            picks[p] = "a0"
    arms = sorted(set(picks.values()))
    fac = truth("cost", pv, rng, picks=picks, arms=arms, want=want)
    cells = {}
    for d in DENS:
        for L in LENS:
            base_ns = 20 + L * (0.3 if d == "miss" else 1.2)
            av = {}
            for a in arms:
                f = fac[a] * rng.uniform(0.97, 1.03)
                av[a] = [base_ns * f * rng.lognormvariate(0, NOISE) for _ in range(LAUNCHES)]
            for cp in ("#b", "#c"):
                av["a0" + cp] = [base_ns * fac["a0"] * rng.lognormvariate(0, NOISE) for _ in range(LAUNCHES)]
            cells[f"{d}/{L}"] = av
    return dict(id="S%03d" % i, stratum=rng.choice(STRATA), pieces=pv, picks=picks, cells=cells)

def planted(kind, pv, rng, **k):
    want = ("no-offset-skip" if pv["req_run_len"] >= 3 else
            "k:no-fd-pres-g1" if pv["dflt_presence"] else "default")
    if kind == "pick":
        return want
    return {a: 1.0 if a == k["picks"][want] else rng.uniform(1.3, 2.5) for a in k["arms"]}

PAR = ["no-start-set", "no-run-prefilter", "k:no-fd-pres-g1", "no-req-handoff"]
def beyond(kind, pv, rng, **k):
    want = PAR[2 * (pv["anchored"] ^ pv["nullable"]) + (pv["caseless"] ^ pv["utf"])]
    if kind == "pick":
        return want
    return {a: 1.0 if a == k["picks"][want] else rng.uniform(1.6, 2.5) for a in k["arms"]}

def noise_truth(kind, pv, rng, **k):
    if kind == "pick":
        return None
    return {a: rng.uniform(1.0, 2.0) for a in k["arms"]}

def null_truth(kind, pv, rng, **k):
    if kind == "pick":
        return None
    return {a: 1.0 for a in k["arms"]}

def dataset(truth, seed):
    rng = random.Random(seed)
    return dict(picks=PICKS, sites=[site(rng, i, truth) for i in range(N_SITES)])

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 20261031
    pt = {n: t for n, (t, _, _) in PIECES.items()}
    # (a) must pass at exactly 2 rules AND name the planted literals in the planted order
    expect = {"a-planted": lambda r: (r["verdict"] == "PASS at 2 rule(s)"
                                      and r["lists"][2]["text"].startswith("if req_run_len >= 3 (FITTED) -> no-offset-skip; if dflt_presence -> k:no-fd-pres-g1")),
              "b-beyond": lambda r: r["verdict"].startswith("FAIL"),
              "c-noise": lambda r: r["verdict"].startswith("FAIL"),
              "d-null": lambda r: r["verdict"] == "PASS at 0 rule(s)"}
    ok = True; lines = []
    for name, truth in (("a-planted", planted), ("b-beyond", beyond), ("c-noise", noise_truth), ("d-null", null_truth)):
        print(f"=== drill {name} (seed {seed})")
        r = search.run(dataset(truth, seed), pt)
        good = expect[name](r); ok &= good
        lines.append(f"drill {name}: {r['verdict']} -> {'AS INTENDED' if good else 'NOT AS INTENDED'}")
        print()
    print("\n".join(lines))
    print("DRILL: " + ("ALL FOUR AS INTENDED" if ok else "A DRILL DID NOT LAND"))
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
