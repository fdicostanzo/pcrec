# studies/form_char_twins/ — [FORM-CHAR] STEP 0 + [OPT-CLSPACK] STEP 0

Directory map; see `README.md` for the how-to-reproduce and
`docs/dev/form_char_step0.md` for the design, the measured tables and the
recommendation. `studies/CLAUDE.md`'s standing rule applies: self-contained
(own `Makefile`, plain `gcc -O2`), never built by pcrec's top-level `make`,
never run by `make test`. No `src/`/`tests/` change anywhere in this study.

## Files

- `README.md` — how to reproduce (`make base`/`twins`/`check`/`sizes`/`asm`),
  the family/twin table, what each transform script does, the family-C
  `.rodata` caveat (base artifacts there are full DFA machines, so the
  section total includes tables this study does not vary), and the
  compiler-equivalence evidence section (why family A's fold-vs-table
  question is closed on `.text` alone, and which two families the timing
  run's open latency question is actually scoped to).
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
  `range`/`fold`, `tag`-parametrized so one script serves the `small` and
  `nonpair` witnesses and `ci-256` at real scale. On a NON-fold-pair site
  (`nonpair`) `fold`'s fallback makes it emit `range`'s own text verbatim —
  the two twins compile to byte-identical objects, which is the control
  that isolates what `fold`'s real ascii-fold transform buys on a genuine
  fold-pair site (`small`/`ci256`): a small, real, and now compiler-
  verified `.text` win (`asm_evidence.c`, below).
- `asm_evidence.c` — the compiler-equivalence check behind family A's
  size-only ranking: three spellings of a caseless letter test
  (`c=='a'||c=='A'`, `(c=='a')|(c=='A')`, `(c|0x20)=='a'`) all compile
  branchless to the SAME `and/or`+`cmp`+`sete`, so `table`'s one-load
  latency has nothing to beat there; `test_nonpair` is the two-compare
  control, the same shape `twin_C.py`'s `nonpair` witness measures on the
  scan edge. `make asm` compiles it to `results/three_spellings.s`.
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
- `results/three_spellings.s` — `asm_evidence.c` compiled `gcc -O2 -S`,
  committed: the raw evidence for the compiler-equivalence claim above.
- `Makefile` — `base` (calls `gen_base.sh`), `twins` (calls the four
  `twin_*.py` scripts against `base/`), `check` (calls `check_twins.sh`),
  `sizes` (calls `sizes.sh`), `asm` (compiles `asm_evidence.c`), `clean`
  (removes the gitignored `base/`, `twins/`, `.bin/`, `.obj/` directories).
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
caveats first.

**One caveat is narrower than it first looked.** `results/three_spellings.s`
(`asm_evidence.c`) shows gcc compiles every fold-pair spelling — the OR
form, the bitwise-OR form, the ascii-fold compare — to the SAME branchless
mask+compare+sete, with no load at all. So the "256-byte table's one-load
LATENCY could still win despite losing on size" argument does NOT apply to
family A (`fold` vs `table`/`atom` on the VM literal chain) — there is no
load on the `fold` side for a table's one load to beat. It DOES still apply
to family B (`table` vs the bit array on a general/sparse VM class) and
family D (the atom table): both of those forms' non-table alternatives
(the bit array, `rangecmp`) genuinely read from memory too, so a real
timing number is still needed there.

Maintenance: update this file when files are added/removed or their roles
change.
