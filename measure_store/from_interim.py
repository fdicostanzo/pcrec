#!/usr/bin/env python3
"""measure_store/from_interim.py -- the ONE-TIME conversion of the kit's interim
grid1 set (memfn/data/sets/kit-interim-grid1.tsv, Q-REVAL-10) into the store's
first set, zen4-grid1@1 ([MEASURE-SET] M0; docs/design/measure_sets.md §1.8's
"Q-REVAL-10 migration").

It changes two header values and nothing else: `id` (kit-interim-grid1 ->
zen4-grid1) and `values_digest`, recomputed under docs/spec/measures.md §3's
code table (the interim file hashed each unit's and status's FIRST LETTER, as
its own generator says, until that table existed). Every row, card and value is
carried byte for byte. The output is then written through pcrec's own
canonical writer, which is what is committed (PROVENANCE.md has the command),
so the committed file is canonical by construction (R4) and the C loader
re-checks this digest on every load.

    python3 -I measure_store/from_interim.py IN.tsv > OUT.tsv
"""
import struct
import sys

UNIT = {"ratio": 1, "walkbytes": 2, "bytes": 3, "count": 4}
STATUS = {"measured": 1, "fitted": 2, "derived": 3, "null": 4}


def digest(rows):
    h = 0xcbf29ce484222325
    def feed(b):
        nonlocal h
        for c in b:
            h = ((h ^ c) * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    feed(b"pcrec-meas-1\0")
    for key, unit, status, value in sorted(rows, key=lambda r: r[0].encode()):
        feed(key.encode() + b"\0")
        feed(bytes([UNIT[unit], STATUS[status]]))
        feed(struct.pack("<q", -(1 << 63) if value == "" else int(value)))
    return "%016x" % h


def main(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    sect, cols, rows = None, None, []
    for ln in lines:
        if ln.startswith("#section "):
            sect, cols = ln[9:], None
        elif ln.startswith("#"):
            cols = ln[1:].split("\t")
        elif ln and sect == "rows":
            c = dict(zip(cols, ln.split("\t")))
            rows.append((c["key"], c["unit"], c["status"], c["value_e6"]))
    d = digest(rows)
    out, sect = [], None
    for ln in lines:
        if ln.startswith("#section "):
            sect = ln[9:]
        elif sect == "header" and ln.startswith("id\t"):
            ln = "id\tzen4-grid1"
        elif sect == "header" and ln.startswith("values_digest\t"):
            ln = "values_digest\t" + d
        out.append(ln)
    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1])
