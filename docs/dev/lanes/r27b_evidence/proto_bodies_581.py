#!/usr/bin/env python3
# docs/dev/lanes/r27b_evidence/proto_bodies_581.py — job 581 (lane r27b, MEASUREMENT ONLY): the
# hand-rendered REPORT-site text for the eight cells of the 650 harness. Extends job 580's
# proto_bodies.py (kept unchanged, in ../r27_evidence/): PRO and SHF are rendered by the SAME code
# (build.sh checks them byte-for-byte against 580's output when it is given the path); new arms:
#
#   PRO2  a byte-identical recompile of PRO (the A/A pair for the new text)
#   PRR   PRO with the RIGHTMOST tie for the stop (year4: @3, hex8-bounded: @7)
#   PRF   PRO's text as a FUNC-shaped `noinline` twin (lit-l8, foobar, file-ext-order): the
#         search is a separate function, as the default build's ofsskip FUNC is
#   HRS   Horspool over sets, on all 8 cells: test the window's LAST span-0 position first; a
#         byte not in S[K-1] shifts by sh[b] = the least t >= 1 (t <= K-1) with b in S[K-1-t],
#         else K; otherwise the rest of the span and the ctx items are tested as PRO does, and a
#         failed candidate resumes at c + sh[b] (the same table: positions c+u, u < sh[b], would
#         need b in S[K-1-u], and b is in none of them).
#
# usage: python3 -I proto_bodies_581.py BASE OUT
#   BASE  a measure.sh build directory (arts/<cell>/COV/a.c, a.h)
#   OUT   gets <cell>/<ARM>/a.c and a.h for every arm of the cell (ARMS_OF)
# The module is also loaded (importlib) by diff_581.py and pop_581.py for CELLS / set tables.
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


def members(expr):
    """The byte set a SET text denotes (the C text, evaluated per byte)."""
    py = expr.replace("&&", " and ").replace("||", " or ")
    return frozenset(b for b in range(256) if eval(py.replace("X", str(b))))


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

# The span-0 sets by offset, and the ctx items as (offset, set, absent-ok), for the population
# counts, the shift table and the predictor. A literal is one single-byte set per offset.
LITS = {"lit-l8": "abcdefgh", "foobar": "foobar", "file-ext-order": ".tar", "cat-bounded": "cat",
        "done-eol": "done"}
CTX = {"cat-bounded": [(-1, NWD), (3, NWD)], "done-eol": [(4, "(X == 10)")],
       "hex8-bounded": [(-1, NWD), (8, NWD)]}


def span_sets(cell):
    k, stop, tests = CELLS[cell]
    if cell in LITS:
        return [frozenset([ord(ch)]) for ch in LITS[cell]]
    sets = {}
    for t in tests:
        if t[0] == "set":
            sets[t[1]] = members(t[2])
    if stop[0] == "walk":
        sets[stop[1]] = members(stop[2])
    return [sets[j] for j in range(k)]


def ctx_items(cell):
    return [(off, members(e)) for off, e in CTX.get(cell, [])]


ARMS_OF = {}
for _c in CELLS:
    ARMS_OF[_c] = ["DEF", "COV", "AA", "PRO", "PRO2", "SHF", "HRS"]
    if _c in ("year4", "hex8-bounded"):
        ARMS_OF[_c].append("PRR")
    if _c in ("lit-l8", "foobar", "file-ext-order"):
        ARMS_OF[_c].append("PRF")


def shift(sets, j):
    # S[i] as frozensets of the SET text (all equal text = equal set, the only case used here)
    for t in range(1, j + 1):
        if sets.get(j - t) != sets.get(j):
            return t
    return j + 1


def stop_text(stop, k):
    if stop[0] == "chr":
        d, b = stop[1], stop[2]
        return ("{ const void *rx_mf1_q = %s + %d < %s ? memchr(%s + %s + %d, %d, %s - %s - %d) : 0; "
                "if (!rx_mf1_q) break; %s = (size_t)((const unsigned char *)rx_mf1_q - %s) - %d; } "
                % (C, d, N, S, C, d, b, N, C, d, C, S, d))
    d, st = stop[1], stop[2]
    return "while (%s + %d < %s && !%s) %s++; " % (C, d, N, setx(st, d), C)


def body(cell, shifted, stop=None, tests=None):
    """580's PRO / SHF text (stop/tests default to the cell's own; PRR passes the rightmost)."""
    k, dstop, dtests = CELLS[cell]
    stop = stop or dstop
    tests = tests if tests is not None else dtests
    sets = {}
    for t in tests:
        if t[0] == "set":
            sets[t[1]] = t[2]
    if stop[0] == "walk":
        sets[stop[1]] = stop[2]
    out = ["for (;;) { "]
    out.append(stop_text(stop, k))
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


def rightmost(cell):
    """PRR: the stop at the RIGHTMOST span-0 position (a walk), every other position tested."""
    k, stop, tests = CELLS[cell]
    assert stop[0] == "walk"
    st = ("walk", k - 1, stop[2])
    sets = {t[1]: t[2] for t in tests if t[0] == "set"}
    sets[stop[1]] = stop[2]
    nt = [("set", j, sets[j]) for j in range(k - 1)] + [t for t in tests if t[0] == "ctx"]
    return st, nt


def hrs_body(cell):
    """HRS: last span-0 position first, shift table sh[b], then the rest as PRO's chain."""
    k, _stop, tests = CELLS[cell]
    ss = span_sets(cell)
    sh = []
    for b in range(256):
        t = next((t for t in range(1, k) if b in ss[k - 1 - t]), k)
        sh.append(t)
    tbl = "static const unsigned char rx_mf1_sh[256] = {%s}; " % ",".join(map(str, sh))
    if cell in LITS:
        last = "%s == %d" % (at(k - 1), ord(LITS[cell][-1]))
        last = last.replace(at(k - 1), "rx_mf1_b")
    else:
        sets = {t[1]: t[2] for t in tests if t[0] == "set"}
        sets[CELLS[cell][1][1]] = CELLS[cell][1][2]
        last = setx(sets[k - 1], k - 1).replace(at(k - 1), "rx_mf1_b")
    conds = []
    if cell in LITS:
        if k > 1:
            conds.append("!memcmp(%s + %s, \"%s\", %d)" % (S, C, LITS[cell][:-1], k - 1))
    else:
        sets = {t[1]: t[2] for t in tests if t[0] == "set"}
        sets[CELLS[cell][1][1]] = CELLS[cell][1][2]
        for j in range(k - 1):
            conds.append(setx(sets[j], j))
    conds += [t[1] for t in tests if t[0] == "ctx"]
    out = [tbl, "for (;;) { unsigned char rx_mf1_b; if (%s + %d > %s) break; rx_mf1_b = %s[%s + %d]; "
           % (C, k, N, S, C, k - 1)]
    out.append("if (!(%s)) { %s += rx_mf1_sh[rx_mf1_b]; continue; } " % (last, C))
    if conds:
        out.append("if (%s) { %s = 1; break; } " % (" && ".join(conds), F))
    else:
        out.append("{ %s = 1; break; } " % F)
    out.append("%s += rx_mf1_sh[rx_mf1_b]; }" % C)
    return "".join(out)


OLD = "for (; rx_mf1_c < rx_mf1_n; rx_mf1_c++) if ("
END = ") { rx_mf1_f = 1; break; }"
EXPR0 = "scan_position = ({ "
EXPR1 = "rx_mf1_f ? rx_mf1_c : (subject_length); });"


def render(src, cell, arm):
    i = src.index(OLD)
    j = src.index(END, i)
    if arm in ("PRO", "PRO2"):
        b = body(cell, False)
    elif arm == "SHF":
        b = body(cell, True)
    elif arm == "HRS":
        b = hrs_body(cell)
    elif arm == "PRR":
        st, nt = rightmost(cell)
        b = body(cell, False, st, nt)
    elif arm == "PRF":
        # the whole statement expression becomes a call to a noinline function holding PRO's loop
        a = src.index(EXPR0)
        z = src.index(EXPR1, a) + len(EXPR1)
        decl = src[a + len(EXPR0):src.index(OLD, a)]    # the kit's operand declarations
        fn = ("static __attribute__((noinline)) size_t rx_mf1_find(const unsigned char *subject, "
              "size_t subject_length, size_t scan_position)\n{\n"
              "    return ({ %s%s rx_mf1_f ? rx_mf1_c : (subject_length); });\n}\n\n"
              % (decl, body(cell, False)))
        call = "scan_position = rx_mf1_find(subject, subject_length, scan_position);"
        k = src.index("#ifndef __has_attribute")
        return src[:k] + fn + src[k:a] + call + src[z:]
    else:
        raise SystemExit("unknown arm " + arm)
    return src[:i] + b + src[j + len(END):]


def main():
    if sys.argv[1] == "--arms":
        print(" ".join(ARMS_OF[sys.argv[2]]))
        return
    base, outd = sys.argv[1], sys.argv[2]
    for cell in CELLS:
        src = open(os.path.join(base, "arts", cell, "COV", "a.c")).read()
        hdr = open(os.path.join(base, "arts", cell, "COV", "a.h")).read()
        for arm in ARMS_OF[cell]:
            if arm in ("DEF", "COV", "AA"):
                continue
            d = os.path.join(outd, cell, arm)
            os.makedirs(d, exist_ok=True)
            open(os.path.join(d, "a.c"), "w").write(render(src, cell, arm))
            open(os.path.join(d, "a.h"), "w").write(hdr)


if __name__ == "__main__":
    main()
