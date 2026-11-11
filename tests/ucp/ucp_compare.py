#!/usr/bin/env python3
"""tests/ucp/ucp_compare.py — pcrec's UCP SETS against the committed 10.46
store, EXACT (docs/design/ucp_design.md §1.6, D130 Q9).

For every construct in `ucp_sets.py` and both encodings:

  * NARROW (every byte cell, and the utf8 cells the ruling ships): pcrec
    compiles `--ucp` + the construct, the artifact is driven over EVERY code
    point of the encoding (tests/uprops/uprops_sweep.c, reused, not copied),
    and the member intervals must EQUAL the store's
    `oracle_store/libpcre2-10.46-ucp/membership.tsv` row. The store is the
    true reference pin, so no drift budget exists here on any box.
  * construct == spelling (every utf8 entry): the store must say libpcre2's
    construct EQUALS the spelling the definitions table carries, so the
    chain construct == spelling (the store) == producer
    (tests/registry/definitions_check.c) stays pinned.

Every set compiles under both encodings; the wide/narrow partition this
script once counted (the PCREC_UCP_NARROW_MAX_INTERVALS knee) is retired with
the knee (review 2026-11-10 r4 ucpu3 RULES-9/checks-8): it compared
ucp_sets.py with itself.

Usage: ucp_compare.py PCREC CC WORKDIR       exit 0 = all agree
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tests", "oracle"))
sys.path.insert(0, HERE)
import oracle_store as os_  # noqa: E402
from ucp_sets import SETS  # noqa: E402

STORE_ROOT = os.path.join(ROOT, "oracle_store")
OID = os_.OracleId("libpcre2", "10.46", ucp=True)
SWEEP = os.path.join(ROOT, "tests", "uprops", "uprops_sweep.c")

npass = nfail = 0


def ok(msg):
    global npass
    npass += 1
    print("  ok: " + msg)


def bad(msg):
    global nfail
    nfail += 1
    print("FAIL: " + msg)


def store(construct, enc):
    a = os_.lookup(STORE_ROOT, OID, "membership", property=construct,
                   encoding=enc)
    return None if a is None else a[0]


def compile_sweep(pcrec, cc, work, construct, enc):
    """(refused_message, intervals) — exactly one is not None."""
    gen = os.path.join(work, "g.c")
    r = subprocess.run([pcrec, "--features", "all", "--ucp", "-e", enc, "-p",
                        "rx", "-o", gen, "--pattern", construct],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        return (r.stderr.strip() or "refused"), None
    maxcp = "0x10FFFF" if enc == "utf8" else "0xFF"
    exe = os.path.join(work, "sweep")
    r = subprocess.run([cc, "-O1", "-std=gnu11", "-I", work,
                        '-DUPROPS_ARTIFACT="g.c"', "-DUPROPS_MAXCP=" + maxcp,
                        "-o", exe, SWEEP], capture_output=True, text=True,
                       timeout=300)
    if r.returncode != 0:
        raise SystemExit("ucp_compare: sweep driver does not build for %r %s:"
                         "\n%s" % (construct, enc, r.stderr[-1500:]))
    r = subprocess.run([exe], capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise SystemExit("ucp_compare: sweep over %r %s did not complete"
                         % (construct, enc))
    return None, r.stdout.strip()


def main(argv):
    if len(argv) != 4:
        sys.stderr.write(__doc__)
        return 2
    pcrec, cc, work = argv[1:]
    compared = 0
    for construct, spelling in SETS:
        for enc in ("byte", "utf8"):
            want = store(construct, enc)
            if want is None:
                bad("%s %s: the committed store has no row (re-run "
                    "tests/ucp/build_ucp_store.py)" % (construct, enc))
                continue
            msg, got = compile_sweep(pcrec, cc, work, construct, enc)
            if enc == "utf8":
                sp = store(spelling, "utf8")
                if sp != want:
                    bad("%s utf8: libpcre2's construct and the table's "
                        "spelling %r DIFFER in the store" % (construct,
                                                             spelling))
                else:
                    ok("%s utf8: store construct == spelling %s" % (construct,
                                                                    spelling))
            if msg is not None:
                bad("%s %s: REFUSED (%s) — the ruling ships it" % (construct,
                                                                   enc, msg))
                continue
            compared += 1
            if got != want:
                bad("%s %s: pcrec's set differs from libpcre2 10.46's "
                    "(pcrec %d intervals, oracle %d)"
                    % (construct, enc, len(got.split()), len(want.split())))
            else:
                ok("%s %s: pcrec == libpcre2 10.46 (%d intervals)"
                   % (construct, enc, len(want.split())))
    # the POPULATION, counted (K35): 16 byte + 16 utf8 compared. A shrunken
    # population is a failure, not a pass.
    if compared != 32:
        bad("population moved: %d sets compared (32 expected) — ucp_sets.py "
            "changed" % compared)
    else:
        ok("population: 32 sets compared exactly")
    print("ucp_compare: %d passed, %d failed" % (npass, nfail))
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
