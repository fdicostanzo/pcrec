#!/usr/bin/env python3
"""bsu6fix3: the J2 drill's OWN stubs (the 3-argument prepare_cell lambda, as committed) on a cards.py copy: the row statuses
and the first void note (why the drill read '0 launches'). usage: j2stale.py CARDS SCRATCH"""
import importlib.util, os, sys, tempfile
CARDS, SCR = sys.argv[1:3]
spec = importlib.util.spec_from_file_location("cards", CARDS)
m = importlib.util.module_from_spec(spec)
sys.argv = ["x"]
spec.loader.exec_module(m)
calls = []
m.prepare_cell = lambda _rd, c, _n: list(c)
m._exec = lambda argv, c, env=None: calls.append(tuple(c)) or "t %d\n" % (len(calls) + 1)
cl = [c for c in m.cells(cards=("C1",)) if c[1] == "hex24" and c[3] in ("hit-dense", "near-miss")]
d = tempfile.mkdtemp(dir=SCR)
p = os.path.join(d, "r.tsv")
open(p, "w").close()
m.time_cells(d, cl, p)
rows = [ln.split("\t") for ln in open(p) if not ln.startswith("#")]
print("launches %d, rows %d, statuses %s" % (len(calls), len(rows), sorted({r[5] for r in rows})))
print("first non-ok note: %s" % next((r[8] for r in rows if r[5] != "ok"), "-"))
