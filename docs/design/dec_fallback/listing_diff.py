#!/usr/bin/env python3
"""docs/design/dec_fallback/listing_diff.py -- [DEC-FALLBACK] B7's listing
instrument (dec_fallback.md §4.2: B7 is a DECLARED stream-5-only commit), the
C7 instrument (docs/design/start_table/listing_diff.py) extended for what B7
does and C7 did not: rows that MOVE (the engine-route order swap) and rows that
are ADDED (the `fallback` and `prefilter-admit` axes).

Compares two `pcrec --list-axes` outputs, the PARENT's (REF) and the commit's
(NEW), against a declared manifest (`listing_declared_B7.tsv`). A row is keyed
by (axis, candidate); `order` is an ordinary column, so a swap is two declared
`order` cells. Everything not declared must be identical: no other cell, no row
removed, no header/comment line, no column, and no row added that is not
declared. Within every axis the NEW listing must also be in ascending dense
`order` (1..n) in file order (the listing's own contract).

MANIFEST lines (TAB-separated, `#` comments):
  axis  candidate  column  old  new     a changed cell; candidate `*` = every
                                        row the REF listing has under axis
                                        (an empty population is an error)
  +  axis  order  candidate  kind  stamp_macro  stamp_value  deny_macro
     deny_bit  force_macro  force_bit  cli_flag  applies_prefix
                                        an ADDED row. Every cell but the last
                                        must equal exactly; `applies` must
                                        START WITH applies_prefix (it is text
                                        generated from the table row's cells,
                                        so the prefix pins the part that names
                                        the row's action)
The set of declared cells is read from the manifest and the REF listing only,
never from the listing under test. Exit 0 when the diff is exactly the
declaration, 1 otherwise, 2 on usage or input errors.
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
            rows.append(((cells["axis"], cells["candidate"]), cells))
    if not rows:
        die(f"{path}: no rows (an empty listing passes any diff)")
    keys = [k for k, _ in rows]
    if len(set(keys)) != len(keys):
        die(f"{path}: a (axis, candidate) key occurs twice")
    return head, rows, tail


def main():
    if len(sys.argv) != 4:
        die("usage: listing_diff.py REF_TSV NEW_TSV MANIFEST_TSV")
    rh, rr, rt = load(sys.argv[1])
    nh, nr, nt = load(sys.argv[2])
    want = {}      # (key, col) -> (old, new)
    added = {}     # key -> (cells without applies, applies_prefix)
    with open(sys.argv[3], encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            p = line.split("\t")
            if p[0] == "+":
                if len(p) != 1 + len(COLS):
                    die(f"{sys.argv[3]}:{n}: an added row wants {len(COLS)} cells after `+`")
                cells = dict(zip(COLS, p[1:]))
                k = (cells["axis"], cells["candidate"])
                if any(k == r for r, _ in rr) or k in added:
                    die(f"{sys.argv[3]}:{n}: added row {k} already exists in REF or is declared twice")
                added[k] = cells
                continue
            if len(p) != 5 or p[2] not in COLS:
                die(f"{sys.argv[3]}:{n}: want axis, candidate, column, old, new")
            axis, cand, col, old, new = p
            keys = [k for k, _ in rr if k[0] == axis and (cand == "*" or k[1] == cand)]
            if not keys:
                die(f"{sys.argv[3]}:{n}: declares {axis}/{cand}, which the REF listing does not have")
            for k in keys:
                if (k, col) in want:
                    die(f"{sys.argv[3]}:{n}: {k} {col} declared twice")
                want[(k, col)] = (old, new)
    bad = []
    if rh != nh:
        bad.append("the header/comment lines differ")
    if rt != nt:
        bad.append("the #section tail differs")
    ref, new = dict(rr), dict(nr)
    for k in ref:
        if k not in new:
            bad.append(f"REMOVED row {'/'.join(k)}")
    for k in new:
        if k not in ref and k not in added:
            bad.append(f"UNDECLARED ADDED row {'/'.join(k)}")
    for k in added:
        if k not in new:
            bad.append(f"DECLARED ADDED row {'/'.join(k)} is absent")
    # the REF rows keep their relative file order (a move is a cell, not a reshuffle of axes)
    ref_axes = [a for a in dict.fromkeys(k[0] for k, _ in rr)]
    new_axes = [a for a in dict.fromkeys(k[0] for k, _ in nr) if a in ref_axes]
    if ref_axes != new_axes:
        bad.append("the REF axes' relative order changed")
    # per axis: ascending dense order in file order
    by_axis = {}
    for k, c in nr:
        by_axis.setdefault(k[0], []).append(c["order"])
    for a, os_ in by_axis.items():
        if os_ != [str(i) for i in range(1, len(os_) + 1)]:
            bad.append(f"axis {a}: order column is not 1..{len(os_)} in file order: {os_}")
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
            elif (a, b) != d:
                bad.append(f"DECLARED NOT AS STATED {'/'.join(k)} {col}: "
                           f"{a[:60]!r} -> {b[:60]!r}, declared {d[0][:40]!r} -> {d[1][:40]!r}")
            else:
                seen += 1
    addok = 0
    for k, decl in added.items():
        if k not in new:
            continue
        got = new[k]
        ok = True
        for col in COLS[:-1]:
            if got[col] != decl[col]:
                bad.append(f"ADDED {'/'.join(k)} {col}: got {got[col]!r}, declared {decl[col]!r}")
                ok = False
        if not got["applies"].startswith(decl["applies"]) or not decl["applies"]:
            bad.append(f"ADDED {'/'.join(k)} applies {got['applies'][:60]!r} does not start with {decl['applies']!r}")
            ok = False
        addok += ok
    print(f"rows {len(rr)}/{len(nr)}; declared cells {len(want)}, changed as declared {seen}; "
          f"declared added rows {len(added)}, as declared {addok}")
    for b in bad:
        print("  " + b)
    good = not bad and seen == len(want) and addok == len(added)
    print("listing diff: " + ("EXACTLY AS DECLARED" if good else "FAIL"))
    sys.exit(0 if good else 1)


if __name__ == "__main__":
    main()
