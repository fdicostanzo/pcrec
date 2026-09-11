#!/usr/bin/env python3
"""proptest.py — DELIVERABLE (4): the property test the general-form
bottleneck makes possible.

THE EXPLOIT.  CONSTITUTIONAL CONSTRAINT 1 says the kit's input is the bare
set and the dial derives the written form from SET STRUCTURE ALONE.  That is
usually argued as a design virtue.  It is also a TESTING LEVER, and a sharp
one: if the matcher is a function of the set and of nothing else, then

    * the test population does not have to be reachable from any pattern.
      Arbitrary sets are legitimate inputs, so the generator can produce
      structures no regex would ever build — and it is exactly those that
      break a form's preconditions.
    * every COMPOSITION of sets is an oracle for free.  Membership commutes
      with union, intersection, complement and difference, so for any sets
      A and B the kit's matcher for `A u B` must agree, on every code point,
      with `kit(A) or kit(B)` — where the left side went through discovery
      ONCE on a merged set and the right side went through it TWICE on
      unmerged ones.  No external oracle is consulted, and a bug in the kit
      cannot hide, because it would have to corrupt both sides identically
      through two different sectionings.

This is the check a provenance-TAGGED design could not write.  If the form
depended on where the set came from, `A u B` and `kit(A) or kit(B)` would be
allowed to differ, and the identity would not be a law to test against.

Structures generated (each a deliberate attack on one kit member):
  random      uniform random intervals over the whole code-point space
  sparse      many singletons, no two adjacent           -> RANGES/BSEARCH
  dense       few very wide intervals                    -> ALL/PAGE64
  comb        every other code point over a run          -> the parity CUBE
  fold        {x, x^bit} pairs for a random single bit   -> the one-cube fold
  orbit       complete orbits under 2-3 free bits        -> multi-free-bit cube
  boundary    intervals pinned to 64/256/0x10000 edges   -> page/width seams
  pathologic  alternating 1-wide members at 65-apart     -> defeats PAGE64
"""

import argparse
import os
import random
import subprocess
import sys
import time

import emit
import section

HERE = os.path.dirname(os.path.abspath(__file__))
CC = os.environ.get("CC", "gcc-16")
MAX_CP = 0x10FFFF

MAIN = r"""
#include <stdio.h>
int main(void)
{
    unsigned long bad = 0;
    for (unsigned cp = 0; cp <= 0x10FFFFu; cp++) {
        int l = LHS(cp) ? 1 : 0, r = RHS(cp) ? 1 : 0;
        if (l != r) {
            if (bad < 4) fprintf(stderr, "MISMATCH cp=U+%04X lhs=%d rhs=%d\n",
                                 cp, l, r);
            bad++;
        }
    }
    printf("%lu\n", bad);
    return bad ? 1 : 0;
}
"""


# ------------------------------------------------------------- generators

def norm(members_or_iv):
    """Sorted, disjoint, NON-ADJACENT — pcrec's own cpset invariant.  The kit
    is entitled to assume it, so the generator must establish it."""
    iv = sorted(members_or_iv)
    out = []
    for l, h in iv:
        if out and l <= out[-1][1] + 1:
            out[-1] = (out[-1][0], max(out[-1][1], h))
        else:
            out.append((l, h))
    return [(l, h) for l, h in out]


def g_random(rng, n):
    return norm([(lambda a: (a, min(MAX_CP, a + rng.randint(0, 300))))(
        rng.randint(0, MAX_CP)) for _ in range(n)])


def g_sparse(rng, n):
    pts = rng.sample(range(0, MAX_CP, 2), min(n, 4000))
    return norm([(p, p) for p in pts])


def g_dense(rng, n):
    out = []
    pos = rng.randint(0, 1000)
    for _ in range(max(1, n // 40)):
        w = rng.randint(1000, 60000)
        out.append((pos, min(MAX_CP, pos + w)))
        pos += w + rng.randint(2, 500)
        if pos >= MAX_CP:
            break
    return norm(out)


def g_comb(rng, n):
    base = rng.randrange(0, 0x10000, 2)
    return norm([(base + 2 * i, base + 2 * i) for i in range(min(n, 2000))])


def g_fold(rng, n):
    bit = 1 << rng.randint(0, 5)
    out = []
    for _ in range(min(n, 2000)):
        x = rng.randint(0, 0xFFFF) & ~bit
        out += [(x, x), (x | bit, x | bit)]
    return norm(out)


def g_orbit(rng, n):
    free = rng.sample(range(0, 7), rng.randint(2, 3))
    out = []
    for _ in range(max(1, min(n, 400))):
        base = rng.randint(0, 0xFFFF)
        for m in range(1 << len(free)):
            x = base
            for b, f in enumerate(free):
                if (m >> b) & 1:
                    x |= 1 << f
                else:
                    x &= ~(1 << f)
            out.append((x, x))
    return norm(out)


def g_boundary(rng, n):
    edges = [0, 63, 64, 65, 127, 128, 255, 256, 0xFFFF, 0x10000, 0x10FFFF,
             0xD7FF, 0xE000]
    out = []
    for _ in range(min(n, 500)):
        e = rng.choice(edges)
        d = rng.randint(-2, 2)
        a = max(0, min(MAX_CP, e + d))
        out.append((a, min(MAX_CP, a + rng.randint(0, 3))))
    return norm(out)


def g_pathologic(rng, n):
    """One member every 65 code points: every 64-wide page is distinct and
    non-empty, so PAGE64's leaf dedup buys nothing and its index is as long
    as the span.  The point is to make a form's own best case impossible."""
    base = rng.randint(0, 1000)
    return norm([(base + 65 * i, base + 65 * i) for i in range(min(n, 3000))])


GENS = dict(random=g_random, sparse=g_sparse, dense=g_dense, comb=g_comb,
            fold=g_fold, orbit=g_orbit, boundary=g_boundary,
            pathologic=g_pathologic)


# ----------------------------------------------------------- set algebra

def s_union(a, b):
    return norm(list(a) + list(b))


def s_complement(a):
    out, pos = [], 0
    for l, h in a:
        if l > pos:
            out.append((pos, l - 1))
        pos = h + 1
    if pos <= MAX_CP:
        out.append((pos, MAX_CP))
    return out


def s_inter(a, b):
    return s_complement(s_union(s_complement(a), s_complement(b)))


def s_diff(a, b):
    return s_inter(a, s_complement(b))


# ---------------------------------------------------------------- driver

def build_and_run(outdir, tag, lhs_src, rhs_expr, extra_src):
    cpath = os.path.join(outdir, tag + ".c")
    with open(cpath, "w") as f:
        f.write(emit.PRELUDE)
        f.write(extra_src)
        f.write(lhs_src)
        f.write("\n#define RHS(cp) (%s)\n" % rhs_expr)
        f.write(MAIN)
    bpath = os.path.join(outdir, tag)
    r = subprocess.run([CC, "-O1", "-std=gnu11", "-w", cpath, "-o", bpath],
                       capture_output=True, text=True)
    if r.returncode:
        return None, "compile: " + (r.stderr.strip().splitlines() or [""])[0]
    r = subprocess.run([bpath], capture_output=True, text=True)
    return (r.returncode == 0, r.stdout.strip()), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--cases", type=int, default=40)
    ap.add_argument("--lams", default="0,16,256")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    lams = [float(x) for x in args.lams.split(",")]
    outdir = args.out or os.path.join(HERE, "build", "prop")
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)

    rows = []
    npass = nfail = 0
    t0 = time.time()
    for c in range(args.cases):
        gname = sorted(GENS)[c % len(GENS)]
        hname = sorted(GENS)[(c * 3 + 1) % len(GENS)]
        A = GENS[gname](rng, rng.randint(2, 600))
        B = GENS[hname](rng, rng.randint(2, 600))
        if not A or not B:
            continue
        for opname, setop, expr in (
                ("union", s_union, "(KA(cp) || KB(cp))"),
                ("inter", s_inter, "(KA(cp) && KB(cp))"),
                ("diff", s_diff, "(KA(cp) && !KB(cp))"),
                ("compl", lambda a, _b: s_complement(a), "(!KA(cp))")):
            C = setop(A, B)
            if not C:
                continue
            for lam in lams:
                # LHS: discovery run ONCE on the composed set
                sc, _, _, fo = section.partition_c(C, lam)
                lhs, _ = emit.emit("LHS", C, sc, fo, static=True)
                # RHS: discovery run SEPARATELY on each operand
                sa, _, _, fa = section.partition_c(A, lam)
                ka, _ = emit.emit("KA", A, sa, fa, static=True)
                sb, _, _, fb = section.partition_c(B, lam)
                kb, _ = emit.emit("KB", B, sb, fb, static=True)
                tag = "p%03d_%s_l%g" % (c, opname, lam)
                res, err = build_and_run(outdir, tag, lhs, expr, ka + kb)
                if err:
                    rows.append((tag, gname, hname, opname, lam, len(A),
                                 len(B), len(C), "BUILDFAIL", err))
                    nfail += 1
                    continue
                ok, bad = res
                rows.append((tag, gname, hname, opname, lam, len(A), len(B),
                             len(C), "PASS" if ok else "FAIL", bad))
                if ok:
                    npass += 1
                else:
                    nfail += 1
                    sys.stderr.write("PROPERTY FAIL %s: %s mismatches\n"
                                     % (tag, bad))

    path = os.path.join(HERE, "results", "proptest.tsv")
    with open(path, "w") as out:
        out.write("# seed=%d cases=%d lams=%s cc=%s elapsed_s=%.1f date=%s\n"
                  % (args.seed, args.cases, args.lams, CC, time.time() - t0,
                     time.strftime("%Y-%m-%dT%H:%M:%S")))
        out.write("# EVERY row compares %d code points (0..0x10FFFF)\n"
                  % (MAX_CP + 1))
        out.write("# PASS=%d FAIL=%d\n" % (npass, nfail))
        out.write("case\tgenA\tgenB\top\tlam\tnA\tnB\tnC\tverdict\tdetail\n")
        for r in rows:
            out.write("\t".join(str(x) for x in r) + "\n")
    print("wrote %s: PASS=%d FAIL=%d (%d code points each)"
          % (path, npass, nfail, MAX_CP + 1))
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
