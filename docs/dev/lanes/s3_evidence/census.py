#!/usr/bin/env python3
"""docs/dev/lanes/s3_evidence/census.py -- lane s3's MOVER CENSUS for D172 S3 (abi 83 -> 84,
PROVISIONAL), job 587's stand-in for emit_sweep's five streams (emit_sweep has no abi
normalization; corefix's census.py is the precedent): which corpus artifacts move, and does
anything move OUTSIDE the declared population?

    python3 -I census.py --base BIN --new BIN --tree DIR --out FILE [--jobs N] [--limit N]

BASE is main c3ea619c3's pcrec, NEW the S3 commit's. Over every distinct corpus pattern
(scripts/emit_sweep.py's own enumeration), ten arms are compiled by both: the .c at the default
engine, under -e utf8 and at --engine=vm, the VM listing (--emit-ir), the facts listing, the
OFF ARM (NEW under --memfn=no-wf-find,no-wf-hors against BASE's default .c), and (the S3 review's
item D) the .c at the SIMD layer (-fmemfn-simd) and under norun (-fno-run-prefilter), each with
its own OFF arm (the same flag on both sides, NEW also under both denies). NEW's output has the
abi digits mapped back (84 -> 83) in the places they occur; nothing else is normalized; rc and
stderr are compared too.

THE DECLARED POPULATION is read from NEW's OWN ARTIFACT on that arm, a pcrec-side stamp, never
from the kit and never from the diff: a .c arm's pattern is class COVER iff NEW's artifact on that
arm reads `#define RX_DFA_SCAN "cover"` (D172 S3: the cover LOCATE row routed by default). The
judgment, BOTH WAYS, per arm:
  c-default, c-utf8   a COVER artifact MUST move, and nothing else may (a cover artifact that did
                      not move, or a non-cover mover, is UNEXPECTED)
  c-vm, ir            nothing may move (cover is a DFA-route row)
  facts               only a pattern whose DEFAULT .c is COVER may move, with its rc and stderr
                      unchanged: the listing mirrors the artifact's stamps (its RX_DFA_* rows) and
                      records which facts a pass asked (`used`, facts_listing.md §4.1: passes the
                      composite ran asked them, the cover walk runs none); a cover pattern whose
                      listing did not move is counted, not red
  c-simd, c-norun     as c-default, at the SIMD layer and under -fno-run-prefilter: the cover
                      stamp is read from NEW's artifact on THAT arm
  off, off-simd,      nothing may move (the OFF arm renders the parent's text, at each of the
  off-norun           three flag settings)
D-HORS (Table D's dense-stop resume) appears as a file-scope skip table `_sh[256]`; it may appear
only in a COVER artifact (counted: `hors`), never elsewhere (UNEXPECTED).
Trailer: `== s3 census COMPLETE: patterns=P compiles=C movers=M unexpected=U`; exit 0 iff U == 0.
"""
import argparse
import concurrent.futures
import os
import subprocess
import sys

ABI = [(b"(abi 84)", b"(abi 83)"), (b"(PCREC_RX_ABI_H + 0) != 84", b"(PCREC_RX_ABI_H + 0) != 83"),
       (b"#define PCREC_RX_ABI_H 84", b"#define PCREC_RX_ABI_H 83"), (b"    .abi = 84,", b"    .abi = 83,")]
COVER = b'#define RX_DFA_SCAN "cover"'
HORS = b"_sh[256]"
OFF = "--memfn=no-wf-find,no-wf-hors"

# (arm, base argv, new argv, judged by the artifact's own stamp?)
ARMS = [
    ("c-default", ["-p", "rx", "--features", "all", "-o", "-"], None, True),
    ("c-utf8", ["-p", "rx", "--features", "all", "-e", "utf8", "-o", "-"], None, True),
    ("c-vm", ["-p", "rx", "--features", "all", "--engine=vm", "-o", "-"], None, False),
    ("ir", ["--features", "all", "--engine=vm", "--emit-ir"], None, False),
    ("facts", ["--features", "all", "--emit-facts=byte,utf8"], None, False),
    ("off", ["-p", "rx", "--features", "all", "-o", "-"],
     ["-p", "rx", "--features", "all", OFF, "-o", "-"], False),
    ("c-simd", ["-p", "rx", "--features", "all", "-fmemfn-simd", "-o", "-"], None, True),
    ("c-norun", ["-p", "rx", "--features", "all", "-fno-run-prefilter", "-o", "-"], None, True),
    ("off-simd", ["-p", "rx", "--features", "all", "-fmemfn-simd", "-o", "-"],
     ["-p", "rx", "--features", "all", "-fmemfn-simd", OFF, "-o", "-"], False),
    ("off-norun", ["-p", "rx", "--features", "all", "-fno-run-prefilter", "-o", "-"],
     ["-p", "rx", "--features", "all", "-fno-run-prefilter", OFF, "-o", "-"], False),
]


def norm(out):
    for a, b in ABI:
        out = out.replace(a, b)
    return out


def run(argv, timeout=60):
    try:
        r = subprocess.run(argv, capture_output=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -9, b"", b"TIMEOUT"


def first_diff(a, b):
    la, lb = a.split(b"\n"), b.split(b"\n")
    for i in range(max(len(la), len(lb))):
        x = la[i] if i < len(la) else b"<eof>"
        y = lb[i] if i < len(lb) else b"<eof>"
        if x != y:
            return "line %d: base=%r new=%r" % (i + 1, x[:100], y[:100])
    return ""


def one(task):
    base, new, pat = task
    res = []
    dcover = 0
    for arm, fb, fn, stamped in ARMS:
        rb, ob, eb = run([base] + fb + ["--pattern", pat])
        rn, on, en = run([new] + (fn or fb) + ["--pattern", pat])
        what = []
        if rb != rn:
            what.append("rc base=%d new=%d" % (rb, rn))
        if ob != norm(on):
            what.append("bytes " + first_diff(ob, norm(on)))
        if eb != norm(en):
            what.append("stderr " + first_diff(eb, norm(en)))
        cover = stamped and rn == 0 and COVER in on
        if arm == "c-default":
            dcover = cover
        if arm == "facts":
            # declared: a default-cover pattern's listing, its `used` cells only
            cover = dcover and rb == rn and eb == norm(en)
        res.append((arm, "; ".join(what), cover, HORS in on))
    return pat, res


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
    import emit_sweep  # noqa: E402  (the corpus enumeration, one implementation)
    corpus = emit_sweep.enumerate_corpus(a.new, a.tree, 60)
    pats = sorted(set(p for _, _, p in corpus))
    if a.limit:
        pats = pats[:a.limit]
    tally = {arm: {"cover": 0, "moved": 0, "hors": 0} for arm, _, _, _ in ARMS}
    unexpected, rows = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for pat, res in ex.map(one, [(a.base, a.new, p) for p in pats], chunksize=8):
            ep = emit_sweep.encode_escape(pat)
            for arm, what, cover, hors in res:
                t = tally[arm]
                t["cover"] += cover
                t["hors"] += hors and cover
                if what:
                    t["moved"] += 1
                    rows.append((arm, "COVER" if cover else "other", ep, what))
                if cover and not what and arm != "facts":
                    unexpected.append((arm, "COVER", ep, "a cover artifact did NOT move"))
                elif what and not cover:
                    unexpected.append((arm, "other", ep, what))
                if hors and not cover:
                    unexpected.append((arm, "other", ep, "a D-hors skip table outside a cover artifact"))
    with open(a.out, "w", encoding="utf-8", errors="backslashreplace") as f:
        f.write("# s3 census: base=%s new=%s patterns=%d\n#arm\tclass\tpattern\tmoved\n"
                % (a.base, a.new, len(pats)))
        for r in unexpected + rows:
            f.write("\t".join(x.replace("\t", "\\t").replace("\n", "\\n") for x in r) + "\n")
    print("census: corpus rows %d, distinct patterns %d" % (len(corpus), len(pats)))
    for arm, _, _, stamped in ARMS:
        t = tally[arm]
        print("  %-9s cover %5d (D-hors %4d)  movers %5d  declared: %s" % (
            arm, t["cover"], t["hors"], t["moved"],
            "movers == cover artifacts" if stamped else
            "movers within default-cover patterns" if arm == "facts" else "no mover"))
    for u in unexpected[:20]:
        print("  UNEXPECTED %s %s %s: %s" % u)
    print("== s3 census COMPLETE: patterns=%d compiles=%d movers=%d unexpected=%d"
          % (len(pats), 2 * len(pats) * len(ARMS), len(rows), len(unexpected)))
    return 0 if not unexpected else 1


if __name__ == "__main__":
    sys.exit(main())
