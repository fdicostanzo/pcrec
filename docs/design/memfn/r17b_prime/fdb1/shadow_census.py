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

[b4close2] (lane b4close2) three additions to MANIFEST mode, all survey/record:
  * K35: a COMPILE THAT FAILS IS NEVER DROPPED SILENTLY. Every non-zero return
    code (and every timeout) is checked against the same argv run through the
    plain compiler (`--ls-bin`, no lever): a pattern the plain compiler refuses
    too (same code) is an expected refusal, counted and printed; anything else
    is a LOST compile, listed, and the run exits 3 without writing a
    manifest. The totals line states rc0 / refused-in-both / lost.
  * `lookup` column: `ok`, or `NOMS` where the site's key lookup answered ABSENT
    for a key the set DOES hold (the site's art carries no measures: a compound
    walk's part compile, src/core/compound.c part_compile, `.harness = NULL`;
    such an attempt is DISCARDED when the compound is not admitted). A NOMS
    row's pick is "no set" (R7w) by construction, not the rule's; the summary
    reports it apart.
  * `poscov`, `hull`, `walk0` columns: the POSCOST survey fields of
    memfn/src/finder.c (needs a harness built with POSCOV=1,
    mk_trace_harness.sh; `-` columns otherwise).
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
    pats_of = {}                         # key -> distinct patterns

    def task(item):
        p, arm, extra = item
        rc, err = compile_one(a.bin, p, extra, env)
        recs = [ln.split(b"\t") for ln in err.split(b"\n") if ln.startswith(b"MFASK\t")]
        orc = [ln for ln in err.split(b"\n") if ln.startswith(b"CANDORACLE")]
        return p, arm, rc, recs, orc

    with ThreadPoolExecutor(a.jobs) as ex:
        for p, arm, rc, recs, orc in ex.map(task, items):
            for r in recs:
                k = (arm,) + tuple(x.decode() for x in r[1:4])
                tally[k] += 1
                pats_of.setdefault(k, set()).add(p)
            if orc:
                aborts.append((arm, es.encode_escape(p), orc[0].decode("utf-8", "replace")))
            elif rc not in (0, 1):
                nfail += 1
    with open(a.out, "w") as fh:
        fh.write("# reader-shadow census (shadow_census.py reader): arm, reader, "
                 "shadow-arm, verdict, records, distinct patterns\n")
        fh.write("# population: %d distinct patterns x %d arms (every %d)\n"
                 % (len(pats), len(READER_ARMS), a.every))
        for k in sorted(tally):
            fh.write("\t".join(k) + "\t%d\t%d\n" % (tally[k], len(pats_of[k])))
        fh.write("# CANDORACLE aborts: %d\n" % len(aborts))
        for ab in aborts:
            fh.write("# ABORT\t%s\t%s\t%s\n" % ab)
    print("reader census: %d patterns x %d arms, %d MFASK records, %d aborts, "
          "%d other failures -> %s" % (len(pats), len(READER_ARMS), sum(tally.values()),
                                       len(aborts), nfail, a.out))
    return 1 if aborts else 0


def set_keys(path):
    """The keys the lever set holds (its `rows` section's first column)."""
    keys, sec = set(), None
    with open(path) as fh:
        for ln in fh:
            if ln.startswith("#section"):
                sec = ln.split()[1]
            elif sec == "rows" and not ln.startswith("#") and ln.strip():
                keys.add(ln.split("\t")[0])
    return keys


def pattern_list(path):
    """[e8min] --patterns FILE: `id<TAB>extra argv or -<TAB>pattern` per line (`#` lines skipped);
    the J1 population (a user-question list) instead of emit_sweep's corpus. One arm per
    line: the arm label is the extra argv ('byte' when empty)."""
    out = []
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            if ln.startswith("#") or not ln.strip("\n"):
                continue
            qid, extra, pat = ln.rstrip("\n").split("\t", 2)
            extra = "" if extra == "-" else extra
            out.append((pat.encode("utf-8"), "byte" if not extra else extra.replace(" ", ""),
                        extra.split(), qid))
    return out


def manifest(a):
    extra0 = ["--harness=measures=" + a.set]
    keys = set_keys(a.set)
    if a.patterns:
        items = pattern_list(a.patterns)
        pats = [i[0] for i in items]
    else:
        pats = population(a.ls_bin or a.bin, a.every)
        items = [(p, arm, extra, "") for p in pats for arm, extra in MANIFEST_ARMS]

    def task(item):
        p, arm, extra, qid = item
        rc, err = compile_one(a.bin, p, extra0 + extra, dict(os.environ))
        # K35: a failing compile is checked against the plain compiler, never dropped
        plain = None
        if rc != 0:
            plain, _ = compile_one(a.ls_bin or a.bin, p, extra, dict(os.environ))
        nom = set()                     # (art, site) with a held key answered absent
        for ln in err.split(b"\n"):
            if ln.startswith(b"MFTRACE FDKEY ") and b" found=0" in ln:
                d = dict(t.split(b"=", 1) for t in ln.split()[2:] if b"=" in t)
                if d.get(b"key", b"").decode() in keys:
                    nom.add((d[b"art"], d[b"site"]))
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
                        d[b"pick"].decode(),
                        "NOMS" if (d[b"art"], d[b"site"]) in nom else "ok",
                        d.get(b"poscov", b"-").decode(), d.get(b"hull", b"-").decode(),
                        d.get(b"walk0", b"-").decode()))
        return p, arm, rc, plain, out, qid

    rows, movers, nsite = [], set(), 0
    tally, lost = Counter(), []
    with ThreadPoolExecutor(a.jobs) as ex:
        for p, arm, rc, plain, out, qid in ex.map(task, items):
            if rc == 0:
                tally["rc0"] += 1
            elif rc is not None and plain == rc:       # a timeout is never a refusal
                tally["refused-in-both"] += 1
            else:
                tally["lost"] += 1
                lost.append((arm, es.encode_escape(p), rc, plain))
            for site, m, shape, row, pick, lk, pc, hull, w0 in out:
                nsite += 1
                mv = int(pick == "V1")
                if mv:
                    movers.add((arm, p))
                rows.append((arm, es.encode_escape(p), site, m, shape, row, pick, mv, lk,
                             pc, hull, w0) + ((qid,) if a.patterns else ()))
    total = sum(tally.values())
    line = ("compiles=%d rc0=%d refused-in-both=%d lost=%d"
            % (total, tally["rc0"], tally["refused-in-both"], tally["lost"]))
    if lost or total != len(items):
        print("LOST COMPILES (K35): " + line + " of %d expected" % len(items), file=sys.stderr)
        for l in lost[:20]:
            print("   lost\t%s\t%s\trc=%s\tplain rc=%s" % l, file=sys.stderr)
        return 3
    rows.sort()
    with open(a.out, "w") as fh:
        fh.write("# R17-b' B4's PREDICTED-MOVER MANIFEST (lane fdb1, B1; r17b_prime.md "
                 "§1.6 [rev3 B6]): the finder shadow's slot-FIND decision at layer OFF for "
                 "every set site of >= 2 members, under the set %s\n"
                 % os.path.basename(a.set))
        fh.write("# population: %d distinct patterns x arms %s (every %d); %d set "
                 "sites; %d (arm, pattern) movers\n"
                 % (len(pats), "per-line (--patterns)" if a.patterns else
                    ",".join(x for x, _ in MANIFEST_ARMS), a.every, nsite, len(movers)))
        fh.write("# compiles: %s\n" % line)
        fh.write("# generated by docs/design/memfn/r17b_prime/fdb1/shadow_census.py manifest\n")
        fh.write("#arm\tpattern\tsite\tmembers\tshape\trow\tpick\tmover\tlookup\tposcov\thull\twalk0%s\n" % ("\tqid" if a.patterns else ""))
        for r in rows:
            fh.write(("%s\t%s\t%s\t%d\t%s\t%s\t%s\t%d\t%s\t%s\t%s\t%s" + ("\t%s" if a.patterns else "") + "\n") % r)
    by_shape = Counter((r[0], r[4], r[6]) for r in rows)
    print("manifest: %d set sites, %d (arm, pattern) movers -> %s" % (nsite, len(movers), a.out))
    print("compiles: " + line)
    for k in sorted(by_shape):
        print("  %s %s %s: %d" % (k[0], k[1], k[2], by_shape[k]))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("reader", "manifest"))
    ap.add_argument("--bin", required=True)
    ap.add_argument("--ls-bin", help="a plain pcrec for --list-source (manifest mode)")
    ap.add_argument("--set")
    ap.add_argument("--patterns", help="manifest mode: a pattern list (pattern_list)")
    ap.add_argument("--every", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    return reader(a) if a.mode == "reader" else manifest(a)


if __name__ == "__main__":
    sys.exit(main())
