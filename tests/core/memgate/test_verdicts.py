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
Run: python3 -I tests/core/memgate/test_verdicts.py   (builds the inject library incrementally for the MG_ENC behaviour check: ~2 s warm, longer cold). Prints `ok N/N` or the failures.
"""
import argparse, contextlib, importlib.util, io, os, subprocess, sys

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
    run_peak.out = buf.getvalue()
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

ia, pa = mg.drv_argv("/s", "mg_instr"), mg.drv_argv("/s", "mg_peak")
check("instr driver runs with ASLR off (setarch -R)", ia, lambda c: c[0] == "setarch" and "-R" in c and c[-1] == "/s/mg_instr")
check("peak driver is run directly", pa, lambda c: c == ["/s/mg_peak"])

# SCOPE-4 population levers: MG_ENG sets the corpus engine, MG_ENC is validated (mg_drv.c reads it), both read as ints
def with_env(**kw):
    saved = {k: os.environ.get(k) for k in ("MG_ENC", "MG_ENG")}
    for k in saved:
        os.environ.pop(k, None)
    os.environ.update(kw)
    try:
        return mg.levers()
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v

check("levers unset read 0,0 (the default population)", with_env(), lambda g: g == (0, 0))
check("levers MG_ENC=1 MG_ENG=2", with_env(MG_ENC="1", MG_ENG="2"), lambda g: g == (1, 2))
try:
    with_env(MG_ENG="vm")
    refused = False
except SystemExit:
    refused = True
check("a non-integer lever is refused, not read as 0", refused, lambda g: g is True)
# BEHAVIOUR, not text (r108 C): population() must hand MG_ENG to the corpus items, and the built mg_peak driver must
# honour MG_ENC. Each check fails on its own mutation (levers()[1] ignored; getenv moved above pcrec_default_options;
# the getenv turned into a comment): a grep of mg_drv.c shares its source with what it vouches for.
class FakeRG:
    LADDER = ()
    build_cells = staticmethod(lambda *_: [])
    limit = staticmethod(lambda _n: 0)


def population_engines(**env):
    saved = {k: os.environ.get(k) for k in ("MG_ENC", "MG_ENG", "PCREC")}
    for k in saved:
        os.environ.pop(k, None)
    os.environ.update(env)
    os.environ["PCREC"] = "/fake/pcrec"
    fake_es = type(sys)("emit_sweep")
    fake_es.enumerate_corpus = lambda pcrec, tree, n: [("f", "k", "a+b"), ("f", "k", "c+d")]
    old = (mg.load_growth, sys.modules.get("emit_sweep"))
    mg.load_growth = lambda side: ("/fake/tree", FakeRG)
    sys.modules["emit_sweep"] = fake_es
    d = os.path.join("/var/tmp", "pcrec-%s" % os.environ.get("USER", "x"), "scratch", "memgate_ctl")
    os.makedirs(os.path.join(d, "pat"), exist_ok=True)
    try:
        return [it[3] for it in mg.population(ns(out=d, mode="peak", limit=0))]
    finally:
        mg.load_growth = old[0]
        if old[1] is None:
            sys.modules.pop("emit_sweep", None)
        else:
            sys.modules["emit_sweep"] = old[1]
        for k, v in saved.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v


check("population(): corpus items carry MG_ENG=2 as their engine", population_engines(MG_ENG="2"), lambda g: g == [2, 2])
check("population(): unset MG_ENG leaves the corpus on engine 0", population_engines(), lambda g: g == [0, 0])


def peak_lines(env_enc):
    """Build the mg_peak driver here (the inject library, incremental) and compile `x\\p{L}y` under MG_ENG=2 once."""
    root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    d = os.path.join("/var/tmp", "pcrec-%s" % os.environ.get("USER", "x"), "scratch", "memgate_ctl", "levers_build")
    os.makedirs(d, exist_ok=True)
    lib = os.path.join(d, "inject", "libpcrec.a")
    r = subprocess.run(["make", "-C", root, "--no-print-directory", "-j8", "BUILD_DIR=" + os.path.join(d, "inject"),
                        "CFLAGS=-O1 -g -include %s/tests/core/alloc_inject.h" % root, lib],
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if r.returncode:
        return "BUILD-FAIL " + r.stderr.decode()[-200:]
    exe = os.path.join(d, "mg_peak")
    r = subprocess.run(["gcc", "-O2", "-std=gnu11", "-DMG_PEAK", "-I" + os.path.join(root, "lib"), "-I" + os.path.join(root, "src"),
                        "-o", exe, os.path.join(HERE, "mg_drv.c"), lib, "-lpthread", "-lm",
                        "-Wl,--wrap=pcrec_arena_alloc", "-Wl,--wrap=pcrec_arena_free"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if r.returncode:
        return "DRV-FAIL " + r.stderr.decode()[-200:]
    pf = os.path.join(d, "pat.txt")
    open(pf, "w").write("x\\p{L}y")
    env = dict(os.environ)
    env.pop("MG_ENC", None)
    if env_enc is not None:
        env["MG_ENC"] = env_enc
    r = subprocess.run([exe], input="0\t-\t2\t%s\n" % pf, capture_output=True, text=True, env=env)
    return r.stdout.strip()


off, on = peak_lines(None), peak_lines("1")
check("mg_peak driver: MG_ENC=1 changes the compile (peak line differs from unset)", (off, on),
      lambda g: g[0] and g[1] and not g[0].startswith(("BUILD-FAIL", "DRV-FAIL")) and not g[1].startswith(("BUILD-FAIL", "DRV-FAIL"))
      and g[0] != g[1])
run_peak(0, 0)
check("peak prints the levers it ran under", run_peak.out, lambda g: "peak: levers MG_ENC=" in g)

if fails:
    print("test_verdicts: %d of %d FAILED" % (len(fails), n))
    for f in fails:
        print("  FAIL " + f)
    sys.exit(1)
print("test_verdicts: ok %d/%d" % (n, n))
