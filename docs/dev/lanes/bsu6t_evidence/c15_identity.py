#!/usr/bin/env python3
"""bsu6t R-1 (a): with the CPU-quiet control unarmed, C1-C5's time_cells path is unchanged.

Loads cards.py at the base (BASE_FILE, `git show 09c206cb0:memfn/tests/span_forms/cards.py`) and at the lane (NEW_FILE) as
two modules and compares, over every C1-C5 + AA cell (cells() of STEP1 and STEP2B at h* in GRID):
  1. the cell list and the launch order (launch_order);
  2. every pool (pool_variants under the arm's salt vs arm_pool at retime 0) for 400 text keys x every layer x every arm;
  3. the per-launch draws (launch_variant under the default salt, the results file's name);
  4. time_cells' OUTPUT FILE, byte for byte, over STEP1 (with and without --with-approx) and STEP2B, with prepare_cell and
     _exec stubbed (no exe, no clock: a deterministic `TIME` line per argv and call; one stub cell raises GateFail, one a
     void, one a void on its 3rd launch), so every branch of time_cells runs.
Prints one line per check and `c15 identity: N checks, M differ`; exit 1 if any differ."""
import importlib.util, os, sys, tempfile, hashlib

BASE_FILE, NEW_FILE, SCRATCH = sys.argv[1:4]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.argv = ["x"]
    spec.loader.exec_module(m)
    return m


old, new = load("cards_old", BASE_FILE), load("cards_new", NEW_FILE)
bad, n = [], 0


def check(ok, what):
    global n
    n += 1
    print("%s  %s" % ("same" if ok else "DIFF", what))
    if not ok:
        bad.append(what)


cl_old = {h: old.cells(hstar=h, cards=old.STEP1 + old.STEP2B) for h in old.GRID}
cl_new = {h: new.cells(hstar=h, cards=new.STEP1 + new.STEP2B) for h in new.GRID}
check(cl_old == cl_new, "cell lists, STEP1 + STEP2B at every h* in GRID (%d cells at h*=64)" % len(cl_new[64]))
check(all(old.launch_order(cl_old[h]) == new.launch_order(cl_new[h]) for h in old.GRID),
      "launch order (interleaved rounds) at every h*")
check(old.launch_order(cl_old[64], False) == new.launch_order(cl_new[64], False), "launch order, arm-major control")
arms = sorted({c[2] for h in old.GRID for c in cl_old[h]})
check(all(old.pool_variants(k, old.align_variants_of(ly), old.pool_salt(a)) == new.arm_pool(k, ly, a)
          for k in ("t%d" % i for i in range(400)) for ly in old.LAYER for a in arms),
      "pools: base pool_variants == lane arm_pool(retime 0), 400 keys x %d layers x %d arms" % (len(old.LAYER), len(arms)))
check(all(old.launch_variant("rid|results.tsv", c, r) == new.launch_variant("rid|results.tsv", c, r)
          for c in cl_old[64] for r in range(old.LAUNCHES)), "launch draws (launch_variant) at the default salt")


def stub(m):
    calls = {"n": 0}

    def prep(rundir, cell, nn, *a):
        if cell[1] == "hex24" and cell[2] == "h8" and cell[3] == "random":
            raise m.GateFail("stub gate fail")
        if cell[1] == "dig24" and cell[2] == "h16" and cell[3] == "random":
            raise RuntimeError("stub void")
        return [["taskset", "-c", "15", "exe|%s|v%d" % ("/".join(cell), v)] for v in range(m.POOL_SIZE)]

    def ex(argv, cell, env=None):
        calls["n"] += 1
        if cell[1] == "hex32" and cell[2] == "h4" and cell[3] == "near-miss" and calls["n"] % 5 == 3:
            raise RuntimeError("stub launch void")
        x = int(hashlib.sha256(("%s|%d" % (argv[-1], calls["n"])).encode()).hexdigest()[:6], 16) / 1e7
        return "TIME %.6f ns/B reps 1\n" % (0.1 + x)
    m.prepare_cell, m._exec = prep, ex


stub(old)
stub(new)
for label, cl, wa in (("STEP1", cl_old[64], False), ("STEP1 --with-approx", cl_old[64], True),
                      ("STEP2B at h*=8", old.cells(hstar=8, cards=old.STEP2B), False)):
    outs = []
    for m in (old, new):
        d = tempfile.mkdtemp(dir=SCRATCH)
        open(os.path.join(d, "run_id"), "w").write("c15identity\n")
        p = os.path.join(d, "results.tsv")
        open(p, "w").close()
        m.time_cells(d, [c for c in cl if c[0] != "C4"], p, with_approx=wa)
        outs.append(open(p, "rb").read())
    check(outs[0] == outs[1], "time_cells output file, %s: %d bytes, %d rows (sha %s)" % (
        label, len(outs[1]), outs[1].count(b"\n"), hashlib.sha256(outs[1]).hexdigest()[:16]))
print("c15 identity: %d checks, %d differ" % (n, len(bad)))
sys.exit(1 if bad else 0)
