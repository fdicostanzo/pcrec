# docs/design/dec_fallback/reach/ — the row-reach PROTOTYPE (rev 2)

`../../dec_fallback.md` rev 2 §4.3a's evidence (lane decfbrev2, 2026-10-08,
main `42ab7c25`, src identical to rev 1's `31a9ae4c`). A PROTOTYPE of the
`row_reach` instrument B1 builds for real: B1 reads the fallback trace, which
does not exist before B1, so this reads stderr probes in a scratch COPY of the
tree (decfb0's method, `../../decision_families/decfb0/`). Design evidence, not
a check: nothing here is run by `make`, and nothing under `src/` is modified.

- `build_reach.py` — copies src/ lib/ cli/ memfn/ to SCRATCH/tree, patches
  the copy's `compile.c` and `select_engine.c` with `DECFB` probes (attempt
  header, arrival labels incl. `pf.forcing`/`failed_nomem`, the branch taken,
  every attempt's admission inputs and verdict, the collapse gate), and builds
  one compiler per limit variant (`plain`, `lowsize`, `lowdfa`, `lowboth`,
  `lowthr`).
- `reach.py` — compiles decfb0's population (every distinct corpus block, its
  own flags/features/encoding/engine) plus `witnesses.tsv` under one variant
  and one flag ARM (14 arms), records stamps + probes + `--emit-ir`'s
  prefilter value, and on `plain/base` asserts the probed stdout/rc identical
  to the unprobed `build/pcrec` (0 differ at `42ab7c25`). Corpus patterns are
  DECODED (emit_sweep.py's decoder) and passed as raw `--pattern` bytes:
  `--pattern-esc` is ignored by `--emit-ir` (rev 2 F-B5).
- `witnesses.tsv` — the constructed witnesses (name, pattern, flags,
  features, encoding).
- `analyse.py` — the reach table (`out/reach.tsv`, `out/sequences.tsv`) and
  the checks of the design's tables against probes and stamps, computed from
  the rev-2 row lists (no shared code with src/): T2 verdict and listing, T3
  PFLW, the attribution walk vs `ENGINE_SEL`, the attempt bound, the
  at-most-once rule, §1.9's run-time invariants, and the
  [DEC-COLLAPSE-WASTE] three-way split. `out/analyse.txt` is its output.
- `summarize.py` — `out/reach.tsv` -> `out/reach.md`, the row x variant table.

Reproduce (light, ~12 min at -j6 for all 60 variant x arm runs): from the
worktree root, `python3 .../build_reach.py build/decfbrev2`, then
`reach.py ROOT build/decfbrev2 VARIANT ARM` per cell (lowthr: base, vm,
no-st, unroll4 only), then `analyse.py build/decfbrev2 OUT` and
`summarize.py OUT`. Scratch stays under the worktree's `build/`.

Maintenance: update this file when files are added/removed or their roles
change.
