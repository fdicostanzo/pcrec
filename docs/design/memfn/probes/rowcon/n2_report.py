#!/usr/bin/env python3
"""[MEMFN-ROWCON] N2: parse MFTRACE output (memfn/docs/trace_format.md) and
render the census (docs/design/memfn/row_contracts.md rev 4.1, §5's N2 row).

Library (n2_census.py imports it):
  parse_trace(stderr_bytes) -> Trace     one compile's records
  Agg                                    counters; add(), merge(), save(), load()
  render(agg, meta) -> markdown

CLI:  n2_report.py RESULTS_DIR [-o n2_results.md]
      merges RESULTS_DIR/arm_*.json (one Agg per arm, written by the driver)
      and writes the tables. Prints `would_decline=K` on its last line.

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
            tr.ends.append({
                "table": d.get("table", "?"), "phase": d.get("phase", "?"),
                "chosen": d.get("chosen", "-"), "wd": d.get("would_decline", "-"),
                "shape": shape, "fields": parse_fields(d.get("fields", "-"))})
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

    def would_decline_total(self):
        return sum(self.wd.values())

    def save(self, path):
        j = {"compiles": [[SEP.join(k), v] for k, v in self.compiles.items()],
             "ends": [[SEP.join(k), v] for k, v in self.ends.items()],
             "noend": self.noend,
             "wd": [[SEP.join(k), v, dict(self.wd_arms[k]), self.wd_wit[k]] for k, v in self.wd.items()],
             "reach_chosen": [[SEP.join(k), v] for k, v in self.reach_chosen.items()],
             "reach_cell": [[SEP.join(k), v] for k, v in self.reach_cell.items()]}
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
              ["would-decline selections", wdn]], ["quantity", "count"])
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

    L += ["", "## 4. Reach: selections per chosen row (define + run phases)", ""]
    L += _md([[t, r, n] for (t, r), n in sorted(agg.reach_chosen.items())],
             ["table", "row", "chosen"])
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


def main(argv):
    if not argv:
        sys.exit(__doc__)
    d = argv[0]
    out = argv[argv.index("-o") + 1] if "-o" in argv else os.path.join(d, "n2_results.md")
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
    with open(out, "w") as f:
        f.write(render(agg, meta))
    print("n2_report: wrote %s" % out)
    print("would_decline=%d" % agg.would_decline_total())


if __name__ == "__main__":
    main(sys.argv[1:])
