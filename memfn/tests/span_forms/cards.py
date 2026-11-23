#!/usr/bin/env python3
# SPDX-License-Identifier: 0BSD
# Provenance: original pcrec-memory-functions text (lane forms, R-45 plan A; lane formsfixa,
# review 2026-11-17 r35's F2-F11; lane formsfixc, review r36's G2-G8 and rulings R1; lane formsfixe,
# review r37's H1-H4, H7: the twin term, the agreement gate, the pool record and reach refusals;
# lane formsfixg, review r38's J1, J2, J7, J8: the per-pattern twin term, the launch rounds, the
# class drill, the identity reach per source; lane formsfixi, review r39's K1-K6, K8, K12: the layout
# twins, R0 over the confirm, reading B, one owed list, the checked controls; lane formsfixk, review
# r41's L9, L5, L6: the layout pools replace the twins, the strict arguments and the keyed G2 record;
# lane formsfixl, review r44's A-L: the variant x regime interaction void, the per-head layout floor,
# the pool refusal's 32-B half, the confirm's rounds, a fresh run id, the compiler-keyed exe cache,
# K6's placed win, the power line's bracket, the checked power pins, the fixed axes named; lane formsfixm,
# review r45's FORMS8-1..5: the interaction test per text, winsorized, the POOL_SIZE refusal, the docs).
"""memfn/tests/span_forms/cards.py -- THE SPAN FORMS' CARDS C1-C5, their rule R0-R5 and the
identity check; and CARD C6 `span_vector` (+ C6c, the SIMD-off layer under clang -O2 and gcc -Os; R-47 U5,
block_span.md §8, kit-grid@8: V against `--memfn=no-span-vector` on one binary, patterns, widths and regimes
declared below, THE RULE the committed c6_rule.md beside this file (review r79); `plan` and
`dry [--cards C6,C6c]` read it, `c6selftest [RUNDIR]` drills its verdict, `time` (U6) times it and
`c6decide` reads its record; a timing is owed to a window main clears, on every bench box that runs V; UNMEASURED) (docs/design/memfn/r45_reply.md rev 11 §3 "The cards", "The head `h` and the
default", "The head lever and its identity check"; cards kit-grid@7 in
memfn/data/cards/kit-grid.tsv).

The kit's measurement script for the forms I / L / H(h) (memfn/src/window.c, THE SPAN FORMS).
Every cell compiles a card pattern at PCREC level on ONE binary (the frozen combined-branch
build), h set through the TEST-ONLY lever (`build/pcrec-harness --harness=span-head=N`, never a
shipped compile), I as the deny `--memfn=no-span-loop`, the engine route (C5) as
`--memfn=no-window-search`; the artifact plus one find-all wrapper is one C file per cell, its
answers gated against python `re` before any timing.

THE NIGHT (r45_reply rev 11 §3 "the night order"; each step a command, RUNDIR one directory):
  plan                     every cell (card, pattern, arm, regime, layer), the counts and the
                           EXPECTED WALL TIME of each timing step (UNMEASURED constants, named)
  dry RUNDIR [--quick] [--cards C6,C6c]
                           builds EVERY cell (--cards: only the named cards' cells, a PARTIAL dry: the C1-C5 deny checks and the
                           identical-to-I record are the full dry's) (compile, gcc, the gate on every regime's
                           subject; C4's size record at the grid top) and prints the cell list
                           and count; no clock
  run RUNDIR [--with-approx]
                           step 1: times C1, C2, C5 and the A/A cells (results.tsv), each
                           cell in ROUNDS of one launch per arm (rev 10, r38 J2); every launch
                           runs a variant drawn from its arm's LAYOUT POOL (rev 12, r41 L9: an
                           in-TU prelude and an alignment variant; the draw recorded per launch
                           in the row's `variants`); the A/A pair is aa and aa.b, two arms of
                           aa's pool. Writes a FRESH RUNDIR/run_id. Regimes
                           the kit only APPROXIMATES are void by method (rev 7, F8) and are not
                           timed unless --with-approx (a record only; the rule never reads them)
  rerun RUNDIR [--g2 FILE] re-times what `rule` OWES, computed by the SAME function with the
                           same recorded G2 list (rev 11, r39 K6): every cell VOID ONCE (all
                           its arms) into results_rerun.tsv / results_c3_h<H>_rerun.tsv (rev 7,
                           F7); once none is void, the CONFIRM: each cell holding a head's win
                           beyond f, I and each winning head on FRESH launch draws of the
                           SAME pools, into results_confirm.tsv (round 1) or
                           results_confirm_r<K>.tsv (round K, r44 D) (rev 10 R2; rev 12 r41 L9)
  rule RUNDIR [--g2 FILE]  R0-R5: the floor, h*, its label, the filings; exit 0 complete,
                           2 the night is void or defective, 3 a step is owed (a re-run, a
                           confirm, or C3 at h*); the line `rule: NEXT ...` names it. --g2
                           FILE (one G2-defective head a line) is RECORDED in
                           RUNDIR/rule_g2.json keyed by the run id and the file's sha-256;
                           every later `rule`/`rerun` reads the record; a record of another
                           run, a moved file, an unknown option or a valueless --g2 refuse
                           (exit 2; rev 12, r41 L6)
  c3 RUNDIR H              step 2b: times C3 at I, L and H(H) (results_c3_h<H>.tsv) and records
                           C4's sizes at H (sizes_h<H>.tsv); run at the h* `rule` picked (F4)
  selftest [--rev11] [--rev12]   (the full selftest is SLOW: ~90 min alone on the dev box, formsfixm 2026-11-17; bound
                                  it at >= 7200 s, never 3000 s: bsu5's 3000 s run timed out, review r79 R-1)
                           the rule against every drill r45_reply rev 11 §3 lists, plus the noise
                           drill (F2), the unimodal drill (F3), the void/R0/re-run drills, the
                           CLASS drill (r38: noise, a step and a drift at every level) and rev
                           11's rows (r39: per-exe offsets, reading B's power, R0 over the
                           confirm, one owed list) and rev 12's (r41: the layout pools under
                           each layout model, GAP_K under layout bimodality, the power rows;
                           r44: the interaction and noisy-loser drills, each with its control;
                           r45: heterogeneous noise under layout, the POOL_SIZE refusal);
                           --rev11 / --rev12 run those rows alone
  time RUNDIR [--cards C6,C6c] [--deadline EPOCH|+SECONDS] [--dry [--dry-model tie|exercise] [--patterns P,..]]
                           C6/C6c's TIMER (R-47 U6; c6_rule.md, every clause): the C6 text check, the reach build (N/A),
                           every pool BUILT and PROVED before the clock (the first pass's and the re-time's fresh pool,
                           arm_pool), the record's head (`#c6` header, the population with its span calls), the
                           CPU-QUIET CONTROL's sample (rule_710.md, ported here), the first pass (time_cells: rounds of one
                           launch per arm, each on its arm's own pool, the draw recorded; a void launch re-timed up to 2
                           more times), the RE-TIME of every reading WIN/LOSS and A/A non-TIE (all three arms, fresh pool,
                           fresh draws), no cell started at or after --deadline (NOT-RUN), `#end`; then c6decide on the
                           file. Exit 0, 1 a gate failed, 2 refused, 4 TRUNCATED. --dry runs NO launch: the clock and any
                           taskset/CARD_TIME exec raise (dry_guard), the readings are DRY_MODELS' synthetic values, the
                           wall simulated; --patterns limits a dry's population (a lane's proof under the compile cap)
  c6decide RESULTS         THE VERDICT (c6_rule.md VERDICT and REPORTED) from a `time` record alone; refuses a missing
                           or stale `#c6` header, a record without `#end`, and a re-time set that the first pass does not
                           owe (or owed and lacks)
  identity H [PATTERNS]    step 3: the lever at H on the FROZEN pcrec-harness against the
                           REBUILT build/pcrec, byte for byte, both encodings, both layers,
                           over the card patterns, the census covers (read from the sweep's own
                           corpus) and the PATTERNS file (main's predicted movers, one a line;
                           REQUIRED when H < 64)

Env: PCREC_TREE (default: this file's tree), FROZEN (the frozen tree's build dir; REQUIRED by
`identity`, default the tree's build/ elsewhere), REBUILT (identity's rebuilt build dir, default
the tree's build/), WIDTH_FLAG (default `--window-search-width=4095`; `none` on a tree without
main's width option), CPU (taskset core, default 15), LAUNCHES (default 5), JOBS.
"""
import functools, hashlib, json, math, os, random, re, resource, statistics, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.environ.get("PCREC_TREE") or os.path.normpath(os.path.join(HERE, "..", "..", ".."))
BUILD = os.environ.get("FROZEN") or os.path.join(TREE, "build")
HARNESS = os.path.join(BUILD, "pcrec-harness")
PCREC = os.path.join(BUILD, "pcrec")
WIDTH_FLAG = os.environ.get("WIDTH_FLAG", "--window-search-width=4095")
CPU = os.environ.get("CPU", "15")
LAUNCHES = int(os.environ.get("LAUNCHES", "5"))
PREFIX = "rxa"
CC = os.environ.get("CC", "gcc")

# ---- the grid and the arms (r45_reply §3 "The grid") ----------------------------------------
# The DEFAULT candidates are the FINITE heads; I (h >= k) is timed in every cell as the
# reference, never a candidate. UNMEASURED: the grid is CHOSEN (r45_reply §3).
GRID = [0, 1, 2, 4, 8, 16, 24, 32, 64]
GRID_TOP = 64
SIMD = "-fmemfn-simd=x86-64-v3"
CLANG = os.environ.get("CLANG", "clang")
# THE LAYER TABLE (R-47 U5; review r79 F3, F13): one row per layer, every fact of a layer a DECLARED COLUMN, never read off
# its name: the pcrec flags (the SIMD switch), the COMPILER (a row of COMPILERS, below: its command), the optimization
# level and the pool's ALIGNMENT VARIANTS (a row of ALIGNS, below: a level that aligns nothing, -Os, needs another odd
# variant). Read through `layer_flags` (artifact), `layer_simd` (check_c6), `cc_of`, `opt_of` and `align_variants_of`
# (build_cell, its pool and its exe key; dry's pool proof) only. C1-C5 iterate LAYERS, the off/on subset (unchanged).
# C6's compiler-axis card C6c reads the two SIMD-off legs of plan row [BSPAN-CLANG-DIFF] the bench has an arm for: clang -O2
# (pcrec-auto-clang and siblings) and gcc -Os (pcrec-auto-os). clang -O3 has no bench arm and no row here, and every cell is
# a non-PIC executable where the bench builds `-O2 -fPIC -shared`: both named gaps (c6_rule.md CLAIM, block_span.md §8).
LAYER = {
    # name:      (pcrec flags, compiler, level, alignment variants)
    "off":       ([],     "gcc",   "-O2", "gcc"),
    "on":        ([SIMD], "gcc",   "-O2", "gcc"),
    "off-clang": ([],     "clang", "-O2", "clang"),
    "off-os":    ([],     "gcc",   "-Os", "gcc-Os"),
}
LAYERS = {ly: LAYER[ly][0] for ly in ("off", "on")}     # C1-C5's layers

# ---- the rule's statistical constants (r45_reply rev 11 §3 "The floor `f`", "Void") ----------
# ALPHA: the rule's FAMILY-WISE false-pick budget, CHOSEN = the acceptance r35 F2 ruled (P(h* !=
# 64 on pure noise) <= 5 %). The floor is sized so that ALL the per-cell comparisons together
# show a false win beyond f with probability at most ALPHA (one-sided Bonferroni over N).
ALPHA = 0.05
# SIGMA_CONF: the one-sided confidence of the upper bound on the A/A sigma (12 cells estimate
# it; the bound pays for that estimate's own noise). CHOSEN.
SIGMA_CONF = 0.95
# GAP_K: a timed arm is BIMODAL when its launches split into two groups of >= 2 each with a gap
# of more than GAP_K launch sigmas between them (rev 7, F3). CHOSEN from a 2e7-sample simulation
# of 5 launches (lane formsfixa): P(gap > 4.5 sigma) is 1e-7 per arm under normal noise; under
# t(5) noise about 3e-5 per arm (r36 SIMULATE-7: the pooled sigma reads 0.908 of the true one,
# so the effective gap is ~4.1 true sigmas), consistent with the unimodal drill's 2-3 % of
# nights; its bimodal control shows the test can fire. A split that MOVES a median (3 of 5) at
# sizes f..2f is below any 5-launch gate at that false rate (rev 8 §3 "Bimodal"); I's POOLED
# reading carries that case (rulings R1).
GAP_K = 4.5
# MED_SD5: the median of the sample SD of 5 normal draws, in sigma units: sqrt(median
# chi2(4) / 4) = sqrt(3.3567 / 4). DERIVED. The launch sigma of a (regime, layer) pool is the
# median of its arms' launch SDs over this constant (a median, so one bimodal arm cannot
# inflate the pool's own scale).
MED_SD5 = 0.9161
# MIN_POOL: a pool with fewer timed arms borrows the night's pooled scale (for the bimodal test;
# the floor takes the larger of the two). CHOSEN; unreachable on a real night (92-105 arms a pool).
MIN_POOL = 10
# THE PER-POOL FLOOR TERM (rev 8, r36 G2). SDMED5: the SD of the median of 5 standard normal
# draws, sqrt(0.2868) (order-statistic tables; 0.5355 by 4e6 draws). DERIVED. A ratio of two
# arms' medians then has log SD sqrt(2) x SDMED5 x the pool's launch sigma.
SDMED5 = 0.5355
# MEDSD_REL: the relative standard error of the pool's sigma (a median of n launch SDs over
# MED_SD5), 1 / (2 f(m) m) per sqrt(n), f the density of a 5-draw SD at its median m: f(m) =
# chi2(4)'s density at 4 m^2 times 8 m = 1.148, so 1 / (2 x 1.148 x 0.9161) = 0.4754. DERIVED
# (asymptotic in n; a pool holds ~100 arms).
MEDSD_REL = 0.4754


# ---- LAYOUT POOLS: SETUP RANDOMIZATION of every arm's layout (rev 12, RULED r41 L9) ----------
# Rev 11's layout twins (I.lt, aa-twin, the confirm's I.cf / h<N>.cf) were the same object code
# linked behind a pad object, a whole-.text shift by a multiple of the TU's alignment: every twin
# kept its base's 32-B phase and its relative layout (r41 L1), so the night's between-exe estimate
# read a lower bound of unknown tightness (r41 L2). Rev 12 replaces them: every arm's TEXT (I, each
# head, aa, the engine route, C3's arms) is linked as a POOL of POOL_SIZE layout VARIANTS, each its
# own compile of the TU with
#   (1) an IN-TU PRELUDE: a top-level `.skip 16 x j` in .text AHEAD of the artifact, so the TU's own
#       .text alignment cannot absorb it (the artifact's functions and its driver move by 16 j inside
#       one aligned TU: their 16-B phase is kept, their 32-/64-B phase moves); and
#   (2) an ALIGNMENT VARIANT: the odd variants compile with gcc's function/loop/jump/label alignment
#       off (ALIGN_VARIANTS[1]): the SAME instruction stream with other alignment padding, so another
#       RELATIVE layout (r44 H: one gcc -O2 does not ship; the even pair's is the default build's). Odd
#       variants' function entries are NOT 16-B aligned (r44 G: `-fno-align-functions` puts
#       `rxa_search` off the 16-B grid); the prelude moves them by its own 16 j all the same.
# Every LAUNCH draws one variant of its arm's pool (`launch_variant`: a hash of the night's run id,
# the arm cell and the round, recorded per launch in the results row's `variants` column), so
# layout noise is iid in every comparison by construction and the median averages it at zero extra
# launches (links only). Every variant is answer-gated (`dry`, and `prepare_cell` before timing);
# `dry` prints each pool's phase spread (nm / objdump of the built exes, never counts) and REFUSES
# a pool whose variants share one 64-B phase or one relative layout, whose variants of one relative
# layout share a 32-B phase vector, or that holds fewer than POOL_SIZE distinct built layouts (r44 C).
# Hash-equal arms (a head whose text is I's) share I's pool: one text, one pool.
# FIXED AXES (r44 F): a pool moves CODE placement only. In every variant of every text the data stay
# put: the matcher's .rodata tables, .data/.bss, the driver's `main`, and the subject buffer (malloc'd,
# 16 mod 64 on this box's glibc for the whole-buffer and not-warm regimes; short-subject record starts
# vary by record but not by variant). A share common to every variant of a text therefore also holds
# THIS harness's data placement, which a user's binary does not share.
# UNMEASURED DEFAULT: POOL_SIZE = 4 (one variant per 16-B phase mod 64, two of each alignment). FIXED at 4
# (r45 FORMS8-2): PHASE_ORDER strides four 16-B phase classes and ALIGN_VARIANTS two, so at 8 variant v + 4
# repeats v's class and flags and r44 C's 32-B and distinct-layout clauses refuse EVERY pool (`dry` exits 1
# for the whole night); any other value is refused at start (`pool_size_refusal`), never run.
POOL_SIZE = int(os.environ.get("POOL_SIZE", "4"))


def pool_size_refusal(n):
    """Why a POOL_SIZE `n` cannot run (r45 FORMS8-2), or None: the 32-B guard and the stratified preludes
    are built for exactly four phase classes."""
    if n != 4:
        return ("POOL_SIZE=%d: the pool is built for exactly 4 variants (PHASE_ORDER strides four 16-B phase "
                "classes, ALIGN_VARIANTS two alignments; at 8 every pool repeats a layout and r44 C's clauses refuse "
                "it, below 4 a phase class is never timed); unset POOL_SIZE" % n)
    return None
# UNMEASURED DEFAULT: the prelude's draw space, j in 0..255 (16-B steps mod 4096). STRATIFIED: variant
# v takes the 16-B phase class (r + PHASE_ORDER[v mod 4]) mod 4 (r drawn per pool), a random multiple
# of 64 B above it, so the PRELUDES of a pool of 4 span the four 16-B phases mod 64 by construction.
# What that buys each hot loop (r44 G, as built): each RELATIVE layout (alignment variant) is timed at
# TWO 64-B classes 16 B apart (classes r, r + 1 for the even variants, r + 2, r + 3 for the odd), never
# all four; and the two variants of each alignment differ by 16 B mod 32 (the selftest's 32-B row and
# the refusal's 32-B half are the checks): with (r + v) mod 4 they differed by 32 B, so a TU whose
# .text gcc aligns to 32 kept every hot loop's 32-B phase in 18 of 80 pools (the formsfixk dry run).
PHASE_ORDER = (0, 2, 1, 3)
PRELUDE_STEPS = 256
# UNMEASURED DEFAULT: the alignment variants (variant v takes ALIGN_VARIANTS[v % 2]). The odd variant
# turns off every gcc alignment of code, x86's tight-loop alignment too (`-mtune-ctrl=^align_tight_loops`,
# gcc 15 x86 only: it pads a small hot loop to 32 B whatever -fno-align-loops says; without it 18 of 80
# pools kept every hot loop's 32-B phase, the formsfixk dry run).
ALIGN_VARIANTS = ([], ["-fno-align-functions", "-fno-align-loops", "-fno-align-jumps", "-fno-align-labels",
                       "-mtune-ctrl=^align_tight_loops"])
# The ALIGNMENT VARIANT under clang (C6c; UNMEASURED DEFAULT, chosen by `dry`'s pool proof, which refuses a pool whose
# variants share one relative layout): gcc's list above does not exist in clang (`-mtune-ctrl`, the loop/jump/label
# alignment switches). The odd variant turns clang's function alignment off and its loop alignment off (LLVM's x86 default
# aligns loops and functions to 16 B): `-fno-align-functions` and `-mllvm -x86-experimental-pref-innermost-loop-alignment=0`.
CLANG_ALIGN_OFF = ["-fno-align-functions", "-mllvm", "-x86-experimental-pref-innermost-loop-alignment=0"]
# The ALIGNMENT VARIANT at gcc -Os (C6c's `off-os`; UNMEASURED DEFAULT, accepted by `dry`'s pool proof): -Os aligns
# nothing, so gcc's alignment-OFF list builds the default's layout again and the pool proof refuses every -Os pool (one
# relative layout); the odd variant turns alignment ON instead, to 16 B (at 32 B every loop head sits at 32-B phase 0 in
# both odd variants and the proof's 32-B half refuses the pool), the same instruction stream with other padding.
ALIGN_OS_ON = ["-falign-functions=16", "-falign-loops=16", "-falign-jumps=16", "-falign-labels=16"]
# THE COMPILER ROWS and THE ALIGNMENT ROWS the layer table names (variant v takes the row's [v % 2])
COMPILERS = {"gcc": CC, "clang": CLANG}
ALIGNS = {"gcc": ALIGN_VARIANTS, "clang": ([], CLANG_ALIGN_OFF), "gcc-Os": ([], ALIGN_OS_ON)}


def layer_flags(layer):
    """The layer's pcrec flags (LAYER's first column)."""
    return LAYER[layer][0]


def layer_simd(layer):
    """1 iff the layer compiles with the SIMD switch on (read off its flags, never its name)."""
    return SIMD in LAYER[layer][0]


def cc_of(layer):
    """The command of the layer's compiler (LAYER's second column, a COMPILERS row)."""
    return COMPILERS[LAYER[layer][1]]


def opt_of(layer):
    """The layer's optimization level (LAYER's third column)."""
    return LAYER[layer][2]


def align_variants_of(layer):
    """The alignment variants of the layer's pools (LAYER's fourth column, an ALIGNS row)."""
    return ALIGNS[LAYER[layer][3]]


# AN ARM'S OWN POOL (review r79 F2): an A/A arm whose comparison moves the LAYOUT POOL axis draws a pool of its OWN: H64.b
# times H64's text, but V vs H64 compares two pools, so the A/A arm compares two pools too (salted; c6_rule.md A/A). The
# AA card's aa.b keeps aa's pool (r41 L9, unchanged). RETIME_SALT: a re-time builds a FRESH pool (c6_rule.md RE-TIME), four
# new layouts per text, never the first pass's.
POOL_SALT = {"H64.b": "aa"}
RETIME_SALT = "retime"


def pool_salt(arm, retime=0):
    """The pool salt of arm `arm` (POOL_SALT) at re-time round `retime` (0: the first pass)."""
    parts = [POOL_SALT.get(arm, "")] + (["%s%d" % (RETIME_SALT, retime)] if retime else [])
    return "|".join(x for x in parts if x)


def pool_variants(textkey, aligns=ALIGN_VARIANTS, salt=""):
    """The pool of the TEXT `textkey` (the hash of its TU): [(v, prelude bytes, compile flags)], drawn
    from the text's hash (one text, one pool, every night: the draws are the night's); `aligns` the
    layer compiler's alignment variants; `salt` (pool_salt) draws ANOTHER pool of the same text."""
    hd = hashlib.sha256(("pool|%s" % textkey + ("|" + salt if salt else "")).encode()).digest()
    r = hd[0] % 4
    out = []
    for v in range(POOL_SIZE):
        hi = hd[1 + v % 31] % (PRELUDE_STEPS // 4)
        j = 4 * hi + (r + PHASE_ORDER[v % 4]) % 4
        out.append((v, 16 * j, aligns[v % 2]))
    return out


def arm_pool(key, layer, arm, retime=0):
    """The pool arm `arm` draws for text `key` at `layer` (pool_variants under the arm's salt), at re-time round `retime`.
    A RE-TIME pool is FOUR NEW LAYOUTS (c6_rule.md RE-TIME: "never the first pass's"): the salted draw is redrawn
    (`|redraw<t>`, t = 1, 2, ..) until no variant repeats a (prelude, flags) of any first-pass pool of the same text (every
    arm salt), since one salted draw collides with a first-pass variant with probability about 1 in 64 per variant, and a
    collision is the SAME exe (build_cell's cache name is the text, prelude and flags)."""
    aligns = align_variants_of(layer)
    if not retime:
        return pool_variants(key, aligns, pool_salt(arm))
    first = {(pre, tuple(fl)) for salt in {""} | set(POOL_SALT.values()) for _v, pre, fl in pool_variants(key, aligns, salt)}
    t = 0
    while True:
        pool = pool_variants(key, aligns, pool_salt(arm, retime) + ("|redraw%d" % t if t else ""))
        if not any((pre, tuple(fl)) in first for _v, pre, fl in pool):
            return pool
        t += 1


def launch_variant(rid, cell, r):
    """The pool variant launch `r` of arm cell `cell` runs: a hash of the night's run id, the cell
    and the round (no RNG state: reproducible from the record; independent across arms and rounds)."""
    return int(hashlib.sha256(("%s|%s|%d" % (rid, "/".join(cell), r)).encode()).hexdigest(), 16) % POOL_SIZE


def arm_base(arm):
    """The arm whose TEXT this arm compiles: `aa.b` (the A/A pair's second arm) -> aa."""
    return arm.split(".")[0]


def arm_head(arm):
    """The finite head an arm times (h8, h8.cf -> 8), else None."""
    b = arm_base(arm)
    return int(b[1:]) if b.startswith("h") else None


def arm_flags(arm):
    """The compile flags of an arm: I (the deny, today's text), h<N> (the lever), engine, aa; the
    A/A pair's second arm `aa.b` compiles aa's (one text, one pool)."""
    arm = arm_base(arm)
    if arm == "I":
        return HARNESS, ["--memfn=no-span-loop"]
    if arm == "engine":
        return HARNESS, ["--memfn=no-window-search"]
    if arm.startswith("h"):
        return HARNESS, ["--harness=span-head=%d" % int(arm[1:])]
    if arm == "aa":
        return HARNESS, []
    # C6's arms (R-47 U5): ONE shipped binary, V the default compile, H64 the deny; H64.b is the A/A arm (H64's text)
    if arm == "V":
        return PCREC, []
    if arm == "H64":
        return PCREC, ["--memfn=no-span-vector"]
    raise SystemExit("cards: unknown arm %r" % arm)


# ---- the card patterns: each a fixed-width window, stated per position as its byte set ------
HEX, DIG = "0123456789abcdef", "0123456789"
LIT40 = "quick brown fox jumps over the lazy dogs"    # 40 bytes: lit-l40, the run-compare control
LIT16 = "jumps over a dog"                             # 16 bytes: the A/A control lit-l16
assert len(LIT40) == 40 and len(LIT16) == 16


def rep(s, k):
    return [s] * k


PATTERNS = {
    # id: (regex, per-position byte sets)
    "hex24": (r"[0-9a-f]{24}", rep(HEX, 24)),
    "hex32": (r"[0-9a-f]{32}", rep(HEX, 32)),
    "dig24": (r"\d{24}", rep(DIG, 24)),
    "dig32": (r"\d{32}", rep(DIG, 32)),
    "uuid36": (r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
               rep(HEX, 8) + ["-"] + rep(HEX, 4) + ["-"] + rep(HEX, 4) + ["-"] + rep(HEX, 4) + ["-"]
               + rep(HEX, 12)),
    "lit40": (re.escape(LIT40), list(LIT40)),
    # the census rows' own patterns (cover_cap.md's corpus list): counterk.rxt (49), spanarms.rxt (60)
    "alt49": (r"(?:ab|ba|aa|bb){24}c", rep("ab", 48) + ["c"]),
    "abc60": (r"(?:abc){20}", list("abc" * 20)),
    "hex64": (r"[0-9a-f]{64}", rep(HEX, 64)),
    "hex500": (r"[0-9a-f]{500}", rep(HEX, 500)),
    "hex1000": (r"[0-9a-f]{1000}", rep(HEX, 1000)),
    "a500": (r"a{500}", rep("a", 500)),
    "a1000": (r"a{1000}", rep("a", 1000)),
    "hex4095": (r"[0-9a-f]{4095}", rep(HEX, 4095)),
    "a4095": (r"a{4095}", rep("a", 4095)),
    "a32": (r"a{32}", rep("a", 32)),
    "lit16": (re.escape(LIT16), list(LIT16)),
    # CARD C6's patterns (R-47 U5; block_span.md §0.1 and §8). Each states its WINDOW WIDTH (C6_WIDTH) and k, the number of
    # positions one loop tests (§3.1: `{n}` is k = n - 1). The 3 REAL bench sites at width 32 (k 31 each; the window k 31
    # cell IS the hex32 site: one text, one cell) ...
    "c6_hex32": (r"[0-9a-f]{32}", rep(HEX, 32)),                    # bounded/hex32, D-hors, window
    "c6_hexb32": (r"\b[0-9a-f]{32}\b", rep(HEX, 32)),               # loglines/hex32-id, D-hors, window
    "c6_dig32": (r"\d{32}", rep(DIG, 32)),                          # bounded/dig-exact-32, R7w, scan
    # ... and the six BOUND cells: window k 16 and 31 at width 32 (k 31 above), k 32 and 1000 at width 4095;
    # scan k 24 at width 32, k 64 at width 4095. The outside-bound cells (window k 15, 1001; scan k 23, 65) are CUT: both
    # arms render today's bytes there, so they are A/A by construction (the T-table pins check the flip in text, §10.2).
    "c6_hex17": (r"[0-9a-f]{17}", rep(HEX, 17)),                    # window k 16, w32
    "c6_hex33": (r"[0-9a-f]{33}", rep(HEX, 33)),                    # window k 32, w4095
    "c6_hex1001": (r"[0-9a-f]{1001}", rep(HEX, 1001)),              # window k 1000, w4095
    "c6_dig25": (r"\d{25}", rep(DIG, 25)),                          # scan k 24, w32
    "c6_dig65": (r"\d{65}", rep(DIG, 65)),                          # scan k 64, w4095
}
# C6's per-pattern state: the window width the cell compiles at (`--window-search-width=`), the site kind (read from the
# finder row, §0.1: window = D-hors, scan = R7w) and k. Patterns not named here take WIDTH_FLAG (the C1-C5 cards).
C6_WIDTH = {"c6_hex32": 32, "c6_hexb32": 32, "c6_dig32": 32, "c6_hex17": 32, "c6_hex33": 4095, "c6_hex1001": 4095,
            "c6_dig25": 32, "c6_dig65": 4095}
C6_SITE = {"c6_hex32": ("window", 31), "c6_hexb32": ("window", 31), "c6_dig32": ("scan", 31), "c6_hex17": ("window", 16),
           "c6_hex33": ("window", 32), "c6_hex1001": ("window", 1000), "c6_dig25": ("scan", 24), "c6_dig65": ("scan", 64)}
C6_REAL = ["c6_hex32", "c6_hexb32", "c6_dig32"]
C6_BOUND = ["c6_hex17", "c6_hex33", "c6_hex1001", "c6_dig25", "c6_dig65"]
# the F2 DIFFERS patterns (§8: "every F2 DIFFERS pattern, at width 4095"): F2 (block_span.md §6, lane bsu3's report,
# docs/dev/lanes/bsu3_report.md "F2 AND THE GUARDED BOUND") matched 82 of 82 routed cells, so the list is EMPTY; a later
# F2 that DIFFERS adds its patterns here (a pattern id, its regex, its per-position sets) and C6 times them at 4095
C6_F2_DIFFERS = []
# hit-dense's separator after a whole match, for a pattern whose regex needs one (`\b` ... `\b`: two adjacent hex runs have
# no boundary between them); every other pattern appends nothing, so C1-C5's subjects are unchanged
C6_SEP = {"c6_hexb32": b" "}
# the MISS BYTE of near-miss and near-miss-in, for a pattern whose boundary would swallow the default (review r79 F4): the
# default is the first of "zZ#@!" outside the set, `z`, a WORD byte, so at `\b...\b` the left boundary fails after every
# miss and the site never reaches the span (near-miss-in called it once per MiB); a space keeps the boundary. Every other
# pattern takes the default, so C1-C5's subjects are unchanged
C6_MISS = {"c6_hexb32": " "}
NMI = "near-miss-in"

# The regimes (r45_reply §3 C1; cover_cap.md §11.4's five plus uniform random bytes). Two take
# their METHOD from the bench (D198 (f) NOT-WARM, the bench's `short-subject-search` subject);
# until the bench names them, the script carries the kit's own approximation, and a cell in such
# a regime is VOID BY METHOD (rev 7, r35 F8): the rule never reads it as that regime. A regime
# whose bench method is ported here leaves APPROX in the same change.
REGIMES = ["hit-dense", "near-miss", "not-warm", "miss-heavy", "short-subject", "random"]
APPROX = {"not-warm": "kit approximation (each 4 KiB call after a 32 MiB eviction sweep, "
                      "untimed); the bench's D198 (f) method replaces it",
          "short-subject": "kit approximation (LF-separated 48-80 byte records, one find-all "
                           "each); the bench's short-subject-search subject replaces it"}


def method_of(regime):
    return "kit-approx" if regime in APPROX else "kit"


# ---- the cards (r45_reply rev 11 §3 "The cards"; kit-grid@7) ---------------------------------
FINITE = ["h%d" % h for h in GRID]
CARD_ROWS = {"C1": "span_cross", "C2": "span_pop", "C3": "span_long", "C4": "span_size",
             "C5": "span_engine", "C6": "span_vector", "C6c": "span_vector"}
CARDS = [
    # card, patterns, arms, regimes, layers, kind
    ("C1", ["hex24", "dig24", "hex32", "dig32"], ["I"] + FINITE, REGIMES, ["off", "on"], "time"),
    ("C2", ["uuid36", "lit40", "alt49", "abc60", "hex64"], ["I"] + FINITE, REGIMES, ["off", "on"], "time"),
    ("C3", ["hex500", "hex1000", "a500", "a1000"], ["I", "h0", "hstar"], REGIMES, ["off", "on"], "time"),
    ("C4", ["hex32", "hex500", "hex1000", "hex4095", "a32", "a500", "a1000", "a4095"],
     ["I", "h0", "hstar"], [], ["off", "on"], "size"),
    ("C5", ["hex24", "dig24", "hex32", "dig32", "uuid36", "lit40", "alt49", "abc60", "hex64",
            "hex500", "hex1000", "a500", "a1000"], ["engine"], REGIMES, ["off"], "time"),
    ("AA", ["lit16"], ["aa", "aa.b"], REGIMES, ["off", "on"], "time"),
    # C6 `span_vector` (R-47 U5, kit-grid@8; block_span.md §8): the SHIPPED trade on ONE binary at -fmemfn-simd=x86-64-v3, V
    # (the default compile) against H64@on (`--memfn=no-span-vector`); H64.b is the A/A arm (the deny exe, H64's text, timed as
    # both arms on each C6 pattern). The six regimes, plus near-miss-in at the window sites (`regimes_of`). The 3 real sites,
    # the six bound cells, the F2 DIFFERS list (empty today)
    ("C6", C6_REAL + C6_BOUND + [p[0] for p in C6_F2_DIFFERS], ["V", "H64", "H64.b"], REGIMES, ["on"], "time"),
    # C6c, C6's COMPILER-AXIS card (D201 add. 5; plan row [BSPAN-CLANG-DIFF]; block_span.md §8 "C6c"): the 3 real sites, the
    # SIMD-off layer under the two compilers the bench has SIMD-off arms for, clang -O2 (`off-clang`) and gcc -Os (`off-os`):
    # the V wrapper's text against `--memfn=no-span-vector`, the A/A arm as above. Says whether the wrapper costs anything
    # where the census said the SIMD-off machine code differs (§2.2.1 `wrap-clang`, ANSWERED by add. 5). NOT covered: clang
    # -O3 (no bench arm), the bench's -fPIC shared-object build (every cell is a non-PIC executable): named gaps
    ("C6c", C6_REAL, ["V", "H64", "H64.b"], REGIMES, ["off-clang", "off-os"], "time"),
]
CARD_PATS = {c[0]: c[1] for c in CARDS}
C6_CARDS = ("C6", "C6c")                # timed by `time` (U6), in a window main clears: no step of `run` reads it
STEP1 = ("C1", "C2", "C5", "AA")       # `run`: before h* exists
STEP2B = ("C3", "C4")                   # `c3 H`: after the rule froze h* (rev 7, F4)


def regimes_of(card, pat, regs):
    """The regimes of pattern `pat` in card `card`: `regs`, plus near-miss-in at C6's WINDOW sites where k + 1 <= 255
    (c6_rule.md N/A's named cuts: there the cards' near-miss never calls the span, the probe landing on each record's miss
    byte; at k + 1 > 255, c6_hex1001, the shift table caps at 255 and the plain near-miss already calls it at failing depths
    0..745, so no near-miss-in cell is built; every other cell is `regs`)."""
    site = C6_SITE.get(pat)
    return regs + [NMI] if card in C6_CARDS and site and site[0] == "window" and site[1] + 1 <= 255 else regs


def cells(hstar=GRID_TOP, cards=None):
    """Every cell: (card, pattern, arm, regime, layer); `hstar` resolves C3/C4's H(h*) arm.
    `cards`: only these cards (default all)."""
    out = []
    for card, pats, arms, regs, layers, kind in CARDS:
        if cards is not None and card not in cards:
            continue
        for p in pats:
            seen = []
            for a in arms:
                a = "h%d" % hstar if a == "hstar" else a
                if a in seen:          # h* = 0: H(h*) is L, one arm
                    continue
                seen.append(a)
                for ly in layers:
                    for r in (regimes_of(card, p, regs) or ["-"]):
                        out.append((card, p, a, r, ly))
    return out


# ---- subjects ---------------------------------------------------------------------------------
WORDS = ("the of and to in is it that was for on are as with his they at be this from have or "
         "by one had not but what all were when we there can an your which their said if do "
         "will each about how up out them then she many some so these would other into has "
         "more her two like him see time could no make than first been its who now people my "
         "made over did down only way find use may water long little very after words called "
         "just where most know get through back much before go good new write our used me man "
         "too any day same right look think also around another came come work three word must "
         "because does part even place well such here take why things help put years different "
         "away again off went old number great tell men say small every found still between "
         "name should home big give air line set own under read last never us left end along "
         "while might next sound below saw something thought both few those always looked show "
         "large often together asked house don't world going want school important until 1 2 3 "
         "2026 404 200 0x1f ab12 deadbeef c0ffee").split()


def subject(pat, regime, n, seed):
    """The regime's subject for pattern `pat`, n bytes (records for short-subject)."""
    rnd = random.Random("%s|%s|%d|%d" % (pat, regime, n, seed))
    pos = PATTERNS[pat][1]
    k = len(pos)
    out = bytearray()
    if regime == "hit-dense":
        while len(out) < n:
            out += bytes(ord(rnd.choice(s)) for s in pos) + C6_SEP.get(pat, b"")
    elif regime == NMI:
        # near-miss-in (710's definition): runs of members of uniform random length g in [ceil(k/2), k] (k = positions - 1, never
        # the full width: no match), each followed by ONE non-member. The window after a miss reaches the next miss at index g;
        # unless that is the window's last byte the span runs and fails there: a staircase of failing depths per run
        mem, mset = pos[0], set(pos[0])
        miss = C6_MISS.get(pat) or next((c for c in "zZ#@!" if c not in mset), None) or next(
            chr(x) for x in range(256) if chr(x) not in mset)
        while len(out) < n:
            g = rnd.randint(k // 2, k - 1)      # k positions: 710's k - 1 tested ones, g in [ceil((k-1)/2), k - 1]
            out += bytes(ord(rnd.choice(mem)) for _ in range(g)) + miss.encode("latin-1")
    elif regime == "near-miss":
        # EMITTED-2's shape: the window's first k - 1 positions, then a byte outside the last set
        last = set(pos[-1])
        miss = C6_MISS.get(pat) or next(c for c in "zZ#@!" if c not in last)
        while len(out) < n:
            out += bytes(ord(rnd.choice(s)) for s in pos[:-1]) + miss.encode()
    elif regime == "random":
        out += bytes(rnd.getrandbits(8) for _ in range(n))
    elif regime == "short-subject":
        while len(out) < n:
            ln = rnd.randint(48, 80)
            rec = bytearray()
            while len(rec) < ln:
                rec += (rnd.choice(WORDS) + " ").encode()
            if rnd.randrange(8) == 0 and k <= 4096:
                m = bytes(ord(rnd.choice(s)) for s in pos)
                at = rnd.randrange(len(rec) + 1)
                rec = rec[:at] + m + rec[at:]
            out += rec.replace(b"\n", b" ") + b"\n"
    else:   # miss-heavy and not-warm: plain text, death at depth 0-1
        while len(out) < n:
            out += (rnd.choice(WORDS) + (" " if rnd.randrange(12) else "\n")).encode()
    return bytes(out[:n])


def expect(pat, regime, buf):
    """python `re`'s find-all over the subject (each LF-free record for short-subject):
    count and the sum of the match starts."""
    rx = re.compile(PATTERNS[pat][0].encode())
    parts = []
    if regime == "short-subject":
        off = 0
        for rec in buf.split(b"\n"):
            parts.append((off, rec))
            off += len(rec) + 1
    else:
        parts = [(0, buf)]
    k = s = 0
    for off, b in parts:
        for m in rx.finditer(b):
            k += 1
            s += off + m.start()
    return k, s


# ---- the cell's C text: the artifact and one driver -----------------------------------------
DRIVER = r"""
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
/* one find-all over s[0, n) (restart at the match end, one past an empty match);
   positions reported as base + start; a give-up returns a count no gate can equal */
static uint64_t fa(const unsigned char *s, size_t n, size_t base, uint64_t *sum)
{
    ptrdiff_t caps[RXA_NCAPS][2];
    uint64_t k = 0;
    size_t from = 0;
    while (from <= n) {
        int r = rxa_search(s, n, from, caps);
        if (r == 0) break;
        if (r < 0) return (uint64_t)1 << 62;
        size_t st = (size_t)caps[0][0], en = (size_t)caps[0][1];
        k++;
        if (sum) *sum += base + st;
        from = en > st ? en : st + 1;
    }
    return k;
}
static unsigned char *evict;
enum { EVICT = 32 << 20, CHUNK = 4096 };
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec * 1e9 + t.tv_nsec; }
/* one call of the regime over the subject: whole, per record, or per 4 KiB chunk after an
   untimed eviction sweep (not-warm); *ns gets the timed nanoseconds */
static uint64_t call(int regime, const unsigned char *s, size_t n, uint64_t *sum, double *ns)
{
    uint64_t k = 0;
    if (regime == 0) {
        double t0 = now(); k = fa(s, n, 0, sum); *ns += now() - t0;
    } else if (regime == 1) {
        double t0 = now();
        for (size_t p = 0; p < n;) {
            const unsigned char *e = memchr(s + p, '\n', n - p);
            size_t q = e ? (size_t)(e - s) : n;
            k += fa(s + p, q - p, p, sum);
            p = q + 1;
        }
        *ns += now() - t0;
    } else {
        for (size_t p = 0; p < n; p += CHUNK) {
            for (size_t i = 0; i < EVICT; i += 64) evict[i]++;
            size_t m = n - p < CHUNK ? n - p : CHUNK;
            double t0 = now(); k += fa(s + p, m, p, sum); *ns += now() - t0;
        }
    }
    return k;
}
int main(int argc, char **argv)
{
    if (argc != 5) return 2;
    int regime = atoi(argv[2]);
    FILE *f = fopen(argv[1], "rb");
    if (!f) return 2;
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    fseek(f, 0, SEEK_SET);
    unsigned char *s = malloc((size_t)n + 1);
    if (!s || fread(s, 1, (size_t)n, f) != (size_t)n) return 2;
    fclose(f);
    if (regime == 2 && !(evict = calloc(EVICT, 1))) return 2;
    uint64_t sum = 0;
    double ns = 0;
    uint64_t k = call(regime, s, (size_t)n, &sum, &ns);
    if (k != strtoull(argv[3], 0, 10) || sum != strtoull(argv[4], 0, 10)) {
        printf("GATE FAIL count %llu sum %llu\n", (unsigned long long)k, (unsigned long long)sum);
        return 1;
    }
    if (!getenv("CARD_TIME")) { printf("GATE ok %llu\n", (unsigned long long)k); return 0; }
    /* calibrated: repeat whole calls until 50 ms of timed work, report ns per byte. NOT-WARM is
       calibrated on CALLS instead (r35 F11): one pass, i.e. n / CHUNK timed chunk calls, each
       after its untimed eviction sweep; a time-calibrated loop would pay ~50 untimed passes */
    unsigned long reps = 0;
    ns = 0;
    do { call(regime, s, (size_t)n, NULL, &ns); reps++; } while (regime != 2 && ns < 5e7);
    printf("TIME %.6f ns/B reps %lu\n", ns / reps / (double)n, reps);
    return 0;
}
"""
REGIME_CODE = {"short-subject": 1, "not-warm": 2}
SUBJECT_N = 1 << 20


class GateFail(RuntimeError):
    """A cell's answers differ from python `re`'s: R0's input, never a void (rev 7, F5)."""


def _h(*parts):
    h = hashlib.sha256()
    for x in parts:
        h.update(hashlib.sha256(x if isinstance(x, bytes) else x.encode("latin-1")).digest())
    return h.hexdigest()[:16]


# C4 records sizes AGAINST the size-cap ladder (250,000 / 1,000,000), so its compiles lift the cap
# past the largest form (I at 4095 is ~630 KB, R-45 FACT); no timed cell lifts it
SIZE_CAP = ["--max-emit-code-bytes=4000000"]


def artifact(rundir, pat, arm, layer, size=False):
    """The cell's artifact (pcrec-level compile on the frozen binary), cached by its inputs."""
    binp, fl = arm_flags(arm)
    wf = ["--window-search-width=%d" % C6_WIDTH[pat]] if pat in C6_WIDTH else [] if WIDTH_FLAG == "none" else [WIDTH_FLAG]
    args = [binp, "-p", PREFIX, "--features", "all"] + wf + (SIZE_CAP if size else []) + layer_flags(layer) + fl + [
        "-o", "-", "--pattern", PATTERNS[pat][0]]
    d = os.path.join(rundir, "art")
    os.makedirs(d, exist_ok=True)
    c = os.path.join(d, "a_%s.c" % _h(" ".join(args), open(binp, "rb").read()))
    if not os.path.exists(c):
        r = subprocess.run(args, capture_output=True, timeout=600)
        if r.returncode:
            raise RuntimeError("pcrec refused %s %s %s: %s" % (pat, arm, layer,
                               r.stderr.decode(errors="replace")[-400:]))
        tmp = "%s.%d.%d" % (c, os.getpid(), threading.get_ident())
        open(tmp, "wb").write(r.stdout)
        os.replace(tmp, c)
    return c


# A span loop's text (window.c wf_loop: `size_t <J> = LO; for (; <J> < END; <J>++) if (!`; G2's
# parse_loops reads the same head). Arm I (`--memfn=no-span-loop`) must carry none.
LOOP_RE = re.compile(rb"_j = [0-9]+; for \(; [A-Za-z0-9_]*_j < [0-9]+; [A-Za-z0-9_]*_j\+\+\) if \(!")


def loop_audit(texts, reach_arm=None):
    """texts: [(label, arm, bytes)]. (arm-I cells whose text holds a span loop, reach cells that do;
    the reach cells are the non-I arms, or only `reach_arm`): a deny that is ignored is invisible
    to every other check (r35 F15), and a zero over I with a zero reach is vacuous (the caller
    fails that too)."""
    leaks = [l for l, a, t in texts if a == "I" and LOOP_RE.search(t)]
    reach = [l for l, a, t in texts if a != "I" and (reach_arm is None or a == reach_arm) and LOOP_RE.search(t)]
    return leaks, reach


def check_deny(rundir, cl, reach_arm=None, vacuous_why="the loop text moved, or no arm loops at this width"):
    """Every arm-I artifact of `cl` carries no span loop, and a reach artifact does (the reach
    control; `reach_arm` names its arm, else any non-I arm). `vacuous_why`: the caller's reading of
    an empty reach (rev 10, r38 J8: c3's is a width where H(64) loops nowhere, not a moved loop
    text). Returns (failures, n_I, n_reach)."""
    keys = sorted({(c[1], arm_base(c[2]), c[4], c[0] == "C4") for c in cl})     # a layout twin is its base's text
    texts = [("%s %s %s" % (k[0], k[1], k[2]), k[1], open(artifact(rundir, k[0], k[1], k[2], size=k[3]), "rb").read())
             for k in keys]
    leaks, reach = loop_audit(texts, reach_arm)
    nI = sum(1 for _l, a, _t in texts if a == "I")
    bad = ["DENY IGNORED: arm I emits a span loop: %s" % l for l in leaks]
    if not nI:
        bad.append("DENY CHECK VACUOUS: no arm-I artifact in the cell list")
    if not reach:
        bad.append("DENY CHECK VACUOUS: no %s artifact emits a span loop (%s)" % (reach_arm or "non-I", vacuous_why))
    return bad, nI, len(reach)


V_SEL_RE = re.compile(rb"_vs[0-9]+\(")         # the selector's call (block_span.md §5)
V_BODY_RE = re.compile(rb"_vs[0-9]+__body\(")
V_W32_RE = re.compile(rb"_vs[0-9]+__w32\(")
V_SELDEF_RE = re.compile(rb"int ([A-Za-z0-9_]+_vs[0-9]+)\(const unsigned char \*")     # the selector's definition
V_LOOP_RE = re.compile(rb"for \(; i \+ ([0-9]+) < ([0-9]+); i \+= ([0-9]+)\)")            # __w32's block loop
WINDOW_SH_RE = re.compile(rb"_mf[0-9]+_sh\[")            # D-hors's shift table: a WINDOW site (a SCAN site has none)
C_COMMENT_RE = re.compile(rb"/\*.*?\*/", re.S)


def _fn_text(t, name):
    """The definition of function `name` in `t` (its head through the first `\\n}\\n`), or None."""
    m = re.search(rb"int " + re.escape(name) + rb"\(const unsigned char \*[^\n]*\n\{\n", t)
    if not m:
        return None
    e = t.find(b"\n}\n", m.end())
    return t[m.start():e + 3] if e >= 0 else None


def check_c6_texts(items, site=None):
    """C6's DENY AND REACH CHECK over [(pattern, layer, V's text, H64's text)] (the card's own: the loop check reads arm I,
    which C6 has none of; review r79 F10). Per (pattern, layer): the two arms render DIFFERENT text; the deny arm H64 carries
    no V text; V carries `__body` and ONE selector, the site CALLS the selector (a call, not its definition), and the selector
    calls `__w32` at a SIMD layer (whose definition exists, outside a comment) and `__body` elsewhere (no `__w32` at all);
    at a SIMD layer the block loop's k and width B are C6_SITE's k and the B the renderer picks (32 iff k >= 32, else 16:
    the rendering formhash's b16 / b32 instance hashes); the site kind (window: D-hors's shift table; scan: none) is C6_SITE's.
    Comments are stripped first. A defect is a text the card would time as what it is not. Returns (failures, pairs read)."""
    site = C6_SITE if site is None else site
    bad = []
    for pat, layer, v, d in items:
        tag = "C6 %s %s" % (pat, layer)
        v, d = C_COMMENT_RE.sub(b"", v), C_COMMENT_RE.sub(b"", d)
        if v == d:
            bad.append("%s: V and H64 render ONE text (an A/A cell by construction: the deny is ignored, or the stretch is "
                       "outside the table)" % tag)
        if V_SEL_RE.search(d) or V_BODY_RE.search(d) or V_W32_RE.search(d):
            bad.append("%s: DENY IGNORED: arm H64 (--memfn=no-span-vector) carries V's wrapper text" % tag)
        names = sorted({m.group(1) for m in V_SELDEF_RE.finditer(v) if b"__" not in m.group(1)})
        if not V_BODY_RE.search(v) or len(names) != 1:
            bad.append("%s: arm V carries no wrapper (`__body` and ONE selector; selectors %s)" % (tag, names))
            continue
        name = names[0]
        sel = _fn_text(v, name)
        calls = len(re.findall(rb"(?<![A-Za-z0-9_])" + re.escape(name) + rb"\(", v)) - 1
        if calls < 1:
            bad.append("%s: the site never calls the selector %s: V's text is dead code" % (tag, name.decode()))
        w32def = _fn_text(v, name + b"__w32")
        if layer_simd(layer):
            if not (sel and name + b"__w32(" in sel and w32def):
                bad.append("%s: arm V's selector does not call a defined `__w32` at the SIMD layer: the cell does not time "
                           "the vector span" % tag)
            else:
                m = V_LOOP_RE.search(w32def)
                k = site.get(pat, ("-", -1))[1]
                if not m or int(m.group(2)) != k or int(m.group(1)) != (32 if k >= 32 else 16):
                    bad.append("%s: the block loop %s is not C6_SITE's k %d at B %d" % (
                        tag, m.group(0).decode() if m else "(none)", k, 32 if k >= 32 else 16))
        else:
            if not (sel and name + b"__body(" in sel) or V_W32_RE.search(v):
                bad.append("%s: arm V's selector does not call `__body` alone at a layer that admits no level" % tag)
        kind = "window" if WINDOW_SH_RE.search(v) else "scan"
        if site.get(pat, ("-",))[0] != kind:
            bad.append("%s: the site is a %s site, C6_SITE says %s" % (tag, kind, site.get(pat, ("-",))[0]))
    return bad, len(items)


def check_c6(rundir, cl):
    """check_c6_texts over every C6 (pattern, layer) of `cl`'s artifacts. Returns (failures, pairs read)."""
    items = [(pat, layer, open(artifact(rundir, pat, "V", layer), "rb").read(),
              open(artifact(rundir, pat, "H64", layer), "rb").read())
             for pat, layer in sorted({(c[1], c[4]) for c in cl if c[0] in C6_CARDS})]
    return check_c6_texts(items)


# THE REACH BUILD (c6_rule.md N/A; review r79 F4): the span calls of ONE UNTIMED pass of a C6 cell, read from an
# INSTRUMENTED build of V's text (a counter at the top of the site's selector, printed at exit), at the layer's compiler and
# level; never a timed arm. A cell reading 0 is N/A.
def c6_reach(rundir, pat, layer, regime, n):
    """The span calls of one untimed pass of V's (pat, layer) text over the regime's subject."""
    v = open(artifact(rundir, pat, "V", layer), "rb").read().decode("latin-1")
    defs = [m for m in re.finditer(r"int ([A-Za-z0-9_]+_vs[0-9]+)\(const unsigned char \*[^\n]*\n\{\n", v)
            if "__" not in m.group(1)]
    if len(defs) != 1:
        raise RuntimeError("reach %s %s: %d selector definitions, not one" % (pat, layer, len(defs)))
    m = defs[0]
    src = v[:m.end()] + "    c6_reach_n++;\n" + v[m.end():]
    tu_src = ("#include <stddef.h>\n#include <stdint.h>\n#include <string.h>\nstatic unsigned long long c6_reach_n;\n" + src
              + "\n" + DRIVER + "\n__attribute__((destructor)) static void c6_reach_out(void) "
              "{ fprintf(stderr, \"REACH %llu\\n\", c6_reach_n); }\n")
    key = _h(tu_src, cc_ident(cc_of(layer)), opt_of(layer))
    exe = os.path.join(rundir, "reach", "r_%s" % key)
    if not os.path.exists(exe):
        os.makedirs(os.path.dirname(exe), exist_ok=True)
        tu = _tmp(exe) + ".c"
        open(tu, "w", encoding="latin-1").write(tu_src)
        r = subprocess.run([cc_of(layer), "-std=gnu11", opt_of(layer), "-w", "-o", _tmp(exe), tu], capture_output=True,
                           timeout=1800)
        if r.returncode:
            raise RuntimeError("reach build %s %s: %s" % (pat, layer, r.stderr.decode()[-400:]))
        os.replace(_tmp(exe), exe)
        os.replace(tu, exe + ".c")
    sp, k, s = subj_file(rundir, pat, regime, n)
    t = subprocess.run([exe, sp, str(REGIME_CODE.get(regime, 0)), k, s], capture_output=True, text=True, timeout=900)
    got = re.search(r"REACH ([0-9]+)", t.stderr)
    if t.returncode or not got:
        raise RuntimeError("reach %s %s %s: rc %d %s" % (pat, regime, layer, t.returncode, (t.stdout + t.stderr).strip()[-300:]))
    return int(got.group(1))


def _tmp(p):
    return "%s.%d.%d" % (p, os.getpid(), threading.get_ident())


def text_key(rundir, pat, arm, layer):
    """(the artifact path, its source, the TEXT key its pool is drawn from: the artifact + driver)."""
    a = artifact(rundir, pat, arm, layer)
    src = open(a, encoding="latin-1").read()
    return a, src, _h(src, DRIVER)


@functools.lru_cache(maxsize=None)
def cc_ident(cc):
    """The compiler's identity for the exe cache key (r44 I): `cc`, the caller's declared compiler, as named and `$cc --version`'s whole
    output (`-std=gnu11 -w` are constants of `build_cell`; the level is the layer's and rides the key's flags)."""
    r = subprocess.run([cc, "--version"], capture_output=True, text=True, timeout=60)
    return ("%s\n%s" % (cc, r.stdout)).encode("ascii", "replace").decode()


def variant_key(key, pre, fl, cc):
    """The cache name's variant part: the text key, the prelude, the flags and the compiler (r44 I)."""
    return _h(key, str(pre), " ".join(fl), cc_ident(cc))


def build_cell(rundir, pat, arm, layer, v=0, retime=0):
    """Variant `v` of the cell's POOL (rev 12, RULED r41 L9): the artifact + driver TU with its
    in-TU prelude and alignment variant, at the layer's compiler and level (LAYER), linked; cached by the
    text key AND the variant's parameters (prelude bytes, level and flags: a changed draw space is a new
    name, r41 L7) AND the compiler (its command and --version, r44 I: an exe another compiler built is
    never re-used). The pool is the arm's (pool_salt: H64.b its own) at re-time round `retime`."""
    a, src, key = text_key(rundir, pat, arm, layer)
    cc = cc_of(layer)
    _v, pre, fl = arm_pool(key, layer, arm, retime)[v]
    fl = [opt_of(layer)] + fl
    vk = variant_key(key, pre, fl, cc)
    exe = os.path.join(rundir, "bin", "x_%s_v%d_%s" % (key, v, vk))
    if os.path.exists(exe):
        return exe, a
    os.makedirs(os.path.dirname(exe), exist_ok=True)
    obj = exe + ".o"
    tu = _tmp(obj) + ".src"
    # the prelude: top-level asm, emitted ahead of every function of the TU (`dry` proves it moved)
    open(tu, "w", encoding="latin-1").write(
        "__asm__(\".text\\n\\t.skip %d\\n\");\n#include <stddef.h>\n#include <stdint.h>\n#include <string.h>\n"
        % pre + src + "\n" + DRIVER)
    # two arms can render the same text (H(h) is I where h >= k): each build its own temp names
    r = subprocess.run([cc, "-std=gnu11", "-w"] + fl + ["-x", "c", "-c", "-o", _tmp(obj), tu],
                       capture_output=True, timeout=1800)
    if r.returncode:
        raise RuntimeError("%s %s %s %s v%d: %s" % (os.path.basename(cc), pat, arm, layer, v, r.stderr.decode()[-400:]))
    os.replace(_tmp(obj), obj)
    os.replace(tu, exe + ".c")
    r = subprocess.run([cc, "-o", _tmp(exe), obj], capture_output=True, timeout=600)
    if r.returncode:
        raise RuntimeError("link %s %s %s v%d: %s" % (pat, arm, layer, v, r.stderr.decode()[-400:]))
    os.replace(_tmp(exe), exe)
    return exe, a


def search_addr(exe):
    """The address of `rxa_search` in an exe (nm), or None."""
    r = subprocess.run(["nm", exe], capture_output=True, text=True, timeout=60)
    for ln in r.stdout.splitlines():
        f = ln.split()
        if len(f) == 3 and f[2] == PREFIX + "_search":
            return int(f[0], 16)
    return None


BRANCH_RE = re.compile(r"^\s*([0-9a-f]+):\s+j[a-z]+\s+([0-9a-f]+) <")


def layout_of(exe):
    """An exe's LAYOUT as built (rev 12, r41 L9; nm + objdump, never counts): (rxa_search's address,
    its loop heads' offsets from it: the targets of its backward branches, the hot loops). Its
    64-B PHASES are the loop heads' absolute addresses mod 64 (the entry's when it has no loop); its
    RELATIVE layout is the tuple of offsets."""
    at = search_addr(exe)
    if at is None:
        return None
    r = subprocess.run(["objdump", "-d", "--no-show-raw-insn", "--disassemble=%s_search" % PREFIX, exe],
                       capture_output=True, text=True, timeout=120)
    heads = set()
    for ln in r.stdout.splitlines():
        m = BRANCH_RE.match(ln)
        if m and int(m.group(2), 16) < int(m.group(1), 16) and int(m.group(2), 16) >= at:
            heads.add(int(m.group(2), 16) - at)
    return at, tuple(sorted(heads))


def pool_proof(rundir, pat, arm, layer, retime=0):
    """The pool's proof (rev 12, RULED r41 L9): every variant built; {v: (64-B phase of each hot
    loop in offset order, the 32-B phases, relative layout)}; and the refusal text when the variants share ONE 64-B
    phase set or ONE relative layout (the pool would not move what a head's body moves), else None. `retime`: the
    re-time round's pool (C6's `time` proves its fresh pools too)."""
    lay = {}
    for v in range(POOL_SIZE):
        exe, _a = build_cell(rundir, pat, arm, layer, v, retime)
        lo = layout_of(exe)
        if lo is None:
            return lay, "%s %s %s v%d: no %s_search symbol" % (pat, arm, layer, v, PREFIX)
        at, rel = lo
        pts = [at + o for o in rel] or [at]
        # per hot loop, IN ITS ORDER (never a set: two loops 32 B apart moving by 32 swap phases and keep the set)
        lay[v] = (tuple(x % 64 for x in pts), tuple(x % 32 for x in pts), rel)
    why = pool_refusal(lay)
    return lay, ("POOL REFUSED %s %s %s: %s" % (pat, arm, layer, why) if why else None)


def pool_refusal(lay):
    """THE POOL REFUSAL (rev 12, RULED r41 L9; r44 C), one clause a half (r41 L4's lesson: one control a
    half): `lay` {v: (64-B phase of each hot loop in order, 32-B phases, relative layout)}. Refused
    when every variant puts every hot loop at ONE 64-B phase; or shares ONE relative layout; or (r44 C)
    two variants of ONE relative layout share their per-loop 32-B phase vector (the alignment pair's
    16 B mod 32 did not reach the loops: PHASE_ORDER's half); or the pool holds fewer than POOL_SIZE
    distinct built layouts (64-B, 32-B, relative), since `text_var` charges the pool-mean term as
    sL2 / POOL_SIZE, i.e. POOL_SIZE independent layouts. The text, or None."""
    why = []
    if len({p64 for p64, _p, _r in lay.values()}) < 2:
        why.append("every variant puts its hot loops at one 64-B phase each %s" % (next(iter(lay.values()))[0],))
    if len({r for _a, _b, r in lay.values()}) < 2:
        why.append("every variant shares one relative layout")
    by_rel = {}
    for v, (_a, p32, rel) in sorted(lay.items()):
        by_rel.setdefault(rel, []).append((v, p32))
    for rel, vs in sorted(by_rel.items()):
        seen = {}
        for v, p32 in vs:
            if p32 in seen:
                why.append("variants %d and %d of one relative layout share the 32-B phases %s" % (seen[p32], v, p32))
                break
            seen[p32] = v
    # (a duplicated layout shares its relative layout AND its 32-B phases, so the clause above fires with
    # this one: its plant shows both, never this one alone)
    k = len(set(lay.values()))
    if k < POOL_SIZE:
        why.append("%d distinct built layouts of %d variants (text_var charges sL2 / %d)" % (k, POOL_SIZE, POOL_SIZE))
    return "; ".join(why) or None


def subj_file(rundir, pat, regime, n):
    p = os.path.join(rundir, "subj", "%s.%s.%d" % (pat, regime, n))
    if not os.path.exists(p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        b = subject(pat, regime, n, 1)
        k, s = expect(pat, regime, b)
        tmp = "%s.%d.%d" % (p, os.getpid(), threading.get_ident())
        open(tmp + ".e", "w").write("%d %d\n" % (k, s))
        os.replace(tmp + ".e", p + ".expect")
        open(tmp, "wb").write(b)
        os.replace(tmp, p)
    k, s = open(p + ".expect").read().split()
    return p, k, s


def size_record(rundir, pat, arm, layer):
    """C4: emitted C bytes, gcc -O2 -c time and max RSS, .text bytes (no timing of the matcher)."""
    a = artifact(rundir, pat, arm, layer, size=True)
    obj = os.path.join(rundir, "obj", os.path.basename(a) + ".o")
    os.makedirs(os.path.dirname(obj), exist_ok=True)
    tu = obj + ".c"
    open(tu, "w", encoding="latin-1").write("#include <stddef.h>\n#include <stdint.h>\n#include <string.h>\n"
                                             + open(a, encoding="latin-1").read())
    r = subprocess.run(["/usr/bin/time", "-f", "%e %M", cc_of(layer), "-std=gnu11", opt_of(layer), "-w", "-c", "-o", obj, tu],
                       capture_output=True, text=True, timeout=1800)
    if r.returncode:
        raise RuntimeError("gcc -c %s %s: %s" % (pat, arm, r.stderr[-300:]))
    secs, rss = r.stderr.strip().splitlines()[-1].split()
    sz = subprocess.run(["size", "-A", obj], capture_output=True, text=True).stdout
    text = next((int(l.split()[1]) for l in sz.splitlines() if l.startswith(".text ")), 0)
    return os.path.getsize(a), float(secs), int(rss), text


def _exec(argv, cell, env=None):
    t = subprocess.run(argv, capture_output=True, text=True, timeout=900, env=env)
    if t.returncode == 1 and t.stdout.startswith("GATE FAIL"):
        raise GateFail("cell %s: %s" % ("|".join(cell), t.stdout.strip()))
    if t.returncode:
        raise RuntimeError("cell %s: rc %d %s" % ("|".join(cell), t.returncode, t.stdout.strip()))
    return t.stdout


def run_cell(rundir, cell, n):
    """The gate's line on EVERY pool variant (no clock; rev 12, r41 L9), or C4's size record. Timing
    is `time_cells`' (rev 10: the rounds)."""
    card, pat, arm, regime, layer = cell
    if card == "C4":
        cb, secs, rss, text = size_record(rundir, pat, arm, layer)
        return "size c_bytes=%d gcc_s=%.2f rss_kb=%d text=%d" % (cb, secs, rss, text)
    sp, k, s = subj_file(rundir, pat, regime, n)
    outs = []
    for v in range(POOL_SIZE):
        exe, _a = build_cell(rundir, pat, arm, layer, v)
        outs.append(_exec([exe, sp, str(REGIME_CODE.get(regime, 0)), k, s], cell).strip())
    return "%s (all %d variants)" % (outs[0], POOL_SIZE) if len(set(outs)) == 1 else " | ".join(outs)


# ---- results files: one row per arm cell ------------------------------------------------------
# card pattern arm regime layer status median spread launches method; status ok | void |
# gatefail | method (void by method, not timed). The launches are kept so the rule can test
# bimodality (rev 7, F3); `spread` (max - min) is a record only. `variants` (rev 12, r41 L9): the
# pool variant each launch ran, in launch order (the draw, recorded per launch).
HEADER = "#card\tpattern\tarm\tregime\tlayer\tstatus\tmedian_ns_per_B\tspread\tlaunches\tmethod\tvariants\n"


def row_line(cell, status, launches=None, note="", variants=None):
    if launches:
        med, spr = statistics.median(launches), max(launches) - min(launches)
        return "\t".join(cell) + "\t%s\t%.6f\t%.6f\t%s\t%s\t%s\n" % (
            status, med, spr, ",".join("%.6f" % v for v in launches), method_of(cell[3]),
            ",".join(map(str, variants)) if variants else "-")
    return "\t".join(cell) + "\t%s\t-\t-\t%s\t%s\n" % (status, note.replace("\t", " ").replace("\n", " ")[:300] or "-",
                                                       method_of(cell[3]))


def read_rows(path):
    """{(card, pat, arm, regime, layer): row dict} from a results file (absent file: {})."""
    out = {}
    if not os.path.exists(path):
        return out
    for ln in open(path):
        if ln.startswith("#") or not ln.strip():
            continue
        key, row = row_of(ln.rstrip("\n").split("\t"))
        out[key] = row
    return out


def row_of(f):
    """One results row's fields `f` (row_line's columns) -> (cell key, row dict)."""
    st = f[5]
    launches = [float(x) for x in f[8].split(",")] if st == "ok" else []
    return tuple(f[:5]), {"status": st, "med": float(f[6]) if st == "ok" else None, "launches": launches,
                          "method": f[9], "note": f[8] if st != "ok" else "",
                          "variants": [int(x) for x in f[10].split(",")] if len(f) > 10 and f[10] != "-" else []}


# ---- THE LAUNCH ORDER (rev 10, RULED r38 J2): interleaved within a cell --------------------
# Rev 9 timed a card's arm cells ARM-MAJOR (all 5 launches of one arm, then the next arm), so a
# step in box speed between I and its twins (h24, h32, h64 at k 24: last in the block) read as a
# head win no estimator could see (r38 J2). Rev 10 times each CELL (card, pattern, regime,
# layer) as ROUNDS: one launch of every arm per round, LAUNCHES rounds, so every arm of the
# cell samples the same stretch of time and a step or a drift moves every arm alike. Within a
# round the arms run in a fixed pseudo-random order per (cell, round), derived from the cell's
# key (no RNG state; `cards.py` and the drills read the same order): a step INSIDE the middle
# round splits the cell's arms into "before" and "after" at random, never twins against heads
# by construction. The cells' own order (the ruled night order inside a card) is unchanged.
def cell_groups(cl):
    """The cell list `cl` grouped by cell (card, pattern, regime, layer), in first-appearance order:
    [(cellkey, [arm cells])]."""
    groups = {}
    for c in cl:
        groups.setdefault((c[0], c[1], c[3], c[4]), []).append(c)
    return list(groups.items())


def round_arms(cs, r):
    """Round r's launch order over a cell's arm cells `cs`: a fixed permutation from the cell key."""
    return sorted(cs, key=lambda c: hashlib.sha256(("%s/%d" % ("/".join(c), r)).encode()).hexdigest())


def launch_order(cl, interleave=True):
    """[(arm cell, launch index)] in the order the night times them; interleave=False is rev 9's
    arm-major order (the drills' control)."""
    out = []
    if not interleave:
        for c in cl:
            out += [(c, i) for i in range(LAUNCHES)]
        return out
    for _k, cs in cell_groups(cl):
        for r in range(LAUNCHES):
            out += [(c, r) for c in round_arms(cs, r)]
    return out


def prepare_cell(rundir, cell, n, retime=0):
    """The gate run (untimed) of one arm cell on EVERY variant of its pool (rev 12, r41 L9); returns
    the timed argv of each variant [v]. Raises GateFail on a wrong answer, anything else on a void.
    `retime`: the pool of that re-time round (pool_salt; C6's fresh re-time pool), 0 the first pass's."""
    _card, pat, _arm, regime, _layer = cell
    sp, k, s = subj_file(rundir, pat, regime, n)
    code = str(REGIME_CODE.get(regime, 0))
    out = []
    for v in range(POOL_SIZE):
        exe, _a = build_cell(rundir, pat, cell[2], cell[4], v, retime)
        _exec([exe, sp, code, k, s], cell)
        out.append(["taskset", "-c", CPU, exe, sp, code, k, s])
    return out


def timed_launch(argv, cell, env):
    """ONE timed launch (THE CLOCK CALL): the exe under CARD_TIME, its `TIME <ns/B>` reading."""
    return float(_exec(argv, cell, env).split()[1])


def time_cells(rundir, cl, path, with_approx=True, retime=0, launch=None, stop=None, prefix="", salt=None):
    """Times the arm cells `cl` into `path` (appended), cell by cell in ROUNDS (rev 10, J2), each launch on a variant drawn
    from its arm's pool (rev 12, r41 L9). C1-C5 call it with the defaults. C6's timer (`time`, U6) passes: `retime` (the
    re-time round's FRESH pool, pool_salt), `launch(argv, cell, env)` -> ns/B, or None when the launch stayed VOID under
    the CPU-quiet control after its re-times (the arm falls short; default `timed_launch`), `stop()` -> True once no new
    cell may start (the WINDOW: the cell's rows read `notrun`), `prefix` (a leading field on every row: C6's pass) and
    `salt` (the launch draws' salt; default the results file's name, so a re-run draws afresh)."""
    launch = launch or timed_launch
    env = dict(os.environ, CARD_TIME="1")
    with open(path, "a") as f:
        if os.path.getsize(path) == 0:
            f.write(HEADER)
        rid = run_id(rundir, create=True)
        for _key, cs in cell_groups(cl):
            if stop is not None and stop():
                for c in cs:        # the window closed: no new cell starts (c6_rule.md WINDOW; 710's)
                    f.write(prefix + row_line(c, "notrun", note="not started: the window's deadline passed"))
                f.flush()
                continue
            argv, launches, out, drawn = {}, {}, {}, {}
            for c in cs:
                if c[3] in APPROX and not with_approx:
                    out[c] = row_line(c, "method", note="void by method: " + APPROX[c[3]])
                    continue
                try:
                    argv[c] = prepare_cell(rundir, c, SUBJECT_N, retime)
                    launches[c], drawn[c] = [], []
                except GateFail as e:
                    out[c] = row_line(c, "gatefail", note=str(e))
                except Exception as e:      # noqa: BLE001 -- a void, re-run once (F7)
                    out[c] = row_line(c, "void", note=str(e))
            for r in range(LAUNCHES):       # the rounds (rev 10, J2): one launch of every arm per round
                for c in round_arms(list(argv), r):
                    if c in out:
                        continue
                    # the layout draw (rev 12, r41 L9), salted by the results file: a re-run or the
                    # confirm draws afresh, never step 1's sequence again
                    v = launch_variant("%s|%s" % (rid, os.path.basename(path) if salt is None else salt), c, r)
                    try:
                        x = launch(argv[c][v], c, env)
                        if x is not None:
                            launches[c].append(x)
                            drawn[c].append(v)
                    except Exception as e:      # noqa: BLE001 -- the arm is void, re-run once (F7)
                        out[c] = row_line(c, "void", note=str(e))
            for c in cs:
                if c not in out and not launches[c]:
                    out[c] = row_line(c, "void", note="no valid launch (every launch VOID under the CPU-quiet control)")
                f.write(prefix + (out[c] if c in out else row_line(c, "ok", launches[c], variants=drawn[c])))
            f.flush()


# ---- C6's RULE (R-47 U5; review r79 F2, F5-F8; block_span.md §8) ---------------------------------------------------
# THE RULE is the COMMITTED file c6_rule.md beside this script (its fenced block, written before any C6 timing); job 710's,
# which it adapts clause by clause, is the committed rule_710.md. Both shas are COMPUTED from the files (the fenced block's
# lines, each followed by a newline; the bytes 710's recorded sha covers), never typed; the rule's CONSTANTS are parsed
# from its CONSTANTS clause, so the code and the text cannot hold two values. `c6_decide` is the rule's VERDICT on a
# cell set (U6's timer feeds it; `c6selftest` drills it on constructed outcomes); `c6_header` / `c6_header_check` the
# RECORD clause's header line.
C6_RULE_FILE = os.path.join(HERE, "c6_rule.md")
C6_RULE_710_FILE = os.path.join(HERE, "rule_710.md")
C6_RULE_710_RECORDED = "6351bff3901e3955"     # the sha job 710's record and every citation of it state (checked)


def rule_block(path):
    """The fenced block of a rule file: its lines between the first two ``` lines, each followed by a newline."""
    ln = open(path, encoding="utf-8").read().split("\n")
    f = [i for i, x in enumerate(ln) if x == "```"]
    if len(f) < 2:
        raise SystemExit("cards: %s holds no fenced rule block" % path)
    return "".join(x + "\n" for x in ln[f[0] + 1:f[1]])


def rule_sha(path):
    return hashlib.sha256(rule_block(path).encode("utf-8")).hexdigest()[:16]


def rule_constants(path):
    """{name: value} from the rule's CONSTANTS clause (its line and the indented lines after it)."""
    ln = rule_block(path).split("\n")
    i = next(k for k, x in enumerate(ln) if x.startswith("CONSTANTS:"))
    j = next((k for k in range(i + 1, len(ln)) if ln[k] and not ln[k].startswith(" ")), len(ln))
    txt = " ".join(ln[i:j])
    got = {m.group(1): float(m.group(2)) for m in re.finditer(r"\b([A-Z][A-Z_]+) ([0-9]+(?:\.[0-9]+)?)\b", txt)}
    want = ("FLOOR_MIN", "SPREAD_MAX", "AA_VOID_MAX", "READABLE_MIN")
    if any(w not in got for w in want):
        raise SystemExit("cards: %s's CONSTANTS clause lacks %s" % (path, [w for w in want if w not in got]))
    return {w: got[w] for w in want}


C6_RULE_SHA = rule_sha(C6_RULE_FILE)
C6_CONST = rule_constants(C6_RULE_FILE)


def c6_arm(launches):
    """An arm's reading (UNIT): (median, spread over the middle launches), or None (short of LAUNCHES valid launches)."""
    if not launches or len(launches) < LAUNCHES:
        return None
    x = sorted(launches)
    med = statistics.median(x)
    return med, (x[-2] - x[1]) / med


def c6_cmp(a, b):
    """The cell rule on two arm readings: WIN / LOSS / TIE of A against B, or NOISE (an arm unread, or FLOOR > SPREAD_MAX)."""
    if a is None or b is None:
        return "NOISE"
    floor = max(C6_CONST["FLOOR_MIN"], a[1], b[1])
    if floor > C6_CONST["SPREAD_MAX"]:
        return "NOISE"
    return "WIN" if a[0] < b[0] / (1 + floor) else "LOSS" if a[0] > b[0] * (1 + floor) else "TIE"


def _standing(first, again):
    """RE-TIME: a first-pass verdict and its re-time's (None: not run) -> (standing verdict, note)."""
    if first in ("TIE", "NOISE"):
        return first, ""
    if again == first:
        return first, "repeated"
    if again in (None, "NOISE"):
        return ("LOSS", "re-time %s" % ("NOT-RUN" if again is None else "noisy")) if first == "LOSS" else (
            "TIE", "%s not repeated (re-time %s)" % (first, "NOT-RUN" if again is None else "noisy"))
    return "TIE", "%s not repeated" % first


def c6_cell(cell):
    """One cell's readings: cell = {key: (card, pat, regime, layer), calls, run, arms: {V, H64, H64.b: launches|None},
    retime: the same arms dict or None (not run)}. -> (reading, A/A, notes)."""
    if not cell.get("calls"):
        return "N/A", "N/A", []
    if not cell.get("run", True):
        return "NOT-RUN", "NOT-RUN", []
    arm = {a: c6_arm(cell["arms"].get(a)) for a in ("V", "H64", "H64.b")}
    rt = cell.get("retime")
    rarm = {a: c6_arm(rt.get(a)) for a in ("V", "H64", "H64.b")} if rt else None
    rd, rn = _standing(c6_cmp(arm["V"], arm["H64"]), rarm and c6_cmp(rarm["V"], rarm["H64"]))
    aa1 = c6_cmp(arm["H64.b"], arm["H64"])
    aa, an = _standing(aa1, rarm and c6_cmp(rarm["H64.b"], rarm["H64"]))
    notes = [x for x in (rn and "reading " + rn, an and "A/A " + an) if x]
    if aa in ("WIN", "LOSS"):
        rd = "HARNESS"
    return rd, ("AA-NOISE" if aa == "NOISE" else aa), notes + (["A/A single-pass non-TIE"] if aa1 in ("WIN", "LOSS") else [])


def c6_decide(cells):
    """THE VERDICT (c6_rule.md VERDICT, first match) per (card, layer) over a cell set (VOID BY METHOD regimes are not
    in the population). -> {(card, layer): {verdict, rate, lists}}."""
    out = {}
    groups = {}
    for c in cells:
        if c["key"][2] in APPROX:
            continue
        groups.setdefault((c["key"][0], c["key"][3]), []).append(c)
    for g, cs in sorted(groups.items()):
        rows = [(c["key"],) + c6_cell(c) for c in cs]
        pop = [r for r in rows if r[1] != "N/A"]
        aar = [r for r in pop if r[2] not in ("NOT-RUN", "AA-NOISE")]
        aas = [r for r in aar if r[2] in ("WIN", "LOSS")]
        single = sum(1 for r in aar if "A/A single-pass non-TIE" in r[3])
        rate = len(aas) / len(aar) if aar else None
        readable = [r for r in pop if r[1] in ("WIN", "LOSS", "TIE")]
        loss = [r for r in readable if r[1] == "LOSS"]
        cause = {w: sum(1 for r in pop if r[1] == w) for w in ("HARNESS", "NOISE", "NOT-RUN")}
        if not pop:
            v = "INCONCLUSIVE-N/A"
        elif not aar:
            v = "VOID (A/A UNREAD)"
        elif rate > C6_CONST["AA_VOID_MAX"]:
            v = "VOID (A/A FAILED: rate %.3f > %.3f)" % (rate, C6_CONST["AA_VOID_MAX"])
        elif loss:
            v = "LOSS"
        elif len(readable) < C6_CONST["READABLE_MIN"] * len(pop):
            v = "INCONCLUSIVE-%s" % max(("HARNESS", "NOISE", "NOT-RUN"), key=lambda w: (cause[w], -("HARNESS", "NOISE", "NOT-RUN").index(w)))
        else:
            v = "NO LOSS"
        if cause["NOT-RUN"]:
            v = "TRUNCATED: " + v
        wtl = {w: sum(1 for r in readable if r[1] == w) for w in ("WIN", "TIE", "LOSS")}
        out[g] = {"verdict": v, "rate": rate, "aa_readable": len(aar), "aa_standing": len(aas), "aa_single": single,
                  "population": len(pop), "readable": len(readable), "wtl": wtl, "loss": [r[0] for r in loss],
                  "na": [r[0] for r in rows if r[1] == "N/A"], "harness": [r[0] for r in pop if r[1] == "HARNESS"],
                  "noise": [r[0] for r in pop if r[1] == "NOISE"], "notrun": [r[0] for r in pop if r[1] == "NOT-RUN"],
                  "notes": [(r[0], n) for r in rows for n in r[3]], "rows": rows}
    return out


def c6_verdict_lines(dec):
    """The REPORTED lines of a c6_decide result."""
    out = []
    for (card, layer), d in sorted(dec.items()):
        out.append("%s %s: %s; readable %d of %d; W/T/L %d/%d/%d; A/A: %d standing non-TIE of %d readable (rate %s, "
                   "AA_VOID_MAX %.3f), %d single-pass; N/A %d, HARNESS %d, NOISE %d, NOT-RUN %d" % (
                       card, layer, d["verdict"], d["readable"], d["population"], d["wtl"]["WIN"], d["wtl"]["TIE"],
                       d["wtl"]["LOSS"], d["aa_standing"], d["aa_readable"],
                       "-" if d["rate"] is None else "%.3f" % d["rate"], C6_CONST["AA_VOID_MAX"], d["aa_single"],
                       len(d["na"]), len(d["harness"]), len(d["noise"]), len(d["notrun"])))
    return out


# THE RECORD's header (c6_rule.md RECORD): the first line of every C6/C6c results file. The format is fixed here; the
# writer that fills it (the form hash, the binary, the run id) is U6's timer, `time` (cmd_time).
C6_HEADER_KEYS = ("rule", "rule710", "form", "binary", "widths", "run")


def c6_header(form_hash, binary_sha, layers, run):
    return "#c6\t" + "\t".join(["rule=%s" % C6_RULE_SHA, "rule710=%s" % rule_sha(C6_RULE_710_FILE), "form=%s" % form_hash,
                                "binary=%s" % binary_sha]
                               + ["cc.%s=%s" % (ly, hashlib.sha256(cc_ident(cc_of(ly)).encode()).hexdigest()[:16])
                                  for ly in layers]
                               + ["widths=%s" % ",".join("%s:%d:%s:%d" % (p, C6_WIDTH[p], C6_SITE[p][0], C6_SITE[p][1])
                                                         for p in sorted(C6_WIDTH)), "run=%s" % run])


def c6_header_check(line):
    """None, or why the decider refuses a results file whose first line is `line`."""
    if not line or not line.startswith("#c6\t"):
        return "no #c6 RECORD header"
    f = dict(x.split("=", 1) for x in line.rstrip("\n").split("\t")[1:] if "=" in x)
    miss = [k for k in C6_HEADER_KEYS if k not in f]
    if miss:
        return "the header lacks %s" % ",".join(miss)
    if f["rule"] != C6_RULE_SHA or f["rule710"] != rule_sha(C6_RULE_710_FILE):
        return "recorded under rule %s / %s, the live files are %s / %s" % (
            f["rule"], f["rule710"], C6_RULE_SHA, rule_sha(C6_RULE_710_FILE))
    return None
# ---- THE CPU-QUIET CONTROL (rule_710.md "CPU-QUIET CONTROL", which c6_rule.md applies UNCHANGED) ---------------------
# The in-tree copy of job 710's control (ported from 710's harness, scratch/memfn/blockconfirm/confirm.py `quiet_sample` /
# `timed_pass_a` / `void_reason`, which is untracked; lane bsu6t, R-47 U6). The timed process is pinned (taskset, CPU) and
# nothing isolates the pin or its SMT sibling; so: a QUIET SAMPLE before the first timed cell (QC_SECS 1-s /proc/stat
# samples of the sibling and the pin, nothing of ours running, then QC_CAL_REPS launches of ONE calibration exe), the
# thresholds from that sample only, and per timed launch the sibling's busy fraction (observed over >= OBS_MIN s) and the
# involuntary context switches of the timed child (getrusage RUSAGE_CHILDREN delta: launches are serial). A VOID launch is
# re-timed up to QC_RETIMES more times on the same variant; an arm still short of LAUNCHES valid launches reads None
# (c6_arm), so both of its cell's comparisons are INCONCLUSIVE-NOISE (c6_rule.md CPU-QUIET CONTROL).
QC_SECS = 60           # the quiet sample's 1-s samples (rule_710.md: "60 s")
QC_CAL_REPS = 10       # the calibration exe's launches ("10 repeats")
QC_RETIMES = 2         # a void launch is re-timed up to this many more times ("up to 2 more times")
CPU7_CAP = 0.20        # CPU7_MAX = min(20 %, max(5 %, 2 x the sample's max 1-s busy fraction of the sibling))
CPU7_LOW = 0.05
OBS_MIN = 0.1          # the sibling's busy fraction is read over at least 100 ms (/proc/stat moves in 10 ms ticks)


def smt_sibling(cpu):
    """The pin's SMT sibling from sysfs (thread_siblings_list), as a string; None when the pin has none (or several)."""
    try:
        txt = open("/sys/devices/system/cpu/cpu%s/topology/thread_siblings_list" % cpu).read().strip()
    except OSError:
        return None
    ids = []
    for part in txt.split(","):
        lo, _, hi = part.partition("-")
        ids += [str(x) for x in range(int(lo), int(hi or lo) + 1)]
    ids = [x for x in ids if x != str(cpu)]
    return ids[0] if len(ids) == 1 else None


def read_stat(cpu):
    """(total jiffies, idle + iowait jiffies) of CPU `cpu` from /proc/stat."""
    for ln in open("/proc/stat"):
        f = ln.split()
        if f[0] == "cpu" + str(cpu):
            v = [int(x) for x in f[1:9]]
            return sum(v), v[3] + v[4]
    raise RuntimeError("no cpu%s line in /proc/stat" % cpu)


def busy_between(s0, s1):
    dt = s1[0] - s0[0]
    return (1.0 - (s1[1] - s0[1]) / dt) if dt > 0 else 0.0


class RealProbe:
    """The box: the clock (`timed_launch`, pinned by prepare_cell's taskset argv), /proc/stat and getrusage."""

    def __init__(self, cpu):
        self.cpu, self.sib = str(cpu), smt_sibling(cpu)
        if self.sib is None:
            raise SystemExit2("cards: time: CPU %s has no single SMT sibling in sysfs: the CPU-quiet control cannot run "
                              "(set CPU= to a core with one sibling)" % cpu)
        self._prev = None

    def wall(self):
        return time.time()

    def second(self):
        """One 1-s quiet sample: (sibling busy, pin busy) over the second."""
        if self._prev is None:
            self._prev = (read_stat(self.sib), read_stat(self.cpu))
        time.sleep(1)
        now = (read_stat(self.sib), read_stat(self.cpu))
        b = (busy_between(self._prev[0], now[0]), busy_between(self._prev[1], now[1]))
        self._prev = now
        return b

    def measure(self, argv, cell, env):
        """One timed launch with the control's two readings: (ns/B, sibling busy, nivcsw, seconds)."""
        s0, n0, t0 = read_stat(self.sib), resource.getrusage(resource.RUSAGE_CHILDREN).ru_nivcsw, time.monotonic()
        ns = timed_launch(argv, cell, env)          # THE CLOCK CALL (a module-level lookup: DRY's guard replaces it)
        t1, n1 = time.monotonic(), resource.getrusage(resource.RUSAGE_CHILDREN).ru_nivcsw
        if t1 - t0 < OBS_MIN:
            time.sleep(OBS_MIN - (t1 - t0))
        return ns, busy_between(s0, read_stat(self.sib)), n1 - n0, t1 - t0


class QuietControl:
    """The control's logic over a probe (RealProbe, or DRY's DryProbe: the same code either way)."""

    def __init__(self, probe, sample_path, voids_path):
        self.probe, self.sample_path, self.voids_path = probe, sample_path, voids_path
        self.qc, self.voids = None, 0
        open(voids_path, "w").write("pass\tcard\tpattern\tarm\tregime\tlayer\tattempt\tcpu7_busy\tnivcsw\tsecs\treason\tns_b\n")
        self.pass_ = "-"

    def sample(self, cal_argv, cal_cell, env):
        """The QUIET SAMPLE and its thresholds (rule_710.md); written to sample_path. Returns the threshold dict."""
        rows = ["kind\tidx\tcpu7_busy\tpin_busy\tnivcsw\tsecs"]
        b7 = []
        for i in range(QC_SECS):
            a, b = self.probe.second()
            b7.append(a)
            rows.append("sample\t%d\t%.4f\t%.4f\t\t1" % (i, a, b))
        cal = []
        for i in range(QC_CAL_REPS):
            _ns, busy, niv, secs = self.probe.measure(cal_argv, cal_cell, env)
            cal.append((busy, niv, secs))
            rows.append("calib\t%d\t%.4f\t\t%d\t%.3f" % (i, busy, niv, secs))
        raw = max(CPU7_LOW, 2 * max(b7))
        self.qc = {"cpu7_max": min(CPU7_CAP, raw), "cpu7_capped": raw > CPU7_CAP, "sample_cpu7_max_busy": max(b7),
                   "nivcsw_max": max(2, 2 * max(c[1] for c in cal)), "t_cal": statistics.mean(c[2] for c in cal),
                   "cal_cell": "/".join(cal_cell), "cpu": getattr(self.probe, "cpu", "-"), "sibling": getattr(self.probe, "sib", "-")}
        rows.append("threshold\tCPU7_MAX\t%.4f\t\t\t" % self.qc["cpu7_max"])
        rows.append("threshold\tNIVCSW_MAX\t\t\t%d\t%.3f" % (self.qc["nivcsw_max"], self.qc["t_cal"]))
        open(self.sample_path, "w").write("\n".join(rows) + "\n")
        return self.qc

    def void_reason(self, busy7, nivcsw, secs):
        why = []
        if busy7 > self.qc["cpu7_max"]:
            why.append("cpu7 busy %.3f > %.3f" % (busy7, self.qc["cpu7_max"]))
        lim = self.qc["nivcsw_max"] * max(1.0, secs / self.qc["t_cal"])
        if nivcsw > lim:
            why.append("nivcsw %d > %.1f" % (nivcsw, lim))
        return "; ".join(why) or None

    def launch(self, argv, cell, env):
        """time_cells' `launch`: ns/B of the first valid of 1 + QC_RETIMES attempts (same variant), else None."""
        for attempt in range(1 + QC_RETIMES):
            ns, busy7, niv, secs = self.probe.measure(argv, cell, env)
            why = self.void_reason(busy7, niv, secs)
            if why is None:
                return ns
            self.voids += 1
            open(self.voids_path, "a").write("%s\t%s\t%d\t%.4f\t%d\t%.3f\t%s\t%.6f\n" % (
                self.pass_, "\t".join(cell), attempt, busy7, niv, secs, why, ns))
        return None


# ---- DRY (no clock): the timer end to end with every launch SYNTHETIC ----------------------------------------------
class ClockCalled(BaseException):
    """DRY's loud failure: a timed launch was attempted. A BaseException, so no `except Exception` (time_cells' void
    path) can swallow it."""


DRY_LAUNCH_S = 0.06    # DRY's simulated wall per launch (UNMEASURED; the deadline drill reads it, no rule does)
# DRY's models: {regime: {(pass, arm): factor}} over a 1.0 base with +-1 % jitter, plus the void plants. `exercise` drives
# every path of the timer: a repeated WIN (hit-dense), a LOSS the re-time does not repeat (miss-heavy), an A/A non-TIE the
# re-time does not repeat (random), voided launches the control re-times (near-miss: the first launch of each exe in a pass), and an
# arm whose every attempt is void (near-miss-in, V: short, NOISE). `tie` is all 1.0.
DRY_MODELS = {
    "tie": {},
    "exercise": {"hit-dense": {("first", "V"): 0.5, ("retime", "V"): 0.5},
                 "miss-heavy": {("first", "V"): 1.3},
                 "random": {("first", "H64.b"): 1.3}},
}
DRY_VOID = {"exercise": {"near-miss": ("first-launch-per-exe", None), NMI: ("every-attempt", "V")}}


class DryProbe:
    """A synthetic probe: the clock never runs (each launch's value is the model's), the quiet sample reads a quiet box, and
    the wall is SIMULATED (QC sample 1 s a sample, DRY_LAUNCH_S a launch) so a deadline truncates deterministically."""

    def __init__(self, model, t0, qc_ref):
        self.model, self.voidm, self.t, self.qcr = DRY_MODELS[model], DRY_VOID.get(model, {}), float(t0), qc_ref
        self.cpu, self.sib = "dry", "dry"
        self.n, self.att = 0, {}

    def wall(self):
        return self.t

    def second(self):
        self.t += 1.0
        return 0.01, 0.0

    def measure(self, argv, cell, env):
        exe = argv[3] if argv[:1] == ["taskset"] else argv[0]
        if not os.path.exists(exe):
            raise RuntimeError("DRY: the cell's exe %s was never built" % exe)
        self.n += 1
        self.t += DRY_LAUNCH_S
        q = self.qcr()
        pass_ = q.pass_ if q else "cal"
        k = (pass_, cell, exe)
        a = self.att[k] = self.att.get(k, -1) + 1      # this exe's attempt counter in this pass
        f = self.model.get(cell[3], {}).get((pass_, cell[2]), 1.0)
        j = 1 + (int(hashlib.sha256(("%s|%s|%d" % (pass_, "/".join(cell), self.n)).encode()).hexdigest(), 16) % 201 - 100) / 1e4
        busy = 0.01
        vk = self.voidm.get(cell[3])
        if vk and pass_ != "cal" and (vk[1] is None or vk[1] == cell[2]):
            if vk[0] == "every-attempt" or (vk[0] == "first-launch-per-exe" and a == 0):
                busy = 0.9
        return f * j, busy, 0, DRY_LAUNCH_S


def dry_guard():
    """DRY's proof that no launch runs: `timed_launch` (the clock call) and any subprocess run under `taskset` or with
    CARD_TIME set raise ClockCalled. Returns (uninstall, counter)."""
    seen = {"clock": 0, "subprocess": 0}
    real_run, real_launch = subprocess.run, globals()["timed_launch"]

    def no_clock(argv, cell, env):
        seen["clock"] += 1
        raise ClockCalled("DRY: the clock was called (timed_launch %s, cell %s)" % (argv, "/".join(cell)))

    def guarded(argv, *a, **kw):
        env = kw.get("env")
        if (isinstance(argv, (list, tuple)) and argv[:1] == ["taskset"]) or (env and "CARD_TIME" in env):
            seen["subprocess"] += 1
            raise ClockCalled("DRY: a timed exec was attempted: %s" % (argv,))
        return real_run(argv, *a, **kw)
    globals()["timed_launch"], subprocess.run = no_clock, guarded

    def uninstall():
        globals()["timed_launch"], subprocess.run = real_launch, real_run
    return uninstall, seen


# ---- THE RECORD (c6_rule.md RECORD) and its reader ---------------------------------------------------------------
# results_c6_<run>.tsv: line 1 the `#c6` header (c6_header); `#run` (launches, deadline, dry); `#qc` (the thresholds);
# `#pass` + HEADER's columns; `cell` lines (card pattern regime layer calls: the WHOLE population with its reach count,
# written before any timing); `first` / `retime` rows (row_line's columns behind the pass); `#end` last (a file without
# it is a run that died: refused). A re-time row set exists exactly for the cells the first pass owes one (its rows
# `notrun` when the window closed first); the reader refuses a record where that does not hold.
C6_END = "#end"


def c6_record_head(path, header, run, keys_calls):
    """The record's head (written before any timing): the `#c6` header, the `#run` fields, the column line, and a `cell`
    line per population cell with its span calls. `run`: [(key, value)]."""
    with open(path, "w") as f:
        f.write(header + "\n")
        f.write("#run\t%s\n" % "\t".join("%s=%s" % kv for kv in run))
        f.write("#pass\t" + HEADER[1:])
        for k, n in keys_calls:
            f.write("cell\t%s\t%d\n" % ("\t".join(k), n))


def c6_record_end(path, fields):
    """The record's last line, `#end` (a record without it is refused: the run died)."""
    with open(path, "a") as f:
        f.write("%s\t%s\n" % (C6_END, "\t".join("%s=%s" % kv for kv in fields)))


def c6_owes(arms):
    """Whether a first pass's arm readings {V, H64, H64.b: launches|None} owe a re-time (c6_rule.md RE-TIME): a reading
    WIN or LOSS, or an A/A non-TIE."""
    a = {k: c6_arm(arms.get(k)) for k in ("V", "H64", "H64.b")}
    return c6_cmp(a["V"], a["H64"]) in ("WIN", "LOSS") or c6_cmp(a["H64.b"], a["H64"]) in ("WIN", "LOSS")


def c6_read(path):
    """A C6 record -> (cells for c6_decide, info) or raises SystemExit2 with the refusal. info: header fields, run fields,
    gate failures, re-time NOT-RUN cells, the DRY flag, the approx (void by method) rows."""
    ln = open(path).read().split("\n")
    why = c6_header_check(ln[0] if ln else "")
    if why:
        raise SystemExit2("cards: c6decide: %s: REFUSED: %s" % (path, why))
    if C6_END not in [x.split("\t")[0] for x in ln if x]:
        raise SystemExit2("cards: c6decide: %s: REFUSED: no %s line (the run died before it finished)" % (path, C6_END))
    head = dict(x.split("=", 1) for x in ln[0].split("\t")[1:] if "=" in x)
    info = {"header": head, "run": {}, "gatefail": [], "retime_notrun": [], "dry": False, "approx": 0, "qc": {}}
    cells, rows = {}, {"first": {}, "retime": {}}
    for x in ln[1:]:
        if not x:
            continue
        f = x.split("\t")
        if f[0] in ("#run", "#qc", C6_END):
            info[{"#run": "run", "#qc": "qc", C6_END: "end"}[f[0]]] = dict(y.split("=", 1) for y in f[1:] if "=" in y)
        elif f[0] == "cell":
            cells[tuple(f[1:5])] = int(f[5])
        elif f[0] in rows:
            key, r = row_of(f[1:])
            rows[f[0]][key] = r
        elif not f[0].startswith("#"):
            raise SystemExit2("cards: c6decide: %s: REFUSED: an unknown line %r" % (path, x[:80]))
    info["dry"] = info["run"].get("dry") == "1"
    if int(info["run"].get("launches", -1)) != LAUNCHES:
        raise SystemExit2("cards: c6decide: %s: REFUSED: recorded at LAUNCHES=%s, read at %d" % (
            path, info["run"].get("launches"), LAUNCHES))
    out = []
    for ck, calls in cells.items():
        card, pat, regime, layer = ck
        if regime in APPROX:
            info["approx"] += 1
            continue
        c = {"key": ck, "calls": calls}
        if calls:
            first = {a: rows["first"].get((card, pat, a, regime, layer)) for a in ("V", "H64", "H64.b")}
            if any(r is None for r in first.values()):
                raise SystemExit2("cards: c6decide: %s: REFUSED: cell %s calls the span and has no first-pass row for %s" % (
                    path, "/".join(ck), [a for a, r in first.items() if r is None]))
            info["gatefail"] += ["%s %s: %s" % ("/".join(ck), a, r["note"]) for a, r in first.items() if r["status"] == "gatefail"]
            c["run"] = not any(r["status"] == "notrun" for r in first.values())
            c["arms"] = {a: (r["launches"] or None) if r["status"] == "ok" else None for a, r in first.items()}
            again = {a: rows["retime"].get((card, pat, a, regime, layer)) for a in ("V", "H64", "H64.b")}
            have = [r for r in again.values() if r is not None]
            owed = c["run"] and c6_owes(c["arms"])
            if bool(have) != owed or (have and len(have) != 3):
                raise SystemExit2("cards: c6decide: %s: REFUSED: cell %s %s a re-time and the record holds %d re-time rows" % (
                    path, "/".join(ck), "owes" if owed else "owes no", len(have)))
            if have:
                info["gatefail"] += ["%s %s (re-time): %s" % ("/".join(ck), a, r["note"])
                                     for a, r in again.items() if r["status"] == "gatefail"]
                if any(r["status"] == "notrun" for r in have):
                    info["retime_notrun"].append(ck)
                else:
                    c["retime"] = {a: (r["launches"] or None) if r["status"] == "ok" else None for a, r in again.items()}
        out.append(c)
    stray = [k for p in rows for k in rows[p] if (k[0], k[1], k[3], k[4]) not in cells]
    if stray:
        raise SystemExit2("cards: c6decide: %s: REFUSED: %d rows of cells outside the record's population (%s)" % (
            path, len(stray), "/".join(stray[0])))
    return out, info


def c6_report(dec, info):
    """THE REPORTED lines (c6_rule.md REPORTED) of a decided record."""
    out = []
    if info["dry"]:
        out.append("DRY RECORD: every reading is SYNTHETIC (no clock ran): NOT A TIMING, NOT A VERDICT")
    out += c6_verdict_lines(dec)
    for (card, layer), d in sorted(dec.items()):
        tag = "%s %s" % (card, layer)
        out.append("%s: A/A single-pass rate %s (%d of %d)" % (tag, "%.3f" % (d["aa_single"] / d["aa_readable"])
                                                              if d["aa_readable"] else "-", d["aa_single"], d["aa_readable"]))
        for i, name in ((1, "pattern"), (2, "regime")):
            by = {}
            for key, rd, _aa, _n in d["rows"]:
                if rd in ("WIN", "TIE", "LOSS"):
                    by.setdefault(key[i], {"WIN": 0, "TIE": 0, "LOSS": 0})[rd] += 1
            out.append("%s: W/T/L per %s: %s" % (tag, name, ", ".join("%s %d/%d/%d" % (k, v["WIN"], v["TIE"], v["LOSS"])
                                                                         for k, v in sorted(by.items())) or "none"))
        fmt = lambda ks: " ".join("/".join(k[1:3]) for k in ks) or "none"
        out.append("%s: N/A (0 span calls): %s" % (tag, fmt(d["na"])))
        for name, k in (("LOSS (standing)", "loss"), ("INCONCLUSIVE-NOISE", "noise"), ("INCONCLUSIVE-HARNESS", "harness"),
                        ("NOT-RUN", "notrun")):
            out.append("%s: %s: %s" % (tag, name, fmt(d[k])))
        out.append("%s: standing WINs (information; a WIN gates nothing): %s" % (
            tag, fmt([key for key, rd, _a, _n in d["rows"] if rd == "WIN"])))
        out.append("%s: not repeated: %s" % (tag, "; ".join("%s %s" % ("/".join(key[1:3]), n) for key, n in d["notes"]
                                                             if "not repeated" in n) or "none"))
        rtn = [k for k in info["retime_notrun"] if (k[0], k[3]) == (card, layer)]
        out.append("%s: re-time NOT-RUN (the window closed; RE-TIME: a reading LOSS stands, a WIN counts as a TIE, an A/A "
                   "non-TIE stands): %s" % (tag, fmt(rtn)))
    out.append("approx (VOID BY METHOD, never timed): %d cells" % info["approx"])
    for g in info["gatefail"]:
        out.append("GATE FAIL %s" % g)
    return out


def cmd_c6decide(args):
    """c6decide RESULTS: THE VERDICT from a C6/C6c record alone. Exit 0 read; 1 a gate failed (a wrong answer: the run is
    red whatever it reads); 2 refused; 4 TRUNCATED (a cell of either pass not started)."""
    (path,), _opt = parse_args("c6decide", args)
    cells_, info = c6_read(path)
    dec = c6_decide(cells_)
    for x in c6_report(dec, info):
        print(x)
    if info["gatefail"]:
        return 1
    return 4 if any(d["notrun"] for d in dec.values()) or info["retime_notrun"] else 0


def c6_form_hash(rundir):
    """mf_form_hash("span-vector") of the FROZEN build's kit: tests/memfn/arm_fixtures.c linked against BUILD's
    libpcrec.a (its `--hash` FORM line)."""
    fx = os.path.join(rundir, "fx", "arm_fixtures")
    os.makedirs(os.path.dirname(fx), exist_ok=True)
    r = subprocess.run([CC, "-std=gnu11", "-O1", "-I" + os.path.join(TREE, "memfn", "include"),
                        os.path.join(TREE, "tests", "memfn", "arm_fixtures.c"), os.path.join(BUILD, "libpcrec.a"),
                        "-o", _tmp(fx)], capture_output=True, text=True, timeout=600)
    if r.returncode:
        raise SystemExit2("cards: time: the form-hash driver does not build: %s" % r.stderr[-300:])
    os.replace(_tmp(fx), fx)
    for x in subprocess.run([fx, "--hash"], capture_output=True, text=True, timeout=120).stdout.splitlines():
        f = x.split("\t")
        if f[:2] == ["FORM", "span-vector"] and f[2] == "0":
            return f[3]
    raise SystemExit2("cards: time: arm_fixtures --hash printed no FORM line for span-vector")


def cmd_time(args):
    """time RUNDIR [--cards C6,C6c] [--deadline EPOCH|+SECONDS] [--dry [--dry-model tie|exercise] [--patterns P,..]]:
    C6/C6c's TIMER (c6_rule.md; R-47 U6). See the module docstring's `time`."""
    (rundir,), opt = parse_args("time", args, nflags=("--dry",), vflags=("--cards", "--deadline", "--dry-model", "--patterns"))
    dry = "--dry" in opt
    if not dry and ("--dry-model" in opt or "--patterns" in opt):
        raise SystemExit2("cards: time: --dry-model and --patterns are DRY's (a timing times the whole population)")
    sel = opt.get("--cards", ",".join(C6_CARDS)).split(",")
    if not sel or any(c not in C6_CARDS for c in sel):
        raise SystemExit2("cards: time: --cards takes C6 and/or C6c (got %s)" % opt.get("--cards"))
    model = opt.get("--dry-model", "exercise")
    if model not in DRY_MODELS:
        raise SystemExit2("cards: time: --dry-model is one of %s" % ",".join(sorted(DRY_MODELS)))
    if rule_sha(C6_RULE_710_FILE) != C6_RULE_710_RECORDED:
        raise SystemExit2("cards: time: rule_710.md's sha %s is not job 710's %s" % (rule_sha(C6_RULE_710_FILE), C6_RULE_710_RECORDED))
    uninstall, seen = dry_guard() if dry else (lambda: None, None)
    try:
        return _time(rundir, sel, opt, dry, model, seen)
    finally:
        uninstall()


def _time(rundir, sel, opt, dry, model, seen):
    t_start = time.time()
    os.makedirs(rundir, exist_ok=True)
    pop = cells(cards=sel)
    if "--patterns" in opt:
        pats = opt["--patterns"].split(",")
        pop = [c for c in pop if c[1] in pats]
        if not pop:
            raise SystemExit2("cards: time: --patterns %s selects no cell" % opt["--patterns"])
    jobs = int(os.environ.get("JOBS", "4"))
    # 1. the texts: C6's deny and reach check (as `dry`), refused on any failure
    cbad, cn = check_c6(rundir, pop)
    print("cards: time: C6 deny and reach check: %d (pattern, layer) pairs, failures %d" % (cn, len(cbad)))
    if cbad:
        for b in cbad:
            print("FAIL", b)
        raise SystemExit2("cards: time: the C6 text check failed; no timing")
    # 2. N/A (c6_rule.md): the reach build's span calls, one UNTIMED instrumented pass per cell over the timed subject
    keys = list(dict.fromkeys((c[0], c[1], c[3], c[4]) for c in pop))
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        calls = dict(zip(keys, ex.map(lambda k: c6_reach(rundir, k[1], k[3], k[2], SUBJECT_N), keys)))
    dead = sorted({(k[1], k[3]) for k in keys if k[2] == "hit-dense" and calls[k] == 0})
    if dead:
        raise SystemExit2("cards: time: REACH CONTROL: hit-dense calls the span 0 times at %s" % dead)
    timed = [c for c in pop if calls[(c[0], c[1], c[3], c[4])] and c[3] not in APPROX]
    approx = [c for c in pop if c[3] in APPROX]
    # 3. every pool the run can time, BUILT and PROVED before the clock (no compile inside the timing): the first pass's
    # and the re-time's FRESH pool (arm_pool) of every timed arm cell, each pool's layouts refused as `dry` refuses
    texts = sorted({(c[1], c[2], c[4], rt) for c in timed for rt in (0, 1)})
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        proofs = list(ex.map(lambda t: pool_proof(rundir, t[0], t[1], t[2], t[3])[1], texts))
    refused = [w for w in proofs if w]
    print("cards: time: %d pools built and proved (first pass and re-time, %d exes), refused %d" % (
        len(texts), len(texts) * POOL_SIZE, len(refused)))
    if refused:
        for w in refused:
            print("FAIL", w)
        raise SystemExit2("cards: time: a pool was refused; no timing")
    # 4. the record's head, before any timing: the header, the run, the population with its reach counts
    rid = start_timing(rundir)
    path = os.path.join(rundir, "results_c6_%s.tsv" % rid)
    if os.path.exists(path):
        raise SystemExit2("cards: time: %s exists" % path)
    probe_t0 = time.time()
    dl = opt.get("--deadline")
    deadline = None if dl is None else (probe_t0 + float(dl[1:])) if dl.startswith("+") else float(dl)
    binary = hashlib.sha256(open(PCREC, "rb").read()).hexdigest()[:16]
    layers = sorted({c[4] for c in pop})
    c6_record_head(path, c6_header(c6_form_hash(rundir), binary, layers, rid),
                   [("launches", LAUNCHES), ("pool", POOL_SIZE), ("cpu", CPU),
                    ("deadline", "-" if deadline is None else "%d" % deadline), ("dry", int(dry))]
                   + ([("model", model)] if dry else []) + [("cards", ",".join(sel)), ("subject", SUBJECT_N)],
                   [(k, calls[k]) for k in keys])
    print("cards: time: run %s -> %s; population %d cells (%d N/A, %d void by method), %d timed arm cells, %d first-pass "
          "launches%s" % (rid, path, len(keys), sum(1 for k in keys if not calls[k] and k[2] not in APPROX),
                          len({(c[0], c[1], c[3], c[4]) for c in approx}), len(timed), len(timed) * LAUNCHES,
                          "; DRY (model %s): no clock" % model if dry else ""))
    # 5. the quiet sample (calibration: H64 of the first timed cell, variant 0 of its first-pass pool), then the passes
    qref = {}
    probe = DryProbe(model, probe_t0, lambda: qref.get("q")) if dry else RealProbe(CPU)
    q = QuietControl(probe, os.path.join(rundir, "quiet_sample_c6_%s.tsv" % rid), os.path.join(rundir, "voids_c6_%s.tsv" % rid))
    qref["q"] = None
    if not timed:
        raise SystemExit2("cards: time: no cell calls the span: nothing to time")
    cal = next(c for c in timed if c[2] == "H64")
    qc = q.sample(prepare_cell(rundir, cal, SUBJECT_N)[0], cal, dict(os.environ, CARD_TIME="1"))
    qref["q"] = q
    with open(path, "a") as f:
        f.write("#qc\tcpu7_max=%.4f\tcapped=%d\tsample_max=%.4f\tnivcsw_max=%d\tt_cal=%.4f\tcal=%s\tsibling=%s\n" % (
            qc["cpu7_max"], qc["cpu7_capped"], qc["sample_cpu7_max_busy"], qc["nivcsw_max"], qc["t_cal"], qc["cal_cell"],
            qc["sibling"]))
    if qc["cpu7_capped"]:
        print("cards: time: QUIET SAMPLE BUSY: CPU7_MAX capped at 20 %% (sample max %.1f %%)" % (100 * qc["sample_cpu7_max_busy"]))
    print("cards: time: quiet sample: CPU7_MAX %.3f, NIVCSW_MAX %d per %.3f s launch (calibration %s)" % (
        qc["cpu7_max"], qc["nivcsw_max"], qc["t_cal"], qc["cal_cell"]))
    stop = (lambda: probe.wall() >= deadline) if deadline is not None else None
    q.pass_ = "first"
    time_cells(rundir, timed + approx, path, with_approx=False, launch=q.launch, stop=stop, prefix="first\t", salt="first")
    first = {}
    for x in open(path):
        if x.startswith("first\t"):
            key, r = row_of(x.rstrip("\n").split("\t")[1:])
            first[key] = r
    owed = []
    for k in keys:
        if not calls[k] or k[2] in APPROX:
            continue
        rs = {a: first.get((k[0], k[1], a, k[2], k[3])) for a in ("V", "H64", "H64.b")}
        if all(r and r["status"] != "notrun" for r in rs.values()) and c6_owes(
                {a: (r["launches"] or None) if r["status"] == "ok" else None for a, r in rs.items()}):
            owed.append(k)
    q.pass_ = "retime"
    time_cells(rundir, [c for c in timed if (c[0], c[1], c[3], c[4]) in owed], path, with_approx=False, retime=1,
               launch=q.launch, stop=stop, prefix="retime\t", salt="retime")
    nr = {p: sum(1 for x in open(path) if x.startswith(p + "\t") and x.split("\t")[6] == "notrun") for p in ("first", "retime")}
    c6_record_end(path, [("status", "truncated" if nr["first"] or nr["retime"] else "complete"),
                         ("notrun_first", nr["first"]), ("notrun_retime", nr["retime"]), ("owed", len(owed)),
                         ("void_launches", q.voids), ("wall", round((probe.wall() if dry else time.time()) - t_start))])
    print("cards: time: first pass done, %d cells owe a re-time (fresh pools), %d void launches; arm rows NOT-RUN: first %d, "
          "re-time %d" % (len(owed), q.voids, nr["first"], nr["retime"]))
    if dry:
        print("cards: time: DRY: %d synthetic launches, clock calls %d, timed execs refused %d" % (
            probe.n, seen["clock"], seen["subprocess"]))
    # 6. the verdict, read back from the record alone
    print("cards: time: the record read back (c6decide %s):" % path)
    rc = cmd_c6decide([path])
    if nr["first"] or nr["retime"]:
        print("cards: time: TRUNCATED")
    print("cards: time: DONE rc=%d" % rc)
    return rc


# What C6 settles (block_span.md §8): c6_rule.md CLAIM. The SIMD-off layer's wrapper under gcc -O2 is not timed (r68 F-14:
# U2b's census is its record); C6c times it under clang -O2 and gcc -Os, where the census said the machine code differs.


# ---- plan (with the expected wall time, r35 F11) ---------------------------------------------
# UNMEASURED: the per-launch costs below are assumptions for the window request, never inputs to
# the rule; F11 asks for one launch's wall time in the cards' own window to replace them.
EST_LAUNCH_S = float(os.environ.get("EST_LAUNCH_S", "0.08"))   # 50 ms timed + exec + one gate call
EST_SWEEP_S = float(os.environ.get("EST_SWEEP_S", "0.004"))    # one 32 MiB eviction sweep (~8 GB/s)
# one extra pool variant's untimed gate call (rev 12, r41 L9): MEASURED 0.0008-0.0033 s (median 0.0015) over 30
# calls on 1 MiB subjects, 5 cells, lane formsfixk 2026-11-17 on a NON-quiet box (not a timing); 0.01 s = 3 x the max
EST_GATE_S = float(os.environ.get("EST_GATE_S", "0.01"))


def est_cell_s(cell):
    """One arm cell's wall: its gate run on EVERY pool variant (rev 12, r41 L9) plus LAUNCHES launches."""
    if cell[3] == "not-warm":   # every call sweeps once per 4 KiB chunk: the gate calls + one timed pass
        per = 2 * (SUBJECT_N // 4096) * EST_SWEEP_S
        return (POOL_SIZE + LAUNCHES) * per
    return EST_LAUNCH_S * (1 + LAUNCHES) + EST_GATE_S * (POOL_SIZE - 1)


def cmd_plan(args):
    parse_args("plan", args, npos=0)
    cl = cells()
    by = {}
    for c in cl:
        by[c[0]] = by.get(c[0], 0) + 1
    for c in cl:
        print("\t".join(c))
    # the pools' line counts C1-C5's population, whose alignment variants are gcc's (review r79 F9); C6/C6c have their block
    builds = {(c[1], arm_base(c[2]), c[4], c[0] == "C4") for c in cl if c[0] not in C6_CARDS}
    timed = {b for b in builds if not b[3]}
    print("# cells %d (%s); C1-C5: distinct pcrec compiles %d; LAYOUT POOLS (rev 12, r41 L9): %d timed texts at most "
          "(hash-equal arms share I's pool; `dry` counts the real number) x POOL_SIZE %d variants = %d gcc compiles + "
          "links at most (rev 11: one compile a text, %d, plus its twins' links); UNMEASURED DEFAULT: POOL_SIZE, the prelude draw space "
          "(%d 16-B steps mod %d B), the alignment variants %s" % (
              len(cl), ", ".join("%s %d" % kv for kv in sorted(by.items())), len(builds), len(timed), POOL_SIZE,
              POOL_SIZE * len(timed), len(timed), PRELUDE_STEPS, 16 * PRELUDE_STEPS,
              " / ".join(" ".join(a) or "(gcc default)" for a in ALIGN_VARIANTS)))
    for r, why in APPROX.items():
        print("# regime %s: %s; VOID BY METHOD (rev 7, F8)" % (r, why))
    s1 = [c for c in cells(cards=STEP1)]
    s1_read = [c for c in s1 if c[3] not in APPROX]
    s2 = [c for c in cells(cards=("C3",))]
    s2_read = [c for c in s2 if c[3] not in APPROX]
    w = lambda cs: sum(est_cell_s(c) for c in cs) / 3600.0      # noqa: E731
    print("# expected wall (UNMEASURED: EST_LAUNCH_S %.3f s per launch, EST_SWEEP_S %.4f s per eviction "
          "sweep, LAUNCHES %d, the cells already built by `dry`):" % (EST_LAUNCH_S, EST_SWEEP_S, LAUNCHES))
    print("#   run:  %d cells timed, %.2f h (with --with-approx: %d cells, %.2f h)" % (
        len(s1_read), w(s1_read), len(s1), w(s1)))
    print("#   run's gates (rev 12, r41 L9): every arm cell gates EVERY pool variant before timing (in the hours above): "
          "+%d untimed gate calls over rev 11's one a cell, +%.4f h (EST_GATE_S %.3f s each)"
          % ((POOL_SIZE - 1) * len(s1_read), (POOL_SIZE - 1) * len(s1_read) * EST_GATE_S / 3600.0, EST_GATE_S))
    print("#   c3:   %d cells timed, %.2f h (C4's sizes: compile-only, not in the window)" % (len(s2_read), w(s2_read)))
    na = len(GRID) + 1
    print("#   rerun: one cell per void, ~%.0f s per C1-C2 cell (%d arms)" % (na * est_cell_s(("C1", "-", "I", "random", "off")), na))
    # THE CONFIRM'S COST (rev 11, r39 K5; rev 12, r41 L9): one re-run per winning (cell, head) of I and the head, each
    # launch a fresh draw of its pool; its BOUND is every mover cell read with every moving head winning; the one-win
    # case is one head in one regime (its moving patterns x 2 layers)
    lp = est_cell_s(("C1", "-", "I", "random", "off"))
    movers = [(card, p, rg) for card in ("C1", "C2") for p in CARD_PATS[card] for rg in REGIMES if rg not in APPROX
              if p not in ("lit40", "abc60") and any(h < len(PATTERNS[p][1]) for h in GRID)]
    bound_arms = sum(2 * (1 + sum(1 for h in GRID if h < len(PATTERNS[p][1]))) for _c, p, _r in movers)
    one = sum(2 for card in ("C1", "C2") for p in CARD_PATS[card] if p not in ("lit40", "abc60") and 8 < len(PATTERNS[p][1]))
    print("#   confirm (rev 10, r38 R2; rev 12, r41 L9): one re-run per winning (cell, head), I and the head on fresh "
          "pool draws, ~%.0f s per cell and winning head; BOUND (every mover cell read, every moving head winning): %d "
          "cells, %d arm cells, %.3f h; one real win of one head in one regime (H(8): %d cells) %.3f h (the confirm "
          "cells a no-win night costs: the selftest's RECORD)" % (2 * lp, 2 * len(movers), bound_arms,
                                                               bound_arms * lp / 3600.0, one, one * 2 * lp / 3600.0))
    print("# timing order (rev 10, r38 J2): the cells above grouped by (card, pattern, regime, layer), each timed in "
          "%d ROUNDS of one launch per arm (`launch_order`): run %d cells, %d timed launches" % (
              LAUNCHES, len(cell_groups(s1_read)), len(launch_order(s1_read))))
    # C6 (R-47 U5): its own block; no step of `run` reads it (`time` times it, U6)
    for card in C6_CARDS:
        cc = cells(cards=(card,))
        rd = [c for c in cc if c[3] not in APPROX]
        lys = sorted({c[4] for c in cc})
        print("# %s (kit-grid@8 %s; CANDIDATE, UNMEASURED): %d cells, %d timed (no approx regime), %.2f h expected (UNMEASURED constants); "
              "layers %s; patterns %s" % (
                  card, CARD_ROWS[card], len(cc), len(rd), sum(est_cell_s(c) for c in rd) / 3600.0,
                  " ".join("%s(%s %s %s; pool alignment variants %s)" % (
                      ly, os.path.basename(cc_of(ly)), opt_of(ly), " ".join(layer_flags(ly)) or "SIMD-off",
                      " / ".join(" ".join(a) or "(default)" for a in align_variants_of(ly))) for ly in lys),
                  " ".join("%s(w%d,%s k%d)" % (p, C6_WIDTH[p], C6_SITE[p][0], C6_SITE[p][1]) for p in CARD_PATS[card])))
    print("# C6 pools: H64.b draws its OWN pool (POOL_SALT, review r79 F2); a re-time builds a FRESH pool (salt %s<n>)" % RETIME_SALT)
    print("# C6 cut cells (c6_rule.md N/A's named cuts; A/A by construction: both arms render today's bytes outside the bounds, "
          "block_span.md §8): window k 15, 1001; scan k 23, 65 (the T-table pins check the flip in text, §10.2); near-miss-in at the "
          "window sites with k + 1 <= 255 only (c6_hex1001: the shift cap 255): %s; near-miss at the window sites k <= 32 is N/A by "
          "construction (`dry`'s reach build counts it); F2 DIFFERS patterns timed at width 4095: %s (bsu3 report: 82 of 82 routed cells MATCH)" % (
              ",".join(sorted(p for p, (st, k) in C6_SITE.items() if st == "window" and k + 1 <= 255)),
              ",".join(p[0] for p in C6_F2_DIFFERS) or "none"))
    print("# C6 rule: %s, sha %s (job 710's: %s, sha %s); constants %s; the RECORD header keys %s:" % (
        os.path.relpath(C6_RULE_FILE, TREE), C6_RULE_SHA, os.path.relpath(C6_RULE_710_FILE, TREE), rule_sha(C6_RULE_710_FILE),
        " ".join("%s=%g" % kv for kv in C6_CONST.items()), ",".join(C6_HEADER_KEYS + ("cc.<layer>",))))
    for ln in rule_block(C6_RULE_FILE).rstrip("\n").split("\n"):
        print("#   " + ln)


def cmd_dry(args):
    """Builds every cell and runs its gate once (no clock): the cell list, the count, the
    distinct compiles, and every failure (a failure is the run's red)."""
    (rundir,), opt = parse_args("dry", args, nflags=("--quick",), vflags=("--cards",))
    quick = "--quick" in opt
    n = 1 << 16 if quick else SUBJECT_N
    os.makedirs(rundir, exist_ok=True)
    # --cards C6,C6c: a PARTIAL dry over the named cards (a new card need not rebuild the night's 241 texts); the C1-C5 checks
    # (the deny check on arm I, step 2b's, the identical-to-I record) are the full dry's and are named as skipped
    sel = opt["--cards"].split(",") if "--cards" in opt else None
    bad_sel = [c for c in sel or [] if c not in {x[0] for x in CARDS}]
    if bad_sel:
        raise SystemExit2("cards: dry: unknown card(s) %s (known: %s)" % (",".join(bad_sel), ",".join(x[0] for x in CARDS)))
    cl = cells(cards=sel)
    jobs = int(os.environ.get("JOBS", "4"))
    bad, done = [], {}
    # the compiles first, one per (pattern, arm, layer), in parallel; the gates then reuse them
    builds = sorted({(c[1], c[2], c[4], c[0] == "C4") for c in cl})

    def one_build(b):
        pat, arm, layer, size = b
        try:
            if size:
                artifact(rundir, pat, arm, layer, size=True)
            else:
                for v in range(POOL_SIZE):          # every variant of the arm's pool (rev 12, r41 L9)
                    build_cell(rundir, pat, arm, layer, v)
            return None
        except Exception as e:
            return "BUILD %s %s %s: %s" % (pat, arm, layer, e)
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        for e in ex.map(one_build, builds):
            if e:
                bad.append(e)

    def one(c):
        try:
            return c, run_cell(rundir, c, n), None
        except Exception as e:
            return c, None, str(e)
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        for c, out, err in ex.map(one, cl):
            print("%s\t%s" % ("\t".join(c), out if out else "FAIL " + err))
            if err:
                bad.append(err)
            done[c] = out
    if sel is None:
        # C1-C5's population only (review r79 F9): C6's texts have their own check (check_c6), and two of them carry a span
        # loop, which would keep this check's REACH control from going vacuous on C1-C5's own texts
        dbad, nI, nreach = check_deny(rundir, [c for c in cl if c[0] not in C6_CARDS])
        bad += dbad
        print("# dry: deny check: %d arm-I artifacts with no span loop, %d non-I artifacts with one (reach), "
              "failures %d" % (nI, nreach, len(dbad)))
        cbad, cI, creach = c3_deny_check(rundir)
        print("# dry: step 2b's deny check (`c3` refuses on it; r37 H4): %d arm-I C3/C4 artifacts loop-free, reach "
              "(h%d) %d%s" % (cI, GRID_TOP, creach, "; WOULD REFUSE: " + "; ".join(cbad) if cbad else ""))
    else:
        print("# dry: PARTIAL (--cards %s): the C1-C5 deny checks and the identical-to-I record are the full dry's, not run" % opt["--cards"])
    c6bad, c6n = check_c6(rundir, cl)
    bad += c6bad
    if any(c[0] in C6_CARDS for c in cl):
        print("# dry: C6 deny and reach check: %d (pattern, layer) pairs: V and H64 render different text, the deny arm carries no V "
              "text, the site calls V's ONE selector, which calls `w32` at a SIMD layer (its loop C6_SITE's k at B 16/32) and "
              "`__body` elsewhere, the site kind C6_SITE's; failures %d" % (c6n, len(c6bad)))
        # THE REACH BUILD (c6_rule.md N/A): span calls of one untimed pass per C6 (pattern, regime, layer)
        rcells = sorted({(c[0], c[1], c[3], c[4]) for c in cl if c[0] in C6_CARDS})

        def one_reach(k):
            try:
                return k, c6_reach(rundir, k[1], k[3], k[2], n), None
            except Exception as e:      # noqa: BLE001
                return k, None, str(e)
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            reach = list(ex.map(one_reach, rcells))
        for k, calls, err in reach:
            print("# reach\t%s\t%s" % ("\t".join(k), calls if err is None else "FAIL " + err))
            if err:
                bad.append(err)
        # the build's own control: every (pattern, layer)'s hit-dense pass calls the span
        dead = sorted({(k[1], k[3]) for k, calls, _e in reach if k[2] == "hit-dense" and calls == 0})
        bad += ["REACH CONTROL: %s %s: hit-dense calls the span 0 times (the counter or the selector moved)" % d for d in dead]
        na = [k for k, calls, _e in reach if calls == 0]
        print("# dry: C6 reach build (untimed, instrumented V; the N/A rule's input): %d cells, N/A (0 calls) %d: %s" % (
            len(reach), len(na), " ".join("%s/%s/%s/%s" % k for k in na) or "none"))
    # THE POOLS' PROOF (rev 12, RULED r41 L9): every timed text's pool, each variant built and answer-gated
    # above (run_cell gates every variant in every regime); here each pool's hot-loop PHASES mod 32 / 64 and
    # its RELATIVE layouts, read from the built exes (nm, objdump: the backward-branch targets inside
    # rxa_search); a pool whose variants share ONE 64-B phase set or ONE relative layout is REFUSED
    texts = {}
    for c in cl:
        if c[0] != "C4":
            # one pool per text, arm salt, compiler and level: off-clang and off-os share a text, never a pool's exes
            texts.setdefault((text_key(rundir, c[1], c[2], c[4])[2], pool_salt(c[2]), cc_of(c[4]), opt_of(c[4])),
                             (c[1], c[2], c[4]))
    def one_pool(item):
        key, (p, a, ly) = item
        try:
            return key, (p, a, ly), pool_proof(rundir, p, a, ly)
        except Exception as e:      # noqa: BLE001
            return key, (p, a, ly), ({}, "POOL %s %s %s: %s" % (p, a, ly, e))
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        pools = list(ex.map(one_pool, sorted(texts.items())))
    prefused = [why for _k, _t, (_l, why) in pools if why]
    bad += prefused
    for _k, (p, a, ly), (lay, why) in pools:
        print("# pool %s %s %s: %s%s" % (p, a, ly, "; ".join(
            "v%d 64B %s 32B %s rel %s" % (v, ",".join(map(str, p64)), ",".join(map(str, p32)), "/".join(map(str, rel)) or "-")
            for v, (p64, p32, rel) in sorted(lay.items())), " REFUSED" if why else ""))
    spread64 = [len({p64 for p64, _q, _r in lay.values()}) for _k, _t, (lay, _w) in pools if lay]
    nrel = [len({r for _a, _b, r in lay.values()}) for _k, _t, (lay, _w) in pools if lay]
    print("# dry: layout pools (rev 12, r41 L9): %d timed texts x %d variants = %d exes, every variant answer-gated; "
          "distinct 64-B phase vectors (each hot loop's) per pool min %s max %s; distinct relative layouts per pool min %s max %s; "
          "pools REFUSED %d" % (len(pools), POOL_SIZE, len(pools) * POOL_SIZE, min(spread64, default="-"),
                                max(spread64, default="-"), min(nrel, default="-"), max(nrel, default="-"),
                                len(prefused)))
    print("# dry: cells %d, built and gated %d, failures %d; distinct compiles %d; subject %d B" %
          (len(cl), len(cl) - len(bad), len(bad), len({(b[0], arm_base(b[1]), b[2], b[3]) for b in builds}), n))
    if sel is None:
        same = identical_to_I(rundir)
        print("# dry: H(h) artifact hash-equal to I's (I's pool, measured per layer): %s" % ", ".join(
            "%s/%s:%s" % (p, ly, ",".join(map(str, hs))) for p, d in sorted(same.items()) for ly, hs in sorted(d.items())))
    for b in bad[:20]:
        print("FAIL", b)
    return 1 if bad else 0


def identical_to_I(rundir):
    """Per C1-C2 pattern and LAYER, the finite heads whose built artifact hash-equals I's (MEASURED
    when the cells are built, never inferred from h >= k; rulings R1, rev 8 r36 G3: rev 7 read
    the SIMD-off layer for both). Where it does, the rule reads I's POOLED median for the head:
    one text, one binary, one reading (rev 7, F2)."""
    out = {}
    for card in ("C1", "C2"):
        for p in CARD_PATS[card]:
            out[p] = {}
            for ly in LAYERS:
                ia = hashlib.sha256(open(artifact(rundir, p, "I", ly), "rb").read()).hexdigest()
                out[p][ly] = [h for h in GRID if hashlib.sha256(
                    open(artifact(rundir, p, "h%d" % h, ly), "rb").read()).hexdigest() == ia]
    return out


def same_heads(same, pat, ly):
    """The heads whose text is I's for (pattern, layer), from the measured record (validated by
    `pool_record_refusal` before the rule reads it: no silent default, r37 H3)."""
    return same[pat][ly]


def cmd_run(args):
    (rundir,), opt = parse_args("run", args, nflags=("--with-approx",))
    os.makedirs(rundir, exist_ok=True)
    res = os.path.join(rundir, "results.tsv")
    if os.path.exists(res):
        raise SystemExit("cards: %s exists; a night's step 1 runs once (re-runs: `rerun`)" % res)
    # a RUNDIR is ONE night (rev 12, r41 L6): any results file of an earlier timing refuses, so a G2 record
    # can only be this night's (its run id must match RUNDIR's, `night_g2`)
    old = [n for n in os.listdir(rundir) if n.startswith("results") and n.endswith(".tsv")]
    if old:
        raise SystemExit("cards: %s holds %s from an earlier timing: a RUNDIR is one night" % (rundir, ", ".join(sorted(old))))
    print("cards: run id %s" % start_timing(rundir))
    open(res, "w").close()
    dbad, nI, nreach = check_deny(rundir, cells(cards=STEP1))
    print("cards: deny check: %d arm-I artifacts loop-free, reach %d" % (nI, nreach))
    if dbad:
        for b in dbad:
            print("FAIL", b)
        os.remove(res)
        raise SystemExit("cards: the deny check failed; no timing")
    json.dump(identical_to_I(rundir), open(os.path.join(rundir, "same_as_I.json"), "w"))
    time_cells(rundir, cells(cards=STEP1), res, with_approx="--with-approx" in opt)
    print("cards: results in %s; next: cards.py rule %s" % (res, rundir))


def c3_deny_check(rundir):
    """The deny check on step 2b's population (rev 8, r36 G7; rev 9, r37 H4). C3 and C4 are where
    an ignored deny loops; step 1's patterns never reach that. The REACH arm is the DEFECT'S OWN
    arm: an ignored deny renders I as the build's default head H(64), so the reach is H(64)'s
    artifacts over C3 and C4, rendered whatever h* the step times (rev 8's L proved the regex
    works, not that the defect's arm loops: at width 32 only C4's hex32 at h0 loops, and an
    ignored deny read GREEN). Where H(64) loops nowhere (width 32) the check is VACUOUS and red."""
    return check_deny(rundir, cells(hstar=GRID_TOP, cards=STEP2B), reach_arm="h%d" % GRID_TOP,
                      vacuous_why="H(%d) loops nowhere in C3/C4 at this window width (a width below the cards' "
                                  "longest span, e.g. 32), or its loop text moved" % GRID_TOP)


def cmd_c3(args):
    (rundir, hs), _opt = parse_args("c3", args, npos=2)
    try:
        h = int(hs)
    except ValueError:
        raise SystemExit2("cards: c3: head %r is not a number" % hs)
    if h not in GRID:
        raise SystemExit("cards: c3: %d is not a finite grid head" % h)
    res = os.path.join(rundir, "results_c3_h%d.tsv" % h)
    if os.path.exists(res):
        raise SystemExit("cards: %s exists (re-runs: `rerun`)" % res)
    dbad, nI, nreach = c3_deny_check(rundir)
    print("cards: c3: deny check on C3 and C4: %d arm-I artifacts loop-free, reach (h%d, the arm an ignored deny "
          "renders) %d" % (nI, GRID_TOP, nreach))
    if dbad:
        for b in dbad:
            print("FAIL", b)
        raise SystemExit("cards: c3: the deny check failed; no timing")
    open(res, "w").close()
    time_cells(rundir, cells(hstar=h, cards=("C3",)), res, with_approx=False)
    with open(os.path.join(rundir, "sizes_h%d.tsv" % h), "w") as f:
        for c in cells(hstar=h, cards=("C4",)):
            try:
                f.write("\t".join(c) + "\t" + run_cell(rundir, c, 0) + "\n")
            except Exception as e:      # noqa: BLE001
                f.write("\t".join(c) + "\tFAIL " + str(e).replace("\n", " ")[:300] + "\n")
    print("cards: C3 at H(%d) in %s; next: cards.py rule %s" % (h, res, rundir))


G2_RECORD = "rule_g2.json"


RUN_ID = "run_id"


def run_id(rundir, create=False):
    """The night's run id (RUNDIR/run_id, written by the first command that needs it: `dry`, `run`,
    or `rule`/`rerun --g2` recording the list before any timing, as job 701 does): keys the G2 record
    (rev 12, r41 L6) and seeds the per-launch layout draws (rev 12, r41 L9). Renewed only by `run`
    (`start_timing`, r44 E) when the id already timed a night. None when absent and not created."""
    p = os.path.join(rundir, RUN_ID)
    if not os.path.exists(p):
        if not create:
            return None
        os.makedirs(rundir, exist_ok=True)
        open(p, "w").write("%s\n" % hashlib.sha256(os.urandom(32)).hexdigest()[:16])
    return open(p).read().strip()


RUN_TIMED = "run_id.timed"


def start_timing(rundir):
    """`run`'s run id (r44 E): the RUNDIR's id, unless that id already TIMED a night (RUNDIR/run_id.timed
    names it: a RUNDIR re-used after its results files were removed), in which case a FRESH id is minted,
    so no draw sequence repeats. A G2 record keyed to any other id then REFUSES (exit 2): the record a
    job writes before `run` (701) is kept, an earlier night's never is. Marks the id timed."""
    rid = run_id(rundir, create=True)
    pt = os.path.join(rundir, RUN_TIMED)
    if os.path.exists(pt) and open(pt).read().strip() == rid:
        open(os.path.join(rundir, RUN_ID), "w").write("%s\n" % hashlib.sha256(os.urandom(32)).hexdigest()[:16])
        rid = run_id(rundir)
    rec = os.path.join(rundir, G2_RECORD)
    if os.path.exists(rec):
        old = json.load(open(rec)).get("run_id")
        if old != rid:
            raise SystemExit2("cards: run: %s holds run %s, this timing is run %s: a G2 record of another night "
                              "(remove it and record --g2 again)" % (G2_RECORD, old, rid))
    open(pt, "w").write("%s\n" % rid)
    return rid


def parse_args(cmd, args, nflags=(), vflags=(), npos=1):
    """The command's arguments, STRICT (rev 12, RULED r41 L6): `npos` positionals, the boolean flags
    `nflags`, the valued flags `vflags` as `--x VALUE` or `--x=VALUE`; anything else (an unknown or
    mistyped option, a valueless `--g2`, a missing or extra positional) refuses with exit 2."""
    pos, opt, i = [], {}, 0
    while i < len(args):
        a = args[i]
        if a.startswith("--"):
            name, eq, val = a.partition("=")
            if name in vflags:
                if not eq:
                    if i + 1 >= len(args) or args[i + 1].startswith("--"):
                        raise SystemExit2("cards: %s: %s needs a value" % (cmd, name))
                    i += 1
                    val = args[i]
                if not val:
                    raise SystemExit2("cards: %s: %s needs a value" % (cmd, name))
                opt[name] = val
            elif name in nflags and not eq:
                opt[name] = True
            else:
                raise SystemExit2("cards: %s: unknown option %r (known: %s)" % (cmd, a, " ".join(
                    sorted(nflags) + ["%s FILE" % v for v in sorted(vflags)]) or "none"))
        else:
            pos.append(a)
        i += 1
    if len(pos) != npos:
        raise SystemExit2("cards: %s: %d positional argument(s) expected, got %d (%s)" % (cmd, npos, len(pos),
                                                                                           " ".join(pos) or "none"))
    return pos, opt


class SystemExit2(SystemExit):
    """A refusal with exit code 2 (the message on stderr)."""

    def __init__(self, msg):
        sys.stderr.write(msg + "\n")
        super().__init__(2)


def night_g2(rundir, g2file=None):
    """R0's G2 list for the night, ONE source for every command (rev 11, RULED r39 K6): `--g2 FILE`
    (one defective head per line) is recorded in RUNDIR/rule_g2.json; a command without `--g2`
    reads that record (none recorded: no G2-defective head). Returns (set, where it came from).
    Rev 12 (RULED r41 L6): the record is KEYED by the night's run id and the G2 file's sha-256; a
    record of another run (a reused RUNDIR), or a file whose bytes moved since it was recorded,
    REFUSES (exit 2), as does `--g2` naming a file that differs from the recorded one."""
    rec = os.path.join(rundir, G2_RECORD)
    rid = run_id(rundir, create=bool(g2file))
    old = json.load(open(rec)) if os.path.exists(rec) else None
    if old is not None and old.get("run_id") != rid:
        raise SystemExit2("cards: %s holds run %s, this RUNDIR is run %s: a stale G2 record (remove it and pass "
                          "--g2 again)" % (G2_RECORD, old.get("run_id"), rid))
    if g2file:
        raw = open(g2file, "rb").read()
        try:
            g2 = {int(x) for x in raw.decode().split()}
        except ValueError:
            raise SystemExit2("cards: --g2 %s: not one head a line" % g2file)
        sha = hashlib.sha256(raw).hexdigest()
        if old is not None and old.get("sha") != sha:
            raise SystemExit2("cards: --g2 %s (sha %s) differs from the night's recorded G2 list (sha %s, %s): one "
                              "list a night" % (g2file, sha[:12], str(old.get("sha"))[:12], old.get("from")))
        json.dump({"g2": sorted(g2), "from": os.path.abspath(g2file), "sha": sha, "run_id": rid}, open(rec, "w"))
        return g2, "from %s (sha %s), recorded in %s" % (g2file, sha[:12], G2_RECORD)
    if old is not None:
        f = old.get("from")
        if f and os.path.exists(f) and hashlib.sha256(open(f, "rb").read()).hexdigest() != old.get("sha"):
            raise SystemExit2("cards: the G2 file %s changed since %s recorded it: refused" % (f, G2_RECORD))
        return set(old["g2"]), "recorded in %s (sha %s)" % (G2_RECORD, str(old.get("sha"))[:12])
    return set(), "none given, none recorded"


def owed_now(rundir, g2file=None):
    """The rule over the night with its recorded G2 list: THE one computation of what is owed
    (`owed_rerun`, `owed_confirm`), called by `rule` and by `rerun` alike (rev 11, r39 K6: rev 10's
    `rerun` read an empty G2 list, owed a subset of `rule --g2`'s confirms, and the night stalled)."""
    g2, src = night_g2(rundir, g2file)
    v = analyse(load_night(rundir), g2)
    v["g2"], v["g2_src"] = g2, src
    return v


def confirm_name(k):
    """The results file of confirm ROUND k (r44 D): round 1 `results_confirm.tsv`, round k
    `results_confirm_r<k>.tsv`. A round's file name salts its launch draws (`time_cells`), so no round
    repeats another's draw sequence, and each head's confirm reads the I row of ITS OWN round."""
    return "results_confirm.tsv" if k == 1 else "results_confirm_r%d.tsv" % k


CONFIRM_RE = re.compile(r"^results_confirm(_r([0-9]+))?\.tsv$")


def confirm_round(name):
    """The confirm round a results file holds (`confirm_name`'s inverse), else None."""
    m = CONFIRM_RE.match(name)
    return None if not m else int(m.group(2) or 1)


def confirm_cells(owed):
    """The confirm's arm cells for owed {(card, pat, regime, layer): [heads]}: I and each owed head,
    every launch a FRESH draw of its arm's layout pool (rev 12, r41 L9: the pools replace rev 11's
    fresh twins I.cf / h<N>.cf). THE one spelling: `rerun` times it and the drills build their
    confirm rows from it (r41 L5)."""
    out = []
    for (card, pat, rg, ly), hs in sorted(owed.items()):
        out += [(card, pat, a, rg, ly) for a in ["I"] + ["h%d" % h for h in sorted(hs)]]
    return out


def cmd_rerun(args):
    """Re-times every cell the rule lists as void ONCE, all arms of the cell (F7), into
    results_rerun.tsv / results_c3_h<H>_rerun.tsv; and every cell the rule lists as holding a win
    beyond f, ONCE, into results_confirm.tsv (rev 10, r38 R2: confirm by re-run)."""
    (rundir,), opt = parse_args("rerun", args, vflags=("--g2",))
    v = owed_now(rundir, opt.get("--g2"))
    print("cards: rerun: R0's G2 list %s (%s)" % (sorted(v["g2"]) or "none", v["g2_src"]))
    if v["code"] == 2:
        print("cards: rerun: the night is void or defective (`rule` says why); nothing to re-run")
        return 2
    todo = v["owed_rerun"]
    if v["owed_confirm"]:
        cl = confirm_cells(v["owed_confirm"])
        k = 1 + sum(1 for n in os.listdir(rundir) if confirm_round(n) is not None)
        time_cells(rundir, cl, os.path.join(rundir, confirm_name(k)))
        print("cards: confirming re-run of %d cells (%d arm cells: I and each winning head, fresh pool draws) that "
              "hold a win beyond f" % (len(v["owed_confirm"]), len(cl)))
        return 0
    if not todo:
        print("cards: rerun: no cell is void once and no win awaits its confirm")
        return 0
    for src, cellkeys in todo.items():
        # every arm the card defines for the cell, whether or not step 1 wrote its row
        defined = (cells(cards=STEP1) if src == "results.tsv" else
                   cells(hstar=int(src[len("results_c3_h"):-len(".tsv")]), cards=("C3",)))
        cl = [k for k in defined if (k[0], k[1], k[3], k[4]) in cellkeys]
        time_cells(rundir, cl, os.path.join(rundir, src.replace(".tsv", "_rerun.tsv")))
        print("cards: re-timed %d cells (%d arm cells) of %s" % (len(cellkeys), len(cl), src))
    return 0


# ---- THE RULE (r45_reply rev 11 §3, R0-R5, steps (1)-(5)) -------------------------------------
def r1(heads, cells_read, void_cells, t, tI, same_as_I, f, top=None, measured="MEASURED", wins_ok=None, fh=None, fp=None):
    """R1 over the FINITE heads `heads` (R0 already applied). cells_read: the C1-C2 cells with a
    reading; void_cells: the cells void twice (or void by method); t[h][c], tI[c] the raw
    medians; same_as_I[h][c] true where H(h)'s text is I's in cell c; f the floor, one number
    or {cell: floor} (rev 8, r36 G2: each cell's (regime, layer) floor). `top`: the largest
    R0-surviving head (rev 8, r36 G5), never the constant. Returns (h*, label, recorded pick or
    None, detail); h* None when no finite head survives R0. `wins_ok`: the (head, cell) wins the
    confirm reproduced (rev 11, r39 K4 READING B: they gate step (4)'s "beat I beyond f" ONLY;
    W, E and dominance read the first reading); None: every first-reading win counts. `fh(c, h)` (r44
    B): the floor of H(h) vs I in cell c (step (4)'s win and E's tolerance); `fp(c, g, h)`: the floor
    of H(g) vs H(h) (dominance); both default to f's cell floor."""
    if not heads:
        return None, "no form ships: every finite head failed R0 (plan A's fallback: forms land OFF)", None, {}
    fc = (lambda c: f[c]) if isinstance(f, dict) else (lambda c: f)      # noqa: E731
    fh = fh or (lambda c, h: fc(c))      # noqa: E731
    fp = fp or (lambda c, g, h: fc(c))      # noqa: E731
    # E reads worst ratios across cells: its tolerance is the largest floor of the cells read
    fE = max((fc(c) for c in cells_read), default=max(f.values(), default=0.0) if isinstance(f, dict) else f)
    if top is None:
        top = max(heads)
    lead = ("h = grid top (%d, CHOSEN)" % top if top == GRID_TOP else
            "h = %d, the largest R0-surviving head (CHOSEN; the grid top failed R0)" % top)
    # (1) W(h): the worst ratio to I over the cells READ; a twice-void cell adds the term 1
    #     for each head whose text is I there, no term for any other head
    W = {}
    for h in heads:
        terms = [t[h][c] / tI[c] for c in cells_read]
        terms += [1.0 for c in void_cells if same_as_I[h][c]]
        W[h] = max(terms) if terms else float("inf")
    # (2) E, computed once, never chained
    m = min(W.values())
    # r44 B: E's tolerance per head, the largest of ITS floors against I over the cells read, and the
    # minimum's own (W(h) / W(min) compares two heads' worst ratios to I); with one floor a cell this is fE
    fEh = {h: max((fh(c, h) for c in cells_read), default=fE) for h in heads}
    hm = min(heads, key=lambda h: W[h])
    E = sorted(h for h in heads if W[h] <= (1 + max(fEh[h], fEh[hm])) * m)

    # (3) dominance over the cells READ only: g dominates h when g is faster beyond f in at
    #     least one cell and slower beyond f in none; keep the members dominated by the fewest
    def dom(g, h):
        faster = any(t[h][c] / t[g][c] > 1 + fp(c, g, h) for c in cells_read)
        slower = any(t[g][c] / t[h][c] > 1 + fp(c, g, h) for c in cells_read)
        return faster and not slower
    nd = {h: sum(1 for g in E if g != h and dom(g, h)) for h in E}
    least = min(nd.values())
    kept = [h for h in E if nd[h] == least]
    # (4) the LARGEST kept head that is the top or itself beat I beyond f in some cell read
    #     (rev 8, r36 G4: the tolerance is not transitive, so a kept head within f of a
    #     winner and within f of I measured no win and never ships)
    won = [h for h in kept if any(tI[c] / t[h][c] > 1 + fh(c, h) and (wins_ok is None or (h, c) in wins_ok)
                                  for c in cells_read)]
    cand = [h for h in kept if h == top or h in won]
    pick = max(cand) if cand else top
    if pick not in won:             # the top on a tie: CHOSEN (a top that measured a win is MEASURED)
        tie = "every finite head" if top == GRID_TOP else "every R0-surviving head"
        if not cand:
            label = "%s: no kept head (%s) measured a win against I beyond f" % (lead, ", ".join(map(str, kept)))
        elif E == sorted(heads):
            label = "%s, on a measured tie of %s" % (lead, tie)
        elif E == [top]:
            label = "%s: every shorter finite head measured slower beyond f" % lead
        else:
            label = "%s, on a measured tie of {%s}" % (lead, ", ".join(map(str, E)))
    else:
        label = measured
    detail = {"W": W, "E": E, "dominated_by": nd, "kept": kept, "won": won, "fE": fE}
    # (5) VOID: a C1-C2 cell void twice never helps a head; h* is the LARGEST R0-SURVIVING head
    #     (rev 7, F5), the grid top whenever it survives
    if void_cells:
        hs = top
        vs = sorted(void_cells)
        named = ", ".join(vs) if len(vs) <= 6 else "%s, ... (%d in all)" % (", ".join(vs[:4]), len(vs))
        return hs, ("%s: cell(s) %s void twice; the cells read picked H(%d)"
                    % (lead, named, pick)), pick, detail
    return pick, label, None, detail


def z_upper(p):
    """The standard normal quantile at 1 - p."""
    return statistics.NormalDist().inv_cdf(1 - p)


def _gamma_p(a, x):
    """The regularized lower incomplete gamma P(a, x): series below a + 1, Lentz's continued
    fraction for Q above (Numerical Recipes' split)."""
    if x <= 0:
        return 0.0
    lead = math.exp(-x + a * math.log(x) - math.lgamma(a))
    if x < a + 1:
        s = term = 1.0 / a
        ap = a
        for _ in range(10000):
            ap += 1
            term *= x / ap
            s += term
            if abs(term) < abs(s) * 1e-15:
                break
        return s * lead
    tiny = 1e-300
    b = x + 1 - a
    c, d = 1 / tiny, 1 / b
    h = d
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = tiny if abs(d) < tiny else d
        c = b + an / c
        c = tiny if abs(c) < tiny else c
        d = 1 / d
        h *= d * c
        if abs(d * c - 1) < 1e-15:
            break
    return 1 - lead * h


@functools.lru_cache(maxsize=None)
def chi2_lower(q, n):
    """chi-square(n)'s q quantile, EXACT by bisection on P(n/2, x/2) (rev 9: the twin term's
    degrees of freedom can be small, where rev 8's Wilson-Hilferty form is poor)."""
    lo, hi = 0.0, n + 20 * math.sqrt(2 * n) + 20
    for _ in range(100):
        mid = (lo + hi) / 2
        if _gamma_p(n / 2, mid / 2) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def count_floor(aa_logs, n_comp, alpha=ALPHA):
    """THE FLOOR f (rev 7, r35 F2): sized to the rule's comparison count. aa_logs: ln(t(aa) /
    t(aa.b)) over the A/A cells read (two arms of aa's pool, each launch its own draw); n_comp: the number of one-sided head-against-I
    comparisons the rule makes (heads x cells read where the head's text is not I's). sigma is the
    A/A cells' RMS log ratio (two independent medians, as a head against I), raised to its
    SIGMA_CONF upper bound; f = exp(z(alpha / N) sigma_up) - 1, never below the largest A/A ratio
    itself (the floor cover_cap.md §11.4 reads)."""
    n = len(aa_logs)
    sig = math.sqrt(sum(x * x for x in aa_logs) / n)
    sig_up = sig * math.sqrt(n / chi2_lower(1 - SIGMA_CONF, n))
    z = z_upper(alpha / max(1, n_comp))
    f_aa = max(math.exp(abs(x)) - 1 for x in aa_logs)
    return max(f_aa, math.exp(z * sig_up) - 1), {"sigma": sig, "sigma_up": sig_up, "z": z, "N": n_comp,
                                                  "f_aa": f_aa}


def launch_sigmas(rows, raw=False):
    """Per (regime, layer), the launch sigma (log scale) of its timed arm cells: median SD /
    MED_SD5; a thin pool borrows the night's. raw: {pool: (own sigma, n arms)} as well."""
    pools, allsd = {}, []
    for k, r in rows.items():
        if r["status"] == "ok" and len(r["launches"]) >= 2:
            lg = [math.log(v) for v in r["launches"]]
            sd = statistics.stdev(lg)
            pools.setdefault((k[3], k[4]), []).append(sd)
            allsd.append(sd)
    glob = statistics.median(allsd) / MED_SD5 if allsd else 0.0
    sigs = {p: (statistics.median(v) / MED_SD5 if len(v) >= MIN_POOL else glob) for p, v in pools.items()}
    if raw:
        return sigs, glob, {p: (statistics.median(v) / MED_SD5, len(v)) for p, v in pools.items()}, len(allsd)
    return sigs, glob


def twin_sigmas(pool_logs):
    """THE TWIN CONTRASTS (rev 9, RULED r37 H1 + H2): per (regime, layer), the noise of one
    ratio of two arms' medians, read from the arms the night ALREADY times that are one binary:
    I's pool in each C1-C2 cell read (I and every head whose artifact hash-equals I's there).
    pool_logs: {(regime, layer): [[ln median of each pool arm], ...]}, one list per cell. Within
    a pool every arm has one true time, so its spread is launch noise PLUS between-run noise
    (an arm-level offset held over all 5 launches, which the launch sigma cannot see). sigma_c
    = sqrt(2 x SS / df), SS the pools' summed squared deviations from their own means and df the
    summed (arms - 1): the RMS of the pools' log-median contrasts, the log SD of a head against
    I. Returns {(regime, layer): (sigma_c, df)}; a (regime, layer) with no pool of two is absent."""
    out = {}
    for p, pools in pool_logs.items():
        ss, df = 0.0, 0
        for xs in pools:
            if len(xs) >= 2:
                m = sum(xs) / len(xs)
                ss += sum((x - m) ** 2 for x in xs)
                df += len(xs) - 1
        if df:
            out[p] = (math.sqrt(2 * ss / df), df)
    return out


def pool_floors(f_aa, raw, glob, n_all, n_comp, alpha=ALPHA, twins=None):
    """THE PER-(REGIME, LAYER) FLOOR (rev 8, r36 G2; rev 9, r37 H1): f(regime, layer) = max(
    the A/A floor `f_aa`, the LAUNCH term exp(z(alpha / N) x sqrt(2) x SDMED5 x sigma_up) - 1,
    the TWIN term exp(z(alpha / N) x sigma_c_up) - 1). sigma_up: the pool's launch sigma raised to
    its SIGMA_CONF upper bound (MEDSD_REL / sqrt(n)); a thin pool takes the LARGER of its own and
    the night's sigma (r37 H10 (1): the bimodal test borrows the night's; the floor never goes
    below its own). sigma_c_up: `twins`' sigma_c raised to its SIGMA_CONF upper bound
    sqrt(df / chi2(1 - SIGMA_CONF; df)). The launch term sees one arm's launch scatter only; the
    twin term sees an arm-level (between-run) offset in its own (regime, layer), which neither
    the launch term nor the night-wide A/A term can (r37 H1)."""
    z = z_upper(alpha / max(1, n_comp))
    zc = statistics.NormalDist().inv_cdf(SIGMA_CONF)
    twins = twins or {}
    out = {}
    for p, (s, n) in raw.items():
        up = s * (1 + zc * MEDSD_REL / math.sqrt(n))
        if n < MIN_POOL:
            up = max(up, glob * (1 + zc * MEDSD_REL / math.sqrt(max(1, n_all))))
        fl = max(f_aa, math.exp(z * math.sqrt(2) * SDMED5 * up) - 1) if POOL_TERM else f_aa
        if TWIN_TERM and p in twins:
            fl = max(fl, twin_term(twins[p], z))
        out[p] = fl
    return out


def twin_term(tw, z):
    """One twin term: exp(z x sigma_c,up) - 1, sigma_c raised to its SIGMA_CONF upper bound
    sqrt(df / chi2(1 - SIGMA_CONF; df)) (exact; df can be small)."""
    sc, df = tw
    return math.exp(z * sc * math.sqrt(df / chi2_lower(1 - SIGMA_CONF, df))) - 1


# Rev 11's LAYOUT_TERM / LAYOUT_TWIN_ARM / LAYOUT_TWINS switches and `layout_sigma` are DELETED (rev
# 12, r41 L9): the layout pools put layout noise in every arm's launches, so no separate term reads it.
READING_B = True    # selftest's K4 control turns reading B off (rev 10: an unreproduced win read as a tie in W/E/dominance)
POOL_I = True       # selftest's control turns I's pool off (rev 7's reading) to show the G3 drill sees it
POOL_TERM = True    # selftest's control turns the pool term off (rev 7's floor) to show the drill sees it
TWIN_TERM = True    # selftest's controls turn the twin term off (rev 8's floor) to show the H1 drill sees it
AGREE_GATE = True   # ... and the agreement gate off (rev 8's rule) to show the H2 drill sees it
PAT_TWIN = True     # selftest's controls turn the PER-PATTERN twin term off (rev 9's floor) to show J1's drill sees it
CONFIRM = True      # ... and the confirming re-run off (rev 9's rule) to show the arm-level drill sees it (r38 R2)


LAYOUT_TEXT_TERM = True    # selftest's control turns the per-TEXT layout term off (rev 12 before R2 B)
VARIANT_BIMODAL = True     # ... and the variant-aware bimodal test off (rev 12 before R2 C: the raw launches)
PER_HEAD_FLOOR = True      # r44 B: the layout term per (cell, head); off: rev 12's one cell max (the control)
INTERACTION_VOID = True    # r44 A: void a text's cells on a variant x regime interaction; off: rev 12 (the control)
# r44 A: THE VARIANT x REGIME INTERACTION LINES. A text's interaction is read from its own launches by a
# lack-of-fit test: the per-text fit (row level + one effect a variant) against the (row, variant) cell
# means, the launch noise from the launches that repeat a variant inside one row (pure error: r45 FORMS8-1,
# the TEXT's OWN, on launches winsorized at INTER_CLIP, its regime shape from the night's pool per regime;
# r44 pooled it per regime over every text, which read a noisier text or heavy tails as an interaction;
# `text_interaction`). INTER_SHARE: the share sI2 / (sI2 + sL2), sI2 = max(0, MS(lack of fit) - the
# pure-error variance), on the mean-square scale: an INDEX, NOT the variance share (the lack-of-fit mean
# square carries ~1.3 launches a (row, variant) cell, so it is not a variance component), and it does NOT
# BIND today (r45 FORMS8-3): with sL2 ~ 0 (a small layout main effect) the share is 1 for any sI2 > 0, so the
# F line at INTER_ALPHA alone decides. A text whose share exceeds INTER_SHARE AND whose lack of fit is beyond
# its own launch noise at INTER_ALPHA (family-wise over the night's texts, F on Satterthwaite df shrunk for
# the night's kurtosis) has its C1-C2 cells VOIDED: the per-text term assumes one effect a variant in every
# regime, which that text does not show. THE VOID'S SCOPE (r45 FORMS8-1 (b), ruled): r1 step (5) returns the
# grid top for the WHOLE NIGHT when any cell is void, so ONE flagged text means NO PICK THAT NIGHT
# (conservative by design; the would-be pick is only recorded). PLANNED (r45 FORMS8-3): an effect-size floor
# for the void (sI2 above a stated fraction of the floor's own variance), trigger = the first real night that
# flags a text. COUPLING (r45 FORMS8-4): r44 B's per-head floor does not hold P(h* != 64) under a
# regime-specific layout on its own (its V_h pools the head's text over its regimes); THIS void carries that
# safety, so a looser line re-opens it.
# UNMEASURED DEFAULT: INTER_SHARE = 0.5 (set so drill (xxiii)'s interaction rows pass; never measured on
# a real pool).
INTER_SHARE = 0.5
# UNMEASURED DEFAULT: INTER_ALPHA = 0.01 (the night's false-void budget for this test, family-wise).
INTER_ALPHA = 0.01
INTER_PE_PER_TEXT = True   # r45 FORMS8-1: the lack of fit against the TEXT's own pure error; off: r44's pure
                           # error pooled per regime over the night's texts (the control)
# UNMEASURED DEFAULT: INTER_MIN_PE_DF = 4 (a text with fewer pure-error df is not read for the interaction:
# never flagged; a head text's six regime rows carry ~12 at LAUNCHES 5 over POOL_SIZE 4).
INTER_MIN_PE_DF = 4
# INTER_CLIP = 4.0: the interaction test's winsorizing line, in robust launch sigmas (`_clipped`; a normal
# launch passes it but for ~6e-5). MEASURED on the drill's SYNTHETIC models only (lane formsfixm, 300 nights a
# reading): t(5) launches + "phase" tau 1 % + one 5 % H(8) win, nights flagged 21 / 9 / 11 / 10 / 10 of 300 at
# no clip / 5 / 4 / 3.5 / 3; r44 A's "regime" heads tau 3 % row (seed 3331), P(h* != 64) 0.010 / 0.013 / 0.023
# / 0.030 / 0.053: 4 is the lowest line that holds both gates with room. On a real night UNMEASURED.
INTER_CLIP = 4.0


def _additive_fit(rs, vs):
    """The per-text two-way fit (rev 12, R2 B): log x = row level + variant effect, backfitting 4
    passes, the effects centred to mean 0. `rs` [(row key, log launches, variants)]."""
    e = {v: 0.0 for v in vs}
    lev = {}
    for _ in range(4):
        for k, ls, vv in rs:
            lev[k] = sum(x - e[v] for x, v in zip(ls, vv)) / len(ls)
        acc = {v: [] for v in vs}
        for k, ls, vv in rs:
            for x, v in zip(ls, vv):
                acc[v].append(x - lev[k])
        e = {v: sum(a) / len(a) for v, a in acc.items()}
        m = sum(e.values()) / len(e)
        e = {v: x - m for v, x in e.items()}
    return lev, e


def _fit_stats(rs, vs, lev, e):
    """A text's fit statistics (r44 A): the residual SS and df, per row (key, launches, pure-error SS
    and df: the launches that repeat a variant inside the row), and per row the pure-error deviations'
    moments (r45 FORMS8-1: each squared deviation scaled by m / (m - 1), m its group's size, unbiased for
    the launch variance: (sum, sum of squares, count)); `fit` keeps the data for the robust re-read."""
    res = [x - lev[k] - e[v] for k, ls, vv in rs for x, v in zip(ls, vv)]
    prow, qrow = [], []
    for k, ls, vv in rs:
        g = {}
        for x, v in zip(ls, vv):
            g.setdefault(v, []).append(x)
        ss = sum((x - sum(a) / len(a)) ** 2 for a in g.values() for x in a)
        prow.append((k, len(ls), ss, len(ls) - len(g)))
        d2 = [(x - sum(a) / len(a)) ** 2 * len(a) / (len(a) - 1) for a in g.values() if len(a) > 1 for x in a]
        qrow.append((sum(d2), sum(x * x for x in d2), len(d2)))
    return {"ss_res": sum(x * x for x in res), "df_a": len(res) - len(rs) - len(vs) + 1, "rows": prow,
            "q": qrow, "fit": (rs, vs, lev, e)}


def text_effects(rows, text_of, stats=None):
    """THE PER-TEXT LAYOUT EFFECTS (rev 12, RULED R2 B/C): every arm row's launches with their recorded
    pool variants, grouped by the TEXT the arm runs (`text_of(key)`, None: not grouped). Per text a
    two-way fit, log x = row level + variant effect (backfitting, 4 passes; the effects centred to mean
    0), over every row of that text (all its regimes and hash-equal arms). Returns {text: (effects
    {v: e_v}, sL2)}: sL2 the between-variant variance of the effects, unbiased over the pool's
    variants, less the effects' own estimation noise (the residual variance over each variant's
    launch count), floored at 0. A text with launches in fewer than 2 variants is absent. `stats` (a
    dict, r44 A): filled per text with the fit's residual sum of squares and df, and per row (its key,
    launches, pure-error SS and df: the launches that repeat a variant inside the row)."""
    by = {}
    for k, r in (rows.items() if isinstance(rows, dict) else rows):
        if r.get("status") != "ok" or not r.get("variants"):
            continue
        t = text_of(k)
        if t is not None:
            by.setdefault(t, []).append((k, [math.log(x) for x in r["launches"]], r["variants"]))
    out = {}
    for t, rs in by.items():
        vs = sorted({v for _k, _l, vv in rs for v in vv})
        if len(vs) < 2:
            continue
        lev, e = _additive_fit(rs, vs)
        res = [x - lev[k] - e[v] for k, ls, vv in rs for x, v in zip(ls, vv)]
        n = len(res)
        dfr = max(1, n - len(rs) - len(vs) + 1)
        s2 = sum(x * x for x in res) / dfr
        cnt = {v: sum(1 for _k, _l, vv in rs for w in vv if w == v) for v in vs}
        noise = sum(s2 / cnt[v] for v in vs) / len(vs)
        sl2 = max(0.0, sum(x * x for x in e.values()) / (len(vs) - 1) - noise)
        out[t] = (e, sl2)
        if stats is not None:
            stats[t] = _fit_stats(rs, vs, lev, e)
    return out


def _beta_cf(a, b, x):
    """The continued fraction of the regularized incomplete beta (Numerical Recipes' betacf, Lentz)."""
    tiny = 1e-300
    c, d = 1.0, 1 - (a + b) * x / (a + 1)
    d = 1 / (tiny if abs(d) < tiny else d)
    h = d
    for m in range(1, 10000):
        m2 = 2 * m
        for an in (m * (b - m) * x / ((a + m2 - 1) * (a + m2)), -(a + m) * (a + b + m) * x / ((a + m2) * (a + m2 + 1))):
            d = 1 + an * d
            d = 1 / (tiny if abs(d) < tiny else d)
            c = 1 + an / c
            c = tiny if abs(c) < tiny else c
            h *= d * c
        if abs(d * c - 1) < 1e-15:
            break
    return h


def _beta_i(a, b, x):
    """The regularized incomplete beta I_x(a, b)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lead = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return lead * _beta_cf(a, b, x) / a
    return 1 - lead * _beta_cf(b, a, 1 - x) / b


@functools.lru_cache(maxsize=None)
def f_lower(q, d1, d2):
    """F(d1, d2)'s q quantile, EXACT by bisection on its cdf I_{d1 f / (d1 f + d2)}(d1 / 2, d2 / 2)
    (FORMS8-1: the lack-of-fit test against the TEXT's own pure error, whose df are small)."""
    lo, hi = 0.0, 1.0
    while _beta_i(d1 / 2, d2 / 2, d1 * hi / (d1 * hi + d2)) < q:
        hi *= 2
    for _ in range(100):
        mid = (lo + hi) / 2
        if _beta_i(d1 / 2, d2 / 2, d1 * mid / (d1 * mid + d2)) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _clipped(st, s2, regime_of):
    """A text's fit statistics re-read on WINSORIZED launches (r45 FORMS8-1): each launch's residual from
    the text's additive fit, in units of its regime's launch sigma (`s2`, the night's pool per regime),
    clipped at INTER_CLIP times the text's own robust scale (1.4826 x the median absolute standardized
    residual), then the fit and its statistics again. A heavy-tailed launch that lands alone in a (row,
    variant) cell enters the lack of fit whole and the pure error not at all: t(5) launches flagged 21 of
    300 nights on the variance ratio alone (no clip), 11 at INTER_CLIP 4."""
    rs, vs, lev, e = st["fit"]
    z = [(x - lev[k] - e[v]) / math.sqrt(s2[regime_of(k)]) for k, ls, vv in rs for x, v in zip(ls, vv)]
    sc = 1.4826 * statistics.median(abs(x) for x in z)
    if sc <= 0:
        return st
    cap = INTER_CLIP * sc
    rs2 = [(k, [lev[k] + e[v] + max(-cap, min(cap, (x - lev[k] - e[v]) / math.sqrt(s2[regime_of(k)])))
                * math.sqrt(s2[regime_of(k)]) for x, v in zip(ls, vv)], vv) for k, ls, vv in rs]
    lev2, e2 = _additive_fit(rs2, vs)
    return _fit_stats(rs2, vs, lev2, e2)


def text_interaction(te, stats, regime_of, alpha=None, info=None):
    """THE VARIANT x REGIME INTERACTION per text (r44 A; r45 FORMS8-1), from `text_effects`' stats.
    Per text: the lack-of-fit mean square (residual SS less the text's pure-error SS, over (row, variant)
    cells - rows - variants + 1 df) against the TEXT'S OWN pure-error mean square (the launches that
    repeat a variant inside one of its rows), each scaled by its rows' regime launch variances (pooled
    over the night per regime: the SHAPE of the noise across regimes, never its level), an F line at
    alpha / (texts read) on Satterthwaite's effective df of each side (regime-unequal rows weigh
    unequally), both df shrunk by 1 / (1 + kappa / 2), kappa the night's excess kurtosis of the
    pure-error deviations standardized per (text, regime) (a heavy-tailed launch spreads a variance
    ratio as fewer df would: m squared deviations of excess kurtosis kappa vary as m / (1 + kappa / 2)
    normal ones). r44 read the lack of fit against the
    regime pool alone, on chi-square: a text noisier than its regime's pool (one pattern's head arms at
    2x sigma) or heavy-tailed launches (t(5)) read as an interaction (r45 FORMS8-1: 100 and 55 of 100
    nights flagged with none). INTER_PE_PER_TEXT off: that r44 form (the control). Returns {text:
    (share, ratio, line, flagged, df)}; a text with no lack-of-fit df, or fewer than INTER_MIN_PE_DF
    pure-error df, is absent (never flagged). `info` (a dict): filled with the kurtosis read."""
    alpha = INTER_ALPHA if alpha is None else alpha
    pe = {}
    for st in stats.values():
        for k, _n, ss, df in st["rows"]:
            a = pe.setdefault(regime_of(k), [0.0, 0])
            a[0] += ss
            a[1] += df
    s2 = {rg: ss / df for rg, (ss, df) in pe.items() if df > 0}
    cand = {}
    if INTER_PE_PER_TEXT:
        stats = {t: _clipped(st, s2, regime_of) for t, st in stats.items()
                 if all(regime_of(k) in s2 for k, _n, _ss, _df in st["rows"])}
        # each text's own noise level c_t (its pure error over its rows' regime variances), then the night's
        # kurtosis of the deviations standardized by c_t x the regime variance
        lev, m2, m4, nq = {}, 0.0, 0.0, 0
        for t, st in stats.items():
            rows = st["rows"]
            if any(regime_of(k) not in s2 for k, _n, _ss, _df in rows):
                continue
            pw = sum(df * s2[regime_of(k)] for k, _n, _ss, df in rows)
            ssp = sum(ss for _k, _n, ss, _df in rows)
            if pw <= 0 or ssp <= 0:
                continue
            lev[t] = ssp / pw
            for (k, _n, _ss, _df), (q2, q4, n) in zip(rows, st["q"]):
                w = lev[t] * s2[regime_of(k)]
                m2 += q2 / w
                m4 += q4 / (w * w)
                nq += n
        kap = max(0.0, (m4 / nq) / (m2 / nq) ** 2 - 3) if nq and m2 > 0 else 0.0
        shrink = 1 / (1 + kap / 2)
        if info is not None:
            info["kurtosis"], info["df_shrink"] = kap, shrink
        for t, st in stats.items():
            if t not in lev:
                continue
            rows = st["rows"]
            dfp = sum(df for _k, _n, _ss, df in rows)
            dfl = st["df_a"] - dfp
            if dfl < 1 or dfp < INTER_MIN_PE_DF:
                continue
            ssp = sum(ss for _k, _n, ss, _df in rows)
            ssl = max(0.0, st["ss_res"] - ssp)
            # the lack-of-fit df shared over the rows as their (cells - 1)
            cl = [max(0, n - df - 1) for _k, n, _ss, df in rows]
            if sum(cl) <= 0:
                continue
            al = [dfl * c / sum(cl) for c in cl]
            w = [s2[regime_of(k)] for k, _n, _ss, _df in rows]
            lw = sum(a * x for a, x in zip(al, w))
            pw = sum(df * x for (_k, _n, _ss, df), x in zip(rows, w))
            el = lw * lw / sum(a * x * x for a, x in zip(al, w)) * shrink
            ep = pw * pw / sum(df * x * x for (_k, _n, _ss, df), x in zip(rows, w)) * shrink
            # ratio = (msl / its regime expectation) / (msp / its regime expectation): c_t cancels
            cand[t] = (ssl / lw, ssp / pw, el, ep, ssl / dfl, ssp / dfp)
    else:
        for t, st in stats.items():
            rows = st["rows"]
            dfp = sum(df for _k, _n, _ss, df in rows)
            dfl = st["df_a"] - dfp
            if dfl < 1 or any(regime_of(k) not in s2 for k, _n, _ss, _df in rows):
                continue
            ssl = max(0.0, st["ss_res"] - sum(ss for _k, _n, ss, _df in rows))
            nn = sum(n for _k, n, _ss, _df in rows)
            exp_ = sum(n * s2[regime_of(k)] for k, n, _ss, _df in rows) / nn
            if exp_ <= 0:
                continue
            cand[t] = (ssl / dfl, exp_, dfl, None, ssl / dfl, exp_)
    out = {}
    for t, (a, b, dl, dp, msl, mse) in cand.items():
        q = 1 - alpha / len(cand)
        line = f_lower(q, dl, dp) if dp is not None else chi2_lower(q, dl) / dl
        si2 = max(0.0, msl - mse)
        sl2 = te[t][1] if t in te else 0.0
        share = si2 / (si2 + sl2) if si2 > 0 else 0.0
        out[t] = (share, a / b, line, a / b > line and share > INTER_SHARE, dl)
    return out


def varmed5(effects, pool=None, n=None):
    """The variance of the MEDIAN of LAUNCHES draws (uniform over `pool` variants) of the effects
    {v: e_v} (variants never drawn count as e = 0), plus the pool-mean term: exact by the order
    statistics of uniform draws (P(median <= e_(k)) = P(at least ceil(n/2) draws <= the k-th))."""
    pool = pool or POOL_SIZE
    xs = sorted([effects.get(v, 0.0) for v in range(pool)])
    n = n or LAUNCHES
    need = n // 2 + 1
    cdf = []
    for k in range(1, pool + 1):
        q = k / pool
        cdf.append(sum(math.comb(n, j) * q ** j * (1 - q) ** (n - j) for j in range(need, n + 1)))
    pm = [cdf[0]] + [cdf[i] - cdf[i - 1] for i in range(1, pool)]
    mu = sum(p * x for p, x in zip(pm, xs))
    return sum(p * (x - mu) ** 2 for p, x in zip(pm, xs))


def text_var(te, t, n=None):
    """A text's layout variance in one median (rev 12, R2 B): its median-of-draws variance plus its
    finite pool's mean offset (sL2 / POOL_SIZE: the pool's own draw, not the text's speed); 0 when
    the night has no estimate for it."""
    if t not in te:
        return 0.0
    e, sl2 = te[t]
    raw = sum(x * x for x in e.values()) / max(1, len(e) - 1)
    shrink = sl2 / raw if raw > 0 else 0.0           # the noise-corrected share of the plug-in spread
    return varmed5(e, n=n) * shrink + sl2 / POOL_SIZE


def adjusted(r, te, t):
    """A row's launches with its text's per-variant effect removed (rev 12, R2 C), else as read."""
    if not VARIANT_BIMODAL or t not in te or not r.get("variants"):
        return r["launches"]
    e = te[t][0]
    return [x / math.exp(e.get(v, 0.0)) for x, v in zip(r["launches"], r["variants"])]


# THE NIGHT'S POWER AGAINST ITS OWN LAYOUT SIGMA (rev 12, RULED R2 D): `selftest --rev12`'s power rows
# (300 nights each, the "phase" layout model, 1 % launch noise), pinned by hand from the drill (re-pin when
# the rule or the drill moves; r44 L: `selftest --rev12` CHECKS the pins at tau 1 and 2 %, so a stale pin is
# red): {layout tau: (one 5 % winner, one 10 % winner, every head <= 16 5 % faster), each of 300}; rev 11's
# accept lines 270 / 270 / 255. Re-pinned by lane formsfixl (r44 B's per-head floor moved them: rev 12 read
# (170, 299, 176) / (7, 260, 5)). Re-pinned by lane formsfixm (r45 FORMS8-1's per-text interaction test
# voids other nights: rev 13 read (204, 296, 179) / (25, 271, 18)).
POWER_RECORD = {0.0: (281, 300, 279), 0.01: (203, 296, 183), 0.02: (25, 267, 18)}
POWER_ACCEPT = (270, 270, 255)


# r44 K: the night's sigma read (`msig`, the median over texts of sqrt(sL2)) runs LOW: the median of the root
# of a ~3-df variance, less the noise subtraction. MEASURED on the drill's SYNTHETIC model (r44 V11,
# ESTIMATOR-6; the "phase" model, 30 nights a tau), NOT on night data: msig / tau 0.875 / 0.880 / 0.880 at
# tau 1 / 1.5 / 2 %. The bias depends on the layout model and the text mix (under "heads", I's and aa's texts
# read sL2 = 0 and pull the median down; under "rho" only the uncorrelated part is read), and POWER_RECORD is
# drilled under the same "phase" model, so the correction is self-consistent only inside that model: on a
# real night it is an UNMEASURED correction (r45 FORMS8-5). The power line reads msig / this.
SIGMA_READ_BIAS = 0.88


def power_line(sig):
    """The night's power line (R2 D; r44 K): the measured layout sigma corrected for its read bias
    (SIGMA_READ_BIAS), the two RECORD rows that BRACKET it (never the nearest one across a cliff), the
    power interpolated between them in log power, and whether that power is below rev 11's accept lines.
    Above the largest pinned tau: that row is an upper bound."""
    known = {t: v for t, v in POWER_RECORD.items() if v}
    if not known:
        return "no power record pinned"
    sc = sig / SIGMA_READ_BIAS
    ts = sorted(known)
    rowtxt = lambda t: "tau %d %% (%s)" % (round(100 * t), "/".join(map(str, known[t])))      # noqa: E731
    if sc <= ts[0]:
        est, where = known[ts[0]], "at or below the smallest pinned row, %s" % rowtxt(ts[0])
    elif sc >= ts[-1]:
        est, where = known[ts[-1]], ("ABOVE the largest pinned row, %s: the power is at most that row's"
                                      % rowtxt(ts[-1]))
    else:
        lo = max(t for t in ts if t <= sc)
        hi = min(t for t in ts if t > sc)
        w = (sc - lo) / (hi - lo)
        est = tuple(round(math.exp((1 - w) * math.log(max(a, 0.5)) + w * math.log(max(b, 0.5))))
                    for a, b in zip(known[lo], known[hi]))
        where = "between the RECORD rows %s and %s, log-interpolated" % (rowtxt(lo), rowtxt(hi))
    below = [n for n, (got, acc) in zip(("one 5 %", "one 10 %", "multi 5 %"), zip(est, POWER_ACCEPT)) if got < acc]
    return ("measured layout sigma %.4f (read ~%d %% low, r44 K: corrected %.4f) %s: one 5 %% winner %d, one 10 %% "
            "winner %d, every head <= 16 5 %% faster %d, of 300 nights; %s" % (
                sig, round(100 * (1 - SIGMA_READ_BIAS)), sc, where, est[0], est[1], est[2],
                "BELOW rev 11's accept lines (%s): a win of that size may go unseen; a missed win keeps 64 "
                "(speed only, never an answer)" % ", ".join(below) if below else "at or above rev 11's accept lines"))


def bimodal(launches, sig):
    """Two groups of >= 2 launches with more than GAP_K launch sigmas between them (F3)."""
    if len(launches) < 4 or sig <= 0:
        return False
    x = sorted(math.log(v) for v in launches)
    return any(x[i] - x[i - 1] > GAP_K * sig for i in range(2, len(x) - 1))


def load_night(rundir):
    """Every results file of a night: {name: (rows, rerun rows)}, same_as_I, the C3 heads."""
    files = {}
    for name in sorted(os.listdir(rundir)):
        if name.startswith("results") and name.endswith(".tsv") and not name.endswith("_rerun.tsv"):
            files[name] = (read_rows(os.path.join(rundir, name)),
                           read_rows(os.path.join(rundir, name.replace(".tsv", "_rerun.tsv"))))
    sp = os.path.join(rundir, "same_as_I.json")
    # absent: None, which the rule REFUSES (rev 9, r37 H3); never `{}`, which read as I-alone pools
    same = json.load(open(sp)) if os.path.exists(sp) else None
    return {"files": files, "same": same}


def pool_record_refusal(same):
    """I's pool record (`same_as_I.json`) must name EVERY C1-C2 pattern x layer, each list holding
    the grid top (H(64) renders exactly I at every C1-C2 length: rev 8's "at least I and H(64)").
    A missing file, pattern or layer silently shrank every pool to I alone (r37 H3). Returns the
    refusal text, or None."""
    if same is None:
        return "same_as_I.json is missing (I's pool record; `cards.py run` writes it)"
    if not isinstance(same, dict):
        return "same_as_I.json is not a pattern map"
    for card in ("C1", "C2"):
        for pat in CARD_PATS[card]:
            v = same.get(pat)
            if isinstance(v, list):
                return ("same_as_I.json holds rev 7's format (SIMD-off only, one list a pattern): re-run "
                        "`cards.py dry`/`run` to record identity per layer (rev 8)")
            if not isinstance(v, dict):
                return "same_as_I.json lacks C1-C2 pattern %s" % pat
            for ly in LAYERS:
                if ly not in v:
                    return "same_as_I.json lacks pattern %s at layer %s" % (pat, ly)
                if GRID_TOP not in v[ly]:
                    return ("same_as_I.json: pattern %s layer %s lists %s, without the grid top %d (H(%d) renders "
                            "exactly I at every C1-C2 length)" % (pat, ly, v[ly], GRID_TOP, GRID_TOP))
    return None


def merge(rows1, rows2):
    """A re-run replaces EVERY arm of each cell it re-timed; attempts per cell."""
    cell = lambda k: (k[0], k[1], k[3], k[4])      # noqa: E731
    redone = {cell(k) for k in rows2}
    out = {k: r for k, r in rows1.items() if cell(k) not in redone}
    out.update(rows2)
    att = {cell(k): (2 if cell(k) in redone else 1) for k in out}
    return out, att


def analyse(night, g2_defective, alpha=ALPHA):
    """The whole rule over a night's files. Returns a dict: code (0 complete, 2 void/defective,
    3 owed), lines (the record), hstar, label, rec, owed_rerun {file: {cellkeys}}."""
    lines, owed = [], {}
    res = {"code": 0, "lines": lines, "hstar": None, "label": None, "rec": None, "owed_rerun": owed,
           "owed_confirm": {}, "wins": 0, "confirmed": 0}
    if "results.tsv" not in night["files"]:
        lines.append("rule: no results.tsv: step 1 (`run`) has not run")
        res["code"] = 3
        return res
    rows, att = merge(*night["files"]["results.tsv"])
    same = night["same"]
    why_pool = pool_record_refusal(same)
    if why_pool:
        lines.append("rule: REFUSED: %s; I's pools cannot be read: the night is DEFECTIVE (rev 9, r37 H3)" % why_pool)
        res["code"] = 2
        return res
    sigs, glob, sig_raw, n_all = launch_sigmas(rows, raw=True)
    cellk = lambda k: (k[0], k[1], k[3], k[4])      # noqa: E731

    # ---- R0: G2's list, plus every head whose cell gate failed in ANY reading (rev 7, F5; rev 11,
    #      r39 K2: the confirm's reading too, `results_confirm.tsv`, and C3's) -----------------
    # One scan, every results file the night holds, read alike: I or an A/A arm (or a layout twin
    # of either: the reference itself) failing makes the night DEFECTIVE; a head (or its twin)
    # failing is DEFECTIVE; the engine route's failure is filed (R4 not computed there).
    defective = set(g2_defective)
    c3files = {n: merge(*v) for n, v in night["files"].items() if n.startswith("results_c3_h")}
    allfiles = [("results.tsv", rows)] + [(n, merge(*v)[0]) for n, v in sorted(night["files"].items())
                                          if n != "results.tsv"]
    for n, rr in allfiles:
        where = "" if n == "results.tsv" else " (%s)" % n
        for k, r in sorted(rr.items()):
            if r["status"] != "gatefail":
                continue
            if arm_base(k[2]) in ("I", "aa"):
                lines.append("R0: %s failed its gate in %s%s: the reference is wrong; the night is DEFECTIVE "
                             "(filed)" % (k[2], "/".join(k), where))
                res["code"] = 2
                return res
            h = arm_head(k[2])
            if h is not None:
                defective.add(h)
                lines.append("R0: H(%d) failed its gate in %s%s: DEFECTIVE (filed)" % (h, "/".join(k), where))
            else:
                lines.append("R0: the engine route failed its gate in %s%s (filed; R4 not computed there)"
                             % ("/".join(k), where))
    heads = [h for h in GRID if h not in defective]

    # THE TEXTS' LAYOUT EFFECTS (rev 12, RULED R2 B/C): each arm row grouped by the text it runs (I's
    # pool by the measured identity record; each other head its own; aa; the engine route; C3's arms),
    # the per-variant effects fitted over all of that text's rows (every regime, every reading's file)
    def text_of(k):
        card, pat, arm, _rg, ly = k
        if card == "AA":
            return ("aa", ly)
        if card in ("C1", "C2"):
            h = arm_head(arm)
            if arm_base(arm) == "I" or (h is not None and h in same_heads(same, pat, ly)):
                return ("I", pat, ly)
            return (arm_base(arm), pat, ly)
        return (card, pat, arm_base(arm), ly)
    # keyed (file, cell): each file's row its own level (a confirm or re-run row of one cell is a
    # second reading, never the same row's launches)
    tstats = {}
    te = text_effects([((n, k), r) for n, rr in allfiles for k, r in rr.items()], lambda nk: text_of(nk[1]), tstats)
    # r44 A: each text's variant x regime interaction, read from its own launches (`text_interaction`)
    iinfo = {}
    inter = text_interaction(te, tstats, lambda nk: nk[1][3], info=iinfo)
    flagged = {t for t, v in inter.items() if v[3]} if INTERACTION_VOID else set()
    res["inter_flagged"] = len([t for t, v in inter.items() if v[3]])
    adj_rows = {k: dict(r, launches=adjusted(r, te, text_of(k))) if r["status"] == "ok" else r
                for k, r in rows.items()}
    sigs_b, glob_b = launch_sigmas(adj_rows) if VARIANT_BIMODAL else (sigs, glob)

    def is_void(k, r):
        """Void: not ok, or BIMODAL; rev 12 (RULED R2 C): the test reads the launches with the text's
        per-variant effect removed, against the pool's sigma of those adjusted launches, so a split the
        layout draw explains is not a transient."""
        if r["status"] != "ok":
            return r["status"]
        sig = sigs_b.get((k[3], k[4]), glob_b)
        return "bimodal" if bimodal(adjusted(r, te, text_of(k)), sig) else None

    # ---- the floor: A/A cells of the regimes READ (approximated regimes are void by method) ---
    aa_logs = []
    for rg in REGIMES:
        if rg in APPROX:
            continue
        for ly in ("off", "on"):
            a, b = rows.get(("AA", "lit16", "aa", rg, ly)), rows.get(("AA", "lit16", "aa.b", rg, ly))
            bad = [x for x in (a, b) if x is None or is_void(("AA", "lit16", "aa", rg, ly), x)]
            if bad:
                if att.get(("AA", "lit16", rg, ly), 1) < 2:
                    owed.setdefault("results.tsv", set()).add(("AA", "lit16", rg, ly))
                    continue
                lines.append("rule: the floor is not computable (A/A cell %s/%s missing or void twice): the "
                             "night is VOID (cover_cap.md §11.4 row 1)" % (rg, ly))
                res["code"] = 2
                return res
            aa_logs.append(math.log(a["med"] / b["med"]))

    # ---- C1-C2 cells: read, void twice, void by method, or owed a re-run (F7, F8) -----------
    ccells, vc, tI, t = [], [], {}, {h: {} for h in heads}
    sa = {h: {} for h in heads}
    pool_n, pool_meds, cell_key, pool_arms = {}, {}, {}, {}
    for card in ("C1", "C2"):
        for pat in CARD_PATS[card]:
            for rg in REGIMES:
                for ly in ("off", "on"):
                    cid = "%s/%s/%s" % (pat, rg, ly)
                    ident = same_heads(same, pat, ly)
                    for h in heads:
                        sa[h][cid] = h in ident
                    if rg in APPROX:
                        vc.append(cid + " (void by method)")
                        for h in heads:
                            sa[h][cid + " (void by method)"] = sa[h][cid]
                        continue
                    # r44 A: a cell whose I text or a compared head's text shows a variant x regime
                    # interaction is VOID (the per-text term cannot cover it; never re-run: layout is fixed)
                    hit = sorted({text_of((card, pat, a, rg, ly)) for a in ["I"] + ["h%d" % h for h in heads
                                                                                   if not sa[h][cid]]} & flagged)
                    if hit:
                        lab = "%s (variant x regime interaction: %s)" % (cid, ", ".join("/".join(x) for x in hit))
                        vc.append(lab)
                        for h in heads:
                            sa[h][lab] = sa[h][cid]
                        continue
                    # I's POOL (rulings R1, rev 8 r36 G3): I and every arm whose built artifact
                    # hash-equals I's in this cell (measured, `same_as_I.json`), R0 or not: one
                    # binary, so one reading, the median over all their launches
                    # (rev 12, r41 L9: every arm of the pool draws each launch from I's layout pool)
                    pool = ["I"] + (["h%d" % h for h in GRID if h in ident] if POOL_I else [])
                    if rows.get((card, pat, "I", rg, ly)) is None:
                        lines.append("rule: cell %s REFUSED: I's own arm is missing from its pool (no row); the "
                                     "night is DEFECTIVE (filed)" % cid)
                        res["code"] = 2
                        return res
                    arms = pool + ["h%d" % h for h in heads if not sa[h][cid]]
                    why = []
                    for a in arms:
                        r = rows.get((card, pat, a, rg, ly))
                        w = "missing" if r is None else is_void((card, pat, a, rg, ly), r)
                        if w:
                            why.append("%s %s" % (a, w))
                    if why:
                        if att.get((card, pat, rg, ly), 1) < 2:
                            owed.setdefault("results.tsv", set()).add((card, pat, rg, ly))
                        else:
                            vc.append(cid)
                        continue
                    ccells.append(cid)
                    tI[cid] = statistics.median([v for a in pool for v in rows[(card, pat, a, rg, ly)]["launches"]])
                    pool_n[cid] = len(pool)
                    pool_arms[cid] = pool
                    pool_meds[cid] = [rows[(card, pat, a, rg, ly)]["med"] for a in pool]
                    cell_key[cid] = (card, pat, rg, ly)
                    for h in heads:
                        t[h][cid] = tI[cid] if sa[h][cid] else rows[(card, pat, "h%d" % h, rg, ly)]["med"]
    # C3 voids are never dropped: once, owed a re-run; twice, carried on the record below
    for n, (r3, a3) in sorted(c3files.items()):
        for k, r in r3.items():
            w = is_void(k, r)
            if w and w != "gatefail" and a3.get(cellk(k), 1) < 2 and r["method"] != "kit-approx":
                owed.setdefault(n, set()).add(cellk(k))
    if owed:
        for n, ks in sorted(owed.items()):
            lines.append("rule: %d cell(s) of %s void ONCE (%s%s): R1 waits for the re-run"
                         % (len(ks), n, ", ".join("/".join(c) for c in sorted(ks)[:6]),
                            ", ..." if len(ks) > 6 else ""))
        lines.append("rule: NEXT cards.py rerun RUNDIR")
        res["code"] = 3
        return res
    if not aa_logs:
        lines.append("rule: no A/A cell is read: the night is VOID")
        res["code"] = 2
        return res

    z_now = [0.0]

    def floors_over(cs):
        """The floors over the cells `cs` (N and the twin contrasts read from them): the (regime,
        layer) floors, and the PER-PATTERN twin terms (rev 10, RULED r38 J1)."""
        n_c = sum(1 for h in heads for c in cs if not sa[h][c])
        f_, fd_ = count_floor(aa_logs, n_c, alpha)
        logs, plogs = {}, {}
        for c in cs:
            lm = [math.log(m) for m in pool_meds[c]]
            logs.setdefault(tuple(c.split("/")[1:3]), []).append(lm)
            plogs.setdefault(c.split("/")[0], []).append(lm)
        tw = twin_sigmas(logs)
        ptw = twin_sigmas(plogs)
        z = z_upper(alpha / max(1, n_c))
        pterm = {p: twin_term(v, z) for p, v in ptw.items()}
        z_now[0] = z
        return f_, fd_, tw, pool_floors(f_, sig_raw, glob, n_all, n_c, alpha, twins=tw), ptw, pterm
    f, fd, tw, floors, ptw, pterm = floors_over(ccells)

    def base_floor(c):
        """The cell's floor without the layout term: max(its (regime, layer) floor, its pattern's twin term)."""
        p, rg, ly = c.split("/")
        fl = floors.get((rg, ly), f)
        return max(fl, pterm[p]) if PAT_TWIN and p in pterm else fl

    tv_cache = {}

    def tvar(c, h):
        """The layout variance in one median of the arm H(h) (None: I) in cell c (`text_var`; I's side,
        and a head whose text is I's, over I's pooled launches)."""
        card, pat, rg, ly = cell_key[c]
        if h is None or sa[h][c]:
            k = (("I", pat, ly), LAUNCHES * pool_n.get(c, 1))
        else:
            k = (("h%d" % h, pat, ly), None)
        if k not in tv_cache:
            tv_cache[k] = text_var(te, k[0], n=k[1])
        return tv_cache[k]

    def f_hI(c, h):
        """r44 B: the floor of the comparison H(h) vs I in cell c (wins, the confirm, W/E, R2, R4): max(the
        base floor, exp(z sqrt(V_I + V_h)) - 1) from the two texts' own pools; rev 12's cell max over
        every head when PER_HEAD_FLOOR is off (the control)."""
        if not PER_HEAD_FLOOR:
            return cell_floor(c)
        fl = base_floor(c)
        if not LAYOUT_TEXT_TERM or sa[h][c]:
            return fl
        return max(fl, math.exp(z_now[0] * math.sqrt(tvar(c, None) + tvar(c, h))) - 1)

    def f_pair(c, g, h):
        """r44 B: the floor of H(g) vs H(h) in cell c (dominance): max(the base floor, exp(z sqrt(V_g +
        V_h)) - 1); the cell max when PER_HEAD_FLOOR is off."""
        if not PER_HEAD_FLOOR:
            return cell_floor(c)
        fl = base_floor(c)
        if not LAYOUT_TEXT_TERM:
            return fl
        return max(fl, math.exp(z_now[0] * math.sqrt(tvar(c, g) + tvar(c, h))) - 1)

    def cell_floor(c):
        """THE CELL'S FLOOR (rev 10, RULED r38 J1): max(its (regime, layer) floor, its PATTERN's twin
        term). r44 B: read by the AGREEMENT GATE only (I's arms against each other, with rev 12's largest
        per-text term: a noisy head can only loosen the gate there) and printed; every head comparison
        takes `f_hI` / `f_pair`. The twin term is computed at the finest level the night times twins: per pattern,
        over that pattern's own hash-equal pools in the cells read (its 12 (regime, layer) cells:
        df 12 at a 2-arm pool, 36 at hex24's 4), because between-run noise acts per binary and a
        (regime, layer) term pooled over 9 patterns dilutes one pattern's noise (r38 J1: 0.40-0.69).
        A pattern with no estimate (df 0) has no term: its cells are VOID (the gate), never pooled up."""
        fl = base_floor(c)
        return max(fl, layout_text_term(c)) if LAYOUT_TEXT_TERM else fl

    def layout_text_term(c):
        """THE PER-TEXT LAYOUT TERM (rev 12, RULED R2 B): for each head compared with I in cell c, the
        log variance of t(I) / t(H(h)) from the two TEXTS' own layout pools (`text_var`: the median of
        5 draws plus the finite pool's mean offset, I's side over its pool's launches), the term
        exp(z(alpha / N) sqrt(V_I + V_h)) - 1; the cell takes the largest (one floor a cell). The
        floor's other estimators read only I's and aa's texts; a head text more layout-sensitive than
        I is read here."""
        best = 0.0
        for h in heads:
            if not sa[h][c]:
                best = max(best, math.exp(z_now[0] * math.sqrt(tvar(c, None) + tvar(c, h))) - 1)
        return best
    # THE AGREEMENT GATE (rev 9, RULED r37 H2): I's pool is one binary, so its arms' medians differ
    # only by noise. Where they disagree beyond the cell's own floor, one of them moved (a whole-arm
    # slowdown moves a 2-arm pool's median by ~half its size and no gap test sees it): the cell is
    # VOID, re-run once, never a pick. A pool of two cannot say which arm moved; it voids too.
    # Rev 10 (r38 J1): the cell's own floor includes its pattern's twin term, and a cell whose
    # pattern has no twin estimate is void here too (never pooled up to a coarser level).
    gated = []
    if AGREE_GATE:
        for c in list(ccells):
            ms = pool_meds[c]
            fl = cell_floor(c)
            noest = PAT_TWIN and c.split("/")[0] not in pterm
            if noest or (len(ms) >= 2 and max(ms) / min(ms) > 1 + fl):
                gated.append("%s (no twin estimate for its pattern)" % c if noest else
                             "%s (pool of %d: %.4f > 1 + %.4f)" % (c, len(ms), max(ms) / min(ms), fl))
                ccells.remove(c)
                del tI[c], pool_n[c]
                for h in heads:
                    t[h].pop(c, None)
                if att.get(cell_key[c], 1) < 2:
                    owed.setdefault("results.tsv", set()).add(cell_key[c])
                else:
                    vc.append(c)
    if gated:
        lines.append("rule: agreement gate: %d cell(s) whose hash-equal arms disagree beyond f: %s"
                     % (len(gated), "; ".join(gated[:6]) + ("; ..." if len(gated) > 6 else "")))
    res["gated"] = len(gated)
    if owed:
        lines.append("rule: %d cell(s) of results.tsv VOID ONCE by the agreement gate: R1 waits for the re-run"
                     % len(owed["results.tsv"]))
        lines.append("rule: NEXT cards.py rerun RUNDIR")
        res["code"] = 3
        return res
    if gated:      # void twice: the floors are re-read over the cells still read
        f, fd, tw, floors, ptw, pterm = floors_over(ccells)
    lines.append("rule: f(A/A) = %.4f (count-sized: A/A sigma %.4f, upper %.4f over %d cells; N = %d comparisons, "
                 "z = %.2f; the A/A max ratio alone %.4f)" % (f, fd["sigma"], fd["sigma_up"], len(aa_logs),
                                                               fd["N"], fd["z"], fd["f_aa"]))
    pf = lambda rg, ly: floors.get((rg, ly), f)      # noqa: E731
    lines.append("rule: twin contrasts per (regime, layer) (I's pools, rev 9, r37 H1): %s"
                 % ", ".join("%s/%s sigma %.4f df %d" % (rg, ly, tw[(rg, ly)][0], tw[(rg, ly)][1])
                             for rg in REGIMES if rg not in APPROX for ly in ("off", "on") if (rg, ly) in tw))
    lines.append("rule: f per (regime, layer) = max(f(A/A), the launch-sigma term, the twin term) (rev 9): %s"
                 % ", ".join("%s/%s %.4f" % (rg, ly, pf(rg, ly)) for rg in REGIMES if rg not in APPROX
                             for ly in ("off", "on")))
    lines.append("rule: twin term per pattern (its own hash-equal pools, rev 10, r38 J1)%s: %s"
                 % ("" if PAT_TWIN else " [OFF: control]",
                    ", ".join("%s sigma %.4f df %d term %.4f" % (p, ptw[p][0], ptw[p][1], pterm[p])
                              for p in sorted(ptw))))
    # THE NIGHT'S LAYOUT READING (rev 12, RULED r41 L9, R2 A/D): every launch ran a recorded pool
    # variant; per text the between-variant sigma (`text_effects`, launch noise removed) is the layout
    # share the draws average over. A share COMMON to every variant of a text is that text's own speed
    # (R2 A) and no estimator reads it. Printed with the per-text term and the night's power line.
    lsig = sorted(math.sqrt(v[1]) for v in te.values())
    msig = statistics.median(lsig) if lsig else 0.0
    lines.append("rule: layout pools (rev 12, r41 L9): %s" % (
        "%d texts with a variant record; between-variant (layout) sigma per text median %.4f, max %.4f; per-text "
        "layout term (R2 B)%s: largest %.4f" % (len(lsig), msig, lsig[-1], "" if LAYOUT_TEXT_TERM else " [OFF: control]",
                                                max((layout_text_term(c) for c in ccells), default=0.0))
        if lsig else "no row carries a variant record: not read"))
    lines.append("rule: layout pools hold FIXED (r44 F): the matcher's data tables (.rodata/.data/.bss), the "
                 "driver's main, the subject buffer (16 mod 64 in the whole-buffer and not-warm regimes); a share "
                 "common to every variant of a text includes THIS harness's data placement")
    # r44 A: the night's own variant x regime interaction reading, per text
    if inter:
        shs = sorted(v[0] for v in inter.values())
        fl_ = sorted(t for t, v in inter.items() if v[3])
        lines.append("rule: variant x regime interaction (r44 A): %d texts read; share median %.3f, max %.3f; flagged "
                     "(share > %.2f, an index that does not bind today, r45 FORMS8-3; and lack of fit beyond the "
                     "text's own launch noise at %.3f family-wise, launches winsorized at %.1f robust sigmas, F df "
                     "shrunk x%.2f for the night's pure-error kurtosis %.2f, r45 FORMS8-1) %d; ONE flagged text voids "
                     "the night's pick (r1 step 5)%s%s" % (
                         len(shs), statistics.median(shs), shs[-1], INTER_SHARE, INTER_ALPHA, INTER_CLIP,
                         iinfo.get("df_shrink", 1.0), iinfo.get("kurtosis", 0.0), len(fl_),
                         ": " + ", ".join("%s share %.3f ratio %.2f (line %.2f)" % ("/".join(t), inter[t][0], inter[t][1],
                                                                                  inter[t][2]) for t in fl_[:6]) if fl_ else "",
                         "" if INTERACTION_VOID else " [OFF: control, nothing voided]"))
    # r44 H: per text, the even (default-alignment) pair against the odd pair: the contrast of their effects
    hcon = sorted((abs((e.get(0, 0) + e.get(2, 0)) - (e.get(1, 0) + e.get(3, 0))) / 2, t) for t, (e, _s) in te.items())
    if hcon:
        lines.append("rule: even-pair vs odd-pair contrast per text (r44 H; the odd pair's relative layout is not the "
                     "one gcc -O2 ships): median %.4f, max %.4f (%s)" % (statistics.median([x for x, _t in hcon]),
                                                                       hcon[-1][0], "/".join(hcon[-1][1])))
    lines.append("rule: power at this night's layout sigma (rev 12, R2 D; r44 K): %s" % power_line(msig))
    fcell = {c: cell_floor(c) for c in ccells}
    res["fcell"], res["tI"], res["t"] = fcell, tI, t
    # CONFIRM BY RE-RUN (rev 10, RULED r38 R2; rev 11, RULED r39 K3, K4, K6; rev 12, r41 L9; r44 D).
    # Replication: a head's win beyond f in a cell COUNTS only if the cell's confirming re-run wins
    # again beyond the cell's floor. The confirm times I and each head owed in that cell into its
    # ROUND's file (`confirm_name`), every launch a fresh DRAW from the SAME 4-exe pools step 1 timed
    # (the cache returns the built exes). So the confirm is NOT an exe-level control (r44 D): the pool's
    # mean offset (`text_var`'s sL2 / POOL_SIZE term) replicates between the night and the confirm, and
    # the exe level rests on the per-text layout term in the floor; the confirm retires a launch-level
    # transient that does not recur (r38 R2). The confirm's reading of a head's win is ITS ROUND's I
    # median against its h<N> median (r44 D: a later round's I never replaces it): a missing, void or
    # bimodal I or h<N> there confirms nothing for that head; another head's arm says nothing about this
    # head's win (r39 K3). The confirm feeds ONE predicate, step (4)'s "beat I beyond f" (READING B, r39
    # K4); W, E and dominance read the first reading, never the confirm's. One confirm per (cell,
    # head) win: a head whose confirm row exists is never owed again, so the confirms end.
    wins = sorted((h, c) for h in heads for c in ccells if not sa[h][c] and tI[c] / t[h][c] > 1 + f_hI(c, h))
    # r44 H: each win re-read on the EVEN draws only (the default-alignment pair, the layout gcc ships): a
    # record beside the pick, never an input to it
    if wins:
        ev = []
        for h, c in wins:
            card, pat, rg, ly = cell_key[c]
            ie = [x for a in pool_arms[c] for x, v in zip(rows[(card, pat, a, rg, ly)]["launches"],
                                                          rows[(card, pat, a, rg, ly)].get("variants") or []) if v % 2 == 0]
            r_ = rows[(card, pat, "h%d" % h, rg, ly)]
            he = [x for x, v in zip(r_["launches"], r_.get("variants") or []) if v % 2 == 0]
            ev.append("H(%d) %s %.4f (even draws: %s)" % (h, c, tI[c] / t[h][c] - 1, "%.4f, I %d / H %d launches" % (
                statistics.median(ie) / statistics.median(he) - 1, len(ie), len(he)) if ie and he else "none"))
        lines.append("rule: wins beyond f re-read on even draws only (r44 H, a record): %s%s"
                     % ("; ".join(ev[:8]), "; ..." if len(ev) > 8 else ""))
    confs = [merge(*night["files"][n])[0] for n in sorted(night["files"], key=lambda n: confirm_round(n) or 0)
             if confirm_round(n) is not None]
    need = {}
    for h, c in wins if CONFIRM else []:
        card, pat, rg, ly = cell_key[c]
        if not any((card, pat, "h%d" % h, rg, ly) in cf for cf in confs):
            need.setdefault(cell_key[c], []).append(h)
    res["wins"] = len(wins)
    if need:
        res["owed_confirm"] = need
        ks = sorted(need)
        lines.append("rule: %d cell(s) hold a head's win beyond f (%d wins, %d owed): R1 waits for their confirming re-run "
                     "on fresh pool draws (%s%s)" % (len(need), len(wins), sum(len(v) for v in need.values()),
                                                       ", ".join("/".join(k) + " H(%s)" % ",".join(map(str, need[k]))
                                                                 for k in ks[:6]), ", ..." if len(ks) > 6 else ""))
        lines.append("rule: NEXT cards.py rerun RUNDIR")
        res["code"] = 3
        return res

    def confirmed(h, c):
        card, pat, rg, ly = cell_key[c]
        arms = ["I", "h%d" % h]
        own = [cf for cf in confs if (card, pat, arms[1], rg, ly) in cf]       # the head's own round (one)
        cf = own[0] if own else {}
        rs = [cf.get((card, pat, a, rg, ly)) for a in arms]
        if any(r is None or is_void((card, pat, a, rg, ly), r) for a, r in zip(arms, rs)):
            return False
        return rs[0]["med"] / rs[1]["med"] > 1 + f_hI(c, h)
    okwins = {(h, c) for h, c in wins if confirmed(h, c)} if CONFIRM else None
    res["confirmed"] = nok = len(okwins) if okwins is not None else 0
    if CONFIRM and not READING_B:       # the K4 control: rev 10's reading (an unreproduced win reads as a TIE)
        for h, c in wins:
            if (h, c) not in okwins:
                t[h][c] = tI[c]
        okwins = None
    if wins and CONFIRM:
        lines.append("rule: confirm by re-run on fresh pool draws (rev 12, r41 L9; r39 K4): %d of %d wins beyond f reproduced; "
                     "only those count as step (4)'s win; W, E and dominance read the first reading"
                     % (nok, len(wins)))
    lines.append("rule: I's pool per cell read (arms whose artifact is I's, measured): %s"
                 % ", ".join("%s %d" % kv for kv in sorted(pool_n.items())))
    lines.append("rule: R0 defective heads: %s; cells read %d, void %d" % (sorted(defective) or "none",
                                                                         len(ccells), len(vc)))
    measured = "MEASURED (kit-grid@7 cards C1 %s, C2 %s; %d cells read)" % (CARD_ROWS["C1"], CARD_ROWS["C2"],
                                                                           len(ccells))
    hs, label, rec, det = r1(heads, ccells, vc, t, tI, sa, fcell, measured=measured, wins_ok=okwins, fh=f_hI, fp=f_pair)
    res.update(hstar=hs, label=label, rec=rec, f=f, floors=floors, det=det)
    if hs is None:
        lines.append("rule: h* none: %s" % label)
        res["code"] = 2
        return res
    lines.append("rule: W = %s" % {h: round(w, 4) for h, w in det["W"].items()})
    lines.append("rule: E = %s; dominated-by counts %s; kept %s" % (det["E"], det["dominated_by"], det["kept"]))
    # R3: per class, the head its own cells pick, against the grid value nearest E[D]; DERIVED
    # when every class with a cell read tracks (rev 7, F10). Only a class whose text MOVES for
    # some surviving head is read (rev 8, r36 G6): a literal class (lit40, abc60) renders I at
    # every head, so its own pick is the top on any data and could never track
    track, any_cls = True, False
    for card in ("C1", "C2"):
        for pat in CARD_PATS[card]:
            mine = [c for c in ccells if c.startswith(pat + "/")]
            if not mine:
                continue
            if all(all(h in same_heads(same, pat, ly) for ly in LAYERS) for h in heads):
                lines.append("R3 class %s: its text is I's at every surviving head (never a mover): not read" % pat)
                continue
            any_cls = True
            hcls = r1(heads, mine, [], t, tI, sa, {c: fcell[c] for c in mine}, wins_ok=okwins, fh=f_hI, fp=f_pair)[0]
            ed = death_depth(pat)
            near = min(heads, key=lambda h: (abs(h - ed), -h))
            track &= hcls == near
            lines.append("R3 class %s: its own cells pick %d; E[D] %.2f (nearest head %d)%s"
                         % (pat, hcls, ed, near, "" if hcls == near else ": does not track"))
    if label.startswith("MEASURED") and any_cls and track:
        label = "DERIVED (R3: h* tracks E[D] in every class)" + label[len("MEASURED"):]
        res["label"] = label
    lines.append("rule: h* = %d, %s" % (hs, label))
    # R2 (C1-C2 half): every cell where I beats H(h*) beyond f (dial evidence; never changes h*)
    for c in ccells:
        if t[hs][c] / tI[c] > 1 + f_hI(c, hs):
            lines.append("R2 dial evidence: %s: H(%d) %.4f vs I %.4f" % (c, hs, t[hs][c], tI[c]))
    # R4: C1's near-miss column, H(h*) against C5 (the engine route)
    for pat in CARD_PATS["C1"]:
        for ly in ("off", "on"):
            cid = "%s/near-miss/%s" % (pat, ly)
            hv = t[hs].get(cid)
            ev = rows.get(("C5", pat, "engine", "near-miss", "off"))
            if hv is not None and ev and ev["status"] == "ok" and hv / ev["med"] > 1 + max(
                    f_hI(cid, hs), pf("near-miss", "off")):
                lines.append("R4 near-miss trigger (r45_reply §4): %s/%s H(%d) %.4f vs engine %.4f"
                             % (pat, ly, hs, hv, ev["med"]))
    # C3 at h* (step 2b, F4): R2's C3 half and R5; absent, NOT COMPUTED and owed
    name = "results_c3_h%d.tsv" % hs
    if name not in c3files:
        lines.append("rule: R2(C3)/R5 NOT COMPUTED at h* = %d" % hs)
        lines.append("rule: NEXT cards.py c3 RUNDIR %d" % hs)
        res["code"] = 3
        return res
    r3, a3 = c3files[name]
    harm = "h%d" % hs
    if any(rg in APPROX for rg in REGIMES):
        lines.append("R5 C3: regimes %s void by method (not checked)" % ", ".join(sorted(APPROX)))
    for pat in CARD_PATS["C3"]:
        for rg in REGIMES:
            for ly in ("off", "on"):
                cid = "%s/%s/%s" % (pat, rg, ly)
                got = {a: r3.get(("C3", pat, a, rg, ly)) for a in ("I", "h0", harm)}
                bad = [a for a, r in got.items() if r is None or is_void(("C3", pat, a, rg, ly), r)]
                if rg in APPROX:
                    continue
                if bad:
                    lines.append("R5 C3 %s: VOID twice (%s): R2/R5 not checked there (recorded)"
                                 % (cid, ", ".join(bad)))
                    continue
                v = got[harm]["med"]
                fr = pf(rg, ly)
                if got["I"]["med"] < v / (1 + fr):
                    lines.append("R2 dial evidence: C3 %s: H(%d) %.4f vs I %.4f" % (cid, hs, v, got["I"]["med"]))
                for other in ("I", "h0"):
                    if other != harm and v / got[other]["med"] > 1 + fr:
                        lines.append("R5 long-span loss: C3 %s H(%d) %.4f vs %s %.4f" % (cid, hs, v, other,
                                                                                        got[other]["med"]))
    lines.append("rule: NEXT the build compiles h* = %d in; then cards.py identity %d (FROZEN=<this night's "
                 "build>)" % (hs, hs))
    return res


def cmd_rule(args):
    """R0-R5 over a night's RUNDIR. --g2 FILE: R0's input, one defective head per line (a head
    whose answers G2 failed)."""
    (rundir,), opt = parse_args("rule", args, vflags=("--g2",))
    v = owed_now(rundir, opt.get("--g2"))
    print("rule: R0's G2 list %s (%s)" % (sorted(v["g2"]) or "none", v["g2_src"]))
    for ln in v["lines"]:
        print(ln)
    return v["code"]


@functools.lru_cache(maxsize=None)
def death_depth(pat):
    """E[D] = sum_i prod_{j<i} mass(S_j), the masses from the miss-heavy subject's byte rate."""
    b = subject(pat, "miss-heavy", 1 << 16, 1)
    cnt = [0] * 256
    for x in b:
        cnt[x] += 1
    mass = [sum(cnt[ord(ch)] for ch in set(s)) / len(b) for s in PATTERNS[pat][1]]
    e, p = 0.0, 1.0
    for ms in mass:
        e += p
        p *= ms
    return e


# ---- the drills (r45_reply rev 11 §3 "Drills"), each with the result the design states ------
def drill(spec):
    """spec: f, heads, cells [(id, k)], ratios {h: [per cell]} (t(I) = 1 unless tI given),
    void [ids]; the default ratio is 1.0 (a head that ties I)."""
    f = spec.get("f", 0.025)
    heads = spec.get("heads", GRID)
    cl = spec["cells"]
    tI = {c: spec.get("tI", {}).get(c, 1.0) for c, _k in cl}
    t = {h: {} for h in heads}
    for h in heads:
        r = spec["ratios"].get(h, spec.get("default", {}).get(h))
        for i, (c, k) in enumerate(cl):
            v = r[i] if isinstance(r, list) else (r if r is not None else 1.0)
            t[h][c] = v if h < k else tI[c]     # H(h) renders exactly I where h >= k
            if h >= k and isinstance(r, list) and r[i] != tI[c]:
                raise SystemExit("drill data: H(%d) differs from I in cell %s (k %d)" % (h, c, k))
    void = spec.get("void", [])
    read = [c for c, _k in cl if c not in void]
    same = {h: {c: h >= k for c, k in cl} for h in heads}
    return r1(heads, read, void, t, tI, same, f)


LOSE = 1.20
DRILLS = [
    ("(i) I and H equal at k <= 32", {"cells": [("c24", 24), ("c32", 32)], "ratios": {}},
     64, "on a measured tie of every finite head"),
    ("(ii) I faster in one cell (k 24)", {"cells": [("c24", 24), ("c32", 32)],
                                          "ratios": {h: [1.10, 1.0] for h in (0, 1, 2, 4, 8, 16)}},
     64, "on a measured tie of {24, 32, 64}"),
    ("(iii) L faster everywhere", {"cells": [("c24", 24), ("c60", 60)],
                                   "ratios": {0: [0.80, 0.80]}}, 0, "MEASURED"),
    ("(iv) all within noise", {"cells": [("c%d" % i, 60) for i in range(6)],
                               "ratios": {h: [1 + ((h * 7 + i * 13) % 19 - 9) / 1000 for i in range(6)]
                                          for h in GRID if h < 60}},
     64, "on a measured tie of every finite head"),
    ("(v) I faster in both k 60 cells", {"cells": [("a60", 60), ("b60", 60)],
                                         "ratios": {h: [1.08, 1.06] for h in GRID if h < 60}},
     64, "(64, CHOSEN): every shorter finite head measured slower beyond f"),
    ("(vi) near-equal chain", {"cells": [("c60", 60)],
                               "ratios": {0: [0.94], 1: [0.92], 2: [0.90], 4: [1.12], 8: [1.12],
                                          16: [1.12], 24: [1.12], 32: [1.12]}}, 2, "MEASURED"),
    ("(vii) a losing value outside E", {"f": 0.01, "heads": [0, 4, 8],
                                        "cells": [("c1", 60), ("c2", 60)], "tI": {"c1": 1.20, "c2": 1.20},
                                        "ratios": {0: [1.00, 1.10], 8: [1.08, 1.00], 4: [0.80, 2.00]}},
     8, "MEASURED"),
    ("(vii') without the losing value", {"f": 0.01, "heads": [0, 8],
                                         "cells": [("c1", 60), ("c2", 60)], "tI": {"c1": 1.20, "c2": 1.20},
                                         "ratios": {0: [1.00, 1.10], 8: [1.08, 1.00]}}, 8, "MEASURED"),
    ("(viii) H(64) fails G2 (R0) on (ii)'s data", {"heads": [0, 1, 2, 4, 8, 16, 24, 32],
                                                    "cells": [("c24", 24), ("c32", 32)],
                                                    "ratios": {h: [1.10, 1.0] for h in (0, 1, 2, 4, 8, 16)}},
     32, "h = 32, the largest R0-surviving head (CHOSEN; the grid top failed R0), on a measured tie of {24, 32}"),
    ("(viii) every finite head fails R0", {"heads": [], "cells": [("c24", 24)], "ratios": {}},
     None, "no form ships"),
    ("(ix) a dominance cycle", {"cells": [("c1", 60), ("c2", 60), ("c3", 60)],
                                "ratios": {0: [LOSE] * 3, 1: [LOSE] * 3, 2: [LOSE] * 3, 4: [LOSE] * 3,
                                           24: [LOSE] * 3, 8: [0.95, 1.02, 0.99], 16: [0.97, 0.99, 1.00],
                                           32: [0.99, 1.00, 0.97]}}, 32, "MEASURED"),
    ("R3-1: H(8) best in one cell, H(32) in another",
     {"cells": [("c24", 24), ("c60", 60), ("c3", 60)],
      "ratios": {0: [LOSE] * 3, 1: [LOSE] * 3, 2: [LOSE] * 3, 4: [LOSE] * 3,
                 8: [0.80, 0.95, 1.00], 32: [1.00, 0.85, 1.00]}}, 32, "MEASURED"),
    ("(x) one cell, no new minimum", {"cells": [("c", 60)],
                                      "ratios": {0: [LOSE], 1: [LOSE], 2: [LOSE], 4: [LOSE],
                                                 8: [0.97], 16: [0.975]}}, 16, "MEASURED"),
    ("(x) h = 4 at 0.95, the new minimum", {"cells": [("c", 60)],
                                            "ratios": {0: [LOSE], 1: [LOSE], 2: [LOSE], 4: [0.95],
                                                       8: [0.97], 16: [0.975]}}, 8, "MEASURED"),
    ("(x) h = 4 at 0.985, not the minimum", {"cells": [("c", 60)],
                                             "ratios": {0: [LOSE], 1: [LOSE], 2: [LOSE], 4: [0.985],
                                                        8: [0.97], 16: [0.975]}}, 16, "MEASURED"),
    ("(xi) two cells", {"heads": [0, 1, 2, 4, 8, 16, 24, 32, 64], "cells": [("c1", 60), ("c2", 60)],
                        "ratios": {0: [LOSE] * 2, 1: [LOSE] * 2, 2: [LOSE] * 2, 4: [LOSE] * 2,
                                   8: [0.97, 0.97], 16: [0.975, 0.975]}}, 16, "MEASURED"),
    ("(xi) h = 12 joins E and dominates 16", {"heads": [0, 1, 2, 4, 8, 12, 16, 24, 32, 64],
                                              "cells": [("c1", 60), ("c2", 60)],
                                              "ratios": {0: [LOSE] * 2, 1: [LOSE] * 2, 2: [LOSE] * 2,
                                                         4: [LOSE] * 2, 8: [0.97, 0.97],
                                                         12: [0.985, 0.95], 16: [0.975, 0.975]}},
     12, "MEASURED"),
    ("(G4) H(8) alone wins; 16, 24 within f of both", {"cells": [("c", 60)],
                                                        "ratios": {0: [LOSE], 1: [LOSE], 2: [LOSE], 4: [LOSE],
                                                                   8: [0.97], 16: [0.99], 24: [0.99]}},
     8, "MEASURED"),
    ("(xii) drill V read clean", {"f": 0.04, "cells": [("k36", 36), ("k40", 40), ("k49", 49), ("k24", 24)],
                                  "ratios": {0: [LOSE] * 3 + [1.0], 1: [LOSE] * 3 + [1.0], 2: [LOSE] * 3 + [1.0],
                                             4: [LOSE] * 3 + [1.0], 16: [LOSE] * 3 + [1.0],
                                             8: [0.90, 0.93, 0.95, 1.0], 24: [0.95, 0.90, 0.93, 1.0],
                                             32: [0.93, 0.95, 0.90, 1.0]}}, 32, "MEASURED"),
    ("(xii) drill V, k 24 void twice", {"f": 0.04, "cells": [("k36", 36), ("k40", 40), ("k49", 49), ("k24", 24)],
                                        "void": ["k24"],
                                        "ratios": {0: [LOSE] * 3 + [1.0], 1: [LOSE] * 3 + [1.0],
                                                   2: [LOSE] * 3 + [1.0], 4: [LOSE] * 3 + [1.0],
                                                   16: [LOSE] * 3 + [1.0], 8: [0.90, 0.93, 0.95, 1.0],
                                                   24: [0.95, 0.90, 0.93, 1.0], 32: [0.93, 0.95, 0.90, 1.0]}},
     64, "cell(s) k24 void twice; the cells read picked H(8)"),
    ("(xii) drill V, k 40 void twice", {"f": 0.04, "cells": [("k36", 36), ("k40", 40), ("k49", 49), ("k24", 24)],
                                        "void": ["k40"],
                                        "ratios": {0: [LOSE] * 3 + [1.0], 1: [LOSE] * 3 + [1.0],
                                                   2: [LOSE] * 3 + [1.0], 4: [LOSE] * 3 + [1.0],
                                                   16: [LOSE] * 3 + [1.0], 8: [0.90, 0.93, 0.95, 1.0],
                                                   24: [0.95, 0.90, 0.93, 1.0], 32: [0.93, 0.95, 0.90, 1.0]}},
     64, "cell(s) k40 void twice; the cells read picked H(32)"),
    ("(xii') k 24 void twice, H(64) failed R0", {"f": 0.04, "heads": [0, 1, 2, 4, 8, 16, 24, 32],
                                                 "cells": [("k36", 36), ("k40", 40), ("k49", 49), ("k24", 24)],
                                                 "void": ["k24"],
                                                 "ratios": {0: [LOSE] * 3 + [1.0], 1: [LOSE] * 3 + [1.0],
                                                            2: [LOSE] * 3 + [1.0], 4: [LOSE] * 3 + [1.0],
                                                            16: [LOSE] * 3 + [1.0], 8: [0.90, 0.93, 0.95, 1.0],
                                                            24: [0.95, 0.90, 0.93, 1.0],
                                                            32: [0.93, 0.95, 0.90, 1.0]}},
     32, "h = 32, the largest R0-surviving head"),
    ("(xiii) drill N, a NOT-WARM-only loss", {"f": 0.02, "cells": [("hd32", 32), ("nw32", 32)],
                                              "ratios": {8: [0.90, 1.20], 16: [0.99, 1.0], 24: [0.99, 1.0]}},
     64, "on a measured tie of {0, 1, 2, 4, 16, 24, 32, 64}"),
    ("(xiv) a regime's method missing", {"f": 0.02, "cells": [("hd32", 32), ("nw32", 32), ("nw24", 24)],
                                         "void": ["nw32", "nw24"],
                                         "ratios": {8: [0.90, 1.20, 1.0], 16: [0.99, 1.0, 1.0],
                                                    24: [0.99, 1.0, 1.0]}},
     64, "cell(s) nw24, nw32 void twice; the cells read picked H(8)"),
]


# ---- synthetic nights: the noise, unimodal and void/R0/re-run drills (rev 7, F2-F7) --------
def synth_body(key, same):
    """The TEXT an arm cell runs (rev 12, r41 L9), the unit a layout pool belongs to: I's text serves
    I and every head whose text is I's (one text, one pool); each other head its own; aa's serves
    the A/A pair (aa, aa.b). One text serves every regime of its (pattern, layer)."""
    card, pat, arm, _rg, ly = key
    if card == "AA":
        return ("aa", ly)
    h = arm_head(arm)
    if arm_base(arm) == "I" or (h is not None and h in same[pat][ly]):
        return ("I", pat, ly)
    return (arm_base(arm), pat, ly)


def synth_layout_effect(lay, body, v, rg=None):
    """The layout effect (a factor) of pool variant v of `body` under the drill's model `lay` (rev 12,
    RULED r41 L9 drill rows): {"tau", "model", "rho", "store"}. model "phase": a FIXED function of
    (body, the variant's 64-B phase) (the pool's variant v sits at phase class (r + v) mod 4, r drawn
    per body), exp(N(0, tau)) drawn once per (body, phase) a night; "heads": the same, on head
    texts only (I's and aa's pools carry none); "rho": CORRELATED offsets inside a pool, z_v = rho
    z_body + sqrt(1 - rho^2) e_v (a share rho^2 of the layout variance common to every variant of the
    body, which no draw averages). r44 A: "regime": a VARIANT x REGIME effect, exp(N(0, tau)) drawn per
    (body, regime `rg`, variant), nothing common to a variant across regimes (the shape the per-text fit
    cannot hold; `heads`: on head texts only). r44 B: "loser": layout exp(N(0, tau)) per (body, variant)
    on the texts of the arms `arms` only (a never-picked noisy head), every other text none. r45 FORMS8-3
    (the critic's models, keyed UNLIKE the fit): "onereg": exp(N(0, tau)) per (body, variant) on head
    texts in the ONE regime `rg` only (the per-text fit half-absorbs it); "mix": the "phase" model on head
    texts times a per-(body, regime, variant) interaction exp(N(0, ti))."""
    st, tau = lay["store"], lay["tau"]
    if lay["model"] == "heads" and body[0] in ("I", "aa"):
        return 1.0
    rng = st["_rng"]
    if lay["model"] == "regime":
        if lay.get("heads") and body[0] in ("I", "aa"):
            return 1.0
        if (body, rg, v) not in st:
            st[(body, rg, v)] = math.exp(rng.gauss(0, tau))
        return st[(body, rg, v)]
    if lay["model"] == "onereg":
        if body[0] in ("I", "aa") or rg != lay["rg"]:
            return 1.0
        if (body, v) not in st:
            st[(body, v)] = math.exp(rng.gauss(0, tau))
        return st[(body, v)]
    if lay["model"] == "mix":
        if body[0] in ("I", "aa"):
            return 1.0
        if (body, "r") not in st:
            st[(body, "r")] = rng.randrange(4)
        ph = (st[(body, "r")] + v) % 4
        if (body, "ph", ph) not in st:
            st[(body, "ph", ph)] = math.exp(rng.gauss(0, tau))
        if (body, rg, v) not in st:
            st[(body, rg, v)] = math.exp(rng.gauss(0, lay["ti"]))
        return st[(body, "ph", ph)] * st[(body, rg, v)]
    if lay["model"] == "loser":
        if body[0] not in lay["arms"]:
            return 1.0
        if (body, v) not in st:
            st[(body, v)] = math.exp(rng.gauss(0, tau))
        return st[(body, v)]
    if lay["model"] == "rho":
        if (body, "z") not in st:
            st[(body, "z")] = rng.gauss(0, 1)
        if (body, v) not in st:
            r = lay["rho"]
            st[(body, v)] = math.exp(tau * (r * st[(body, "z")] + math.sqrt(1 - r * r) * rng.gauss(0, 1)))
        return st[(body, v)]
    if (body, "r") not in st:
        st[(body, "r")] = rng.randrange(4)
    ph = (st[(body, "r")] + v) % 4
    if (body, "ph", ph) not in st:
        st[(body, "ph", ph)] = math.exp(rng.gauss(0, tau))
    return st[(body, "ph", ph)]


def synth_rows(rng, sigma, wins=None, noise="normal", bimodal_cells=(), approx_read=True, regimes=None,
               rscale=None, aascale=1.0, splits=None, cellwins=None, armoff=None, timefx=None,
               order="interleaved", pos0=0, layout=None, only=None, tscale=None):
    """A synthetic step-1 results set: C1-C2 every arm, A/A (aa, aa.b) every regime and layer; each
    arm cell's
    LAUNCHES launches are T x exp(noise) with T the cell's true time (one per pattern/regime/
    layer, every arm equal: pure noise) times the arm's `wins` factor where its text is not I's.
    Regimes are all READ (`approx_read`: the bench's methods present), so the rule's floor and
    dominance see the real cell count (108 C1-C2 cells x 9 heads). HETEROGENEOUS noise (rev 8,
    r36 G2): `rscale` {regime: x} multiplies a regime's launch sigma, `aascale` the A/A arms'.
    `splits` {(card, pat, arm, regime, layer): (n, factor)}: n of the arm's launches x factor (a
    median-moving split when n >= 3, r36 G3). `cellwins` {(card, pat, arm, regime, layer): factor}:
    one arm's true time in one cell (r36 G4; a layout twin of the arm shares it: one text).
    `armoff` (tau, regimes, spare_aa): BETWEEN-RUN
    noise (rev 9, r37 H1): every arm of those regimes (None: every regime) carries its own offset
    exp(N(0, tau)), held over all its launches; the A/A arms are spared when spare_aa. A re-run
    draws fresh offsets (a new run). Its draws come after the arm's launches, so a night without
    `armoff` draws exactly rev 8's stream. `armoff` (tau, sel): the offset on every arm cell
    `sel(key)` names (rev 10's CLASS DRILL, r38: noise confined to one night, regime, layer,
    pattern or arm; a layout twin is selected as its base arm). TIME (rev 10, r38 J2): `timefx(pos)`
    multiplies every launch by a function
    of its position in the night's launch order (`launch_order` over step 1's cells, the order
    `time_cells` times; `order` "arm-major" is rev 9's, the control), `pos0` the first position
    (a re-run runs after the night). It draws nothing, so the streams are unchanged.
    LAYOUT noise (rev 12, RULED r41 L9): `layout` {"tau", "model", "rho", "store"}: every launch draws
    a variant of its text's pool (`synth_body`), uniformly from POOL_SIZE with the store's own RNG
    ("_rng", so a night without `layout` draws exactly rev 11's stream), and is multiplied by that
    variant's effect (`synth_layout_effect`, held over the night: the first reading, every re-run
    and the confirm draw from the same pools); the draws are recorded in the row's `variants`.
    `only` {(card, pat, regime, layer): [arms]}: generate those arm cells only (the confirm's, from
    `confirm_cells`), else step 1's. `tscale(key)` (r45 FORMS8-1): a factor on one arm cell's launch
    sigma (heterogeneous noise per TEXT: one pattern's head arms noisier); it draws nothing."""
    wins = wins or {}
    rscale = rscale or {}
    splits = splits or {}
    cellwins = cellwins or {}
    rows = {}
    slots = launch_slots(order) if timefx else None
    same = {}
    for card in ("C1", "C2"):
        for pat in CARD_PATS[card]:
            k = len(PATTERNS[pat][1])
            lit = pat in ("lit40", "abc60")
            same[pat] = {ly: [h for h in GRID if lit or h >= k] for ly in LAYERS}

    def eps():
        if noise == "t5":
            return rng.gauss(0, 1) / math.sqrt(rng.gammavariate(2.5, 2.0) / 5) / math.sqrt(5 / 3)
        return rng.gauss(0, 1)

    def put(key, T):
        base = (key[0], key[1], arm_base(key[2])) + key[3:5]
        sg = sigma * rscale.get(key[3], 1.0) * (aascale if key[0] == "AA" else 1.0)
        if tscale is not None:
            sg *= tscale(key)
        T *= cellwins.get(base, 1.0)
        if key[:5] in bimodal_cells or (key[1], key[3], key[4]) in bimodal_cells:
            ls = [T * math.exp(sg * eps()) * (1.08 if i < 2 else 1.0) for i in range(LAUNCHES)]
        elif key[:5] in splits:
            n, fac = splits[key[:5]]
            ls = [T * math.exp(sg * eps()) * (fac if i < n else 1.0) for i in range(LAUNCHES)]
        else:
            ls = [T * math.exp(sg * eps()) for _ in range(LAUNCHES)]
        if armoff and (armoff[1](base) if callable(armoff[1]) else
                       (armoff[1] is None or key[3] in armoff[1]) and not (armoff[2] and key[0] == "AA")):
            o = math.exp(rng.gauss(0, armoff[0]))
            ls = [v * o for v in ls]
        drawn = []
        if layout:
            body = synth_body(key, same)
            drawn = [layout["store"]["_rng"].randrange(POOL_SIZE) for _ in ls]
            ls = [x * synth_layout_effect(layout, body, v, key[3]) for x, v in zip(ls, drawn)]
        if timefx:
            ls = [v * timefx(pos0 + q) for v, q in zip(ls, slots.get(key[:5]) or slots[base])]
        rows[key] = {"status": "ok", "med": statistics.median(ls), "launches": ls,
                     "method": "kit" if approx_read else method_of(key[3]), "note": "", "variants": drawn}
    for card in ("C1", "C2"):
        for pat in CARD_PATS[card]:
            for rg in (regimes or REGIMES):
                for ly in ("off", "on"):
                    T = rng.uniform(0.2, 2.0)
                    arms = (["I"] + ["h%d" % h for h in GRID] if only is None else
                            only.get((card, pat, rg, ly), []))
                    for a in arms:
                        h = arm_head(a)
                        put((card, pat, a, rg, ly), T * (1.0 if h is None or h in same[pat]["off"] else wins.get(h, 1.0)))
    for rg in (regimes or REGIMES) if only is None else ():
        for ly in ("off", "on"):
            T = rng.uniform(0.2, 2.0)
            put(("AA", "lit16", "aa", rg, ly), T)
            put(("AA", "lit16", "aa.b", rg, ly), T)
    return rows, same


@functools.lru_cache(maxsize=None)
def launch_slots(order="interleaved"):
    """{arm cell: [the night position of each of its launches]} over step 1's cells (C5's launches
    take their places in the order too), and the night's launch count under key None."""
    lo = launch_order(cells(cards=STEP1), interleave=order == "interleaved")
    out = {}
    for q, (c, _i) in enumerate(lo):
        out.setdefault(c, []).append(q)
    out[None] = len(lo)
    return out


def synth_night(rng, sigma, **kw):
    """One whole synthetic night through `analyse`: step 1, then the re-run of any cell void once
    (fresh launches), so the drill exercises the merge too."""
    global APPROX
    keep = APPROX
    APPROX = {}                   # every regime read: the bench's methods present
    if kw.get("layout") is not None:        # one store a night (the pools' effects), its own RNG
        kw = dict(kw, layout=dict(kw["layout"], store={"_rng": random.Random(rng.random())}))
    try:
        rows, same = synth_rows(rng, sigma, **kw)
        night = {"files": {"results.tsv": (rows, {})}, "same": same}
        v = analyse(night, set())
        voided_first = sum(len(s) for s in v["owed_rerun"].values())
        # the re-run rounds: a transient does not recur; the re-run runs AFTER the night (a time
        # effect holds its end value there). A cell the gate voids only once the cells first owed
        # are read owes a further round (r38 J4 (1)); every cell is re-run at most once
        kw2 = dict(kw, bimodal_cells=(), splits={},
                   pos0=launch_slots(kw.get("order", "interleaved"))[None] if kw.get("timefx") else 0)
        redo, rounds = {}, 0
        while v["owed_rerun"].get("results.tsv") and rounds < 3:
            rounds += 1
            fresh, _s = synth_rows(rng, sigma, **kw2)
            redo.update({k: r for k, r in fresh.items() if (k[0], k[1], k[3], k[4]) in v["owed_rerun"]["results.tsv"]})
            night["files"]["results.tsv"] = (rows, redo)
            v = analyse(night, set())
        v["voided_first"] = voided_first
        v["rerun_rounds"] = rounds
        # the confirming re-run (rev 10, r38 R2; rev 12, r41 L9): fresh launches after the night, I and each
        # owed head on fresh draws of the SAME pools, the arm list from `confirm_cells` (r41 L5: one source);
        # a confirm owed only after an earlier confirm (R0 from it moved N) is one more round, each (cell, head) once
        conf, ncells, crounds = {}, 0, 0
        while v["owed_confirm"] and crounds < 3:
            crounds += 1
            ncells += len(v["owed_confirm"])
            fresh, _s = synth_rows(rng, sigma, only=confirm_only(v["owed_confirm"]), **kw2)
            night["files"][confirm_name(crounds)] = (fresh, {})        # each round its own file (r44 D)
            v = analyse(night, set())
        v["voided_first"], v["rerun_rounds"], v["confirm_cells"] = voided_first, rounds, ncells
        return v
    finally:
        APPROX = keep


NOISE_TRIALS = 300


def noise_drill(trials=NOISE_TRIALS, sigma=0.01, noise="normal", seed=1, **kw):
    """P(h* != 64), the nights with a first void, the median f(A/A); NOISE_LAST keeps the median
    floor of (hit-dense, off), the cell floor the H2 drill sizes its shifts by."""
    rng = random.Random(seed)
    off, voids, fs, fc, cc, lx, ni = 0, 0, [], [], [], [], 0
    for _ in range(trials):
        v = synth_night(rng, sigma, noise=noise, **kw)
        ni += v.get("inter_flagged", 0) > 0
        off += v["hstar"] != GRID_TOP
        voids += v["voided_first"] > 0
        fs.append(v.get("f", 0))
        cc.append(v.get("confirm_cells", 0))
        if v.get("floors"):
            fc.append(v["floors"].get(("hit-dense", "off"), 0))
    NOISE_LAST["fcell"] = statistics.median(fc) if fc else 0.0
    NOISE_LAST["confirm"] = cc
    NOISE_LAST["inter"] = ni
    return off / trials, voids, statistics.median(fs)


NOISE_LAST = {}


# ---- THE CLASS DRILL (rev 10, RULED r38): noise at EVERY level of the night's structure -------
# Three rounds running (r36 G2, r37 H1, r38 J1/J2) the rule's defect was a noise shape one level
# below the drills: an estimator pooled coarser than the noise it must read, or a noise that
# followed the launch ORDER. So the drill family varies noise at each level the floor pools over
# (night, regime, layer, pattern, arm) and a STEP and a DRIFT in box speed inside a block of each
# level of the night's launch order (the night; one pattern's block; one layer of it; one cell =
# one regime there; the cell's middle round, where a step splits the arms). The blocks sit in
# hex24 (the largest twin pool, r38 J2's shape) and the middle round also in hex64 (a 2-arm pool).
CLASS_TAUS = (0.01, 0.02, 0.03)
CLASS_SIZES = (0.02, 0.05, 0.10)


def _c12(k):
    return k[0] in ("C1", "C2")


CLASS_NOISE = [
    # (level, what, armoff selector): the offset exp(N(0, tau)) per arm cell it names
    ("night", "every arm, A/A too", lambda k: True),
    ("regime", "one regime (random), A/A spared", lambda k: _c12(k) and k[3] == "random"),
    ("layer", "one layer (on), A/A spared", lambda k: _c12(k) and k[4] == "on"),
    ("pattern", "hex24 (pool 4)", lambda k: k[1] == "hex24"),
    ("pattern", "hex32 (pool 3)", lambda k: k[1] == "hex32"),
    ("pattern", "hex64 (pool 2)", lambda k: k[1] == "hex64"),
    ("arm", "I, every cell", lambda k: _c12(k) and k[2] == "I"),
] + [("arm", "H(%d), every cell" % h, (lambda k, a="h%d" % h: _c12(k) and k[2] == a)) for h in GRID]


@functools.lru_cache(maxsize=None)
def night_blocks():
    """The launch-order blocks the class drill places a step or a drift in: {name: (first, end)}
    positions in the interleaved night (`launch_order` over step 1's cells); each block is
    asserted CONTIGUOUS, so the drill's block is the night's."""
    lo = launch_order(cells(cards=STEP1))
    sel = {
        "night": lambda c, r: True,
        "pattern block (hex24)": lambda c, r: c[:2] == ("C1", "hex24"),
        "layer block (hex24/off)": lambda c, r: c[:2] == ("C1", "hex24") and c[4] == "off",
        "regime cell (hex24/near-miss/off)": lambda c, r: c[:2] == ("C1", "hex24") and c[3:] == ("near-miss", "off"),
        "middle round (hex24/near-miss/off)": lambda c, r: (c[:2] == ("C1", "hex24") and c[3:] == ("near-miss", "off")
                                                            and r == LAUNCHES // 2),
        "middle round (hex64/near-miss/off)": lambda c, r: (c[:2] == ("C2", "hex64") and c[3:] == ("near-miss", "off")
                                                            and r == LAUNCHES // 2),
    }
    out = {}
    for name, f in sel.items():
        qs = [q for q, (c, r) in enumerate(lo) if f(c, r)]
        assert qs and qs[-1] - qs[0] + 1 == len(qs), "block %s is not contiguous" % name
        out[name] = (qs[0], qs[-1] + 1)
    return out


def time_drill(kind, block, size, seed, trials=NOISE_TRIALS, sigma=0.01, **kw):
    """P(h* != 64) and the nights with a first void, on 1 % nights with a box-speed STEP (x(1 +
    size) from a cut drawn uniformly inside the block, every night its own cut, held to the end)
    or a linear DRIFT (0 at the block's start to `size` at its end, held after) in launch order."""
    a, b = night_blocks()[block] if block in night_blocks() else block
    rng, rc = random.Random(seed), random.Random(seed + 7919)
    off = voids = 0
    for _ in range(trials):
        if kind == "step":
            cut = rc.randrange(a + 1, b) if b - a > 1 else a
            fx = lambda q, cut=cut: 1 + size if q >= cut else 1.0       # noqa: E731
        else:
            fx = lambda q: 1 + size * min(1.0, max(0.0, (q - a) / (b - a)))      # noqa: E731
        v = synth_night(rng, sigma, timefx=fx, **kw)
        off += v["hstar"] != GRID_TOP
        voids += v["voided_first"] > 0
    return off / trials, voids


def power_cells(head, regime, win):
    """`cellwins` for a true win of H(head) in ONE regime: every C1-C2 cell of that regime where the
    head's text is not I's (both layers)."""
    out = {}
    for card in ("C1", "C2"):
        for p in CARD_PATS[card]:
            if p in ("lit40", "abc60") or head >= len(PATTERNS[p][1]):
                continue
            for ly in LAYERS:
                out[(card, p, "h%d" % head, regime, ly)] = win
    return out


def power_rate(head=8, regime="hit-dense", win=0.95, trials=NOISE_TRIALS, seed=700, with_confirms=False, **kw):
    rng = random.Random(seed)
    vs = [synth_night(rng, 0.01, cellwins=power_cells(head, regime, win), **kw) for _ in range(trials)]
    picks = [v["hstar"] for v in vs]
    if with_confirms:
        return sum(x == head for x in picks), picks, [v.get("confirm_cells", 0) for v in vs]
    return sum(x == head for x in picks), picks


def inter_rate(seed, win=0.95, trials=NOISE_TRIALS, **kw):
    """r45 FORMS8-1/-3: over `trials` nights, (nights where H(8)'s one `win` in hit-dense is picked, nights
    with a text flagged by the interaction test, nights with h* != 64); win None: no win."""
    rng = random.Random(seed)
    hit = fl = off = 0
    for _ in range(trials):
        v = synth_night(rng, 0.01, cellwins=power_cells(8, "hit-dense", win) if win else None, **kw)
        hit += v["hstar"] == 8
        fl += v.get("inter_flagged", 0) > 0
        off += v["hstar"] != GRID_TOP
    return hit, fl, off


def _flags(**kw):
    """Set the rule's control switches; returns the previous values (restore with _flags(**old))."""
    old = {k: globals()[k] for k in kw}
    globals().update(kw)
    return old


def confirm_only(owed):
    """synth_rows' `only` for the confirm, built from `confirm_cells` (the command's own arm list, r41 L5)."""
    only = {}
    for c in confirm_cells(owed):
        only.setdefault((c[0], c[1], c[3], c[4]), []).append(c[2])
    return only


def _confirm_rows(rng, owed, **kw):
    return synth_rows(rng, 0.01, only=confirm_only(owed), **kw)[0]


def gapk_rate(tau, texts=10000, sigma=0.01, seed=1, pool=POOL_SIZE, aware=True, rows_per_text=6):
    """GAP_K's FALSE-SPLIT rate under LAYOUT bimodality (rev 12, RULED r41 L9; R2 C re-derived): `texts`
    synthetic texts, each a pool of `pool` variants with effects exp(N(0, tau)) (the "phase" model) and
    `rows_per_text` arm rows (a head text's regimes) of LAUNCHES launches, each launch a uniform draw,
    on top of launch noise sigma. aware (R2 C): the test reads each row with its text's per-variant
    effect removed (`text_effects` fitted over the text's rows, as `analyse` does) against the sigma of
    those adjusted launches; else (rev 12 before R2) the raw launches against the raw sigma. Returns
    (rate per arm row, the sigma read)."""
    rng = random.Random(seed)
    rows = {}
    for t in range(texts):
        eff = [rng.gauss(0, tau) for _ in range(pool)]
        for j in range(rows_per_text):
            vs = [rng.randrange(pool) for _ in range(LAUNCHES)]
            rows[(t, j)] = {"status": "ok", "variants": vs,
                            "launches": [math.exp(eff[v] + sigma * rng.gauss(0, 1)) for v in vs]}
    if aware:
        te = text_effects(rows, lambda k: k[0])
        old = _flags(VARIANT_BIMODAL=True)
        try:
            ls = {k: adjusted(r, te, k[0]) for k, r in rows.items()}
        finally:
            _flags(**old)
    else:
        ls = {k: r["launches"] for k, r in rows.items()}
    sds = [statistics.stdev([math.log(x) for x in v]) for v in ls.values()]
    sig = statistics.median(sds) / MED_SD5
    return sum(bimodal(v, sig) for v in ls.values()) / len(ls), sig


def selftest_rev12(check):
    """The rev 12 rows (RULED r41 L9, R2): the layout POOLS under every layout model the ruling names (a
    fixed function of (text, 64-B phase); heads-only; rho 0.8 / 0.95 correlated variants) at tau
    1/2/3 %, with the per-TEXT layout term (R2 B) and the variant-aware bimodal test (R2 C), each with
    its control; GAP_K's false-split rate re-derived under the new test; the power rows at tau 0
    (gated) and 1/2 % (RECORD, R2 D); the pool refusal per half; L6."""
    # accept per (model, tau): (P(h* != 64) gated?, void-night line or None for RECORD) -- R2's terms:
    # rho rows RECORD (A: a share common to every variant IS the text's speed); heads-only tau 3 % RECORD
    # (B); voids <= 0.05 at tau 1 % (F3), <= 0.10 at tau 2 % (C), RECORD at 3 %
    models = (("phase", "a fixed function of (text, 64-B phase)", {}),
              ("heads", "heads only (I's and aa's pools carry none)", {}),
              ("rho", "rho 0.8 correlated variants", {"rho": 0.8}),
              ("rho", "rho 0.95 correlated variants", {"rho": 0.95}))
    void_acc = {0.01: 0.05, 0.02: 0.10, 0.03: None}
    for i, (model, what, extra) in enumerate(models):
        for j, tau in enumerate(CLASS_TAUS):
            ph, nvh, _fm = noise_drill(seed=3300 + 10 * i + j, layout=dict(extra, model=model, tau=tau))
            cc = NOISE_LAST["confirm"]
            name = "(r41 L9) layout: %s, tau %d %%" % (what, round(100 * tau))
            line = ("P(h* != 64) = %.3f over %d nights%s; nights with a first void %d (%.3f); confirm cells a night "
                    "mean %.2f, max %d; nights with an interaction void (r44 A) %d" % (
                        ph, NOISE_TRIALS, "" if model == "rho" or (model == "heads" and tau > 0.025)
                        else " (accept <= 0.05)", nvh, nvh / NOISE_TRIALS, statistics.mean(cc), max(cc), NOISE_LAST["inter"]))
            if model == "rho" or (model == "heads" and tau > 0.025):
                print("REC  %-48s %s (RECORD, R2 %s)" % (name, line, "A" if model == "rho" else "B"))
            else:
                check(name, ph <= 0.05, line)
            vname = "(r41 L9) layout void rate: %s, tau %d %%" % (model + ("" if model != "rho" else " %.2f" % extra["rho"]),
                                                                   round(100 * tau))
            acc = void_acc[tau]
            if acc is None or model == "rho":
                print("REC  %-48s nights with a first void %.3f (RECORD)" % (vname, nvh / NOISE_TRIALS))
            else:
                check(vname, nvh / NOISE_TRIALS <= acc, "nights with a first void %.3f (the variant-aware bimodal test "
                      "and the gate under layout: accept <= %.2f)" % (nvh / NOISE_TRIALS, acc))
    # the CONTROLS, one per new mechanism (r41 L4's lesson): the per-text term off on the heads-only 2 % night;
    # the variant-aware test off on the phase 2 % night
    # (gated at tau 3 %, where the defect is plain; tau 2 % printed beside it: the term's row there
    # reads 0.000, the control's share is the term's whole effect)
    old = _flags(LAYOUT_TEXT_TERM=False)
    try:
        pb2, _nv, _f = noise_drill(seed=3311, layout=dict(model="heads", tau=0.02))
        pb, nvb, _f = noise_drill(seed=3312, layout=dict(model="heads", tau=0.03))
    finally:
        _flags(**old)
    print("REC  %-48s P(h* != 64) = %.3f over %d nights (with the term: the row above)"
          % ("(R2 B) control: heads-only tau 2 %, no term", pb2, NOISE_TRIALS))
    check("(R2 B) control: heads-only tau 3 %, no per-text term", pb > 0.15,
          "P(h* != 64) = %.3f over %d nights (the drill sees the defect: accept > 0.15); voids %d" % (pb, NOISE_TRIALS, nvb))
    old = _flags(VARIANT_BIMODAL=False)
    try:
        _pc, nvc, _f = noise_drill(seed=3301, layout=dict(model="phase", tau=0.02))
    finally:
        _flags(**old)
    check("(R2 C) control: phase tau 2 %, the raw bimodal test", nvc / NOISE_TRIALS > 0.10,
          "nights with a first void %.3f (the drill sees the defect: accept > 0.10)" % (nvc / NOISE_TRIALS))
    # r44 A: the VARIANT x REGIME interaction model (a drill keyed unlike the fit: its effects vary per regime,
    # nothing common to a variant), heads only at tau 2 and 3 % GATED, every text at 2 % RECORD; the control
    # (INTERACTION_VOID off: rev 12's rule) on heads only at 3 %, where r44 V1 read 0.193
    for k, (tau, heads, gated) in enumerate(((0.02, True, True), (0.03, True, True), (0.02, False, False))):
        ph, nvh, _f = noise_drill(seed=3330 + k, layout=dict(model="regime", tau=tau, heads=heads))
        name = "(r44 A) layout: variant x regime, %s, tau %d %%" % ("heads only" if heads else "every text", round(100 * tau))
        line = ("P(h* != 64) = %.3f over %d nights%s; nights with an interaction void %d; nights with a first void %.3f "
                "(RECORD: the variant-aware bimodal test cannot hold this shape; a per-(text, regime) fit is PLANned)"
                % (ph, NOISE_TRIALS, " (accept <= 0.05)" if gated else "", NOISE_LAST["inter"], nvh / NOISE_TRIALS))
        if gated:
            check(name, ph <= 0.05, line)
        else:
            print("REC  %-48s %s (RECORD)" % (name, line))
    old = _flags(INTERACTION_VOID=False)
    try:
        pa_, _nv, _f = noise_drill(seed=3331, layout=dict(model="regime", tau=0.03, heads=True))
    finally:
        _flags(**old)
    check("(r44 A) control: variant x regime heads tau 3 %, no void", pa_ > 0.10,
          "P(h* != 64) = %.3f over %d nights (the drill sees the defect: accept > 0.10)" % (pa_, NOISE_TRIALS))
    # r45 FORMS8-1 (c): HETEROGENEOUS launch noise WITH a layout ("phase" tau 1 %) and one true 5 % H(8) win in
    # hit-dense, no interaction anywhere: (i) t(5) launches, (ii) one pattern's head arms at 2x sigma. GATED:
    # nights flagged <= 0.05 AND the win's power with the void >= 0.9 x without it (the void off, same seed);
    # the CONTROL (INTER_PE_PER_TEXT off: r44's pure error pooled per regime, chi-square) flags > 0.05 (r45
    # read 55 and 100 of 100)
    hexp = CARD_PATS["C1"][0]
    ph1 = dict(model="phase", tau=0.01)
    for k, (what, kw) in enumerate((
            ("t(5) launches", dict(noise="t5")),
            ("one pattern's (%s) head arms at 2x sigma" % hexp,
             dict(tscale=lambda key: 2.0 if key[1] == hexp and key[2] != "I" else 1.0)))):
        hon, fon, _o = inter_rate(3460 + k, layout=ph1, **kw)
        old = _flags(INTERACTION_VOID=False)
        try:
            hoff, _f, _o = inter_rate(3460 + k, layout=ph1, **kw)
        finally:
            _flags(**old)
        check("(r45 FORMS8-1) no interaction, %s" % what, fon / NOISE_TRIALS <= 0.05 and hon >= 0.9 * hoff,
              "nights flagged %d of %d (accept <= 0.05); h* = 8 in %d with the void, %d without (accept >= 0.9 x)"
              % (fon, NOISE_TRIALS, hon, hoff))
        old = _flags(INTER_PE_PER_TEXT=False)
        try:
            _h, fc_, _o = inter_rate(3460 + k, layout=ph1, **kw)
        finally:
            _flags(**old)
        check("(r45 FORMS8-1) control: %s, r44's pooled pure error" % what, fc_ / NOISE_TRIALS > 0.05,
              "nights flagged %d of %d (the drill sees the defect: accept > 0.05)" % (fc_, NOISE_TRIALS))
    # r45 FORMS8-3 RECORD: a SMALL interaction (0.5 %, half the launch sigma; the critic's "mix" model, keyed
    # unlike the fit: heads' "phase" main effect tau x a per-(text, regime, variant) interaction ti), one 5 % H(8)
    # win: the flagged-night rate and the power, void on vs off
    for k, (tau, ti) in enumerate(((0.01, 0.005), (0.0, 0.005))):
        lay = dict(model="mix", tau=tau, ti=ti)
        hon, fon, _o = inter_rate(3470 + k, layout=lay)
        old = _flags(INTERACTION_VOID=False)
        try:
            hoff, foff, _o = inter_rate(3470 + k, layout=lay)
        finally:
            _flags(**old)
        print("REC  %-48s nights flagged %d of %d; h* = 8 in %d with the void, %d without (RECORD, r45 FORMS8-3)"
              % ("(r45 FORMS8-3) interaction %g %% x main %g %%" % (100 * ti, 100 * tau), fon, NOISE_TRIALS, hon, hoff))
    # r45 FORMS8-4 RECORD: the interaction rows keyed unlike the fit, under the new line WITH the per-head floor
    # (both on, the night's rule), no win: P(h* != 64) and the flagged nights, void on vs off
    for k, lay in enumerate((dict(model="onereg", tau=0.03, rg="hit-dense"), dict(model="onereg", tau=0.05, rg="hit-dense"),
                             dict(model="mix", tau=0.03, ti=0.015))):
        _h, fon, oon = inter_rate(3480 + k, win=None, layout=lay)
        old = _flags(INTERACTION_VOID=False)
        try:
            _h, _f, ooff = inter_rate(3480 + k, win=None, layout=lay)
        finally:
            _flags(**old)
        print("REC  %-48s P(h* != 64) = %.3f with the void (nights flagged %d), %.3f without, of %d (RECORD, r45 "
              "FORMS8-4)" % ("(r45 FORMS8-4) %s" % ", ".join("%s %s" % kv for kv in sorted(lay.items())),
                             oon / NOISE_TRIALS, fon, ooff / NOISE_TRIALS, NOISE_TRIALS))
    # r45 FORMS8-2: a POOL_SIZE other than 4 is refused at start (at 8 every pool repeats a layout: r44 C refuses
    # every pool), 4 runs; and the command line refuses it before any command (exit 2)
    ps = {n: pool_size_refusal(n) for n in (2, 3, 4, 8)}
    cp = subprocess.run([sys.executable, "-I", os.path.abspath(__file__), "plan"], capture_output=True, text=True,
                        env=dict(os.environ, POOL_SIZE="8"), timeout=120)
    check("(r45 FORMS8-2) POOL_SIZE other than 4 refused at start", ps[4] is None and all(ps[n] for n in (2, 3, 8))
          and cp.returncode == 2 and "POOL_SIZE=8" in cp.stderr,
          "refused: %s; `POOL_SIZE=8 cards.py plan` exit %d, %s" % (
              ", ".join(str(n) for n in (2, 3, 4, 8) if ps[n]), cp.returncode, cp.stderr.strip()[:90]))
    # r44 B: a NEVER-PICKED NOISY LOSER (H(1) 20 % slower everywhere, layout tau 4 % on its texts only) beside
    # one 5 % winner H(8) in hit-dense; GATED at rev 11's line; the control (PER_HEAD_FLOOR off: rev 12's
    # one cell max) at the same nights (r44 V2 read 151 of 300)
    lose = dict(model="loser", tau=0.04, arms={"h1"})
    nl, _p = power_rate(win=0.95, seed=3440, layout=lose, wins={1: 1.20})
    check("(r44 B) power: one 5 % winner beside a noisy loser", nl >= POWER_ACCEPT[0],
          "h* = 8 in %d of %d nights (rev 11's accept >= %d; H(1) 20 %% slower, layout tau 4 %% on its texts only)"
          % (nl, NOISE_TRIALS, POWER_ACCEPT[0]))
    old = _flags(PER_HEAD_FLOOR=False)
    try:
        nlc, _p = power_rate(win=0.95, seed=3440, layout=lose, wins={1: 1.20})
    finally:
        _flags(**old)
    check("(r44 B) control: the same nights, one floor a cell", nlc < POWER_ACCEPT[0],
          "h* = 8 in %d of %d nights (the drill sees the defect: accept < %d)" % (nlc, NOISE_TRIALS, POWER_ACCEPT[0]))
    # GAP_K re-derived under the variant-aware test (R2 C; GAP_K stays 4.5)
    for tau in (0.0,) + CLASS_TAUS:
        rate, sg = gapk_rate(tau, seed=3390 + round(1000 * tau))
        raw, sgr = gapk_rate(tau, texts=4000, seed=3395 + round(1000 * tau), aware=False)
        print("REC  %-48s per-arm false-split rate %.2e variant-aware (sigma read %.4f), %.2e raw (sigma %.4f); "
              "~1200 arms a night -> %.3f / %.3f expected false voids a night" % (
                  "(R2 C) GAP_K %.1f under layout tau %d %%" % (GAP_K, round(100 * tau)), rate, sg, raw, sgr,
                  1200 * rate, 1200 * raw))
    # the POWER rows (r41 L3; R2 D): one winner 5 % / 10 % (H(8), hit-dense) and the multi-winner row; gated at
    # layout tau 0 (rev 11's accept lines), RECORD at 1 and 2 % (POWER_RECORD pins them for `rule`'s power line)
    multi = {}
    for h in (0, 1, 2, 4, 8, 16):
        multi.update(power_cells(h, "hit-dense", 0.95))
    for k, tau in enumerate((0.0, 0.01, 0.02)):
        lay = dict(model="phase", tau=tau) if tau else None
        n5, _p = power_rate(win=0.95, seed=3400 + k, layout=lay)
        n10, _p = power_rate(win=0.90, seed=3410 + k, layout=lay)
        rng = random.Random(3420 + k)
        nm = sum(synth_night(rng, 0.01, cellwins=multi, layout=lay)["hstar"] == 16 for _ in range(NOISE_TRIALS))
        got = (n5, n10, nm)
        pin = POWER_RECORD.get(tau)
        for (nmx, acc), n in zip((("one winner 5 %% (H(8))", POWER_ACCEPT[0]), ("one winner 10 %% (H(8))", POWER_ACCEPT[1]),
                                  ("every head <= 16 5 %% faster", POWER_ACCEPT[2])), got):
            name = "(r41 L3) power: %s, layout tau %d %%" % (nmx % (), round(100 * tau))
            line = "h* = %s in %d of %d nights (rev 11's accept >= %d)" % ("16" if "16" in nmx else "8", n, NOISE_TRIALS, acc)
            if tau == 0.0:
                check(name, n >= acc, line)
            else:
                print("REC  %-48s %s (RECORD, R2 D)" % (name, line))
        if tau:
            check("(R2 D, r44 L) POWER_RECORD pin, tau %d %%" % round(100 * tau), got == pin,
                  "the drill reads %s, POWER_RECORD pins %s (re-pin in the change that moves them)" % (got, pin))
    # the POOL REFUSAL, one row per half (r41 L4's lesson; r44 C adds the 32-B half and the distinct-layout
    # count): a moving pool passes; each plant fires its own clause and no other (the duplicate's plant fires
    # the 32-B clause too, by construction: a duplicated layout shares its relative layout and 32-B phases)
    A, B, C, D = (8,), (12,), (9,), (13,)
    ok_l = {0: ((0,), (0,), A), 1: ((20,), (20,), B), 2: ((16,), (16,), A), 3: ((36,), (4,), B)}
    one_ph = {0: ((16,), (16,), A), 1: ((16,), (16,), B), 2: ((16,), (16,), C), 3: ((16,), (16,), D)}
    one_rel = {0: ((0,), (0,), A), 1: ((16,), (16,), A), 2: ((36,), (4,), A), 3: ((52,), (20,), A)}
    one_32 = {0: ((0,), (0,), A), 1: ((20,), (20,), B), 2: ((32,), (0,), A), 3: ((36,), (4,), B)}
    dup = {0: ((0,), (0,), A), 1: ((20,), (20,), B), 2: ((0,), (0,), A), 3: ((36,), (4,), B)}
    T64, TREL, T32, TDIS = "one 64-B phase each", "shares one relative layout", "share the 32-B phases", "distinct built layouts"
    rr = {n: pool_refusal(x) or "" for n, x in (("ok", ok_l), ("one_ph", one_ph), ("one_rel", one_rel),
                                                ("one_32", one_32), ("dup", dup))}
    fires = {n: tuple(t for t in (T64, TREL, T32, TDIS) if t in r) for n, r in rr.items()}
    halves = (fires["ok"] == () and fires["one_ph"] == (T64,) and fires["one_rel"] == (TREL,)
              and fires["one_32"] == (T32,) and fires["dup"] == (T32, TDIS))
    spans = all(len({(pre // 16) % 4 for _v, pre, _f in pool_variants("t%d" % i)}) == min(4, POOL_SIZE)
                and len({tuple(f) for _v, _p, f in pool_variants("t%d" % i)}) == min(2, POOL_SIZE)
                and all(0 <= pre < 16 * PRELUDE_STEPS and pre % 16 == 0 for _v, pre, _f in pool_variants("t%d" % i))
                for i in range(2000))
    check("(r41 L9, r44 C) the pool refusal, each half", halves and spans,
          "clauses fired: moving %s; one 64-B phase %s; one relative layout %s; a 32-B-sharing pair %s; a duplicate %s; "
          "pool_variants over 2000 texts spans the 16-B phase classes and the alignments: %s" % (
              fires["ok"], fires["one_ph"], fires["one_rel"], fires["one_32"], fires["dup"], spans))
    # r44 C: the CONSTRUCTION's 32-B half: each alignment's two variants (v, v + 2) take preludes 16 B apart
    # mod 32, for every text drawn (fails on rev 11's PHASE_ORDER (0, 1, 2, 3), whose pairs sit 32 B apart)
    bad32 = sum(1 for i in range(2000) for (v, pre, _f) in pool_variants("t%d" % i)
                if v + 2 < POOL_SIZE and (pre - pool_variants("t%d" % i)[v + 2][1]) % 32 != 16)
    check("(r44 C) each alignment pair's preludes differ by 16 B mod 32", bad32 == 0,
          "pairs (v, v + 2) over 2000 texts NOT 16 B apart mod 32: %d (accept 0; PHASE_ORDER %s)" % (bad32, PHASE_ORDER))
    # r44 K: the power line BRACKETS a sigma between two pinned rows (never the nearest row across a cliff) and
    # reads the sigma corrected for its bias: a read of 0.88 x 1.5 % lies between the 1 % and 2 % rows
    pl15 = power_line(SIGMA_READ_BIAS * 0.015)
    pl05 = power_line(SIGMA_READ_BIAS * 0.005)
    check("(r44 K) the power line brackets the night's sigma", "tau 1 %" in pl15 and "tau 2 %" in pl15
          and "tau 0 %" in pl05 and "tau 1 %" in pl05,
          "at a read of %.4f: %s | at %.4f: %s" % (SIGMA_READ_BIAS * 0.015, pl15[:230], SIGMA_READ_BIAS * 0.005, pl05[:120]))
    # r44 D: each confirm ROUND its own file: its launch draws differ from every other round's (the salt), and a
    # head's confirm reads the I row of its OWN round (a later round's I never replaces it)
    cl_ = ("C1", "hex24", "I", "hit-dense", "off")
    seqs = [[launch_variant("rid0|%s" % confirm_name(k), cl_, r) for r in range(LAUNCHES)] for k in (1, 2)]
    old = _flags(APPROX={})
    try:
        rng = random.Random(1630)
        cw = power_cells(8, "hit-dense", 0.90)
        rows, same = synth_rows(rng, 0.01, cellwins=cw)
        night = {"files": {"results.tsv": (rows, {})}, "same": same}
        v0 = analyse(night, set())
        owed = v0["owed_confirm"]
        r1rows = _confirm_rows(rng, owed, cellwins=cw)                 # round 1: I and H(8), H(8) wins again
        r2rows = {}
        for (card, pat, rg, ly) in owed:                                 # round 2: I only, 15 % FASTER (a later round
            k = (card, pat, "I", rg, ly)                                 # owed for another head re-times I there)
            r2rows[k] = dict(r1rows[k], launches=[x * 0.85 for x in r1rows[k]["launches"]], med=r1rows[k]["med"] * 0.85)
        night["files"][confirm_name(1)] = (r1rows, {})
        night["files"][confirm_name(2)] = (r2rows, {})
        vd = analyse(night, set())
    finally:
        _flags(**old)
    check("(r44 D) the confirm's rounds: own draws, own I row", seqs[0] != seqs[1] and vd["hstar"] == 8,
          "round 1 / 2 draws of one cell %s / %s; H(8)'s round-1 confirm against round 1's I with a 15 %% faster I in "
          "round 2: h* %s (accept 8; %d cells owed)" % (seqs[0], seqs[1], vd["hstar"], len(owed)))
    # L6 (r41): unknown or mistyped arguments refuse (exit 2); the G2 record is keyed by run id and sha
    import contextlib
    import io
    import pwd
    import tempfile

    def refuses(f, *a):
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                f(*a)
        except SystemExit as e:
            return e.code == 2
        return False
    pa = [refuses(parse_args, "rule", ["R", "--g2=F", "--gg2", "x"], (), ("--g2",)),
          refuses(parse_args, "rule", ["R", "--g2"], (), ("--g2",)),
          refuses(parse_args, "rule", ["R", "--g2="], (), ("--g2",)),
          refuses(parse_args, "rule", ["R", "S"], (), ("--g2",)),
          refuses(parse_args, "dry", ["R", "--quik"], ("--quick",)),
          refuses(parse_args, "rule", [], (), ("--g2",))]
    good = (parse_args("rule", ["R", "--g2=F"], (), ("--g2",)) == (["R"], {"--g2": "F"})
            and parse_args("rule", ["--g2", "F", "R"], (), ("--g2",)) == (["R"], {"--g2": "F"}))
    troot = os.environ.get("PCREC_TMPDIR") or "/var/tmp/pcrec-%s" % pwd.getpwuid(os.getuid()).pw_name
    os.makedirs(troot, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=troot) as td:
        rid = run_id(td, create=True)
        g = os.path.join(td, "g2.txt")
        open(g, "w").write("16\n")
        first = night_g2(td, g)[0] == {16} and night_g2(td)[0] == {16}
        open(g, "w").write("16\n8\n")
        moved = refuses(night_g2, td)                       # the recorded file's bytes moved
        other = os.path.join(td, "g2b.txt")
        open(other, "w").write("32\n")
        open(g, "w").write("16\n")
        differs = refuses(night_g2, td, other)              # a second, different list for the night
        other_dir = os.path.join(td, "other")             # another night's RUNDIR: its record copied in
        os.makedirs(other_dir)
        rid2 = run_id(other_dir, create=True)
        with open(os.path.join(other_dir, G2_RECORD), "w") as f:
            f.write(open(os.path.join(td, G2_RECORD)).read())
        stale = refuses(night_g2, other_dir) and rid2 != rid
    check("(r41 L6) strict arguments and the keyed G2 record", all(pa) and good and first and moved and differs and stale,
          "refused (unknown, valueless x2, extra positional, mistyped flag, none): %s; --g2=F and --g2 F accepted: %s; "
          "recorded and re-read %s; moved file refused %s; a second list refused %s; another run's record refused %s"
          % (pa, good, first, moved, differs, stale))
    # r44 E: a RUNDIR re-used after its results files are removed: `run` mints a fresh run id and refuses the
    # earlier night's G2 record; a record written before the FIRST `run` (job 701's order) is kept
    saved = {n: globals()[n] for n in ("check_deny", "identical_to_I", "time_cells")}
    globals().update(check_deny=lambda *a, **k: ([], 0, 0), identical_to_I=lambda *a, **k: {},
                     time_cells=lambda *a, **k: None)
    try:
        with tempfile.TemporaryDirectory(dir=troot) as td:
            g = os.path.join(td, "g2.txt")
            open(g, "w").write("16\n")
            rid0 = run_id(td, create=True)
            night_g2(td, g)                                          # 701: the record before `run`
            with contextlib.redirect_stdout(io.StringIO()):
                cmd_run([td])
            kept = run_id(td) == rid0 and night_g2(td)[0] == {16}
            for n in os.listdir(td):
                if n.startswith("results") and n.endswith(".tsv"):
                    os.remove(os.path.join(td, n))
            with contextlib.redirect_stdout(io.StringIO()):
                again = refuses(cmd_run, [td])                       # the earlier night's record: refused
            fresh = run_id(td) != rid0
            os.remove(os.path.join(td, G2_RECORD))
            with contextlib.redirect_stdout(io.StringIO()):
                cmd_run([td])
            rid2 = run_id(td)
            seq = [launch_variant("%s|results.tsv" % r_, ("C1", "hex24", "h8", "hit-dense", "off"), k)
                   for r_ in (rid0, rid2) for k in range(LAUNCHES)]
    finally:
        globals().update(saved)
    check("(r44 E) a re-used RUNDIR: a fresh run id, the old G2 record refused", kept and again and fresh
          and seq[:LAUNCHES] != seq[LAUNCHES:],
          "701's pre-run record kept: %s; the re-used RUNDIR's second `run` refused the old record: %s; a fresh id: %s; "
          "draws %s / %s" % (kept, again, fresh, seq[:LAUNCHES], seq[LAUNCHES:]))
    # r44 I: the exe cache name carries the compiler (CC and its --version)
    real_cc = cc_ident
    try:
        ks = []
        for ident in ("gcc\ngcc (GCC) 15.2.0", "gcc\ngcc (GCC) 14.1.0"):
            globals()["cc_ident"] = lambda cc, ident=ident: ident
            ks.append(variant_key("t0", 16, ["-fno-align-loops"], CC))
    finally:
        globals()["cc_ident"] = real_cc
    check("(r44 I) the exe cache key carries the compiler", ks[0] != ks[1], "two compilers' keys %s / %s" % tuple(ks))


K6_FIXED_WIN = None     # r44 J's fail-before: a fixed win for every K6 night (rev 12's 0.953 / 0.955), not placed


def selftest_rev11(check):
    """The rev 11 rows (RULED r39): K2's R0 over the confirm, K3's per-arm confirm, K4's reading B
    and its power rows, K6's one owed list (K1's layout twins: replaced by rev 12's pools)."""
    # ---- K4: READING B; the multi-winner power row and the one-winner 4 % row (RECORD) ------------
    multi = {}
    for h in (0, 1, 2, 4, 8, 16):
        multi.update(power_cells(h, "hit-dense", 0.95))
    rng = random.Random(1620)
    pm = [synth_night(rng, 0.01, cellwins=multi)["hstar"] for _ in range(NOISE_TRIALS)]
    old = _flags(READING_B=False)
    try:
        rng = random.Random(1620)
        pma = [synth_night(rng, 0.01, cellwins=multi)["hstar"] for _ in range(NOISE_TRIALS)]
    finally:
        _flags(**old)
    check("(r39 K4) power: every head <= 16 5 % faster (hit-dense)", sum(x == 16 for x in pm) >= 0.85 * NOISE_TRIALS,
          "h* = 16 (the largest equal head) in %d of %d nights (accept >= 85 %%); picks %s"
          % (sum(x == 16 for x in pm), NOISE_TRIALS, dict(sorted((x, pm.count(x)) for x in set(pm)))))
    check("(r39 K4) control: the same nights, rev 10's reading", sum(x == 16 for x in pma) < 0.85 * NOISE_TRIALS,
          "h* = 16 in %d of %d nights (the drill sees the defect: accept < 85 %%; r39 measured 122-131)"
          % (sum(x == 16 for x in pma), NOISE_TRIALS))
    n4, _p4 = power_rate(win=0.96, seed=1621)
    print("REC  %-48s h* = 8 in %d of %d nights (RECORD, not gated: a one-winner 4 %% win, H(8) in hit-dense; "
          "r39 measured 182 under rev 10)" % ("(r39 K4) power: a 4 % win of H(8), one regime", n4, NOISE_TRIALS))

    # ---- K2 and K3: the confirm's own reading, through R0 and per arm ----------------------------
    def win_night(seed, edit):
        """A night with a real 10 % win of H(8) in hit-dense, its confirm rows `edit`ed, analysed."""
        rng = random.Random(seed)
        old = _flags(APPROX={})
        try:
            cw = power_cells(8, "hit-dense", 0.90)
            rows, same = synth_rows(rng, 0.01, cellwins=cw)
            night = {"files": {"results.tsv": (rows, {})}, "same": same}
            v = analyse(night, set())
            owed = v["owed_confirm"]
            conf = _confirm_rows(rng, owed, cellwins=cw)
            edit(conf, owed)
            night["files"]["results_confirm.tsv"] = (conf, {})
            return v, analyse(night, set())
        finally:
            _flags(**old)

    def gatefail(arm):
        def ed(conf, owed):
            card, pat, rg, ly = sorted(owed)[0]
            conf[(card, pat, arm, rg, ly)] = {"status": "gatefail", "med": None, "launches": [], "method": "kit",
                                              "note": "GATE FAIL"}
        return ed
    v0, v = win_night(1630, lambda conf, owed: None)
    _v0, vh = win_night(1630, gatefail("h8"))
    _v0, vi = win_night(1630, gatefail("I"))
    check("(r39 K2) a gate failure in the CONFIRM reaches R0", v["hstar"] == 8
          and vh["hstar"] != 8 and any("H(8) failed its gate" in l and "results_confirm.tsv" in l for l in vh["lines"])
          and vi["code"] == 2 and vi["hstar"] is None and any("I failed its gate" in l and "results_confirm.tsv" in l for l in vi["lines"]),
          "clean: h* %s (%d cells owed); H(8)'s confirm row gatefail: h* %s, R0 line %s; I's: code %d, h* %s"
          % (v["hstar"], len(v0["owed_confirm"]), vh["hstar"],
             any("H(8) failed its gate" in l for l in vh["lines"]), vi["code"], vi["hstar"]))

    def void_arm(arm):
        def ed(conf, owed):
            for card, pat, rg, ly in owed:
                conf[(card, pat, arm, rg, ly)] = {"status": "void", "med": None, "launches": [], "method": "kit",
                                                  "note": "void"}
        return ed
    _v0, vo = win_night(1631, void_arm("h0"))
    _v0, vI = win_night(1631, void_arm("I"))
    check("(r39 K3) the confirm reads I's twin and the head's own", vo["hstar"] == 8 and vI["hstar"] == GRID_TOP,
          "another head's confirm arm void in every owed cell: h* %s (accept 8); I void there: h* %s (accept 64, "
          "nothing confirms)" % (vo["hstar"], vI["hstar"]))

    # ---- K6: `rule --g2` and `rerun` owe ONE list; a G2-defective head never stalls the night -----
    import pwd
    import tempfile
    troot = os.environ.get("PCREC_TMPDIR") or "/var/tmp/pcrec-%s" % pwd.getpwuid(os.getuid()).pw_name
    os.makedirs(troot, exist_ok=True)

    def k6_place(seed):
        """r44 J: the K6 win placed BY CONSTRUCTION inside the night's own band. The night's rows without
        the win (the same RNG stream: `cellwins` draws nothing) are read twice, with G2 = {16} and without;
        the first C1-C2 hit-dense cell where H(8)'s text is not I's gets the factor that puts its ratio
        t(I) / t(H(8)) at the MIDPOINT of (f with G2, f without G2) (the floor reads no H(8) time, so the
        placement is exact). UNMEASURED DEFAULT: the midpoint (a margin of half the band each side).
        Returns (cellwins, the band) or None when the first reading owes a re-run (no floor to place on)."""
        old = _flags(APPROX={})
        try:
            rows, same = synth_rows(random.Random(seed), 0.01)
            night = {"files": {"results.tsv": (rows, {})}, "same": same}
            a, b = analyse(night, {16}), analyse(night, set())
        finally:
            _flags(**old)
        if "fcell" not in a or "fcell" not in b:
            return None
        cs = sorted(c for c in a["fcell"] if c.split("/")[1] == "hit-dense" and c in b["fcell"] and c in a["t"][8]
                    and a["t"][8][c] != a["tI"][c])
        if not cs:
            return None
        c = cs[0]
        lo, hi = a["fcell"][c], b["fcell"][c]
        if not hi > lo:
            return None
        pat, rg, ly = c.split("/")
        card = "C1" if pat in CARD_PATS["C1"] else "C2"
        fac = (a["tI"][c] / a["t"][8][c]) / (1 + (lo + hi) / 2)
        return {(card, pat, "h8", rg, ly): fac}, (lo, hi)

    def k6_night(seed, keep_record=True, cw=None):
        """One night through the COMMANDS (files on disk): `rule --g2` (G2 = {16}) then `rerun` without
        --g2, as the night's jobs call them, until the rule stops owing a rerun. Returns (stalled,
        rerun timed exactly the rule's owed list every pass, passes). `cw`: the win (r44 J: `k6_place`'s,
        inside the night's own band; rev 12's fixed 0.953 was seed-tuned, its control non-monotone in the
        win: 4 / 0 / 0 / 2 of 12 at 0.953 / 0.954 / 0.955 / 0.958, r44 V10)."""
        import contextlib
        import io
        rng = random.Random(seed)
        cw = cw if cw is not None else power_cells(8, "hit-dense", 0.953)
        old = _flags(APPROX={})
        real_tc = time_cells
        same_lists = True
        try:
            with tempfile.TemporaryDirectory(dir=troot) as td:
                rows, same = synth_rows(rng, 0.01, cellwins=cw)
                json.dump(same, open(os.path.join(td, "same_as_I.json"), "w"))
                with open(os.path.join(td, "results.tsv"), "w") as f:
                    f.write(HEADER)
                    for k, r in rows.items():
                        f.write(row_line(k, "ok", r["launches"]))
                g2f = os.path.join(td, "g2.txt")
                open(g2f, "w").write("16\n")
                timed = []

                def fake_tc(rundir, cl, path, with_approx=True):
                    timed.append(sorted(cl))
                    only = {}
                    for c in cl:
                        only.setdefault((c[0], c[1], c[3], c[4]), []).append(c[2])
                    fresh = synth_rows(rng, 0.01, cellwins=cw, only=only)[0]
                    new = not os.path.exists(path)
                    with open(path, "a") as f:
                        if new:
                            f.write(HEADER)
                        for c in cl:
                            f.write(row_line(c, "ok", fresh[c]["launches"]))
                globals()["time_cells"] = fake_tc
                for i in range(6):
                    with contextlib.redirect_stdout(io.StringIO()) as out:
                        code = cmd_rule([td, "--g2", g2f])
                    if not (code == 3 and "rule: NEXT cards.py rerun RUNDIR" in out.getvalue()):
                        return False, same_lists, i
                    vr = owed_now(td, g2f)          # what `rule --g2` owes
                    want = sorted(confirm_cells(vr["owed_confirm"])) if vr["owed_confirm"] else None
                    if not keep_record:             # the control: rev 10's `rerun` read no G2 list
                        os.remove(os.path.join(td, G2_RECORD))
                    timed.clear()
                    with contextlib.redirect_stdout(io.StringIO()):
                        cmd_rerun([td])
                    if want is not None and timed != [want]:
                        same_lists = False
                return True, same_lists, 6
        finally:
            globals()["time_cells"] = real_tc
            _flags(**old)
    # r44 J: the win placed in each night's own band (`k6_place`); the control is gated on a stall RATE over
    # the placed nights. UNMEASURED DEFAULT: K6_NIGHTS 16 seeds, at least 12 placed, the control stalling on at
    # least 80 % of the placed nights.
    K6_NIGHTS = 16
    placed = [(1640 + i, k6_place(1640 + i) if K6_FIXED_WIN is None else
               (power_cells(8, "hit-dense", K6_FIXED_WIN), (0.0, 0.0))) for i in range(K6_NIGHTS)]
    placed = [(sd, pl) for sd, pl in placed if pl is not None]
    res = [k6_night(sd, cw=pl[0]) for sd, pl in placed]
    ctl = [k6_night(sd, keep_record=False, cw=pl[0]) for sd, pl in placed]
    nst = sum(1 for s, _l, _n in ctl if s)
    check("(r39 K6, r44 J) `rule --g2` and `rerun` owe one list (G2 = {16})", len(placed) >= 12 and not any(s for s, _l, _n in res)
          and all(l for _s, l, _n in res) and nst >= 0.8 * len(placed),
          "%d of %d nights placed in their own band (bands %s); through the commands: stalled %d, rerun timed the rule's "
          "owed list on every pass: %s, passes %s; control (no G2 record, rev 10's rerun): stalled %d of %d (accept >= 80 %%)"
          % (len(placed), K6_NIGHTS, ", ".join("%.4f-%.4f" % pl[1] for _sd, pl in placed[:4]) + ", ...",
             sum(1 for s, _l, _n in res if s), all(l for _s, l, _n in res), [n for _s, _l, n in res], nst, len(placed)))


def cmd_selftest(args):
    parse_args("selftest", args, nflags=("--rev11", "--rev12"), npos=0)
    if "--rev12" in args and "--rev11" not in args:       # rev 12's rows alone (a development aid)
        bad, n = [0], [0]

        def check(name, ok, line):
            bad[0] += not ok
            n[0] += 1
            print("%s %-48s %s" % ("ok  " if ok else "FAIL", name, line), flush=True)
        selftest_rev12(check)
        print("selftest --rev12: %d checks, %d failed" % (n[0], bad[0]))
        return 1 if bad[0] else 0
    if "--rev11" in args:       # the rev 11 rows alone (a development aid; the night runs the whole selftest)
        bad, n = [0], [0]

        def check(name, ok, line):
            bad[0] += not ok
            n[0] += 1
            print("%s %-48s %s" % ("ok  " if ok else "FAIL", name, line))
        selftest_rev11(check)
        if "--rev12" in args:
            selftest_rev12(check)
        print("selftest --rev11: %d checks, %d failed" % (n[0], bad[0]))
        return 1 if bad[0] else 0
    bad = 0
    for name, spec, want_h, want_label in DRILLS:
        h, label, rec, det = drill(spec)
        ok = h == want_h and want_label in label
        bad += not ok
        print("%s %-48s h* = %-4s %s" % ("ok  " if ok else "FAIL", name, h, label))
        if not ok:
            print("     want h* = %s, a label holding %r; detail %s" % (want_h, want_label, det))

    nchk = len(DRILLS)

    def check(name, ok, line):
        nonlocal bad, nchk
        bad += not ok
        nchk += 1
        print("%s %-48s %s" % ("ok  " if ok else "FAIL", name, line))

    # F2: THE NOISE DRILL at the real cell count (108 C1-C2 cells x 9 heads), >= 300 trials
    p, nv, fmed = noise_drill()
    check("(F2) noise drill, normal launches sigma 1 %", p <= 0.05,
          "P(h* != 64) = %.3f over %d trials (accept <= 0.05); median f %.4f; nights with a first void %d"
          % (p, NOISE_TRIALS, fmed, nv))
    p5, nv5, fmed5 = noise_drill(noise="t5", seed=2)
    check("(F2) noise drill, t(5) launches sigma 1 %", p5 <= 0.05,
          "P(h* != 64) = %.3f over %d trials (accept <= 0.05); median f %.4f; nights with a first void %d"
          % (p5, NOISE_TRIALS, fmed5, nv5))
    # G2 (rev 8, r36): the same acceptance under HETEROGENEOUS noise: one regime 2x or 3x the
    # others, the A/A cells 0.7x the arms, and every regime at its own scale
    for i, (nm, kw) in enumerate((
            ("one regime 2x (random)", {"rscale": {"random": 2.0}}),
            ("one regime 3x (not-warm)", {"rscale": {"not-warm": 3.0}}),
            ("A/A cells 0.7x the arms", {"aascale": 0.7}),
            ("regimes 0.5/1/3/0.7/2/1 x", {"rscale": dict(zip(REGIMES, (0.5, 1, 3, 0.7, 2, 1)))}))):
        ph, nvh, fmh = noise_drill(seed=40 + i, **kw)
        check("(G2) noise drill, %s" % nm, ph <= 0.05,
              "P(h* != 64) = %.3f over %d trials (accept <= 0.05); median f(A/A) %.4f; nights with a first void %d"
              % (ph, NOISE_TRIALS, fmh, nvh))
    # its control: rev 7's floor (the A/A term alone) on the 3x night must FAIL the acceptance;
    # rev 9's twin term and gate also see a noisier regime, so the control turns them off too
    # (rev 10: and the per-pattern twin term, which sees a noisier regime too)
    globals()["POOL_TERM"], globals()["TWIN_TERM"], globals()["AGREE_GATE"], globals()["PAT_TWIN"], globals()["CONFIRM"] = (False,) * 5
    try:
        pc, _nv, _fm = noise_drill(seed=41, rscale={"not-warm": 3.0})
    finally:
        globals()["POOL_TERM"], globals()["TWIN_TERM"], globals()["AGREE_GATE"], globals()["PAT_TWIN"], globals()["CONFIRM"] = (True,) * 5
    check("(G2) control: one regime 3x, A/A floor alone", pc > 0.15,
          "P(h* != 64) = %.3f over %d trials (the drill sees the defect: accept > 0.15)" % (pc, NOISE_TRIALS))
    # its power (the floor's cost, recorded): a true 10 % win of every head <= 8 where it loops
    rng = random.Random(3)
    picks = [synth_night(rng, 0.01, wins={h: 0.90 for h in (0, 1, 2, 4, 8)})["hstar"] for _ in range(60)]
    check("(F2) power: a true 10 % win at h <= 8", sum(x == 8 for x in picks) / 60 >= 0.9,
          "h* = 8 in %d of 60 nights (picks %s)" % (sum(x == 8 for x in picks), sorted(set(picks))))
    # G4 (rev 8, r36): a real one-cell win of H(8) alone (5 % in C1/hex32/hit-dense/off) never
    # ships a head that measured no win (r36 measured H(16)/H(24) MEASURED in ~12 % of nights)
    rng = random.Random(9)
    g4 = {}
    for _ in range(200):
        x = synth_night(rng, 0.01, cellwins={("C1", "hex32", "h8", "hit-dense", "off"): 0.95})["hstar"]
        g4[x] = g4.get(x, 0) + 1
    nowin = sum(n for x, n in g4.items() if x not in (8, GRID_TOP))
    check("(G4) a one-cell win of H(8) alone", nowin <= 10,
          "picks %s over 200 nights; a head other than 8 or 64: %d (accept <= 10, the noise budget)"
          % (dict(sorted(g4.items())), nowin))
    # F3: THE UNIMODAL DRILL: unimodal launches must not void (per night, and per cell)
    rng = random.Random(4)
    nights, cellsv, ncell = 0, 0, 0
    for _ in range(NOISE_TRIALS):
        v = synth_night(rng, 0.01, noise="t5")
        nights += v["voided_first"] > 0
        cellsv += v["voided_first"]
        ncell += 108 + 12
    check("(F3) unimodal drill, t(5) launches", nights / NOISE_TRIALS <= 0.05,
          "void rate %.3f of nights, %.5f of cells over %d nights (accept <= 0.05)"
          % (nights / NOISE_TRIALS, cellsv / ncell, NOISE_TRIALS))
    # its control: a truly bimodal arm (2 of 5 launches 8 % slow) must void
    rng = random.Random(5)
    hit = 0
    for _ in range(50):
        APP, globals()["APPROX"] = APPROX, {}
        try:
            rows, same = synth_rows(rng, 0.01, bimodal_cells=[("C1", "hex32", "h8", "hit-dense", "off")])
            v = analyse({"files": {"results.tsv": (rows, {})}, "same": same}, set())
        finally:
            globals()["APPROX"] = APP
        hit += ("C1", "hex32", "hit-dense", "off") in v["owed_rerun"].get("results.tsv", set())
    check("(F3) control: a bimodal arm voids", hit >= 45,
          "2 of 5 launches 8 %% slow (~8 launch sigmas): voided in %d of 50 (accept >= 45)" % hit)

    # G3 (rulings R1, rev 8 r36): a MEDIAN-MOVING split (3 of 5 launches slow) of I's arm in ONE
    # cell, at sizes f..2f (f this script's median floor on a 1 % night): I's pooled reading
    # keeps it from shipping a head (r36 measured h* = 24 in 54 of 100 nights at 5 %)
    cellI = ("C1", "hex32", "I", "hit-dense", "off")
    for mult in (1.0, 1.5, 2.0):
        s = fmed * mult
        rng = random.Random(int(50 + 10 * mult))
        offn = sum(synth_night(rng, 0.01, splits={cellI: (3, 1 + s)})["hstar"] != GRID_TOP
                   for _ in range(NOISE_TRIALS))
        check("(G3) 3-of-5 split of I, %.1f f (%.1f %%)" % (mult, 100 * s), offn / NOISE_TRIALS <= 0.05,
              "P(h* != 64) = %.3f over %d nights (accept <= 0.05)" % (offn / NOISE_TRIALS, NOISE_TRIALS))
    # its control: rev 7's reading (I's own arm alone) under the same split must FAIL the acceptance
    # (rev 10: rev 7 had no per-pattern twin term either; with I alone no pool has a twin, so the
    # term would void every cell and blind the control)
    globals()["POOL_I"], globals()["PAT_TWIN"], globals()["CONFIRM"] = False, False, False
    try:
        rng = random.Random(65)
        offc = sum(synth_night(rng, 0.01, splits={cellI: (3, 1 + 1.5 * fmed)})["hstar"] != GRID_TOP
                   for _ in range(NOISE_TRIALS))
    finally:
        globals()["POOL_I"], globals()["PAT_TWIN"], globals()["CONFIRM"] = True, True, True
    check("(G3) control: the 1.5 f split, I's arm alone", offc / NOISE_TRIALS > 0.15,
          "P(h* != 64) = %.3f over %d nights (the drill sees the defect: accept > 0.15)"
          % (offc / NOISE_TRIALS, NOISE_TRIALS))
    # its converse: the same split in a HEAD arm (not pooled) never ships that head
    cellH = ("C1", "hex32", "h8", "hit-dense", "off")
    for mult in (1.0, 2.0):
        s = fmed * mult
        rng = random.Random(int(70 + 10 * mult))
        picks = [synth_night(rng, 0.01, splits={cellH: (3, 1 + s)})["hstar"] for _ in range(100)]
        check("(G3) converse: the split in H(8), %.1f f" % mult, sum(x == 8 for x in picks) == 0,
              "h* = 8 in %d of 100 nights (accept 0); picks %s" % (sum(x == 8 for x in picks), sorted(set(picks))))
    # The FAST 3-of-5 split in a head arm: outside the pool's reach and the gate's (r36's null-rate
    # numbers, rev 8 §3 "Bimodal"), rev 9's NAMED LIMIT (27 of 100). Rev 10's confirming re-run
    # (r38 R2) retires it: a transient does not recur on the confirm. Now a check (accept <= 5 of
    # 100), with rev 9's rate printed beside it
    rng = random.Random(90)
    picks = [synth_night(rng, 0.01, splits={cellH: (3, 1 / (1 + 1.5 * fmed))})["hstar"] for _ in range(100)]
    globals()["PAT_TWIN"], globals()["CONFIRM"] = False, False
    try:
        rng = random.Random(90)
        picks9 = [synth_night(rng, 0.01, splits={cellH: (3, 1 / (1 + 1.5 * fmed))})["hstar"] for _ in range(100)]
    finally:
        globals()["PAT_TWIN"], globals()["CONFIRM"] = True, True
    check("(G3, r38 R2) a FAST 3-of-5 split in H(8), 1.5 f", sum(x == 8 for x in picks) <= 5,
          "h* = 8 in %d of 100 nights (accept <= 5: rev 9's NAMED LIMIT retired by the confirm)" % sum(x == 8 for x in picks))
    # its control, CHECKED (rev 11, r39 K8: rev 10 only printed it): rev 9's rule must ship the split
    check("(G3, r38 R2) control: the FAST split, rev 9's rule", sum(x == 8 for x in picks9) > 15,
          "h* = 8 in %d of 100 nights, no per-pattern term and no confirm (the drill sees the limit: accept > 15)"
          % sum(x == 8 for x in picks9))

    # H1 (rev 9, RULED r37): BETWEEN-RUN noise, an offset per ARM held over its 5 launches. In one
    # regime with the A/A cells spared (the shape the launch term and the night-wide A/A term
    # cannot see), and in every regime (A/A arms included, and spared)
    for i, tau in enumerate((0.01, 0.02, 0.03)):
        for nm, ao, sd in (("one regime (not-warm), A/A spared", (tau, ("not-warm",), True), 300 + i),
                           ("every regime", (tau, None, False), 310 + i),
                           ("every regime, A/A spared", (tau, None, True), 320 + i)):
            ph, nvh, fmh = noise_drill(seed=sd, armoff=ao)
            check("(H1) arm offsets tau %d %%, %s" % (round(100 * tau), nm), ph <= 0.05,
                  "P(h* != 64) = %.3f over %d nights (accept <= 0.05); median f(A/A) %.4f, f(hit-dense/off) %.4f; "
                  "nights with a first void %d" % (ph, NOISE_TRIALS, fmh, NOISE_LAST["fcell"], nvh))
    # its control: rev 8's rule (no twin term, no agreement gate) on the 2 % one-regime night
    globals()["TWIN_TERM"], globals()["AGREE_GATE"], globals()["PAT_TWIN"], globals()["CONFIRM"] = (False,) * 4
    try:
        pc, _nv, _fm = noise_drill(seed=301, armoff=(0.02, ("not-warm",), True))
    finally:
        globals()["TWIN_TERM"], globals()["AGREE_GATE"], globals()["PAT_TWIN"], globals()["CONFIRM"] = (True,) * 4
    check("(H1) control: tau 2 %, one regime, rev 8's rule", pc > 0.15,
          "P(h* != 64) = %.3f over %d nights (the drill sees the defect: accept > 0.15)" % (pc, NOISE_TRIALS))

    # H2 (rev 9, RULED r37): a WHOLE-ARM (5-of-5) shift of I and of H(64) in the SMALLEST pools (I,
    # H(64): hex64, uuid36, alt49), sized by the cell's own floor f (hit-dense, off) on a 1 % night
    _p, _n, _f = noise_drill(seed=1)
    fcell = NOISE_LAST["fcell"]
    for pat in ("hex64", "uuid36", "alt49"):
        for arm in ("I", "h%d" % GRID_TOP):
            for j, mult in enumerate((1.0, 1.5, 2.0)):
                key = ("C2", pat, arm, "hit-dense", "off")
                ph, nvh, _fm = noise_drill(seed=400 + 10 * j + (arm == "I") + 100 * ("hex64", "uuid36", "alt49").index(pat),
                                           splits={key: (5, 1 + mult * fcell)})
                check("(H2) 5-of-5 shift of %s at %s, %.1f f (%.1f %%)" % (arm if arm == "I" else "H(64)", pat, mult,
                                                                          100 * mult * fcell), ph <= 0.05,
                      "P(h* != 64) = %.3f over %d nights (accept <= 0.05); nights with a first void %d"
                      % (ph, NOISE_TRIALS, nvh))
    globals()["TWIN_TERM"], globals()["AGREE_GATE"], globals()["PAT_TWIN"], globals()["CONFIRM"] = (False,) * 4
    try:
        pc, _nv, _fm = noise_drill(seed=499, splits={("C2", "hex64", "I", "hit-dense", "off"): (5, 1 + 1.5 * fcell)})
    finally:
        globals()["TWIN_TERM"], globals()["AGREE_GATE"], globals()["PAT_TWIN"], globals()["CONFIRM"] = (True,) * 4
    check("(H2) control: I at hex64, 1.5 f, rev 8's rule", pc > 0.15,
          "P(h* != 64) = %.3f over %d nights (the drill sees the defect: accept > 0.15)" % (pc, NOISE_TRIALS))
    # the agreement gate's own cost: the void rate it ADDS on pure noise (F3's acceptance: <= 5 %
    # of nights void a cell once, whatever voids it)
    for nm, nz, sd in (("normal", "normal", 500), ("t(5)", "t5", 501)):
        globals()["AGREE_GATE"] = False
        try:
            _p0, nv0, _f0 = noise_drill(seed=sd, noise=nz)
        finally:
            globals()["AGREE_GATE"] = True
        _p1, nv1, _f1 = noise_drill(seed=sd, noise=nz)
        check("(H2) the gate's void rate, %s launches" % nm, nv1 / NOISE_TRIALS <= 0.05,
              "nights with a first void %.3f with the gate, %.3f without: added %.3f (accept: with <= 0.05)"
              % (nv1 / NOISE_TRIALS, nv0 / NOISE_TRIALS, (nv1 - nv0) / NOISE_TRIALS))
    # H3 (rev 9, r37): I's pool record must name every C1-C2 pattern x layer, each with the top
    full = {p: {ly: [h for h in GRID if h >= len(PATTERNS[p][1]) or p in ("lit40", "abc60")] for ly in LAYERS}
            for c in ("C1", "C2") for p in CARD_PATS[c]}
    part = {p: v for p, v in full.items() if p != "hex64"}
    nolayer = dict(full, uuid36={"off": full["uuid36"]["off"]})
    no64 = dict(full, alt49={ly: [] for ly in LAYERS})
    refs = [pool_record_refusal(x) for x in (full, None, part, nolayer, no64)]
    APP, globals()["APPROX"] = APPROX, {}
    try:
        rows, _same = synth_rows(random.Random(11), 0.01)
        vmiss = analyse({"files": {"results.tsv": (rows, {})}, "same": None}, set())
    finally:
        globals()["APPROX"] = APP
    check("(H3) a missing or partial pool record is refused", refs[0] is None and all(refs[1:]) and vmiss["code"] == 2
          and vmiss["hstar"] is None and any("REFUSED" in l for l in vmiss["lines"]),
          "full: %s; missing/partial/layer/no-64 refused: %s; the rule on a missing record: code %d"
          % (refs[0], [bool(x) for x in refs[1:]], vmiss["code"]))
    # F7: the re-run merge: void once -> owed; re-run clean -> read; re-run void -> void twice
    def night_with(first_bimodal, rerun_bimodal, g2=(), c3=None, seed=6):
        rng = random.Random(seed)
        APP, globals()["APPROX"] = APPROX, {}
        try:
            cell = ("C1", "hex32", "h8", "hit-dense", "off")
            rows, same = synth_rows(rng, 0.01, bimodal_cells=[cell] if first_bimodal else [])
            files = {"results.tsv": (rows, {})}
            if rerun_bimodal is not None:
                fresh, _s = synth_rows(rng, 0.01, bimodal_cells=[cell] if rerun_bimodal else [])
                files["results.tsv"] = (rows, {k: r for k, r in fresh.items()
                                               if (k[0], k[1], k[3], k[4]) == ("C1", "hex32", "hit-dense", "off")})
            if c3 is not None:
                files.update(c3)
            return analyse({"files": files, "same": same}, set(g2))
        finally:
            globals()["APPROX"] = APP
    v = night_with(True, None)
    check("(F7) a cell void once", v["code"] == 3 and v["hstar"] is None and any("rerun" in l for l in v["lines"]),
          "code %d; %s" % (v["code"], v["lines"][-1]))
    v = night_with(True, False)
    check("(F7) re-run clean: the cell is read", v["hstar"] == GRID_TOP and v["rec"] is None,
          "h* %s, %s" % (v["hstar"], v["label"]))
    v = night_with(True, True)
    check("(F7) re-run void again: void twice, step (5)", v["hstar"] == GRID_TOP and v["rec"] is not None
          and "void twice" in v["label"], "h* %s, %s" % (v["hstar"], v["label"]))
    # F5: step (5) with G2's 64 defective and a void cell: the largest R0-surviving head, not 64
    v = night_with(True, True, g2=[64])
    check("(F5) step (5) after R0 removed 64", v["hstar"] == 32 and "largest R0-surviving" in v["label"],
          "h* %s, %s" % (v["hstar"], v["label"]))

    # F5's worse case: H(64) fails its gate in C3 (the only card where it loops): never a clean tie
    def c3_rows(h, gatefail_arm=None):
        rng = random.Random(7)
        r3 = {}
        for pat in CARD_PATS["C3"]:
            for rg in REGIMES:
                for ly in ("off", "on"):
                    T = rng.uniform(0.2, 2.0)
                    for a in dict.fromkeys(("I", "h0", "h%d" % h)):
                        if a == gatefail_arm and pat == "hex1000" and rg == "hit-dense" and ly == "off":
                            r3[("C3", pat, a, rg, ly)] = {"status": "gatefail", "med": None, "launches": [],
                                                          "method": "kit", "note": "GATE FAIL"}
                            continue
                        ls = [T * math.exp(0.01 * rng.gauss(0, 1)) for _ in range(LAUNCHES)]
                        r3[("C3", pat, a, rg, ly)] = {"status": "ok", "med": statistics.median(ls),
                                                      "launches": ls, "method": "kit", "note": ""}
        return {"results_c3_h%d.tsv" % h: (r3, {})}
    v = night_with(False, None, c3=c3_rows(64, gatefail_arm="h64"))
    check("(F5, G5) C3 gate fail of H(64): a CHOSEN tie at 32", v["hstar"] == 32
          and any("H(64) failed its gate in C3" in l for l in v["lines"]) and v["code"] == 3
          and "largest R0-surviving head (CHOSEN" in v["label"] and "MEASURED" not in v["label"],
          "h* %s, code %d; %s" % (v["hstar"], v["code"], v["label"]))
    v = night_with(False, None, c3=c3_rows(64))
    check("(F4) C3 timed at h* = 64: R2(C3)/R5 computed", v["code"] == 0 and v["hstar"] == GRID_TOP
          and not any("NOT COMPUTED" in l for l in v["lines"]), "code %d; %s" % (v["code"], v["lines"][-1]))
    v = night_with(False, None)
    check("(F4) C3 not yet timed at h*", v["code"] == 3 and any("NOT COMPUTED at h* = 64" in l for l in v["lines"]),
          v["lines"][-1])
    # F8: the approximated regimes are void by method: step (5) fires, the pick is recorded
    rng = random.Random(8)
    rows, same = synth_rows(rng, 0.01, approx_read=False)
    v = analyse({"files": {"results.tsv": (rows, {})}, "same": same}, set())
    check("(F8) approximated regimes void by method", v["hstar"] == GRID_TOP and "void by method" in v["label"],
          "h* %s; %s" % (v["hstar"], v["label"][:110]))
    # r35 F15: the deny check fires on an arm-I artifact that carries a span loop, and passes a clean one
    loop = b"x = ({ size_t rxa_mf1_j = 0; for (; rxa_mf1_j < 31; rxa_mf1_j++) if (!(a)) break; });"
    lk, rc_ = loop_audit([("p I off", "I", loop), ("p h0 off", "h0", loop)])
    check("(F15) deny check: a looping arm I fails", lk == ["p I off"] and rc_ == ["p h0 off"], "leaks %s reach %s" % (lk, rc_))
    lk, rc_ = loop_audit([("p I off", "I", b"for (;;) { }"), ("p h0 off", "h0", loop)])
    check("(F15) deny check: a clean arm I passes", lk == [] and rc_ == ["p h0 off"], "leaks %s reach %s" % (lk, rc_))
    # G6 (rev 8, r36): R3's DERIVED is reachable: H(1) 30 % faster wherever it loops; every
    # moving class picks 1, its E[D] head; the literal classes are not read
    APP, globals()["APPROX"] = APPROX, {}
    try:
        rng = random.Random(10)
        rows, same = synth_rows(rng, 0.01, wins={1: 0.70})
        night = {"files": {"results.tsv": (rows, {})}, "same": same}
        v = analyse(night, set())
        if v["owed_confirm"]:       # rev 10 (r38 R2): its wins are confirmed by the cells' re-run (rev 11: fresh twins)
            fresh, _s = synth_rows(rng, 0.01, wins={1: 0.70}, only=confirm_only(v["owed_confirm"]))
            night["files"]["results_confirm.tsv"] = (fresh, {})
            v = analyse(night, set())
    finally:
        globals()["APPROX"] = APP
    notread = sorted(l.split()[2].rstrip(":") for l in v["lines"] if "never a mover" in l)
    check("(G6) R3 DERIVED reachable", v["hstar"] == 1 and v["label"].startswith("DERIVED")
          and notread == ["abc60", "lit40"], "h* %s, %s; classes not read %s" % (v["hstar"], v["label"][:60], notread))
    # G7 (rev 8, r36; rev 9, r37 H4): the deny check reds on C3's population (an ignored deny
    # renders I as H(64), which loops past offset 64 at k = 500), with H(64), the DEFECT'S arm, as
    # the reach arm
    c3loop = b"x = ({ size_t rxa_mf1_j = 64; for (; rxa_mf1_j < 500; rxa_mf1_j++) if (!(a)) break; });"
    l0 = b"x = ({ size_t rxa_mf1_j = 0; for (; rxa_mf1_j < 500; rxa_mf1_j++) if (!(a)) break; });"
    lk, rc_ = loop_audit([("hex500 I off", "I", c3loop), ("hex500 h0 off", "h0", l0),
                          ("hex500 h64 off", "h64", c3loop)], reach_arm="h64")
    check("(G7) C3 deny check: an ignored deny fails", lk == ["hex500 I off"] and rc_ == ["hex500 h64 off"],
          "leaks %s reach %s" % (lk, rc_))
    # H4: at a width where H(64) loops nowhere (32), an ignored deny renders I = H(64) loop-free:
    # with L as the reach (rev 8) it read GREEN; with H(64) the reach is empty, VACUOUS and red
    w32 = [("hex500 I off", "I", b"if (!(a)) return 0;"), ("hex32 h0 off", "h0", l0),
           ("hex500 h64 off", "h64", b"if (!(a)) return 0;")]
    lk0, rc0 = loop_audit(w32, reach_arm="h0")
    lk, rc_ = loop_audit(w32, reach_arm="h64")
    seen = {}
    real = check_deny
    globals()["check_deny"] = lambda _rd, cl, reach_arm=None, vacuous_why=None: seen.update(
        arms=sorted({c[2] for c in cl}), cards=sorted({c[0] for c in cl}), reach=reach_arm, why=vacuous_why) or ([], 0, 0)
    try:
        c3_deny_check("-")
    finally:
        globals()["check_deny"] = real
    check("(H4) c3's reach arm is H(64), the defect's", lk0 == [] and rc0 == ["hex32 h0 off"] and lk == [] and rc_ == []
          and seen.get("reach") == "h64" and "h64" in seen.get("arms", []) and seen.get("cards") == ["C3", "C4"]
          and "loops nowhere" in (seen.get("why") or ""),
          "width 32, ignored deny: reach h0 %s (rev 8: green), reach h64 %s (vacuous: red); c3 checks %s over "
          "arms %s, reach %s" % (rc0, rc_, seen.get("cards"), seen.get("arms"), seen.get("reach")))
    # G8 (rev 8, r36): an empty movers file at h < 64 is refused; a smoke exits 4 first (the
    # example a real mover, r37 H7: `\w{32}\B` loops at h <= 29)
    r_none, r_empty, r_one, r_64 = (movers_refusal(32, None), movers_refusal(32, []),
                                    movers_refusal(24, [r"\w{32}\B"]), movers_refusal(64, []))
    check("(G8) identity: empty movers at h < 64 refused", bool(r_none) and bool(r_empty) and r_one is None
          and r_64 is None, "none: %s; empty: %s; one: %s; h 64 empty: %s" % (
              bool(r_none), (r_empty or "")[:40], r_one, r_64))
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        codes = (census_verdict([], 5), census_verdict(["x"], 5), census_verdict([], None), census_verdict(["x"], None))
    check("(G8) identity: smoke exit 4 before the empty FAIL", codes == (4, None, 1, None),
          "limit+empty %s, limit %s, empty %s, full %s" % codes)
    # H7 (rev 9, r37): the identity check floors the population that MOVES, not the file
    rr = (reach_refusal(32, 0, 40), reach_refusal(24, 3, 40), reach_refusal(64, 0, 40))
    check("(H7) identity: zero movers at h < 64 refused", bool(rr[0]) and rr[1] is None and rr[2] is None,
          "h 32 none move: %s; h 24 three move: %s; h 64: %s" % (bool(rr[0]), rr[1], rr[2]))
    # ---- rev 10 (RULED r38): THE CLASS DRILL, its controls, the power line, the void rate ----
    for i, (lvl, what, sel) in enumerate(CLASS_NOISE):
        for j, tau in enumerate(CLASS_TAUS):
            ph, nvh, _fm = noise_drill(seed=1000 + 10 * i + j, armoff=(tau, sel))
            check("(r38) noise at %s: %s, tau %d %%" % (lvl, what, round(100 * tau)), ph <= 0.05,
                  "P(h* != 64) = %.3f over %d nights (accept <= 0.05); nights with a first void %d"
                  % (ph, NOISE_TRIALS, nvh))
    for i, block in enumerate(night_blocks()):
        for kind in ("step", "drift"):
            for j, size in enumerate(CLASS_SIZES):
                ph, nvh = time_drill(kind, block, size, seed=1200 + 20 * i + 10 * (kind == "drift") + j)
                check("(r38) %s %+d %% in the %s" % (kind, round(100 * size), block), ph <= 0.05,
                      "P(h* != 64) = %.3f over %d nights (accept <= 0.05); nights with a first void %d"
                      % (ph, NOISE_TRIALS, nvh))
    # the controls: each defect's own shape under rev 9's rule must FAIL the acceptance
    globals()["PAT_TWIN"], globals()["CONFIRM"] = False, False
    try:
        pj1, _n = noise_drill(seed=1400, armoff=(0.02, lambda k: k[1] == "hex64"))[:2]
        cut = min(launch_slots("arm-major")[("C1", "hex24", "h8", rg, ly)][0] for rg in REGIMES for ly in LAYERS)
        pj2, _n = time_drill("step", (cut, cut + 1), 0.05, seed=1401, order="arm-major")
        pj2i, _n = time_drill("step", (cut, cut + 1), 0.05, seed=1401)
        parm, _n, _f = noise_drill(seed=1402, armoff=(0.02, lambda k: _c12(k) and k[2] == "h8"))
    finally:
        globals()["PAT_TWIN"], globals()["CONFIRM"] = True, True
    check("(r38) control J1: hex64 tau 2 %, rev 9's floor", pj1 > 0.15,
          "P(h* != 64) = %.3f over %d nights (the drill sees the defect: accept > 0.15)" % (pj1, NOISE_TRIALS))
    check("(r38) control J2: +5 % after hex24's H(4), arm-major", pj2 > 0.15,
          "P(h* != 64) = %.3f over %d nights, rev 9's floor and order (accept > 0.15); the same cut in the "
          "interleaved order, rev 9's floor: %.3f" % (pj2, NOISE_TRIALS, pj2i))
    # rev 11 (r39 K8): the interleaved order is r38 J2's fix, so the same cut in ROUNDS under rev 9's floor
    # must hold (a check, not a printed number: an order that regressed to arm-major reds here)
    check("(r38 J2) the same cut in rounds, rev 9's floor", pj2i <= 0.05,
          "P(h* != 64) = %.3f over %d nights (the rounds alone hold the step: accept <= 0.05)" % (pj2i, NOISE_TRIALS))
    check("(r38 R2) control: H(8)'s arm tau 2 %, rev 9's rule", parm > 0.15,
          "P(h* != 64) = %.3f over %d nights, no per-pattern term and no confirm (accept > 0.15)" % (parm, NOISE_TRIALS))
    # the POWER line: a real 5 % win of ONE head in ONE regime, before (rev 9's rule) and after;
    # with the confirm cells it costs (the plan's re-run term on a night with one real win)
    globals()["PAT_TWIN"], globals()["CONFIRM"] = False, False
    try:
        pw0 = {rg: power_rate(regime=rg)[0] for rg in ("hit-dense", "random")}
    finally:
        globals()["PAT_TWIN"], globals()["CONFIRM"] = True, True
    pw1, pcc = {}, {}
    for rg in ("hit-dense", "random"):
        pw1[rg], _p, pcc[rg] = power_rate(regime=rg, with_confirms=True)
    check("(r38) power: a 5 % win of H(8) in one regime", all(pw1[rg] >= max(0.9 * NOISE_TRIALS, pw0[rg] / 2)
                                                             for rg in pw1),
          "h* = 8 in %s of %d nights (rev 9's rule: %s; accept >= 90 %% and >= half rev 9's); confirm cells a night "
          "mean %s" % ("/".join("%s %d" % kv for kv in pw1.items()), NOISE_TRIALS,
                       "/".join("%s %d" % kv for kv in pw0.items()),
                       "/".join("%s %.1f" % (rg, statistics.mean(v)) for rg, v in pcc.items())))
    # the void rate on pure noise under rev 10 (F3: <= 5 % of nights void a cell once)
    for nm, nz, sd in (("normal", "normal", 1500), ("t(5)", "t5", 1501)):
        _p, nv, _f = noise_drill(seed=sd, noise=nz)
        check("(r38) void rate on pure noise, %s launches" % nm, nv / NOISE_TRIALS <= 0.05,
              "nights with a first void %.3f (accept <= 0.05); confirm cells a night mean %.3f, nights with one %d"
              % (nv / NOISE_TRIALS, statistics.mean(NOISE_LAST["confirm"]), sum(1 for x in NOISE_LAST["confirm"] if x)))
    selftest_rev11(check)
    selftest_rev12(check)
    # J2: `time_cells` times in ROUNDS (stubbed execution, no clock): each run of n launches holds
    # every arm of the cell once, and the order is the one the drills place their steps in
    import tempfile
    calls = []
    real_p, real_e = prepare_cell, _exec
    globals()["prepare_cell"] = lambda _rd, c, _n: list(c)
    globals()["_exec"] = lambda argv, c, env=None: calls.append(tuple(c)) or "t %d\n" % (len(calls) + 1)
    try:
        cl = [c for c in cells(cards=("C1",)) if c[1] == "hex24" and c[3] in ("hit-dense", "near-miss")]
        import pwd
        troot = os.environ.get("PCREC_TMPDIR") or "/var/tmp/pcrec-%s" % pwd.getpwuid(os.getuid()).pw_name
        os.makedirs(troot, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=troot) as td:      # the temp root, never /tmp
            out = os.path.join(td, "r.tsv")
            open(out, "w").close()
            time_cells(td, cl, out)
            nrows = sum(1 for ln in open(out) if not ln.startswith("#"))
    finally:
        globals()["prepare_cell"], globals()["_exec"] = real_p, real_e
    n_arm = len(GRID) + 1       # I and the finite heads (rev 12: no layout twin arm)
    rounds = [calls[i:i + n_arm] for i in range(0, len(calls), n_arm)]
    rr = all(len(set(r)) == n_arm and len({(c[0], c[1], c[3], c[4]) for c in r}) == 1 for r in rounds)
    same_order = [c for c, _i in launch_order(cl)] == calls
    check("(r38 J2) time_cells interleaves the arms in rounds", rr and same_order and nrows == len(cl)
          and len(calls) == LAUNCHES * len(cl),
          "%d launches over %d arm cells (%d rows): every round of %d holds each arm once: %s; the drills' order: %s"
          % (len(calls), len(cl), nrows, n_arm, rr, same_order))
    # J7: the identity reach per SOURCE: a movers file that moves nothing fails though a card moves
    rs = (source_reach_refusal(24, {"cards": 1, "census": 0, "movers": 0}, has_movers=True),
          source_reach_refusal(24, {"cards": 1, "census": 0, "movers": 2}, has_movers=True),
          source_reach_refusal(64, {"cards": 0, "census": 0, "movers": 0}, has_movers=True))
    check("(r38 J7) identity: the movers file's own reach", bool(rs[0]) and rs[1] is None and rs[2] is None,
          "h 24, a card moves, movers 0: %s; movers 2: %s; h 64: %s" % (bool(rs[0]), rs[1], rs[2]))
    print("selftest: %d checks, %d failed" % (nchk, bad))
    return 1 if bad else 0


# ---- the identity check (r45_reply rev 11 §3 "The head lever and its identity check") -------
ENCODINGS = {"byte": [], "utf8": ["-e", "utf8"]}


def census_covers(frozen_pcrec, limit=None):
    """Every corpus pattern the FROZEN pcrec covers in either encoding: the sweep's own population
    (scripts/emit_sweep.py enumerate_corpus) read through `--emit-facts`'s `cover` section, the
    census of record (cover_cap.md §6: "the sweep's count is the count of record"; r35 F9)."""
    sys.path.insert(0, os.path.join(TREE, "scripts"))
    import emit_sweep as es     # noqa: E402
    # the sweep decodes escapes to bytes; argv takes them back through the fs encoding
    pats = sorted({os.fsdecode(p) if isinstance(p, bytes) else p
                   for _f, _k, p in es.enumerate_corpus(frozen_pcrec, TREE, 60)})
    if limit:
        pats = pats[:limit]

    def covered(p):
        r = subprocess.run([frozen_pcrec, "--features", "all", "--emit-facts=byte,utf8", "--pattern", p],
                           capture_output=True, timeout=120)
        sect = ""
        for ln in r.stdout.decode("latin-1").splitlines():
            if ln.startswith("#section "):
                sect = ln.split(None, 1)[1]
            elif sect == "cover" and not ln.startswith("#"):
                f = ln.split("\t")
                if len(f) > 1 and f[1] == "cover":
                    return p
        return None
    with ThreadPoolExecutor(max_workers=int(os.environ.get("JOBS", "8"))) as ex:
        return len(pats), [p for p in ex.map(covered, pats) if p]


def movers_refusal(h, movers):
    """At h < 64 the predicted movers are the population (r45_reply §3): a missing OR EMPTY
    movers file is refused (rev 8, r36 G8: at h = 32 and width 32 neither the cards nor the census
    can move, so an empty file would pass on populations blind to the head). None: proceed."""
    if h >= GRID_TOP:
        return None
    if movers is None:
        return ("h = %d < %d and no PATTERNS file: the predicted movers are the population at h* < 64 "
                "(r45_reply §3); refusing to pass on the cards alone" % (h, GRID_TOP))
    if not movers:
        return ("h = %d < %d and the PATTERNS file is EMPTY: an empty prediction at h* < 64 is a population "
                "of zero (K35); refusing" % (h, GRID_TOP))
    return None


def reach_refusal(h, n_moving, n_pats):
    """The identity check's population is the patterns whose bytes MOVE at h, not the file that
    names them (rev 9, r37 H7: `a{40}` is byte-identical at heads 0-64, so a movers file holding
    it passed the file-level refusal with zero head-sensitive patterns). At h < 64 a zero is
    refused (K35). None: proceed."""
    if h >= GRID_TOP or n_moving:
        return None
    return ("h = %d < %d and none of the %d patterns (cards, census, movers) renders differently at lever %d "
            "than at lever %d on the frozen binary: the identity check would compare a population blind to "
            "the head (K35); refusing" % (h, GRID_TOP, n_pats, h, GRID_TOP))


def source_reach_refusal(h, counts, has_movers):
    """The reach PER SOURCE (rev 10, RULED r38 J7): `counts` {cards, census, movers: the number of
    that source's patterns whose bytes move at h}. Rev 9 pooled the three (r37 H7), so a movers
    file that moves nothing passed whenever a card moved (r38 J7: `a{40}` beside card hex32 at h
    24). At h < 64 the movers file's OWN count must be nonzero, and so must the total (K35).
    None: proceed."""
    if h >= GRID_TOP:
        return None
    if has_movers and not counts.get("movers"):
        return ("h = %d < %d and none of the PATTERNS file's patterns renders differently at lever %d than at "
                "lever %d on the frozen binary (cards %d, census %d move): the predicted movers are the "
                "population at h* < 64 and this one is blind to the head (K35); refusing"
                % (h, GRID_TOP, h, GRID_TOP, counts.get("cards", 0), counts.get("census", 0)))
    if not sum(counts.values()):
        return reach_refusal(h, 0, 0)
    return None


def lever_reach(h, pats, wf):
    """The patterns whose FROZEN lever-h text differs from the frozen lever-64 text in some
    encoding x layer (the defect a head-blind identity check would degenerate to is lever-64's
    bytes: the reach renders that arm and counts where it differs)."""
    def one(job):
        p, ename, ly = job
        base = ["-p", PREFIX, "--features", "all"] + ENCODINGS[ename] + wf + LAYERS[ly] + ["-o", "-", "--pattern", p]
        a = subprocess.run([HARNESS, "--harness=span-head=%d" % h] + base, capture_output=True, timeout=600)
        b = subprocess.run([HARNESS, "--harness=span-head=%d" % GRID_TOP] + base, capture_output=True, timeout=600)
        return p, a.returncode != b.returncode or a.stdout != b.stdout
    jobs = [(p, e, ly) for p in pats for e in ENCODINGS for ly in LAYERS]
    with ThreadPoolExecutor(max_workers=int(os.environ.get("JOBS", "8"))) as ex:
        return sorted({p for p, d in ex.map(one, jobs) if d})


def census_verdict(census, limit):
    """None to proceed; else the exit code: a SMOKE (--census-limit) exits 4 before any verdict,
    an empty census or none (rev 8, r36 G8); a full run with an empty census FAILS (K35)."""
    if limit:
        if not census:
            print("identity: SMOKE (--census-limit %d): the census of the first %d patterns is empty; not a "
                  "verdict" % (limit, limit))
            return 4
        return None
    if not census:
        print("identity: FAIL: the census is empty (K35)")
        return 1
    return None


def cmd_identity(args):
    """The lever at H on the FROZEN binary (pcrec-harness --harness=span-head=H) against the
    REBUILT build/pcrec, byte for byte, both encodings and both layers, over the card patterns,
    the census covers (read from the sweep's corpus) and the PATTERNS file (main's predicted
    movers; REQUIRED when H < 64). --census-limit N is a SMOKE (exit 4, never a verdict)."""
    if not os.environ.get("FROZEN"):
        raise SystemExit("identity: FROZEN is unset: name the build dir the cards timed (an unset FROZEN would "
                         "compare the rebuilt tree's own harness, losing the frozen-to-rebuilt tie; r35 F9)")
    h = int(args[0])
    rest = [a for a in args[1:] if not a.startswith("--census-limit")]
    limit = None
    if "--census-limit" in args:
        limit = int(args[args.index("--census-limit") + 1])
        rest = [a for a in rest if a != str(limit)]
    rebuilt_dir = os.environ.get("REBUILT") or os.path.join(TREE, "build")
    if os.path.realpath(rebuilt_dir) == os.path.realpath(BUILD):
        raise SystemExit("identity: FROZEN and REBUILT are one build dir (%s): nothing ties the frozen binary "
                         "to the rebuilt one" % BUILD)
    movers = None
    if rest:
        movers = [ln.rstrip("\n") for ln in open(rest[0], encoding="latin-1") if ln.strip()]
    why = movers_refusal(h, movers)
    if why:
        raise SystemExit("identity: " + why)
    movers = movers or []
    if rest:
        print("identity: predicted movers: %d (%s)" % (len(movers), rest[0]))
    pats = sorted({p[0] for p in PATTERNS.values()})
    n_corpus, census = census_covers(PCREC, limit)
    print("identity: census: %d corpus patterns read, %d covered by the frozen pcrec" % (n_corpus, len(census)))
    code = census_verdict(census, limit)
    if code is not None:
        return code
    allp = sorted(set(pats) | set(census) | set(movers))
    rebuilt = os.path.join(rebuilt_dir, "pcrec")
    wf = [] if WIDTH_FLAG == "none" else [WIDTH_FLAG]
    if h < GRID_TOP:
        moving = lever_reach(h, allp, wf)
        print("identity: reach: %d of %d patterns render differently at lever %d than at lever %d on the frozen "
              "binary (r37 H7)%s" % (len(moving), len(allp), h, GRID_TOP,
                                     (": " + ", ".join(repr(p) for p in moving[:8]) + (", ..." if len(moving) > 8 else ""))
                                     if moving else ""))
        mv = set(moving)
        counts = {"cards": len(mv & set(pats)), "census": len(mv & set(census)), "movers": len(mv & set(movers))}
        print("identity: reach per source (r38 J7): cards %d of %d, census %d of %d, movers %d of %d"
              % (counts["cards"], len(set(pats)), counts["census"], len(set(census)), counts["movers"], len(set(movers))))
        why = source_reach_refusal(h, counts, has_movers=bool(rest))
        if why:
            print("identity: FAIL: " + why)
            return 4 if limit else 1

    def one(job):
        p, ename, ly = job
        base = ["-p", PREFIX, "--features", "all"] + ENCODINGS[ename] + wf + LAYERS[ly] + ["-o", "-", "--pattern", p]
        a = subprocess.run([HARNESS, "--harness=span-head=%d" % h] + base, capture_output=True, timeout=600)
        b = subprocess.run([rebuilt] + base, capture_output=True, timeout=600)
        return job, a.returncode != b.returncode or a.stdout != b.stdout
    jobs = [(p, e, ly) for p in allp for e in ENCODINGS for ly in LAYERS]
    diff = 0
    with ThreadPoolExecutor(max_workers=int(os.environ.get("JOBS", "8"))) as ex:
        for (p, e, ly), d in ex.map(one, jobs):
            if d:
                diff += 1
                print("IDENTITY DIFFERS: %r %s %s" % (p, e, ly))
    print("identity: head %d, %d patterns (cards %d, census %d, movers %d) x %d encodings x %d layers, %d differ"
          % (h, len(allp), len(pats), len(census), len(movers), len(ENCODINGS), len(LAYERS), diff))
    if limit:
        print("identity: SMOKE (--census-limit %d): not a verdict" % limit)
        return 4
    return 1 if diff else 0


def cmd_c6selftest(args):
    """C6's checks of its own (review r79 F2, F5, F8, F10; no clock, no box): the rule files' shas and constants, the VERDICT
    on constructed outcomes (each drill names the clause it reads and must read its stated word), the RECORD header's
    refusals, and, given a RUNDIR (`dry`'s, or built here: 4 pcrec compiles), check_c6's plants, each red, beside its
    unplanted control. Exit 0 only when every row holds."""
    (rundir,), _opt = parse_args("c6selftest", args)
    fails, n = [], 0

    def row(ok, what):
        nonlocal n
        n += 1
        print("%s  c6selftest: %s" % ("ok  " if ok else "FAIL", what))
        if not ok:
            fails.append(what)
    row(rule_sha(C6_RULE_710_FILE) == C6_RULE_710_RECORDED,
        "rule_710.md's block sha %s is job 710's recorded %s" % (rule_sha(C6_RULE_710_FILE), C6_RULE_710_RECORDED))
    row(C6_RULE_SHA != C6_RULE_710_RECORDED and re.fullmatch(r"[0-9a-f]{16}", C6_RULE_SHA),
        "c6_rule.md's block sha %s, computed from the file" % C6_RULE_SHA)
    row(C6_CONST == {"FLOOR_MIN": 0.15, "SPREAD_MAX": 0.30, "AA_VOID_MAX": 0.05, "READABLE_MIN": 0.5},
        "the rule's CONSTANTS clause parses to %s" % C6_CONST)
    # ---- the VERDICT drills: constructed outcomes, LAUNCHES launches an arm
    J = [1.00, 1.01, 0.99, 1.02, 0.98]          # 2 % launch noise, deterministic

    def L(f, j=J):
        return [f * x for x in j]

    def cell(i, v=1.0, h=1.0, hb=1.0, rt=None, calls=1000, run=True, vj=J, layer="on"):
        c = {"key": ("C6", "p%d" % i, "random", layer), "calls": calls, "run": run,
             "arms": {"V": L(v, vj), "H64": L(h), "H64.b": L(hb)}}
        if rt is not None:
            c["retime"] = {"V": L(rt[0]), "H64": L(rt[1]), "H64.b": L(rt[2])}
        return c

    def verdict(cs):
        d = c6_decide(cs)[("C6", "on")]
        return d["verdict"], d
    base = [cell(i) for i in range(40)]
    drills = [
        ("CELL RULE, all TIE", base, "NO LOSS"),
        ("RE-TIME: a repeated LOSS (V 30 % slower twice)", base[1:] + [cell(99, v=1.3, rt=(1.3, 1.0, 1.0))], "LOSS"),
        ("RE-TIME: a LOSS not repeated", base[1:] + [cell(99, v=1.3, rt=(1.0, 1.0, 1.0))], "NO LOSS"),
        ("RE-TIME: a LOSS whose re-time did not run stands", base[1:] + [cell(99, v=1.3)], "LOSS"),
        ("RE-TIME: a WIN whose re-time did not run is a TIE", base[1:] + [cell(99, v=0.7)], "NO LOSS"),
        ("A/A: a standing A/A non-TIE at 4 of 40 cells (rate 0.10 > 0.05) VOIDS the box",
         base[4:] + [cell(90 + i, hb=1.3, rt=(1.0, 1.0, 1.3)) for i in range(4)], "VOID (A/A FAILED: rate 0.100 > 0.050)"),
        ("A/A: one standing A/A non-TIE of 40 (rate 0.025) makes its cell HARNESS, the box reads on",
         base[1:] + [cell(99, v=1.3, hb=1.3, rt=(1.3, 1.0, 1.3))], "NO LOSS"),
        ("A/A: no readable A/A cell is VOID", [dict(c, arms=dict(c["arms"], **{"H64.b": None})) for c in base],
         "VOID (A/A UNREAD)"),
        ("UNIT: a bimodal V (2 of 5 launches 40 % slow) is NOISE, never a TIE: all cells so -> INCONCLUSIVE-NOISE",
         [cell(i, vj=[1.0, 1.0, 1.0, 1.4, 1.4]) for i in range(40)], "INCONCLUSIVE-NOISE"),
        ("UNIT: one outlier launch does not hide a 25 % LOSS (the middle-three spread)",
         base[1:] + [dict(cell(99, rt=(1.25, 1.0, 1.0)), arms={"V": [1.25, 1.26, 1.24, 1.25, 2.5], "H64": L(1.0),
                                                                "H64.b": L(1.0)})], "LOSS"),
        ("N/A: every cell calls the span 0 times", [cell(i, calls=0) for i in range(10)], "INCONCLUSIVE-N/A"),
        ("WINDOW: 24 of 40 cells NOT-RUN", base[:16] + [cell(50 + i, run=False) for i in range(24)],
         "TRUNCATED: INCONCLUSIVE-NOT-RUN"),
        ("WINDOW: 4 of 40 cells NOT-RUN, the rest clean", base[:36] + [cell(50 + i, run=False) for i in range(4)],
         "TRUNCATED: NO LOSS"),
    ]
    for what, cs, want in drills:
        got, d = verdict(cs)
        row(got == want, "VERDICT drill %s: reads %r (want %r); A/A rate %s" % (what, got, want, d["rate"]))
    # the old unit's contrast (MEAS-3): the whole-range spread hides the same 25 % LOSS as a TIE
    old = [1.25, 1.26, 1.24, 1.25, 2.5]
    ofl = max(0.15, (max(old) - min(old)) / statistics.median(old))
    row(not (statistics.median(old) > 1.0 * (1 + ofl)), "the contrast: the whole-range spread floor %.2f reads that LOSS as a TIE" % ofl)
    # ---- the RECORD header
    h = c6_header("0" * 16, "1" * 16, ["on"], "rid")
    row(c6_header_check(h) is None, "RECORD: a header written now passes the check")
    row(c6_header_check(h.replace(C6_RULE_SHA, "f" * 16)) is not None, "RECORD: a header of another rule sha is refused")
    row(c6_header_check("#card\tpattern") is not None, "RECORD: a file with no #c6 header is refused")
    # ---- THE TIMER'S RECORD through its READER (U6): constructed records over C6/C6c's real population, written by the
    # timer's own head/end writers and row_line, read by c6_read alone (no timing, no exe)
    dd = os.path.join(rundir, "c6drill")
    os.makedirs(dd, exist_ok=True)
    pop = cells(cards=C6_CARDS)
    pkeys = list(dict.fromkeys((c[0], c[1], c[3], c[4]) for c in pop))
    # the named N/A cuts (c6_rule.md N/A: near-miss at the window sites with k <= 32), the dry's reach reading
    cut = {k for k in pkeys if k[2] == "near-miss" and C6_SITE[k[1]][0] == "window" and C6_SITE[k[1]][1] <= 32}

    def record(name, spec, end=True, header=None, launches=None):
        """spec(key) -> (calls, first {arm: factor | None (void) | 'short' | 'notrun'}, retime {arm: ..} | 'notrun' | None)."""
        path = os.path.join(dd, name + ".tsv")
        specs = {k: spec(k) for k in pkeys}
        c6_record_head(path, header or c6_header("0" * 16, "1" * 16, sorted({k[3] for k in pkeys}), "drill-" + name),
                       [("launches", LAUNCHES if launches is None else launches), ("dry", 0)],
                       [(k, specs[k][0]) for k in pkeys])

        def arm_row(pfx, k, a, x):
            c = (k[0], k[1], a, k[2], k[3])
            if k[2] in APPROX:
                return pfx + row_line(c, "method", note="void by method")
            if x == "notrun":
                return pfx + row_line(c, "notrun", note="drill")
            if x is None:
                return pfx + row_line(c, "void", note="drill: no valid launch")
            ls = L(1.0)[:3] if x == "short" else (x if isinstance(x, list) else L(x))
            return pfx + row_line(c, "ok", ls, variants=list(range(len(ls))))
        with open(path, "a") as f:
            for k in pkeys:
                calls, first, again = specs[k]
                if not calls:
                    continue
                for a in ("V", "H64", "H64.b"):
                    f.write(arm_row("first\t", k, a, first.get(a, 1.0)))
                if again is not None and k[2] not in APPROX:
                    for a in ("V", "H64", "H64.b"):
                        f.write(arm_row("retime\t", k, a, "notrun" if again == "notrun" else again.get(a, 1.0)))
        if end:
            c6_record_end(path, [("status", "drill")])
        return path

    def tie(k):
        return (0 if k in cut else 1000), {}, None

    def owe(first):
        return c6_owes({a: (None if first.get(a, 1.0) in (None, "short", "notrun") else L(first.get(a, 1.0)))
                        for a in ("V", "H64", "H64.b")})

    def mk(f):
        """spec from f(key) -> (first, retime-if-owed): the re-time set written exactly where the first pass owes one."""
        def spec(k):
            calls = 0 if k in cut else 1000
            first, again = f(k)
            return calls, first, (again if owe(first) and "notrun" not in first.values() else None)
        return spec
    timed_keys = [k for k in pkeys if k not in cut and k[2] not in APPROX]
    nm = {g: sum(1 for k in timed_keys if (k[0], k[3]) == g) for g in {(k[0], k[3]) for k in timed_keys}}
    late = set()                                              # the window closed after 40 % of each (card, layer)'s cells
    for g in nm:
        gk = [k for k in timed_keys if (k[0], k[3]) == g]
        late |= set(gk[len(gk) * 2 // 5:])
    aa3 = {g: [k for k in timed_keys if (k[0], k[3]) == g][:3] for g in nm}
    rdrills = [
        ("design: V WINs (repeated) at hit-dense, TIE elsewhere (block_span.md §8 on 710's CONFIRMED table)",
         mk(lambda k: (({"V": 0.5}, {"V": 0.5}) if k[2] == "hit-dense" else ({}, None))),
         {g: "NO LOSS" for g in nm}, 0),
        ("all-TIE", mk(lambda k: ({}, None)), {g: "NO LOSS" for g in nm}, 0),
        ("a high A/A rate (3 standing A/A non-TIE cells per (card, layer), rate > 0.05) VOIDS each box",
         mk(lambda k: (({"H64.b": 1.3}, {"H64.b": 1.3}) if k in aa3[(k[0], k[3])] else ({}, None))),
         {g: "VOID (A/A FAILED: rate %.3f > 0.050)" % (3 / n) for g, n in nm.items()}, 0),
        ("all-unreadable (every arm short of LAUNCHES valid launches): no readable A/A, VOID",
         mk(lambda k: ({"V": "short", "H64": "short", "H64.b": "short"}, None)), {g: "VOID (A/A UNREAD)" for g in nm}, 0),
        ("all-unreadable readings with a clean A/A (every V arm short): INCONCLUSIVE-NOISE",
         mk(lambda k: ({"V": "short"}, None)), {g: "INCONCLUSIVE-NOISE" for g in nm}, 0),
        ("truncated: 60 % of the cells NOT-RUN (first pass)",
         mk(lambda k: (({"V": "notrun", "H64": "notrun", "H64.b": "notrun"}, None) if k in late else ({}, None))),
         {g: "TRUNCATED: INCONCLUSIVE-NOT-RUN" for g in nm}, 4),
        ("a reading LOSS the re-time repeats", mk(lambda k: (({"V": 1.3}, {"V": 1.3}) if k == timed_keys[0] else ({}, None))),
         {g: ("LOSS" if g == (timed_keys[0][0], timed_keys[0][3]) else "NO LOSS") for g in nm}, 0),
        ("a reading LOSS the re-time does not repeat (a TIE, listed)",
         mk(lambda k: (({"V": 1.3}, {}) if k == timed_keys[0] else ({}, None))), {g: "NO LOSS" for g in nm}, 0),
        ("truncated re-time: a reading LOSS whose re-time did not start STANDS (and the reader exits 4)",
         mk(lambda k: (({"V": 1.3}, "notrun") if k == timed_keys[0] else ({}, None))),
         {g: ("LOSS" if g == (timed_keys[0][0], timed_keys[0][3]) else "NO LOSS") for g in nm}, 4),
    ]
    for i, (what, spec, want, wrc) in enumerate(rdrills):
        path = record("drill%d" % i, spec)
        cs, info = c6_read(path)
        dec = c6_decide(cs)
        got = {g: dec[g]["verdict"] for g in dec}
        rc = 4 if any(d["notrun"] for d in dec.values()) or info["retime_notrun"] else 0
        row(got == want and rc == wrc, "RECORD drill %s: reads %s, exit %d (want %s, exit %d)" % (
            what, sorted(got.items()), rc, sorted(want.items()), wrc))
        if i == 0:      # the design's WINs are the re-time's: a reader that dropped the re-time would read them as TIEs
            hd = {g: sum(1 for k in timed_keys if (k[0], k[3]) == g and k[2] == "hit-dense") for g in nm}
            row(all(dec[g]["wtl"]["WIN"] == hd[g] and len(dec[g]["notes"]) == hd[g] for g in nm),
                "RECORD drill design: the standing WINs are the hit-dense cells, each 'repeated' (%s)" % sorted(
                    (g, dec[g]["wtl"]["WIN"], hd[g]) for g in nm))
    # one cell per (card, layer, regime) N/A: listed with its count, excluded from every count
    one = {}
    for k in timed_keys:
        one.setdefault((k[0], k[3], k[2]), k)
    na1 = set(one.values())
    path = record("na_per_regime", lambda k: (0 if k in cut or k in na1 else 1000, {}, None))
    cs, info = c6_read(path)
    dec = c6_decide(cs)
    okna = all(set(dec[g]["na"]) == {k for k in cut | na1 if (k[0], k[3]) == g} and dec[g]["population"] ==
               nm[g] - sum(1 for k in na1 if (k[0], k[3]) == g) and dec[g]["verdict"] == "NO LOSS" for g in nm)
    row(okna, "RECORD drill one N/A cell per regime per (card, layer) (%d cells + the %d named cuts): listed N/A, out of the "
              "population, NO LOSS: %s" % (len(na1), len(cut), sorted((g, d["verdict"], len(d["na"]), d["population"])
                                                                       for g, d in dec.items())))
    # the reader's refusals (each beside the clean record above, which it reads)
    refusals = [
        ("no #end line (the run died)", record("noend", tie, end=False)),
        ("a header of another rule sha", record("oldrule", tie, header=c6_header("0" * 16, "1" * 16, ["on"], "x").replace(
            C6_RULE_SHA, "f" * 16))),
        ("recorded at another LAUNCHES", record("launches", tie, launches=LAUNCHES + 2)),
        ("a re-time the first pass owes, absent", record("owedmissing", lambda k: (
            0 if k in cut else 1000, {"V": 1.3} if k == timed_keys[0] else {}, None))),
        ("a re-time the first pass does not owe, present", record("notowed", lambda k: (
            0 if k in cut else 1000, {}, {} if k == timed_keys[0] else None))),
    ]
    for what, path in refusals:
        try:
            c6_read(path)
            row(False, "RECORD refusal %s: READ (want refused)" % what)
        except SystemExit as e:
            row(e.code == 2, "RECORD refusal %s: refused, exit %s" % (what, e.code))
    # ---- THE CPU-QUIET CONTROL (rule_710.md; R-1 (c)): a stubbed probe, stubbed counters, no clock
    class StubProbe:
        def __init__(self, busy, niv=0, secs=lambda i: 0.06, sample=0.01):
            self.busy, self.niv, self.secs, self.sample, self.n, self.cpu, self.sib = busy, niv, secs, sample, 0, "s", "s"

        def second(self):
            return self.sample, 0.0

        def measure(self, argv, cell, env):
            self.n += 1
            b = self.busy(self.n) if callable(self.busy) else self.busy
            return 1.0, b, self.niv(self.n) if callable(self.niv) else self.niv, self.secs(self.n)
    cell0 = ("C6", "p", "V", "random", "on")
    qd = os.path.join(dd, "qc")
    os.makedirs(qd, exist_ok=True)

    def qcon(probe):
        qc = QuietControl(probe, os.path.join(qd, "sample.tsv"), os.path.join(qd, "voids.tsv"))
        qc.sample(["stub"], cell0, {})
        qc.pass_ = "drill"
        return qc
    q = qcon(StubProbe(0.01))
    row(abs(q.qc["cpu7_max"] - CPU7_LOW) < 1e-12 and q.qc["nivcsw_max"] == 2 and not q.qc["cpu7_capped"],
        "QUIET thresholds from a quiet stubbed sample: CPU7_MAX %.3f (the 5 %% floor), NIVCSW_MAX %d" % (
            q.qc["cpu7_max"], q.qc["nivcsw_max"]))
    qb = qcon(StubProbe(0.01, sample=0.15))
    row(abs(qb.qc["cpu7_max"] - CPU7_CAP) < 1e-12 and qb.qc["cpu7_capped"],
        "QUIET thresholds from a busy sample (15 %%): CPU7_MAX capped at %.2f, flagged" % qb.qc["cpu7_max"])
    p = StubProbe(lambda i: 0.9 if i == QC_CAL_REPS + 1 else 0.01)      # the first launch after the calibration is noisy
    q = qcon(p)
    x = q.launch(["stub"], cell0, {})
    row(x == 1.0 and q.voids == 1 and p.n == QC_CAL_REPS + 2,
        "QUIET a noisy launch (sibling 90 %% busy) is VOID and re-timed once: value %s, voids %d, launches %d" % (
            x, q.voids, p.n - QC_CAL_REPS))
    p = StubProbe(0.01, niv=lambda i: 0 if i <= QC_CAL_REPS else 50)       # every timed launch preempted
    q = qcon(p)
    x = q.launch(["stub"], cell0, {})
    row(x is None and q.voids == 1 + QC_RETIMES and p.n - QC_CAL_REPS == 1 + QC_RETIMES,
        "QUIET a launch void on every attempt (nivcsw 50 > 2) is re-timed up to %d more times, then counts as SHORT (None):"
        " voids %d, launches %d" % (QC_RETIMES, q.voids, p.n - QC_CAL_REPS))
    for secs, want in ((0.5, 1.0), (0.06, None)):
        p = StubProbe(0.01, niv=lambda i: 1 if i <= QC_CAL_REPS else 3, secs=lambda i, s=secs: 0.06 if i <= QC_CAL_REPS else s)
        q = qcon(p)
        got = q.launch(["stub"], cell0, {})
        row(got == want, "QUIET the nivcsw limit scales with the launch's length: 3 switches in a %.2f s launch vs NIVCSW_MAX "
                         "%d per %.2f s reads %s" % (secs, q.qc["nivcsw_max"], q.qc["t_cal"], "valid" if got else "VOID"))
    short = c6_cell({"key": ("C6", "p", "random", "on"), "calls": 1, "arms": {"V": L(1.0)[:LAUNCHES - 1], "H64": L(1.0),
                                                                               "H64.b": L(1.0)}})
    row(short[0] == "NOISE" and short[1] == "TIE", "QUIET an arm short of LAUNCHES valid launches: its reading is NOISE, "
                                                    "the A/A reads on (%s, %s)" % short[:2])
    # ---- DRY's guard (no clock): the clock call and a timed exec raise ClockCalled, which no `except Exception` swallows
    un, seen = dry_guard()
    hit = []
    try:
        for what, fn in (("timed_launch", lambda: timed_launch(["true"], cell0, {})),
                         ("a taskset exec", lambda: subprocess.run(["taskset", "-c", "0", "true"])),
                         ("a CARD_TIME exec", lambda: subprocess.run(["true"], env={"CARD_TIME": "1"}))):
            try:
                fn()
            except ClockCalled:
                hit.append(what)
        plain = subprocess.run(["true"]).returncode == 0
    finally:
        un()
    row(len(hit) == 3 and plain and not issubclass(ClockCalled, Exception) and seen["clock"] == 1 and seen["subprocess"] == 2,
        "DRY guard: %s raise ClockCalled (a BaseException); an untimed exec runs" % ", ".join(hit))
    # ---- the RE-TIME pool (arm_pool): four new layouts, never a first-pass variant; the first pass's pool unchanged
    same0 = all(arm_pool("t%d" % i, ly, a) == pool_variants("t%d" % i, align_variants_of(ly), pool_salt(a))
                for i in range(300) for ly in LAYER for a in ("V", "H64", "H64.b"))
    clash, redrawn = 0, 0
    for i in range(2000):
        for ly in ("on", "off-clang", "off-os"):
            fp = {(pre, tuple(fl)) for salt in ("", "aa") for _v, pre, fl in pool_variants("t%d" % i, align_variants_of(ly), salt)}
            for a in ("V", "H64", "H64.b"):
                rp = arm_pool("t%d" % i, ly, a, 1)
                clash += sum(1 for _v, pre, fl in rp if (pre, tuple(fl)) in fp)
                redrawn += rp != pool_variants("t%d" % i, align_variants_of(ly), pool_salt(a, 1))
    row(same0 and clash == 0 and redrawn > 0, "RE-TIME pool: retime 0 is pool_variants' pool (300 texts x every layer x arm); "
        "over 2000 texts x 3 layers x 3 arms the fresh pool shares no (prelude, flags) with a first pass (%d clashes), %d "
        "draws redrawn" % (clash, redrawn))
    # ---- check_c6's plants (on RUNDIR's artifacts: `dry`'s, or built here)
    if True:
        os.makedirs(rundir, exist_ok=True)
        it = {(p, ly): (open(artifact(rundir, p, "V", ly), "rb").read(), open(artifact(rundir, p, "H64", ly), "rb").read())
              for p, ly in (("c6_hex32", "on"), ("c6_dig32", "on"), ("c6_hex32", "off-clang"))}
        items = [(p, ly, v, d) for (p, ly), (v, d) in sorted(it.items())]
        b0, _n = check_c6_texts(items)
        row(not b0, "check_c6 control: the 3 real (pattern, layer) texts read clean (%s)" % b0)
        v, d = it[("c6_hex32", "on")]
        name = sorted({m.group(1) for m in V_SELDEF_RE.finditer(v) if b"__" not in m.group(1)})[0]
        sel = _fn_text(v, name)
        dead_sel = v.replace(sel, sel.replace(name + b"__w32(", name + b"__body("))
        cut = v.find(sel) + len(sel)
        no_call = v[:cut] + re.sub(rb"(?<![A-Za-z0-9_])" + re.escape(name) + rb"\(", name + b"X(", v[cut:])
        w32 = _fn_text(v, name + b"__w32")
        cmt = dead_sel.replace(w32, b"/* " + name + b"__w32( */\n")
        m = V_LOOP_RE.search(w32)
        badk = v.replace(m.group(0), m.group(0).replace(b"< " + m.group(2), b"< " + str(int(m.group(2)) - 1).encode()))
        plants = [
            ("the selector calls `__body` while `__w32` is defined", [("c6_hex32", "on", dead_sel, d)], None),
            ("the site never calls the selector (only its definition names it)", [("c6_hex32", "on", no_call, d)], None),
            ("`__w32` only in a comment", [("c6_hex32", "on", cmt, d)], None),
            ("the block loop's k is not C6_SITE's", [("c6_hex32", "on", badk, d)], None),
            ("a scan site labelled window in C6_SITE", [("c6_dig32", "on") + it[("c6_dig32", "on")]],
             dict(C6_SITE, c6_dig32=("window", 31))),
            ("the deny arm carries V's text", [("c6_hex32", "on", v, v)], None),
        ]
        for what, its, site in plants:
            b, _n = check_c6_texts(its, site)
            row(bool(b), "check_c6 plant %s: RED (%s)" % (what, b[0] if b else "no failure"))
    print("c6selftest: %d rows, %d failed" % (n, len(fails)))
    return 1 if fails else 0


def main():
    # line-buffered (review r79 R-1): a long command killed by its bound (the full selftest, ~90 min) still
    # leaves its finished rows in a redirected log; block buffering left U5's 3000 s run an empty file
    sys.stdout.reconfigure(line_buffering=True)
    cmds = {"plan": cmd_plan, "dry": cmd_dry, "run": cmd_run, "rerun": cmd_rerun, "rule": cmd_rule,
            "c3": cmd_c3, "selftest": cmd_selftest, "identity": cmd_identity, "c6selftest": cmd_c6selftest,
            "time": cmd_time, "c6decide": cmd_c6decide}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(__doc__)
        return 2
    why = pool_size_refusal(POOL_SIZE)
    if why:
        print("cards: REFUSED: %s" % why, file=sys.stderr)
        return 2
    return cmds[sys.argv[1]](sys.argv[2:]) or 0


if __name__ == "__main__":
    sys.exit(main())
