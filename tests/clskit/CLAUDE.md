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
  mode writes checker `.c` compile units plus the census, packing VARIANTS
  (each set's reference arrays are copied into every unit holding one of its
  variants) into units by EMITTED BYTES (budget `CHUNK_BYTES` = 250 KB,
  optional argv[4]) so gcc's time per unit is bounded by the text it
  compiles, not by a set count (clstri: a fixed 12 sets/unit made one unit
  5.2 MB and over gcc-15's 10 s GENCPU on Linux; citri: at 1.5 MB units gcc-13
  on CI needed ~10x the Mac's CPU and 23 of 51 units exceeded it, so the
  budget is sized for the slowest supported compiler, 0.2-0.4 s a unit on the
  Mac) AND by RUN COST (`CHUNK_VARS` checker variants per unit, optional
  argv[5]: bytes alone let 118 small sets run 6.4 s solo against the 10 s
  GENRUNTIMEOUT and time out under make test's -j load, s1tri 2026-09-29).
  Since admin1008 (2026-10-07) the checker runs' wall backstop is
  `CLSKIT_RUN_WALL` (default `gen_timeout_secs`, 60 s plain / 180 s
  sanitizer) rather than gen_run's tight 10 s: the checkers are CPU-bound
  for ~1 s by construction (MEASURED on the Linux dev box: 331 units, run
  wall median 0.14 s / max 1.58 s with 16 threads busy; worst unit solo
  0.94-1.10 s CPU), so 10 s was a load gauge, not a hang detector. The CPU
  budget (`gen_cpu_secs`) stays the primary bound.
  The only indivisible part of a group is its LAW bundle: when a group has
  compositions, the K4 and P3 variants of all its sets plus its COMPS rows
  share one unit (the law compares a result against its operands in one
  process). `emit` also prints `VARIANTS n`, which the script sums against
  the `CHECKED` lines (a set is counted by NAME: it can appear in several
  units). Its `dump` mode prints `SEC`/`WHOLE`/`ATOMS`/`SEL`/`ROW` lines for
  the cross-check; since clss2fix (D139) a `SEL` line is per (position,
  deny, SITE, CALLS) — the VM and the scan edge, one and two writes of the
  test — and a `ROW` line carries the row's site mask.
  **The reference in each checker is plain interval arrays written by THIS
  file from the population file.** No line of `clskit.c` produces it.
- `checker_main.inc`: the checker's `main()`, included at the end of every
  chunk.
- `crosscheck.py`: recomputes each decision with the frozen reference code
  in `ref/`: `section.partition` at CUBES tier 1, `wholeset.PageW2/PageW3`,
  and `bench_bytes.atom_partition`. The selection TABLE is restated
  independently from D131 (NO atom row — item 6's atom table is an
  artifact-level choice, not a per-set `ROWS` outcome), and `clskit.c`'s
  printed `ROW` listing is held to that restatement. Since [CLS-TREE] S2
  (lane clss2; review fixes clss2fix, D139) the restatement carries the
  BYTE rows and each row's SITES: `byte-range` (one interval, every
  position and site), `byte-fold` (the ASCII case pair, -2/-1, both sites,
  deny ordinal 7), `byte-fold-default` (0..+2, VM only, D138 Q1),
  `byte-kit` (-2/-1, where `calls` x the kit is smaller than the lone-set
  table its site reads, `LONE_TABLE`) and `byte-table` (every position, so
  a denied or larger `byte-kit` falls to a table). `KIT_DISP_BYTES` /
  `KIT_DISP_BYTES_BYTE` restate clskit.c `PLACE.kit_disp_bytes` (D131
  addendum 1's fitted dispatch/prologue term, code points) and
  `kit_disp_bytes_byte` (the byte domain's, 0), added to K's bytes wherever
  the restated predicates compare K against another form — never to the
  DP's own sectioning bytes.

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
- **The five sabotage rows S360-S364 are on the `clskit` mech arm**, the
  only arm that can see them at S1. S363 plants a table row firing on a
  false predicate; S364 (clss1b) drops D131 addendum 1's fitted K-byte
  term back out of the selection. Every emitted form stays a correct
  matcher under either, so the differential is green by construction and
  the cross-check is the detector.
