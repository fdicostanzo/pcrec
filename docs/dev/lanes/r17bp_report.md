# r17bp — the R17-b′ design note (D166)

Lane r17bp, 2026-10-14, for the memfn kit manager. Branch
`lane/memfn-r17bp`, cut from `lane/memfn-r17` at `9775409fc`. DESIGN ONLY:
nothing under `src/`, `memfn/src/`, `tests/` or `lib/` changed, and no
timing was run. The deliverable is `docs/design/memfn/r17b_prime.md`. Its
compile-only instruments are in `docs/design/memfn/r17b_prime/`.

## What was delivered

- **The note.** It covers:
  - the candidate-finder table as declared data (§1), with the stop column
    and the listing;
  - the emitted N dispatch's C text for WALK+V1, WALK+A1 and WALK+V1+A1,
    its placement, its pay rule, and its literals from the set (§2);
  - the measurement table with 18 families keyed (quantity, form, site kind,
    shape) in walk-byte units, grid1 provenance and three ABSENT entries
    (§3);
  - the contract's missing facts and the set's channel (§4);
  - bytes, the abi event, stamps, spec hunks and size (§5);
  - four denies, G1/G2, the every-set answer test and 12 sabotage rows (§6);
  - acceptance and predictions (§7);
  - the R17-b″ seam (§8);
  - Q-R17P-1..8 (§9), the standing questions (§10), F1-F9 (§11) and the
    charter-vs-committed table (§12).
- **Instruments.** Their transcripts are in `r17b_prime/out/`:
  - `census_shapes.py`: the cover shape of every R17-b mover. Byte arm:
    996 movers, 219 R0. VM arm: 2,910 movers, 243 R0. Every mover has
    exactly one stateful site.
  - `twin_sizes.sh` / `twin_gen.py`: object sizes of multi-form hand twins.
    WALK+V1 is +320-416 B per site over R17-b; three forms are +1.9-3.4 KB
    over main.
  - `walk_helper_asm.py`: the walk reached through a helper is NOT
    identical to the inline walk (−3..+14 instructions on 6 of 6 cells).

## Findings that change what a build would do

1. Under D166's one-run rule the dispatch is never emitted on grid1. The
   dispatch-cost quantities (M16-M18) are absent, so R17-b′ on today's data
   is R0 + R7. The first embedded set needs one new slot (Q-R17P-7).
2. R17-b′ removes 5.5% of ALPHA's OFF-layer loss ns. The residual 1.17 ms
   (dense find-all, dfa-hat prose) is not reachable by any R17-b′ row, so
   D162 add. 1's no-loss bench gate cannot pass SIMD-off (Q-R17P-4).
3. dfa-hat prose loses at g = 10.2 B, above every measured g\*, so even E's
   R6 would admit V1 there. The missing knowledge is near-hit depth (F7).
4. The floor rule plus D155 mean a W64 arm needs the SIMD-off text to route
   through a selector. So R0 sites carry a scaffold at SIMD-off, or get no
   W64 at either layer (F5).
5. The brief's "forms-per-site in `MEMFN_FORMS`" conflicts with the ruled
   spec (Q-R17P-1).

## Validation

Docs and instruments only. `make test-spec-history` was run on the
worktree; the verdict is in the handback message. No `make test`, no
timing, nothing owed.
