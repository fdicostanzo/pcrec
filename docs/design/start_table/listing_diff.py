#!/usr/bin/env python3
"""docs/design/start_table/listing_diff.py -- [START-TABLE] C7's listing
instrument (start_table.md §3.2 C7: a DECLARED stream-5-only commit).

Compares two `pcrec --list-axes` outputs, the PARENT's (REF) and the commit's
(NEW), cell by cell, against a declared-movers manifest
(`listing_declared_C7.tsv`): every cell the manifest declares must change
from its stated old value to its stated new value, and NOTHING else may
differ -- no other cell, no row added, removed or reordered, no header or
comment line, no column. A row is keyed by (axis, order, candidate).

THE MANIFEST: `axis  candidate  column  old  new`, TAB-separated, `#`
comments. `candidate` `*` means every row the REF listing has under `axis`;
each such axis must expand to at least one row (K35: a declaration over an
empty population declares nothing). The expansion reads the REF side only,
so the set of declared cells comes from the parent and the manifest, never
from the listing under test.

Exit 0 when the diff is exactly the declaration, 1 otherwise, 2 on a usage
or input error. Prints the declared count, the observed count, and every
undeclared or missing change.
Usage: listing_diff.py REF_TSV NEW_TSV MANIFEST_TSV
"""
import sys

COLS = ("axis", "order", "candidate", "kind", "stamp_macro", "stamp_value",
        "deny_macro", "deny_bit", "force_macro", "force_bit", "cli_flag",
        "applies")


def die(msg):
    print(f"listing_diff: {msg}", file=sys.stderr)
    sys.exit(2)


def load(path):
    """(comment/header lines, ordered [(key, {col: value})]) of the main
    table; the kit's `#section` tail, if any, is kept as raw lines."""
    head, rows, tail = [], [], []
    in_tail = False
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("#section"):
                in_tail = True
            if in_tail:
                tail.append(line)
                continue
            if line.startswith("#") or not line:
                head.append(line)
                continue
            parts = line.split("\t")
            if len(parts) != len(COLS):
                die(f"{path}: row with {len(parts)} cells, want {len(COLS)}: {line[:80]!r}")
            cells = dict(zip(COLS, parts))
            rows.append(((cells["axis"], cells["order"], cells["candidate"]), cells))
    if not rows:
        die(f"{path}: no rows (an empty listing passes any diff)")
    return head, rows, tail


def main():
    if len(sys.argv) != 4:
        die("usage: listing_diff.py REF_TSV NEW_TSV MANIFEST_TSV")
    rh, rr, rt = load(sys.argv[1])
    nh, nr, nt = load(sys.argv[2])
    want = {}           # (key, col) -> (old, new)
    with open(sys.argv[3], encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            p = line.split("\t")
            if len(p) != 5 or p[2] not in COLS:
                die(f"{sys.argv[3]}:{n}: want axis, candidate, column, old, new")
            axis, cand, col, old, new = p
            keys = [k for k, _ in rr if k[0] == axis and (cand == "*" or k[2] == cand)]
            if not keys:
                die(f"{sys.argv[3]}:{n}: declares {axis}/{cand}, which the REF listing does not have")
            for k in keys:
                want[(k, col)] = (old, new)
    bad = []
    if rh != nh:
        bad.append("the header/comment lines differ")
    if rt != nt:
        bad.append("the #section tail differs")
    if [k for k, _ in rr] != [k for k, _ in nr]:
        bad.append(f"the row keys differ (ref {len(rr)}, new {len(nr)} rows, or reordered)")
    ref, new = dict(rr), dict(nr)
    seen = 0
    for k, cells in rr:
        if k not in new:
            continue
        for col in COLS:
            a, b = cells[col], new[k][col]
            d = want.get((k, col))
            if d is None:
                if a != b:
                    bad.append(f"UNDECLARED {'/'.join(k)} {col}: {a[:60]!r} -> {b[:60]!r}")
            else:
                if (a, b) != d:
                    bad.append(f"DECLARED NOT AS STATED {'/'.join(k)} {col}: "
                               f"{a[:60]!r} -> {b[:60]!r}, declared {d[0][:40]!r} -> {d[1][:40]!r}")
                else:
                    seen += 1
    print(f"rows {len(rr)}/{len(nr)}; declared cells {len(want)}; changed as declared {seen}")
    for b in bad:
        print("  " + b)
    print("listing diff: " + ("EXACTLY AS DECLARED" if not bad and seen == len(want) else "FAIL"))
    sys.exit(0 if not bad and seen == len(want) else 1)


if __name__ == "__main__":
    main()
