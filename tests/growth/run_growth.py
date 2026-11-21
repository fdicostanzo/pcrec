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
        --shard K/N [--table T]   only shard K's cells of the declared cloud table; --shard-check: the population check;
        --units FILE              per-cell seconds for the cloud reweigh ([GROWTH-CLOUD]).
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
# A LIMIT cell's matcher runs on each of these subjects (no match, a one-byte, a longer
# one); each run must exit 0 or 1.  Fixed, not per-cell: the verdict is "it runs", not the answer.
SUBJECTS = ("", "a", "abcabc")
# LIBRARY per-cell bound ([GROWTH-SWEEP] timeout addendum): each in-process
# compile gets its OWN wall bound = max(LIB_FLOOR_S, LIB_MARGIN x that cell's
# slowest CLI-stage run), from the walls file the CLI stage writes.  The
# margin covers the sanitizer build's slowdown (ASan+LSan at -O1 is several
# times the plain -O2 CLI) and a loaded box; a cell the walls file has never
# seen (a --lib run alone) gets the floor.  A cell over its bound is a FAIL
# (a timeout is a crash) and the series stops there with the cell named.
LIB_FLOOR_S, LIB_MARGIN = 300, 20
DEPTH_LIMIT_TEXT = "too deeply nested"      # PCREC_MAX_GROUP_DEPTH's diagnostic
CAPTURING = ("group", "named")              # the matrix kinds whose groups capture (a backreference core needs one)
# matrix `+` cells at depth 250 (measured 2026-11-21 on a 20-pair sample): refused by a limit far below depth 250
PLUS_250_EXPECT = "refuse:NFA exceeds,refuse:nested bounded repeats would replicate"
PLUS_250_LIMIT = "PCREC_MAX_NFA_STATES or PCREC_MAX_VM_REPLICATION_PRODUCT"


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


KINDS = ("stability", "limit")      # a closed set; every cell declares one, there is no default


class Cell:
    def __init__(self, cid, family, pattern, stack, raise_, features, engine, kind, expect, limit_name, pair, red):
        self.id, self.family, self.pattern = cid, family, pattern
        # kind: RULING limit-test-criteria (owner, 2026-11-21).  STABILITY = sized PAST the
        # named limit: it passes on a clean refusal by THAT limit.  LIMIT = JUST BEFORE it:
        # it passes only if it compiles and its matcher runs.  pair: the id shared by a limit
        # cell and its stability twin across the same limit ("" = none: reported UNPAIRED).
        if kind not in KINDS:
            sys.exit("run_growth: cell %s: kind %r is not one of %s" % (cid, kind, "/".join(KINDS)))
        self.kind, self.pair = kind, pair
        if kind == "limit" and expect not in ("compile", "compile:norun"):
            sys.exit("run_growth: cell %s: a limit cell's expect is `compile` or `compile:norun`, got %r" % (cid, expect))
        if kind == "limit" and not limit_name:
            sys.exit("run_growth: cell %s: a limit cell names the limit it sits just before" % cid)
        if kind == "stability" and (not expect or any(not a.startswith("refuse:") for a in expect.split(","))):
            sys.exit("run_growth: cell %s: a stability cell's expect is refuse:SUBSTR (the limit's text), got %r" % (cid, expect))
        self.stack, self.raise_, self.features, self.engine = stack, raise_, features, engine
        self.expect, self.limit = expect, limit_name
        # red: "ID:KIND" -> the known issue and the one failure kind it takes
        self.red, _, self.red_kind = red.partition(":")
        if self.red and not self.red_kind:
            sys.exit("run_growth: cell %s: red %r needs a kind (ID:KIND)" % (cid, red))
        if self.red_kind not in ("", "CRASH", "TIMEOUT", "RUNAWAY", "ERROR", "refused", "BUILD", "MATCHER"):
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
            lim = d == depth        # depth is the limit's value: AT it = just before, one more = past
            cells.append(Cell("depth/%s@%d" % (name, d), "depth", nest(pre, op, core, cl, post, d),
                              budget, 1, feat or "all", int(eng or 0),
                              "limit" if lim else "stability",
                              "compile" if lim else "refuse:" + DEPTH_LIMIT_TEXT,
                              "PCREC_MAX_GROUP_DEPTH", "depth/" + name, ""))
    # --- MATRIX: kind x quantifier x position x core ------------------------
    ax = {"K": [], "Q": [], "P": [], "C": []}
    for row in tsv(os.path.join(HERE, "matrix_axes.tsv"), {"K": 3, "Q": 3, "P": 4, "C": 4}):
        ax[row[0]].append(tuple(row[1:]))
    for kn, kopen in ax["K"]:
        for qn, q in ax["Q"]:
            for pn, ppre, ppost in ax["P"]:
                for cn, calts, core in ax["C"]:
                    if kn == "lookbehind" and cn == "bref":
                        continue    # PCRE2 refuses a backreference inside a lookbehind: no cell can compile
                    a, b = calts.split(",")
                    op = kopen + ppre.replace("{A}", a).replace("{B}", b)
                    cl = ppost.replace("{B}", b) + ")" + q
                    # a `\1` core needs a group 1: the kinds that capture nothing get one in front
                    pre = "(a)" if cn == "bref" and kn not in CAPTURING else ""
                    cid = "%s.%s.%s.%s" % (kn, qn, pn, cn)
                    for d in (depth, depth + 1):
                        pat = nest(pre, op, core, cl, "", d)    # nest() repeats `cl` once per level
                        if d > depth:       # past the depth limit: stability
                            kind, exp, lim, pair = "stability", "refuse:" + DEPTH_LIMIT_TEXT, "PCREC_MAX_GROUP_DEPTH", "matrix/" + cid
                        elif qn == "plus":
                            # `+` replicates the body at every level, so a LOWER limit binds long before depth 250
                            # (limits.md 3.10: "`+` ... is refused as too large (PCREC_MAX_NFA_STATES)"): this cell
                            # is sized past THAT limit (its limit cell would sit at a much smaller depth: UNPAIRED)
                            kind, exp, lim, pair = "stability", PLUS_250_EXPECT, PLUS_250_LIMIT, ""
                        else:
                            kind, exp, lim, pair = "limit", "compile", "PCREC_MAX_GROUP_DEPTH", "matrix/" + cid
                        cells.append(Cell("matrix/%s@%d" % (cid, d), "matrix", pat, budget, 1, "all", 0,
                                          kind, exp, lim, pair, ""))
    # --- CELLS: explicit ----------------------------------------------------
    for (cid, fam, pre, unit, sep, mid, unit2, post, n, stack, rz, kind, exp, lim, pair, red) in \
            tsv(os.path.join(HERE, "cells.tsv"), 16):
        if stack not in ("budget", "main"):
            sys.exit("run_growth: cells.tsv: %s: stack %r is neither `budget` nor `main`" % (cid, stack))
        for nn in n.split(","):
            cells.append(Cell("%s/%s@%s" % (fam, cid, nn), fam,
                              spine(pre, unit, sep, mid, unit2, post, int(nn)),
                              budget if stack == "budget" else 0, int(rz), "all", 0, kind, exp, lim, pair, red))
    return cells


def pair_report(cells):
    """-> (pairs, unpaired): pair id -> its cells; and the cells with no twin of the other kind
    (a limit cell with no stability cell across the same limit, or the reverse; empty pair too).
    A pair whose cells name different limits is a table error."""
    pairs = {}
    for c in cells:
        if c.pair:
            pairs.setdefault(c.pair, []).append(c)
    for pid, cs in pairs.items():
        if len({c.limit for c in cs}) != 1:
            sys.exit("run_growth: pair %s names two limits: %s" % (pid, sorted({c.limit for c in cs})))
    unpaired = [c for c in cells if not c.pair or {x.kind for x in pairs[c.pair]} != set(KINDS)]
    return pairs, unpaired


def sample_matrix(cells, npairs):
    """Keep every non-matrix cell and `npairs` matrix PAIRS (both cells of each), chosen by a
    prime stride over the product so every construct kind, quantifier, position and core shows
    up (the sweep's own coverage check below).  The full matrix is the queued sweep's job."""
    base = lambda c: c.id.rsplit("@", 1)[0]
    mat = [c for c in cells if c.family == "matrix"]
    ids = list(dict.fromkeys(base(c) for c in mat))
    pick = {ids[(k * 37) % len(ids)] for k in range(npairs)}
    return [c for c in cells if c.family != "matrix" or base(c) in pick]


# ---- CLOUD SHARDS ([GROWTH-CLOUD]) ------------------------------------------------------------
# The cloud kind `growth` splits the cell list over N shards.  The partition is a DECLARED table
# (tests/ci/cloud_growth_shards.tsv: `cell id<TAB>shard<TAB>weight_s<TAB>weight_source`, `# shards=N`), generated by
# tests/ci/cloud_units_plan.py growth (LPT over each cell's measured seconds) and read here, never recomputed: a
# shard is "the cells the table gives K".  --shard-check is the kind's population check: every cell of the
# unsplit list is in exactly one shard, and the table names no cell that does not exist.
DEFAULT_TABLE = os.path.join(ROOT, "tests", "ci", "cloud_growth_shards.tsv")


def read_table(path):
    """-> (n, {cell id: shard}); exits on a malformed table or a cell listed twice."""
    n, rows, seen_head = None, {}, False
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        m = re.match(r"# shards=(\d+)$", line)
        if m:
            n = int(m.group(1))
        if not line or line.startswith("#"):
            continue
        if not seen_head:
            seen_head = True    # the column-name line
            continue
        f = line.split("\t")
        if len(f) < 2 or not f[1].isdigit():
            sys.exit("run_growth: %s: bad row %r" % (path, line[:80]))
        if f[0] in rows:
            sys.exit("run_growth: %s: cell %s is listed twice (in shards %s and %s)" % (path, f[0], rows[f[0]], f[1]))
        rows[f[0]] = int(f[1])
    if not n:
        sys.exit("run_growth: %s: no `# shards=N` line" % path)
    return n, rows


def shard_cells(cells, spec, table):
    """The cells of shard K of `spec` (K/N): by the declared table.  A cell the table lacks, or a shard with
    no cells, exits nonzero (a shard must never silently run an unfiltered or empty sweep)."""
    m = re.fullmatch(r"(\d+)/(\d+)", spec)
    if not m:
        sys.exit("run_growth: --shard wants K/N, got %r" % spec)
    k, n = int(m.group(1)), int(m.group(2))
    tn, rows = read_table(table)
    if tn != n or not 1 <= k <= n:
        sys.exit("run_growth: --shard %s: the table %s has %d shards" % (spec, table, tn))
    missing = [c.id for c in cells if c.id not in rows]
    if missing:
        sys.exit("run_growth: %d cell(s) are in no shard of %s (first: %s); regenerate it (make cloud-reweight KIND=growth)"
                 % (len(missing), table, missing[0]))
    mine = [c for c in cells if rows[c.id] == k]
    if not mine:
        sys.exit("run_growth: shard %s has NO cells in %s (refusing to run an unfiltered sweep)" % (spec, table))
    return mine


def shard_check(cells, table):
    """The population check: the table's shards, summed, are the unsplit cell list, each cell once.  Prints one
    PASS line or the differences by cell id.  -> number of problems."""
    n, rows = read_table(table)
    have = {c.id for c in cells}
    bad = ["DROPPED (in no shard): " + i for i in sorted(have - set(rows))]
    bad += ["EXTRA (not a cell of the sweep): " + i for i in sorted(set(rows) - have)]
    bad += ["shard %d/%d has no cells" % (k, n) for k in range(1, n + 1) if k not in set(rows.values())]
    bad += ["cell %s is in shard %d, outside 1..%d" % (i, k, n) for i, k in sorted(rows.items()) if not 1 <= k <= n]
    for b in bad[:40]:
        print("FAIL: " + b)
    if not bad:
        print("PASS: %d shards of %s run the unsplit sweep's %d cells exactly once" % (n, os.path.basename(table), len(cells)))
    return len(bad)


class Runner:
    def __init__(self, work, drv, wd):
        self.work, self.drv, self.wd = work, drv, wd
        self.walls = {}        # cell id -> slowest CLI-stage wall seconds
        self.libtotals = {}    # cell id -> SUM of its library-mode compiles' wall seconds
        self.totals = {}       # cell id -> SUM of every CLI-stage run's wall seconds (the cell's cost; --units)
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
        self.totals[cell.id] = self.totals.get(cell.id, 0) + w
        return r

    def one_(self, cell, cap):
        pf = self.patfile(cell)
        # a LIMIT cell's uncapped run also emits the artifact's C (with a main()) so its
        # matcher can be built and run: "compiles AND its matcher runs"
        csrc = pf + ".c" if (cell.kind == "limit" and cell.expect == "compile" and cap == 0) else None
        cmd = [self.wd, "-s", str(WALL_S), "-c", str(CPU_S), "-m", RSS, "-i", "0.1",
               "-S", "growth", "-L", os.path.join(self.work, "watchdog.log"), "--",
               self.drv, "one", str(cap), str(cell.stack), str(cell.raise_),
               cell.features or "-", str(cell.engine), pf] + ([csrc] if csrc else [])
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
            if csrc:
                bad = self.matcher(csrc)
                if bad:
                    return bad
            return "compiled", "hw=%s" % m.group(2)
        if m.group(1) == "-9":   # the thread never started: the compile never ran
            return "ERROR", m.group(3)
        return "refused", m.group(3)


    def matcher(self, csrc):
        """Build the cell's emitted C and run it on SUBJECTS: each run must exit 0 (match) or
        1 (no match), the generated main()'s contract; a crash, a give-up (3) or any other exit
        fails.  -> None, or an outcome (kind, text) with kind BUILD or MATCHER (or TIMEOUT)."""
        exe = csrc[:-2] + ".exe"
        cc = os.environ.get("CC", "gcc")
        b = subprocess.run([self.wd, "-s", str(WALL_S), "-c", str(CPU_S), "-m", RSS, "-S", "growth-cc",
                            "-L", os.path.join(self.work, "watchdog.log"), "--",
                            cc, "-O0", "-std=gnu11", "-w", "-o", exe, csrc, "-lm"],
                           capture_output=True, text=True, errors="replace")
        if b.returncode in (122, 123, 124):
            return "TIMEOUT", "gcc on the emitted C over its wall/CPU/RSS bound (rc=%d)" % b.returncode
        if b.returncode != 0:
            return "BUILD", "the emitted C did not build: " + (b.stderr or b.stdout).strip()[:160]
        for subj in SUBJECTS:
            r = subprocess.run([self.wd, "-s", "60", "-c", "60", "-m", "1g", "-S", "growth-run", "-L",
                                os.path.join(self.work, "watchdog.log"), "--", exe, subj],
                               capture_output=True, text=True, errors="replace")
            if r.returncode in (122, 123, 124):
                return "TIMEOUT", "matcher on %r over its bound (rc=%d)" % (subj, r.returncode)
            if r.returncode not in (0, 1):
                return "MATCHER", "matcher on %r exited %d (0 = match, 1 = no match): %s" % (
                    subj, r.returncode, (r.stdout or r.stderr).strip()[:80])
        return None


def judge(cell, kind, text):
    """The uncapped verdict, by the cell's declared kind (RULING limit-test-criteria).
    -> (good, why)."""
    if cell.kind == "limit":
        if kind == "compiled":
            return True, ""
        extra = ""
        if kind == "refused":
            extra = " CROSSED OVER: a limit cell was REFUSED (the limit fires early)."
        return False, "limit cell: expected to compile and run its matcher, got %s: %s.%s" % (kind, text, extra)
    if kind == "refused" and any(r in text for r in cell.refusals):
        return True, ""
    extra = ""
    if kind == "compiled":
        extra = " CROSSED OVER: a stability cell COMPILED (it no longer tests the limit)."
    elif kind == "refused":
        extra = " A DIFFERENT refusal than limit %s." % (cell.limit or "-")
    return False, "stability cell: expected a clean refusal by %s (%s), got %s: %s.%s" % (
        cell.limit or "-", "/".join(cell.refusals), kind, text, extra)


def ladder_ok(cell, kind, text):
    """A capped run passes iff it compiled, or was refused by the cell's own
    limit text or by out-of-memory (not by an `internal error:`)."""
    if kind == "compiled":
        return True
    return kind == "refused" and ("out of memory" in text or any(r in text for r in cell.refusals))


def job(rn, cell, ladder):
    res = [("uncapped", 0) + rn.one(cell, 0)]
    for cap in ladder:
        if cap < 2 * len(cell.pattern):
            continue    # the pattern's own bytes (read before the cap is set) would fill the rung: no thread can start
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
    order = []      # the cell id of each series line, in order
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
                order.append(c.id)
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
    # the library cells' seconds (--units): each progress line's wall, by its series index
    for l in lines:
        m = re.match(r"cell (\d+) rc=.* wall=([\d.]+) ", l)
        if m and int(m.group(1)) < len(order):      # the driver numbers the series lines from 0
            cid = order[int(m.group(1))]
            rn.libtotals[cid] = rn.libtotals.get(cid, 0) + float(m.group(2))
    if r.returncode != 0:
        # name the cell the process was on: the series line after the last progress line
        died = order[len(lines)] if len(lines) < len(order) else "none (after the series)"
        bad.append("library process exit %d (signal, abort, sanitizer report, or watchdog kill) while on cell %s\n%s"
                   % (r.returncode, died, r.stderr[-1500:]))
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


def write_units(path, rn):
    """`cell id<TAB>seconds`: the cell's cost on this runner, CLI runs and library compiles summed.  A stage that
    did not run adds nothing, so a --lib run completes (never overwrites) what the CLI stage wrote."""
    have = {}
    try:
        for line in open(path):
            k, _, v = line.rstrip("\n").partition("\t")
            if v:
                have[k] = float(v)
    except OSError:
        pass
    for src in (rn.totals, rn.libtotals):
        for k, v in src.items():
            have[k] = have.get(k, 0) + v
    with open(path, "w") as f:
        for k in sorted(have):
            f.write("%s\t%.2f\n" % (k, have[k]))


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
    ap.add_argument("--sample", type=int, default=0, metavar="N", help="run N matrix PAIRS (2N cells) instead of the whole matrix")
    ap.add_argument("--pairs", action="store_true", help="list every limit/stability pair and every UNPAIRED cell, then exit")
    ap.add_argument("--selftest", action="store_true", help="the crossing-over alert: a stability cell that compiles and a limit cell that is refused must both FAIL")
    ap.add_argument("--shard", default="", metavar="K/N", help="only the cells shard K of N owns, by --table (the cloud kind `growth`)")
    ap.add_argument("--shard-check", action="store_true", help="the population check: the --table's shards are exactly the cell list, each cell once; then exit")
    ap.add_argument("--table", default=DEFAULT_TABLE, help="the shard table (default tests/ci/cloud_growth_shards.tsv)")
    ap.add_argument("--units", default="", metavar="FILE", help="write `cell id<TAB>seconds` (the cell's CLI + library cost) to FILE: what the cloud reweigh reads")
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
    pairs, unpaired = pair_report(cells)
    if a.pairs:
        for pid, cs in pairs.items():
            print("%s\t%s\t%s" % (pid, cs[0].limit, " ".join("%s:%s" % (c.kind, c.id.split("@")[-1]) for c in cs)))
        for c in unpaired:
            print("UNPAIRED\t%s\t%s\t%s" % (c.id, c.kind, c.limit or "-"))
        print("# %d pairs, %d unpaired cells, %d limit cells, %d stability cells" % (
            len(pairs), len(unpaired), sum(c.kind == "limit" for c in cells), sum(c.kind == "stability" for c in cells)))
        return 0
    if a.shard_check:
        return 1 if shard_check(cells, a.table) else 0
    if a.shard:
        cells = shard_cells(cells, a.shard, a.table)
        print("shard %s: %d of the sweep's cells (table %s)" % (a.shard, len(cells), os.path.relpath(a.table, ROOT)))
    if a.sample:
        cells = sample_matrix(cells, a.sample)
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
            print("%s\t%s\t%s\t%s" % (c.id, c.kind, c.expect, c.red))
        print("# %d cells (%d limit, %d stability): %s" % (len(cells), sum(c.kind == "limit" for c in cells),
              sum(c.kind == "stability" for c in cells), ", ".join("%s %d" % kv for kv in sorted(fams.items()))))
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
    if a.selftest:
        return selftest(rn, budget, depth)
    ladder = [] if a.no_ladder else LADDER
    if a.lib:
        nbad = lib_mode(rn, cells, ladder)
        if a.units:
            write_units(a.units, rn)
        return 1 if nbad else 0
    jobs = a.jobs or max(1, (os.cpu_count() or 4) // 2)
    npass = nfail = nred = nfixed = 0
    fam = {}
    with cf.ThreadPoolExecutor(jobs) as ex:
        for cell, res in ex.map(lambda c: job(rn, c, ladder), cells):
            st = fam.setdefault(cell.family, [0, 0, 0, 0])
            for col, cap, kind, text in res:
                if col == "uncapped":
                    good, why = judge(cell, kind, text)
                else:
                    good = ladder_ok(cell, kind, text)
                    why = ("a capped run must compile or be refused by %s or out of memory, got %s: %s"
                           % (cell.refusals or "its limit", kind, text))
                tag = "%s (%s) %s [%s]" % (cell.id, cell.kind, col, kind)
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
    if a.units:
        write_units(a.units, rn)
    print("walls file %s: %d cells" % (walls_path(), len(rn.walls)))
    print("== Growth sweep ==")
    for f, (p, fl, rd, fx) in sorted(fam.items()):
        print("family %-8s runs passed %d  failed %d  known-red %d  fixed-red %d" % (f, p, fl, rd, fx))
    print("runs passed: %d" % npass)
    print("runs failed: %d" % (nfail + nfixed))
    print("runs known-red: %d" % nred)
    sel = {c.id for c in cells}
    for c in unpaired:
        if c.id in sel:
            print("UNPAIRED: %s (%s, limit %s) has no %s twin across the same limit" % (
                c.id, c.kind, c.limit or "-", "limit" if c.kind == "stability" else "stability"))
    if not a.keep:
        subprocess.run(["rm", "-rf", "--", work])
    else:
        print("work dir kept: " + work)
    return 1 if (nfail or nfixed) else 0


def selftest(rn, budget, depth):
    """The crossing-over alert, both ways (RULING limit-test-criteria (3)): a stability cell
    that COMPILES and a limit cell that is REFUSED must each be judged FAIL, and each cell on
    its own side of the limit must be judged PASS.  Exit 0 iff all four are judged as written."""
    deep = lambda d: nest("", "(?:", "a", ")", "", d)
    cases = [("stability", "a", False, "CROSSED OVER"),                      # compiles: the limit is not tested
             ("stability", deep(depth + 1), True, ""),                        # refused by the limit: PASS
             ("limit", deep(depth + 1), False, "CROSSED OVER"),               # refused: the limit fires early
             ("limit", deep(depth), True, "")]                                # compiles and its matcher runs
    bad = 0
    for k, (kind, pat, want_good, want_word) in enumerate(cases):
        c = Cell("selftest/%d" % k, "selftest", pat, budget, 1, "all", 0, kind,
                 "compile" if kind == "limit" else "refuse:" + DEPTH_LIMIT_TEXT, "PCREC_MAX_GROUP_DEPTH", "", "")
        outcome = rn.one(c, 0)
        good, why = judge(c, *outcome)
        ok = good == want_good and want_word in why
        print("%s: %s cell, %s: judged %s%s" % ("selftest ok" if ok else "FAIL: selftest", kind,
              outcome[0], "PASS" if good else "FAIL", ("  <- " + why) if why else ""))
        bad += not ok
    subprocess.run(["rm", "-rf", "--", rn.work])
    return 1 if bad else 0


def repro(cell, cap):
    return ("pattern %d bytes; scripts/watchdog -s %d -m %s -- growth_driver one %d %d %d %s %d <patfile> (run_growth.py --only %s --keep)"
            % (len(cell.pattern), WALL_S, RSS, cap, cell.stack, cell.raise_, cell.features or "-", cell.engine, cell.family))


if __name__ == "__main__":
    sys.exit(main())
