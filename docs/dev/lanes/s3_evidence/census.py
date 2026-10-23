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
                      listing did not move is counted, not red. ALSO (job 600's three rows,
                      `\\p{Zl}` `\\p{Zp}` `\\p{sc=Thaana}`: byte `empty`, utf8 `cover`) a pattern whose
                      -e utf8 .c is COVER may move its `utf8` rows and nothing else
                      (`utf8-cover` in the tally line)
  c-simd, c-norun     as c-default, at the SIMD layer and under -fno-run-prefilter: the cover
                      stamp is read from NEW's artifact on THAT arm
  off, off-simd,      nothing may move (the OFF arm renders the parent's text, at each of the
  off-norun           three flag settings)
D-HORS (Table D's dense-stop resume) appears as a file-scope skip table `_sh[256]`; it may appear
only in a COVER artifact (counted: `hors`), never elsewhere (UNEXPECTED).
THE BLOCK'S OPTIONS (code review r1 C11): a corpus pattern is compiled under its own block's
options, read from `pcrec --list-source` (the .rxt as written): `flags` i -> `-i`, u -> `--ucp`,
`encoding` -> `-e ENC` (rxt_format.md §1.5¶4; the corpus states no per-block raw `pcrec` flags
and no `with`/`from` cascade on a pattern row, and a row stating one is counted and REFUSED, not
compiled without it). A pattern is one task per distinct (pattern, options); the options come
first on every arm's command line, so an arm's own `-e` overrides a block's. The tally line
`options:` counts the option-driven tasks and the cover artifacts among them.
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


def utf8_rows_only(a, b):
    la, lb = a.split(b"\n"), b.split(b"\n")
    return len(la) == len(lb) and all(x == y or (x.startswith(b"utf8\t") and y.startswith(b"utf8\t"))
                                      for x, y in zip(la, lb))


FLAG_ARGV = {"i": "-i", "u": "--ucp"}


def block_options(row):
    """The pcrec options of one `--list-source` pattern row (its columns as written), or
    None where it states something this census does not pass (a raw `pcrec` flag, a
    `with`/`from` cascade, an unknown flag letter)."""
    flags, enc, cascade_with, cascade_from, raw = row[5], row[8], row[12], row[13], row[14]
    if raw or cascade_with or cascade_from or any(c not in FLAG_ARGV for c in flags):
        return None
    opts = [FLAG_ARGV[c] for c in flags]
    if enc:
        opts += ["-e", enc]
    return tuple(opts)


def corpus_tasks(es, pcrec_bin, tree):
    """(rows, tasks, refused): every corpus pattern row with its block's options; the
    distinct (pattern, options) tasks; the rows whose options this census cannot pass."""
    rows, refused = 0, []
    tasks = set()
    for f in es.find_files(tree, (".rxt",)):
        rc, out, _ = run([pcrec_bin, "--list-source", f], 60)
        if rc:
            continue
        for ln in out.decode("utf-8", errors="surrogateescape").splitlines():
            c = ln.split("\t")
            if ln.startswith("#") or len(c) < 15 or c[0] not in ("pattern", "pattern-esc"):
                continue
            rows += 1
            opts = block_options(c)
            if opts is None:
                refused.append((os.path.relpath(f, tree), c[1]))
                continue
            tasks.add((es.decode_escape(c[4]), opts))
    return rows, sorted(tasks), refused


def one(task):
    base, new, pat, opts = task
    opts = list(opts)
    res = []
    dcover = ucover = 0
    for arm, fb, fn, stamped in ARMS:
        rb, ob, eb = run([base] + opts + fb + ["--pattern", pat])
        rn, on, en = run([new] + opts + (fn or fb) + ["--pattern", pat])
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
        if arm == "c-utf8":
            ucover = cover
        if arm == "facts":
            # declared: a default-cover pattern's listing, its `used` cells only; or a
            # utf8-only-cover pattern's listing, its `utf8` rows only
            cover = (dcover or (ucover and utf8_rows_only(ob, norm(on)))) and rb == rn and eb == norm(en)
            ucover = cover and not dcover
        res.append((arm, "; ".join(what), cover, HORS in on, arm == "facts" and ucover))
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
    import emit_sweep  # noqa: E402  (the corpus enumeration, one implementation)
    nrows, tasks, refused = corpus_tasks(emit_sweep, a.new, a.tree)
    if a.limit:
        tasks = tasks[:a.limit]
    pats = tasks
    tally = {arm: {"cover": 0, "moved": 0, "hors": 0, "u8": 0} for arm, _, _, _ in ARMS}
    optn = {"tasks": 0, "cover": 0}
    unexpected, rows = [], []
    for f, line in refused:
        unexpected.append(("-", "refused", "%s:%s" % (f, line),
                           "a block option this census does not pass (raw pcrec flags, a cascade)"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for pat, opts, res in ex.map(one, [(a.base, a.new, p, o) for p, o in tasks], chunksize=8):
            ep = emit_sweep.encode_escape(pat) + (" [" + " ".join(opts) + "]" if opts else "")
            if opts:
                optn["tasks"] += 1
                optn["cover"] += any(arm == "c-default" and cover for arm, _, cover, _, _ in res)
            for arm, what, cover, hors, u8 in res:
                t = tally[arm]
                t["cover"] += cover
                t["u8"] += u8
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
    print("census: corpus rows %d, distinct (pattern, options) tasks %d" % (nrows, len(pats)))
    print("  options: %d tasks under their block's options (flags i/u, encoding), %d of them "
          "cover at c-default; %d rows refused" % (optn["tasks"], optn["cover"], len(refused)))
    for arm, _, _, stamped in ARMS:
        t = tally[arm]
        print("  %-9s cover %5d (D-hors %4d)  movers %5d  declared: %s" % (
            arm, t["cover"], t["hors"], t["moved"],
            "movers == cover artifacts" if stamped else
            "movers within default-cover patterns, utf8-cover %d" % t["u8"] if arm == "facts"
            else "no mover"))
    for u in unexpected[:20]:
        print("  UNEXPECTED %s %s %s: %s" % u)
    print("== s3 census COMPLETE: patterns=%d compiles=%d movers=%d unexpected=%d"
          % (len(pats), 2 * len(pats) * len(ARMS), len(rows), len(unexpected)))
    return 0 if not unexpected else 1


if __name__ == "__main__":
    sys.exit(main())
