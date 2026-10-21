#!/usr/bin/env python3
"""CK-8 ([DD-11.5], docs/design/ctx_span.md §6): THE CONTEXT TRUTH TABLE
AGAINST LIBPCRE2.

    Usage: ctxfn_table_check.py [path/to/src/core/ctxfn.def]

Every row of src/core/ctxfn.def is a 9-cell grid: the answer for each
(previous character, next character) pair, each `out` (not in the row's set),
`in`, or `absent` (no character). This check derives each row's nine cells
from LIBPCRE2 and compares them with the grid the file states. The
expectation never comes from the bits: a row is identified by NAME, and the
name maps to a canonical PCRE2 spelling and a set below, written here. The
grid is read as TEXT from the .def (the subject), never through the compiler.

THE FAMILY. Every subject over {a, -, \\n} of length 0..4 (121 subjects,
the 547 (subject, position) cells of ctx_span.md's equivalence runs with the
end positions), each position asked with `\\G(?:SPELLING)` at that start
offset, so a lookbehind sees the real previous byte. A cell is the
(previous, next) class of the position; every row must see ALL NINE cells
(the empty subject is (absent, absent); a position after a final newline is
(in, absent) for the newline rows) and see each one consistently, or the
check fails (K35: a family that missed a cell would certify nothing).

ROWS WITH A NATIVE SPELLING are asked again per spelling: `\\b`/`\\B`/
`(?m)^`/`(?m)$`/`\\A`/`^`/`\\z` must give the same nine cells as the
lookaround spelling, so the table is
tied to the construct the parser builds it for (CK-9's half on the libpcre2
side; pcrec's own answers are the corpus's).

FAILING DIRECTION: flip one cell of one row in the .def (SP-8,
`MLINE_EOL`'s out/absent cell) and this reports the row and the cell.
SKIPS LOUDLY (exit 0, a SKIP line) when libpcre2 cannot be loaded.
"""
import itertools
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "d27"))
try:
    import lib_pcre2 as P
except OSError as e:
    print("SKIP ctxfn_table_check: libpcre2 not loadable (%s)" % e)
    sys.exit(0)

WORD = set(b"a")          # \w over the family's alphabet {a, -, \n}
A = set(b"a")
NL = set(b"\n")

# name -> (set, canonical lookaround spelling, native spellings)
# The SUBJECT rows read no set; theirs is any set, so the family still reaches
# every (in, *) and (*, in) cell and the grid's in row/column is checked too.
ROWS = {
    "BOUNDARY":    (WORD, rb"(?<=\w)(?!\w)|(?<!\w)(?=\w)", (rb"\b",)),
    "NONBOUNDARY": (WORD, rb"(?<=\w)(?=\w)|(?<!\w)(?!\w)", (rb"\B",)),
    "PREV":        (A,    rb"(?<=a)", ()),
    "NOT_PREV":    (A,    rb"(?<!a)", ()),
    "NEXT":        (A,    rb"(?=a)", ()),
    "NOT_NEXT":    (A,    rb"(?!a)", ()),
    "MLINE_BOL":   (NL,   rb"\A|(?<=\n)(?=[\s\S])", (rb"(?m)^",)),
    "MLINE_EOL":   (NL,   rb"(?![^\n])", (rb"(?m)$",)),
    "SUBJECT_START": (NL, rb"(?<![\s\S])", (rb"\A", rb"^")),
    "SUBJECT_END":   (NL, rb"(?![\s\S])", (rb"\z",)),
}

ROW_RE = re.compile(r"^CTXFN_ROW\(\s*(\w+)\s*,\s*(0x[0-9A-Fa-f]+)\s*,"
                    r"\s*([01])\s*,\s*([01])\s*,\s*([01])\s*,"
                    r"\s*([01])\s*,\s*([01])\s*,\s*([01])\s*,"
                    r"\s*([01])\s*,\s*([01])\s*,\s*([01])\s*,", re.M)


def read_def(path):
    rows = {}
    for m in ROW_RE.finditer(open(path).read()):
        rows[m.group(1)] = [int(m.group(k)) for k in range(3, 12)]
    return rows


def cls(c, s):
    return 2 if c is None else (1 if c in s else 0)


def observe(spelling, cset):
    """{cell: answer} from libpcre2 over the family, or a conflict string."""
    seen = {}
    pat = rb"\G(?:" + spelling + rb")"
    for n in range(5):
        for t in itertools.product(b"a-\n", repeat=n):
            subj = bytes(t)
            for pos in range(n + 1):
                p = cls(subj[pos - 1] if pos > 0 else None, cset)
                q = cls(subj[pos] if pos < n else None, cset)
                r = P.match(pat, subj, pos)
                ans = 1 if r else 0
                cell = 3 * p + q
                if cell in seen and seen[cell] != ans:
                    return "cell (%d,%d) answers both ways (subject %r at %d)" % (
                        p, q, subj, pos)
                seen[cell] = ans
    return seen


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "src", "core", "ctxfn.def")
    table = read_def(path)
    fails = 0
    names = ("out", "in", "absent")
    if set(table) != set(ROWS):
        print("FAIL: ctxfn.def rows %s, this check knows %s -- a row needs its "
              "canonical spelling here" % (sorted(table), sorted(ROWS)))
        return 1
    for name, grid in table.items():
        cset, canon, native = ROWS[name]
        for label, sp in [("canonical", canon)] + [("native", n) for n in native]:
            seen = observe(sp, cset)
            if isinstance(seen, str):
                print("FAIL %s (%s %r): %s" % (name, label, sp, seen)); fails += 1
                continue
            if len(seen) != 9:
                print("FAIL %s (%s): the family reached %d of 9 cells (K35)" % (
                    name, label, len(seen))); fails += 1
                continue
            for cell in range(9):
                if seen[cell] != grid[cell]:
                    print("FAIL %s (%s %r): cell (p=%s, q=%s) is %d in libpcre2, "
                          "%d in ctxfn.def" % (name, label, sp, names[cell // 3],
                                               names[cell % 3], seen[cell], grid[cell]))
                    fails += 1
    print("ctxfn_table_check: %d rows x 9 cells against libpcre2 %s: %d failures" % (
        len(table), "(canonical + native spellings)", fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
