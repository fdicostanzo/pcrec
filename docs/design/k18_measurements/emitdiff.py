#!/usr/bin/env python3
"""Emitted-source blast radius between two pcrec binaries.

Usage: emitdiff.py <binary-A> <binary-B> <patterns-file> [--list-diff FILE]

For every pattern both binaries accept, compile to stdout with each and compare
the bytes. Reports identical / differing counts and writes the differing
patterns out. This is the net docs/dev/known_issues.md K17 argues for over
subject sampling: it cannot miss a difference that the sampled subjects happen
not to reach.

Refusals are reported per binary and per direction, because a change that makes
the compiler REFUSE a pattern it used to accept is a blast-radius event too.
"""
import os
import subprocess
import sys

a, b, patfile = sys.argv[1], sys.argv[2], sys.argv[3]
listfile = None
if "--list-diff" in sys.argv:
    listfile = sys.argv[sys.argv.index("--list-diff") + 1]

pats = [l.rstrip("\n") for l in open(patfile, errors="replace") if l.strip()]
env = dict(os.environ)
env.pop("PCREC_K18_STATS", None)


def emit(binary, p):
    try:
        r = subprocess.run([binary, "-o", "-", "--", p], capture_output=True,
                           env=env, timeout=60)
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT"
    if r.returncode != 0:
        return None, "REFUSED"
    return r.stdout, None


def classify(p):
    sa, ea = emit(a, p)
    sb, eb = emit(b, p)
    if ea and eb:
        return "both_refused"
    if ea and not eb:
        return "only_b"
    if eb and not ea:
        return "only_a"
    return "same" if sa == sb else "diff"


from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=int(os.environ.get("JOBS", "8"))) as ex:
    verdicts = list(ex.map(classify, pats))

same = 0
diff = []
only_a = []
only_b = []
both_refused = 0
for p, v in zip(pats, verdicts):
    if v == "same":
        same += 1
    elif v == "diff":
        diff.append(p)
    elif v == "only_a":
        only_a.append(p)
    elif v == "only_b":
        only_b.append(p)
    else:
        both_refused += 1

print("patterns=%d  identical=%d  differing=%d  both_refused=%d  "
      "accepted_only_by_A=%d  accepted_only_by_B=%d"
      % (len(pats), same, len(diff), both_refused, len(only_a), len(only_b)))
for p in diff[:40]:
    print("  DIFF  %s" % p)
if len(diff) > 40:
    print("  ... %d more" % (len(diff) - 40))
for p in only_a[:10]:
    print("  A-ONLY %s" % p)
for p in only_b[:10]:
    print("  B-ONLY %s" % p)

if listfile:
    with open(listfile, "w") as fh:
        fh.write("\n".join(diff) + ("\n" if diff else ""))
