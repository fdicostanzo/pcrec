#!/usr/bin/env python3
"""docs/design/memfn/r17b_prime/fdb1/shadow_census.py -- R17-b' B1's two
compile-only censuses over emit_sweep's population (lane fdb1; r17b_prime.md
rev 3 §1.6 [rev3 B6], §4.5 rule 6).

  shadow_census.py reader   --bin TRACE_PCREC  [--every K] [--jobs J] --out TSV
  shadow_census.py manifest --bin MFTRACE_HARNESS --set SET.tsv
                            [--every K] [--jobs J] --out TSV

READER: compiles every distinct corpus pattern under four arms (default,
--engine=vm, -e utf8, -fmemfn-simd) with a -DPCREC_CAND_TRACE compiler and
PCREC_MF_ASK_TRACE=1, and tallies the reader shadow's `MFASK` records (G1 /
R4 / L4 computed from pcrec's own row AND from the kit's form class) by
(reader, arm, verdict), plus every `CANDORACLE` abort. An in-scope
disagreement ABORTS the compile (reader-shadow-differs), so the gate is
`aborts == 0`; the out-of-scope and recorded arms are counted for the report.

MANIFEST: compiles the same population (byte and byte-vm arms, R17-b's
census arms, r17b_prime/census_shapes.py) with a traced pcrec-harness (the
kit built -DMF_TRACE, pcrec -DPCREC_HARNESS) under `--harness=measures=SET`,
and writes every slot-FIND shadow decision at layer OFF of a SET site of two
or more members (one-member sites read the consumer kind, stated from B2, so
their B1 decision is not B4's: fd_shadow's header) as one TSV line:
`arm  pattern-escaped  site  members  shape  row  pick  mover`. `mover` is 1
where the pick is V1 (a byte move at B4, when R7 routes); this file, under
the interim set, is B4's COMMITTED PREDICTED-MOVER MANIFEST: B4's movers by
ID are held to it (r17b_prime.md §1.6 [rev3 B6]).

The population is emit_sweep's (enumerate_corpus + distinct_patterns, the
--list-source escapes), so a sample here and a sample there are one set.
"""
import argparse
import os
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "../../../../.."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import emit_sweep as es  # noqa: E402

READER_ARMS = (("default", []), ("vm", ["--engine=vm"]), ("utf8", ["-e", "utf8"]),
               ("simd", ["-fmemfn-simd"]))
MANIFEST_ARMS = (("byte", []), ("byte-vm", ["--engine=vm"]))


def compile_one(binary, pattern, extra, env, timeout=60):
    argv = [binary, "-p", "rx", "--features", "all"] + extra + ["-o", "-"]
    argv += es._pattern_argv(binary, pattern)
    try:
        r = subprocess.run(argv, capture_output=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return None, b"TIMEOUT"
    return r.returncode, r.stderr


def population(lsbin, every):
    pats = es.distinct_patterns(es.enumerate_corpus(lsbin, ROOT, 30), every=every)
    return [(p[2] if isinstance(p, tuple) else p) for p in pats]


def reader(a):
    env = dict(os.environ, PCREC_MF_ASK_TRACE="1")
    pats = population(a.bin, a.every)
    items = [(p, arm, extra) for p in pats for arm, extra in READER_ARMS]
    tally, aborts, nfail = Counter(), [], 0

    def task(item):
        p, arm, extra = item
        rc, err = compile_one(a.bin, p, extra, env)
        recs = [ln.split(b"\t") for ln in err.split(b"\n") if ln.startswith(b"MFASK\t")]
        orc = [ln for ln in err.split(b"\n") if ln.startswith(b"CANDORACLE")]
        return p, arm, rc, recs, orc

    with ThreadPoolExecutor(a.jobs) as ex:
        for p, arm, rc, recs, orc in ex.map(task, items):
            for r in recs:
                tally[(arm,) + tuple(x.decode() for x in r[1:4])] += 1
            if orc:
                aborts.append((arm, es.encode_escape(p), orc[0].decode("utf-8", "replace")))
            elif rc not in (0, 1):
                nfail += 1
    with open(a.out, "w") as fh:
        fh.write("# reader-shadow census (shadow_census.py reader): arm, reader, "
                 "shadow-arm, verdict, records\n")
        fh.write("# population: %d distinct patterns x %d arms (every %d)\n"
                 % (len(pats), len(READER_ARMS), a.every))
        for k in sorted(tally):
            fh.write("\t".join(k) + "\t%d\n" % tally[k])
        fh.write("# CANDORACLE aborts: %d\n" % len(aborts))
        for ab in aborts:
            fh.write("# ABORT\t%s\t%s\t%s\n" % ab)
    print("reader census: %d patterns x %d arms, %d MFASK records, %d aborts, "
          "%d other failures -> %s" % (len(pats), len(READER_ARMS), sum(tally.values()),
                                       len(aborts), nfail, a.out))
    return 1 if aborts else 0


def manifest(a):
    pats = population(a.ls_bin or a.bin, a.every)
    extra0 = ["--harness=measures=" + a.set]
    items = [(p, arm, extra) for p in pats for arm, extra in MANIFEST_ARMS]

    def task(item):
        p, arm, extra = item
        rc, err = compile_one(a.bin, p, extra0 + extra, dict(os.environ))
        out = []
        for ln in err.split(b"\n"):
            if not ln.startswith(b"MFTRACE FD ") or b" slot=FIND " not in ln:
                continue
            d = dict(t.split(b"=", 1) for t in ln.split()[2:] if b"=" in t)
            if d.get(b"layer") != b"OFF":
                continue
            m = int(d.get(b"members", b"0"))
            if m < 2:
                continue
            out.append((d[b"site"].decode(), m, d[b"shape"].decode(), d[b"row"].decode(),
                        d[b"pick"].decode()))
        return p, arm, rc, out

    rows, movers, nsite = [], set(), 0
    with ThreadPoolExecutor(a.jobs) as ex:
        for p, arm, rc, out in ex.map(task, items):
            for site, m, shape, row, pick in out:
                nsite += 1
                mv = int(pick == "V1")
                if mv:
                    movers.add((arm, p))
                rows.append((arm, es.encode_escape(p), site, m, shape, row, pick, mv))
    rows.sort()
    with open(a.out, "w") as fh:
        fh.write("# R17-b' B4's PREDICTED-MOVER MANIFEST (lane fdb1, B1; r17b_prime.md "
                 "§1.6 [rev3 B6]): the finder shadow's slot-FIND decision at layer OFF for "
                 "every set site of >= 2 members, under the set %s\n"
                 % os.path.basename(a.set))
        fh.write("# population: %d distinct patterns x arms %s (every %d); %d set "
                 "sites; %d (arm, pattern) movers\n"
                 % (len(pats), ",".join(x for x, _ in MANIFEST_ARMS), a.every, nsite,
                    len(movers)))
        fh.write("# generated by docs/design/memfn/r17b_prime/fdb1/shadow_census.py manifest\n")
        fh.write("#arm\tpattern\tsite\tmembers\tshape\trow\tpick\tmover\n")
        for r in rows:
            fh.write("%s\t%s\t%s\t%d\t%s\t%s\t%s\t%d\n" % r)
    by_shape = Counter((r[0], r[4], r[6]) for r in rows)
    print("manifest: %d set sites, %d (arm, pattern) movers -> %s" % (nsite, len(movers), a.out))
    for k in sorted(by_shape):
        print("  %s %s %s: %d" % (k[0], k[1], k[2], by_shape[k]))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("reader", "manifest"))
    ap.add_argument("--bin", required=True)
    ap.add_argument("--ls-bin", help="a plain pcrec for --list-source (manifest mode)")
    ap.add_argument("--set")
    ap.add_argument("--every", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    return reader(a) if a.mode == "reader" else manifest(a)


if __name__ == "__main__":
    sys.exit(main())
