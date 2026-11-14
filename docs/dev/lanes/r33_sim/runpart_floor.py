#!/usr/bin/env python3
"""docs/dev/lanes/r33_sim/runpart_floor.py -- R-38 Part D D3's PCREC-ARTIFACT FLOOR (part_d.md §5.1 D3 [r3pd RDY-5],
§9 item 9; request R-43), beside runpart_prod.py (the production path).

    python3 -I runpart_floor.py --tree TREE CELL=SWEEP.jsonl ... [--movers CELL=MOVERS.tsv ...]

CELL is one of emit_sweep's (base, stream) cells for the deny `--memfn=no-run-verify-wide`: byte/c-default,
byte/c-vm, utf8/c-default, utf8/c-vm. SWEEP is collect.py's corpus sweep of that cell (`--sources corpus --flags`:
nothing, `--engine=vm`, `-e utf8`, `-e utf8 --engine=vm`).

THE CENSUS (per cell): the DISTINCT corpus patterns (`pat_hex`; collect.py's corpus is already distinct) that
compiled and carry at least one `run_part_terms` record ON THE SHIPPED (last) art holding an UNSPELLED SET term
(census0.py's own parser and `run_part_unspelled`: members not one byte and not a cube). Every term of the record
is a position of the derived part, so each is inside the extent by construction.
THE CHECK: every one of the four cells is present (the population); census >= CENSUS_FLOOR[cell], the measured
census (R-43, the first green run); CENSUS_FLOOR[cell] >= MOVERS[cell], the deny's DIFFER movers measured by
emit_sweep's arms run on main 370aab9fe; and CENSUS_FLOOR[cell] >= emit_sweep's live DIFFER_PINS floor for the
cell (read from TREE, so a pcrec re-pin above the census reds here and is looked at).
Why census >= movers (INFERRED, the review's): the deny clips every extent to its findable stretch and is the
identity where every position is findable, so a pattern moves only if its part holds an unspelled verified position,
which prints such a record. The census and the movers share no source: the record is the kit's trace, the movers
are pcrec's artifact diff.

--movers CELL=MOVERS.tsv (deny_reach.py's output, the same cell): the per-pattern form of the same claim, every mover
is in the census. A mover outside it is printed (`MOVER-WITHOUT-RECORD`) and reds: the inferred direction is wrong.
Exit 0 green, 1 red.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CELLS = ("byte/c-default", "byte/c-vm", "utf8/c-default", "utf8/c-vm")
DENY = "--memfn=no-run-verify-wide"

# the deny's DIFFER movers per cell, emit_sweep `--arms start` on main 370aab9fe (box batch
# b202611140752593761835, /var/tmp/pcrec-pcrec/scratch/s2arms/arms_370aab9fe.tsv): R-43's FACT
MOVERS = {"byte/c-default": 58, "byte/c-vm": 117, "utf8/c-default": 99, "utf8/c-vm": 181}

# the census, MEASURED at R-43's first green run (lane r43, box job kit-r43-measure, m1 sweeps on 5,489 corpus
# patterns; was 0 on the kit branch, part_d.md §5.1 D3). Every deny mover is in its cell's census.
CENSUS_FLOOR = {"byte/c-default": 58, "byte/c-vm": 143, "utf8/c-default": 99, "utf8/c-vm": 216}


def load_census0(tree):
    sys.path.insert(0, os.path.join(tree, "docs/design/memfn/span_pick"))
    import census0  # noqa: E402
    return census0


def census(lines, c0):
    """the set of pat_hex with a shipped-art record holding an unspelled SET term; and (compiles, records)"""
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


def pairs(xs, what):
    out = {}
    for x in xs:
        cell, _, path = x.partition("=")
        if cell not in CELLS or not path:
            sys.exit("runpart_floor: %s %r is not CELL=PATH with CELL one of %s" % (what, x, ", ".join(CELLS)))
        out[cell] = path
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True)
    ap.add_argument("sweeps", nargs="+", metavar="CELL=SWEEP.jsonl")
    ap.add_argument("--movers", action="append", default=[], metavar="CELL=MOVERS.tsv")
    a = ap.parse_args()
    sweeps, movers = pairs(a.sweeps, "sweep"), pairs(a.movers, "--movers")
    c0 = load_census0(a.tree)
    fails = []
    for cell in CELLS:
        if cell not in sweeps:
            fails.append("FAIL: cell %s: no sweep given (the population is all four cells)" % cell)
            print(fails[-1])
            continue
        hit, n, nrec = census((json.loads(ln) for ln in open(sweeps[cell])), c0)
        floor, mv, pin = CENSUS_FLOOR[cell], MOVERS[cell], pin_floor(a.tree, cell)
        why = []
        if len(hit) < floor:
            why.append("census %d below its floor %d" % (len(hit), floor))
        if floor < mv:
            why.append("the census floor %d is below the deny's movers %d" % (floor, mv))
        if pin is None:
            why.append("emit_sweep DIFFER_PINS has no (%s, %s) cell" % (cell, DENY))
        elif floor < pin:
            why.append("the census floor %d is below emit_sweep's DIFFER floor %d" % (floor, pin))
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
              % (cell, n, nrec, len(hit), floor, mv, pin, out_of, "RED: " + "; ".join(why) if why else "ok"))
        if why:
            fails.append(cell)
    print("D3-FLOOR cells=%d failed=%d" % (len(CELLS), len(fails)))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
