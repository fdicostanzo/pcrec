# studies/ctx_prefilter_joint/ — [CTX-PREFILTER] joint-position measurement

Lane `ctxjoint` (2026-09-29, sonnet, measurement only, nothing under `src/`).
Backs `docs/dev/ctx_prefilter_joint.md`. Study code: never imported into
`src/`, never run by `make`.

## Files

- `joint.py PCREC OUTDIR SUBJECT[,SUBJECT...]` — for each pattern in
  `population.tsv`, derives the lookaround-free candidate set `C0`, the set
  `C1` surviving the necessary one-character condition and the true-start set
  `T` by libpcre2 (ctypes, `(?=(?:P))` wrapping), checks `T ⊆ C1 ⊆ C0`, writes
  `joint.tsv` and `controls.txt`. Runs its four positive/negative controls
  first and refuses to continue if one fails. Imports step 0's parsers from
  `docs/dev/lookaround_census/` unchanged.
- `analyze.py JOINT_TSV` — population accounting, per-subject distribution,
  model-vs-measured gap, bench-derived rows, absolute density.
- `gen_bench_subjects.py OUTDIR` — regenerates pcrec-bench's syntax@0.1
  throughput texts in memory (bytecode writing off, bench read-only) and
  refuses unless sha256 equals the bench manifest.
- `population.tsv` — the 354 still-VM rows of `df93ecf5:tests/ucp/
  ctxnode_route.tsv` (id, encoding, pattern); U2 is not on main.
- `results/` — `joint.tsv` (594 cells), `analysis.txt`, `controls.txt` from the
  run the memo quotes (main `31979ed3`, libpcre2 10.48 Homebrew).

Numbers are Mac evidence (D35 spirit); positions are machine-independent.
