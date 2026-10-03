#!/usr/bin/env python3
"""Writes the A2 form variants of one shipped ADAPTIVE artifact.

usage: mkforms.py CELL.a.c OUTDIR CELL
Produces OUTDIR/CELL.<v>.c for every v below. Each keeps `#include
"CELL.a.h"`, so CELL.a.h must sit beside them.

  ai   the shipped form with the prefilter forced inline (xcall.md §3's
       "forced-inline prefilter" column)
  f1   ../shape/mkbound.py f1: one prefilter call site in an outer seed loop,
       a call-free inner step loop bounded by step_end; init hoisted above
       the seed loop (pays it when the entry finds no candidate)
  f1i  f1 with its one prefilter site forced inline (lane a2build, round 2:
       round 1's f1 was the only form to recover possq on gcc, and the
       forced-inline prefilter (ai, f3i) the only change to beat the deny on
       the lka* short-search rows on both compilers; with one call site the
       inline duplicates nothing)
  f2   ../shape/mkbound.py f2: f1 with the init on the entry pass only
  f3   ../shape/mkb3.py: today's entry, the budget as a position bound, the
       re-seed in a cold in-loop branch (two call sites)
  f3i  f3 with the prefilter forced inline at both sites (xcall.md §4 A2's
       third starting point)
  f4   f2 with the entry pass told apart by `seed_from == search_from`
       (no sentinel read on the hot path) and the re-seed bookkeeping marked
       likely: a second spelling of "init on the entry pass only", since
       F2's x1.742 says gcc's answer depends on the spelling
All seven are semantically the shipped machine (same attempts, same re-seeds
under -e byte); bakeoff.sh checks every variant's answer hash against the
deny before it times anything.
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SHAPE = os.path.join(HERE, "..", "shape")
src, out, cell = sys.argv[1], sys.argv[2], sys.argv[3]
P = lambda v: os.path.join(out, f"{cell}.{v}.c")

def inline_prefilter(s):
    s2, n = re.subn(r'^static int rx_prefilter\(', 'static inline __attribute__((always_inline)) int rx_prefilter(', s, flags=re.M)
    if n < 1: sys.exit(f"mkforms: {src}: no `static int rx_prefilter(` definition to force inline")
    return s2

subprocess.run([sys.executable, os.path.join(SHAPE, "mkbound.py"), src, P("f1"), "f1"], check=True)
subprocess.run([sys.executable, os.path.join(SHAPE, "mkbound.py"), src, P("f2"), "f2"], check=True)
subprocess.run([sys.executable, os.path.join(SHAPE, "mkb3.py"), src, P("f3")], check=True)
open(P("ai"), "w").write(inline_prefilter(open(src).read()))
open(P("f3i"), "w").write(inline_prefilter(open(P("f3")).read()))
open(P("f1i"), "w").write(inline_prefilter(open(P("f1")).read()))
f2 = open(P("f2")).read()
a, b = "        if (reseed_steps == ~0u) {\n", "        if (__builtin_expect(seed_from != search_from, 1)) {\n"
if f2.count(a) != 1: sys.exit(f"mkforms: {P('f2')}: the entry-pass test is not where f4 expects it")
open(P("f4"), "w").write(f2.replace(a, b))
for v in ("ai", "f1", "f1i", "f2", "f3", "f3i", "f4"):
    if open(P(v)).read() == open(src).read(): sys.exit(f"mkforms: {cell}.{v} is identical to the shipped artifact")
