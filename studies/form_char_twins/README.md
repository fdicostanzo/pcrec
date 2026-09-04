# studies/form_char_twins/ — [FORM-CHAR] STEP 0 + [OPT-CLSPACK] STEP 0 hand-twins

Chartered by Frank 2026-09-04 as lane C′ (`form0`). Answers: is a caseless
CLASS test faster than a folded COMPARE, and is a 256-byte table load
faster than the 32-byte bit array's load+shift+and — on both engines, cache
footprint counted. Self-contained per `studies/CLAUDE.md`: own Makefile,
plain `gcc -O2`, never built by pcrec's own `make`, never run by
`make test`. Nothing under this repo's `src/` or `tests/` changes.

See `docs/dev/form_char_step0.md` for the design, the full measured tables,
the recommendation and what is still owed (a real timing run on a quiet
box — this study's own `make check`/`make sizes` are answer-identity and
static-size only, never a stopwatch).

## What this is

Four families of hand-twins. Each twin is ONE emitted `build/pcrec`
artifact whose class-test (VM) or scan-edge-test (DFA) form has been
hand-edited by a mechanical Python transform, applied against the base
artifact's OWN emitted text — the byte set every twin tests is PARSED off
the compiler's real output, never re-derived from the pattern, so a twin
can never disagree with what the compiler actually built.

| family | base pattern | what it exercises | twins |
|---|---|---|---|
| A | `abcdef` (`-i --engine=vm`) | VM literal chain under caselessness, 6 two-member class sites | `fold` (folded compare), `table` (256B/site), `atom` (shared 256B table + per-class mask) |
| B/general | `[a-zA-Z0-9_]` (`--engine=vm`) | one VM class site, 4 disjoint runs | `table`, `rangecmp` (OR of runs) |
| B/sparse | `[aeiou]` (`--engine=vm`) | one VM class site, 5 singleton runs | `table`, `rangecmp` |
| C/small | `(?i)a{2,40}Z` (`--engine=dfa --no-captures`) | DFA scan edge (axis I), 4 sites, all case-fold pairs | `range`, `fold` |
| C/ci256 | pcrec-bench's `bench/altwide/patterns/ci-256.rx` (read-only) | DFA scan edge at real scale, 8 sites, all case-fold pairs | `range`, `fold` |
| D | `abcdefghijklmnop` (`-i --engine=vm`) | 16 distinct VM class sites (above the plan row's ~10-class crossover estimate) | `table`, `atom` |

`bitmap` (today's shape — a 32-byte bit array for the VM, a 256-byte
membership table for the DFA scan edge) is always the BASE artifact, never
regenerated as a twin.

## Reproducing

```
make base    # regenerate base/*.c from a real build/pcrec (gen_base.sh)
make twins   # derive twins/*.c from base/*.c (twin_A.py/twin_B.py/twin_C.py/twin_D.py)
make check   # compile every base+twin, run the per-family subjects, diff
             # every twin's answer against its OWN base's answer
make sizes   # `size` + a plain objdump read on every compiled object
```

`base/` and `twins/` are gitignored — they regenerate byte-for-byte from
the pinned compiler (`build/pcrec`) and the four transform scripts, so
committing them would just be a second copy of what the scripts already
determine. `PCREC` and `BENCH_CI256` (see `gen_base.sh`'s header) may be
overridden, e.g. `make base PCREC=/path/to/pcrec`. If `pcrec-bench`'s
sibling repo is not present, `gen_base.sh` skips only the `C/ci256` base
artifact and warns — every other family builds regardless.

`make check`'s correctness bar is answer-identity against each twin's OWN
base binary on a handful of hand-picked subjects per family (never a
hardcoded oracle) — the same bar `docs/dev/form_char_step0.md` reports
against. `results/twin_sizes.tsv` is this study's committed, measured
output (`make sizes`'s numbers, transcribed) — the raw table
`docs/dev/form_char_step0.md`'s size tables are read off. Its
`rodata_bytes` column is each object's WHOLE `.rodata` section
(`readelf -S`), not only the tables under test: family C's base artifacts
are full DFA machines and carry `byte_class`/`is_accepting`/`next_state`
tables alongside the scan-edge tables this study varies, so the
scan-edge-only delta (verified exact against the 256-bytes-per-site
prediction) is base-minus-twin: 2,560 → 1,536 (1,024 = 4×256) for `small`,
280,178 → 278,130 (2,048 = 8×256) for `ci-256`. Families A/B/D have no such
background tables, so their `rodata_bytes` column already IS the per-site
table cost.

## What each transform does

- **`twin_A.py`** — parses every `rx*_class_bitmapN[32]` site in a VM
  artifact, derives `fold` (a folded compare per site, falling back to an
  OR of exact compares for a non-fold-pair set — never exercised by this
  study's own patterns, kept so the script carries no silent special
  case), `table` (a 256-byte table per site), and `atom` (one shared
  256-byte byte→atom table, built from each byte's SIGNATURE — the set of
  classes containing it — plus a 64-bit mask per class).
- **`twin_B.py`** — the same `table`/`rangecmp` pair for a SINGLE class
  site, parametrized by a `tag` so it can run against more than one
  pattern (`general`/`sparse` here).
- **`twin_C.py`** — parses every `<m>_scanN[256]` DFA scan-edge site
  (`emit_dfa.c`'s `bitmap` body), derives `range` (OR of maximal
  contiguous runs) and `fold` (a folded compare, falling back to `range`
  for a non-fold-pair set). Runs identically against a small witness and
  `ci-256`, since a scan edge's site count and byte sets are a property of
  the DFA construction, not of the pattern's syntactic size.
- **`twin_D.py`** — `twin_A.py`'s `table`/`atom` pair generalized to an
  arbitrary class count, run here at N=16 to check
  [OPT-CLSPACK]'s stated "~10 classes" crossover.

Every transform prints a diff-line-count against its base as it runs — the
mechanical check that the ONLY thing that moved is the declaration block
and the test-expression substrings at each site, never a label, a `goto`,
or a comment.

## Files

- `gen_base.sh` — regenerates `base/*.c` from a real `build/pcrec`. See its
  own header for `PCREC`/`BENCH_CI256`.
- `twin_A.py`, `twin_B.py`, `twin_C.py`, `twin_D.py` — the four transforms,
  each with a `usage:` line and a module docstring describing its forms.
- `check_twins.sh` — compiles every `base/*.c` + `twins/*.c`, runs the
  per-family subjects, diffs every twin's answer against its own base.
- `sizes.sh` — `size` (`.text`/`.data`/`.bss`) on every compiled object;
  read `.rodata` per-object with `objdump -h <obj>` (`README.md`'s table
  above has the family-C caveat).
- `results/twin_sizes.tsv` — this study's committed, measured output.
- `Makefile` — `base`/`twins`/`check`/`sizes`/`clean` targets, all
  self-contained (plain `gcc -O2 -std=gnu11`, no dependency on pcrec's own
  build beyond `build/pcrec` itself).
