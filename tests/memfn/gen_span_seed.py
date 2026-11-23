#!/usr/bin/env python3
"""tests/memfn/gen_span_seed.py -- writes tests/memfn/span_seed.rxt, SPAN-SEED.

WHAT IT IS. docs/design/memfn/block_span.md §10.1 (R-47, D201; review r69
R-20, ruled): the committed corpus file that puts the vector span's
witnesses into the corpus, so every check that reads the corpus (the answer
tests, the axes arms, the identity gates, C18, the sweep's floors) sees
them. Committed at unit U1, where it moves no artifact byte; later units
read the committed file. The real corpus holds no such site (§0.1).

ITS PATTERNS: 41 distinct, three blocks (the list is §10.1's):
  1. the 3 bench patterns (§0.1);
  2. the 11 T-table pin patterns (§10.2);
  3. a slice of job 710's grid: each of its ten classes at {17}, {25}, {32};
     a pattern already written in an earlier block is written once, there.

ITS CASES, per pattern, every expectation computed HERE by python `re`
(bytes patterns, re.ASCII; the file's oracle, rxt_format.md §3, re-checked
by tests/harness/verify_rxt.py): a match at the subject start; a match
flush against the subject end after a non-member prefix; the failing-index
staircase (each position replaced by a byte outside it) on every pattern of
at most 33 positions, and at the rung edges 0 15 16 31 32 63 64 999 and the
last position on a longer one; one byte short; the empty subject; an `mc`
find-all count over two back-to-back matches and a near-miss (`re.finditer`
counts it: every pattern here is non-empty, rxt_format.md §1.7); for
`\\b[0-9a-f]{32}\\b` a word byte before and after.

The `[\\x80-\\xbf]` blocks state `encoding byte` (the corpus's byte-only
convention, as tests/utf8/*.rxt write it). The generated file is the record:
a change is a re-run of this script, never a hand edit.

Usage: python3 -I -B tests/memfn/gen_span_seed.py [OUT]   (default: the
committed path beside this script)
"""
import os
import re
import sys

# A position: (regex atom, member bytes). The members are written HERE, from
# the class's definition, never read off pcrec or the kit.
HEX = (r"[0-9a-f]", b"0123456789abcdef")
DIG = (r"[0-9]", b"0123456789")
WORD = (r"\w", b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz")
GZ = (r"[g-z]", b"ghijklmnopqrstuvwxyz")
XY = (r"[xy]", b"xy")
LIT_A = ("a", b"a")
LIT_B = ("b", b"b")

# job 710's ten classes (confirm.py CLASSES), in its order
GRID = [
    ("hex", HEX),
    ("dig", DIG),
    ("word", WORD),
    ("vowel", (r"[aeiou]", b"aeiou")),
    ("nonl", (r"[^\n]", bytes(i for i in range(256) if i != 10))),
    ("hi", (r"[\x80-\xbf]", bytes(range(0x80, 0xC0)))),
    ("af", (r"[a-f]", b"abcdef")),
    ("ident", (r"[A-Za-z0-9_-]", b"-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz")),
    ("upper", (r"[A-Z]", b"ABCDEFGHIJKLMNOPQRSTUVWXYZ")),
    ("num", (r"[+.0-9]", b"+.0123456789")),
]

STAIR_MAX = 33                                   # §10.1: the default-width V sites
RUNG_EDGES = (0, 15, 16, 31, 32, 63, 64, 999)    # §10.1: a longer pattern's staircase
OUTSIDE = b"g!\na-~"                             # the preferred non-member bytes, in order


class Pat:
    """One pattern: its text, its positions (one (atom, members) each, in
    order) and, for \\b-anchored text, the boundary flag."""

    def __init__(self, text, positions, bounded=False):
        self.text = text
        self.pos = positions
        self.bounded = bounded


def rep(cls, n):
    return Pat(cls[0] + "{%d}" % n, [cls] * n)


def cat(*parts):
    """A concatenation of (cls, n) parts (a literal's n is 1)."""
    text, pos = "", []
    for cls, n in parts:
        text += cls[0] if n == 1 else cls[0] + "{%d}" % n
        pos += [cls] * n
    return Pat(text, pos)


def blocks():
    bench = [
        rep(HEX, 32),
        Pat(r"\b[0-9a-f]{32}\b", [HEX] * 32, bounded=True),
        Pat(r"\d{32}", [DIG] * 32),
    ]
    pins = [
        rep(HEX, 16), rep(HEX, 17), rep(HEX, 1001), rep(HEX, 1002),
        rep(DIG, 24), rep(DIG, 25), rep(DIG, 65), rep(DIG, 66),
        cat((LIT_A, 1), (LIT_B, 1), (DIG, 26)),
        cat((XY, 1), (DIG, 26)),
        cat((HEX, 20), (GZ, 20)),
    ]
    grid = [rep(cls, n) for _, cls in GRID for n in (17, 25, 32)]
    seen, out = set(), []
    for title, pats in (("the 3 bench patterns (block_span.md §0.1)", bench),
                        ("the T-table pin patterns (block_span.md §10.2)", pins),
                        ("a slice of job 710's grid: ten classes at {17}, {25}, {32}", grid)):
        kept = [p for p in pats if p.text not in seen]
        seen.update(p.text for p in kept)
        out.append((title, kept))
    return out


def member(cls, i):
    """The i-th member byte of a position's class, cycling, so a subject
    exercises many members rather than one."""
    m = cls[1]
    return m[(i * 7 + 3) % len(m)]


def outside(cls):
    for b in OUTSIDE:
        if b not in cls[1]:
            return b
    return next(b for b in range(256) if b not in cls[1])


def full(p, shift=0):
    return bytes(member(c, i + shift) for i, c in enumerate(p.pos))


def esc(s):
    """rxt_format.md §1.5.1: printable ASCII as itself, `"` and `\\`
    escaped, every other byte \\xHH."""
    o = []
    for b in s:
        if b in (0x22, 0x5C):
            o.append("\\" + chr(b))
        elif 0x20 <= b <= 0x7E:
            o.append(chr(b))
        else:
            o.append("\\x%02x" % b)
    return '"' + "".join(o) + '"'


def subjects(p):
    """The block's subjects, in order, each once."""
    n = len(p.pos)
    first_out = outside(p.pos[0])
    subs = [full(p), bytes([first_out]) + full(p, 1)]
    stair = range(n) if n <= STAIR_MAX else sorted({i for i in RUNG_EDGES if i < n} | {n - 1})
    for i in stair:
        s = bytearray(full(p))
        s[i] = outside(p.pos[i])
        subs.append(bytes(s))
    subs.append(full(p)[:-1])
    subs.append(b"")
    if p.bounded:
        subs.append(b"g" + full(p))
        subs.append(full(p) + b"g")
    out, seen = [], set()
    for s in subs:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def findall_subject(p):
    near = bytearray(full(p, 2))
    near[-1] = outside(p.pos[-1])
    sep = b"!" if p.bounded else b""     # a bounded match abuts into one word without it
    return full(p) + sep + full(p, 1) + sep + bytes(near)


def render(path):
    lines = [
        "# SPAN-SEED (docs/design/memfn/block_span.md §10.1, R-47 / D201): the vector",
        "# span's corpus witnesses. GENERATED by tests/memfn/gen_span_seed.py: re-run it,",
        "# never hand-edit. Every expectation is python `re`'s (bytes, re.ASCII).",
    ]
    npat = ncase = 0
    for title, pats in blocks():
        lines += ["", "# ---- " + title]
        for p in pats:
            rx = re.compile(p.text.encode("ascii"), re.ASCII)
            if len(rx.pattern) and rx.search(b"") is not None:
                raise SystemExit("gen_span_seed: %s matches the empty subject" % p.text)
            lines += ["", "pattern " + p.text]
            if p.bounded:
                lines.append("features assertions")   # \b is module `assertions`'s
            if any(c[0] == r"[\x80-\xbf]" for c in p.pos):
                lines.append("encoding byte")
            npat += 1
            for s in subjects(p):
                mt = rx.search(s)
                lines.append("m %s %d %d" % (esc(s), mt.start(), mt.end()) if mt else "n " + esc(s))
                ncase += 1
            fs = findall_subject(p)
            lines.append("mc %s %d" % (esc(fs), sum(1 for _ in rx.finditer(fs))))
            ncase += 1
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return npat, ncase


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "span_seed.rxt")
    npat, ncase = render(out)
    if npat != 41:
        raise SystemExit("gen_span_seed: %d patterns, block_span.md §10.1 states 41" % npat)
    print("gen_span_seed: %d patterns, %d cases -> %s" % (npat, ncase, out))


if __name__ == "__main__":
    main()
