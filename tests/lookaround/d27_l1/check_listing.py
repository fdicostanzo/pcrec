#!/usr/bin/env python3
"""The LISTING half of the D27 L1 witnesses (span_arms §14.4 L1, lane l1ffix).

What it checks: for every row of l1d27_listing.tsv (the blinded author's, never
edited here), pcrec's own `--emit-facts` listing of the row's pattern, in the
row's encoding, gives the `req_whole_run` value and why the author recorded.
The ANSWERS of the same witnesses are l1d27_witnesses.rxt, which rides
`test-corpus`; a `.rxt` cannot state a listing, which is why this file exists.

Its independent control: the expected values are the AUTHOR's record (written
from the spec, blinded, against pcrec's listing at authoring time), and the
author's own PASS/FAIL verdict against the spec is kept beside each one. A row
the author judged FAIL (the listing states less than the promise allows) must
name a declared LIMIT in l1d27_limits.tsv, written by the build side, and a
PASS row must name none: a limit that stops applying, or a new shortfall with
no named limit, is red, never a silent pass.

How it fails: any listing that moves (a later unit lifting a limit moves its
rows: re-judge them against `spec_expectation`, re-pin the value, drop the
limit), a FAIL row with no limit or an undeclared key, a PASS row with one, a
limit row naming no listing row, and an empty population (K35).

usage: check_listing.py PCREC   (exit 0 green, 1 red, 2 usage)
"""
import csv
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LISTING = os.path.join(HERE, "l1d27_listing.tsv")
LIMITS = os.path.join(HERE, "l1d27_limits.tsv")
KEYS = {"domain", "guard-domain", "rep-wall", "nested-item", "edge-drop"}


def listing(pcrec, pat, enc):
    """pcrec's (value, why) for `req_whole_run` of `pat` under `enc`."""
    p = subprocess.run([pcrec, "--features", "all", "--emit-facts=" + enc,
                        "--pattern", pat], capture_output=True, text=True,
                       timeout=120)
    for line in p.stdout.splitlines():
        f = line.split("\t")
        if len(f) > 7 and f[0] == enc and f[1] == "req_whole_run":
            return f[6], f[7]
    return "REFUSED", (p.stderr.strip().splitlines() or ["no row"])[0]


def main():
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    pcrec = sys.argv[1]
    rows = list(csv.DictReader(open(LISTING), delimiter="\t"))
    limits = {}
    for line in open(LIMITS):
        if line.startswith("#") or not line.strip():
            continue
        rid, keys = line.rstrip("\n").split("\t")
        limits[rid] = keys.split(",")
    bad = []
    ids = set()
    for r in rows:
        rid = r["id"]
        ids.add(rid)
        got = listing(pcrec, r["pattern"], r["encoding"])
        want = (r["listing_req_whole_run"], r["listing_why"])
        if got != want:
            bad.append(f"{rid} `{r['pattern']}` ({r['encoding']}) lists {got[0]} [{got[1]}], "
                       f"recorded {want[0]} [{want[1]}]: re-judge against "
                       f"`{r['spec_expectation']}`, re-pin, and drop its limit if lifted")
        fail = r["verdict"] == "FAIL"
        lim = limits.get(rid)
        if fail and not lim:
            bad.append(f"{rid} fails the spec ({r['finding']}) and names no limit")
        if not fail and lim:
            bad.append(f"{rid} meets the spec but still names limit(s) {','.join(lim)}")
        for k in lim or []:
            if k not in KEYS:
                bad.append(f"{rid} names undeclared limit key `{k}`")
    for rid in limits:
        if rid not in ids:
            bad.append(f"limit row {rid} names no listing row")
    nfail = sum(1 for r in rows if r["verdict"] == "FAIL")
    print(f"REACH: {len(rows)} listing row(s), {nfail} at a named limit")
    if not rows:
        bad.append("no listing row was read")
    for b in bad:
        print("FAIL:", b)
    if bad:
        return 1
    print(f"PASS: [d27-l1-listing] {len(rows)} rows list as recorded; "
          f"{nfail} shortfalls each name a declared limit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
