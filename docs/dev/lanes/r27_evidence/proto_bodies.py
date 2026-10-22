#!/usr/bin/env python3
# docs/dev/lanes/r27_evidence/proto_bodies.py — lane r27 (DESIGN ONLY, no build go): the
# hand-rendered text of the PROPOSED REPORT form (a stop search, then the rest tested) for the
# eight cells of the 650 harness, written into copies of the harness build's COV artifacts.
#
# usage: python3 -I proto_bodies.py BASE OUT
#   BASE  a measure.sh build directory (arts/<cell>/COV/a.c, a.h)
#   OUT   gets <cell>/PRO/a.c and <cell>/SHF/a.c (+ a.h)
#
# PRO  the stop: the span-0 position whose set has the least mass under pcrec's default byte-rate
#      (tests/findings/default_ppm.tsv; a tie to the LEFTMOST: lane r27's calibration read the
#      rightmost 1.4x slower than DEF on year4), searched by memchr where it is one
#      byte (finder row D1's form) and by the walk otherwise (Frank 2026-10-21: the walk when the
#      subject is unknown); one bound test `c + k > n` ends the search; then every REQUIRED term
#      and context item is tested at c as one `&&` chain (consecutive one-byte positions as one
#      memcmp), a failed candidate resuming at c + 1.
# SHF  PRO with each test its own branch and the failure shift: a failed test at offset j resumes at c + t, t the least t >= 1
#      such that S[j - t] is not a subset of S[j] (j + 1 if none): positions in between would need
#      the failed byte in a subset of the set it is not in.
# The cover site's loop `for (; c < n; c++) if (CONJ) { f = 1; break; }` is replaced; the
# statement expression around it (its operands, its miss) is the kit's text unchanged.
import os
import sys

DIG = "(X >= 48 && X <= 57)"
HEX = "((X >= 48 && X <= 57) || (X >= 97 && X <= 102))"
WRD = "((X >= 48 && X <= 57) || (X >= 65 && X <= 90) || X == 95 || (X >= 97 && X <= 122))"
NWD = "(X <= 47 || (X >= 58 && X <= 64) || (X >= 91 && X <= 94) || X == 96 || X >= 123)"
S, N, C, F = "rx_mf1_s", "rx_mf1_n", "rx_mf1_c", "rx_mf1_f"


def at(k):
    return "%s[%s + %d]" % (S, C, k) if k > 0 else "%s[%s - %d]" % (S, C, -k) if k < 0 else "%s[%s]" % (S, C)


def setx(expr, k):
    return expr.replace("X", at(k))


# cell: (k, stop, tests). stop = ("chr", d, byte) | ("walk", d, SET). tests: ("run", off, lit)
# | ("set", off, SET) | ("ctx", text) where text is the item under its absent rule.
CELLS = {
    "lit-l8": (8, ("chr", 1, 98), [("run", 0, "abcdefgh")]),
    "foobar": (6, ("chr", 3, 98), [("run", 0, "foobar")]),
    "file-ext-order": (4, ("chr", 0, 46), [("run", 0, ".tar")]),
    "cat-bounded": (3, ("chr", 0, 99), [("run", 0, "cat"),
                                        ("ctx", "(%s < 1 || %s)" % (C, setx(NWD, -1))),
                                        ("ctx", "(%s + 4 > %s || %s)" % (C, N, setx(NWD, 3)))]),
    "done-eol": (4, ("chr", 0, 100), [("run", 0, "done"),
                                      ("ctx", "(%s + 5 > %s || %s == 10)" % (C, N, at(4)))]),
    "year4": (4, ("walk", 0, DIG), [("set", 1, DIG), ("set", 2, DIG), ("set", 3, DIG)]),
    "word-digit": (2, ("walk", 1, DIG), [("set", 0, WRD)]),
    "hex8-bounded": (8, ("walk", 0, HEX), [("set", j, HEX) for j in range(1, 8)] +
                     [("ctx", "(%s < 1 || %s)" % (C, setx(NWD, -1))),
                      ("ctx", "(%s + 9 > %s || %s)" % (C, N, setx(NWD, 8)))]),
}


def shift(sets, j):
    # S[i] as frozensets of the SET text (all equal text = equal set, the only case used here)
    for t in range(1, j + 1):
        if sets.get(j - t) != sets.get(j):
            return t
    return j + 1


def body(cell, shifted):
    k, stop, tests = CELLS[cell]
    sets = {}
    for t in tests:
        if t[0] == "set":
            sets[t[1]] = t[2]
    if stop[0] == "walk":
        sets[stop[1]] = stop[2]
    out = ["for (;;) { "]
    if stop[0] == "chr":
        d, b = stop[1], stop[2]
        out.append("{ const void *rx_mf1_q = %s + %d < %s ? memchr(%s + %s + %d, %d, %s - %s - %d) : 0; "
                   "if (!rx_mf1_q) break; %s = (size_t)((const unsigned char *)rx_mf1_q - %s) - %d; } "
                   % (C, d, N, S, C, d, b, N, C, d, C, S, d))
    else:
        d, st = stop[1], stop[2]
        out.append("while (%s + %d < %s && !%s) %s++; " % (C, d, N, setx(st, d), C))
    out.append("if (%s + %d > %s) break; " % (C, k, N))
    if not shifted:     # PRO: one `&&` chain, a failed candidate resuming at c + 1
        conds = []
        for t in tests:
            if t[0] == "run":
                conds.append("!memcmp(%s + %s%s, \"%s\", %d)" % (S, C, " + %d" % t[1] if t[1] else "", t[2], len(t[2])))
            elif t[0] == "set":
                conds.append(setx(t[2], t[1]))
            else:
                conds.append(t[1])
        out.append("if (%s) { %s = 1; break; } %s++; }" % (" && ".join(conds), F, C))
        return "".join(out)
    for t in tests:
        if t[0] == "run":
            cond = "!memcmp(%s + %s%s, \"%s\", %d)" % (S, C, " + %d" % t[1] if t[1] else "", t[2], len(t[2]))
            sh = 1
        elif t[0] == "set":
            cond = setx(t[2], t[1])
            sh = shift(sets, t[1]) if shifted else 1
        else:
            cond = t[1]
            sh = 1
        out.append("if (!(%s)) { %s += %d; continue; } " % (cond, C, sh))
    out.append("%s = 1; break; }" % F)
    return "".join(out)


def main():
    base, outd = sys.argv[1], sys.argv[2]
    old = "for (; rx_mf1_c < rx_mf1_n; rx_mf1_c++) if ("
    end = ") { rx_mf1_f = 1; break; }"
    for cell in CELLS:
        src = open(os.path.join(base, "arts", cell, "COV", "a.c")).read()
        i = src.index(old)
        j = src.index(end, i)
        for arm, shifted in (("PRO", False), ("SHF", True)):
            d = os.path.join(outd, cell, arm)
            os.makedirs(d, exist_ok=True)
            open(os.path.join(d, "a.c"), "w").write(src[:i] + body(cell, shifted) + src[j + len(end):])
            open(os.path.join(d, "a.h"), "w").write(open(os.path.join(base, "arts", cell, "COV", "a.h")).read())


main()
