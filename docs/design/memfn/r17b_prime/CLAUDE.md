# docs/design/memfn/r17b_prime/ — R17-b′'s design-note instruments

Compile-only instruments behind `../r17b_prime.md` (lane r17bp, 2026-10-14).
Nothing here is timed, and nothing here is built or run by pcrec's `make`.
Every number they produce is a COUNT or a BYTE SIZE, read on the Linux dev
box (gcc 15.2), from the kit branch's tree at `lane/memfn-r17bp`'s base
(R17-b built, abi 77 on that branch).

- `census_shapes.py` — compiles every distinct corpus pattern (emit_sweep's
  own enumeration) at `--features all` on the `byte` and `byte-vm` arms with
  the tree's `build/pcrec`. For each artifact holding R17-b's stateful site,
  it reads the cover's term kinds off the emitted `<stem>__mask`. Prints the
  movers, the stateful sites per artifact, the R0 population (>= 2 RANGE terms)
  and the shape histogram.
  `python3 -I census_shapes.py <worktree>`.
- `twin_gen.py` — hand twins for SIZE ONLY (not answer-checked). It takes
  the vecspike slot's verbatim V0 (walk), V1 (R17-b `mask8_swar`) and A1
  (`mask64_avx2`) artifacts and builds WALK+V1, WALK+A1 and WALK+V1+A1
  sites with a per-call form byte and an N dispatch. These are the use-branch
  shape, not the note's §2 text; the bytes they add are of the same kind.
- `twin_sizes.sh` — runs `twin_gen.py` per cell, compiles every arm with
  `gcc -O2 -c` (`-mavx2` where an AVX2 form is present) and prints `.text`
  and `.rodata`+`.data`. `twin_sizes.sh SPIKE_BIN_DIR OUT_DIR`.
- `walk_helper_asm.py` — asks whether pcrec's table walk, moved out of
  the use and into a kit helper reached through the per-call struct,
  compiles to the same holding-function code as today's inline walk.
  `python3 -I walk_helper_asm.py SPIKE_BIN_DIR OUT_DIR`.
- `out/` — the three transcripts the note cites: `census_shapes.out`,
  `twin_sizes.out`, `walk_helper_asm.out`.

The spike sources are read read-only from
`worktrees/memfn-slot/spike1/bin/<cell>/{V0,V1,A1}/` (the vecspike slot's
build tree). Outputs go to a scratch directory the caller names (never
`/tmp`).

- `fdb1/` — step B1's instruments (lane fdb1, 2026-10-16): the reader-shadow
  and predicted-mover censuses, the traced-harness builder, and the
  COMMITTED predicted-mover manifest B4 is held to. Own CLAUDE.md.

Revision 2 of the note (lane r17bp3, 2026-10-14) adds no instrument and
re-runs none. It cites these transcripts as revision 1's evidence, which was
taken on the KIT branch (R17-b built); its step plan re-counts every
population against MAIN at each build step (`../r17b_prime.md` §3.5).
