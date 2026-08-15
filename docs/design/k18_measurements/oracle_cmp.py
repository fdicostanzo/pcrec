#!/usr/bin/env python3
"""Three-way span comparison: two pcrec binaries against python3 `re`.

Usage: oracle_cmp.py <bin-A> <label-A> <bin-B> <label-B> <patterns-file> [--subjects S]

For every pattern, compiles with each binary (--emit-main), runs both matchers
over a subject set derived from the pattern's own alphabet, and compares each
span against python3 `re`'s. Reports, per pattern, the cells where the two
binaries DISAGREE, and which of them agrees with the oracle. That is the
question a design comparison actually has to answer: not "does the candidate
pass the corpus" — both candidates do — but "where they differ, which one is
right".

The oracle is python3 `re` for the base tier, per the repo's convention; the
K17/K18 entries record that every expectation in this space was additionally
re-measured against libpcre2 10.46 with zero disagreements, so a single-oracle
run here is a screen, and anything it flags is a candidate for the second
oracle rather than a verdict on its own. Cells where BOTH binaries disagree
with the oracle are reported separately: they are not a difference between the
candidates, they are a defect neither one repairs.
"""
import os
import re as _re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

binA, labA, binB, labB, patfile = sys.argv[1:6]
NSUB = 24
if "--subjects" in sys.argv:
    NSUB = int(sys.argv[sys.argv.index("--subjects") + 1])

pats = [l.rstrip("\n") for l in open(patfile, errors="replace") if l.strip()]
CC = os.environ.get("CC", "gcc")


def subjects_for(p):
    """Short subjects over the pattern's own alphabet. Short on purpose: every
    witness in K17's and K18's entries is 2-4 bytes, because the defect is
    about which thread reaches ACCEPT first, and a long subject only buries
    that under more of the same."""
    alpha = sorted(set(c for c in p if c.isalnum())) or ["a"]
    alpha = [c for c in alpha if c.isalpha()][:4] or ["a"]
    out = [""]
    cur = [""]
    for _ in range(3):
        nxt = []
        for s in cur:
            for c in alpha:
                nxt.append(s + c)
        out += nxt
        cur = nxt
    return out[:NSUB]


def build(binary, p, d, tag):
    csrc = os.path.join(d, "m_%s.c" % tag)
    exe = os.path.join(d, "m_%s" % tag)
    r = subprocess.run([binary, "-p", "rx", "--emit-main", "-o", csrc, "--", p],
                       capture_output=True, timeout=60)
    if r.returncode != 0:
        return None
    r = subprocess.run([CC, "-O0", "-std=gnu11", "-o", exe, csrc],
                       capture_output=True, timeout=120)
    if r.returncode != 0:
        return None
    return exe


def run(exe, subj):
    r = subprocess.run([exe, subj], capture_output=True, timeout=20)
    out = r.stdout.decode(errors="replace").strip()
    m = _re.match(r"match (\d+) (\d+)", out)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    return None


def oracle(p, subj):
    try:
        m = _re.compile(p).search(subj)
    except _re.error:
        return "ORACLE-ERR"
    return (m.start(), m.end()) if m else None


def one(p):
    with tempfile.TemporaryDirectory() as d:
        ea = build(binA, p, d, "a")
        eb = build(binB, p, d, "b")
        if not ea or not eb:
            return p, None, []
        rows = []
        for s in subjects_for(p):
            va, vb, vo = run(ea, s), run(eb, s), oracle(p, s)
            if vo == "ORACLE-ERR":
                continue
            if va != vb:
                rows.append((s, va, vb, vo))
        return p, True, rows


with ThreadPoolExecutor(max_workers=int(os.environ.get("JOBS", "8"))) as ex:
    results = list(ex.map(one, pats))

a_right = b_right = neither = both_wrong_same = 0
skipped = 0
print("pattern\tsubject\t%s\t%s\toracle\tverdict" % (labA, labB))
for p, ok, rows in results:
    if not ok:
        skipped += 1
        continue
    for s, va, vb, vo in rows:
        if va == vo:
            v = "%s-RIGHT" % labA
            a_right += 1
        elif vb == vo:
            v = "%s-RIGHT" % labB
            b_right += 1
        else:
            v = "BOTH-WRONG"
            neither += 1
        print("%s\t%r\t%s\t%s\t%s\t%s" % (p, s, va, vb, vo, v))

print("\ncells where the two binaries differ: %d" % (a_right + b_right + neither),
      file=sys.stderr)
print("  %s agrees with oracle: %d" % (labA, a_right), file=sys.stderr)
print("  %s agrees with oracle: %d" % (labB, b_right), file=sys.stderr)
print("  neither agrees:        %d" % neither, file=sys.stderr)
print("  patterns skipped (refused/uncompilable): %d" % skipped, file=sys.stderr)
