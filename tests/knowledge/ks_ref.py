#!/usr/bin/env python3
"""tests/knowledge/ks_ref.py -- the INDEPENDENT reader of the measures kind
([MEASURE-SET] M0; docs/design/measure_sets.md rev 3 §9.6, R3 and R5).

Written from docs/spec/measures.md alone (the section shape §2, the header
keys §2.1 and the formats §2.1¶1a, the tables §2.2 with format 2's `events`
§2.2¶1a and noise §2.2¶3a, the code table §3.1, the digests §3.3¶1 and
§3.3¶1a, the hand rule §4¶2a, the decoded view §6¶3 and §6¶3a), in another
language, sharing no code with src/core/ks_measures.c,
src/core/ksrc.c or scripts/ksgen.c. pcrec's own reader is checked AGAINST
this one, so this file must never be "fixed" by reading the C.

    ks_ref.py decode FILE   the decoded view of FILE, the shape
                            `pcrec --list-measurements=FILE --view=decoded`
                            prints (R5)
    ks_ref.py doc FILE      the document as a canonical python repr, one line
                            per field (R3: two files load to one document iff
                            these agree)
    ks_ref.py digest FILE   the values digest of FILE's rows, 16 hex
    ks_ref.py handed FILE   what a compile under FILE hands the kit (§4¶2a),
                            as the trace build's MFMEAS record spells it
                            (docs/design/memfn/span_cards.md §4.2): the count
                            of measured rows, TAB, FNV-1a-64 (16 hex) over
                            the lines `key TAB state TAB value_e6 TAB noise_e6 LF` of the
                            handed rows in canonical key order, state
                            `measured` or `unmeasured`, an unmeasured noise 0

It reads; it does not validate beyond what a decode needs. Python 3 stdlib.
"""
import struct
import sys

HEADER = ["format", "id", "rev", "class", "isa", "tier", "composite", "members",
          "unit_key", "method", "run", "box", "compiler", "libc", "code_commit",
          "counters", "partial", "rows", "values_digest"]
CARD = ["owner", "quantity", "ver", "dims", "unit", "subject", "lengths",
        "launches", "rounds", "aa_rule", "gate_e6", "env", "deps"]
ROW = ["key", "unit", "value_e6", "abs_ns_e6", "noise_e6", "n", "status",
       "derivation", "inputs", "deps", "tags", "source"]
CELL = ["cell", "group", "arm", "length", "launch", "round", "ns_e6"]
CELL2 = ["cell", "group", "arm", "length", "launch", "round", "events", "ns_e6"]
MEMBER = ["member", "unit_key", "unit_abs_ns_e6", "box"]
UNIT = {"ratio": 1, "walkbytes": 2, "bytes": 3, "count": 4}
STATUS = {"measured": 1, "fitted": 2, "derived": 3, "null": 4}


def sections(raw):
    """{name: (columns, [row dict])} by the contract: `#section NAME` opens a
    section, its header is the last `#` line before its first data row."""
    out, name, hdr, rows, started = {}, "", None, [], False

    def close():
        if name:
            out[name] = (hdr or [], rows)
    for line in raw.split(b"\n"):
        if not line:
            continue
        if line.startswith(b"#section "):
            close()
            name, hdr, rows, started = line[9:].decode(), None, [], False
            continue
        if line.startswith(b"#"):
            if not started:
                hdr = [c.decode() for c in line[1:].split(b"\t")]
            continue
        started = True
        cells = line.split(b"\t")
        rows.append(dict(zip(hdr, cells)))
    close()
    return out


def load(path):
    s = sections(open(path, "rb").read())
    head = {}
    for r in s.get("header", ([], []))[1]:
        head[r["key"].decode()] = r["value"]

    def tab(name, cols):
        rows = s.get(name, ([], []))[1]
        return sorted(tuple(r.get(c, b"") for c in cols)
                      for r in rows)
    rows = sorted((tuple(r[c] for c in ROW) for r in s.get("rows", ([], []))[1]),
                  key=lambda t: t[0])
    fmt = head.get("format", b"1").decode()
    return {
        "format": fmt,
        "header": [head.get(k, b"") for k in HEADER],
        "cards": tab("cards", CARD),
        "rows": rows,
        "cells": tab("cells", CELL2 if fmt == "2" else CELL),
        "members": tab("members", MEMBER),
    }


def int64(v):
    """A value or noise column as the digest packs it: INT64_MIN when empty
    or `-`."""
    return -(1 << 63) if v in (b"", b"-") else int(v)


def digest(doc):
    h = 0xcbf29ce484222325

    def feed(b):
        nonlocal h
        for c in b:
            h = ((h ^ c) * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    two = doc["format"] == "2"
    if two:
        feed(b"pcrec-meas-2\0")
        feed(doc["header"][HEADER.index("class")] + b"\0")
    else:
        feed(b"pcrec-meas-1\0")
    for r in doc["rows"]:
        v = r[2]
        feed(r[0] + b"\0")
        feed(bytes([UNIT[r[1].decode()], STATUS[r[6].decode()]]))
        feed(struct.pack("<q", -(1 << 63) if v == b"" else int(v)))
        if two:
            feed(struct.pack("<q", int64(r[4])))
    return "%016x" % h


def handed(doc):
    """(count of measured rows, the noise digest) of the rows §4¶2a hands."""
    h = 0xcbf29ce484222325
    n = 0
    for r in doc["rows"]:
        if not r[0].startswith(b"kit.") or r[2] == b"":
            continue
        measured = doc["format"] == "2" and r[4] != b"-"
        n += measured
        line = r[0] + b"\t" + (b"measured" if measured else b"unmeasured") + \
            b"\t" + str(int(r[2])).encode() + \
            b"\t" + (str(int(r[4])).encode() if measured else b"0") + b"\n"
        for c in line:
            h = ((h ^ c) * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return n, "%016x" % h


def decode(doc):
    w = sys.stdout.buffer.write
    w(b"# pcrec measurement set, decoded (spec: docs/spec/measures.md)\n")
    w(b"#section decoded\n#scope\tfield\tvalue\n")
    for k, v in zip(HEADER, doc["header"]):
        w(b"header\t" + k.encode() + b"\t" + v + b"\n")
    for r in doc["rows"]:
        scope = b"row:" + r[0]
        for c, v in zip(ROW[1:], r[1:]):
            if c == "value_e6" and v != b"":
                v = str(int(v)).encode()
            w(scope + b"\t" + c.encode() + b"\t" + v + b"\n")
        w(scope + b"\tunit_code\t" + str(UNIT[r[1].decode()]).encode() + b"\n")
        w(scope + b"\tstatus_code\t" + str(STATUS[r[6].decode()]).encode() + b"\n")
        if doc["format"] == "2":
            n = b"" if r[4] == b"-" else str(int(r[4])).encode()
            w(scope + b"\tnoise_parsed\t" + n + b"\n")
    cell = CELL2 if doc["format"] == "2" else CELL
    for what, cols in (("card", CARD), ("cell", cell), ("member", MEMBER)):
        for i, t in enumerate(doc[what + "s"]):
            for c, v in zip(cols, t):
                w(b"%s:%d\t%s\t" % (what.encode(), i, c.encode()) + v + b"\n")
    w(b"#section item\n#rows\tvalues_digest\n")
    w(b"%d\t%s\n" % (len(doc["rows"]), digest(doc).encode()))


def main(argv):
    if len(argv) != 3 or argv[1] not in ("decode", "doc", "digest", "handed"):
        sys.stderr.write(__doc__)
        return 2
    doc = load(argv[2])
    if argv[1] == "decode":
        decode(doc)
    elif argv[1] == "digest":
        print(digest(doc))
    elif argv[1] == "handed":
        print("%d\t%s" % handed(doc))
    else:
        for part in ("header", "cards", "rows", "cells", "members"):
            for t in doc[part]:
                print(part, repr(t))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
