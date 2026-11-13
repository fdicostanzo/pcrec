# [LOOP-FIXW] plan row body

Filed 2026-11-13 from Frank's question on `(a|b){1,30000}` (the S2 cloud red that turned out not to be a
regression: ~12.5 s to compile on main at both engines, a separate pre-engine analysis anomaly).

## The idea (Frank)

1. A loop whose body has a FIXED WIDTH w needs no per-iteration frames: count = (p - start) / w; give back
   one iteration = p -= w; bounds = pointer comparisons (p - start >= min*w).
2. Captures need not be written per iteration: the last iteration's capture is [p - w, p), set once at loop
   exit and again on each give-back (the same subtraction). For an inner group (`((a)|b)`) which branch
   matched is decidable from the last w bytes alone. PCRE2 reports only the last iteration's capture, so
   the other writes are unobservable.

## What exists

The reverse-deterministic rung (RUNG-SELECT, built 2026-08-16; [ENG-BREP]): src/opt/revdet.c decides
unique-iteration bodies; emit_vm.c's vm_revdet_rep scans forward with O(1) frames, retreats by stepping
boundaries backward through the reversed body, and derives the last iteration's capture by that walk.
Fixed width is the special case where the backward walk is a subtraction. Build it AS that case of the
rung (memory pcrec-general-mechanisms-not-special-cases), never a parallel loop mechanism.

## Survey scope (Frank: "look at other general loop ideas related")

Each idea gets a census line and a trigger (D77), not a build:
- fixed-width bodies in the VM (above), and on the DFA side (counted states as DATA tables);
- bodies of BOUNDED width range [wmin, wmax] (count bounds from the span; retreat by a small search);
- counted repeats whose count only matters at the bounds ({n,} with large n: count to n, then free);
- lazy loops with the same structure (extend by +w instead of a frame);
- nested counted repeats (K22 product-of-factors guard; counter-K);
- loops whose captures are never read by the caller (capture-erased forms);
- possessive/atomic loops and disjoint-follow possessification (existing) as the commit side;
- the compile-time cost of huge counts in pre-engine analysis (the 12.5 s anomaly: where it goes; facts,
  required-run walk, size rung), so large repeats compile in time linear in the pattern, not the count.

## Order

Census first; the compile-time anomaly is measured within it. Waits for the current set (S2) to land.
