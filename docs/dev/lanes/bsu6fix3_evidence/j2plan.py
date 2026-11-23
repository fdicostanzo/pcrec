#!/usr/bin/env python3
"""bsu6fix3: the J2 drill's input (C1, hex24, hit-dense + near-miss) through time_cells at two cards.py copies, with
arity-tolerant stubs (no exe, no clock) and a fixed run id; compares the launch plan (cell, argv per launch, in order) and
the output file byte for byte. usage: j2plan.py OLD NEW SCRATCH"""
import importlib.util, os, sys, tempfile, hashlib
OLD, NEW, SCR = sys.argv[1:4]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.argv = ["x"]
    spec.loader.exec_module(m)
    return m


def plan(m):
    calls = []
    m.prepare_cell = lambda rd, c, n, *a, **k: [["exe|%s|v%d" % ("/".join(c), v)] for v in range(m.POOL_SIZE)]
    m._exec = lambda argv, c, env=None: calls.append((tuple(c), tuple(argv))) or "t %d\n" % (len(calls) + 1)
    cl = [c for c in m.cells(cards=("C1",)) if c[1] == "hex24" and c[3] in ("hit-dense", "near-miss")]
    d = tempfile.mkdtemp(dir=SCR)
    open(os.path.join(d, "run_id"), "w").write("j2plan\n")
    p = os.path.join(d, "r.tsv")
    open(p, "w").close()
    m.time_cells(d, cl, p)
    out = open(p, "rb").read()
    st = sorted({ln.split(b"\t")[5].decode() for ln in out.splitlines() if not ln.startswith(b"#")})
    return cl, calls, out, st


a, b = plan(load("old", OLD)), plan(load("new", NEW))
print("cells: %d / %d, same: %s" % (len(a[0]), len(b[0]), a[0] == b[0]))
print("launches: %d / %d; launch plan (cell, argv incl. the drawn variant, in order) same: %s"
      % (len(a[1]), len(b[1]), a[1] == b[1]))
print("output file: %d / %d bytes, row statuses %s / %s, same bytes: %s (sha %s)"
      % (len(a[2]), len(b[2]), a[3], b[3], a[2] == b[2], hashlib.sha256(b[2]).hexdigest()[:16]))
print("launch plan sha %s" % hashlib.sha256(repr(b[1]).encode()).hexdigest()[:16])
ok = a[:3] == b[:3] and bool(b[1]) and b[3] == ["ok"]
print("j2plan: %s" % ("SAME" if ok else "DIFFERS"))
sys.exit(0 if ok else 1)
