#!/usr/bin/env python3
"""docs/dev/lanes/r33_sim/runpart_prod.py -- R-38 Part D D3's PRODUCTION-PATH check (part_d.md §5.1 D3 [r3pd RDY-1]).

    python3 -I runpart_prod.py SWEEP.jsonl [--floor N]
    python3 -I runpart_prod.py --self-test FIXTURE.jsonl

Over a collect.py sweep: every compile whose ARTIFACT stamps an emitted run (pcrec's own `<PREFIX>_REQ_RUN` other
than `none` with `<PREFIX>_REQ_WHY` "emitted", read off the emitted text by collect.py's req_stamps) is joined to the
derived run part records (`MFTRACE run_part_terms`, kept raw by collect.py's summarize in each site's `trace.parts`)
ON THE ART THAT SHIPPED. The stamps are pcrec's text and the records the kit's trace: the two share no source. The
shipped art is the compile's LAST art (collect.py's `arts`, the probe's count of art begins): a compound walk's trial
parts and a failed attempt begin their own arts first, and their defines print their own records (lane partdfix:
corpus c01877, `tests/compound/split.rxt`, defines its run on a declined split part's art 1 and on the shipped art
3). Those records are counted and reported, never joined. A record's art is the `art=` it prints (the kit's own
trace number, counting the same art begins), not the site line's: the probe resolved a site's art by its pointer,
and an art the allocator reuses resolved to an earlier art (lane r43: corpus c04459, `tests/size/size_term.rxt`
under `--engine=vm`, record `art=7`, site line art 3).

"emitted" is not "the run is tested": the stamp also holds where the kit DECLINES the run (finder.c's PRES row PD, a
run with no findable position on an OPTIONAL route) and a necessary-set member leads the pre-check instead
(match_api.md §6.3.7¶8, tuning.md §2.40); no derived part is laid out there, so no record prints (lane r43: corpus
c00049 `aaa|aab|aba|bba`, c01954, c02026, c01886). So the join is three-way, each way a FAIL when broken:
  scan    the run stamp carries `@idx` (§6.3.7¶7 row 1: the pre-check renders its run part and that part has a
          scan position): exactly one record, its `hint` a term index;
  every   no `@`, the shipped art's define did not decline the run (§6.3.7¶7 row 3's REQUIRED run verified at
          every candidate with no scan position, finder.c's P0): exactly one record, `hint=-`;
  decline no `@`, the shipped art's define chose PD (`ends` holds `fd PD`): no record.
An `@` on a declined run is a FAIL. So is an emitted stamp on an artifact with more than one REQ_RUN stamp (a
compound shell ships several arts: the join names none), a total of emitted stamps below the floor (the
population's own floor, K35; each class is counted), or no `req`/`arts` field (a sweep collected before D3, or
before partdfix). Records on the shipped art of a compile that stamps no emitted run are counted and reported, not
failed.

--self-test FIXTURE: FIXTURE is one REAL collect.py line holding records on an unshipped art and one on the
shipped art (c01877's, committed beside this file); the check must be GREEN on it and RED on each of its
mutations: the shipped art's record doubled, the shipped art's record moved to art 1, the art count dropped,
every record dropped (plant p14's shape), and the run declined (`fd PD` on the shipped art).
Exit 0 green, 1 red.
"""
import argparse
import copy
import json
import re
import sys

REC = re.compile(r" art=(\d+) .* hint=(\S+) ")


def check(lines, floor, out=print):
    n = emitted = ok = stray = unshipped = noreq = 0
    cls = {"scan": 0, "every": 0, "decline": 0}
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
        hints, unrecs, declined = [], 0, False
        for s in rec.get("sites", []):
            for p in s.get("trace", {}).get("parts", []):
                m = REC.search(p)
                if m and int(m.group(1)) == last:
                    hints.append(m.group(2))
                else:
                    unrecs += 1
            if s.get("art") == last and ["fd", "PD"] in s.get("trace", {}).get("ends", []):
                declined = True
        unshipped += unrecs
        em = any(r != "none" for r in req["run"]) and "emitted" in req["why"]
        if em and len(req["run"]) != 1:
            fails.append("FAIL: %s %s: an emitted run on an artifact with %d REQ_RUN stamps (a compound shell "
                         "ships several arts; the join names no single one)" % (rec["src"], rec["id"], len(req["run"])))
        elif em:
            emitted += 1
            at = "@" in req["run"][0]
            if at and declined:
                c, want, good = "scan", "no PD", False
            elif at:
                c, want = "scan", "1 record with a term-index hint"
                good = len(hints) == 1 and hints[0].isdigit()
            elif declined:
                c, want, good = "decline", "0 records", not hints
            else:
                c, want = "every", "1 record with hint=-"
                good = hints == ["-"]
            if good:
                ok += 1
                cls[c] += 1
            else:
                fails.append("FAIL: %s %s: the artifact stamps an emitted run (REQ_RUN %s)%s; its shipped art %d "
                             "carries %d run_part_terms records (hints %s), not %s (%d more on earlier arts)"
                             % (rec["src"], rec["id"], ",".join(req["run"]),
                                " and its define declines it (fd PD)" if declined else "", last, len(hints),
                                ",".join(hints) or "-", want, unrecs))
        elif hints:
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
    out("RUNPART-PROD compiles=%d emitted=%d joined=%d scan=%d every_pos=%d declined=%d records_without_emitted=%d "
        "records_on_unshipped_arts=%d failed=%d" % (n, emitted, ok, cls["scan"], cls["every"], cls["decline"], stray,
                                                    unshipped, len(fails)))
    return not fails


def self_test(path):
    base = [json.loads(ln) for ln in open(path)]
    assert len(base) == 1, "the fixture is one compile"
    rec = base[0]

    def rec_art(p):
        return int(REC.search(p).group(1))

    shipped = [s for s in rec["sites"] if any(rec_art(p) == rec["arts"] for p in s["trace"]["parts"])]
    early = [s for s in rec["sites"] if any(rec_art(p) != rec["arts"] for p in s["trace"]["parts"])]
    bad = 0
    # the fixture must still hold the shape it witnesses: a record on each side of the join, an `@` run
    if len(shipped) != 1 or not early or "@" not in rec["req"]["run"][0]:
        print("SELFTEST FAIL: the fixture holds %d shipped-art and %d earlier-art record sites (not 1 and >=1), "
              "or its run carries no @" % (len(shipped), len(early)))
        return False

    def mut(f):
        r = copy.deepcopy(rec)
        f(r)
        return [r]

    def ship(r):
        return next(s for s in r["sites"] if any(rec_art(p) == r["arts"] for p in s["trace"]["parts"]))

    def doubled(r):
        s = ship(r)
        s["trace"]["parts"] = s["trace"]["parts"] * 2

    def moved(r):
        s = ship(r)
        s["trace"]["parts"] = [re.sub(r" art=\d+ ", " art=1 ", p) for p in s["trace"]["parts"]]

    def no_arts(r):
        del r["arts"]

    def p14(r):
        for s in r["sites"]:
            s["trace"]["parts"] = []

    def declined(r):
        s = ship(r)
        s["art"] = r["arts"]
        s["trace"]["ends"] = s["trace"]["ends"] + [["fd", "PD"]]

    cases = [("fixture", base, True), ("doubled", mut(doubled), False), ("moved", mut(moved), False),
             ("no-arts", mut(no_arts), False), ("p14-dropped", mut(p14), False), ("declined", mut(declined), False)]
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
