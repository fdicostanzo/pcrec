#!/usr/bin/env python3
"""docs/dev/lanes/r33_sim/runpart_prod.py -- R-38 Part D D3's PRODUCTION-PATH check (part_d.md §5.1 D3 [r3pd RDY-1]).

    python3 -I runpart_prod.py SWEEP.jsonl [--floor N]
    python3 -I runpart_prod.py --self-test FIXTURE.jsonl

Over a collect.py sweep: every compile whose ARTIFACT stamps an emitted run (pcrec's own `<PREFIX>_REQ_RUN` other
than `none` with `<PREFIX>_REQ_WHY` "emitted", read off the emitted text by collect.py's req_stamps) carries
EXACTLY ONE derived run part record (`MFTRACE run_part_terms`, kept raw by collect.py's summarize in each site's
`trace.parts`) ON THE ART THAT SHIPPED. The stamps are pcrec's text and the records the kit's trace: the two share
no source. The shipped art is the compile's LAST art (collect.py's `arts`): a compound walk's trial parts and a
failed attempt begin their own arts first, and their defines print their own records (lane partdfix: corpus
c01877, `tests/compound/split.rxt`, defines its run on a declined split part's art 1 and on the shipped art 3).
Those records are counted and reported, never joined. A compile whose stamp says "emitted" with 0 records on the
shipped art (collect.py dropping the record: plant p14) or 2 (a doubled print) is a FAIL; so is an emitted stamp
on an artifact with more than one REQ_RUN stamp (a compound shell ships several arts: the join names none), a
total of emitted stamps below the floor (the population's own floor, K35), or no `req`/`arts` field (a sweep
collected before D3, or before partdfix). Records on the shipped art of a compile that stamps no emitted run are
counted and reported, not failed.

--self-test FIXTURE: FIXTURE is one REAL collect.py line holding records on an unshipped art and one on the
shipped art (c01877's, committed beside this file); the check must be GREEN on it and RED on each of its
mutations: the shipped art's record doubled, the shipped art's record moved to art 1, and the art count dropped.
Exit 0 green, 1 red.
"""
import argparse
import copy
import json
import sys


def check(lines, floor, out=print):
    n = emitted = ok = stray = unshipped = noreq = 0
    fails = []
    for rec in lines:
        if rec.get("rc") != 0:
            continue
        n += 1
        req = rec.get("req")
        if req is None or "arts" not in rec:
            noreq += 1
            continue
        last = rec["arts"]
        recs = unrecs = 0
        for s in rec.get("sites", []):
            k = len(s.get("trace", {}).get("parts", []))
            if s.get("art") == last:
                recs += k
            else:
                unrecs += k
        unshipped += unrecs
        em = any(r != "none" for r in req["run"]) and "emitted" in req["why"]
        if em and len(req["run"]) != 1:
            fails.append("FAIL: %s %s: an emitted run on an artifact with %d REQ_RUN stamps (a compound shell "
                         "ships several arts; the join names no single one)" % (rec["src"], rec["id"], len(req["run"])))
        elif em:
            emitted += 1
            if recs == 1:
                ok += 1
            else:
                fails.append("FAIL: %s %s: the artifact stamps an emitted run (REQ_RUN %s) and its shipped art %d "
                             "carries %d run_part_terms records, not 1 (%d more on earlier arts)"
                             % (rec["src"], rec["id"], ",".join(req["run"]), last, recs, unrecs))
        elif recs:
            stray += 1
    for f in fails[:40]:
        out(f)
    if noreq:
        fails.append("FAIL: %d compiles carry no `req` stamps or `arts` count (a sweep collected before D3's or "
                     "partdfix's collect.py)" % noreq)
        out(fails[-1])
    if emitted < floor:
        fails.append("FAIL: %d compiles stamp an emitted run, below the floor %d" % (emitted, floor))
        out(fails[-1])
    out("RUNPART-PROD compiles=%d emitted=%d one_record=%d records_without_emitted=%d records_on_unshipped_arts=%d "
        "failed=%d" % (n, emitted, ok, stray, unshipped, len(fails)))
    return not fails


def self_test(path):
    base = [json.loads(ln) for ln in open(path)]
    assert len(base) == 1, "the fixture is one compile"
    rec = base[0]
    shipped = [s for s in rec["sites"] if s["art"] == rec["arts"] and s["trace"]["parts"]]
    early = [s for s in rec["sites"] if s["art"] != rec["arts"] and s["trace"]["parts"]]
    bad = 0
    # the fixture must still hold the shape it witnesses: a record on each side of the join
    if len(shipped) != 1 or not early:
        print("SELFTEST FAIL: the fixture holds %d shipped-art and %d earlier-art record sites, not 1 and >=1"
              % (len(shipped), len(early)))
        return False

    def mut(f):
        r = copy.deepcopy(rec)
        f(r)
        return [r]

    def doubled(r):
        s = next(s for s in r["sites"] if s["art"] == r["arts"] and s["trace"]["parts"])
        s["trace"]["parts"] = s["trace"]["parts"] * 2

    def moved(r):
        s = next(s for s in r["sites"] if s["art"] == r["arts"] and s["trace"]["parts"])
        s["art"] = 1

    def no_arts(r):
        del r["arts"]

    cases = [("fixture", base, True), ("doubled", mut(doubled), False), ("moved", mut(moved), False),
             ("no-arts", mut(no_arts), False)]
    for name, lines, want in cases:
        got = check(lines, 1, out=lambda s: None)
        print("SELFTEST %s %s (want %s)" % (name, "GREEN" if got else "RED", "GREEN" if want else "RED"))
        bad += got != want
    print("SELFTEST cases=%d wrong=%d" % (len(cases), bad))
    return bad == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sweep", nargs="?")
    ap.add_argument("--floor", type=int, default=1)
    ap.add_argument("--self-test", metavar="FIXTURE")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(0 if self_test(a.self_test) else 1)
    if not a.sweep:
        ap.error("SWEEP.jsonl or --self-test FIXTURE")
    sys.exit(0 if check((json.loads(ln) for ln in open(a.sweep)), a.floor) else 1)


if __name__ == "__main__":
    main()
