#!/usr/bin/env python3
"""R23-semantics INDEPENDENT oracle check.

Deliberately NOT derived from oracle_cmp.py's generator: subjects here are the
full cross product over an alphabet I choose per run (not "alphanumeric chars
appearing in the pattern, alphabetic only, truncated to 4, truncated to 24
subjects"), lengths 0..N, and the report is against the ORACLE first rather
than against a second binary.  Usage:

    ocheck.py <patterns-file> <bin1> <lab1> [<bin2> <lab2> ...] [--alpha abc]
              [--len 3] [--jobs 8]
"""
import os
import re as _re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from itertools import product

args = sys.argv[1:]


def opt(name, default):
    if name in args:
        i = args.index(name)
        v = args[i + 1]
        del args[i:i + 2]
        return v
    return default


ALPHA = opt("--alpha", "ab")
MAXLEN = int(opt("--len", "3"))
JOBS = int(opt("--jobs", "8"))
patfile = args[0]
bins = []
for i in range(1, len(args), 2):
    bins.append((args[i], args[i + 1]))

pats = [l.rstrip("\n") for l in open(patfile, errors="replace")
        if l.strip() and not l.startswith("#")]
CC = os.environ.get("CC", "gcc")

SUBJ = [""]
for n in range(1, MAXLEN + 1):
    SUBJ += ["".join(t) for t in product(ALPHA, repeat=n)]


BUILD_TIMEOUT = float(os.environ.get("BUILD_TIMEOUT", "120"))
TIMEOUTS = []


def build(binary, p, d, tag):
    csrc = os.path.join(d, "m_%s.c" % tag)
    exe = os.path.join(d, "m_%s" % tag)
    try:
        r = subprocess.run([binary, "-p", "rx", "--emit-main", "-o", csrc, "--", p],
                           capture_output=True, timeout=BUILD_TIMEOUT)
    except subprocess.TimeoutExpired:
        TIMEOUTS.append((binary, p))
        return None, "PCREC-TIMEOUT"
    if r.returncode != 0:
        return None, r.stderr.decode(errors="replace").strip()[:120]
    try:
        r = subprocess.run([CC, "-O0", "-std=gnu11", "-o", exe, csrc],
                           capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        return None, "CC-TIMEOUT"
    if r.returncode != 0:
        return None, "CC-FAIL"
    return exe, None


def run(exe, subj):
    try:
        r = subprocess.run([exe, subj], capture_output=True, timeout=20)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    out = r.stdout.decode(errors="replace").strip()
    m = _re.match(r"match (\d+) (\d+)", out)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    if out == "nomatch":
        return None
    if r.returncode != 0:
        return "RC%d" % r.returncode
    return None


def oracle(p, subj):
    try:
        m = _re.compile(p).search(subj)
    except _re.error:
        return "ORACLE-ERR"
    return (m.start(), m.end()) if m else None


def one(p):
    with tempfile.TemporaryDirectory() as d:
        exes = []
        for i, (b, lab) in enumerate(bins):
            e, err = build(b, p, d, str(i))
            exes.append(e)
        if any(e is None for e in exes):
            return p, "SKIP", []
        rows = []
        for s in SUBJ:
            vo = oracle(p, s)
            if vo == "ORACLE-ERR":
                return p, "ORACLE-ERR", []
            vs = [run(e, s) for e in exes]
            if any(v != vo for v in vs):
                rows.append((s, vs, vo))
        return p, "OK", rows


with ThreadPoolExecutor(max_workers=JOBS) as ex:
    results = list(ex.map(one, pats))

labs = [l for _, l in bins]
print("pattern\tsubject\t" + "\t".join(labs) + "\toracle")
nbad = {l: 0 for l in labs}
npat_bad = {l: set() for l in labs}
nskip = 0
for p, st, rows in results:
    if st != "OK":
        nskip += 1
        continue
    for s, vs, vo in rows:
        print("%s\t%r\t%s\t%s" % (p, s, "\t".join(str(v) for v in vs), vo))
        for lab, v in zip(labs, vs):
            if v != vo:
                nbad[lab] += 1
                npat_bad[lab].add(p)
for b, p in TIMEOUTS:
    print("PCREC-TIMEOUT\t%s\t%s" % (b, p))
print("\n== summary: %d patterns, %d skipped, %d subjects each" %
      (len(pats), nskip, len(SUBJ)))
for lab in labs:
    print("   %-8s disagrees with oracle on %d cells / %d patterns"
          % (lab, nbad[lab], len(npat_bad[lab])))
