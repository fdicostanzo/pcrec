# docs/dev/optloop/artrev/gen/ — the [ARTREV] S5 generalizer's census (lane artgen, 2026-10-06)

The counted populations behind `../generalize.md` (K35). Compile-side only: no subject is matched,
no clock read, gcc never run.

- `census.py` — one `--emit-facts` call and one `-o -` compile per pattern over the corpus
  (`tests/**/*.rxt`, deduplicated on pattern/encoding/icase) and the pcrec-bench pattern exports
  (read-only), plus variant compiles for K2 (`--analysis log|weblog`), K6 (the hand-possessified
  spelling) and K11 (the START-SET stage-3 compiler, `SS3=`). Fifteen classifiers K1-K15, one per
  generalize.md idea; each is described in the module docstring. `--selftest` runs a positive and
  a negative control per classifier. Env: `PCREC`, `SS3`, `BENCH`, `CORPUS`, `OUT`.
- `selftest.txt` — the control transcript (31 controls, 0 failed).
- `summary.txt` — the census output with its provenance header (compiler shas, bench sha).
- `rows.tsv.gz` — one row per pattern, every column the classifiers read (pattern text omitted:
  `pat_sha` is the sha1 prefix of the pattern bytes; `id` names the bench file or corpus file:line).

Re-run at a new pin: `PCREC=build/pcrec SS3=<stage-3 or same> CORPUS=. BENCH=<pcrec-bench>
OUT=<scratch> python3 docs/dev/optloop/artrev/gen/census.py --workers 4` (~2 min on the Mac M1).
