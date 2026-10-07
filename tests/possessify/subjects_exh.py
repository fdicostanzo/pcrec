#!/usr/bin/env python3
"""tests/possessify/subjects_exh.py -- the EXHAUSTIVE subject generator
run_possdiff.sh uses for the arms_*.txt populations ([ART-POSS-ARMS] 8.1;
prototype: docs/design/poss_arms_measurements/rev21/subjects_exh.py).

Every string of length <= ML (default 4) over a CASE-FLIP-CLOSED alphabet:
the pattern's own literal characters (escapes decoded; group names, flag
letters, back-reference and call spellings and quantifier counts EXCLUDED --
they are syntax, not subject text), every letter's case flip, plus one WORD
and one NON-WORD representative (the space, and `a` when the pattern has no
word literal), `7` when it mentions a digit class, and under `-e utf8` the
code points U+00E9 and U+212A.  Under `-e utf8` the strings are built over
CODE POINTS and then encoded, so a two-byte character is never split.

Output: one subject per line in possdiff_driver.c's escape form (every byte
outside printable ASCII, and `\\`, as \\xHH).

  subjects_exh.py PATTERN [FLAGS...]            print the sweep
  subjects_exh.py --alpha PATTERN [FLAGS...]    print the alphabet (repr)
  subjects_exh.py --reach S PATTERN [FLAGS...]  exit 0 iff S (escape form)
                                                is in the sweep  (REACH)
Env: ML (max length)."""
import sys, re, itertools, os

SKIP_GROUP = re.compile(r"""\(\?(?:\#[^)]*\)|<[A-Za-z_]\w*>|P<\w+>|'\w+'|&\w+\)|P>\w+\)|P=\w+\)|R\)|[+-]?\d+\)
    |\(DEFINE\)|\([^)]*\)|<=|<!|[:=!>|]|[A-Za-z^-]*\)|[A-Za-z^-]*:)""", re.X)
SKIP_ESC = re.compile(r"""\\(?:k<\w+>|k\{\w+\}|k'\w+'|g<[^>]+>|g'[^']+'|g\{[^}]+\}|g[+-]?\d+|[1-9]\d*|[pP]\{[^}]*\}|[pP]\w)""")

def literals(p):
    out, i, cls = set(), 0, False
    shorthand = set()
    while i < len(p):
        c = p[i]
        if c == "\\":
            m = SKIP_ESC.match(p, i)
            if m: i = m.end(); continue
            n = p[i + 1] if i + 1 < len(p) else ""
            if n == "x":
                m = re.match(r"\\x\{([0-9a-fA-F]+)\}|\\x([0-9a-fA-F]{1,2})", p[i:])
                out.add(chr(int(m.group(1) or m.group(2), 16))); i += m.end(); continue
            if n in "wWdDsShHvVNRbBAzZGK": shorthand.add(n); i += 2; continue
            out.add({"n": "\n", "t": "\t", "r": "\r", "f": "\f", "e": "\x1b", "a": "\x07"}.get(n, n)); i += 2; continue
        if cls:
            if c == "]": cls = False; i += 1; continue
            m = re.match(r"\[:\^?(\w+):\]", p[i:])
            if m: shorthand.add({"digit": "d", "space": "s"}.get(m.group(1), "w")); i += m.end(); continue
            if c == "-" and i + 1 < len(p) and p[i + 1] != "]" and out:
                i += 1; continue           # a range: both ends are kept as literals
            out.add(c); i += 1; continue
        if c == "[":
            cls = True; i += 1
            if i < len(p) and p[i] == "^": i += 1
            if i < len(p) and p[i] == "]": out.add("]"); i += 1
            continue
        if c == "(" and p[i:i + 2] == "(?":
            m = SKIP_GROUP.match(p, i)
            if m: i = m.end(); continue
        if c == "{":
            m = re.match(r"\{\d*,?\d*\}", p[i:])
            if m: i += m.end(); continue
        if c in "^$.|?*+()": i += 1; continue
        out.add(c); i += 1
    return out, shorthand

def alphabet(p, flags):
    lit, sh = literals(p)
    a = set(lit)
    for c in list(a):
        if c.isalpha(): a.add(c.swapcase())
    a.add(" ")
    if not any(c.isalnum() or c == "_" for c in a): a.add("a")
    if "w" in sh and sum(c.isalnum() or c == "_" for c in a) < 2:
        a.add("b" if "a" in a else "a")
    if "d" in sh or "D" in sh: a.add("7")
    utf = "utf8" in flags
    if utf: a.update(["\u00e9", "\u212a"])
    else: a = {c for c in a if ord(c) < 256}
    return sorted(a), utf

def esc(b):
    return "".join(chr(x) if 0x20 <= x < 0x7f and x != 0x5c else "\\x%02x" % x for x in b)

def sweep(p, flags):
    al, utf = alphabet(p, flags)
    ml = int(os.environ.get("ML", "4"))
    for L in range(ml + 1):
        for t in itertools.product(al, repeat=L):
            s = "".join(t)
            yield esc(s.encode("utf8") if utf else s.encode("latin-1"))

def main():
    a = sys.argv[1:]
    if a[0] == "--alpha":
        print(repr(alphabet(a[1], " ".join(a[2:]))[0])); return
    if a[0] == "--reach":
        s, p, fl = a[1], a[2], " ".join(a[3:])
        sys.exit(0 if any(x == s for x in sweep(p, fl)) else 1)
    for x in sweep(a[0], " ".join(a[1:])): print(x)
main()
