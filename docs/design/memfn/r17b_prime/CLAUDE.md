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
- `fdb2/` — step B2's instruments (lanes fdb2/fdb2fix, 2026-10-16): the
  routed-record census, the REGENERATED predicted-mover manifest B4 is held
  to (superseding fdb1's, which stays unedited), and `proposed/`, the diffs
  drafted for main. Own CLAUDE.md.
- `b3a/` — lane b3a's instruments (R17-b′ B3a, 2026-10-17): `pick_census.py`
  (KW-8 over corpus, bench and rwquest, three arms, `--floors
  pick_floors.tsv`, whose boolean picks are floored on both values of
  `differs` since lane b3afix; `--nonascii` for the caseless UTF-8 arm),
  `pr11_census.py` (the PR-11 control over every count-collapsed hybrid,
  `ok` floored per population by `pr11_floors.tsv`, hand subjects for the
  artifacts no corpus text reaches), `sabotage/` (S1093..S1102 +
  `run_skb3a.sh`, each
  plant solo in a `git archive` copy), `proposed/` (main-side diffs, never
  applied in place: `deleg_entry.diff`, `c17_use_points.diff`,
  `c10_presence.diff`, applied in that order) and `out/` (the census
  transcripts). Report: `docs/dev/lanes/b3a_report.md`.
- `b3b/` — lane b3b's instruments (R17-b′ B3b, 2026-10-18): the declared
  registry-dump delta and its two-way check, the KW-8 census on the
  kit-sourced proof with the ROUTED records (`pick_census_b3b.py`), the
  routed-record census (`routed_census_b3b.py`), their floors and `out/`.
  Own CLAUDE.md. The main-side proposed diff and the heavy chain live under
  `docs/dev/lanes/b3b/`. Report: `docs/dev/lanes/b3b_report.md`.

- `grid2read/` — the reading of the zen4-grid2 timing slot (lane grid2read,
  2026-10-16, analysis only): `grid2read.py`/`grload2.py`, the full output
  `analysis.txt`, the proposed `kit-grid@2` rows `keys.tsv`, and `SHA256SUMS`
  of the 18 slot files read. Own CLAUDE.md; the report is
  `docs/dev/lanes/grid2read_report.md`.

Revision 4 of the note (lane rev4, 2026-10-20) adds no instrument and re-runs
none. It reads `grid2read/` (the slot's reading and its PROPOSED `keys.tsv`) as
B4's evidence. `fdb2/predicted_movers_B4.tsv` is STALE under revision 4's table:
item 3a's shapes now route and R0 is retired. B4 must regenerate it, which is OWED
in the note's §3.1a item 4.
