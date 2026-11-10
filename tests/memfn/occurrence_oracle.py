#!/usr/bin/env python3
"""Occurrence oracle for the run part (K38-2).

Written from span_runs_sheet.md section 3.3 items 1-5 and integration.md
section 14.7 alone.  Reads TSV records (docs/dev/lanes/k382a_oracle_iface.md)
from a file argument or stdin; prints one `VIOLATION <item> <site> <call>
<detail>` line per violation and the trailer `oracle: rows=R violations=V`.
Exit 0 iff V is 0, 1 on violations, 2 on a malformed row (refused, not skipped).

All arithmetic is Python's unbounded integers, so a wrapping implementation
cannot hide behind the oracle's own arithmetic.
"""
import re
import sys

HEADER = "#site\tcall\tsubject\torigin\tomin\tsets\tver_lo\tver_len\tresult\treads"
NCOLS = 10
_HEX = re.compile(r"^[0-9a-f]*$")
_INT = re.compile(r"^-?[0-9]+$")


class Malformed(Exception):
    pass


def _int(s, what, nonneg=False):
    if not _INT.match(s):
        raise Malformed("%s: not a decimal integer: %r" % (what, s))
    v = int(s)
    if nonneg and v < 0:
        raise Malformed("%s: must be >= 0: %r" % (what, s))
    return v


def parse_row(line):
    f = line.split("\t")
    if len(f) != NCOLS:
        raise Malformed("expected %d columns, got %d" % (NCOLS, len(f)))
    site, call, subj_hex, origin, omin, sets_s, ver_lo, ver_len, result, reads = f
    if "\t" in site or site == "":
        raise Malformed("site: empty")
    if call not in ("entry", "reentry"):
        raise Malformed("call: must be entry or reentry: %r" % call)
    if len(subj_hex) % 2 or not _HEX.match(subj_hex):
        raise Malformed("subject: not lowercase two-digit hex")
    subject = bytes.fromhex(subj_hex)
    origin = _int(origin, "origin", nonneg=True)
    omin = _int(omin, "omin")
    if sets_s == "":
        raise Malformed("sets: a run has at least one position")
    sets = []
    for h in sets_s.split(","):
        if len(h) != 64 or not _HEX.match(h):
            raise Malformed("sets: each set is 64 lowercase hex digits: %r" % h)
        v = int(h, 16)  # bitmap as one big-endian 256-bit number
        sets.append(frozenset(b for b in range(256) if (v >> b) & 1))
    ver_lo = _int(ver_lo, "ver_lo", nonneg=True)
    ver_len = _int(ver_len, "ver_len", nonneg=True)
    if ver_lo + ver_len > len(sets):
        raise Malformed("ver_lo + ver_len exceeds the number of sets")
    if result == "MISS":
        cand = None
    else:
        cand = _int(result, "result")
    rd = []
    if reads != "":
        for t in reads.split(","):
            rd.append(_int(t, "reads"))
    return dict(site=site, call=call, subject=subject, origin=origin, omin=omin,
                sets=sets, ver_lo=ver_lo, ver_len=ver_len, cand=cand, reads=rd)


def _is_occurrence(subject, sets, o):
    """Whole run at o: every position in its set, every position inside the subject."""
    n = len(subject)
    if o < 0 or o + len(sets) > n:
        return False
    return all(subject[o + j] in sets[j] for j in range(len(sets)))


def check_row(r):
    """Return a list of (item, detail) violations for one parsed row."""
    out = []
    subject, sets = r["subject"], r["sets"]
    n = len(subject)
    floor = max(0, r["origin"] + r["omin"])  # unbounded: no wrap
    c = r["cand"]

    if c is not None:
        # Item 1: candidate floor.
        if c < floor:
            out.append((1, "candidate %d below floor %d" % (c, floor)))
        # Stricter reading (QUESTION Q2): the candidate is the subject offset of
        # position 0, so it must name a subject byte.
        if c >= n:
            out.append((1, "candidate %d not a subject offset (n=%d)" % (c, n)))
        # Item 2: least. No whole-run occurrence in [floor, c).
        for o in range(floor, min(c, n)):
            if _is_occurrence(subject, sets, o):
                out.append((2, "occurrence at %d in [floor %d, candidate %d)" % (o, floor, c)))
                break
        # Item 3: held where verified.
        for j in range(r["ver_lo"], r["ver_lo"] + r["ver_len"]):
            p = c + j
            if p < 0 or p >= n:
                out.append((3, "verified position %d at offset %d outside [0,%d)" % (j, p, n)))
                break
            if subject[p] not in sets[j]:
                out.append((3, "verified position %d at offset %d: byte %02x not in set" % (j, p, subject[p])))
                break
    else:
        # Item 2, miss form: no occurrence at or after floor.
        for o in range(floor, n):
            if _is_occurrence(subject, sets, o):
                out.append((2, "MISS but occurrence at %d >= floor %d" % (o, floor)))
                break

    # Item 4 (and 5): every read in [0, n), on hits and misses alike.
    for k in r["reads"]:
        if k < 0 or k >= n:
            out.append((4, "read %d outside [0,%d)" % (k, n)))
            break
    return out


def run(lines, out=sys.stdout):
    """Check an iterable of lines.  Returns (rows, violations); raises Malformed."""
    it = iter(lines)
    try:
        first = next(it)
    except StopIteration:
        raise Malformed("empty input: header line missing")
    if first.rstrip("\n") != HEADER:
        raise Malformed("line 1: header line missing or not the interface header")
    rows = viol = 0
    for ln, line in enumerate(it, start=2):
        line = line.rstrip("\n")
        try:
            r = parse_row(line)
        except Malformed as e:
            raise Malformed("line %d: %s" % (ln, e))
        rows += 1
        for item, detail in check_row(r):
            viol += 1
            print("VIOLATION %d %s %s %s" % (item, r["site"], r["call"], detail), file=out)
    print("oracle: rows=%d violations=%d" % (rows, viol), file=out)
    return rows, viol


def main(argv):
    try:
        if len(argv) > 1:
            with open(argv[1], "r", newline="") as fh:
                rows, viol = run(fh)
        else:
            rows, viol = run(sys.stdin)
    except Malformed as e:
        print("oracle: malformed input: %s" % e, file=sys.stderr)
        return 2
    return 0 if viol == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
