# tests/resource — what compiling a pattern COSTS

Every other suite in this tree asserts something about the LANGUAGE: what a
pattern matches, which diagnostic it draws, which engine it routes to. This one
asserts something about the PROCESS — peak memory, wall and CPU time, and the
manner of failure — because K7 was a bug that no assertion about the language
could see.

## Files

- **run_resource_tests.sh** — the [M4.7b] K7 pin, in three sections:

  1. **Bounded outcome.** Eleven large-bounded-repeat shapes (K7's own repro
     list plus multi-byte, class and choice-point bodies) each compile or draw
     a diagnostic, under a peak-tree-RSS ceiling and wall/CPU budgets enforced
     by `scripts/watchdog`. A watchdog kill (122/123/124), an abort (134) or a
     SIGKILL (137) is a FAILURE — those are the four ways K7 used to end.
     WHICH shapes compile and which refuse is deliberately NOT asserted: that
     boundary is `PCREC_MAX_SUBSET_ELEMS`'s to move, and pinning it here would
     make this file a control calibrated against the thing it controls.

  2. **A failed allocation is diagnosed, not aborted.** Four compiles under a
     40 MB (25 MB for the last) `ulimit -v`, which makes malloc genuinely
     return NULL partway through. Each must exit 1 with a diagnostic, never
     134. This is a positive control for `ctx_nomem()` and the seven
     allocation sites that route to it, and it is a SEPARATE section for a
     reason: with the section-1 budget in place, those shapes are refused by
     the budget long before any malloc fails, so section 1 cannot reach the
     allocator paths at all. Revert `ctx_nomem` to `abort()` and section 2
     fails while section 1 stays green.

  3. **The refusal's identity.** `a{0,65535}` must refuse inside the existing
     "too complex for the DFA engine" family AND name the subset construction,
     so a reader knows which of the two DFA bounds they hit; and an
     exponential-blowup pattern must still reach the state-COUNT cap, which
     is how this file notices if the new bound ever took the old one's
     customers away.

## [TT-10] the load guard (2026-08-25)

Section 1's cells assert a CPU/wall/RSS ceiling, and two of them
(`[a-z]{0,30000}`, `(a|b){0,30000}`) were measured going RED under real box
contention even though `K7_CPU` is already CPU-accounted through
`scripts/watchdog -c` — CPU-time ACCOUNTING itself inflates under real
contention, not merely wall stretching around fixed work (K31 addendum,
`docs/dev/plan.md`). `tests/lib/load_guard.sh` (its own header carries the
measurement and the threshold justification) is sourced here: a 123 (CPU
exceeded) or 124 (wall exceeded) outcome is reclassified **INCONCLUSIVE** —
a third, separately-counted outcome, never PASS, never FAIL — when the
1-minute load average / `nproc` exceeds `LOAD_GUARD_RATIO` (default 2.0) at
the moment that specific cell's watchdog kill fires. Every other outcome (0,
1, 122, 134, 137) is unaffected, since none of them can be produced by CPU
inflation. D45-style budgets (`K7_CPU`/`K7_MEM`/`K7_SECS`) are unchanged by
this. Validated solo (19/0/0, unchanged) and under an 8-way `yes`-spinner
artificial load (green-or-INCONCLUSIVE, never FAIL — see
`docs/dev/dev_journal.md` for the run's numbers).

## Why this suite is not on the sanitizer axes

`make ubsan`/`asan`/`lint` do not run it, by design. Section 2 needs
`ulimit -v` to force a real allocation failure, and an ASan build reserves tens
of terabytes of address space at startup — every case would die before `main`.
Section 1's memory ceiling has the mirror-image problem: instrumentation
legitimately multiplies footprint, so a ceiling calibrated on the plain axis
either flakes under ASan or is loosened until it asserts nothing. Resource
promises are measured on the axis they are made on. The `test-resource` target
in the Makefile carries the same note.

## Env

`PCREC` (default `build/pcrec`), `K7_MEM` (default `512m`), `K7_SECS`
(default `60`), `K7_CPU` (default `20`). Same revisit-when as D45's budgets: a
LEGITIMATE case measured needing more raises the default with the measurement
recorded, never silently.

Maintenance: update this file when files are added/removed or their roles change.

## [OPT-4.1] the size-rung cell became a PAIR (2026-08-30)

`(a|b){0,30000}` was the tree's ONE witness that ruling B's size rung ships an
artifact where the exact one is refused. It is also NULLABLE — its collapsed
language `(a|b)*` matches the empty string at every position — so under
[OPT-4.1] the rescue is DECLINED there and the artifact ships with NO prefilter
instead, which is smaller still and rescues the compile just as well.

**SO THE ROW IS TWO CELLS NOW, AND EACH IS THE OTHER'S CONTROL.**
`(a|b){0,30000}` must compile small with `RX_VM_PREFILTER "none"` and no
language macro; `(a|b){1,30000}` — the same pattern one character over, NOT
nullable — must still take the rung and stamp `_LANG_WHY "size cap retry,
exact N > cap"`. Neither direction is safe alone: without the twin, a compiler
that had stopped taking the size rung at all would leave the nullable cell
green (no prefilter is exactly what it asserts) while every oversize
collapsible pattern started refusing; without the nullable cell, a compiler
that had stopped declining would leave the twin green while shipping a scan
that can never dismiss a position.

**AND THE TWIN IS THE `size cap retry` STAMP VALUE'S ONLY WITNESS IN THE
TREE** (K35). No corpus pattern reaches either rung at the default, and
pcrec-bench reaches neither across 74 forms (its O-10 ask (v)); the other two
`size_moved` rows are DFA-engine artifacts, which take no VM prefilter
decision at all. If the twin is ever removed, that bucket becomes tested only
by `make check`.

The nullable cell's own contract is that nothing which compiles today stops
compiling: dropping the prefilter is strictly smaller than collapsing it, so
the rung still rescues (`docs/spec/limits.md` §3.3 states it caller-side).

## [LIM-1] the pair's own verdict moved from LANG_WHY's prefix to ENGINE_SEL (2026-08-30)

D90's fold-in gave the SIZE rung's own SUCCESS a distinct `RX_ENGINE_SEL`
value, `"size-cap-retry"` — before this it stamped `"selected"`,
indistinguishable from a compile that never touched any cap
(`docs/spec/match_api.md` §6.3's own value table names the gap this closed).
`(a|b){1,30000}`'s cell is that value's STANDING WITNESS: nothing else in the
tree reaches `RX_ENGINE_SEL "size-cap-retry"` (`tests/codegen/
run_prefilter_collapse.sh` §7b's own `sel_witness size-cap-retry` reuses this
exact pattern rather than inventing a second one, per this pair's own
one-witness-two-readers precedent). The verdict now reads `RX_ENGINE_SEL`
directly rather than a `${szwhy#size cap retry}` string-prefix test; `LANG_WHY`
is still read and still reported, for the byte comparison it alone carries.
`(a|b){0,30000}`'s nullable twin gained the matching check —
`RX_ENGINE_SEL "declined-nullable"` — since [LIM-1] widened that value's own
reach from the [SEL-1] rung alone to both rungs (`src/opt/select_engine.c`'s
own comment at the fit site has the derivation).
