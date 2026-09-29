# tests/clskit — [CLS-TREE] S1: the class-matcher kit, checked before anything calls it

`src/gen/clskit.c` is the kit: the per-section leaf forms, the sectioning DP
(the design's `K`), the whole-set tables `P3`/`P2`/`B1`, the shared byte
atom table, and D131's `--tune` class-form selection. At S1 NO EMITTER CALLS
IT (docs/design/cls_tree_design.md §6), so no `.rxt` cell, identity gate or
answer anywhere else in the tree can see it. This section is its only net.
`make test-clskit`, in `TEST_SECTIONS`. It takes about 3-4 minutes on the Mac
at `PROCS=4`, most of it in the study's Python DP (crosscheck.py).

## Files

- `ref/`: a FROZEN, provenance-headed copy of the six `studies/
  cls_tree_study/` modules `crosscheck.py`/`populations.py` import
  (`kit.py`, `section.py`, `wholeset.py`, `bench_bytes.py`, `clsets.py`,
  `proptest.py`) plus their two transitive imports (`emit.py`,
  `loadgate.py` — module-level `import`s inside `bench_bytes.py`/
  `proptest.py`, so importing the six without them fails at import time),
  and `ref/results/byteclasses.tsv` (`clsets.byteclasses()`'s own data
  file). `docs/CLAUDE.md`: `studies/` is "never built or tested by
  pcrec's make" — `tests/clskit/` first imported those six live and that
  was a scope violation, fixed here (lane clss1b, 2026-09-29). Each file
  carries a header naming its source path and the commit it was copied
  at; `clsets.py`'s own note is the one behavioural deviation (its
  `HERE`-relative path arithmetic re-derived for one extra directory
  level). Edit `ref/` with the same care as a test oracle — an edit here
  changes what `make test-clskit` compares against — and re-copy by hand
  from `studies/cls_tree_study/` (never patch a `ref/` file to read
  differently from its source) to pick up a real study change.
- `run_clskit_tests.sh`: the section. It has three parts, each with its own
  PASS/FAIL line.
  1. THE DIFFERENTIAL. Every emitted form is compiled under `GENCFLAGS`
     (`gen_cc`) and run (`gen_run`). Each is compared against a reference on
     all 1,114,112 code points, plus three beyond the code space. The
     composition law is checked for `K4` and `P3` on every proptest case.
  2. THE CENSUS. Every leaf form (`ALL`..`BSEARCH`) and every whole-set form
     (`K`, `P3`, `P2`, `B1`, `ATOM`) must have been EMITTED at least once.
     A form nothing reached would otherwise read as a form nothing broke
     (K35).
  3. THE CROSS-CHECK against the study.
  Summary: `checks passed:`/`checks failed:`. The mech arm `clskit` scrapes
  those lines.
- `populations.py`: writes the population file. The four populations are:
  - the 312 `uprops` sets;
  - the K53 twelve;
  - the 41 corpus byte classes;
  - the study's proptest compositions (seed 1, 40 cases, the study's own
    generators and draw order).
  It reads them through `ref/clsets.py`/`ref/proptest.py` — the same
  frozen copy `crosscheck.py` imports — so the kit and the study cannot be
  looking at different sets. Writes one file.
- `clskit_driver.c`: linked against `libpcrec.a` (`unit_build`). Its `emit`
  mode writes one checker `.c` per chunk plus the census. Its `dump` mode
  prints `SEC`/`WHOLE`/`ATOMS`/`SEL`/`ROW` lines for the cross-check.
  **The reference in each checker is plain interval arrays written by THIS
  file from the population file.** No line of `clskit.c` produces it.
- `checker_main.inc`: the checker's `main()`, included at the end of every
  chunk.
- `crosscheck.py`: recomputes each decision with the frozen reference code
  in `ref/`: `section.partition` at CUBES tier 1, `wholeset.PageW2/PageW3`,
  and `bench_bytes.atom_partition`. The selection TABLE is restated
  independently from D131 (NO atom row — item 6's atom table is an
  artifact-level choice, not a per-set `ROWS` outcome), and `clskit.c`'s
  printed `ROW` listing is held to that restatement. `KIT_DISP_BYTES`
  restates clskit.c `PLACE.kit_disp_bytes` (D131 addendum 1's fitted
  dispatch/prologue term), added to K's bytes wherever the restated
  predicates compare K against another form — never to the DP's own
  sectioning bytes.

## Things to know before changing anything here

- **Ties are counted, not failed.** The study's DP is floating point. The
  kit's DP is Q16 fixed point, because a selection must be bit-reproducible
  across boxes. Two sectionings with the same objective to 1e-6 under the
  study's own pricing are an exact tie, broken differently by float rounding
  and by loop order. They print as `TIE` lines. 3 of 1,686 sectionings are
  ties at landing, all on proptest sets, all BSEARCH sections of 64 and 44
  intervals in swapped order.
- **`P2`/`B1` are emitted only where their table is at most 40,000 bytes.**
  A 139 KB bitmap per set would make the checkers hundreds of MB of source.
  The census prints the skip count (`B1` 138 skipped at landing; `P2` none).
  `P3` and every `K` variant are emitted for every set.
- **The byte-set atom table is the largest prefix of the 41 byte classes
  whose partition fits in 64 atoms.** At landing that is all 41, with 40
  atoms. The `ATOMS` line reports both numbers. The cross-check recomputes
  the atom count with the study's partition.
- **The four sabotage rows S360-S363 are on the `clskit` mech arm**, the
  only arm that can see them at S1. S363 plants a table row firing on a
  false predicate. Every emitted form stays a correct matcher under it, so
  the differential is green by construction and the cross-check is the
  detector.
