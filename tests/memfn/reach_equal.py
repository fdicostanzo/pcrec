#!/usr/bin/env python3
"""tests/memfn/reach_equal.py -- REACH EQUALITY between two MF_TRACE pcrec
builds (span_pick.md rev 5.2 §Staging, Witness: "REACH EQUALITY, not
floors"; a stage-1 unit's witness beside byte identity). Opt-in, no make
target; a corpus run is heavy (it takes the box lock through its caller).

  reach_equal.py --ref-bin BASE --bin HEAD --tree TREE
                 [--patterns-file F]... [--gone TABLE:ROW,...] [--arms A;B;...]
                 [--map FILE] [--jobs N] [--timeout S] [--limit N] [--no-corpus]

Both binaries are built with -DMF_TRACE (`make BUILD_DIR=D CFLAGS="-O2 -g
-DMF_TRACE"`). Each compiles every distinct pattern of the corpus (the
working tree's, scripts/emit_sweep.py's enumerate_corpus) plus the patterns
files, at each arm, exactly as emit_sweep's c-default stream does
(`-p rx --features all ARM -o - --pattern P`). Every `MFTRACE REACH` line a
process prints at exit is summed per (arm, line key): a row's `chosen` and
`asked`, and each field/class cell's `n`. The verdict:

  - every (pattern, arm) has the same key->count map at BASE and HEAD
    (per PATTERN, not per sum, so compensating moves between patterns do
    not cancel), a key absent on one side and 0 on the other differing;
  - the ROW SET (rows with any line) of each arm is the same at BASE and
    HEAD less the declared gone rows; the GONE set is DERIVED (rows with
    lines at BASE and none at HEAD, over all arms) and must equal --gone
    exactly, both directions; each gone row's BASE chosen/asked per arm
    is printed (a "zero reach" claim is read from it, not typed);
  - the compile return codes and timeouts: the SETS of failing patterns
    per arm are equal at BASE and HEAD (a pattern failing on both sides
    is counted and printed);
  - REACH_DROPPED is 0 on both sides;
  - K35: compiles counted per arm, and fewer than POP_FLOOR distinct
    patterns, or a side whose rows were never chosen, is red.

Independent control: the population is the tree's own corpus and the
committed patterns files; the counts are the kit's own reach counters on
both sides, so a defect that moves a decision moves a count. The gone set
is derived from the two traces and compared with the declaration.
THE ROW MAP (--map, span_pick 1e: tests/memfn/row_map.tsv): a DECLARED move
of a row from BASE's table to HEAD's, `from_table from_row to_table to_row`
(`-` `-` a row dissolved into the rows of its new table). A BASE table that
prints no REACH lines (window.c's wfD did not) is read from its END records:
its row's selections are counted as the kit counts them (a non-quiet END
naming it, phase neither use nor shadow) and, wherever BASE printed the
target table's REACH lines, added to BASE's map under the target's key
(`asked` 0). A dissolved row's BASE selections are printed per arm. A map
line whose target never prints at HEAD, or a from_table that prints any
record at HEAD, is red. The map is held to BASE's own trace BOTH WAYS (it is
parsed by tests/memfn/row_map.py, which rows_check.py shares): a from-row with
no BASE selection over the population is red (an invented line, or a sample
too small to see it: K35); a table with records at BASE and none at HEAD that
no map line (or --gone row) names is red, as is a map from-table with no BASE
record; and a row of such a table that BASE selected and the map does not name
is red (a deleted line).
A --limit or --no-corpus (the patterns files alone) run is a SMOKE run: it skips the population floor, so its last
line is `reach_equal: LIMITED rc=N ...` and it exits 0 never (3 when clean,
1 when not): it cannot be read as the verdict.
Last line: `reach_equal: DONE rc=N keys=K differ=D` (scripts/verdict's trailer).
"""
import argparse
import collections
import concurrent.futures
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import row_map   # the ONE parser of row_map.tsv (rows_check.py reads it too)

POP_FLOOR = 1000
DEFAULT_ARMS = ["", "--engine=vm", "-fmemfn-simd", "-e utf8"]
LINE = re.compile(r"^MFTRACE REACH table=(\S+) row=(\S+) (.*)$")
END = re.compile(r"^MFTRACE END table=(\S+) .*\bphase=(\S+) chosen=(\S+) ")
TABLE = re.compile(r"^MFTRACE (?!REACH)\S+ .*?\btable=(\S+)")

# One compile's trace. counts: the REACH lines summed per key; tables: every table
# a non-REACH record names; ends: (table, row) -> the selections the kit counts
# (a non-quiet END, phase neither use nor shadow), for every table.
Reach = collections.namedtuple("Reach", "counts dropped why tables ends")


def load_emit_sweep(tree):
    sys.path.insert(0, os.path.join(tree, "scripts"))
    import emit_sweep
    return emit_sweep


def reach_of(binary, pat, arm, timeout):
    argv = [binary, "-p", "rx", "--features", "all"] + arm.split() + ["-o", "-", "--pattern", pat]
    try:
        r = subprocess.run(argv, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=timeout)
    except subprocess.TimeoutExpired:
        return Reach(None, 0, "timeout", set(), collections.Counter())
    counts = collections.Counter()
    ends = collections.Counter()
    tables = set()
    dropped = 0
    for ln in r.stderr.decode("utf-8", "replace").splitlines():
        if ln.startswith("MFTRACE REACH_DROPPED n="):
            dropped += int(ln.split("=", 1)[1])
            continue
        m = LINE.match(ln)
        if not m:
            t = TABLE.match(ln)
            if t:
                tables.add(t.group(1))
                e = END.match(ln)
                if e and e.group(2) not in ("use", "shadow") and e.group(3) != "-":
                    ends[(e.group(1), e.group(3))] += 1
            continue
        table, row, rest = m.groups()
        kv = dict(t.split("=", 1) for t in rest.split())
        if "field" in kv:
            counts[(table, row, "field=%s class=%s" % (kv["field"], kv["class"]))] += int(kv["n"])
        else:
            counts[(table, row, "chosen")] += int(kv["chosen"])
            counts[(table, row, "asked")] += int(kv["asked"])
    return Reach(counts, dropped, "rc%d" % r.returncode if r.returncode else "", tables, ends)


def through_map(rc, rmap, dissolved):
    """BASE's counts with the declared moves applied: a moved row's END selections
    under its target's key (where BASE printed the target table's REACH lines), a
    dissolved row's added to `dissolved` (printed, never compared)."""
    out = collections.Counter(rc.counts)
    reach_tables = {k[0] for k in out}
    for ft, fr, tt, tr, _unit in rmap:
        n = rc.ends[(ft, fr)]
        if tt == "-":
            dissolved["%s:%s" % (ft, fr)] += n
        elif tt in reach_tables:
            out[(tt, tr, "chosen")] += n
            out[(tt, tr, "asked")] += 0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref-bin", required=True)
    ap.add_argument("--bin", required=True)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--patterns-file", action="append", default=[])
    ap.add_argument("--gone", default="", help="TABLE:ROW,... rows deleted at HEAD (must equal the derived set)")
    ap.add_argument("--arms", default=";".join(DEFAULT_ARMS), help="`;`-separated arm flag strings")
    ap.add_argument("--map", help="the declared row map (tests/memfn/row_map.tsv)")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--limit", type=int, default=0, help="SMOKE: first N patterns; skips the floor, trailer LIMITED")
    ap.add_argument("--no-corpus", action="store_true", help="SMOKE: the patterns files alone; trailer LIMITED")
    a = ap.parse_args()
    es = load_emit_sweep(a.tree)
    pats = [] if a.no_corpus else es.enumerate_corpus(a.bin, a.tree, 60)
    for f in a.patterns_file:
        pats += es.read_patterns_file(f)
    pats = sorted(set(bytes(p[2]) if not isinstance(p[2], str) else p[2].encode("utf-8", "surrogateescape")
                      for p in pats))
    if a.limit:
        pats = pats[:a.limit]
    smoke = bool(a.limit or a.no_corpus)
    arms = a.arms.split(";")
    gone = {tuple(g.split(":", 1)) for g in a.gone.split(",") if g}
    try:
        rmap = row_map.read_map(a.map) if a.map else []
    except row_map.MapError as e:
        raise SystemExit("reach_equal: " + str(e))
    problems = []
    dissolved = {arm: collections.Counter() for arm in arms}
    mapped = collections.Counter()     # (side, to_table, to_row): chosen summed
    tables = {"base": set(), "head": set()}                   # tables any non-REACH record names
    base_ends = collections.Counter()  # (table, row) -> BASE selections over the whole population
    from_tables = {m[0] for m in rmap}
    if len(pats) < POP_FLOOR and not smoke:
        problems.append("population %d distinct patterns under POP_FLOOR %d" % (len(pats), POP_FLOOR))
    print("population: %d distinct patterns x %d arms%s" % (len(pats), len(arms), " (LIMITED smoke run)" if smoke else ""))
    rows = {s: {arm: set() for arm in arms} for s in ("base", "head")}
    gone_base = {arm: collections.Counter() for arm in arms}    # (table,row,chosen|asked) summed at BASE
    chosen_head = collections.Counter()
    dropped = collections.Counter()
    fails = {s: collections.defaultdict(dict) for s in ("base", "head")}   # arm -> {pattern: why}
    pending = {}                       # (arm, pattern) -> (side, counter) of the side that arrived first
    perpat = collections.Counter()     # arm -> patterns whose maps differ
    examples = []
    tasks = [(s, b, arm, p) for arm in arms for p in pats
             for s, b in (("base", a.ref_bin), ("head", a.bin))]
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(reach_of, b, p.decode("utf-8", "surrogateescape"), arm, a.timeout): (s, arm, p)
                for s, b, arm, p in tasks}
        for f in concurrent.futures.as_completed(futs):
            s, arm, p = futs[f]
            rc = f.result()
            c, d, why = rc.counts, rc.dropped, rc.why
            dropped[s] += d
            if why:
                fails[s][arm][p] = why
            if c is None:
                continue
            tables[s] |= rc.tables
            if s == "base":
                base_ends.update(rc.ends)
                c = through_map(rc, rmap, dissolved[arm])
            elif rc.tables & from_tables:
                problems.append("arm %r pattern %r: HEAD prints a record of the mapped-away table %s"
                                % (arm, p[:60], sorted(rc.tables & from_tables)))
            for ft, fr, tt, tr, _unit in rmap:
                if tt != "-":
                    mapped[(s, tt, tr)] += c.get((tt, tr, "chosen"), 0)
            rows[s][arm].update((k[0], k[1]) for k in c)
            if s == "base":
                for k, v in c.items():
                    if (k[0], k[1]) in gone and k[2] in ("chosen", "asked"):
                        gone_base[arm][k] += v
            else:
                chosen_head[arm] += sum(v for k, v in c.items() if k[2] == "chosen")
            other = pending.pop((arm, p), None)
            if other is None:
                pending[(arm, p)] = (s, c)
                continue
            b, h = (c, other[1]) if s == "base" else (other[1], c)
            b = {k: v for k, v in b.items() if (k[0], k[1]) not in gone}
            h = {k: v for k, v in h.items() if (k[0], k[1]) not in gone}
            if b != h:
                perpat[arm] += 1
                if len(examples) < 20:
                    diff = sorted((k, b.get(k), h.get(k)) for k in set(b) | set(h) if b.get(k) != h.get(k))
                    examples.append("arm %r pattern %r: %s" % (arm, p[:60], "; ".join(
                        "%s/%s %s base %s head %s" % (k[0], k[1], k[2], x, y) for k, x, y in diff[:3])))
    differ = nkeys = 0
    for arm in arms:
        armd = perpat[arm]
        differ += armd
        nb, nh = len(rows["base"][arm]), len(rows["head"][arm])
        nkeys += nh
        print("arm %-14r rows base %d head %d, patterns differing %d, head chosen total %d, failing base %d head %d"
              % (arm, nb, nh, armd, chosen_head[arm], len(fails["base"][arm]), len(fails["head"][arm])))
        if armd:
            problems.append("arm %r: %d patterns have a different reach map at HEAD" % (arm, armd))
        if rows["base"][arm] - gone != rows["head"][arm]:
            miss = sorted(rows["base"][arm] - gone - rows["head"][arm])
            new = sorted(rows["head"][arm] - rows["base"][arm])
            problems.append("arm %r: row sets differ beyond the declared gone rows: lost %s, new %s" % (arm, miss, new))
        if chosen_head[arm] == 0:
            problems.append("arm %r: no row chosen at HEAD (an empty population)" % arm)
        fb, fh = fails["base"][arm], fails["head"][arm]
        if fb != fh:
            problems.append("arm %r: failing patterns differ (base %d, head %d; %d only at base, %d only at head, %d differing cause)"
                            % (arm, len(fb), len(fh), len(set(fb) - set(fh)), len(set(fh) - set(fb)),
                               sum(1 for q in set(fb) & set(fh) if fb[q] != fh[q])))
        elif fb:
            print("  arm %r: %d patterns fail identically on both sides (%s)" % (arm, len(fb), ",".join(sorted(set(fb.values())))))
    union_b = set().union(*rows["base"].values())
    union_h = set().union(*rows["head"].values())
    derived = union_b - union_h
    for ft, fr, tt, tr, _unit in rmap:
        if tt == "-":
            for arm in arms:
                print("dissolved %s/%s arm %r: BASE chosen %d (its selections are its new table's rows')"
                      % (ft, fr, arm, dissolved[arm]["%s:%s" % (ft, fr)]))
        elif (tt, tr) not in union_h:
            problems.append("map target %s/%s prints no REACH line at HEAD" % (tt, tr))
        else:
            print("mapped %s/%s -> %s/%s: chosen BASE %d HEAD %d (all arms)"
                  % (ft, fr, tt, tr, mapped[("base", tt, tr)], mapped[("head", tt, tr)]))
            if not mapped[("head", tt, tr)]:
                problems.append("map target %s/%s never chosen at HEAD (the map is unexercised)" % (tt, tr))
    if rmap:
        # the map held to BASE's own trace, BOTH WAYS (the BASE side is the control
        # for the file the map is read from)
        gone_t = {t for t, _r in gone}
        for ft in sorted(from_tables - tables["base"]):
            problems.append("map from-table %s has no record at BASE (an invented line, or a sample too small)" % ft)
        for ft in sorted((tables["base"] - tables["head"]) - from_tables - gone_t):
            problems.append("table %s has records at BASE and none at HEAD, and no map line or --gone row "
                            "names it (a deleted line)" % ft)
        for ft, fr, _tt, _tr, _unit in rmap:
            if not base_ends[(ft, fr)]:
                problems.append("map from-row %s/%s has no BASE selection over the population (K35: "
                                "an invented line, or a sample too small to see it)" % (ft, fr))
        named = {(m[0], m[1]) for m in rmap}
        for (t, r), n in sorted(base_ends.items()):
            if t in from_tables and (t, r) not in named:
                problems.append("BASE selected %s/%s %d times and no map line names it (a deleted line)" % (t, r, n))
        print("map vs BASE trace: from-tables %s, BASE selections of mapped rows %s"
              % (sorted(from_tables), {"%s/%s" % (m[0], m[1]): base_ends[(m[0], m[1])] for m in rmap}))
    print("derived gone rows (lines at BASE, none at HEAD): %s" % (", ".join("%s/%s" % g for g in sorted(derived)) or "none"))
    if derived != gone:
        problems.append("derived gone set %s != declared %s" % (sorted(derived), sorted(gone)))
    for t, r in sorted(derived | gone):
        for arm in arms:
            print("gone %s/%s arm %r: BASE chosen %d asked %d" % (
                t, r, arm, gone_base[arm][(t, r, "chosen")], gone_base[arm][(t, r, "asked")]))
    for s in ("base", "head"):
        if dropped[s]:
            problems.append("%s: REACH_DROPPED %d" % (s, dropped[s]))
    for e in examples:
        print("DIFF: " + e)
    for p in problems[:200]:
        print("FAIL: " + p)
    rc = 1 if problems else 0
    if smoke:
        print("reach_equal: LIMITED rc=%d keys=%d differ=%d (smoke run, not a verdict)" % (rc, nkeys, differ))
        return 1 if rc else 3
    print("reach_equal: DONE rc=%d keys=%d differ=%d" % (rc, nkeys, differ))
    return rc


if __name__ == "__main__":
    sys.exit(main())
