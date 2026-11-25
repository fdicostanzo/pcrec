#!/usr/bin/env python3
"""tests/core/memgate/test_verdicts.py -- the CONTROL for memgate's verdicts (review r104: MEMGATE-1, -2, -3).

memgate decides pass/fail from numbers two built sides print; a gate that reads green on a broken pair of
sides is the failure this file plants. It drives memgate's mode functions with FAKE sides (the driver and
bisection calls monkeypatched) and asserts the verdict line AND the exit status:
  - both sides ERR on a rung            -> must not read IDENTICAL (MEMGATE-1)
  - one side ERR                        -> MOVED
  - a compile/refuse flip, equal peak, a threshold unfound on a side -> MOVED, not LAYOUT (MEMGATE-3)
  - the same flip with both thresholds  -> LAYOUT (the positive control: the fix does not break the rule)
  - a refusing-message change           -> MOVED
  - identical sides                     -> IDENTICAL, exit 0
  - peak over its bound / instr over its band -> STOP and a nonzero exit (MEMGATE-2)
Run: python3 -I tests/core/memgate/test_verdicts.py   (no build, no compile; <1 s). Prints `ok N/N` or the failures.
"""
import argparse, contextlib, importlib.util, io, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("memgate", os.path.join(HERE, "memgate.py"))
mg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mg)

A, B = "/fake/A", "/fake/B"
ITEM = ("cellx", 1 << 20, 0, "all", 0, "/fake/pat", 0)


def ns(**kw):
    d = dict(A=A, B=B, out="/var/empty", shard="", jobs=1, bound=None, band=1.02, p95=1.01)
    d.update(kw)
    return argparse.Namespace(**d)


def run_rungs(outs, peaks=(5, 5), need=(4096, 8192)):
    """One rung item; OUTS = (A outcome, B outcome); PEAKS = requested peaks; NEED = (A, B) thresholds."""
    saves = (mg.rung_one, mg.drv_one, mg.rung_need)
    mg.rung_one = lambda sides: (lambda item: (item[0], item[1], {A: outs[0], B: outs[1]}))
    mg.drv_one = lambda binname, sides: (lambda item: (item[0], {A: (peaks[0],), B: (peaks[1],)}))
    mg.rung_need = lambda side, item, cap, compiled: need[0] if side == A else need[1]
    buf = io.StringIO()
    d = mg.os.path.join("/var/tmp", "pcrec-%s" % os.environ.get("USER", "x"), "scratch", "memgate_ctl")
    os.makedirs(d, exist_ok=True)
    try:
        with contextlib.redirect_stdout(buf):
            rc = mg.mode_rungs(ns(out=d), [ITEM])
    finally:
        mg.rung_one, mg.drv_one, mg.rung_need = saves
    verdict = [l for l in buf.getvalue().splitlines() if l.startswith("rungs: VERDICT")]
    return (verdict[-1].split()[-1] if verdict else "NONE"), rc


def run_peak(delta, bound):
    saves = mg.drv_one
    mg.drv_one = lambda binname, sides: (lambda item: (item[0], {A: (100, 0, 0, 0, 0, 0), B: (100 + delta, 0, 0, 0, 0, 0)}))
    buf = io.StringIO()
    d = os.path.join("/var/tmp", "pcrec-%s" % os.environ.get("USER", "x"), "scratch", "memgate_ctl")
    os.makedirs(d, exist_ok=True)
    try:
        with contextlib.redirect_stdout(buf):
            rc = mg.mode_peak(ns(out=d, bound=bound), [("k", 0, "all", 0, "/fake/pat")])
    finally:
        mg.drv_one = saves
    return rc


def run_instr(ratio):
    saves = mg.drv_one
    mg.drv_one = lambda binname, sides: (lambda item: (item[0], {A: (1000,), B: (int(1000 * ratio),)}))
    buf = io.StringIO()
    d = os.path.join("/var/tmp", "pcrec-%s" % os.environ.get("USER", "x"), "scratch", "memgate_ctl")
    os.makedirs(d, exist_ok=True)
    try:
        with contextlib.redirect_stdout(buf):
            rc = mg.mode_instr(ns(out=d), [("k", 0, "all", 0, "/fake/pat")])
    finally:
        mg.drv_one = saves
    return rc


fails, n = [], 0


def check(name, got, want):
    global n
    n += 1
    if not want(got):
        fails.append("%s: got %r" % (name, got))


ok = lambda rc: not rc
bad = lambda rc: bool(rc)
V = lambda v, good: (lambda g: g[0] == v and (ok(g[1]) if good else bad(g[1])))

check("identical sides", run_rungs(("compiled", "compiled")), V("IDENTICAL", True))
check("both sides ERR (MEMGATE-1)", run_rungs(("ERR rc=1", "ERR rc=1")), V("MOVED", False))
check("one side ERR", run_rungs(("compiled", "ERR rc=1")), V("MOVED", False))
check("message change", run_rungs(("refused:a", "refused:b")), V("MOVED", False))
check("layout flip, both thresholds", run_rungs(("compiled", "refused:m")), V("LAYOUT", True))
check("flip, peak changed", run_rungs(("compiled", "refused:m"), peaks=(5, 6)), V("MOVED", False))
check("flip, no threshold on the refusing side (MEMGATE-3)",
      run_rungs(("compiled", "refused:m"), need=(4096, None)), V("MOVED", False))
check("flip, no threshold on the compiling side (MEMGATE-3)",
      run_rungs(("compiled", "refused:m"), need=(None, 4096)), V("MOVED", False))
check("peak within bound exits 0", run_peak(0, 0), ok)
check("peak over bound exits nonzero (MEMGATE-2)", run_peak(8, 0), bad)
check("instr within band exits 0", run_instr(1.0), ok)
check("instr over band exits nonzero (MEMGATE-2)", run_instr(1.5), bad)

if fails:
    print("test_verdicts: %d of %d FAILED" % (len(fails), n))
    for f in fails:
        print("  FAIL " + f)
    sys.exit(1)
print("test_verdicts: ok %d/%d" % (n, n))
