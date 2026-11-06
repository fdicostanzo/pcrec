"""tests/memfn/row_map.py — THE ONE PARSER of tests/memfn/row_map.tsv, read by
rows_check.py (section M) and reach_equal.py (--map). Two readers of one
declaration under two column contracts hid a malformed line from one of them
(span_pick 1e review, F3): the contract is HERE.

    read_map(path) -> [(from_table, from_row, to_table, to_row, unit)]

All five columns, every line, `-` `-` for a dissolved row; a line of any other
width, an empty cell or a duplicate (from_table, from_row) raises MapError.
"""
import os


class MapError(Exception):
    pass


def read_map(path):
    out, seen = [], set()
    name = os.path.basename(path)
    with open(path, encoding="utf-8") as f:
        for i, ln in enumerate(f, 1):
            ln = ln.rstrip("\n")
            if not ln.strip() or ln.startswith("#"):
                continue
            c = ln.split("\t")
            if len(c) != 5 or not all(c):
                raise MapError("%s:%d: a map line has exactly 5 non-empty tab-separated columns "
                               "(from_table from_row to_table to_row unit): %r" % (name, i, ln))
            if (c[2] == "-") != (c[3] == "-"):
                raise MapError("%s:%d: to_table and to_row are both `-` (dissolved) or neither: %r"
                               % (name, i, ln))
            if (c[0], c[1]) in seen:
                raise MapError("%s:%d: %s/%s is mapped twice" % (name, i, c[0], c[1]))
            seen.add((c[0], c[1]))
            out.append(tuple(c))
    return out
