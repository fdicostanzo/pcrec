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

## The delegated form (Frank 2026-11-13: "a kit call might be faster that asks [ab]+ how long?")

A single-byte-class body is a SPAN question: the longest run of bytes in the class from here, capped at the
max count. One kit call (the kit's shared "find the span" unit; D157: pcrec states the fact, the kit picks
the method) replaces the loop; then min-count check, give-back = p -= 1, last capture = [end-1, end).
Generalizes to fixed-width bodies that are a sequence of classes (a span of w-byte units). Span work is
UNSCHEDULED under [SPAN-ISEL] (Frank 2026-10-11, memory pcrec-memfn-span-unscheduled): record the census
count of corpus loops of this shape, no kit request until that row is scheduled.
- PREFERRED ROUTE (Frank 2026-11-13: "It might be find [^ab] as well which we have"): the run end is a FIND
  of the complement class ([^ab]) from p, bounded by min(subject end, p + max*w): an EXISTING kind of kit
  site with a new caller, so no dependency on the unscheduled [SPAN-ISEL]. pcrec states "first position not
  in {a,b}, within this bound"; whether the kit scans the wide complement or turns it into a run of the
  narrow set is the kit's method (D157).
