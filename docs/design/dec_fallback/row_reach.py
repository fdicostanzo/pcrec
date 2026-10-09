#!/usr/bin/env python3
"""docs/design/dec_fallback/row_reach.py -- [DEC-FALLBACK] B0 item 8 (built at
B1): ROW REACH, read off the B1 fallback trace (dec_fallback.md §4.2 B0 item
8, §4.3a; critB2 M3).

For every variant x flag ARM, compile the population with a TRACE build
(`-DPCREC_CAND_TRACE` plus the variant's `-D` set, built from `git archive`)
and count, from the compile's own `CANDTRACE` records:

  T1    the `fallback` slot: (row, arrival label set)       per record
  T2    the `admit` slot:    (row, scope); `default` split on/off by its verdict
  T3    the `gate` slot:     (row, PFLW) -- `rung` keeps its PFLW (sel1/sizecap)
  T4    the `stwhy` slot:    (token)
  ESEL  the `attrib` slot:   (token, the row whose cell gave it)
  SEQ   each compile's fallback sequence CLASS: whether a [SEL-1] row and a
        size-cap row (6-9) both fired, and in which order (§1.7's last two
        sequence rows, legal but unpopulated)

The population is the rev-2 prototype's (`reach/reach.py`: every distinct
corpus block, decoded, its own flags/features/encoding/engine, plus
`reach/witnesses.tsv`) and its 14 arms (lowthr: base/vm/no-st/unroll4, the
prototype's own subset), so the counts are comparable with
`reach/out/reach.md` cell for cell.

WHAT IT FAILS ON (exit 1):
  - a DECLARED-ZERO cell (DECLARED_ZERO below: §4.3a's UNREACHED entries and
    the structural zeros of T2/T3's scopes) is non-zero on the WORKING side,
    in any variant or arm. The declaration is hand-written from the design's
    arguments, never from a count, so a new population is a failure to
    explain, not a silent new cell;
  - a cell reached on the PARENT (> 0) is 0 on the working side, same variant
    and arm (a row that stopped firing, or a record that stopped printing).
    Not applicable when the parent prints no B1 trace at all (a pre-B1
    parent), which the report says;
  - K35: the population is below POPULATION_FLOOR, or a table's records are
    all zero on the working side (a slot that stopped printing everywhere).

It shares no source with T1-T4 (none exists before B2) and reads only the
trace; its declared zeros come from the note. Its limits: it counts what the
trace prints, so a record printed under the wrong row name moves a count
between cells and is caught only if a declared zero or a parent cell sees
it (the cross-record and the trace compare are the stronger detectors).

Writes OUT/reach.tsv (side variant arm table row cell n witness) and
OUT/records_<side>_<variant>_<arm>.jsonl (each compile's records, for the
cross-record), and prints the check summary.

usage: row_reach.py --ref REV --rev REV [--variants a,b] [--arms a,b]
                    [--stride N] [--jobs N] [--out DIR] [--keep-builds]
Exit 0 clean, 1 a check failed, 2 bad input or a build failure.
"""
import argparse, collections, importlib.util, json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import emit_sweep                                   # noqa: E402  VARIANTS, build_from_rev

_spec = importlib.util.spec_from_file_location("reach", os.path.join(HERE, "reach/reach.py"))
reach = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(reach)

TRACE_CFLAGS = emit_sweep.TRACE_CFLAGS
LOWTHR_ARMS = ("base", "vm", "no-st", "unroll4")
SLOTS = {"fallback": "T1", "admit": "T2", "gate": "T3", "stwhy": "T4", "attrib": "ESEL"}
SEL1 = ("sel1-collapse", "sel1-drop")
SIZE = ("prefilter-collapse", "drop-anchored", "drop-premul", "drop-prefilter")
# K35: the distinct-block population, MEASURED 4,794 corpus blocks + 17
# witnesses at B1's base (attempt_hist.py's floor, the same population).
POPULATION_FLOOR = 4746 + 17

# THE DECLARED ZEROS, hand-written from dec_fallback.md §4.3a (each cell's
# argument is there) and from T2/T3's own scope predicates. (table, row, cell)
# with "*" for every cell of the row; a cell containing "|" (two arrival
# labels on one arrival) is declared zero by the rule below the list.
DECLARED_ZERO = [
    ("T1", "forcing", "*"),             # no corpus compile fails inside the force loop (W5)
    ("T1", "nomem", "*"),               # allocation failure only (W4)
    ("T1", "size-term-trial", "overflow"),   # §4.3a: a trial overflows no machine the default fit
    ("T1", "size-term-trial", "size"),  # the caps refuse only the default/final attempt
    ("T1", "unroll-rescue", "*"),       # chosen inside size_term_choose, never at an arrival
    ("T1", "refuse", "nomem"),          # row 1 takes every nomem arrival first
] + [("T1", r, c) for r in SEL1 for c in ("size", "other", "nomem")] \
  + [("T1", r, c) for r in SIZE for c in ("overflow", "other", "nomem")] + [
    # T2: rows 1-3 build no prefilter, so no DFA overflows and no rung applies
    *[("T2", r, s) for r in ("backref", "linked-call", "var")
      for s in ("sel1", "sizecap")],
    # [DEC-VAR-ATTRIB] row 7: only the [PF-DROP] rung writes SDR_NO_PREFILTER,
    # and only on the SIZE ladder (CR is NONE or SIZECAP there, never SEL1)
    ("T2", "size-dropped", "sel1"),
    # ... and the bit the rung ORs in no longer reaches `forced-off` at SIZECAP
    ("T2", "forced-off", "sizecap"),
    ("T2", "nullable-exact", "sel1"), ("T2", "nullable-exact", "sizecap"),   # row 4: CR == NONE
    ("T2", "nullable-collapsed", "none"),     # row 5: CR != NONE
    ("T2", "nullable-collapsed", "sizecap"),  # §4.3a: structural
    ("T2", "overflow-drop", "sizecap"),       # the m2 sequence (F-B3's state)
    ("T2", "forced-on", "sel1"),              # no retry under -fprefilter
    ("T2", "forced-off", "sel1"),             # row 6 catches dd && force_off first
    ("T2", "default-off", "sel1"), ("T2", "default-off", "sizecap"),  # a rung is VM + prefilter
    # T3: `rung` needs CR != NONE and its PFLW is the CR's; `forced` loses to a rung
    ("T3", "rung-sel1", "none"), ("T3", "rung-sel1", "sizecap"),
    ("T3", "rung-sizecap", "none"), ("T3", "rung-sizecap", "sel1"),
    ("T3", "forced", "sel1"), ("T3", "forced", "sizecap"),
    # SEQ: §1.7's two unpopulated legal sequences (critB1 m2; §4.3a)
    ("SEQ", "size-then-sel1", "*"), ("SEQ", "sel1-then-size", "*"),
]


def log(m):
    print(m, file=sys.stderr, flush=True)


def cells_of(recs):
    """[(table, row, cell)] for one compile's CANDTRACE records (tag stripped,
    tab-split: slot route row-field site)."""
    out, seq = [], []
    for slot, route, rowf, _site in recs:
        t = SLOTS.get(slot)
        if not t:
            continue
        w = rowf.split(" ")
        if t == "T1":
            out.append((t, w[0], route)); seq.append(w[0])
        elif t == "T2":
            row = w[0]
            if row == "default":
                row = "default-on" if "pf=1" in w[1:] else "default-off"
            out.append((t, row, route))
        elif t == "T3":
            pflw = w[1].split("=", 1)[1] if len(w) > 1 else "?"
            out.append((t, "rung-" + pflw if w[0] == "rung" else w[0], route))
        elif t == "T4":
            out.append((t, w[0], "-"))
        else:
            out.append((t, w[0], w[1].split("=", 1)[1] if len(w) > 1 else "?"))
    first_sel1 = next((i for i, r in enumerate(seq) if r in SEL1), None)
    first_size = next((i for i, r in enumerate(seq) if r in SIZE), None)
    if first_sel1 is not None and first_size is not None:
        out.append(("SEQ", "sel1-then-size" if first_sel1 < first_size else "size-then-sel1", "-"))
    return out


def declared_zero(table, row, cell):
    if table == "T1" and "|" in cell:
        return True          # two labels on one arrival: only via an optional machine (§1.1)
    return any(t == table and r == row and c in ("*", cell) for t, r, c in DECLARED_ZERO)


def run_cell(comp, arm, cases, jobs, out_jsonl):
    """Compile every case under one arm; -> {cell: [n, witness]} and the
    per-compile records file."""
    counts = collections.defaultdict(lambda: [0, None])

    def one(case):
        src, key = case
        cmd = reach.argv(comp, key, arm, src == "corpus")
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=120)
        except subprocess.TimeoutExpired:
            return src, key, "TIMEOUT", []
        recs = []
        for ln in r.stderr.decode("utf-8", "replace").split("\n"):
            if ln.startswith("CANDTRACE\t"):
                f = ln.split("\t")[1:]
                if len(f) >= 4 and f[0] in SLOTS:
                    recs.append(tuple(f[:4]))
        return src, key, ("ok" if r.returncode == 0 else "refused"), recs

    with ThreadPoolExecutor(max_workers=jobs) as ex, open(out_jsonl, "w") as fh:
        for src, key, status, recs in ex.map(one, cases):
            fh.write(json.dumps({"src": src, "key": key, "status": status, "rec": recs}) + "\n")
            for c in cells_of(recs):
                counts[c][0] += 1
                if counts[c][1] is None:
                    counts[c][1] = (src, key[0], " ".join(reach.ARMS[arm]))
    return counts


def tree_of(rev):
    return subprocess.check_output(["git", "-C", ROOT, "rev-parse", rev + "^{tree}"],
                                   text=True).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--rev", required=True)
    ap.add_argument("--variants", default=",".join(emit_sweep.VARIANTS))
    ap.add_argument("--arms", default=",".join(reach.ARMS))
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--out", default=os.path.join(ROOT, "build/row_reach"))
    a = ap.parse_args()
    variants = a.variants.split(",")
    arms = a.arms.split(",")
    for v in variants:
        if v not in emit_sweep.VARIANTS:
            ap.error(f"unknown variant {v!r}")
    for x in arms:
        if x not in reach.ARMS:
            ap.error(f"unknown arm {x!r}")
    os.makedirs(a.out, exist_ok=True)
    mirror = tree_of(a.ref) == tree_of(a.rev)
    sides = ("ref",) if mirror else ("ref", "rev")
    revs = {"ref": a.ref, "rev": a.rev}
    cases = reach.corpus_cases(ROOT)[::a.stride] + reach.witness_cases(ROOT)
    full = a.stride == 1
    log(f"[row_reach] population {len(cases)} (stride {a.stride}); "
        f"{'MIRROR (one tree)' if mirror else 'ref vs rev'}")
    counts = {}           # (side, variant, arm) -> {cell: [n, wit]}
    for v in variants:
        cflags = (TRACE_CFLAGS + " " + emit_sweep.VARIANTS[v]).strip()
        bins = {}
        for side in sides:
            try:
                bins[side], _ = emit_sweep.build_from_rev(ROOT, revs[side], a.out, "gcc",
                                                          f"{side}-trace-{v}", cflags=cflags)
            except Exception as e:      # noqa: BLE001  a build failure is exit 2
                log(f"[row_reach] BUILD FAILED {side} {v}: {e}")
                sys.exit(2)
        for arm in arms:
            if v == "lowthr" and arm not in LOWTHR_ARMS:
                continue
            for side in sides:
                log(f"[row_reach] {side} {v} {arm} ...")
                counts[(side, v, arm)] = run_cell(
                    bins[side], arm, cases, a.jobs,
                    os.path.join(a.out, f"records_{side}_{v}_{arm}.jsonl"))
            if mirror:
                counts[("rev", v, arm)] = counts[("ref", v, arm)]
    ok, lines = True, []
    if full and len(cases) < POPULATION_FLOOR:
        ok = False
        lines.append(f"POPULATION FLOOR: {len(cases)} < {POPULATION_FLOOR}")
    totals = collections.Counter()
    parent_has_trace = any(c[0] == "T1" or c[0] == "T2" for (s, _v, _a), cs in counts.items()
                           if s == "ref" for c in cs)
    for (side, v, arm), cs in sorted(counts.items()):
        if side != "rev":
            continue
        for cell, (n, wit) in cs.items():
            totals[cell[0]] += n
            if n and declared_zero(*cell):
                ok = False
                lines.append(f"DECLARED ZERO REACHED: {v} {arm} {cell}: {n} (e.g. {wit})")
        if parent_has_trace and not mirror:
            for cell, (n, wit) in counts[("ref", v, arm)].items():
                if n and not cs.get(cell, [0])[0]:
                    ok = False
                    lines.append(f"REACHED CELL DROPPED: {v} {arm} {cell}: parent {n}, "
                                 f"working 0 (parent witness {wit})")
    for t in ("T1", "T2", "T3", "T4", "ESEL"):
        if not totals[t]:
            ok = False
            lines.append(f"K35: table {t} has NO record on the working side (a slot stopped printing)")
    with open(os.path.join(a.out, "reach.tsv"), "w") as fh:
        fh.write("side\tvariant\tarm\ttable\trow\tcell\tn\twitness\n")
        for (side, v, arm), cs in sorted(counts.items()):
            if mirror and side == "rev":
                continue
            for (t, r, c), (n, wit) in sorted(cs.items()):
                fh.write(f"{side}\t{v}\t{arm}\t{t}\t{r}\t{c}\t{n}\t{json.dumps(wit)}\n")
    print(f"population: {len(cases)} cases x {len(variants)} variants x arms ({'mirror' if mirror else 'two sides'})")
    print(f"records per table (working): " + " ".join(f"{t}={totals[t]}" for t in sorted(totals)))
    print(f"declared-zero cells: {len(DECLARED_ZERO)} (+ every two-label arrival)")
    if not parent_has_trace:
        print("parent carries no B1 trace: the dropped-cell check does not apply")
    elif mirror:
        print("one tree: the dropped-cell check is trivially clean")
    for ln in lines[:40]:
        print("  " + ln)
    if len(lines) > 40:
        print(f"  ... {len(lines) - 40} more")
    print(f"table: {os.path.join(a.out, 'reach.tsv')}")
    print("ROW_REACH: " + ("CLEAN" if ok else "FAILED"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
