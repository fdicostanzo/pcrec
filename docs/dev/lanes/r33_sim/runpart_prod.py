#!/usr/bin/env python3
"""docs/dev/lanes/r33_sim/runpart_prod.py -- R-38 Part D D3's PRODUCTION-PATH check (part_d.md §5.1 D3 [r3pd RDY-1]).

    python3 -I runpart_prod.py SWEEP.jsonl [--floor N]

Over a collect.py sweep: every compile whose ARTIFACT stamps an emitted run (pcrec's own `<PREFIX>_REQ_RUN` other
than `none` with `<PREFIX>_REQ_WHY` "emitted", read off the emitted text by collect.py's req_stamps) carries
EXACTLY ONE derived run part record (`MFTRACE run_part_terms`, kept raw by collect.py's summarize in each site's
`trace.parts`). The stamps are pcrec's text and the records the kit's trace: the two share no source. A compile
whose stamp says "emitted" with 0 records (collect.py dropping the record: plant p14) or 2 (a doubled print) is a
FAIL; so is a total of emitted stamps below the floor (the population's own floor, K35), or no `req` field at
all (a sweep collected before D3). Records on a compile that stamps no emitted run are counted and reported, not
failed (the stamp is per artifact; a define the artifact later discards is not this check's).
Exit 0 green, 1 red.
"""
import argparse
import json
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sweep")
    ap.add_argument("--floor", type=int, default=1)
    a = ap.parse_args()
    n = emitted = ok = stray = noreq = 0
    fails = []
    for line in open(a.sweep):
        rec = json.loads(line)
        if rec.get("rc") != 0:
            continue
        n += 1
        req = rec.get("req")
        if req is None:
            noreq += 1
            continue
        recs = sum(len(s.get("trace", {}).get("parts", [])) for s in rec.get("sites", []))
        em = any(r != "none" for r in req["run"]) and "emitted" in req["why"]
        if em:
            emitted += 1
            if recs == 1:
                ok += 1
            else:
                fails.append("FAIL: %s %s: the artifact stamps an emitted run (REQ_RUN %s) and the trace carries %d "
                             "run_part_terms records, not 1" % (rec["src"], rec["id"], ",".join(req["run"]), recs))
        elif recs:
            stray += 1
    for f in fails[:40]:
        print(f)
    if noreq:
        fails.append("FAIL: %d compiles carry no `req` stamps (a sweep collected before D3's collect.py)" % noreq)
        print(fails[-1])
    if emitted < a.floor:
        fails.append("FAIL: %d compiles stamp an emitted run, below the floor %d" % (emitted, a.floor))
        print(fails[-1])
    print("RUNPART-PROD compiles=%d emitted=%d one_record=%d records_without_emitted=%d failed=%d"
          % (n, emitted, ok, stray, len(fails)))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
