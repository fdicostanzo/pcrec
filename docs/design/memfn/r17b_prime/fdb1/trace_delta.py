#!/usr/bin/env python3
"""docs/design/memfn/r17b_prime/fdb1/trace_delta.py --ref REF_TRACED --bin TRACED
       [--every K] [--jobs J]

R17-b' B1's TRACE COMPARE (lane fdb1; r17b_prime.md rev 3 §3.4, B1 row:
"the trace compare: new `fd` shadow records only (B1 retires none)"). Both
binaries are pcrec harnesses linked against an -DMF_TRACE kit
(mk_trace_harness.sh). Every distinct corpus pattern (emit_sweep's
population, every K-th) compiles at three arms (default, --engine=vm,
-e utf8) on both; the `MFTRACE` stderr records are compared IN ORDER after
removing, from the working side only, the records B1 DECLARES new:

  - every record of table `fd` or phase `shadow` (the finder shadow), and
    every `MFTRACE FD` and `MFTRACE FDKEY` line;
  - every `MFTRACE ASK` line (the define-time re-ask, §4.5 rule 2);
  - every `REACH ... field=F` line whose F is a field B1 added
    (body, start, site_kind, layer, need).

Anything else that differs (a reference record missing, reordered, or a new
record of another kind) fails. A self-control runs first: the reference
against itself must compare equal, and the working side UNFILTERED must
differ from the reference on some pattern (else the filter is vacuous).
"""
import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "../../../../.."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import emit_sweep as es  # noqa: E402

ARMS = (("default", []), ("vm", ["--engine=vm"]), ("utf8", ["-e", "utf8"]))
NEW_FIELDS = {b"body", b"start", b"site_kind", b"layer", b"need"}


def records(binary, pattern, extra):
    argv = [binary, "-p", "rx", "--features", "all"] + extra + ["-o", "-"]
    argv += es._pattern_argv(binary, pattern)
    try:
        r = subprocess.run(argv, capture_output=True, timeout=60)
    except subprocess.TimeoutExpired:
        return None
    return [ln for ln in r.stderr.split(b"\n") if ln.startswith(b"MFTRACE")]


def declared_new(ln):
    if ln.startswith((b"MFTRACE FD ", b"MFTRACE FDKEY ", b"MFTRACE ASK")):
        return True
    toks = ln.split()
    if b"table=fd" in toks or b"phase=shadow" in toks:
        return True
    if len(toks) > 1 and toks[1] == b"REACH":
        for t in toks:
            if t.startswith(b"field=") and t[6:] in NEW_FIELDS:
                return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--ls-bin", required=True)
    ap.add_argument("--every", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    pats = es.distinct_patterns(es.enumerate_corpus(a.ls_bin, ROOT, 30), every=a.every)
    pats = [(p[2] if isinstance(p, tuple) else p) for p in pats]
    items = [(p, arm, extra) for p in pats for arm, extra in ARMS]

    def task(item):
        p, arm, extra = item
        ra, rb = records(a.ref, p, extra), records(a.bin, p, extra)
        if ra is None or rb is None:
            return p, arm, "timeout", 0, 0
        rr = records(a.ref, p, extra)
        if rr != ra:
            return p, arm, "ref-nondeterministic", 0, 0
        fb = [ln for ln in rb if not declared_new(ln)]
        return p, arm, ("same" if fb == ra else "differ"), int(rb != ra), len(rb) - len(fb)

    bad, raw_moved, new_recs, n = [], 0, 0, 0
    with ThreadPoolExecutor(a.jobs) as ex:
        for p, arm, verdict, raw, nnew in ex.map(task, items):
            n += 1
            raw_moved += raw
            new_recs += nnew
            if verdict != "same":
                bad.append((arm, es.encode_escape(p), verdict))
    for arm, p, v in bad[:20]:
        print("FAIL: %s %s: %s" % (arm, p, v))
    print("trace delta: %d (pattern, arm) compiles; %d carry B1's new records (%d records "
          "filtered as declared); %d differ outside the declaration"
          % (n, raw_moved, new_recs, len(bad)))
    if raw_moved == 0:
        print("FAIL: no compile carried a new record: the filter is vacuous (control)")
        return 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
