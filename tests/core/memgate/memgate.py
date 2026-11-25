#!/usr/bin/env python3
"""tests/core/memgate/memgate.py — the per-compile MEMORY and COST gate ([ARENA-SCOPES] T1).

Made reproducible from lane k155fix's scratch tool (the manager's R-1 memory gate). Opt-in
(`make memgate`), never in `make test`. Every mode compares two BUILT SIDES compile by compile
over one population, so a side compared with itself is the noise read (design G5: two
identical base runs must print identical numbers).

  memgate.py prep SIDE_DIR (--tree TREE | --ref REF [--repo TREE]) [--jobs J]
      build one side into SIDE_DIR (nothing is written in TREE): with --ref, `git archive REF`
      is unpacked into SIDE_DIR/src first. Builds SIDE_DIR/inject (an alloc_inject.h library,
      -O1, `make alloc`'s flags), SIDE_DIR/plain (the default flags, CLI included), and links
      SIDE_DIR/mg_peak, SIDE_DIR/mg_instr (mg_drv.c, this directory) and SIDE_DIR/gdrv
      (the side's own tests/growth/growth_driver.c).
  memgate.py peak  A B OUT [--bound BYTES] [--jobs J] [--limit N] [--shard K/N]
      per-compile PEAK LIVE HEAP in REQUESTED bytes (and attempt-arena BLOCK high-water, in
      requested block size; the malloc_usable_size peak is an informational column, R-2) of side A vs side B
      over the population: every distinct corpus argv pattern (--features all) and every
      non-red growth cell uncapped (its own raise/features/engine). --bound names the unit's
      predicted per-compile delta; every compile above it is listed OVER-BOUND (a STOP).
  memgate.py rungs A B OUT [--jobs J] [--limit N] [--shard K/N]
      every non-red growth cell at every LADDER rung (RLIMIT_DATA), side A vs side B: the
      outcome (compiled / refused + message) must be IDENTICAL (R-1).
  memgate.py instr A B OUT [--jobs J] [--limit N] [--shard K/N]
      per-compile user-mode instruction count around pcrec_compile, B/A ratio: p95 and max,
      every compile over --band (default 1.02) listed OVER-BAND.

The population is read from side A's tree (corpus via scripts/emit_sweep.py's enumerator and
A's CLI, cells via A's tests/growth/run_growth.py), so both sides compile the same inputs.
Regime (docs/design/arena_scopes.md, standing question 1): REQUESTED bytes, in process, the
dev box (lane arenabuild2's ruling R-2: malloc_usable_size moved by heap history, not by bytes
asked for, read +4,048 B on one cell whose arena call sequence was identical); deterministic,
so 0 B is the expected noise.
"""
import argparse, concurrent.futures as cf, os, re, resource, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def side_tree(side):
    s = os.path.join(side, "src")
    with open(os.path.join(side, "TREE")) as f:
        return f.read().strip() or s


def sh(argv, **kw):
    r = subprocess.run(argv, **kw)
    if r.returncode != 0:
        sys.exit("memgate: failed: %s" % " ".join(argv))


def prep(a):
    side = os.path.abspath(a.side)
    os.makedirs(side, exist_ok=True)
    if a.ref:
        repo = os.path.abspath(a.repo or os.path.join(HERE, "..", "..", ".."))
        tree = os.path.join(side, "src")
        if os.path.isdir(tree):
            shutil.rmtree(tree)
        os.makedirs(tree)
        arc = subprocess.Popen(["git", "-C", repo, "archive", a.ref], stdout=subprocess.PIPE)
        sh(["tar", "-x", "-C", tree], stdin=arc.stdout)
        if arc.wait() != 0:
            sys.exit("memgate: git archive %s failed" % a.ref)
    else:
        tree = os.path.abspath(a.tree)
    with open(os.path.join(side, "TREE"), "w") as f:
        f.write(tree + "\n")
    j = "-j%d" % a.jobs
    inj = os.path.join(side, "inject")
    plain = os.path.join(side, "plain")
    sh(["make", "-C", tree, "--no-print-directory", j, "BUILD_DIR=" + inj,
        "CFLAGS=-O1 -g -include %s/tests/core/alloc_inject.h" % tree, inj + "/libpcrec.a"],
       stdout=subprocess.DEVNULL)
    sh(["make", "-C", tree, "--no-print-directory", j, "BUILD_DIR=" + plain, "all"], stdout=subprocess.DEVNULL)
    inc = ["-I" + os.path.join(tree, "lib"), "-I" + os.path.join(tree, "src")]
    drv = os.path.join(HERE, "mg_drv.c")
    sh(["gcc", "-O2", "-g", "-std=gnu11", "-Wall", "-Wextra", "-DMG_PEAK"] + inc +
       ["-o", os.path.join(side, "mg_peak"), drv, inj + "/libpcrec.a", "-lpthread", "-lm",
        "-Wl,--wrap=pcrec_arena_alloc", "-Wl,--wrap=pcrec_arena_free"])
    sh(["gcc", "-O2", "-g", "-std=gnu11", "-Wall", "-Wextra", "-DMG_INSTR"] + inc +
       ["-o", os.path.join(side, "mg_instr"), drv, plain + "/libpcrec.a", "-lpthread", "-lm"])
    sh(["gcc", "-O2", "-std=gnu11", "-Wall", "-Wextra", "-I" + os.path.join(tree, "lib"), "-o",
        os.path.join(side, "gdrv"), os.path.join(tree, "tests", "growth", "growth_driver.c"),
        plain + "/libpcrec.a", "-lpthread", "-lm"])
    print("memgate: side %s built from %s" % (side, a.ref or tree))


def load_growth(side):
    tree = side_tree(side)
    os.environ["PCREC"] = os.path.join(side, "plain", "pcrec")
    sys.path.insert(0, os.path.join(tree, "tests", "growth"))
    sys.path.insert(0, os.path.join(tree, "scripts"))
    import run_growth as rg
    return tree, rg


def patfile(outdir, key, pattern):
    p = os.path.join(outdir, "pat", re.sub(r"[^A-Za-z0-9_.@-]", "_", key)[:150] + ".pat")
    if not os.path.exists(p):
        with open(p, "wb") as f:
            f.write(pattern if isinstance(pattern, bytes) else pattern.encode("utf-8", "surrogateescape"))
    return p


def limits():
    resource.setrlimit(resource.RLIMIT_AS, (6 << 30, 6 << 30))


def run(argv, inp=None, timeout=900):
    try:
        r = subprocess.run(argv, input=inp, capture_output=True, text=True, errors="replace",
                           timeout=timeout, preexec_fn=limits)
        return r.returncode, r.stdout
    except subprocess.TimeoutExpired:
        return "TIMEOUT", ""


def population(a):
    """(key, raise, features, engine, patfile) for every compile, from side A's tree."""
    tree, rg = load_growth(a.A)
    cs = [c for c in rg.build_cells(rg.limit("PCREC_COMPILE_STACK_BUDGET"), rg.limit("PCREC_MAX_GROUP_DEPTH"))
          if not c.red]   # a red cell is a known runaway/crash: not a memory question
    items = []
    if a.mode in ("peak", "instr"):
        import emit_sweep as es
        seen = set()
        for f, kind, pat in es.enumerate_corpus(os.environ["PCREC"], tree, 30):
            if pat in seen:
                continue
            seen.add(pat)
            items.append(("corpus/%d" % len(items), 0, "all", 0, patfile(a.out, "corpus_%d" % len(items), pat)))
        for c in cs:
            items.append(("cell/" + c.id, c.raise_, c.features, c.engine, patfile(a.out, "cell_" + c.id, c.pattern)))
    else:
        for c in cs:
            pf = patfile(a.out, "cell_" + c.id, c.pattern)
            for cap in rg.LADDER:
                if cap >= 2 * len(c.pattern):
                    items.append((c.id, cap, c.raise_, c.features, c.engine, pf, c.stack))
    if a.shard:
        k, n = map(int, a.shard.split("/"))
        items = items[k - 1::n]
    if a.limit:
        items = items[:a.limit]
    return items


def drv_one(binname, sides):
    def one(item):
        key, raise_, feat, eng, pf = item
        out = {}
        for s in sides:
            rc, so = run([os.path.join(s, binname)], "%d\t%s\t%d\t%s\n" % (raise_, feat or "-", eng, pf))
            nums = (so or "").split()
            out[s] = tuple(int(x) for x in nums) if rc == 0 and nums and all(re.match(r"-?\d+$", x) for x in nums) \
                else ("ERR", rc)
        return key, out
    return one


def rung_one(sides):
    def one(item):
        key, cap, raise_, feat, eng, pf, stack = item
        out = {}
        for s in sides:
            rc, so = run([os.path.join(s, "gdrv"), "one", str(cap), str(stack), str(raise_), feat or "-", str(eng), pf])
            m = re.search(r"^rc=(-?\d+) hw=\d+(?: cpu=[\d.]+)? msg=(.*)$", so or "", re.M)
            out[s] = ("compiled" if m.group(1) == "0" else "refused:" + m.group(2)) if m and rc == 0 else "ERR rc=%s" % rc
        return key, cap, out
    return one


def pct(v, q):
    v = sorted(v)
    return v[min(len(v) - 1, int(q * (len(v) - 1) + 0.5))] if v else 0


def mode_peak(a, items):
    A, B = a.A, a.B
    rows, nerr = [], 0
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for key, out in ex.map(drv_one("mg_peak", (A, B)), items):
            x, y = out[A], out[B]
            if x[0] == "ERR" or y[0] == "ERR":
                nerr += 1
                print("ERR %s %s" % (key, out), flush=True)
                continue
            if y[2] != 0:
                print("LIVE-AFTER %s %d bytes (rc %d)" % (key, y[2], y[1]), flush=True)
            if x[1] != y[1]:
                print("RC-MOVED %s A %d B %d" % (key, x[1], y[1]), flush=True)
            rows.append((key, x[0], y[0], x[1], y[1], x[3], y[3], x[4], y[4], x[5], y[5]))
    with open(os.path.join(a.out, "peak%s.tsv" % a.shard.replace("/", "of")), "w") as fo:
        fo.write("key\tpeakA\tpeakB\trcA\trcB\tattA\tattB\tothA\tothB\tupeakA\tupeakB\n")
        for r in rows:
            fo.write("%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n" % r)
    d = [r[2] - r[1] for r in rows]
    print("peak: %d compared, %d errors; delta (B-A) min %d median %d max %d; B>A %d, equal %d, B<A %d"
          % (len(rows), nerr, min(d or [0]), pct(d, 0.5), max(d or [0]),
             sum(x > 0 for x in d), sum(x == 0 for x in d), sum(x < 0 for x in d)))
    ud = [r[10] - r[9] for r in rows]
    print("peak: usable-size peak (INFORMATIONAL, R-2) delta min %d median %d max %d; B>A %d, B<A %d"
          % (min(ud or [0]), pct(ud, 0.5), max(ud or [0]), sum(x > 0 for x in ud), sum(x < 0 for x in ud)))
    att = [r for r in rows if r[6] > r[5]]
    print("peak: attempt-arena block high-water raised on %d, lowered on %d" % (len(att), sum(r[6] < r[5] for r in rows)))
    for r in att[:20]:
        print("ATT-RAISED %s A %d B %d" % (r[0], r[5], r[6]))
    for r in sorted(rows, key=lambda r: r[2] - r[1], reverse=True)[:10]:
        print("LARGEST %s A %d B %d (%+d)" % (r[0], r[1], r[2], r[2] - r[1]))
    if a.bound is not None:
        over = [r for r in rows if r[2] - r[1] > a.bound]
        for r in over:
            print("OVER-BOUND %s A %d B %d (%+d > %d)" % (r[0], r[1], r[2], r[2] - r[1], a.bound))
        print("peak: VERDICT %s (bound %d B: %d over)" % ("WITHIN" if not over and not nerr else "STOP", a.bound, len(over)))


def mode_instr(a, items):
    A, B = a.A, a.B
    rows, nerr = [], 0
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for key, out in ex.map(drv_one("mg_instr", (A, B)), items):
            x, y = out[A], out[B]
            if x[0] == "ERR" or y[0] == "ERR" or x[0] <= 0:
                nerr += 1
                print("ERR %s %s" % (key, out), flush=True)
                continue
            rows.append((key, x[0], y[0], y[0] / x[0]))
    with open(os.path.join(a.out, "instr%s.tsv" % a.shard.replace("/", "of")), "w") as fo:
        fo.write("key\tinstrA\tinstrB\tratio\n")
        for r in rows:
            fo.write("%s\t%d\t%d\t%.6f\n" % r)
    rat = [r[3] for r in rows]
    print("instr: %d compared, %d errors; B/A ratio p50 %.5f p95 %.5f max %.5f min %.5f"
          % (len(rows), nerr, pct(rat, 0.5), pct(rat, 0.95), max(rat or [0]), min(rat or [0])))
    over = [r for r in rows if r[3] > a.band]
    for r in sorted(over, key=lambda r: -r[3])[:30]:
        print("OVER-BAND %s A %d B %d (x%.4f)" % r)
    print("instr: VERDICT %s (p95 band %.3f, max band %.3f: %d over)" % (
        "WITHIN" if pct(rat, 0.95) <= a.p95 and not over and not nerr else "STOP", a.p95, a.band, len(over)))


def mode_rungs(a, items):
    A, B = a.A, a.B
    n = moved = err = 0
    with open(os.path.join(a.out, "rungs%s.tsv" % a.shard.replace("/", "of")), "w") as fo:
        with cf.ThreadPoolExecutor(a.jobs) as ex:
            for key, cap, out in ex.map(rung_one((A, B)), items):
                n += 1
                fo.write("%s\t%d\t%s\t%s\n" % (key, cap, out[A], out[B]))
                if out[A].startswith("ERR") or out[B].startswith("ERR"):
                    err += 1
                if out[A] != out[B]:
                    moved += 1
                    print("MOVED %s cap%dM A=%s B=%s" % (key, cap >> 20, out[A][:100], out[B][:100]), flush=True)
    print("rungs: %d compared, %d moved, %d with an ERR side" % (n, moved, err))
    print("rungs: VERDICT %s" % ("IDENTICAL" if moved == 0 else "MOVED"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="mode", required=True)
    p = sub.add_parser("prep")
    p.add_argument("side")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--tree")
    g.add_argument("--ref")
    p.add_argument("--repo")
    p.add_argument("--jobs", type=int, default=16)
    for m in ("peak", "rungs", "instr"):
        q = sub.add_parser(m)
        q.add_argument("A")
        q.add_argument("B")
        q.add_argument("out")
        q.add_argument("--jobs", type=int, default=8)
        q.add_argument("--limit", type=int, default=0)
        q.add_argument("--shard", default="", metavar="K/N")
        if m == "peak":
            q.add_argument("--bound", type=int, default=None)
        if m == "instr":
            q.add_argument("--band", type=float, default=1.02)
            q.add_argument("--p95", type=float, default=1.01)
    a = ap.parse_args()
    if a.mode == "prep":
        return prep(a)
    a.A, a.B, a.out = os.path.abspath(a.A), os.path.abspath(a.B), os.path.abspath(a.out)
    os.makedirs(os.path.join(a.out, "pat"), exist_ok=True)
    items = population(a)
    print("%s: %d compiles per side (A %s, B %s)" % (a.mode, len(items), a.A, a.B), flush=True)
    {"peak": mode_peak, "rungs": mode_rungs, "instr": mode_instr}[a.mode](a, items)


if __name__ == "__main__":
    main()
