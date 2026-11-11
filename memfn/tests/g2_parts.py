#!/usr/bin/env python3
# SPDX-License-Identifier: 0BSD
# Provenance: original pcrec-memory-functions text (R-39, lane r39).
"""g2_parts.py -- the part-K-of-N selector's two halves for run_g2.sh --quick.

  g2_parts.py list   --table T
  g2_parts.py assign --table T [--units a,b,..] [--part K/N]
  g2_parts.py gather --table T [--units a,b,..] [--row-floors F] [--unsplit-units FILE] LOG...

`assign` prints the space-separated unit ids of part K of N (all units when --part is absent), in
table order. The rule is declared and deterministic: units sorted by weight (heaviest first, table
order breaking ties) are dealt one at a time to the part with the least weight so far (lowest part
number breaking ties). Nothing about a run enters it.

`gather` reads the stdout of the N parts (one LOG each) and judges what a part cannot:
  P1  the EXACT POPULATION: the parts' `G2UNIT name seconds` manifests cover the expected units (the
      table, or --units, or --unsplit-units FILE: the `name seconds` lines an unsplit run wrote to
      G2_UNITS_OUT) each exactly once, and each part ran exactly the units `assign` deals it;
  P2  the COUNTS over the population: run_g2.sh section 4b's (a)-(e) from the parts' `G2PART` lines, in
      the unsplit run's own words (the prelude generator's one REACH process and one REACH_DROPPED line
      are in every part and counted once);
  P3  the totals: `checks passed` / `checks failed` as one run would print them (the prelude and
      section 5, which every part runs, counted once), and every part's own verdict.
It prints PASS/FAIL lines, the per-part wall times, and the unsplit run's trailer shape; exit 0 only
when nothing failed, 1 on a red, 2 on unusable input.
"""
import argparse
import re
import sys


def read_table(path):
    units = []  # [(name, weight)]
    with open(path) as f:
        for ln in f:
            if ln.startswith("#") or not ln.strip():
                continue
            c = ln.rstrip("\n").split("\t")
            if len(c) < 3 or not re.fullmatch(r"[0-9]+", c[1]):
                sys.exit("g2_parts.py: bad table line (unit, integer weight, source): %r" % ln)
            if c[0] in [u for u, _ in units]:
                sys.exit("g2_parts.py: unit %s listed twice" % c[0])
            units.append((c[0], int(c[1])))
    if not units:
        sys.exit("g2_parts.py: empty table")
    return units


def select(units, names):
    if not names:
        return units
    want = names.split(",")
    known = [u for u, _ in units]
    for w in want:
        if w not in known:
            sys.exit("g2_parts.py: no unit %r (known: %s)" % (w, " ".join(known)))
    if len(set(want)) != len(want):
        sys.exit("g2_parts.py: --units names a unit twice")
    return [(u, w) for u, w in units if u in want]


def parse_part(spec):
    m = re.fullmatch(r"([0-9]+)/([0-9]+)", spec)
    if not m or not (1 <= int(m.group(1)) <= int(m.group(2))):
        sys.exit("g2_parts.py: --part wants K/N with 1 <= K <= N, got %r" % spec)
    return int(m.group(1)), int(m.group(2))


def deal(units, n):
    """-> list of n lists of unit names (each in table order)."""
    order = {u: i for i, (u, _) in enumerate(units)}
    load = [0] * n
    parts = [[] for _ in range(n)]
    for u, w in sorted(units, key=lambda x: (-x[1], order[x[0]])):
        k = min(range(n), key=lambda i: (load[i], i))
        parts[k].append(u)
        load[k] += w
    return [sorted(p, key=order.get) for p in parts]


def cmd_list(a):
    for u, w in read_table(a.table):
        print("%s\t%d" % (u, w))


def cmd_assign(a):
    units = select(read_table(a.table), a.units)
    if a.part:
        k, n = parse_part(a.part)
        units = [(u, w) for u, w in units if u in deal(units, n)[k - 1]]
    print(" ".join(u for u, _ in units))


class Verdict:
    def __init__(self):
        self.passed = 0   # the section 4b checks (a)-(e): counted into `checks passed` as run_g2.sh counts them
        self.failed = 0

    def ok(self, msg, counted=False):
        print("PASS: " + msg)
        self.passed += counted

    def bad(self, msg):
        print("FAIL: " + msg)
        self.failed += 1


def read_part(path):
    d = {"units": [], "rowchosen-prelude": {}, "rowchosen-other": {}, "noreach": [], "path": path}
    with open(path, errors="replace") as f:
        for ln in f:
            ln = ln.rstrip("\n")
            m = re.match(r"G2UNIT (\S+) (\d+)$", ln)
            if m:
                d["units"].append((m.group(1), int(m.group(2))))
                continue
            m = re.match(r"G2PART (\S+)(?: (.*))?$", ln)
            if m:
                key, rest = m.group(1), (m.group(2) or "")
                if key.startswith("rowchosen-"):
                    t, r, n = rest.split()
                    d[key][(t, r)] = int(n)
                elif key == "reach_noreach":
                    d["noreach"].append(rest)
                else:
                    d[key] = rest
                continue
            m = re.match(r"checks (passed|failed): (\d+)$", ln)
            if m:
                d[m.group(1)] = int(m.group(2))
    return d


def cmd_gather(a):
    v = Verdict()
    table = read_table(a.table)
    expected = select(table, a.units)
    exp_names = [u for u, _ in expected]
    slice_mode = bool(a.units)
    parts = [read_part(p) for p in a.logs]
    n = len(parts)
    if a.unsplit_units:
        with open(a.unsplit_units) as f:
            exp_names = [ln.split()[0] for ln in f if ln.strip()]
        if sorted(exp_names) != sorted(set(exp_names)):
            v.bad("the unsplit run's manifest %s lists a unit twice" % a.unsplit_units)
    for p in parts:
        for key in ("passed", "failed", "prelude_passed", "replicated_failed", "part"):
            if key not in p:
                sys.exit("g2_parts.py: %s has no %s line (not a --part/--units run's output?)" % (p["path"], key))

    # P1 the exact population
    seen = {}
    for i, p in enumerate(parts):
        for u, _ in p["units"]:
            seen.setdefault(u, []).append(i + 1)
    missing = [u for u in exp_names if u not in seen]
    dup = ["%s(parts %s)" % (u, ",".join(map(str, ps))) for u, ps in seen.items() if len(ps) > 1]
    extra = [u for u in seen if u not in exp_names]
    cov = sum(1 for u in exp_names if len(seen.get(u, [])) == 1)
    print("population: %d parts, %d units expected, %d run exactly once" % (n, len(exp_names), cov))
    if missing:
        v.bad("units run by no part: %s" % " ".join(missing))
    if dup:
        v.bad("units run by more than one part: %s" % " ".join(dup))
    if extra:
        v.bad("units run that the expected population does not list: %s" % " ".join(extra))
    if not (missing or dup or extra):
        v.ok("the %d parts ran all %d units, each exactly once" % (n, len(exp_names)))
    # each part ran what the declared rule deals it
    if not slice_mode and not a.unsplit_units:
        for i, p in enumerate(parts):
            m = re.match(r"(\d+)/(\d+) units (.*)$", p["part"])
            if not m or int(m.group(2)) != n:
                v.bad("%s: part line %r is not K/%d" % (p["path"], p["part"], n))
                continue
            k = int(m.group(1))
            want = deal(table, n)[k - 1]
            ran = sorted(u for u, _ in p["units"])
            if ran != sorted(want) or sorted(m.group(3).split()) != sorted(want):
                v.bad("part %d/%d ran %s but the rule deals it %s" % (k, n, " ".join(ran), " ".join(want)))
        ks = sorted(int(re.match(r"(\d+)/", p["part"]).group(1)) for p in parts if re.match(r"\d+/", p["part"]))
        if ks != list(range(1, n + 1)):
            v.bad("the logs are parts %s, not 1..%d once each" % (ks, n))

    # P2 the counts over the population (run_g2.sh section 4b (a)-(e))
    have_rows = any("floor_rows" in p for p in parts)
    if not have_rows:
        print("rows: no part ran the rows half (--no-rows?): (a)-(e) not judged")
    else:
        floor_rows = {p.get("floor_rows") for p in parts}
        if len(floor_rows) != 1:
            v.bad("the parts disagree on FLOOR_ROWS: %s" % sorted(floor_rows))
        floor_rows = int(sorted(floor_rows)[0])
        pre = [p["rowchosen-prelude"] for p in parts]
        if any(x != pre[0] for x in pre):
            v.bad("the prelude generator's rows differ between parts (it is deterministic: the seed or the library moved)")
        total = dict(pre[0])
        for p in parts:
            for k, c in p["rowchosen-other"].items():
                total[k] = total.get(k, 0) + c
        nproc = sum(int(p["reach_procs"]) for p in parts) - (n - 1)
        noreach = sorted({x for p in parts for x in p["noreach"]})
        drops = [tuple(map(int, p["reach_dropped"].split())) for p in parts]
        if not noreach and nproc > 0:
            v.ok("(d) all %d G2 kit processes printed REACH lines" % nproc, True)
        else:
            v.bad("(d) G2 kit process(es) printed no REACH line:%s" % (" " + " ".join(noreach) if noreach else " none found at all"))
        if all(d[0] == 0 and d[1] >= int(p["reach_procs"]) for d, p in zip(drops, parts)):
            v.ok("(a) every REACH_DROPPED is 0 (%d lines)" % (sum(d[1] for d in drops) - (n - 1)), True)
        else:
            v.bad("(a) REACH_DROPPED totals %s over the parts" % drops)
        if slice_mode:
            print("rows: a --units slice is not the whole population: (b), (c), (e) not judged")
        else:
            zero = " ".join("%s/%s" % k for k, c in sorted(total.items()) if c == 0 and k[0] != "fd")
            if not zero:
                v.ok("(b) every row chosen >= 1 over the tier", True)
            else:
                v.bad("(b) rows never chosen: %s" % zero)
            if len(total) >= floor_rows:
                v.ok("(c) %d distinct (table,row) pairs >= floor %d" % (len(total), floor_rows), True)
            else:
                v.bad("(c) %d distinct (table,row) pairs < floor %d" % (len(total), floor_rows))
            if a.row_floors:
                under, seen_floor = [], 0
                with open(a.row_floors) as f:
                    for ln in f:
                        c = ln.rstrip("\n").split("\t")
                        if ln.startswith("#") or len(c) < 4 or not re.fullmatch(r"[0-9]+", c[3]):
                            continue
                        seen_floor += 1
                        k = (c[0], c[1])
                        if k not in total or total[k] < int(c[3]):
                            under.append("%s/%s(%s<%s)" % (k[0], k[1], total.get(k, "absent"), c[3]))
                if not seen_floor:
                    under.append("no-numeric-g2-floor")
                if not under:
                    v.ok("(e) every row meets its g2_floor in %s" % a.row_floors, True)
                else:
                    v.bad("(e) rows under their g2_floor: %s" % " ".join(under))

    # P3 totals and verdicts
    rep_fail = parts[0]["replicated_failed"]
    if any(p["replicated_failed"] != rep_fail for p in parts):
        v.bad("the parts disagree on the replicated (prelude + section 5) failures: the generator is not deterministic")
    pre_pass = {p["prelude_passed"] for p in parts}
    if len(pre_pass) != 1:
        v.bad("the parts disagree on the prelude's passed count: %s" % sorted(pre_pass))
    tp = sum(p["passed"] for p in parts) - (n - 1) * int(parts[0]["prelude_passed"]) + v.passed
    tf = sum(p["failed"] for p in parts) - (n - 1) * int(rep_fail) + v.failed
    for i, p in enumerate(parts):
        w = p.get("wall", "?")
        print("part %s: wall %ss, passed %d failed %d, units %s" % (
            p["part"].split(" ")[0], w, p["passed"], p["failed"], " ".join("%s:%ds" % x for x in p["units"])))
        if p["failed"]:
            v.bad("part %s reports checks failed: %d" % (p["part"].split(" ")[0], p["failed"]))
    print("checks passed: %d" % tp)
    print("checks failed: %d" % tf)
    return 0 if v.failed == 0 and tf == 0 else 1


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("list", "assign", "gather"):
        sp = sub.add_parser(name)
        sp.add_argument("--table", required=True)
        if name != "list":
            sp.add_argument("--units")
        if name == "assign":
            sp.add_argument("--part")
        if name == "gather":
            sp.add_argument("--row-floors")
            sp.add_argument("--unsplit-units")
            sp.add_argument("logs", nargs="+")
    a = ap.parse_args()
    if a.cmd == "list":
        cmd_list(a)
    elif a.cmd == "assign":
        cmd_assign(a)
    else:
        sys.exit(cmd_gather(a))


if __name__ == "__main__":
    main()
