#!/usr/bin/env python3
"""[MEMFN-ROWCON] N2: parse MFTRACE output (memfn/docs/trace_format.md) and
render the census (docs/design/memfn/row_contracts.md rev 4.1, §5's N2 row).

Library (n2_census.py imports it):
  parse_trace(stderr_bytes) -> Trace     one compile's records
  Agg                                    counters; add(), merge(), save(), load()
  render(agg, meta) -> markdown

CLI:  n2_report.py RESULTS_DIR [-o n2_results.md] [--floors ROW_FLOORS.tsv [--propose]]
      merges RESULTS_DIR/arm_*.json (one Agg per arm, written by the driver)
      and writes the tables. Prints `would_decline=K` on its last line.
      --floors (N4) also holds every row's CHOSEN count to its pcrec_floor
      (tests/memfn/row_floors.tsv) and every non-`pcrec` row of rows.tsv (read
      beside it) to 0, and prints `floor_fail=F floor_placeholder=P
      reason_stale=R reach_dropped=D` before the last line. Floors apply only
      to a FULL census (no --limit, no --pattern, every arm run); anything
      less prints `floors=NOT-APPLIED`. --propose prints, per row, the
      floor(0.9 x chosen) a human copies into the floor file.

A would-decline is an END record with would_decline=1 (the WARN gate declined
the CHOSEN row). A "pcrec site" is one selection: (table, phase, chosen row,
and for the arms table the site's form/op/handoff classes from its SEL line).
"""
import collections
import json
import os
import sys

WITNESS_N = 3
SEP = "\t"


class Trace:
    """One compile's records. ends: one dict per END; reach_chosen /
    reach_cell: the REACH lines (this process only)."""
    def __init__(self):
        self.ends = []
        self.reach_chosen = collections.Counter()
        self.reach_cell = collections.Counter()
        self.chosen_rows = []      # (table, row) chosen at define/run, first-seen order
        self.reach_dropped = 0     # REACH_DROPPED: selections the counters could not hold


def _kv(tokens):
    d = {}
    for t in tokens:
        k, _, v = t.partition("=")
        d[k] = v
    return d


def parse_fields(s):
    """`-` or `name:R1:UNSTATED,name:R2:CLASS,...` -> [(name, rule, class)]."""
    if s in ("", "-"):
        return []
    out = []
    for f in s.split(","):
        p = f.split(":")
        if len(p) == 3:
            out.append((p[0], p[1], p[2]))
    return out


def parse_trace(err):
    if isinstance(err, bytes):
        err = err.decode("utf-8", "replace")
    tr = Trace()
    sel = {}
    for ln in err.splitlines():
        if not ln.startswith("MFTRACE "):
            continue
        toks = ln.split()
        kind = toks[1]
        d = _kv(toks[2:])
        if kind == "SEL":
            sel = d
        elif kind == "END":
            what = {k: sel.get(k, "") for k in ("form", "op", "handoff", "run")}
            if d.get("table") == "arms":
                shape = "form=%s op=%s handoff=%s" % (what["form"], what["op"], what["handoff"])
            else:
                shape = "run=%s" % what["run"]
            if d.get("chosen", "-") != "-" and d.get("phase") != "use":
                k = (d.get("table", "?"), d["chosen"])
                if k not in tr.chosen_rows:
                    tr.chosen_rows.append(k)
            tr.ends.append({
                "table": d.get("table", "?"), "phase": d.get("phase", "?"),
                "chosen": d.get("chosen", "-"), "wd": d.get("would_decline", "-"),
                "shape": shape, "fields": parse_fields(d.get("fields", "-"))})
        elif kind == "REACH_DROPPED":
            tr.reach_dropped += int(d.get("n", "0"))
        elif kind == "REACH":
            if "field" in d:
                tr.reach_cell[(d["table"], d["row"], d["field"], d["class"])] += int(d["n"])
            else:
                tr.reach_chosen[(d["table"], d["row"])] += int(d["chosen"])
    return tr


def fkey(fields):
    return ",".join("%s:%s:%s" % f for f in fields)


class Agg:
    def __init__(self):
        self.compiles = collections.Counter()      # (arm, "attempted"|"ok"|"refused"|"timeout")
        self.ends = collections.Counter()          # (table, phase, chosen)  every END with a row
        self.noend = 0                             # END with no chosen row (kit refused the site)
        self.wd = collections.Counter()            # (table, phase, chosen, shape, fkey)
        self.wd_arms = collections.defaultdict(collections.Counter)   # same key -> arm -> n
        self.wd_wit = collections.defaultdict(list)                  # same key -> [witness]
        self.reach_chosen = collections.Counter()  # (table, row)
        self.reach_cell = collections.Counter()    # (table, row, field, class)
        self.reach_wit = collections.defaultdict(list)  # (table, row) -> [witness] (N4)
        self.reach_dropped = 0                     # REACH_DROPPED totals (N4: must be 0)

    def add(self, arm, stream, src, pattern, tr):
        for e in tr.ends:
            if e["chosen"] == "-":
                self.noend += 1
                continue
            self.ends[(e["table"], e["phase"], e["chosen"])] += 1
            if e["wd"] == "1":
                k = (e["table"], e["phase"], e["chosen"], e["shape"], fkey(e["fields"]))
                self.wd[k] += 1
                self.wd_arms[k][arm] += 1
                w = [arm, stream, src, str(pattern)[:120]]
                lst = self.wd_wit[k]
                if w not in lst and len(lst) < WITNESS_N * 4:
                    lst.append(w)
                    lst.sort()
                    del lst[WITNESS_N:]
        self.reach_chosen.update(tr.reach_chosen)
        self.reach_cell.update(tr.reach_cell)
        self.reach_dropped += tr.reach_dropped
        for k in tr.chosen_rows:
            lst = self.reach_wit[k]
            if len(lst) < WITNESS_N:
                w = [arm, stream, src, str(pattern)[:120]]
                if w not in lst:
                    lst.append(w)

    def count(self, arm, what, n=1):
        self.compiles[(arm, what)] += n

    def merge(self, o):
        self.compiles.update(o.compiles)
        self.ends.update(o.ends)
        self.noend += o.noend
        self.wd.update(o.wd)
        for k, c in o.wd_arms.items():
            self.wd_arms[k].update(c)
        for k, ws in o.wd_wit.items():
            lst = self.wd_wit[k]
            for w in ws:
                if w not in lst:
                    lst.append(w)
            lst.sort()
            del lst[WITNESS_N:]
        self.reach_chosen.update(o.reach_chosen)
        self.reach_cell.update(o.reach_cell)
        self.reach_dropped += o.reach_dropped
        for k, ws in o.reach_wit.items():
            lst = self.reach_wit[k]
            for w in ws:
                if w not in lst:
                    lst.append(w)
            lst.sort()
            del lst[WITNESS_N:]

    def would_decline_total(self):
        return sum(self.wd.values())

    def save(self, path):
        j = {"compiles": [[SEP.join(k), v] for k, v in self.compiles.items()],
             "ends": [[SEP.join(k), v] for k, v in self.ends.items()],
             "noend": self.noend,
             "wd": [[SEP.join(k), v, dict(self.wd_arms[k]), self.wd_wit[k]] for k, v in self.wd.items()],
             "reach_chosen": [[SEP.join(k), v] for k, v in self.reach_chosen.items()],
             "reach_cell": [[SEP.join(k), v] for k, v in self.reach_cell.items()],
             "reach_wit": [[SEP.join(k), v] for k, v in self.reach_wit.items()],
             "reach_dropped": self.reach_dropped}
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(j, f)
        os.replace(tmp, path)

    @staticmethod
    def load(path):
        with open(path) as f:
            j = json.load(f)
        a = Agg()
        for k, v in j["compiles"]:
            a.compiles[tuple(k.split(SEP))] = v
        for k, v in j["ends"]:
            a.ends[tuple(k.split(SEP))] = v
        a.noend = j["noend"]
        for k, v, arms, wit in j["wd"]:
            k = tuple(k.split(SEP))
            a.wd[k] = v
            a.wd_arms[k].update(arms)
            a.wd_wit[k] = wit
        for k, v in j["reach_chosen"]:
            a.reach_chosen[tuple(k.split(SEP))] = v
        for k, v in j["reach_cell"]:
            a.reach_cell[tuple(k.split(SEP))] = v
        for k, v in j.get("reach_wit", []):        # absent in pre-N4 arm files
            a.reach_wit[tuple(k.split(SEP))] = v
        a.reach_dropped = j.get("reach_dropped", 0)
        return a


def _md(rows, head):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |" for r in rows]
    return out


def _need(f):
    """One failing field -> what R-6 asks of the pcrec site."""
    name, rule, cls = f
    if rule == "R1":
        return "state `%s`" % name
    return "`%s` is %s: the row does not serve it (state a class it serves)" % (name, cls)


def render(agg, meta=None):
    meta = meta or {}
    L = ["# N2 census -- [MEMFN-ROWCON] would-decline verdicts on pcrec sites", ""]
    for k, v in meta.items():
        L.append("- %s: %s" % (k, v))
    L.append("")

    arms = sorted({a for a, _ in agg.compiles})
    tot = collections.Counter()
    for (a, w), n in agg.compiles.items():
        tot[w] += n
    sites = sum(agg.ends.values())
    wdn = agg.would_decline_total()
    L += ["## 1. Population", ""]
    L += _md([["arms", len(arms)], ["compiles attempted", tot["attempted"]],
              ["compiled", tot["ok"]], ["refused (rc != 0)", tot["refused"]],
              ["timeouts", tot["timeout"]],
              ["sites traced (END with a chosen row)", sites],
              ["selections with no row (kit refused the site)", agg.noend],
              ["would-decline selections", wdn],
              ["selections the reach counters dropped (REACH_DROPPED; must be 0)", agg.reach_dropped]],
             ["quantity", "count"])
    L += ["", "Sites traced by table, phase and chosen row:", ""]
    L += _md([[t, p, r, n] for (t, p, r), n in sorted(agg.ends.items())],
             ["table", "phase", "chosen row", "selections"])

    L += ["", "## 2. Would-decline verdicts, one line per (row, phase, site shape, failing fields)", ""]
    if not agg.wd:
        L += ["NONE.", ""]
    rows = []
    for k, n in sorted(agg.wd.items(), key=lambda kv: (-kv[1], kv[0])):
        t, ph, row, shape, fk = k
        arms_hit = agg.wd_arms[k]
        wit = "; ".join("[%s] %s %s: `%s`" % tuple(w) for w in agg.wd_wit[k])
        rows.append([t, row, ph, shape, fk, n, "%d/%d" % (len(arms_hit), len(arms)), wit])
    L += _md(rows, ["table", "row", "phase", "site shape", "failing fields (name:rule:class)",
                    "count", "arms seen", "witnesses [arm] stream src: pattern"])

    L += ["", "## 3. R-6 table: per pcrec site kind, the field to state and the class it needs", ""]
    L += ["Rule 1 (R1): the row uses the field and the site left it unstated -> state it.",
          "Rule 2 (R2): the field is stated with a class the row does not serve.", ""]
    r6 = {}
    for (t, ph, row, shape, fk), n in agg.wd.items():
        for f in (x.split(":") for x in fk.split(",")):
            k = (t, row, shape, f[0], f[1], f[2])
            r6.setdefault(k, [0, set()])
            r6[k][0] += n
            r6[k][1].add(ph)
    rows = [[t, row, shape, name, rule, cls, "/".join(sorted(phs)), n, _need((name, rule, cls))]
            for (t, row, shape, name, rule, cls), (n, phs) in sorted(r6.items())]
    L += _md(rows, ["table", "row", "site shape", "field", "rule", "observed class",
                    "phases", "count", "R-6 obligation"])

    L += ["", "## 4. Reach: selections per chosen row (define + run phases), with witnesses", ""]
    L += _md([[t, r, n, "; ".join("[%s] %s %s: `%s`" % tuple(w) for w in sorted(agg.reach_wit.get((t, r), [])))]
              for (t, r), n in sorted(agg.reach_chosen.items())],
             ["table", "row", "chosen", "witnesses [arm] stream src: pattern"])
    L += ["", "## 5. Reach: per row x field x class (nonzero cells)", ""]
    L += _md([[t, r, f, c, n] for (t, r, f, c), n in sorted(agg.reach_cell.items())],
             ["table", "row", "field", "class", "n"])
    L += ["", "## 6. Per-arm compile counts", ""]
    by = collections.defaultdict(collections.Counter)
    for (a, w), n in agg.compiles.items():
        by[a][w] = n
    L += _md([[a, by[a]["attempted"], by[a]["ok"], by[a]["refused"], by[a]["timeout"]] for a in arms],
             ["arm", "attempted", "ok", "refused", "timeout"])
    return "\n".join(L) + "\n"


def read_tsv(path, ncol):
    """Data lines of a `#`-commented TAB-separated file, each exactly ncol
    columns (a short or long line is an error, never padded)."""
    rows = []
    with open(path) as f:
        for i, ln in enumerate(f, 1):
            ln = ln.rstrip("\n")
            if not ln or ln.startswith("#"):
                continue
            c = ln.split("\t")
            if len(c) != ncol:
                sys.exit("n2_report: %s:%d has %d columns, not %d" % (path, i, len(c), ncol))
            rows.append(c)
    return rows


def floors_verdict(agg, meta, floors_path, propose):
    """N4: the per-row CHOSEN floors (pcrec column) and the closed-reason
    rows' zero. Returns the markdown lines and the summary line."""
    rows = read_tsv(os.path.join(os.path.dirname(floors_path), "rows.tsv"), 9)
    reach = {(r[0], r[1]): r[2] for r in rows}
    fl = {(r[0], r[1]): r[2] for r in read_tsv(floors_path, 4)}
    full = (meta.get("limit", 0) == 0 and meta.get("explicit patterns", 0) == 0
            and meta.get("arms run") == meta.get("arms in table"))
    L = ["", "## 7. Floors (N4): per-row CHOSEN against tests/memfn/row_floors.tsv", ""]
    if not full:
        L += ["NOT APPLIED: a partial census (limit %s, explicit patterns %s, arms run %s of %s)."
              % (meta.get("limit"), meta.get("explicit patterns"), meta.get("arms run"),
                 meta.get("arms in table")), ""]
    fail = ph = stale = 0
    out = []
    for k in sorted(set(fl) | set(reach) | set(agg.reach_chosen)):
        n = agg.reach_chosen.get(k, 0)
        f, why = fl.get(k), reach.get(k)
        if why is None or f is None:
            v = "NOT IN %s" % ("rows.tsv" if why is None else "row_floors.tsv")
            fail += 1
        elif why != "pcrec":
            v = "ok (0, %s)" % why if n == 0 else "STALE REASON: %s, chosen %d" % (why, n)
            stale += n != 0
        elif n == 0:
            v = "UNREACHED: reach is pcrec, chosen 0"
            fail += 1
        elif f == "PLACEHOLDER":
            v = "PLACEHOLDER"
            ph += 1
        elif not f.isdigit():
            v = "BAD FLOOR %r" % f
            fail += 1
        else:
            v = "ok" if n >= int(f) else "BELOW FLOOR"
            fail += n < int(f)
        prop = max(1, n * 9 // 10) if why == "pcrec" and n else "-"
        out.append([k[0], k[1], why or "-", n, f or "-", prop, v])
        if propose:
            print("propose\t%s\t%s\t%s" % (k[0], k[1], prop))
    L += _md(out, ["table", "row", "reach", "chosen", "floor", "floor(0.9 x chosen)", "verdict"])
    if not full:
        return L, "floors=NOT-APPLIED reason_stale=%d reach_dropped=%d" % (stale, agg.reach_dropped)
    return L, ("floor_fail=%d floor_placeholder=%d reason_stale=%d reach_dropped=%d"
               % (fail, ph, stale, agg.reach_dropped))


def main(argv):
    if not argv:
        sys.exit(__doc__)
    d = argv[0]
    out = argv[argv.index("-o") + 1] if "-o" in argv else os.path.join(d, "n2_results.md")
    floors = argv[argv.index("--floors") + 1] if "--floors" in argv else None
    agg = Agg()
    n = 0
    for fn in sorted(os.listdir(d)):
        if fn.startswith("arm_") and fn.endswith(".json"):
            agg.merge(Agg.load(os.path.join(d, fn)))
            n += 1
    if n == 0:
        sys.exit("n2_report: no arm_*.json in %s" % d)
    meta = {"results dir": d, "arm files merged": n}
    mp = os.path.join(d, "meta.json")
    if os.path.exists(mp):
        meta.update(json.load(open(mp)))
    text = render(agg, meta)
    summary = None
    if floors:
        lines, summary = floors_verdict(agg, meta, floors, "--propose" in argv)
        text += "\n".join(lines) + "\n"
    with open(out, "w") as f:
        f.write(text)
    print("n2_report: wrote %s" % out)
    if summary:
        print(summary)
    print("would_decline=%d" % agg.would_decline_total())


if __name__ == "__main__":
    main(sys.argv[1:])
