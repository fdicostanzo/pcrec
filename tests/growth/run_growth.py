#!/usr/bin/env python3
"""run_growth.py - [GROWTH-SWEEP]: extreme depth / length / memory cells that
must REFUSE cleanly, never crash.  See tests/growth/CLAUDE.md and
docs/testing.md "Growth sweep".

Tables (TAB-separated, `-` is the empty string, `#` lines are comments):
  depth_families.tsv  THE depth table: one nesting family per row, expanded to
                      depth 250 and 251 on the budget thread.
  matrix_axes.tsv     the construct kind x quantifier x branch position x core
                      product, expanded to depth 250 and 251.
  cells.tsv           explicit cells: spines, widths, memory families.

Every cell runs through scripts/watchdog (wall + RSS + CPU), as a child of
growth_driver (one compile on a painted, guarded thread).  A cell is run
UNCAPPED (the named-limit rule) and once per memory cap of the LADDER.

Verdicts per run (an outcome is one of: compiled, refused <msg>, CRASH
(signal), TIMEOUT (watchdog 124: a timeout is a crash), RUNAWAY (watchdog
122), ERROR (driver failed to start)):
  uncapped column: PASS iff the outcome is in the cell's `expect` list
      (`compile`, `refuse:SUBSTR`, comma-separated alternatives); a cell whose
      `red` column names a known issue is KNOWN-RED when it fails, and a
      FIXED-RED failure (it passes) when it passes: the ratchet.
  ladder column: PASS iff compiled, or refused by the cell's own limit text
      (a `refuse:` alternative of its `expect`) or by "out of memory"; an
      `internal error:` refusal, CRASH/TIMEOUT/RUNAWAY/ERROR fail.
  `red` column: `ID:KIND` (KIND = CRASH, TIMEOUT, RUNAWAY, ERROR or refused):
      the known issue and the failure kind it is known to take.  A failure
      of THAT kind is KNOWN-RED; a failure of any other kind is a FAIL (a
      known crash that starts timing out is a new finding).

Modes:  run_growth.py [--only FAMILY[,FAMILY]] [--jobs N] [--no-ladder]
                      [--list] [--lib] [--keep]
        --lib   LIBRARY mode: ONE process compiles the whole cell series
                (see lib_mode()).
Exit 0 iff no FAIL and no FIXED-RED, and at least one cell was selected.
"""
import argparse
import concurrent.futures as cf
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# The memory-cap ladder: bytes of RLIMIT_DATA (growth_driver.c).  Measured on
# this tree, gcc 15.2 -O2: a trivial compile needs about 4 MB (1-3 MB refuse
# out of memory, 5 MB compiles); the worst depth family (longwrap 250) peaks
# at 36 MB resident.  2 MB: every cell must refuse; 8 MB: the trivial
# patterns compile, the deep ones refuse; 32 MB: straddles the worst depth
# family; 128 MB: below the quadratic memory families (766 MB and up) and
# above every depth family.
LADDER = [2 << 20, 8 << 20, 32 << 20, 128 << 20]

WALL_S, CPU_S, RSS = 180, 180, "3g"
# LIBRARY per-cell bound ([GROWTH-SWEEP] timeout addendum): each in-process
# compile gets its OWN wall bound = max(LIB_FLOOR_S, LIB_MARGIN x that cell's
# slowest CLI-stage run), from the walls file the CLI stage writes.  The
# margin covers the sanitizer build's slowdown (ASan+LSan at -O1 is several
# times the plain -O2 CLI) and a loaded box; a cell the walls file has never
# seen (a --lib run alone) gets the floor.  A cell over its bound is a FAIL
# (a timeout is a crash) and the series stops there with the cell named.
LIB_FLOOR_S, LIB_MARGIN = 300, 20
DEPTH_LIMIT_TEXT = "too deeply nested"      # PCREC_MAX_GROUP_DEPTH's diagnostic
# matrix@250: compiles, or is refused for one of the reasons MEASURED over the 672
# cells (2026-11-21, r73): a backreference to a group the nest lacks, the NFA state
# limit, the nested-bounded-repeat limit, an unbounded lookbehind. Any other refusal
# (an `internal error:` above all) is a FAIL.
MATRIX_250_EXPECT = ",".join(["compile"] + ["refuse:" + t for t in (
    "refers to capture group", "NFA exceeds", "nested bounded repeats would replicate",
    "a lookbehind containing a backreference")])


def tsv(path, ncols):
    """ncols: an int, or a dict first-field -> column count (matrix_axes.tsv)."""
    rows = []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        f = line.split("\t")
        want = ncols[f[0]] if isinstance(ncols, dict) and f[0] in ncols else ncols
        if isinstance(want, dict) or len(f) != want:
            sys.exit("run_growth: %s: %d columns, wanted %s: %r" % (path, len(f), want if isinstance(want, int) else "a known axis", line[:80]))
        rows.append(["" if x == "-" else x for x in f])
    return rows


def limit(name):
    out = subprocess.run([os.environ.get("PCREC") or os.path.join(ROOT, "build", "pcrec"), "--list-limits"],
                         capture_output=True, text=True, timeout=60).stdout
    for line in out.splitlines():
        k = line.split("\t")
        if k[0] == name:
            return int(k[1])
    sys.exit("run_growth: no limit %s in `pcrec --list-limits`" % name)


def printf_fmt(s, v):
    """The shell nest()'s printf: `\\\\` is a backslash, `%d` the number."""
    return s.replace("\\\\", "\\").replace("%d", str(v)) if "%" in s else s


def nest(pre, op, core, cl, post, depth):
    out = [pre]
    for i in range(depth):
        out.append(printf_fmt(op, i))
    if "%" in core:
        out.extend(printf_fmt(core, i) for i in range(1, depth + 1))
    else:
        out.append(core)
    out.append(cl * depth)
    out.append(post.replace("%d", str(depth)) if "%" in post else post)
    return "".join(out)


def spine(pre, unit, sep, mid, unit2, post, n):
    """pre + unit*n + mid + unit2*n + post; `{i}`/`{j}` = index/index+1, `{n}` = n."""
    def many(u):
        if not u:
            return ""
        return sep.join(u.replace("{i}", str(i)).replace("{j}", str(i + 1)).replace("{n}", str(n))
                        for i in range(n))
    sub = lambda s: s.replace("{n}", str(n))
    return sub(pre) + many(unit) + sub(mid) + many(unit2) + sub(post)


class Cell:
    def __init__(self, cid, family, pattern, stack, raise_, features, engine, expect, limit_name, red):
        self.id, self.family, self.pattern = cid, family, pattern
        self.stack, self.raise_, self.features, self.engine = stack, raise_, features, engine
        self.expect, self.limit = expect, limit_name
        # red: "ID:KIND" -> the known issue and the one failure kind it takes
        self.red, _, self.red_kind = red.partition(":")
        if self.red and not self.red_kind:
            sys.exit("run_growth: cell %s: red %r needs a kind (ID:KIND)" % (cid, red))
        if self.red_kind not in ("", "CRASH", "TIMEOUT", "RUNAWAY", "ERROR", "refused"):
            sys.exit("run_growth: cell %s: red kind %r is not a failure kind" % (cid, self.red_kind))
        # the refusal texts a clean refusal of this cell may carry
        self.refusals = []
        for alt in expect.split(","):
            if alt.startswith("refuse:"):
                if not alt[7:]:
                    sys.exit("run_growth: cell %s: empty refuse: substring accepts any refusal" % cid)
                self.refusals.append(alt[7:])


def build_cells(budget, depth):
    cells = []
    # --- DEPTH: the shared table, at depth and depth + 1 --------------------
    for name, pre, op, core, cl, post, feat, eng in tsv(os.path.join(HERE, "depth_families.tsv"), 8):
        for d in (depth, depth + 1):
            exp = "compile" if d == depth else "refuse:" + DEPTH_LIMIT_TEXT
            cells.append(Cell("depth/%s@%d" % (name, d), "depth", nest(pre, op, core, cl, post, d),
                              budget, 1, feat or "all", int(eng or 0), exp,
                              "PCREC_MAX_GROUP_DEPTH" if d > depth else "", ""))
    # --- MATRIX: kind x quantifier x position x core ------------------------
    ax = {"K": [], "Q": [], "P": [], "C": []}
    for row in tsv(os.path.join(HERE, "matrix_axes.tsv"), {"K": 3, "Q": 3, "P": 4, "C": 4}):
        ax[row[0]].append(tuple(row[1:]))
    for kn, kopen in ax["K"]:
        for qn, q in ax["Q"]:
            for pn, ppre, ppost in ax["P"]:
                for cn, calts, core in ax["C"]:
                    a, b = calts.split(",")
                    op = kopen + ppre.replace("{A}", a).replace("{B}", b)
                    cl = ppost.replace("{B}", b) + ")" + q
                    # the position is part of `op`/`cl`: close is per level
                    for d in (depth, depth + 1):
                        pat = nest("", op, core, cl, "", d)    # nest() repeats `cl` once per level
                        exp = MATRIX_250_EXPECT if d == depth else "refuse:" + DEPTH_LIMIT_TEXT
                        cells.append(Cell("matrix/%s.%s.%s.%s@%d" % (kn, qn, pn, cn, d), "matrix", pat,
                                          budget, 1, "all", 0, exp,
                                          "PCREC_MAX_GROUP_DEPTH" if d > depth else "", ""))
    # --- CELLS: explicit ----------------------------------------------------
    for (cid, fam, pre, unit, sep, mid, unit2, post, n, stack, rz, exp, lim, red) in \
            tsv(os.path.join(HERE, "cells.tsv"), 14):
        if stack not in ("budget", "main"):
            sys.exit("run_growth: cells.tsv: %s: stack %r is neither `budget` nor `main`" % (cid, stack))
        for nn in n.split(","):
            cells.append(Cell("%s/%s@%s" % (fam, cid, nn), fam,
                              spine(pre, unit, sep, mid, unit2, post, int(nn)),
                              budget if stack == "budget" else 0, int(rz), "all", 0, exp, lim, red))
    return cells


class Runner:
    def __init__(self, work, drv, wd):
        self.work, self.drv, self.wd = work, drv, wd
        self.walls = {}        # cell id -> slowest CLI-stage wall seconds
        self.pat_id = {}       # patfile -> cell id

    def patfile(self, cell):
        p = os.path.join(self.work, re.sub(r"[^A-Za-z0-9_.@-]", "_", cell.id) + ".pat")
        self.pat_id[p] = cell.id
        if not os.path.exists(p):
            with open(p, "w", encoding="utf-8") as f:
                f.write(cell.pattern)
        return p

    def one(self, cell, cap):
        """-> (kind, text): kind in compiled|refused|CRASH|TIMEOUT|RUNAWAY|ERROR."""
        t0 = time.monotonic()
        r = self.one_(cell, cap)
        w = time.monotonic() - t0
        if w > self.walls.get(cell.id, 0):
            self.walls[cell.id] = w
        return r

    def one_(self, cell, cap):
        pf = self.patfile(cell)
        cmd = [self.wd, "-s", str(WALL_S), "-c", str(CPU_S), "-m", RSS, "-i", "0.1",
               "-S", "growth", "-L", os.path.join(self.work, "watchdog.log"), "--",
               self.drv, "one", str(cap), str(cell.stack), str(cell.raise_),
               cell.features or "-", str(cell.engine), pf]
        r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        rc = r.returncode
        if rc in (123, 124):    # 124 wall, 123 CPU (scripts/watchdog)
            return "TIMEOUT", "wall/CPU limit (%ds): a timeout is a crash" % WALL_S
        if rc == 122:
            return "RUNAWAY", "tree RSS over %s: runaway memory" % RSS
        if rc >= 128 or rc < 0:
            return "CRASH", "killed by signal %d" % (rc - 128 if rc > 0 else -rc)
        m = re.search(r"^rc=(-?\d+) hw=(\d+) msg=(.*)$", r.stdout, re.M)
        if rc != 0 or not m:
            return "ERROR", "driver rc=%d %s" % (rc, (r.stderr or r.stdout).strip()[:120])
        if m.group(1) == "0":
            return "compiled", "hw=%s" % m.group(2)
        if m.group(1) == "-9":   # the thread never started: the compile never ran
            return "ERROR", m.group(3)
        return "refused", m.group(3)


def meets(expect, kind, text):
    for alt in expect.split(","):
        if alt == "compile" and kind == "compiled":
            return True
        if alt.startswith("refuse:") and kind == "refused" and alt[7:] in text:
            return True
    return False


def ladder_ok(cell, kind, text):
    """A capped run passes iff it compiled, or was refused by the cell's own
    limit text or by out-of-memory (not by an `internal error:`)."""
    if kind == "compiled":
        return True
    return kind == "refused" and ("out of memory" in text or any(r in text for r in cell.refusals))


def job(rn, cell, ladder):
    res = [("uncapped", 0) + rn.one(cell, 0)]
    for cap in ladder:
        res.append(("cap%dM" % (cap >> 20), cap) + rn.one(cell, cap))
    return cell, res


def tmp_base():
    return os.environ.get("PCREC_TMPDIR") or os.environ.get("TMPDIR") or "/var/tmp/pcrec-%s" % os.environ.get("USER", "u")


def walls_path():
    """One walls file PER TREE (keyed by the tree root): a plant, a worktree and
    main must not bound each other's library-mode compiles (r73 VERDICT-8)."""
    key = hashlib.sha1(ROOT.encode()).hexdigest()[:10]
    return os.environ.get("GROWTH_WALLS") or os.path.join(tmp_base(), "growth-walls-%s.tsv" % key)


def read_walls():
    w = {}
    try:
        for line in open(walls_path()):
            k, _, v = line.rstrip("\n").partition("\t")
            if v:
                w[k] = float(v)
    except OSError:
        pass
    return w


def write_walls(w):
    old = read_walls()
    old.update(w)
    with open(walls_path(), "w") as f:
        for k in sorted(old):
            f.write("%s\t%.2f\n" % (k, old[k]))


def lib_mode(rn, cells, ladder):
    """LIBRARY mode: ONE process compiles the whole cell series in a loop, each
    cell once uncapped and once under each ladder cap (RLIMIT_DATA set in that
    process), then a control pattern again.  PASS = the process exits 0 (no
    crash; under the ASan build, no leak report), prints every cell's line
    (none missing), the control compiled before and after the series is
    byte-identical, and that matcher built with gcc finds the known match.
    The compiles run on the main thread, not the budget thread: the budget is
    measured without a sanitizer and ASan inflates every frame (the stack
    budget is the CLI stage's question, this stage asks about clean-up)."""
    lib_drv = os.environ.get("GROWTH_LIB_DRIVER", rn.drv)
    series = os.path.join(rn.work, "series.tsv")
    n = 0
    walls = read_walls()
    print("library mode: walls file %s (%d of %d cells have a CLI-stage wall; the rest get the %ds floor)"
          % (walls_path(), sum(1 for c in cells if c.id in walls), len(cells), LIB_FLOOR_S))
    with open(series, "w") as f:
        for c in cells:
            # a known-red cell's UNCAPPED run is a known runaway (K150/K151, NEW-n):
            # it would take the one process down with it; its capped runs stay
            for cap in ([] if c.red else [0]) + ladder:
                bound = max(LIB_FLOOR_S, int(LIB_MARGIN * walls.get(c.id, 0)) + 1)
                f.write("\t".join([str(cap), "0", str(c.raise_), c.features or "-",
                                   str(c.engine), rn.patfile(c), str(bound)]) + "\n")
                n += 1
    ctl = os.path.join(rn.work, "control")
    env = dict(os.environ)
    env.setdefault("ASAN_OPTIONS", "detect_leaks=1:allocator_may_return_null=1")
    # the driver's progress goes to a LOG that is readable while it runs (a
    # captured pipe showed nothing for 50 minutes on the first run)
    plog = os.path.join(os.path.dirname(walls_path()), "growth-lib-progress.log")
    with open(plog, "w") as pf:
        r = subprocess.run([rn.wd, "-s", "28800", "-c", "28800", "-m", "6g", "-i", "0.5", "-S", "growth-lib",
                            "-L", os.path.join(rn.work, "watchdog.log"), "--", lib_drv, "lib", ctl, series],
                           stdout=pf, stderr=subprocess.PIPE, text=True, errors="replace", env=env)
    r.stdout = open(plog, errors="replace").read()
    print("library mode: progress log " + plog)
    bad = []
    to = [l for l in r.stdout.splitlines() if re.match(r"cell \d+ TIMEOUT ", l)]
    for l in to:
        m = re.match(r"cell (\d+) TIMEOUT bound=(\d+) pat=(.*)", l)
        bad.append("TIMEOUT (a timeout is a crash): series line %s, cell %s, over its own bound of %ss "
                   "(CLI wall x%d, floor %ds); series stopped there. progress line: %s"
                   % (m.group(1), rn.pat_id.get(m.group(3), m.group(3)), m.group(2), LIB_MARGIN, LIB_FLOOR_S, l))
    lines = [l for l in r.stdout.splitlines() if re.match(r"cell \d+ rc=", l)]
    if r.returncode != 0:
        bad.append("library process exit %d (signal, abort, sanitizer report, or watchdog kill)\n%s"
                   % (r.returncode, r.stderr[-1500:]))
    if len(lines) != n and not to:
        bad.append("library process printed %d of %d cell lines" % (len(lines), n))
    crashed = [l for l in lines if not re.match(r"cell \d+ rc=(0|-1|-9) ", l)]
    slow = sorted(((float(m.group(1)), l) for l in lines for m in [re.search(r" wall=([\d.]+) ", l)] if m), reverse=True)[:3]
    for w_, l in slow:
        print("library mode: slowest cell lines: " + l[:140])
    bad += ["unexpected cell line: " + l for l in crashed[:5]]
    if "ERROR: LeakSanitizer" in r.stderr or "ERROR: AddressSanitizer" in r.stderr:
        bad.append("sanitizer report:\n" + r.stderr[-1500:])
    try:
        b, a = open(ctl + ".before").read(), open(ctl + ".after").read()
        if b != a:
            bad.append("the control compiled AFTER the series differs from the one compiled BEFORE it")
        cfile = ctl + ".c"
        open(cfile, "w").write(a)
        exe = ctl + ".exe"
        cc = os.environ.get("CC", "gcc")
        cr = subprocess.run([cc, "-O1", "-std=gnu11", "-w", "-o", exe, cfile], capture_output=True, text=True)
        if cr.returncode != 0:
            bad.append("the control's generated C did not compile: " + cr.stderr[:300])
        else:
            # generated main(): see tests/growth/CLAUDE.md; it reads the subject from argv[1]
            ok = subprocess.run([exe, "ababcdef"], capture_output=True, text=True)
            nok = subprocess.run([exe, "ababcdx"], capture_output=True, text=True)
            if ok.returncode != 0 or nok.returncode != 1:
                bad.append("the control's matcher answered wrongly (match rc=%d, non-match rc=%d)"
                           % (ok.returncode, nok.returncode))
    except OSError as e:
        bad.append("control output missing: %s" % e)
    kinds = {}
    for l in lines:
        m = re.match(r"cell \d+ rc=(-?\d+)", l)
        kinds[m.group(1)] = kinds.get(m.group(1), 0) + 1 if m else 0
    print("library mode: %d compiles in ONE process (%s): rc histogram %s" % (n, lib_drv, kinds))
    for b_ in bad:
        print("FAIL: library mode: " + b_)
    if not bad:
        print("PASS: library mode: no crash, no leak report, every cell answered, control identical and correct")
    return len(bad)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=0)
    ap.add_argument("--no-ladder", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--lib", action="store_true")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--verbose", action="store_true", help="print every uncapped outcome")
    ap.add_argument("--pattern", default="", help="print the pattern of the cell with this id and exit")
    ap.add_argument("--depth-only", action="store_true", help="the uncapped depth family only (make test-stackdepth)")
    a = ap.parse_args()
    budget = limit("PCREC_COMPILE_STACK_BUDGET")
    depth = limit("PCREC_MAX_GROUP_DEPTH")
    cells = build_cells(budget, depth)
    if a.pattern:
        hit = [c for c in cells if c.id == a.pattern]
        if not hit:
            sys.exit("run_growth: no cell %s" % a.pattern)
        sys.stdout.write(hit[0].pattern)
        return 0
    if a.depth_only:
        a.only, a.no_ladder = "depth", True
    if a.only:
        keep = set(a.only.split(","))
        known = {c.family for c in cells}
        if keep - known:
            sys.exit("run_growth: --only names no family: %s (families: %s)" % (",".join(sorted(keep - known)), ",".join(sorted(known))))
        cells = [c for c in cells if c.family in keep]
    if not cells:
        sys.exit("run_growth: no cells selected")
    if a.list:
        fams = {}
        for c in cells:
            fams[c.family] = fams.get(c.family, 0) + 1
        for c in cells:
            print("%s\t%s\t%s" % (c.id, c.expect, c.red))
        print("# %d cells: %s" % (len(cells), ", ".join("%s %d" % kv for kv in sorted(fams.items()))))
        return 0
    base = tmp_base()
    os.makedirs(base, exist_ok=True)
    work = tempfile.mkdtemp(prefix="growth-", dir=base)
    drv = os.path.join(work, "growth_driver")
    cc = os.environ.get("CC", "gcc")
    libp = os.environ.get("LIBPCREC", os.path.join(ROOT, "build", "libpcrec.a"))
    b = subprocess.run([cc, "-O2", "-std=gnu11", "-Wall", "-Wextra", "-I" + os.path.join(ROOT, "lib"), "-o", drv,
                        os.path.join(HERE, "growth_driver.c"), libp, "-lpthread", "-lm"] +
                       os.environ.get("GROWTH_CFLAGS", "").split(), capture_output=True, text=True)
    if b.returncode != 0:
        print("FAIL: could not build growth_driver.c:\n" + b.stderr[:800])
        return 1
    rn = Runner(work, drv, os.path.join(ROOT, "scripts", "watchdog"))
    ladder = [] if a.no_ladder else LADDER
    if a.lib:
        return 1 if lib_mode(rn, cells, ladder) else 0
    jobs = a.jobs or max(1, (os.cpu_count() or 4) // 2)
    npass = nfail = nred = nfixed = 0
    fam = {}
    with cf.ThreadPoolExecutor(jobs) as ex:
        for cell, res in ex.map(lambda c: job(rn, c, ladder), cells):
            st = fam.setdefault(cell.family, [0, 0, 0, 0])
            for col, cap, kind, text in res:
                if col == "uncapped":
                    good = meets(cell.expect, kind, text)
                    why = "expected %s (limit %s), got %s: %s" % (cell.expect, cell.limit or "-", kind, text)
                else:
                    good = ladder_ok(cell, kind, text)
                    why = ("a capped run must compile or be refused by %s or out of memory, got %s: %s"
                           % (cell.refusals or "its limit", kind, text))
                tag = "%s %s [%s]" % (cell.id, col, kind)
                if a.depth_only and kind == "compiled":
                    print("RECORD: %s stack=%d %s" % (cell.id, cell.stack, text))
                if a.verbose and col == "uncapped":
                    print("OUTCOME: %s: %s" % (tag, text[:110]))
                if cell.red and not good and kind != cell.red_kind:
                    # the red names ONE failure kind; a different one is a new finding
                    nfail += 1; st[1] += 1
                    print("FAIL: %s: known-red %s is a %s, but it failed as %s: %s" % (tag, cell.red, cell.red_kind, kind, why))
                    print("      repro: %s" % repro(cell, cap))
                elif cell.red:
                    if not good:
                        nred += 1; st[2] += 1
                        print("KNOWN-RED: %s (%s): %s" % (tag, cell.red, why))
                    elif col == "uncapped":
                        # a red cell that passes in the uncapped column is a ratchet event
                        nfixed += 1; st[3] += 1
                        print("FIXED-RED: %s passes now: remove its `red` (%s)" % (tag, cell.red))
                    else:
                        npass += 1; st[0] += 1
                elif good:
                    npass += 1; st[0] += 1
                else:
                    nfail += 1; st[1] += 1
                    print("FAIL: %s: %s" % (tag, why))
                    print("      repro: %s" % repro(cell, cap))
    print()
    write_walls(rn.walls)
    print("walls file %s: %d cells" % (walls_path(), len(rn.walls)))
    print("== Growth sweep ==")
    for f, (p, fl, rd, fx) in sorted(fam.items()):
        print("family %-8s runs passed %d  failed %d  known-red %d  fixed-red %d" % (f, p, fl, rd, fx))
    print("runs passed: %d" % npass)
    print("runs failed: %d" % (nfail + nfixed))
    print("runs known-red: %d" % nred)
    if not a.keep:
        subprocess.run(["rm", "-rf", "--", work])
    else:
        print("work dir kept: " + work)
    return 1 if (nfail or nfixed) else 0


def repro(cell, cap):
    return ("pattern %d bytes; scripts/watchdog -s %d -m %s -- growth_driver one %d %d %d %s %d <patfile> (run_growth.py --only %s --keep)"
            % (len(cell.pattern), WALL_S, RSS, cap, cell.stack, cell.raise_, cell.features or "-", cell.engine, cell.family))


if __name__ == "__main__":
    sys.exit(main())
