#!/usr/bin/env python3
# SPDX-License-Identifier: 0BSD
# Provenance: original pcrec-memory-functions text (D172 S2 commit 3, lane
#   wsc2).
"""memfn/tests/wshadow.py -- D172 S2 COMMIT 3's TRACE SHADOW, the LOCALIZER
(docs/design/memfn/window_site.md rev 3.2 §5.1 commit 3).

WHAT IT DOES. Builds a pcrec whose kit is compiled -DMF_TRACE (the
tests/memfn/mk_mftrace_lib.sh swap over build/libpcrec.a), compiles every
corpus pattern (scripts/emit_sweep.py's own enumeration: every `.rxt` under
tests/, `--features all`) at the default engine and at --engine=vm with the
lever MF_WSHADOW=1, and reads the kit's `MFTRACE WSHADOW` records
(memfn/src/window.c `wf_shadow`): per window site, the old path's column
and the family's, for `reseed` (the RE-SEED bit against "the old site is
the offset-skip block"), `stop`, `plan` (tested offsets, ascending), `pin`,
`group` (the compare grouping), `arm` and `text` (each side rendered on a
scratch art, normalized form hash). A pre-check's FUNC parts are one record
each (`part`, the kit manager's wsc3 ruling 3). It prints the mismatch count
per column and writes every mismatching record to OUT/mismatch_<column>.tsv;
a difference a DECLARED EQUIVALENCE (EQUIV, below) covers is counted under
its name instead.

G2's GENERATED span sites carry no old fields, so they have no old path to
shadow: their comparator is G2's own reference decision (g2_win_ref.c,
prefix_k's rules transcribed from the design), checked per column (DECIDE:
alt/stop/plan/grouping; PLAN; PROOF) by memfn/tests/run_g2_win.sh. With
--g2 this script runs it and prints its verdict beside the corpus counts.

WHAT IT IS NOT. The family's decision transcribes prefix_k's model, so both
sides share the MODEL: a zero here is a localizer reading for commit 5's
diffs, never acceptance (commit 5's emit_sweep is). The `text` column
compares one rendering per side made the same way (one call where the site
was emitted in one call, else the define then a use with the define's
hooks), not the artifact's bytes.

Heavy (thousands of compiles): run it under the box lock
(`scripts/boxlock run --label wshadow -- python3 -I memfn/tests/wshadow.py`).

--pattern P (repeatable) shadows the given patterns instead of the corpus:
a witness run (S1411: R stated past the walk-proven stretch reads as plan
and group mismatches on `xy.*xy(?i:z)`, docs/dev/lanes/wsc3_report.md).

usage: wshadow.py [--tree DIR] [--out DIR] [--jobs N] [--every K] [--g2]
                  [--pattern P ...]
"""
import argparse
import collections
import concurrent.futures
import os
import re
import subprocess
import sys

COLUMNS = ("reseed", "stop", "plan", "pin", "group", "arm", "text")
REC = re.compile(r"^MFTRACE WSHADOW (.*)$")

# THE DECLARED EQUIVALENCES: a record whose row holds compares the listed
# columns SEMANTICALLY, as one decision both sides reach in two spellings, so
# a difference there is no mismatch; it is counted under the row's name. Every
# other column of that record is still compared literally (`text` never
# appears here: the rendered text must be equal). One row per equivalence, its
# reason beside it; a new spelling difference is a new row, never a special
# case in the family.
EQUIV = (
    # (name, holds(record), columns, reason)
    ("never-yields", lambda r: r.get("yields") == "0/0", ("stop", "plan", "group"),
     "the old site scans an EMPTY set (stop 0, no candidate can hold it) and the "
     "family's A-empty states no stop: both decide that no candidate is ever yielded "
     "(the kit manager's wsc3 ruling 2: \\p{Cn}-shaped VM hats)"),
)


def build_traced(tree, out):
    lib = os.path.join(out, "libpcrec_wsh.a")
    exe = os.path.join(out, "pcrec-wsh")
    cc = os.environ.get("CC", "gcc")
    env = dict(os.environ, CC=cc, TMPDIR=out)
    subprocess.run(["bash", os.path.join(tree, "tests/memfn/mk_mftrace_lib.sh"), lib,
                    os.path.join(tree, "build/libpcrec.a"), "-std=gnu11", "-O2"],
                   check=True, env=env)
    subprocess.run([cc, "-O2", "-std=gnu11", "-I" + os.path.join(tree, "lib"),
                    "-I" + os.path.join(tree, "src"), "-o", exe,
                    os.path.join(tree, "cli/main.c"), lib], check=True)
    return exe


def corpus(tree, exe):
    sys.path.insert(0, os.path.join(tree, "scripts"))
    import emit_sweep  # noqa: E402  (the one enumeration; never a second)
    return emit_sweep.enumerate_corpus(exe, tree, 60)


def one(exe, pattern, engine):
    argv = [exe, "-p", "rx", "--features", "all", "-o", "-"]
    if engine:
        argv.append("--engine=" + engine)
    argv += ["--pattern", pattern]
    env = dict(os.environ, MF_WSHADOW="1")
    try:
        r = subprocess.run(argv, capture_output=True, timeout=120, env=env)
    except subprocess.TimeoutExpired:
        return None, []
    recs = []
    for line in r.stderr.decode("utf-8", "replace").splitlines():
        m = REC.match(line)
        if m:
            recs.append(dict(kv.split("=", 1) for kv in m.group(1).split(" ")))
    return r.returncode, recs


def canon_groups(g):
    """A grouping column in canonical form: each compare's id renumbered by
    its first appearance in plan order (the two sides number compares
    differently; only which positions share one compare is compared)."""
    if g in ("-", "?"):
        return g
    seen = {}
    return ",".join(str(seen.setdefault(x, len(seen))) for x in g.split(","))


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--tree", default=os.path.normpath(os.path.join(here, "../..")))
    ap.add_argument("--out", default=None)
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--every", type=int, default=1)
    ap.add_argument("--g2", action="store_true")
    ap.add_argument("--pattern", action="append", default=[])
    a = ap.parse_args()
    out = a.out or os.path.join(a.tree, "build", "wshadow")
    os.makedirs(out, exist_ok=True)
    exe = build_traced(a.tree, out)
    if a.pattern:
        pats = [("--pattern", None, p) for p in a.pattern]
    else:
        pats = corpus(a.tree, exe)[:: max(1, a.every)]
    if not pats:
        print("FAIL: the corpus enumeration is empty")
        return 1
    tasks = [(f, p, e) for (f, _k, p) in pats for e in (None, "vm")]
    sites = 0
    compiles = 0
    failed = 0
    mism = collections.Counter()
    equiv = collections.Counter()
    rows = collections.defaultdict(list)
    paths = collections.Counter()
    parts = 0
    nparts = collections.Counter()      # pre-check sites by their stating parts
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(one, exe, p, e): (f, p, e) for (f, p, e) in tasks}
        for fu in concurrent.futures.as_completed(futs):
            f, p, e = futs[fu]
            rc, recs = fu.result()
            compiles += 1
            if rc is None:
                failed += 1
            per = collections.Counter((r.get("art"), r.get("site")) for r in recs
                                      if r.get("part", "-") != "-")
            for k in per.values():
                nparts[k] += 1
            for r in recs:
                sites += 1
                parts += r.get("part", "-") != "-"
                paths[r.get("path", "?")] += 1
                for c in COLUMNS:
                    o, _, n = r.get(c, "?/?").partition("/")
                    if c == "group":
                        o, n = canon_groups(o), canon_groups(n)
                    if o != n:
                        why = next((e[0] for e in EQUIV if c in e[2] and e[1](r)), None)
                        if why:
                            equiv[why, c] += 1
                            continue
                        mism[c] += 1
                        rows[c].append((f, e or "default", p, r.get(c), r.get("part", "-"),
                                        r.get("alt"), r.get("path")))
    for c in COLUMNS:
        with open(os.path.join(out, "mismatch_%s.tsv" % c), "w") as fh:
            fh.write("file\tengine\tpattern\told/family\tpart\talt\tpath\n")
            for row in sorted(rows[c]):
                fh.write("\t".join(str(x).encode("unicode_escape").decode() for x in row) + "\n")
    print("wshadow: %d patterns, %d compiles (%d timed out), %d window sites shadowed "
          "(%d of them pre-check parts)" % (len(pats), compiles, failed, sites, parts))
    print("wshadow: pre-check sites stating parts, by parts: " +
          (" ".join("%d=%d" % kv for kv in sorted(nparts.items())) or "none"))
    print("wshadow: family paths: " + " ".join("%s=%d" % kv for kv in sorted(paths.items())))
    for c in COLUMNS:
        print("wshadow: mismatches %-6s %d" % (c, mism[c]))
    for name, _h, cols, _why in EQUIV:
        print("wshadow: equivalent %s: %s" % (name, " ".join(
            "%s=%d" % (c, equiv[name, c]) for c in cols)))
    print("wshadow: records per column in %s/mismatch_<column>.tsv" % out)
    if sites == 0:
        print("FAIL: no window site was shadowed (K35: an empty population)")
        return 1
    if a.g2:
        env = dict(os.environ, TMPDIR=out)
        r = subprocess.run(["bash", os.path.join(a.tree, "memfn/tests/run_g2_win.sh")],
                           capture_output=True, env=env)
        tail = r.stdout.decode("utf-8", "replace").splitlines()
        fails = [l for l in tail if l.startswith("FAIL")]
        print("wshadow: G2 span sites (run_g2_win.sh, the reference's columns): rc %d, %s"
              % (r.returncode, next((l for l in tail if l.startswith("checks failed")), "?")))
        for l in fails[:20]:
            print("  " + l)
    return 0


if __name__ == "__main__":
    sys.exit(main())
