#!/usr/bin/env python3
"""docs/design/start_table/deny_census.py -- the DENY-DELTA census
([r2] start_table.md §2.1 method 2, §3.4's per-row control).

For every corpus pattern, in each base arm (auto / --engine=vm x -e byte /
-e utf8), compile at default and under each start-family deny/force flag
(row_census.START_FLAGS) and compare the EMITTED BYTES. A mover is an
artifact whose bytes differ. Each mover is attributed by the start-family
stamps (row_census.stamps_of, ROUTE-keyed) that moved with it; a mover whose
bytes moved while NO start stamp did is a HIDDEN mover, and its first
differing line is fingerprinted (digits/identifiers normalised) so that a
decision site no stamp reports is found by its emitted text rather than by a
hand list (this is how K65 set-rest / K66 whole-run / P4 set-leads show up).

Shares nothing with the code under refactor: it reads bytes and stamps only.

Usage: deny_census.py PCREC_BIN TREE OUTDIR [--jobs N] [--flags F1,F2] [--every K]
--every K keeps every K-th distinct pattern (sorted order), for a COST or
coverage sample ([r2.1 C-N3]); the committed census tables are --every 1.
Writes OUTDIR/deny_census.tsv (arm, flag, ok_default, ok_flag, movers,
visible, hidden, refusal_moves), deny_transitions.tsv (arm, flag, key,
from, to, count), deny_hidden.tsv (arm, flag, fingerprint, count, example
pattern), deny_movers.tsv (arm, flag, pattern-hex, class, keys),
row_census.tsv (the per-arm stamp census, default and every deny arm, in
row_census.py's format) and slowest.tsv.
"""
import collections, concurrent.futures, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import row_census as rc  # noqa: E402

es = rc.es


def fingerprint(a, b):
    """The first differing line (a linear zip, not a diff: artifacts run to
    100k lines), normalised so one emitter site gives one fingerprint."""
    al, bl = a.split(b"\n"), b.split(b"\n")
    for x, y in zip(al, bl):
        if x != y:
            line = x.decode("utf-8", "replace").strip()
            line = re.sub(r"0x[0-9a-fA-F]+|\b\d+\b", "N", line)
            line = re.sub(r"'(\\.|[^'])'", "'C'", line)
            return line[:90]
    return "<length only>"


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("pcrec"); ap.add_argument("tree"); ap.add_argument("outdir")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--flags", default=",".join(rc.START_FLAGS))
    ap.add_argument("--every", type=int, default=1)
    a = ap.parse_args()
    flags = a.flags.split(",")
    pats = rc.es.enumerate_corpus(a.pcrec, a.tree, 30)
    pats = sorted(set(p[2].encode("utf-8", "surrogateescape") if isinstance(p[2], str)
                      else p[2] for p in pats))
    pats = pats[::a.every]
    t_start = time.time()
    print(f"corpus patterns (distinct, every {a.every}): {len(pats)}", flush=True)
    summ, trans, hidden, movers, rows, slow = [], collections.Counter(), {}, [], [], []
    for eng, enc, base in rc.ARMS:
        arm = f"{eng}/{enc}"

        def job(p):
            t = time.time()
            d0 = rc.one(a.pcrec, p, base, True)
            res = []
            for fl in flags:
                res.append(rc.one(a.pcrec, p, base + [fl], True))
            return p, d0, res, time.time() - t
        stats = {fl: collections.Counter() for fl in flags}
        armcnt = {fl: collections.Counter() for fl in [""] + flags}
        done = 0
        with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
            for p, d0, res, dt in ex.map(job, pats):
                done += 1
                slow.append((dt, arm, p))
                if done % 500 == 0:
                    print(f"  {arm}: {done}/{len(pats)}", flush=True)
                for fl, d in [("", d0)] + list(zip(flags, res)):
                    if d is not None:
                        armcnt[fl][("compiled", "")] += 1
                        for k, v in d[0].items():
                            armcnt[fl][(k, v)] += 1
                for fl, d1 in zip(flags, res):
                    st = stats[fl]
                    if d0 is not None:
                        st["ok_default"] += 1
                    if d1 is not None:
                        st["ok_flag"] += 1
                    if (d0 is None) != (d1 is None):
                        st["refusal_moves"] += 1
                        movers.append((arm, fl, p.hex(), "refusal", ""))
                        continue
                    if d0 is None or d0[1] == d1[1]:
                        continue
                    st["movers"] += 1
                    s0, s1 = d0[0], d1[0]
                    moved = es.start_keys_moved(s0, s1)   # the gate's own definition
                    keys = [k for k in moved if ":" not in k]
                    rkeys = [k for k in moved if ":" in k]
                    for k in keys + rkeys:
                        trans[(arm, fl, k, s0.get(k, "-"), s1.get(k, "-"))] += 1
                    if keys or rkeys:
                        st["visible"] += 1
                        cls = "visible"
                    else:
                        st["hidden"] += 1
                        cls = "hidden"
                        fp = fingerprint(d0[1], d1[1])
                        h = hidden.setdefault((arm, fl, s0.get("ROUTE", "?"), fp), [0, p])
                        h[0] += 1
                    movers.append((arm, fl, p.hex(), cls, ",".join(keys + rkeys)))
        for fl, cnt in armcnt.items():
            for (k, v), n in sorted(cnt.items()):
                rows.append((arm + fl, k, v, n))
        for fl in flags:
            st = stats[fl]
            summ.append((arm, fl, st["ok_default"], st["ok_flag"], st["movers"],
                         st["visible"], st["hidden"], st["refusal_moves"]))
            print(f"{arm:10s} {fl:22s} movers {st['movers']:5d} visible {st['visible']:5d}"
                  f" hidden {st['hidden']:4d} refusal {st['refusal_moves']}", flush=True)
    print(f"WALL {time.time() - t_start:.1f}s compiles {len(pats) * (1 + len(flags)) * len(rc.ARMS)}"
          f" jobs {a.jobs}", flush=True)
    os.makedirs(a.outdir, exist_ok=True)
    with open(os.path.join(a.outdir, "deny_census.tsv"), "w") as f:
        f.write("arm\tflag\tok_default\tok_flag\tmovers\tvisible\thidden\trefusal_moves\n")
        for r in summ:
            f.write("\t".join(map(str, r)) + "\n")
    with open(os.path.join(a.outdir, "deny_transitions.tsv"), "w") as f:
        f.write("arm\tflag\tkey\tfrom\tto\tcount\n")
        for k, n in sorted(trans.items()):
            f.write("\t".join(map(str, k + (n,))) + "\n")
    with open(os.path.join(a.outdir, "deny_hidden.tsv"), "w") as f:
        f.write("arm\tflag\troute\tfingerprint\tcount\texample\n")
        for (arm, fl, rt, fp), (n, p) in sorted(hidden.items()):
            f.write(f"{arm}\t{fl}\t{rt}\t{fp}\t{n}\t{p.decode('utf-8', 'replace')}\n")
    # the row census's DENY ARM ([r2 checks-M4]), from the same compiles:
    # row_census.tsv's format (arm, stamp, value, count), default arms
    # included, so the committed row_census.tsv is this file.
    with open(os.path.join(a.outdir, "row_census.tsv"), "w") as f:
        f.write("arm\tstamp\tvalue\tcount\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    with open(os.path.join(a.outdir, "slowest.tsv"), "w") as f:
        f.write("seconds_all_flags\tarm\tpattern\n")
        for dt, arm, p in sorted(slow, reverse=True)[:25]:
            f.write(f"{dt:.2f}\t{arm}\t{p.decode('utf-8', 'replace')[:120]}\n")
    with open(os.path.join(a.outdir, "deny_movers.tsv"), "w") as f:
        f.write("arm\tflag\tpattern_hex\tclass\tkeys\n")
        for r in movers:
            f.write("\t".join(r) + "\n")


if __name__ == "__main__":
    main()
