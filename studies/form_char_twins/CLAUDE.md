# studies/form_char_twins/ — [FORM-CHAR] STEP 0 + [OPT-CLSPACK] STEP 0

Directory map; see `README.md` for the how-to-reproduce and
`docs/dev/form_char_step0.md` for the design, the measured tables and the
recommendation. `studies/CLAUDE.md`'s standing rule applies: self-contained
(own `Makefile`, plain `gcc -O2`), never built by pcrec's top-level `make`,
never run by `make test`. No `src/`/`tests/` change anywhere in this study.

## Files

- `README.md` — how to reproduce (`make base`/`twins`/`check`/`sizes`), the
  family/twin table, what each transform script does, and the family-C
  `.rodata` caveat (base artifacts there are full DFA machines, so the
  section total includes tables this study does not vary).
- `gen_base.sh` — regenerates `base/*.c` (gitignored) from a real
  `build/pcrec`: the six recipe patterns, one per family/witness. Reads
  `PCREC` (default: this repo's own `build/pcrec`) and `BENCH_CI256`
  (default: pcrec-bench's `bench/altwide/patterns/ci-256.rx`, read-only —
  skipped with a warning, not a failure, if the sibling repo is absent).
- `twin_A.py` — family (A): the VM literal chain under caselessness.
  Parses every `rx*_class_bitmapN[32]` site off a base artifact's own
  text and derives `fold`/`table`/`atom`. Generalizes cleanly to any
  number of case-fold-pair sites (`twin_D.py` reuses its `atom`
  construction at N=16).
- `twin_B.py` — family (B): a SINGLE VM class site, `table`/`rangecmp`
  twins, `tag`-parametrized so one script serves both the `general` and
  `sparse` witnesses.
- `twin_C.py` — family (C): the DFA scan edge's run-extension body
  (`emit_dfa.c`'s axis I). Parses every `<m>_scanN[256]` site (there can be
  several per artifact — one per machine/direction) and derives
  `range`/`fold`, `tag`-parametrized so one script serves both the `small`
  witness and `ci-256` at real scale.
- `twin_D.py` — family (D): `twin_A.py`'s `atom` construction generalized
  and run at N=16 (above [OPT-CLSPACK]'s own ~10-class crossover estimate)
  to check whether the shared-table form is a pure size win, a
  space-for-time trade, or a loss at that scale — measured here: a pure
  win on both `.text` and `.rodata` against `base` and `table`.
- `check_twins.sh` — compiles every `base/*.c` + `twins/*.c` and runs each
  on a small per-family subject list, checking every twin's answer against
  its OWN base's answer (never a hardcoded oracle — a base artifact's own
  correctness is already covered by pcrec's standing test suite; this
  script's only job is "did the transform change the ANSWER").
- `sizes.sh` — `size` (`.text`/`.data`/`.bss`) plus an `objdump -h` read on
  every compiled object; the numbers behind `results/twin_sizes.tsv` and
  `docs/dev/form_char_step0.md`'s tables.
- `results/twin_sizes.tsv` — this study's measured, committed output: one
  row per (family, witness, twin) with `.text`/`.rodata` bytes, the table
  count and the diff-line count against base. Columns documented in
  `README.md`.
- `Makefile` — `base` (calls `gen_base.sh`), `twins` (calls the four
  `twin_*.py` scripts against `base/`), `check` (calls `check_twins.sh`),
  `sizes` (calls `sizes.sh`), `clean` (removes the gitignored `base/`,
  `twins/`, `.bin/`, `.obj/` directories).
- `.gitignore` — `base/`, `twins/`, `.bin/`, `.obj/`: all regenerable
  byte-for-byte from the pinned compiler and the transform scripts, so
  committing them would be a second copy of what the scripts already
  determine (mirrors `studies/alt_dispatch/.gitignore`'s rule for its own
  build outputs, one level further — that study's `patterns/`/`subjects/`
  ARE committed because they are DERIVED-WITH-A-STATED-RULE inputs from
  pcrec-bench and cannot be re-derived from pcrec's own compiler alone;
  this study's `base/`/`twins/` regenerate from `build/pcrec` alone, so
  they carry no information the scripts+recipe don't already have).

## Reading the numbers

Every twin's `.text`/`.rodata` is a SIZE fact, `gcc -O2 -c`, this box.
`docs/dev/form_char_step0.md` is explicit that nothing here is a speed
number — the timing run (this study's twins ARE its inputs, per the
note's §6) still needs a quiet box after `.lift`. Do not cite a `.text`
byte count as a proxy for "faster" without reading that note's own
caveats first (in particular §4's argument that the 256-byte table's
one-load LATENCY could still win ns/byte despite losing on every size
axis measured here).

Maintenance: update this file when files are added/removed or their roles
change.
