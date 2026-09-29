#!/usr/bin/env python3
"""ctx_sets.py SHAPES.tsv -- the context-set census behind ucp_design.md s2
and H7: over the lookaround census's ALL-(a) patterns (every lookaround
occurrence a single one-character atom, docs/dev/lookaround_census.md), how
many DISTINCT context sets does each pattern read (its lookaround bodies,
plus \\w if it spells \\b/\\B), and under -e utf8 is every one of them
ASCII-only (the condition for the all-byte form to be exact, s3.2)?  Text
extraction, not a compile: the body is the single atom following the
lookaround opener, read up to its closing paren with brackets respected."""
import sys, re, collections
OPEN = re.compile(r"\(\?(?:<?[=!*])|\(\*(?:positive_lookahead|negative_lookahead|positive_lookbehind|negative_lookbehind|pla|nla|plb|nlb|napla|naplb|non_atomic_positive_lookahead|non_atomic_positive_lookbehind):")
def body_at(p, i):
    j, depth, incls = i, 0, False
    while j < len(p):
        c = p[j]
        if c == "\\": j += 2; continue
        if incls:
            if c == "]": incls = False
            j += 1; continue
        if c == "[":
            incls = True; j += 1
            if j < len(p) and p[j] == "^": j += 1
            if j < len(p) and p[j] == "]": j += 1
            continue
        if c == "(": depth += 1
        if c == ")":
            if depth == 0: return p[i:j]
            depth -= 1
        j += 1
    return p[i:]
# [r1 GEN-2] the bare two-digit \xHH (HH >= 80) spelling is non-ASCII too;
# the first version caught only \x{...} (harmless on its run: the one bare
# \xHH body is byte-encoded, where the classification short-circuits).
NONASCII_ESC = re.compile(r"\\[pPhHvVDWSNX]|\\x\{0*[89a-fA-F]..|\\x\{0*[1-9a-fA-F]...|\\x[89a-fA-F][0-9a-fA-F]")
# [r1 SEM-2] under UCP the LOWERCASE shorthands are non-ASCII sets as well;
# this census ran on a pre-UCP corpus (no pattern spells (*UCP)), so the
# UCP arm is a guard for re-use, not a correction of the reported numbers.
UCP_ESC = re.compile(r"\\[dws]|\[:")
def ascii_only(b, ucp=False):
    if b == "." or b.startswith("[^") or NONASCII_ESC.search(b): return False
    if ucp and UCP_ESC.search(b): return False
    if any(ord(ch) > 0x7F for ch in b): return False
    return True
rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[1])][1:]
kdist = collections.Counter(); enc_ok = collections.Counter(); n = 0
for r in rows:
    if r[6] != "True": continue
    n += 1; enc, pat = r[2], r[11]
    sets = set(body_at(pat, m.end()) for m in OPEN.finditer(pat))
    if re.search(r"(?<!\\)\\[bB]", pat.replace("\\\\", "")): sets.add("\\w")
    kdist[len(sets)] += 1
    ucp = pat.startswith("(*UCP)") or "(*UCP)" in pat[:12]
    allascii = all(ascii_only(b, ucp) for b in sets)
    enc_ok[(enc, "all-byte exact" if enc == "byte" or allascii else "needs the island")] += 1
print("#all-(a) patterns:", n)
print("#distinct context sets per pattern (k):", dict(sorted(kdist.items())))
for k, v in sorted(enc_ok.items()): print("#%s %-18s %d" % (k[0], k[1], v))
