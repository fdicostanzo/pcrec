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
      `internal error:` refusal, CRASH/TIMEOUT/RUNAWAY/ERROR fail.  An
      `internal error:` refusal fails in EVERY column, whatever text it holds.
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
import atexit
import concurrent.futures as cf
import hashlib
import math
import os
import re
import subprocess
import sys
import tempfile
import threading
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

# TIME BOUNDS (owner ruling growth-time-bound, 2026-11-21): a cell's time bound is CPU SECONDS (user+sys of the compile's
# process tree, scripts/watchdog -c; the library stage's in-process bound is ITIMER_PROF), so a loaded box or a slow
# runner is largely (not wholly: CPU inflates up to ~1.9x under contention, r89 CPU-1) unable to turn a correct cell red;
# the margin is the derivation in BOUNDS_BASIS; the WALL bound is only a HANG GUARD (a process that blocks burns no CPU).  A red
# names which bound fired ("CPU bound" / "WALL hang guard").  BOUNDS_BASIS says where each value comes from; re-derive
# them from the sweep's own `CPU:` lines (the slowest cells and the headroom) when a cell approaches them.
CPU_S, WALL_S, RSS = 300, 1500, "3g"
OCC_CPU_S, OCC_WALL_S = 3600, 14400
BOUNDS_BASIS = """\
CPU_S 300 (default tier, each compile and each matcher build): MEASURED on the dev box (Ryzen 7700X, gcc 15.2, 2026-11-23, after
  K159): the costliest default-tier compile is a possessive/star nest at depth 250 (`group.poss.last.lit@250`: 27.5 s CPU alone at
  -j2, 45 s CPU at -j8 where the cores share caches; `atomic.star.last.lit@250` 33.7 s at -j8; `spine/named@65535` 25 s); gcc on the
  limit cells' matchers costs at most 3.9 s CPU (full sweep, -j8, 2026-11-23).  The cloud runners (4 cores, slower per core) are NOT measured against this box:
  the ratio is unknown until the first cloud run of this harness prints its own `CPU:` lines (the slowest cells and the headroom
  against this bound); 300 s is 6.7x this box's worst under load and 11x its worst alone.  D45's rule, written out: quiet worst
  (27.5 s) x ~2 for contention (CPU inflates up to ~1.9x under load, measured by review r89; this lane's own 27.5 vs 45 s is
  1.64x) x the unknown cloud-per-core ratio x headroom = 300 s; the cloud factor is the open term and the figure is to be
  RE-DERIVED from the first cloud `CPU:` lines.  `CPU` of a gcc build is watchdog's sampled tree sum (about cc1 alone: true tree
  CPU read 0.66 s where watchdog read 0.58 s), and the `CPU:` headroom line adds a cell's compile CPU to its gcc CPU although each
  is bounded alone: read headroom per bound (compile max, gcc max), not the sum.  A superlinear step does not hide under it: the
  per-doubling report (--doubling) is what catches those.
WALL_S 1500 (default tier hang guard): below the cloud shard job's 45 min (2700 s) kill, so the guard names the cell before the job
  is cut (shard 31 of run 44940630891 was cut at the job limit with no cell named), and 5x the CPU bound for a box at one fifth
  of a core.  It never decides a cell's verdict by speed: a process that burns CPU is judged by CPU_S.  It names a cell only if
  the hung run STARTS in the job's first ~1200 s (2700 - 1500 s of guard); a hang that starts later is cut by the job first.
MATCHER_CPU_S 60 / MATCHER_WALL_S 600 (each run of a limit cell's built matcher, on SUBJECTS of at most 6 bytes): MEASURED 2026-11-23
  on the dev box over every limit cell's matcher (the full uncapped sweep, one run per subject, 3 subjects): the worst run read 0.00 s CPU, under
  watchdog's 0.1 s sampling, so every matcher run is below 0.1 s; the generated code walks a 6-byte subject.  60 s CPU is at least
  600x that worst and is meant to hold a slow runner and a loaded box; a matcher over 60 CPU s is a runaway, not a slow run.  The
  wall guard is the hang-guard multiple (10x) of the CPU bound (wall = CPU was NOT a hang guard: a loaded box reads wall >= CPU, so
  the wall fired first).  Re-derive from the `CPU:` headroom line's `matcher run max` if a limit cell's matcher ever costs seconds.
LIB_FLOOR_S 300 / LIB_MARGIN 20 (library stage, unchanged from lane grow2: the sanitizer build's slowdown), now applied to the
  cell's CLI-stage compile CPU rather than its wall; the wall guard there is 10x the bound, capped at (growth_driver.c
  WALL_CAP) = 2400 s: the floor bound 300 x 10 = 3000 s sat PAST the cloud job's 2700 s kill (r89 R89-5), so a hang was never named.
  The library progress is streamed (a `begin` line per cell, library mode prints it as the cell starts), so a cut job still names
  the cell it was on.
"""
MATCHER_CPU_S, MATCHER_WALL_S = 60, 600
# A LIMIT cell's matcher runs on each of these subjects (no match, a one-byte, a longer
# one); each run must exit 0 or 1.  Fixed, not per-cell: the verdict is "it runs", not the answer.
SUBJECTS = ("", "a", "abcabc")
# LIBRARY per-cell bound ([GROWTH-SWEEP] timeout addendum): each in-process
# compile gets its OWN CPU bound = max(LIB_FLOOR_S, LIB_MARGIN x that cell's
# slowest CLI-stage compile CPU), from the CPU file the CLI stage writes (a wall
# hang guard of 10x it rides along, growth_driver.c).  The
# margin covers the sanitizer build's slowdown (ASan+LSan at -O1 is several
# times the plain -O2 CLI) and a loaded box; a cell the CPU file has never
# seen (a --lib run alone) gets the floor.  A cell over its bound is a FAIL
# (a timeout is a crash) and the series stops there with the cell named.
LIB_FLOOR_S, LIB_MARGIN = 300, 20
DEPTH_LIMIT_TEXT = "too deeply nested"      # PCREC_MAX_GROUP_DEPTH's diagnostic
CAPTURING = ("group", "named")              # the matrix kinds whose groups capture (a backreference core needs one)
# NAMED compile-only exceptions (owner ruling limit-cell-matcher-cost, 2026-11-21,
# docs/design/plan_row_bodies/GROWTH-SWEEP.md): a limit cell sits just before a limit whose edge cell
# cannot be built into a matcher.  `compile:norun=NAME` in a cells.tsv row names the exception; the
# runner counts them (every run prints the count) and --list shows each.
NORUN_EXCEPTIONS = {
    "limit-cell-matcher-cost": "NFA-state / VM-node edge with the size limits lifted (raise 1): the emitted C is "
                               "tens of MB (25 MB measured on z_cls 131069; 22 to 119 MB on the matrix `+` edges, "
                               "reached at depth 12-15), gcc -O0 takes about 10 min and 3.4 GB",
}
# A cell with no twin of the other kind across its limit is UNPAIRED; a cells.tsv row declares WHY
# (`none=NAME` in its pair column), so --pairs and the run report list only the unexplained ones.
UNPAIRED_REASONS = {
    "runaway-before-limit": "a memory runaway (K150/K151) starts before any size limit: no just-before cell exists",
    "stability-only-by-ruling": "owner-manager ruling (K156 revision): an ordinary stability test at the shipped limit, no limit half asked",
    "no-depth-half-for-plus": "no `+` cell compiles at depth 250 (a lower limit binds near 12-16): the depth limit has no limit half for `+`",
    "far-limit-differs": "the matrix `+`@250 cell is refused by the replication product, not the edge pair's VM-node limit (a pair names ONE limit)",
}


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


# K157: these matrix `*` limit cells compile at depth 250, but their matcher gives up (exit 3, PCREC_ERR_FRAMES: the
# stamped resume/trail capacity) on 'abc'.  Red kind MATCHER keeps the sweep honest (known_issues K157).
K157_CELLS = {"ncgroup.star.first.bref", "group.star.last.lit", "named.star.last.lit", "inline.star.first.bref"}
K157_RED = "K157:MATCHER"

# Cell ids MEASURED costly by nature (the ruling's "stay costly after the fix"); each needs a measured figure in its comment.
OCCASIONAL_COSTLY = frozenset()

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
        self.kind, self.pair, self.why = kind, pair, ""
        if pair.startswith("none="):
            self.pair, self.why = "", pair[5:]
            if self.why not in UNPAIRED_REASONS:
                sys.exit("run_growth: cell %s: unpaired reason %r is not one of %s" % (cid, self.why, "/".join(sorted(UNPAIRED_REASONS))))
        # a compile-only limit cell is a NAMED exception: `compile:norun=NAME`, NAME in NORUN_EXCEPTIONS
        self.norun = expect.partition("=")[2] if expect.startswith("compile:norun") else ""
        if kind == "limit" and expect != "compile" and not (
                expect.startswith("compile:norun=") and self.norun in NORUN_EXCEPTIONS):
            sys.exit("run_growth: cell %s: a limit cell's expect is `compile` or `compile:norun=NAME` (NAME one of %s), got %r"
                     % (cid, "/".join(sorted(NORUN_EXCEPTIONS)), expect))
        if kind == "limit" and not limit_name:
            sys.exit("run_growth: cell %s: a limit cell names the limit it sits just before" % cid)
        if kind == "stability" and (not expect or any(not a.startswith("refuse:") for a in expect.split(","))):
            sys.exit("run_growth: cell %s: a stability cell's expect is refuse:SUBSTR (the limit's text), got %r" % (cid, expect))
        # OCCASIONAL tier (owner ruling growth-time-bound (3), 2026-11-21): cells MEASURED costly by nature (OCCASIONAL_COSTLY),
        # not in the default tier or the cloud shards; `--tier occasional` runs them with the generous bounds.  EMPTY today:
        # the 107 compile-only cells measured <= 25 s CPU after K159, so they do not qualify (r89 R89-11, ruled 2026-11-23).
        self.occasional = cid in OCCASIONAL_COSTLY
        self.stack, self.raise_, self.features, self.engine = stack, raise_, features, engine
        self.expect, self.limit = expect, limit_name
        # red: "ID:KIND" -> the known issue and the one failure kind it takes
        self.red, _, self.red_kind = red.partition(":")
        if self.red and not self.red_kind:
            sys.exit("run_growth: cell %s: red %r needs a kind (ID:KIND)" % (cid, red))
        if self.red_kind not in ("", "CRASH", "TIMEOUT", "RUNAWAY", "ERROR", "refused", "BUILD", "MATCHER", "compiled"):
            sys.exit("run_growth: cell %s: red kind %r is not a failure kind" % (cid, self.red_kind))
        # the refusal texts a clean refusal of this cell may carry
        self.refusals = []
        for alt in expect.split(","):
            if alt.startswith("refuse:"):
                if not alt[7:]:
                    sys.exit("run_growth: cell %s: empty refuse: substring accepts any refusal" % cid)
                self.refusals.append(alt[7:])


def read_axes():
    ax = {"K": [], "Q": [], "P": [], "C": []}
    for row in tsv(os.path.join(HERE, "matrix_axes.tsv"), {"K": 3, "Q": 3, "P": 4, "C": 4}):
        ax[row[0]].append(tuple(row[1:]))
    return ax


def matrix_parts(kn, kopen, q, ppre, ppost, calts, core, cn):
    """The matrix cell's nest() pieces: (pre, op, core, cl); the one place the product is spelled."""
    a, b = calts.split(",")
    op = kopen + ppre.replace("{A}", a).replace("{B}", b)
    cl = ppost.replace("{B}", b) + ")" + q
    # a `\1` core needs a group 1: the kinds that capture nothing get one in front
    return ("(a)" if cn == "bref" and kn not in CAPTURING else ""), op, core, cl


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
    # plus_edges.tsv: cid, edge E (the deepest `+` nest that compiles), the lower limit that refuses E + 1, its text,
    # then the limit (and text) that refuses the @250 cell
    plus_edges = {r[0]: (int(r[1]), r[2], r[3], r[4], r[5]) for r in tsv(os.path.join(HERE, "plus_edges.tsv"), 6)}
    ax = read_axes()
    for kn, kopen in ax["K"]:
        for qn, q in ax["Q"]:
            for pn, ppre, ppost in ax["P"]:
                for cn, calts, core in ax["C"]:
                    if kn == "lookbehind" and cn == "bref":
                        continue    # PCRE2 refuses a backreference inside a lookbehind: no cell can compile
                    pre, op, core, cl = matrix_parts(kn, kopen, q, ppre, ppost, calts, core, cn)
                    cid = "%s.%s.%s.%s" % (kn, qn, pn, cn)
                    for d in (depth, depth + 1):
                        pat = nest(pre, op, core, cl, "", d)    # nest() repeats `cl` once per level
                        if d > depth:       # past the depth limit: stability (a `+` cell has no limit-test half: unpaired)
                            kind, exp, lim, pair = ("stability", "refuse:" + DEPTH_LIMIT_TEXT, "PCREC_MAX_GROUP_DEPTH",
                                                    "none=no-depth-half-for-plus" if qn == "plus" else "matrix/" + cid)
                        elif qn == "plus":
                            # `+` replicates the body at every level, so a LOWER limit (PCREC_MAX_NFA_STATES or
                            # PCREC_MAX_VM_NODES, limits.md 3.10 para 3) binds near depth 12-16, long before 250.
                            # The @250 cell is sized past THAT limit: a stability twin of the limit cell at the
                            # edge (plus_edges.tsv: the bisected edge E), which is added below with its E+1 twin.
                            # The @251 cell stays a depth-limit stability cell, UNPAIRED: no `+` cell can compile
                            # at 250, so the depth limit has no limit-test half for `+`.
                            # The @250 cell names the limit that REALLY refuses it (plus_edges.tsv far_limit/far_text;
                            # r74 VERDICT-3) and accepts only that text.  The replication product is its own limit, so
                            # where it differs from the edge pair's limit the cell cannot join the pair.
                            e = plus_edges[cid]
                            kind, exp, lim = "stability", "refuse:" + e[4], e[3]
                            pair = "matrix/%s+" % cid if e[3] == e[1] else "none=far-limit-differs"
                        else:
                            kind, exp, lim, pair = "limit", "compile", "PCREC_MAX_GROUP_DEPTH", "matrix/" + cid
                        cells.append(Cell("matrix/%s@%d" % (cid, d), "matrix", pat, budget, 1, "all", 0,
                                          kind, exp, lim, pair, K157_RED if d == depth and cid in K157_CELLS else ""))
                    if qn == "plus":
                        # the `+` limit test just under its lower limit (the bisected edge E) and the exact stability
                        # twin at E + 1; the @250 stability cell above is the same pair's far-past member
                        e, lname, text = plus_edges[cid][:3]
                        for dd, kind, exp in ((int(e), "limit", "compile:norun=limit-cell-matcher-cost"),
                                              (int(e) + 1, "stability", "refuse:" + text)):
                            cells.append(Cell("matrix/%s@%d" % (cid, dd), "matrix", nest(pre, op, core, cl, "", dd), budget, 1,
                                              "all", 0, kind, exp, lname, "matrix/%s+" % cid, ""))
    # --- CELLS: explicit ----------------------------------------------------
    for (cid, fam, pre, unit, sep, mid, unit2, post, n, stack, rz, kind, exp, lim, pair, red) in \
            tsv(os.path.join(HERE, "cells.tsv"), 16):
        if not pair:
            sys.exit("run_growth: cells.tsv: %s: an empty pair column; write `fam/id` or `none=REASON` (%s)" % (cid, "/".join(sorted(UNPAIRED_REASONS))))
        if stack not in ("budget", "main"):
            sys.exit("run_growth: cells.tsv: %s: stack %r is neither `budget` nor `main`" % (cid, stack))
        for nn in n.split(","):
            cells.append(Cell("%s/%s@%s" % (fam, cid, nn), fam,
                              spine(pre, unit, sep, mid, unit2, post, int(nn)),
                              budget if stack == "budget" else 0, int(rz), "all", 0, kind, exp, lim, pair, red))
    return cells


def print_unpaired(unpaired):
    """Unpaired cells by declared reason (one count line each), then every UNEXPLAINED one by name."""
    by = {}
    for c in unpaired:
        by.setdefault(c.why, []).append(c)
    for why in sorted(w for w in by if w):
        print("unpaired, declared (%s): %d cells: %s" % (why, len(by[why]), UNPAIRED_REASONS[why]))
    for c in by.get("", []):
        print("UNPAIRED: %s (%s, limit %s) has no %s twin across the same limit and no declared reason" % (
            c.id, c.kind, c.limit or "-", "limit" if c.kind == "stability" else "stability"))


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
        self.libtotals = {}    # cell id -> SUM of its library-mode compiles' wall seconds
        self.totals = {}       # cell id -> SUM of every CLI-stage run's wall seconds (the cell's cost; --units)
        self.pat_id = {}       # patfile -> cell id
        self.run_cpus = {}     # cell id -> the largest CPU seconds of a run of its built matcher (watchdog's sample)
        self.gcc_cpus = {}     # cell id -> CPU seconds scripts/watchdog saw for the gcc build of the cell's matcher
        self.cpus = {}         # cell id -> the largest compile CPU seconds (user+sys, the driver's own getrusage) of an uncapped run

    def patfile(self, cell):
        return self.patfile_raw(cell.id, cell.pattern)

    def patfile_raw(self, cid, pattern):
        p = os.path.join(self.work, re.sub(r"[^A-Za-z0-9_.@-]", "_", cid) + ".pat")
        self.pat_id[p] = cid
        if not os.path.exists(p):
            with open(p, "w", encoding="utf-8") as f:
                f.write(pattern)
        return p

    def one(self, cell, cap):
        """-> (kind, text): kind in compiled|refused|CRASH|TIMEOUT|RUNAWAY|ERROR."""
        t0 = time.monotonic()
        r = self.one_(cell, cap)
        w = time.monotonic() - t0
        self.totals[cell.id] = self.totals.get(cell.id, 0) + w
        return r

    def drive(self, pf, cap, stack, raise_, features, engine, csrc=None):
        """ONE compile through scripts/watchdog and growth_driver.  -> (kind, text, cpu seconds or None); a TIMEOUT
        names the bound that fired (CPU or the WALL hang guard)."""
        cmd = [self.wd, "-s", str(WALL_S), "-c", str(CPU_S), "-m", RSS, "-i", "0.1",
               "-S", "growth", "-L", os.path.join(self.work, "watchdog.log"), "--",
               self.drv, "one", str(cap), str(stack), str(raise_),
               features or "-", str(engine), pf] + ([csrc] if csrc else [])
        r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        rc = r.returncode
        if rc == 123:
            return "TIMEOUT", "CPU bound: over %d CPU seconds (watchdog -c): a timeout is a crash" % CPU_S, None
        if rc == 124:
            return "TIMEOUT", "WALL hang guard: over %d s elapsed (watchdog -s), under the CPU bound: a hang or a starved box" % WALL_S, None
        if rc == 122:
            return "RUNAWAY", "tree RSS over %s: runaway memory" % RSS, None
        if rc >= 128 or rc < 0:
            return "CRASH", "killed by signal %d" % (rc - 128 if rc > 0 else -rc), None
        m = re.search(r"^rc=(-?\d+) hw=(\d+)(?: cpu=([\d.]+))? msg=(.*)$", r.stdout, re.M)
        if rc != 0 or not m:
            return "ERROR", "driver rc=%d %s" % (rc, (r.stderr or r.stdout).strip()[:120]), None
        cpu = float(m.group(3)) if m.group(3) else None
        if m.group(1) == "0":
            return "compiled", "hw=%s" % m.group(2), cpu
        if m.group(1) == "-9":   # the thread never started: the compile never ran
            return "ERROR", m.group(4), cpu
        return "refused", m.group(4), cpu

    def one_(self, cell, cap):
        pf = self.patfile(cell)
        # a LIMIT cell's uncapped run also emits the artifact's C (with a main()) so its
        # matcher can be built and run: "compiles AND its matcher runs"
        csrc = pf + ".c" if (cell.kind == "limit" and cell.expect == "compile" and cap == 0) else None
        kind, text, cpu = self.drive(pf, cap, cell.stack, cell.raise_, cell.features, cell.engine, csrc)
        if cpu is not None and cap == 0 and cpu > self.cpus.get(cell.id, 0):
            self.cpus[cell.id] = cpu
        if kind == "compiled" and csrc:
            bad = self.matcher(csrc, cell.id)
            if bad:
                return bad
        return kind, text

    def matcher(self, csrc, cid=""):
        """Build the cell's emitted C and run it on SUBJECTS: each run must exit 0 (match) or
        1 (no match), the generated main()'s contract; a crash, a give-up (3) or any other exit
        fails.  -> None, or an outcome (kind, text) with kind BUILD or MATCHER (or TIMEOUT)."""
        exe = csrc[:-2] + ".exe"
        cc = os.environ.get("CC", "gcc")
        wlog = csrc + ".wd.log"     # this build's own watchdog line: its `cpu=` is the number the CPU bound judged
        b = subprocess.run([self.wd, "-s", str(WALL_S), "-c", str(CPU_S), "-m", RSS, "-S", "growth-cc",
                            "-L", wlog, "--",
                            cc, "-O0", "-std=gnu11", "-w", "-o", exe, csrc, "-lm"],
                           capture_output=True, text=True, errors="replace")
        try:
            m = re.search(r" cpu=([\d.]+) ", open(wlog).read())
            if m and cid:
                self.gcc_cpus[cid] = float(m.group(1))
        except OSError:
            pass
        if b.returncode in (122, 123, 124):
            return "TIMEOUT", "gcc on the emitted C over its %s (rc=%d)" % (
                {123: "CPU bound (%d s)" % CPU_S, 124: "WALL hang guard (%d s)" % WALL_S}.get(b.returncode, "RSS bound (%s)" % RSS), b.returncode)
        if b.returncode != 0:
            return "BUILD", "the emitted C did not build: " + (b.stderr or b.stdout).strip()[:160]
        for subj in SUBJECTS:
            mlog = csrc + ".run.log"
            r = subprocess.run([self.wd, "-s", str(MATCHER_WALL_S), "-c", str(MATCHER_CPU_S), "-m", "1g", "-S", "growth-run", "-L",
                                mlog, "--", exe, subj],
                               capture_output=True, text=True, errors="replace")
            try:
                m = re.search(r" cpu=([\d.]+) ", open(mlog).read())
                if m and cid:
                    self.run_cpus[cid] = max(self.run_cpus.get(cid, 0), float(m.group(1)))
            except OSError:
                pass
            if r.returncode in (122, 123, 124):
                return "TIMEOUT", "matcher on %r over its %s (rc=%d)" % (subj, {
                    123: "CPU bound (%d s)" % MATCHER_CPU_S, 124: "WALL hang guard (%d s)" % MATCHER_WALL_S}.get(r.returncode, "RSS bound"), r.returncode)
            if r.returncode not in (0, 1):
                return "MATCHER", "matcher on %r exited %d (0 = match, 1 = no match): %s" % (
                    subj, r.returncode, (r.stdout or r.stderr).strip()[:80])
        return None


def judge(cell, kind, text):
    """The uncapped verdict, by the cell's declared kind (RULING limit-test-criteria).
    -> (good, why)."""
    if kind == "refused" and text.startswith("internal error:"):
        return False, "%s cell: an `internal error:` refusal is a FAIL whatever limit text it holds: %s" % (cell.kind, text)
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
    if text.startswith("internal error:"):
        return False
    return kind == "refused" and ("out of memory" in text or any(r in text for r in cell.refusals))


DEAD = threading.Event()      # set by the first worker that dies: the queued cells are skipped, the pool ends promptly


def safe_job(rn, cell, ladder):
    """job() that cannot raise: an exception becomes a result the ordered loop prints as `FAIL: <cell>: worker died` (r89 R89-2)."""
    if DEAD.is_set():
        return cell, None, 0
    try:
        return job(rn, cell, ladder)
    except Exception as e:
        DEAD.set()
        return cell, "%s: %s" % (type(e).__name__, e), 0


def job(rn, cell, ladder):
    res = [("uncapped", 0) + rn.one(cell, 0)]
    skipped = 0
    for cap in ladder:
        if cap < 2 * len(cell.pattern):
            skipped += 1    # the pattern's own bytes (read before the cap is set) would fill the rung: no thread can start
            continue
        res.append(("cap%dM" % (cap >> 20), cap) + rn.one(cell, cap))
    return cell, res, skipped


def tmp_base():
    return os.environ.get("PCREC_TMPDIR") or os.environ.get("TMPDIR") or "/var/tmp/pcrec-%s" % os.environ.get("USER", "u")


def cpus_path():
    """One CPU file PER TREE (keyed by the tree root): a plant, a worktree and
    main must not bound each other's library-mode compiles (r73 VERDICT-8)."""
    key = hashlib.sha1(ROOT.encode()).hexdigest()[:10]
    return os.environ.get("GROWTH_CPUS") or os.path.join(tmp_base(), "growth-cpus-%s.tsv" % key)


def read_cpus():
    w = {}
    try:
        for line in open(cpus_path()):
            k, _, v = line.rstrip("\n").partition("\t")
            if v:
                w[k] = float(v)
    except OSError:
        pass
    return w


def write_cpus(w):
    old = read_cpus()
    old.update(w)
    with open(cpus_path(), "w") as f:
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
    cpus = read_cpus()
    print("library mode: CPU file %s (%d of %d cells have a CLI-stage compile CPU; the rest get the %ds floor)"
          % (cpus_path(), sum(1 for c in cells if c.id in cpus), len(cells), LIB_FLOOR_S))
    with open(series, "w") as f:
        for c in cells:
            # a known-red cell's UNCAPPED run is a known runaway (K150/K151, NEW-n):
            # it would take the one process down with it; its capped runs stay
            for cap in ([] if c.red else [0]) + ladder:
                bound = max(LIB_FLOOR_S, int(LIB_MARGIN * cpus.get(c.id, 0)) + 1)
                f.write("\t".join([str(cap), "0", str(c.raise_), c.features or "-",
                                   str(c.engine), rn.patfile(c), str(bound)]) + "\n")
                order.append(c.id)
                n += 1
    ctl = os.path.join(rn.work, "control")
    env = dict(os.environ)
    env.setdefault("ASAN_OPTIONS", "detect_leaks=1:allocator_may_return_null=1")
    # the driver's progress goes to a LOG that is readable while it runs (a
    # captured pipe showed nothing for 50 minutes on the first run)
    plog = os.path.join(rn.work, "lib-progress.log")        # this run's own work dir (r74 FIXES-1)
    elog = os.path.join(rn.work, "lib-stderr.log")
    shown = None
    with open(plog, "w") as pf, open(elog, "w") as ef:
        p = subprocess.Popen([rn.wd, "-s", "28800", "-c", "28800", "-m", "6g", "-i", "0.5", "-S", "growth-lib",
                              "-L", os.path.join(rn.work, "watchdog.log"), "--", lib_drv, "lib", ctl, series],
                             stdout=subprocess.PIPE, stderr=ef, text=True, errors="replace", env=env)
        # stream the progress: a `begin` line names the cell as it STARTS, so a job cut by its limit still shows the cell it was on (r89 R89-5)
        for line in p.stdout:
            pf.write(line)
            pf.flush()
            m = re.match(r"begin \d+ bound=\d+ pat=(.*)", line)
            if m and rn.pat_id.get(m.group(1).strip()) != shown:
                shown = rn.pat_id.get(m.group(1).strip(), m.group(1).strip())
                print("library mode: begin cell %s" % shown, flush=True)
        p.wait()
    r = argparse.Namespace(returncode=p.returncode, stdout=open(plog, errors="replace").read(),
                           stderr=open(elog, errors="replace").read())
    print("library mode: progress log " + plog)
    bad = []
    to = [l for l in r.stdout.splitlines() if re.match(r"cell \d+ TIMEOUT ", l)]
    for l in to:
        m = re.match(r"cell (\d+) TIMEOUT (cpu-bound|wall-guard)=(\d+) (?:cpu-bound|wall-guard)=(\d+) pat=(.*)", l)
        bad.append("TIMEOUT (a timeout is a crash): series line %s, cell %s, the %s fired at %ss (its CPU bound is %ss: "
                   "CLI compile CPU x%d, floor %ds; the wall guard is 10x that, capped at 2400 s); series stopped there. progress line: %s"
                   % (m.group(1), rn.pat_id.get(m.group(5), m.group(5)),
                      "CPU BOUND" if m.group(2) == "cpu-bound" else "WALL HANG GUARD", m.group(3),
                      m.group(3) if m.group(2) == "cpu-bound" else m.group(4), LIB_MARGIN, LIB_FLOOR_S, l))
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


# ---- PER-DOUBLING REPORT (owner ruling growth-doubling-report, 2026-11-22) ------------------------------------
# For each growth AXIS (a family at sizes that double), the compile CPU of every size and its ratio to the half-size
# neighbour: about x2 is linear, about x4 quadratic.  A ratio over DOUBLING_RATIO whose larger point costs at least
# DOUBLING_MIN_CPU CPU seconds is a REPORT line (a superlinear compile step surfaces by measurement: the K159 class),
# never a red.  DOUBLING_RATIO 3.0 is x2^1.58, midway between linear and quadratic; DOUBLING_MIN_CPU 0.25 s keeps the
# timer's own noise (a few ms) under 2% of the larger point.  The DOMINANT noise is contention, not the timer: one compile read
# 1.86..3.40 s CPU inside one 8-wide batch (review r89 CPU-2), and -j1 vs -j2 flipped ratios near x3.0 (spine/z_cls 2000: x3.32 vs
# x3.08).  So the report runs SERIAL by default (-j 1; --jobs N overrides, DOUBLING_JOBS in run_growth.sh) and a REPORT line near
# the threshold is a pointer to look, never a verdict: re-run it at -j 1.  REPORT lines are the one output that is not -j-identical.  A point that crashes, times out or runs away IS a FAIL (a timeout
# is a crash), as in the sweep.  The nested-`+` axes double the PATTERN per level (the body is replicated), so their
# neighbour is the previous depth; the spine and depth axes double n.
DOUBLING_RATIO, DOUBLING_MIN_CPU = 3.0, 0.25
DOUBLING_START = 500             # the first n of a spine axis (n, 2n, 4n ... up to the limit cell's n)
DOUBLING_RED_TOP = 4000          # an axis whose cells.tsv row carries a `red` stops here: K148/K150 start near n=8000
DOUBLING_DEPTHS = (16, 32, 64, 128)    # + the depth limit: the matrix depth axes
DOUBLING_PLUS_FIRST = 5          # the first nest depth of a nested-`+` axis, up to its edge E (the pattern doubles per level)
DOUBLING_QUANTS = ("none", "star", "plus", "poss")   # the matrix quantifiers whose depth axis is reported (every construct kind each)
# the position.core rows per quantifier: `+` first and sole (its nest edge E is bisected per row); the others first and last
# (poss.last.lit@250 is the sweep's costliest default-tier compile: 27 s CPU, measured by this lane)
DOUBLING_ROWS = {"plus": ("first.lit", "sole.lit")}
DOUBLING_ROWS_OTHER = ("first.lit", "last.lit")


def doubling_axes(budget, depth):
    """-> [(axis name, [(size, expected growth of the size, pattern, stack, raise)])] in a fixed order."""
    axes = []
    for (cid, fam, pre, unit, sep, mid, unit2, post, n, stack, rz, kind, exp, lim, pair, red) in \
            tsv(os.path.join(HERE, "cells.tsv"), 16):
        if kind != "limit" or "," in n or not unit:
            continue
        top = min(int(n), DOUBLING_RED_TOP) if red else int(n)
        sizes, k = [], DOUBLING_START
        while k <= top:
            sizes.append(k)
            k *= 2
        if len(sizes) >= 3:
            axes.append(("%s/%s" % (fam, cid), [(k, spine(pre, unit, sep, mid, unit2, post, k), budget if stack == "budget" else 0, int(rz))
                                              for k in sizes]))
    ax = read_axes()
    plus_edges = {r[0]: int(r[1]) for r in tsv(os.path.join(HERE, "plus_edges.tsv"), 6)}
    for qn, qsym in ((q[0], q[1]) for q in ax["Q"]):
        if qn not in DOUBLING_QUANTS:
            continue
        for kn, kopen in ax["K"]:
            for pn, ppre, ppost in ax["P"]:
                for cn, calts, core in ax["C"]:
                    if "%s.%s" % (pn, cn) not in DOUBLING_ROWS.get(qn, DOUBLING_ROWS_OTHER):
                        continue
                    pre, op, core2, cl = matrix_parts(kn, kopen, qsym, ppre, ppost, calts, core, cn)
                    cid = "%s.%s.%s.%s" % (kn, qn, pn, cn)
                    if qn == "plus":
                        sizes = list(range(DOUBLING_PLUS_FIRST, plus_edges[cid] + 1))
                    else:
                        sizes = list(DOUBLING_DEPTHS) + [depth]
                    pts = [(d, nest(pre, op, core2, cl, "", d), budget, 1) for d in sizes]
                    axes.append(("matrix/%s" % cid, pts))
    return axes


def doubling_report(rn, budget, depth, jobs, only=""):
    """Run every axis point once (compile CPU from the driver), print the table and the REPORT lines.  -> FAIL count."""
    axes = doubling_axes(budget, depth)
    if only:
        keep = [a for a in axes if any(o in a[0] for o in only.split(","))]
        if not keep:
            sys.exit("run_growth: --doubling-only %r names no axis (axes: %s ...)" % (only, ", ".join(a[0] for a in axes[:6])))
        axes = keep
    pts = [(ai, pi) for ai, (_, pl) in enumerate(axes) for pi in range(len(pl))]

    dead = threading.Event()

    def run(t):
        ai, pi = t
        name, pl = axes[ai]
        size, pat, stack, rz = pl[pi]
        if dead.is_set():
            return "ERROR", "not run: another worker died", None
        try:
            pf = rn.patfile_raw("dbl_%s_%d" % (name, size), pat)
            return rn.drive(pf, 0, stack, rz, "all", 0)
        except Exception as e:     # r89 R89-2: name the point, fail promptly (queued points are skipped)
            dead.set()
            return "ERROR", "worker died: %s: %s" % (type(e).__name__, e), None

    with cf.ThreadPoolExecutor(jobs) as ex:
        res = list(ex.map(run, pts))
    nfail, rep_lines = 0, []
    print("== per-doubling CPU report: %d axes, %d points; ratio = CPU / CPU of the half-size neighbour, per doubling "
          "(~x2 linear, ~x4 quadratic; a step that is not a doubling is normalised by log2 of its size ratio); REPORT when > x%.1f and the larger point >= %.2f CPU s ==" % (len(axes), len(pts), DOUBLING_RATIO, DOUBLING_MIN_CPU))
    print("axis\tsize\tcpu_s\tratio\toutcome")
    k = 0
    for name, pl in axes:
        prev = None
        for size, pat, stack, rz in pl:
            kind, text, cpu = res[k]; k += 1
            if kind in ("CRASH", "TIMEOUT", "RUNAWAY", "ERROR", "refused"):
                # a REFUSED point is a FAIL too: every axis point sits at or under its family's compiling edge, so a refusal
                # is a limit firing early, and a ratio across it means nothing (r89 R89-14)
                nfail += 1
                print("FAIL: %s size %d: %s: %s" % (name, size, kind, text))
                prev = None
                continue
            if cpu is None:
                prev = None     # no CPU figure (an old driver): never pair the next point with a 4x neighbour
                print("%s\t%d\t-\t-\t%s" % (name, size, kind))
                continue
            # the ratio is normalised to a size doubling: ratio^(1/log2(size ratio)), so a x1.95 step (128 -> 250 depth) reads as a doubling
            ratio = None
            if prev and prev[1] > 0:
                lg = math.log2(size / prev[0]) if size >= 1.5 * prev[0] else 1.0    # nested-`+` levels (n, n+1) double the pattern: raw
                ratio = (cpu / prev[1]) ** (1.0 / lg) if cpu > 0 else None
            print("%s\t%d\t%s\t%s\t%s" % (name, size, "%.3f" % cpu if cpu is not None else "-",
                                          "x%.2f" % ratio if ratio else "-", kind))
            if ratio and ratio > DOUBLING_RATIO and cpu >= DOUBLING_MIN_CPU:
                rep_lines.append("REPORT: superlinear step on %s at size %d: x%.2f of size %d (%.2f s vs %.2f s CPU; threshold x%.1f at >= %.2f s)"
                                 % (name, size, ratio, prev[0], cpu, prev[1], DOUBLING_RATIO, DOUBLING_MIN_CPU))
            prev = (size, cpu)
    for l in rep_lines:
        print(l)
    print("per-doubling report: %d points, %d REPORT line(s), %d failed point(s)" % (len(pts), len(rep_lines), nfail))
    return nfail


def main():
    global CPU_S, WALL_S
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("-j", "--jobs", type=int, default=0, help="cells run at once (default nproc/2: a cell can hold GBs; ordered output; -j 1 is the serial control)")
    ap.add_argument("--tier", choices=("default", "occasional", "all"), default=os.environ.get("GROWTH_TIER", "default"),
                    help="default = every cell but the OCCASIONAL ones (the cloud shards' tier); occasional = the named compile-only "
                         "exceptions with the generous bounds (docs: tests/growth/CLAUDE.md); env GROWTH_TIER")
    ap.add_argument("--cells", default="", metavar="ID[,ID]", help="only these cell ids (after the tier and shard selection)")
    ap.add_argument("--bounds", action="store_true", help="print each time bound's value and where it was derived, then exit")
    ap.add_argument("--doubling", action="store_true", help="the per-doubling CPU report (REPORT lines, never a red), then exit")
    ap.add_argument("--doubling-only", default="", metavar="SUBSTR[,SUBSTR]", help="with --doubling: only the axes whose name contains one of these")
    ap.add_argument("--no-ladder", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--lib", action="store_true")
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--verbose", action="store_true", help="print every uncapped outcome")
    ap.add_argument("--pattern", default="", help="print the pattern of the cell with this id and exit")
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
            print("UNPAIRED\t%s\t%s\t%s\t%s" % (c.id, c.kind, c.limit or "-", c.why or "UNEXPLAINED"))
        print("# %d pairs, %d unpaired cells, %d limit cells, %d stability cells" % (
            len(pairs), len(unpaired), sum(c.kind == "limit" for c in cells), sum(c.kind == "stability" for c in cells)))
        return 0
    if a.tier != "all":
        cells = [c for c in cells if c.occasional == (a.tier == "occasional")]
    if a.shard_check:
        return 1 if shard_check(cells, a.table) else 0
    if a.shard and a.tier == "occasional":
        sys.exit("run_growth: --shard and --tier occasional do not combine: the cloud table covers the default tier only")
    if a.shard:
        cells = shard_cells(cells, a.shard, a.table)
        print("shard %s: %d of the sweep's cells (table %s)" % (a.shard, len(cells), os.path.relpath(a.table, ROOT)))
    if a.depth_only:
        a.only, a.no_ladder = "depth", True
    if a.only:
        keep = set(a.only.split(","))
        known = {c.family for c in cells}
        if keep - known:
            sys.exit("run_growth: --only names no family: %s (families: %s)" % (",".join(sorted(keep - known)), ",".join(sorted(known))))
        cells = [c for c in cells if c.family in keep]
    if a.cells:
        want = set(a.cells.split(","))
        if want - {c.id for c in cells}:
            sys.exit("run_growth: --cells names no cell in this tier: %s" % ",".join(sorted(want - {c.id for c in cells})))
        cells = [c for c in cells if c.id in want]
    if not cells:
        sys.exit("run_growth: no cells selected")
    if a.list:
        fams = {}
        for c in cells:
            fams[c.family] = fams.get(c.family, 0) + 1
        for c in cells:
            print("%s\t%s\t%s\t%s" % (c.id, c.kind, c.expect, c.red))
        print("# compile-only exceptions in this tier: %d (%s)" % (sum(bool(c.norun) for c in cells),
              ", ".join("%s: %s" % (n, NORUN_EXCEPTIONS[n]) for n in sorted(NORUN_EXCEPTIONS))))
        print("# %d cells (%d limit, %d stability): %s" % (len(cells), sum(c.kind == "limit" for c in cells),
              sum(c.kind == "stability" for c in cells), ", ".join("%s %d" % kv for kv in sorted(fams.items()))))
        return 0
    if a.bounds:
        print("tier default: CPU %d s, WALL %d s; tier occasional: CPU %d s, WALL %d s\n%s" % (CPU_S, WALL_S, OCC_CPU_S, OCC_WALL_S, BOUNDS_BASIS))
        return 0
    base = tmp_base()
    os.makedirs(base, exist_ok=True)
    work = tempfile.mkdtemp(prefix="growth-", dir=base)
    if not a.keep:      # whatever ends the run (an exception, sys.exit, a dead worker) removes the work dir (r89 R89-2)
        atexit.register(lambda: subprocess.run(["rm", "-rf", "--", work]))
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
    if a.tier == "occasional":
        CPU_S, WALL_S = OCC_CPU_S, OCC_WALL_S
    print("growth: tier %s; time bounds: CPU %d s (watchdog -c), WALL hang guard %d s (watchdog -s); basis: BOUNDS_BASIS in run_growth.py (--bounds)"
          % (a.tier, CPU_S, WALL_S))
    if a.doubling:
        jb = a.jobs or 1      # a measurement: serial by default (DOUBLING_RATIO's comment)
        nf = doubling_report(rn, budget, depth, jb, a.doubling_only)
        subprocess.run(["rm", "-rf", "--", work])
        return 1 if nf else 0
    if a.selftest:
        return selftest(rn, budget, depth)
    ladder = [] if a.no_ladder else LADDER
    if a.lib:
        nbad = lib_mode(rn, cells, ladder)
        if a.units:
            write_units(a.units, rn)
        return 1 if nbad else 0
    jobs = a.jobs or max(1, (os.cpu_count() or 4) // 2)
    npass = nfail = nred = nfixed = nskip = 0
    fam = {}
    with cf.ThreadPoolExecutor(jobs) as ex:
        for cell, res, skipped in ex.map(lambda c: safe_job(rn, c, ladder), cells):
            st = fam.setdefault(cell.family, [0, 0, 0, 0])
            if res is None:     # skipped after a worker died: not run, not counted as a pass
                continue
            if isinstance(res, str):
                nfail += 1; st[1] += 1
                print("FAIL: %s: worker died: %s" % (cell.id, res))
                continue
            nskip += skipped
            if ladder and skipped == len(ladder):
                # a ladder cell with no rung runs nothing of the ladder: a green that tested nothing (learnings 3)
                nfail += 1; st[1] += 1
                print("FAIL: %s: every ladder rung was skipped (pattern %d bytes, smallest rung %d)" % (cell.id, len(cell.pattern), ladder[0]))
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
    write_cpus(rn.cpus)
    if a.units:
        write_units(a.units, rn)
    print("CPU file %s: %d cells" % (cpus_path(), len(rn.cpus)))
    # the CPU the bounds judge: compile CPU (the driver's own rusage) and gcc CPU (watchdog's tree sample), the slowest cells
    cost = sorted(((rn.cpus.get(i, 0.0) + rn.gcc_cpus.get(i, 0.0), i) for i in set(rn.cpus) | set(rn.gcc_cpus)), reverse=True)
    if cost:
        print("CPU: slowest cells by uncapped CPU (compile + gcc matcher build), bound %d s: %s" % (
            CPU_S, "; ".join("%s %.1f s (compile %.1f, gcc %.1f)" % (i, c, rn.cpus.get(i, 0), rn.gcc_cpus.get(i, 0)) for c, i in cost[:5])))
        mc, mg, mr = max(rn.cpus.values(), default=0), max(rn.gcc_cpus.values(), default=0), max(rn.run_cpus.values(), default=0)
        print("CPU: bound headroom, per bound (each is applied to one process tree alone): compile max %.1f of %d s (%.0f%%); "
              "gcc build max %.1f of %d s (%.0f%%); matcher run max %.2f of %d s (%.0f%%)" % (
                  mc, CPU_S, 100.0 * mc / CPU_S, mg, CPU_S, 100.0 * mg / CPU_S, mr, MATCHER_CPU_S, 100.0 * mr / MATCHER_CPU_S))
    print("== Growth sweep ==")
    for f, (p, fl, rd, fx) in sorted(fam.items()):
        print("family %-8s runs passed %d  failed %d  known-red %d  fixed-red %d" % (f, p, fl, rd, fx))
    print("runs passed: %d" % npass)
    print("runs failed: %d" % (nfail + nfixed))
    print("runs known-red: %d" % nred)
    if ladder:
        print("ladder rungs skipped (cap under twice the pattern's bytes): %d of %d" % (nskip, len(ladder) * len(cells)))
    sel = {c.id for c in cells}
    exc = [c for c in cells if c.norun]
    print("compile-only exceptions: %d limit cells (matcher not built; named in cells.tsv): %s" % (
        len(exc), ", ".join("%s=%d" % (n, sum(c.norun == n for c in exc)) for n in sorted(NORUN_EXCEPTIONS))))
    print_unpaired([c for c in unpaired if c.id in sel])
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
    return ("pattern %d bytes; scripts/watchdog -s %d -c %d -m %s -- growth_driver one %d %d %d %s %d <patfile> (run_growth.py --only %s --keep)"
            % (len(cell.pattern), WALL_S, CPU_S, RSS, cap, cell.stack, cell.raise_, cell.features or "-", cell.engine, cell.family))


if __name__ == "__main__":
    sys.exit(main())
