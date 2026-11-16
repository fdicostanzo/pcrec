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
THE CHECK, per cell: the sweep is a POPULATION that is counted and printed, each count pinned to its MEASURED value with a
small band above (below = a loss, above = a gain nobody re-pinned; both red, learnings §3 and review r10 D3W-1/2/5):
compiles, failed compiles (exact), run_part_terms records, and the census (>= census_floor, <= census_floor +
census_band: "census rose: re-pin tests/memfn/d3_floor.tsv"); the census is ALSO pinned as a SET (d3_census.tsv, D3F-2; --repin rewrites it and prints the diff); census_floor >= emit_sweep's live DIFFER_PINS floor for the
cell (read from TREE: ONE source for the movers number, no copy here). `--movers CELL=MOVERS.tsv` (deny_reach.py's
output): every mover is in the census, else `MOVER-WITHOUT-RECORD` and red. Not part of the gate (a second sweep per cell;
the set relation movers <= census is checked on demand, the gate pins the counts EXACTLY; a swap that keeps the counts is D3F-2's set pin).
SELF-TEST (default on; every plant is derived from the MEASURED sweep, not from the floor): S3228 loses one census
pattern's records (below the floor), and a floor left behind a census that rose (above the band); S3229 an empty and a
truncated sweep; S3230 a floor below emit_sweep's DIFFER floor; S3231 a lost corpus pattern and a crash wave of failed
compiles (neither touches the census). PLANTS per cell, all must go red as named, the control green.
Exit 0 green, 1 red (a cell, or a plant that did NOT go red).
"""
import argparse
import json
import os
import sys

CELLS = ("byte/c-default", "byte/c-vm", "utf8/c-default", "utf8/c-vm")
DENY = "--memfn=no-run-verify-wide"
INTCOLS = ("census_floor", "census_band", "compiles", "failed", "pop_band", "records", "records_band")
PLANTS = 10  # per cell; run_d3floor.sh reads this line and counts PLANTS x 4 "D3-FLOOR-PLANT ... ok" lines
REPIN = "census changed: re-pin tests/memfn/d3_floor.tsv"
HERE = os.path.dirname(os.path.abspath(__file__))
CENSUS_FILE = os.path.join(HERE, "d3_census.tsv")
CENSUS_HEAD = """# tests/memfn/d3_census.tsv -- the D3 floor's CENSUS AS A SET (review r11 D3F-2): per cell, every corpus pattern (pat_hex,
# sorted) whose SHIPPED art carries a run_part_terms record with an unspelled SET term, as measured by `make
# test-memfn-d3floor`. d3_floor.py holds the measured census EQUAL to this set: a lost member is red and named, a gained one
# is red and named (a re-pin must show what it absorbs). Re-pin: `D3FLOOR_REPIN=1 bash tests/memfn/run_d3floor.sh` rewrites
# this file and prints the member diff plus the d3_floor.tsv numbers; review the diff, then commit both. d3_floor.tsv's
# census_floor column must equal the row count here (checked).
# Provenance of this pin: %s
# columns (tab-separated): cell, pat_hex
"""


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
        for k in INTCOLS:
            r[k] = int(r[k])
        rows[r["cell"]] = r
    for c in CELLS:
        if c not in rows:
            sys.exit("d3_floor: %s has no row for cell %s" % (path, c))
    return rows


def load_census_set(path):
    out = {c: set() for c in CELLS}
    for ln in open(path):
        ln = ln.rstrip("\n")
        if not ln or ln.startswith("#"):
            continue
        cell, _, h = ln.partition("\t")
        if cell not in out or not h:
            sys.exit("d3_floor: %s: bad row %r" % (path, ln))
        out[cell].add(h)
    return out


def pat_text(h):
    return bytes.fromhex(h).decode("latin-1")


def set_why(fl, pinned, hit):
    """the census as a SET (D3F-2): every pinned member still hits (lost = red, named), nothing unpinned hits (gained =
    red, named), and the tsv's census_floor equals the pinned set's size. Empty list = green."""
    why = []
    lost, gained = sorted(pinned - hit), sorted(hit - pinned)
    if lost:
        why.append("census members LOST (%d): %s" % (len(lost), ", ".join(repr(pat_text(h)) for h in lost[:8])))
    if gained:
        why.append("census members GAINED (%d): %s" % (len(gained), ", ".join(repr(pat_text(h)) for h in gained[:8])))
    if len(pinned) != fl["census_floor"]:
        why.append("d3_census.tsv has %d members for the cell, d3_floor.tsv census_floor is %d" % (len(pinned), fl["census_floor"]))
    if why:
        why.append(REPIN)
    return why


def repin(path, sets, old, a_note):
    """--repin: rewrite d3_census.tsv from the measured sets; print the member diff and the d3_floor.tsv numbers"""
    with open(path, "w") as f:
        f.write(CENSUS_HEAD % a_note)
        for c in CELLS:
            for h in sorted(sets[c]["hit"]):
                f.write("%s\t%s\n" % (c, h))
    for c in CELLS:
        for h in sorted(old[c] - sets[c]["hit"]):
            print("D3-REPIN %s - %r" % (c, pat_text(h)))
        for h in sorted(sets[c]["hit"] - old[c]):
            print("D3-REPIN %s + %r" % (c, pat_text(h)))
        x = sets[c]
        print("D3-REPIN-ROW %s census_floor=%d compiles=%d failed=%d records=%d (d3_floor.tsv: set these, bands 0)"
              % (c, len(x["hit"]), x["n"], x["nfail"], x["nrec"]))


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


def failed_count(lines):
    """compiles that did not succeed (rc != 0, or 'timeout'): census() skips them silently, so they are counted here"""
    return sum(1 for rec in lines if rec.get("rc") != 0)


def pin_floor(tree, cell):
    sys.path.insert(0, os.path.join(tree, "scripts"))
    import emit_sweep  # noqa: E402
    base, stream = cell.split("/")
    v = emit_sweep.DIFFER_PINS.get((base, DENY, stream))
    return None if v is None else v[0]


def verdict(cell, fl, hit, n, nrec, nfail, pin):
    """the reasons a cell is red (empty list = green). Every pinned number is a MEASURED value with a band above it:
    below = a loss (the thing the gate guards), above the band = a gain nobody re-pinned (the floor would go loose)."""
    why = []
    if n < fl["compiles"]:
        why.append("population: %d compiles counted, below the %d measured" % (n, fl["compiles"]))
    elif n > fl["compiles"] + fl["pop_band"]:
        why.append("population: %d compiles counted, above %d+%d: corpus grew, re-pin tests/memfn/d3_floor.tsv"
                   % (n, fl["compiles"], fl["pop_band"]))
    if nfail != fl["failed"]:
        why.append("population: %d failed compiles counted, the pinned count is %d (a crash wave or a lost/new reject: "
                   "look, then re-pin tests/memfn/d3_floor.tsv)" % (nfail, fl["failed"]))
    if nrec < fl["records"]:
        why.append("population: %d run_part_terms records counted, below the %d measured" % (nrec, fl["records"]))
    elif nrec > fl["records"] + fl["records_band"]:
        why.append("population: %d records counted, above %d+%d: re-pin tests/memfn/d3_floor.tsv"
                   % (nrec, fl["records"], fl["records_band"]))
    if len(hit) < fl["census_floor"]:
        why.append("census %d below its floor %d" % (len(hit), fl["census_floor"]))
    elif len(hit) > fl["census_floor"] + fl["census_band"]:
        why.append("census rose: %d above %d+%d, re-pin tests/memfn/d3_floor.tsv" % (len(hit), fl["census_floor"],
                                                                                   fl["census_band"]))
    if why:
        why.append(REPIN)  # any census or population change names its remedy itself (never via a plant going WRONG)
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


def with_rc(recs, pats, rc):
    return [dict(r, rc=rc) if r.get("pat_hex") in pats else r for r in recs]


def self_test(floors, tree, c0, cell, recs, hit, pin, pinned):
    """every plant must go RED and its control GREEN; returns the failure texts. Every plant is derived from the
    MEASURED sweep (the census, the counts), never from the floor under test (learnings 3, D3W-2)."""
    bad = []
    fl = floors[cell]

    def run(tag, fl_, recs_, want_red, needle=""):
        h, n_, r_ = census(recs_, c0)
        why = verdict(cell, fl_, h, n_, r_, failed_count(recs_), pin)
        got = "; ".join(why)
        ok = (bool(why) == want_red) and (not want_red or needle in got)
        print("D3-FLOOR-PLANT %s %s compiles=%d records=%d census=%d floor=%d -> %s %s"
              % (tag, cell, n_, r_, len(h), fl_["census_floor"], "RED" if why else "green", "ok" if ok else "WRONG"))
        if not ok:
            bad.append("%s %s: wanted %s%s, got %r" % (tag, cell, "red" if want_red else "green",
                                                      " (%s)" % needle if needle else "", got))

    ok_pats = sorted({r["pat_hex"] for r in recs if r.get("rc") == 0} - hit)  # compiled, no unspelled record
    run("control", fl, recs, False)
    # S3228: the real census loses one pattern's records (the witness-deletion shape): below the measured floor
    run("S3228-lose-one", fl, drop_records(recs, {sorted(hit)[0]}), True, "below its floor")
    # S3228b: the census gains past the band against a floor that was not re-pinned
    run("S3228-rose", dict(fl, census_floor=len(hit) - fl["census_band"] - 1), recs, True, "census rose")
    run("S3229-empty", fl, [], True, "population")
    run("S3229-truncated", fl, recs[:100], True, "population")
    run("S3230-floor-below-pin", dict(fl, census_floor=pin - 1), recs, True, "below emit_sweep's DIFFER floor")
    # S3231: a lost corpus pattern / a crash wave, neither touching the census
    run("S3231-lost-pattern", fl, [r for r in recs if r.get("pat_hex") != ok_pats[0]], True, "compiles counted, below")
    run("S3231-fail-wave", fl, with_rc(recs, set(ok_pats[:5]), "timeout"), True, "failed compiles")
    # S3232: an in-place swap (one witness lost, another gained, every count unchanged) is red and names both; the
    # control (the measured set against itself) is green
    def run_set(tag, hit_, want):
        why = set_why(fl, pinned, hit_)
        got = "; ".join(why)
        ok = (bool(why) == bool(want)) and all(w in got for w in want)
        print("D3-FLOOR-PLANT %s %s members=%d pinned=%d -> %s %s" % (tag, cell, len(hit_), len(pinned),
                                                                      "RED" if why else "green", "ok" if ok else "WRONG"))
        if not ok:
            bad.append("%s %s: wanted %s, got %r" % (tag, cell, "red " + str(want) if want else "green", got))

    victim = sorted(hit)[0]
    run_set("S3232-swap", (hit - {victim}) | {"ab" * 5}, ["LOST", "GAINED", pat_text(victim)])
    # S3233: a pure loss names the lost pattern; a pure gain names the gained one
    run_set("S3233-lost-named", hit - {victim}, ["LOST", pat_text(victim)])
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True)
    ap.add_argument("--floors", default=os.path.join(HERE, "d3_floor.tsv"))
    ap.add_argument("--no-self-test", action="store_true")
    ap.add_argument("--repin", action="store_true", help="rewrite d3_census.tsv from the sweeps and print the diff")
    ap.add_argument("--census", default=CENSUS_FILE, help="the pinned census set (default tests/memfn/d3_census.tsv)")
    ap.add_argument("--note", default="", help="--repin: the provenance text for the file header")
    ap.add_argument("sweeps", nargs="+", metavar="CELL=SWEEP.jsonl")
    ap.add_argument("--movers", action="append", default=[], metavar="CELL=MOVERS.tsv")
    a = ap.parse_args()
    sweeps, movers = pairs(a.sweeps, "sweep"), pairs(a.movers, "--movers")
    floors = load_floors(a.floors)
    c0 = load_census0(a.tree)
    if a.repin:
        old = load_census_set(a.census) if os.path.exists(a.census) else {c: set() for c in CELLS}
        sets = {}
        for cell in CELLS:
            recs = [json.loads(ln) for ln in open(sweeps[cell])]
            hit, n, nrec = census(recs, c0)
            sets[cell] = {"hit": hit, "n": n, "nrec": nrec, "nfail": failed_count(recs)}
        repin(a.census, sets, old, a.note or "unspecified")
        sys.exit(0)
    pinned_sets = load_census_set(a.census)
    fails, nplant_bad = [], 0
    for cell in CELLS:
        if cell not in sweeps:
            fails.append("FAIL: cell %s: no sweep given (the population is all four cells)" % cell)
            print(fails[-1])
            continue
        recs = [json.loads(ln) for ln in open(sweeps[cell])]
        hit, n, nrec = census(recs, c0)
        nfail = failed_count(recs)
        fl, pin = floors[cell], pin_floor(a.tree, cell)
        why = verdict(cell, fl, hit, n, nrec, nfail, pin)
        why += [w for w in set_why(fl, pinned_sets[cell], hit) if w not in why]
        out_of = ""
        if cell in movers:
            mset = {f[4] for f in (ln.rstrip("\n").split("\t") for ln in open(movers[cell])) if f[3] == "1"}
            miss = sorted(mset - hit)
            for h in miss[:40]:
                print("MOVER-WITHOUT-RECORD %s %r" % (cell, bytes.fromhex(h).decode("latin-1")))
            if miss:
                why.append("%d of %d movers carry no shipped-art record with an unspelled SET term" % (len(miss), len(mset)))
            out_of = " movers_measured=%d movers_in_census=%d" % (len(mset), len(mset) - len(miss))
        print("D3-FLOOR %s compiles=%d failed=%d records=%d census=%d floor=%d band=%d pin=%s%s %s"
              % (cell, n, nfail, nrec, len(hit), fl["census_floor"], fl["census_band"], pin, out_of,
                 "RED: " + "; ".join(why) if why else "ok"))
        if why:
            fails.append(cell)
            if not a.no_self_test:
                print("D3-FLOOR-PLANTS-SKIPPED %s (the cell is red; the plants run on a green cell only)" % cell)
        elif not a.no_self_test:
            bad = self_test(floors, a.tree, c0, cell, recs, hit, pin, pinned_sets[cell])
            for b in bad:
                print("D3-FLOOR-PLANT-WRONG " + b)
            fails += bad
            nplant_bad += len(bad)
    print("D3-FLOOR cells=%d failed_cells=%d failed_plants=%d" % (len(CELLS), len(fails) - nplant_bad, nplant_bad))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
