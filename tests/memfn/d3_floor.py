#!/usr/bin/env python3
"""tests/memfn/d3_floor.py -- R-38 Part D D3's PCREC-ARTIFACT FLOOR (part_d.md §5.1 D3 [r3pd RDY-5], §9 item 9;
requests R-43, R-44). Run by tests/memfn/run_d3floor.sh (`make test-memfn-d3floor`; also the last step of
`make test-axes`, so the battery's axes stage runs it).

    python3 -I d3_floor.py --tree TREE [--floors tests/memfn/d3_floor.tsv] [--no-self-test]
                           CELL=SWEEP.jsonl ... [--movers CELL=MOVERS.tsv ...]

CELL is one of emit_sweep's (base, stream) cells for the deny `--memfn=no-run-verify-wide`: byte/c-default,
byte/c-vm, utf8/c-default, utf8/c-vm. SWEEP is collect.py's corpus sweep of that cell (`--sources corpus --flags`:
nothing, `--engine=vm`, `-e utf8`, `-e utf8 --engine=vm`).

THE FLOORS are DATA, not literals here: d3_floor.tsv (its header names the census, commit and who set each value).
THE CENSUS (per cell): the DISTINCT corpus patterns (`pat_hex`) that compiled and carry at least one
`run_part_terms` record ON THE SHIPPED (last) art holding an UNSPELLED SET term (census0.py's parser and
`run_part_unspelled`: members not one byte and not a cube).
THE CHECK, per cell: the sweep is a POPULATION that is counted and printed (compiles >= min_compiles, records >=
min_records: a zero or short sweep reds, learnings §3); census >= census_floor; census_floor >= movers; and
census_floor >= emit_sweep's live DIFFER_PINS floor for the cell (read from TREE, so a pcrec re-pin above the census
reds here and is looked at). `--movers CELL=MOVERS.tsv` (deny_reach.py's output): every mover is in the census, else
`MOVER-WITHOUT-RECORD` and red. Not part of the gate (it needs a second sweep per cell).
SELF-TEST (default on; the plants live here so the gate shows it can fail): S3228 drops mover patterns' records from
the real sweep (census = floor-1 reds; census = floor stays green: the control), S3229 an empty and a truncated
sweep (the population check reds), S3230 a floor table with census_floor below its movers (reds).
Exit 0 green, 1 red (a cell, or a plant that did NOT go red).
"""
import argparse
import json
import os
import sys

CELLS = ("byte/c-default", "byte/c-vm", "utf8/c-default", "utf8/c-vm")
DENY = "--memfn=no-run-verify-wide"
HERE = os.path.dirname(os.path.abspath(__file__))


def load_floors(path):
    rows, cols = {}, None
    for ln in open(path):
        ln = ln.rstrip("\n")
        if not ln or ln.startswith("#"):
            continue
        f = ln.split("\t")
        if cols is None:
            cols = f
            continue
        r = dict(zip(cols, f))
        for k in ("census_floor", "movers", "min_compiles", "min_records"):
            r[k] = int(r[k])
        rows[r["cell"]] = r
    for c in CELLS:
        if c not in rows:
            sys.exit("d3_floor: %s has no row for cell %s" % (path, c))
    return rows


def load_census0(tree):
    sys.path.insert(0, os.path.join(tree, "docs/design/memfn/span_pick"))
    import census0  # noqa: E402
    return census0


def census(lines, c0):
    """(the set of pat_hex with a shipped-art record holding an unspelled SET term, compiles, records)"""
    hit, n, nrec = set(), 0, 0
    for rec in lines:
        if rec.get("rc") != 0:
            continue
        n += 1
        for s in rec.get("sites", []):
            if s.get("art") != rec["arts"]:
                continue
            for ln in s.get("trace", {}).get("parts", []):
                r = c0.run_part_record(ln)
                nrec += 1
                if r and c0.run_part_unspelled(r) > 0:
                    hit.add(rec["pat_hex"])
    return hit, n, nrec


def pin_floor(tree, cell):
    sys.path.insert(0, os.path.join(tree, "scripts"))
    import emit_sweep  # noqa: E402
    base, stream = cell.split("/")
    v = emit_sweep.DIFFER_PINS.get((base, DENY, stream))
    return None if v is None else v[0]


def verdict(cell, fl, hit, n, nrec, pin):
    """the reasons a cell is red (empty list = green)"""
    why = []
    if n < fl["min_compiles"]:
        why.append("population: %d compiles counted, below the %d the sweep must hold" % (n, fl["min_compiles"]))
    if nrec < fl["min_records"]:
        why.append("population: %d run_part_terms records counted, below %d" % (nrec, fl["min_records"]))
    if len(hit) < fl["census_floor"]:
        why.append("census %d below its floor %d" % (len(hit), fl["census_floor"]))
    if fl["census_floor"] < fl["movers"]:
        why.append("the census floor %d is below the deny's movers %d" % (fl["census_floor"], fl["movers"]))
    if pin is None:
        why.append("emit_sweep DIFFER_PINS has no (%s, %s) cell" % (cell, DENY))
    elif fl["census_floor"] < pin:
        why.append("the census floor %d is below emit_sweep's DIFFER floor %d" % (fl["census_floor"], pin))
    return why


def pairs(xs, what):
    out = {}
    for x in xs:
        cell, _, path = x.partition("=")
        if cell not in CELLS or not path:
            sys.exit("d3_floor: %s %r is not CELL=PATH with CELL one of %s" % (what, x, ", ".join(CELLS)))
        out[cell] = path
    return out


def drop_records(recs, pats):
    """S3228's plant: the same sweep with the derived-part records of the named patterns removed"""
    out = []
    for rec in recs:
        if rec.get("pat_hex") in pats:
            rec = dict(rec, sites=[dict(s, trace=dict(s.get("trace", {}), parts=[])) for s in rec.get("sites", [])])
        out.append(rec)
    return out


def self_test(floors, tree, c0, cell, recs, hit, n, nrec, pin):
    """every plant must go RED and its control GREEN; returns the failure texts"""
    bad = []
    fl = floors[cell]

    def run(tag, fl_, recs_, want_red, needle=""):
        h, n_, r_ = census(recs_, c0)
        why = verdict(cell, fl_, h, n_, r_, pin)
        got = "; ".join(why)
        ok = (bool(why) == want_red) and (not want_red or needle in got)
        print("D3-FLOOR-PLANT %s %s compiles=%d records=%d census=%d floor=%d -> %s %s"
              % (tag, cell, n_, r_, len(h), fl_["census_floor"], "RED" if why else "green", "ok" if ok else "WRONG"))
        if not ok:
            bad.append("%s %s: wanted %s%s, got %r" % (tag, cell, "red" if want_red else "green",
                                                      " (%s)" % needle if needle else "", got))

    slack = len(hit) - fl["census_floor"]
    order = sorted(hit)
    run("control", fl, recs, False)
    run("S3228-at-floor", fl, drop_records(recs, set(order[:slack])), False)
    run("S3228-below-floor", fl, drop_records(recs, set(order[:slack + 1])), True, "below its floor")
    run("S3229-empty", fl, [], True, "population")
    run("S3229-truncated", fl, recs[:100], True, "population")
    run("S3230-floor-below-movers", dict(fl, census_floor=fl["movers"] - 1), recs, True, "below the deny's movers")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True)
    ap.add_argument("--floors", default=os.path.join(HERE, "d3_floor.tsv"))
    ap.add_argument("--no-self-test", action="store_true")
    ap.add_argument("sweeps", nargs="+", metavar="CELL=SWEEP.jsonl")
    ap.add_argument("--movers", action="append", default=[], metavar="CELL=MOVERS.tsv")
    a = ap.parse_args()
    sweeps, movers = pairs(a.sweeps, "sweep"), pairs(a.movers, "--movers")
    floors = load_floors(a.floors)
    c0 = load_census0(a.tree)
    fails = []
    for cell in CELLS:
        if cell not in sweeps:
            fails.append("FAIL: cell %s: no sweep given (the population is all four cells)" % cell)
            print(fails[-1])
            continue
        recs = [json.loads(ln) for ln in open(sweeps[cell])]
        hit, n, nrec = census(recs, c0)
        fl, pin = floors[cell], pin_floor(a.tree, cell)
        why = verdict(cell, fl, hit, n, nrec, pin)
        out_of = ""
        if cell in movers:
            mset = {f[4] for f in (ln.rstrip("\n").split("\t") for ln in open(movers[cell])) if f[3] == "1"}
            miss = sorted(mset - hit)
            for h in miss[:40]:
                print("MOVER-WITHOUT-RECORD %s %r" % (cell, bytes.fromhex(h).decode("latin-1")))
            if miss:
                why.append("%d of %d movers carry no shipped-art record with an unspelled SET term" % (len(miss), len(mset)))
            out_of = " movers_measured=%d movers_in_census=%d" % (len(mset), len(mset) - len(miss))
        print("D3-FLOOR %s compiles=%d records=%d census=%d floor=%d movers=%d pin=%s%s %s"
              % (cell, n, nrec, len(hit), fl["census_floor"], fl["movers"], pin, out_of,
                 "RED: " + "; ".join(why) if why else "ok"))
        if why:
            fails.append(cell)
        elif not a.no_self_test:
            fails += self_test(floors, a.tree, c0, cell, recs, hit, n, nrec, pin)
    print("D3-FLOOR cells=%d failed=%d" % (len(CELLS), len(fails)))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
