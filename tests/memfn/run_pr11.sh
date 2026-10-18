#!/usr/bin/env bash
# tests/memfn/run_pr11.sh — [MEMFN] R17-b' B3a PR-11's CONTROL over its fixed
# witnesses (lane b3a; docs/design/memfn/r17b_prime.md rev 3 §3.1 row B3a,
# §4.6's HYB_PF row; memfn/docs/requests.md R-21 PR-11).
#
# THE CLAIM: every count-collapsed VM hybrid front still enforces the
# necessary set and run (the collapse keeps every rmin >= 1 copy), which is
# why presence on HYB_PF is OPTIONAL. Each witness of
# tests/memfn/pr11_witnesses.tsv is compiled with build/pcrec; its front (the
# artifact's static `<prefix>_prefilter`, called directly from a driver that
# includes the artifact) is run over the matching subject, which must give a
# candidate, and over that subject with each claimed byte, and every
# occurrence of the claimed run, deleted, which must give none
# (tests/memfn/pr11_front.py says why the evidence shares no source with the
# req walk). K35: every witness must be count-collapsed and must check at
# least one claim. The census over the corpus, bench and rwquest populations
# is docs/design/memfn/r17b_prime/b3a/pr11_census.py.
#
# Usage: bash tests/memfn/run_pr11.sh [TREE]   (needs TREE/build/pcrec)
set -u
export LC_ALL=C
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TREE="$(cd "${1:-$SCRIPT_DIR/../..}" && pwd)"
. "$TREE/tests/lib/cc_resolve.sh"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/pr11.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
python3 -I - "$TREE" "$WORK" "${CC:-gcc}" <<'PY'
import os, sys
tree, work, cc = sys.argv[1:4]
sys.path.insert(0, os.path.join(tree, "tests/memfn"))
import pr11_front as p
sys.path.insert(0, os.path.join(tree, "scripts"))

def unesc(s):
    out, i = bytearray(), 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            c = s[i + 1]
            if c == "x":
                out.append(int(s[i + 2:i + 4], 16)); i += 4; continue
            out += {"t": b"\t", "n": b"\n", "r": b"\r", "\\": b"\\"}[c]; i += 2; continue
        out += s[i].encode(); i += 1
    return bytes(out)

pcrec = os.path.join(tree, "build", "pcrec")
ok = bad = n = 0
for ln in open(os.path.join(tree, "tests/memfn/pr11_witnesses.tsv"), encoding="utf-8"):
    ln = ln.rstrip("\n")
    if not ln or ln.startswith("#"):
        continue
    flags, pat, subj = ln.split("\t")
    n += 1
    fl = [] if flags == "-" else flags.split()
    st, det = p.check(pcrec, fl, pat, [unesc(subj)], os.path.join(work, "w%d" % n), cc)
    if st == "ok":
        ok += 1
        print("PASS: [pr11] %s %s: the front enforces every claim (%d derived subjects rejected)"
              % (flags, pat, det["derived"]))
    else:
        bad += 1
        print("FAIL: [pr11] %s %s: %s %s" % (flags, pat, st, det))
if n >= 1:
    ok += 1; print("PASS: [pr11-population] %d witness lines" % n)
else:
    bad += 1; print("FAIL: [pr11-population] no witness line read (K35)")
print("checks passed: %d" % ok)
print("checks failed: %d" % bad)
sys.exit(1 if bad else 0)
PY
