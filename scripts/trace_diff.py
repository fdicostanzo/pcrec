#!/usr/bin/env python3
"""scripts/trace_diff.py -- [START-TABLE] C0's selection-trace DIFF
(docs/design/start_table.md §3.2 C0 deliverable (iv)-(vi), §3.3 item 5).

Compares two trace streams written by scripts/emit_sweep.py --trace (the
REFERENCE side, the parent commit's trace build, and the WORKING side). A
stream is a TSV `idx  arm  seq  record`, where `record` is the compiler's
CANDTRACE line with its tag stripped (tab-separated fields, see FIELDS) and
`idx`/`arm`/`seq` were attached by the sweep, never printed by the compiler.

WHAT IT REQUIRES, per (pattern index, arm):
  - the ORDERED sequence of records is identical on both sides. A diff of a
    corpus-wide multiset would cancel a swap between two patterns, and a
    per-pattern multiset would cancel a reorder inside one; this compares
    sequences, so neither cancels.
  - except for the commit's DECLARED multiplicity: records whose `site` is
    named in --declared are filtered from BOTH sides before comparing
    (C5b's BOUND readers are the one planned case). A declared site that
    filters nothing on the working side is itself a failure (the commit
    claimed an addition that did not happen -- a stale declaration).
  - each arm carries at least --min-records records on EACH side (a records
    floor: a trace build that prints nothing passes every diff).

--keys NAMES selects which record fields are compared (default: all the
fields a record carries). --unordered compares each (pattern, arm)'s SET of
records instead of its sequence: blind to order and multiplicity by design,
which is exactly what the C0 experiment found a selection-neutral commit can
change (a reader asking once more); a row change still shows as a new member. It is how the C0 brittleness experiment measured
a `func` field (the C function's name) against the declared `site` tag.

--order SLOT=ordered|set (repeatable; S-I2's detector, dec_fallback §4.2 item 7)
sets ONE slot's compare mode: SLOT is the record's first field. A slot named
`ordered` is compared as the ordered sequence of that slot's records per
(pattern, arm) -- records of other slots interleaved between them do not
matter; `set` compares that slot's SET. Every slot NOT named follows the
default (ordered, or set under --unordered), and those are compared together
as one subsequence, so cross-slot order among them is still held. Python API:
compare(..., order={slot: "ordered"|"set"}).

Exit 0 when clean, 1 on any difference or floor violation, 2 on a usage or
input error (an unreadable or header-less file is never an empty stream).
"""
import argparse
import collections
import sys

FIELDS = ("slot", "route", "row", "site", "func")
ORDER_MODES = ("ordered", "set")


def fail_input(msg):
    print(f"trace_diff: {msg}", file=sys.stderr)
    sys.exit(2)


def load(path):
    """{(idx, arm): [record tuple, ...]} in seq order."""
    seqs = collections.defaultdict(list)
    with open(path, encoding="utf-8", errors="replace") as fh:
        header = fh.readline().rstrip("\n").split("\t")
        if header[:4] != ["idx", "arm", "seq", "record"]:
            fail_input(f"{path}: not a trace stream (header {header!r})")
        for n, line in enumerate(fh, 2):
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 4:
                fail_input(f"{path}:{n}: short row {line!r}")
            seqs[(int(parts[0]), parts[1])].append((int(parts[2]), tuple(parts[3:])))
    out = {}
    for k, recs in seqs.items():
        recs.sort(key=lambda r: r[0])
        out[k] = [r for _, r in recs]
    return out


def read_declared(path):
    with open(path, encoding="utf-8") as fh:
        return {ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")}


def project(rec, keys):
    if keys is None:
        return rec
    return tuple(rec[FIELDS.index(k)] if FIELDS.index(k) < len(rec) else "" for k in keys)


def site_of(rec):
    return rec[FIELDS.index("site")] if len(rec) > FIELDS.index("site") else ""


def compare(a, b, declared=frozenset(), min_records=None, keys=None, show=5,
            unordered=False, order=None):
    """Returns (ok, report text). a/b as load() returns them; min_records an
    int or {arm: int}. order: optional {slot: "ordered"|"set"} per-slot
    compare modes (see the module docstring); unnamed slots follow
    `unordered`."""
    order = dict(order or {})
    for slot, mode in order.items():
        if mode not in ORDER_MODES:
            raise ValueError(f"order mode for slot {slot!r}: {mode!r} not in {ORDER_MODES}")
    lines = []
    ok = True
    arms = sorted({k[1] for k in a} | {k[1] for k in b})
    totals = {arm: [0, 0] for arm in arms}
    for side, s in ((0, a), (1, b)):
        for (idx, arm), recs in s.items():
            totals[arm][side] += len(recs)
    if min_records is not None:
        floors = min_records if isinstance(min_records, dict) else {}
        if not floors and not arms:
            # an int floor over NO arm checks nothing: the empty-vs-empty
            # shape this floor exists to refuse (its own self-test's catch)
            ok = False
            lines.append(f"  RECORDS FLOOR: no arm carried any record (floor {min_records})")
        for arm in sorted(set(arms) | set(floors)):
            fl = floors.get(arm, min_records if isinstance(min_records, int) else 0)
            got = totals.get(arm, [0, 0])
            for side in (0, 1):
                if got[side] < fl:
                    ok = False
                    lines.append(f"  RECORDS FLOOR side {'ab'[side]} arm {arm}: "
                                 f"{got[side]} < {fl}")
    filtered = [0, 0]
    movers = []
    for k in sorted(set(a) | set(b)):
        sa, sb = [], []
        slot_a, slot_b = collections.defaultdict(list), collections.defaultdict(list)
        for side, src, dst, bys in ((0, a.get(k, []), sa, slot_a), (1, b.get(k, []), sb, slot_b)):
            for rec in src:
                if declared and site_of(rec) in declared:
                    filtered[side] += 1
                    continue
                if order and rec and rec[0] in order:
                    bys[rec[0]].append(project(rec, keys))
                else:
                    dst.append(project(rec, keys))
        for slot in sorted(set(slot_a) | set(slot_b)):
            xa, xb = slot_a.get(slot, []), slot_b.get(slot, [])
            if order[slot] == "set":
                if set(xa) != set(xb):
                    movers.append((k, f"slot {slot} set", sorted(set(xa) - set(xb))[:1] or None,
                                   sorted(set(xb) - set(xa))[:1] or None, len(xa), len(xb)))
            elif xa != xb:
                pos = next((i for i, (x, y) in enumerate(zip(xa, xb)) if x != y), min(len(xa), len(xb)))
                movers.append((k, f"slot {slot} #{pos}", xa[pos] if pos < len(xa) else None,
                               xb[pos] if pos < len(xb) else None, len(xa), len(xb)))
        if unordered:
            if set(sa) != set(sb):
                movers.append((k, "set", sorted(set(sa) - set(sb))[:1] or None,
                               sorted(set(sb) - set(sa))[:1] or None, len(sa), len(sb)))
            continue
        if sa != sb:
            pos = next((i for i, (x, y) in enumerate(zip(sa, sb)) if x != y), min(len(sa), len(sb)))
            movers.append((k, pos, sa[pos] if pos < len(sa) else None,
                           sb[pos] if pos < len(sb) else None, len(sa), len(sb)))
    if declared and filtered[1] == 0:
        ok = False
        lines.append(f"  DECLARED MULTIPLICITY NOT OBSERVED: sites {sorted(declared)} filtered "
                     f"0 working-side records (a stale declaration)")
    if movers:
        ok = False
        lines.append(f"  TRACE MOVERS: {len(movers)} pattern-arm sequences differ; first {show}:")
        for (idx, arm), pos, x, y, na, nb in movers[:show]:
            lines.append(f"    idx={idx} arm={arm} at seq {pos} (len {na}/{nb}): "
                         f"ref={x!r} working={y!r}")
    head = (f"  sequences={len(set(a) | set(b))} records per arm (ref/working): "
            + " ".join(f"{arm}={t[0]}/{t[1]}" for arm, t in sorted(totals.items()))
            + (f" declared-filtered={filtered[0]}/{filtered[1]}" if declared else "")
            + f" keys={','.join(keys) if keys else 'all'}"
            + (" compare=SET (order and multiplicity ignored)" if unordered else " compare=ordered")
            + (" order=" + ",".join(f"{s_}={m}" for s_, m in sorted(order.items())) if order else ""))
    return ok, "\n".join([head] + lines + ([f"  trace: {'CLEAN' if ok else 'FAIL'}"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ref")
    ap.add_argument("working")
    ap.add_argument("--declared")
    ap.add_argument("--min-records", type=int)
    ap.add_argument("--keys")
    ap.add_argument("--unordered", action="store_true")
    ap.add_argument("--order", action="append", default=[], metavar="SLOT=ordered|set")
    a = ap.parse_args()
    keys = a.keys.split(",") if a.keys else None
    if keys and any(k not in FIELDS for k in keys):
        ap.error(f"--keys: known fields are {','.join(FIELDS)}")
    order = {}
    for spec in a.order:
        slot, eq, mode = spec.partition("=")
        if not eq or not slot or mode not in ORDER_MODES:
            fail_input(f"--order {spec!r}: want SLOT=ordered|set")
        order[slot] = mode
    declared = read_declared(a.declared) if a.declared else frozenset()
    ok, text = compare(load(a.ref), load(a.working), declared=declared,
                       min_records=a.min_records, keys=keys, unordered=a.unordered, order=order)
    print(text)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
