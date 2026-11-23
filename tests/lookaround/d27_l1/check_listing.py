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

Shared with d27_l3 (lane l3wire): `check_listing.py PCREC [DIR]` reads DIR's
`*_listing.tsv` and `*_limits.tsv` (DIR defaults to this directory, L1). The
profile is chosen by the listing's header: L1's has `listing_req_whole_run` (one
row per witness, `verdict` PASS/FAIL); L3's has `run`/`K`/`why`/`req_set_maxoff`
(one row per witness x encoding x config, `status` PASS/LIMIT/INFO; limits name a
witness id and apply when any of its rows is LIMIT; INFO is a sound join the brief
did not expect, never a limit). The limit rules are the same for both.

usage: check_listing.py PCREC [DIR]   (exit 0 green, 1 red, 2 usage)
"""
import csv
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
L3CONFIGS = {"def": [], "vm": ["--engine=vm"], "vmpf": ["--engine=vm", "-fprefilter"],
             "dfa": ["--engine=dfa"]}


def facts(pcrec, pat, enc, extra=()):
    """pcrec's {fact: (value, why)} for `pat` under `enc` (the --emit-facts rows)."""
    p = subprocess.run([pcrec, "--features", "all", "--emit-facts=" + enc, *extra,
                        "--pattern", pat], capture_output=True, text=True,
                       timeout=120)
    out = {}
    for line in p.stdout.splitlines():
        f = line.split("\t")
        if len(f) > 7 and f[0] == enc:
            out[f[1]] = (f[6], f[7])
    if "req_whole_run" not in out:
        out["req_whole_run"] = ("REFUSED", (p.stderr.strip().splitlines() or ["no row"])[0])
    return out


def listing(pcrec, pat, enc):
    """pcrec's (value, why) for `req_whole_run` of `pat` under `enc`."""
    return facts(pcrec, pat, enc)["req_whole_run"]


def l1_check(pcrec, rows, bad):
    """(id, fail?) per row; the listing must equal the author's record."""
    out = []
    for r in rows:
        rid = r["id"]
        got = listing(pcrec, r["pattern"], r["encoding"])
        want = (r["listing_req_whole_run"], r["listing_why"])
        if got != want:
            bad.append(f"{rid} `{r['pattern']}` ({r['encoding']}) lists {got[0]} [{got[1]}], "
                       f"recorded {want[0]} [{want[1]}]: re-judge against "
                       f"`{r['spec_expectation']}`, re-pin, and drop its limit if lifted")
        out.append((rid, r["verdict"] == "FAIL", r["finding"]))
    return out


def l3_check(pcrec, rows, bad):
    """(id, limit?) per row; run, K, why and req_set_maxoff must equal the record."""
    out = []
    for r in rows:
        rid = r["id"]
        extra = L3CONFIGS[r["config"]] + (["-i"] if r["flags"] == "i" else [])
        f = facts(pcrec, r["pattern"], r["encoding"], extra)
        got = (f["req_whole_run"], f.get("req_landmark_maxoff", ("?",))[0],
               f.get("req_set_maxoff", ("?",))[0])
        want = ((r["run"], r["why"]), r["K"], r["req_set_maxoff"])
        if got != want:
            bad.append(f"{rid} `{r['pattern']}` ({r['encoding']}, {r['config']}) lists "
                       f"{got[0][0]}@{got[1]} [{got[0][1]}] set {got[2]}, recorded "
                       f"{r['run']}@{r['K']} [{r['why']}] set {r['req_set_maxoff']}: re-judge "
                       f"against `{r['claim']}`, re-pin, and drop its limit if lifted")
        out.append((rid, r["status"] == "LIMIT", r["note"]))
    return out


def main():
    if len(sys.argv) not in (2, 3):
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    pcrec = sys.argv[1]
    here = os.path.abspath(sys.argv[2]) if len(sys.argv) == 3 else HERE
    tag = os.path.basename(here).replace("_", "-")
    names = os.listdir(here)
    lst = [n for n in names if n.endswith("_listing.tsv")]
    lim = [n for n in names if n.endswith("_limits.tsv")]
    if len(lst) != 1 or len(lim) != 1:
        print(f"FAIL: {here} needs exactly one *_listing.tsv and one *_limits.tsv")
        return 1
    rows = list(csv.DictReader(open(os.path.join(here, lst[0])), delimiter="\t"))
    limits = {}
    for line in open(os.path.join(here, lim[0])):
        if line.startswith("#") or not line.strip():
            continue
        rid, keys = line.rstrip("\n").split("\t")
        limits[rid] = keys.split(",")
    keys = set()
    for line in open(os.path.join(here, lim[0])):
        m = re.match(r"#   (\S+)\s+F\d+\.", line)  # a key's declaration line
        if m:
            keys.add(m.group(1))
    bad = []
    l3 = bool(rows) and "listing_req_whole_run" not in rows[0]
    res = (l3_check if l3 else l1_check)(pcrec, rows, bad)
    ids = {rid for rid, _, _ in res}
    failing = {}
    for rid, fail, why in res:
        if fail:
            failing[rid] = why
    for rid, why in failing.items():
        if not limits.get(rid):
            bad.append(f"{rid} fails the spec ({why}) and names no limit")
    for rid in ids - set(failing):
        if limits.get(rid):
            bad.append(f"{rid} meets the spec but still names limit(s) {','.join(limits[rid])}")
    for rid, ks in limits.items():
        for k in ks:
            if k not in keys:
                bad.append(f"{rid} names undeclared limit key `{k}`")
    for rid in limits:
        if rid not in ids:
            bad.append(f"limit row {rid} names no listing row")
    nfail = len(failing)
    unit = "row(s)" if not l3 else "record(s) (witness x encoding x config)"
    print(f"REACH: {len(rows)} listing {unit}, {nfail} witness(es) at a named limit")
    if not rows:
        bad.append("no listing row was read")
    for b in bad:
        print("FAIL:", b)
    if bad:
        return 1
    print(f"PASS: [{tag}-listing] {len(rows)} rows list as recorded; "
          f"{nfail} shortfalls each name a declared limit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
