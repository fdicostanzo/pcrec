#!/usr/bin/env python3
# docs/design/findall_iter/sem/nullable_census.py — lane iterdes, [FINDALL-NEXT].
#
# Joins semprobe.c's verdicts with pcrec's own `nullable` fact (--emit-facts,
# byte encoding, --features all) per distinct pattern, to price the retry gate:
# how many patterns a gate keyed on bare nullability would arm, against how many
# actually diverge (L != G) on their own corpus subjects. A non-nullable pattern
# that diverges would refute the gate's soundness (an empty match needs a
# nullable pattern), so the script asserts there are none.
#
# FIRST RUN FINDING (kept as the rule): bare nullability is NOT a sound gate.
# `ab\K` and `ab\Kc?` are non-nullable and diverge, because \K makes a
# match that CONSUMED bytes REPORT an empty span, and PCRE2's NOTEMPTY_ATSTART
# tests the reported span. The gate is therefore "can report an empty span":
# nullable OR \K-bearing. pcrec's `kinds` fact does not list \K, so the
# census reads it off the pattern text (an unescaped `\K`); the design asks
# for an E1 fact `reports_empty` instead (findall_iter.md §3.3).
#
# usage: python3 -I nullable_census.py PCREC_BIN SEMPROBE_OUT
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

PCREC, SEM = sys.argv[1], sys.argv[2]


def unesc(s):
    """The .rxt subject-escape vocabulary, decoded to BYTES (semprobe.c's rule)."""
    out, i = bytearray(), 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            c = s[i + 1]
            if c in "tnr\\":
                out += {"t": b"\t", "n": b"\n", "r": b"\r", "\\": b"\\"}[c]; i += 2; continue
            if c == "x" and i + 3 < len(s):
                out.append(int(s[i + 2:i + 4], 16)); i += 4; continue
        out += s[i].encode("utf-8", "surrogateescape"); i += 1
    return bytes(out)


verdict = {}
for line in open(SEM, encoding="utf-8", errors="surrogateescape"):
    c = line.rstrip("\n").split("\t")
    if len(c) < 4 or c[0] not in ("SAME", "DIFF"):
        continue
    p = c[3]
    verdict[p] = verdict.get(p, False) or c[0] == "DIFF"


def nullable(pesc):
    pat = unesc(pesc)
    try:
        r = subprocess.run([PCREC.encode(), b"--features", b"all", b"--emit-facts", b"--pattern", pat],
                           capture_output=True, timeout=30)
    except subprocess.TimeoutExpired:
        return pesc, None
    for ln in r.stdout.decode("utf-8", "replace").splitlines():
        f = ln.split("\t")
        if len(f) > 6 and f[0] == "byte" and f[1] == "nullable":
            return pesc, f[6] == "yes"
    return pesc, None


with ThreadPoolExecutor(8) as ex:
    res = dict(ex.map(nullable, sorted(verdict)))

def has_k(pesc):
    t = unesc(pesc)
    i = 0
    while i < len(t) - 1:
        if t[i] == 0x5C:
            if t[i + 1] == ord("K"):
                return True
            i += 2
            continue
        i += 1
    return False


tab = {}
for p, d in verdict.items():
    n = res.get(p)
    g = None if n is None else (n or has_k(p))
    tab[(n, has_k(p), d)] = tab.get((n, has_k(p), d), 0) + 1
print("patterns with a semprobe verdict:", len(verdict))
for k in sorted(tab, key=str):
    print(f"  nullable={k[0]!s:5} has_K={k[1]!s:5} diverges={k[2]!s:5} : {tab[k]}")
bad = [p for p, d in verdict.items() if d and res.get(p) is False and not has_k(p)]
print("gate (nullable or \\K) false yet diverging (must be 0):", len(bad))
for p in bad[:10]:
    print("   ", p)
sys.exit(1 if bad else 0)
