#!/usr/bin/env python3
"""docs/design/counterk_impl/probes/clamp_arith.py -- counterk_design.md S4.2's
clamp, PROVED ARITHMETICALLY before the code exists.

WHY THIS PROBE EXISTS. R25 E1 (blocker) found that S4.2's first specification --
a predicate over `vm_count_slots`'s running `repl` product -- does NOT discharge
K22. That product is ANCESTORS-ONLY and top-down, so on the {0,2} tower nothing
clamps until level 18, the product parks at 2^17 = PCREC_MAX_VM_NODES, and
depths 35/40 still refuse. The panel required the clamp respecified as an
ALGORITHM and its arithmetic proved by probe against PCREC_MAX_VM_NODES before
the design is accepted. This is that probe.

WHAT IT MODELS. The emitted-copy count of one quantifier under S3's shape, and
the product of those counts down a nesting path -- which is the quantity both
PCREC_MAX_VM_REPLICATION_PRODUCT and the Theta(2^d) `vm_count_slots` walk are
posed on. It is arithmetic over the SHAPE, not a compile: the pass does not
exist, so a compile would measure replication and answer nothing.

CONSERVATISM, DISCLOSED (design note S4.3): the pass cannot see
`vm_cursor_fits`, an emitter-internal predicate, so it treats EVERY nested
A_REP as replicating. The K22 tower's innermost `(?:a){0,2}` actually takes the
cursor rung and replicates nothing; it is modelled here as replicating. That
over-estimates the product, so the clamp fires slightly early -- costing
unrolling and never correctness, which is the direction an error here must
point.

Usage: clamp_arith.py            (reads the real constants out of limits.h)
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
LIMITS = os.path.join(ROOT, "src", "core", "limits.h")

# ---------------------------------------------------------------------------
# The bounds come out of limits.h, never from a copy of the number here: a
# constant transcribed into a check is a control sharing a source with the
# thing it controls, which is this project's most-recorded failure mode.
# ---------------------------------------------------------------------------
def read_limits(path):
    txt = open(path, encoding="utf-8").read()
    txt = re.sub(r"/\*.*?\*/", " ", txt, flags=re.S)          # strip comments
    vals = {}
    for name, rhs in re.findall(r"(PCREC_[A-Z0-9_]+)\s*=\s*([^,}]+)", txt):
        rhs = rhs.strip()
        if rhs.isdigit():
            vals[name] = int(rhs)
        elif rhs in vals:
            vals[name] = vals[rhs]                            # e.g. = PCREC_MAX_VM_NODES
    return vals

LIM = read_limits(LIMITS)
MAX_NODES = LIM["PCREC_MAX_VM_NODES"]
MAX_PRODUCT = LIM["PCREC_MAX_VM_REPLICATION_PRODUCT"]
MAX_COPIES = LIM["PCREC_MAX_VM_REPEAT_COPIES"]

# PCREC_DEFAULT_UNROLL_K does not exist yet (D47.2 names it; counter-K lands
# it). Declared here with that fact stated, and read from limits.h the moment
# it appears so this probe cannot drift from the shipped constant.
K_DEFAULT = LIM.get("PCREC_DEFAULT_UNROLL_K", 8)
K_FROM_HEADER = "PCREC_DEFAULT_UNROLL_K" in LIM

# ---------------------------------------------------------------------------
# S3's emitted-copy arithmetic. R25 E3: the trip guard is `ctr + K > NOPT`, so
# the loop is skipped only when K > NOPT -- at K == NOPT the loop RUNS. R25
# E14: NOPT == 0 emits nothing at all rather than an unreadable reset.
# ---------------------------------------------------------------------------
def copies_phase(count, K):
    if count == 0:
        return 0
    if K > count:
        return count                    # loop skipped: literal replication
    return K + (count % K)              # K copies in the trip + the residue tail

def copies(m, rmax, K):
    """Body copies one quantifier emits: the mandatory phase plus the optional
    phase. rmax < 0 is unbounded -- the mandatory prefix is counted and the
    star contributes its own single copy (design note S11 residual 1)."""
    if rmax < 0:
        return copies_phase(m, K) + 1
    return copies_phase(m, K) + copies_phase(rmax - m, K)

def copies_today(m, rmax):
    """What ships: `a->rmax < 0 ? a->rmin + 1 : a->rmax` (emit_vm.c:1003)."""
    return m + 1 if rmax < 0 else max(rmax, 1)

# ---------------------------------------------------------------------------
# THE CLAMP, as an algorithm. A post-order (BOTTOM-UP) pass over the A_REP
# nesting forest:
#
#   sub(v) = product of emitted-copy counts over v's subtree BELOW v
#          = max over immediate A_REP children c of ( copies(c, K_c) * sub(c) )
#          = 1 when v has no A_REP descendant
#
#   K_v = PCREC_DEFAULT_UNROLL_K   if sub(v) == 1
#         1                        otherwise
#
# In one sentence: UNROLL ONLY WHERE UNROLLING MULTIPLIES NOTHING. Unrolling
# costs multiplicatively down a nesting path, so it is taken at the innermost
# replicating level and nowhere above it. K_c is already decided when v is
# visited, which is what makes the pass bottom-up and what the ancestors-only
# `repl` product structurally could not do.
# ---------------------------------------------------------------------------
def clamp_path(levels):
    """levels: [(m, rmax)] outermost first. Returns (rows, total_product)."""
    rows, sub = [], 1
    for m, rmax in reversed(levels):
        K = K_DEFAULT if sub == 1 else 1
        c = copies(m, rmax, K)
        rows.append((m, rmax, K, c, sub))
        sub = c * sub
    rows.reverse()
    return rows, sub

def product_today(levels):
    p = 1
    for m, rmax in levels:
        p *= copies_today(m, rmax)
        if p > 10 ** 18:
            return None                 # astronomically over; report as such
    return p

# ---------------------------------------------------------------------------
# The cells: every S8.5 acceptance cell, the K22 towers at the depths the
# entry records, and the {1,2} tower the design note names as a RESIDUAL --
# included precisely because it must still refuse, and a probe that only shows
# its own successes is not evidence.
# ---------------------------------------------------------------------------
def tower(depth, m, rmax):
    return [(m, rmax)] * depth

CELLS = [
    # (label, levels, note)
    ("((a)|ab){0,4000}c",      [(0, 4000)],            "S8.5 cell 1, the endgame"),
    ("((a)|ab){4000}",         [(4000, 4000)],         "S8.5 cell 3, mandatory phase"),
    ("((a)|ab){4000,}",        [(4000, -1)],           "S8.5 cell 3, unbounded tail"),
    ("((a)|ab){8,4000}c",      [(8, 4000)],            "S8.5 cell 3, both phases"),
    ("((a)|ab){64}",           [(64, 64)],             "the measured cap boundary"),
    ("((a)|ab){65}",           [(65, 65)],             "one copy over the cap today"),
    ("((a)|b){0,3}c",          [(0, 3)],               "below K: must be replication"),
    ("((a)|b){0,8}c",          [(0, 8)],               "K == NOPT: loop RUNS (E3)"),
    ("((a)|b){0,9}c",          [(0, 9)],               "K < NOPT: loop runs, residue 1"),
    ("(a(b|c)?){0,4000}",      [(0, 4000), (0, 1)],    "nested {0,1}: must NOT over-clamp"),
    ("K22 tower d=18",         tower(18, 0, 2),        "refuses today at 0.72 s (node cap)"),
    ("K22 tower d=30",         tower(30, 0, 2),        "11.8 s before the interim guard"),
    ("K22 tower d=35",         tower(35, 0, 2),        "S8.5 cell 2: hung; must COMPILE"),
    ("K22 tower d=40",         tower(40, 0, 2),        "S8.5 cell 2: hung; must COMPILE"),
    ("{1,2} tower d=20",       tower(20, 1, 2),        "S6 RESIDUAL: must still refuse"),
    ("{1,2} tower d=40",       tower(40, 1, 2),        "S6 RESIDUAL: must still refuse"),
]

def main():
    print("== clamp_arith: counterk_design.md S4.2, proved before the code ==")
    print("limits.h            %s" % LIMITS)
    print("PCREC_MAX_VM_NODES  %d" % MAX_NODES)
    print("..REPLICATION_PRODUCT %d" % MAX_PRODUCT)
    print("..MAX_VM_REPEAT_COPIES %d" % MAX_COPIES)
    print("K_DEFAULT           %d (%s)" % (
        K_DEFAULT,
        "read from limits.h" if K_FROM_HEADER
        else "NOT YET IN limits.h -- D47.2 names it; counter-K lands it"))
    print()
    print("%-22s %-13s %-13s %-9s %s" % (
        "cell", "product TODAY", "product CLAMP", "verdict", "note"))
    bad = 0
    for label, levels, note in CELLS:
        rows, prod = clamp_path(levels)
        today = product_today(levels)
        today_s = "over 1e18" if today is None else str(today)
        refused_today = today is None or today > MAX_PRODUCT or \
            any(copies_today(m, r) > MAX_COPIES for m, r in levels)
        refused_clamp = prod > MAX_PRODUCT
        verdict = "REFUSES" if refused_clamp else "compiles"
        flag = ""
        if refused_today and not refused_clamp:
            flag = "  <- counter-K WINS this cell"
        elif refused_clamp:
            flag = "  <- still refused"
        print("%-22s %-13s %-13s %-9s %s%s" % (
            label, today_s, prod, verdict, note, flag))
        # A cell whose note says it must compile and does not is a hard failure.
        if "must COMPILE" in note and refused_clamp:
            bad += 1
        if "must still refuse" in note and not refused_clamp:
            bad += 1
        if "must be replication" in note and prod != levels[0][1]:
            bad += 1

    print()
    print("-- the tower, level by level: where the clamp actually engages --")
    rows, prod = clamp_path(tower(35, 0, 2))
    print("%-8s %-4s %-8s %s" % ("level", "K", "copies", "product below"))
    for i, (m, rmax, K, c, sub) in enumerate(rows[:3], 1):
        print("%-8d %-4d %-8d %d" % (i, K, c, sub))
    print("...      (levels 4..33 identical: K=1, copies=1)")
    for i, (m, rmax, K, c, sub) in enumerate(rows[-2:], len(rows) - 1):
        print("%-8d %-4d %-8d %d" % (i, K, c, sub))
    print()
    print("The innermost replicating level takes K=%d; every level above it is" % K_DEFAULT)
    print("clamped to K=1 and contributes a factor of ONE, so the tower's whole")
    print("product is %d at any depth. That is the property the ancestors-only" % prod)
    print("product could not deliver, and it needs a bottom-up pass to compute.")

    if bad:
        print("\nFAILED: %d cell(s) did not behave as their note requires" % bad)
        return 1
    print("\nAll cells behave as their notes require.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
