#!/usr/bin/env python3
"""docs/dev/lanes/s3_evidence/census_r2.py -- the MOVER CENSUS of code review r2's PAIR
widening (R2-1) and its one two-stream renderer (R2-6), lane s3pair: which corpus artifacts
move between the C1 tip (BASE, ae83da9d4: abi 84 both, nothing normalized) and this build
(NEW), and does anything move OUTSIDE the declared population?

    python3 -I census_r2.py --base BIN --new BIN --tree DIR --out FILE [--jobs N] [--limit N]

The corpus enumeration and the block options are census.py's (beside this script; one
implementation). THE DECLARED POPULATION is read from the two artifacts' OWN text on each arm,
never from the kit and never from the diff: an artifact is a PAIR artifact iff it renders the
window family's B-pair (`_mfN_ha < `, the two pending hits of E-find's loop) on either side. The
judgment, BOTH WAYS, per arm:
  c-default, c-utf8, c-simd, c-norun   a PAIR artifact on NEW must move (NEW's B-pair is either
                      new, a stop R7w walked, or the shared renderer's text), a PAIR artifact on
                      BASE alone is UNEXPECTED (PAIR only widened), and nothing else may move
  c-vm, ir            nothing may move
  facts               only a pattern whose c-default or c-utf8 artifact is a mover may move
  off, off-simd       nothing may move (both denies on both sides)
Counted per arm: PAIR artifacts, movers, and of the movers those whose BASE walked the stop
(`new`) versus those whose BASE already rendered B-pair (`text`).
Trailer: `== r2 census COMPLETE: patterns=P compiles=C movers=M unexpected=U`; exit 0 iff U == 0.
"""
import argparse
import concurrent.futures
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census  # noqa: E402  (corpus_tasks, run, first_diff: one implementation)

PAIR = re.compile(rb"_mf\d+_ha < ")
OFF = "--memfn=no-wf-find,no-wf-hors"
C = ["-p", "rx", "--features", "all"]
ARMS = [   # (arm, argv both sides, judged by the PAIR text?)
    ("c-default", C + ["-o", "-"], True),
    ("c-utf8", C + ["-e", "utf8", "-o", "-"], True),
    ("c-simd", C + ["-fmemfn-simd", "-o", "-"], True),
    ("c-norun", C + ["-fno-run-prefilter", "-o", "-"], True),
    ("c-vm", C + ["--engine=vm", "-o", "-"], False),
    ("ir", ["--features", "all", "--engine=vm", "--emit-ir"], False),
    ("facts", ["--features", "all", "--emit-facts=byte,utf8"], False),
    ("off", C + [OFF, "-o", "-"], False),
    ("off-simd", C + ["-fmemfn-simd", OFF, "-o", "-"], False),
]


def one(task):
    base, new, pat, opts = task
    opts = list(opts)
    res, cmoved = [], False
    for arm, argv, judged in ARMS:
        rb, ob, eb = census.run([base] + opts + argv + ["--pattern", pat])
        rn, on, en = census.run([new] + opts + argv + ["--pattern", pat])
        what = []
        if rb != rn:
            what.append("rc base=%d new=%d" % (rb, rn))
        if ob != on:
            what.append("bytes " + census.first_diff(ob, on))
        if eb != en:
            what.append("stderr " + census.first_diff(eb, en))
        pn, pb = judged and PAIR.search(on) is not None, judged and PAIR.search(ob) is not None
        if arm in ("c-default", "c-utf8") and what:
            cmoved = True
        if arm == "facts":
            pn = cmoved          # declared: a pattern whose .c moved
        res.append((arm, "; ".join(what), pn, pb))
    return pat, tuple(opts), res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(a.tree, "scripts"))
    import emit_sweep  # noqa: E402
    nrows, tasks, refused = census.corpus_tasks(emit_sweep, a.new, a.tree)
    if a.limit:
        tasks = tasks[:a.limit]
    tally = {arm: {"pair": 0, "moved": 0, "new": 0, "text": 0} for arm, _, _ in ARMS}
    unexpected, rows = [], []
    for f, line in refused:
        unexpected.append(("-", "refused", "%s:%s" % (f, line), "a block option this census does not pass"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for pat, opts, res in ex.map(one, [(a.base, a.new, p, o) for p, o in tasks], chunksize=8):
            ep = emit_sweep.encode_escape(pat) + (" [" + " ".join(opts) + "]" if opts else "")
            for arm, what, pn, pb in res:
                t = tally[arm]
                t["pair"] += pn
                if what:
                    t["moved"] += 1
                    t["new"] += pn and not pb
                    t["text"] += pn and pb
                    rows.append((arm, "PAIR" if pn else "other", ep, what))
                if pb and not pn and arm != "facts":
                    unexpected.append((arm, "PAIR-lost", ep, "B-pair on BASE, not on NEW"))
                elif pn and not what and arm != "facts":
                    unexpected.append((arm, "PAIR", ep, "a B-pair artifact did NOT move"))
                elif what and not pn:
                    unexpected.append((arm, "other", ep, what))
    with open(a.out, "w", encoding="utf-8", errors="backslashreplace") as f:
        f.write("# r2 census: base=%s new=%s patterns=%d\n#arm\tclass\tpattern\tmoved\n"
                % (a.base, a.new, len(tasks)))
        for r in unexpected + rows:
            f.write("\t".join(x.replace("\t", "\\t").replace("\n", "\\n") for x in r) + "\n")
    print("r2 census: corpus rows %d, distinct (pattern, options) tasks %d" % (nrows, len(tasks)))
    for arm, _, judged in ARMS:
        t = tally[arm]
        print("  %-9s pair %5d  movers %5d (walk->pair %5d, pair text %5d)  declared: %s" % (
            arm, t["pair"], t["moved"], t["new"], t["text"],
            "movers == B-pair artifacts" if judged else
            "movers within .c movers" if arm == "facts" else "no mover"))
    for u in unexpected[:20]:
        print("  UNEXPECTED %s %s %s: %s" % u)
    print("== r2 census COMPLETE: patterns=%d compiles=%d movers=%d unexpected=%d"
          % (len(tasks), 2 * len(tasks) * len(ARMS), len(rows), len(unexpected)))
    return 0 if not unexpected else 1


if __name__ == "__main__":
    sys.exit(main())
