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
