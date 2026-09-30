# studies/pf_know/ — [PF-KNOW] (D140): what a successful prefilter proves to the VM

Measurement study behind `docs/design/pf_know.md` (lane pfknow, 2026-09-30).
Study code: never built by the top-level `make`, never imported into `src/`.
Everything here is a COUNT or a Mac-directional timing; the note says which.

## Files

- `segprobe.c` — the PROVEN-SEGMENT probe. Links `../../build/libpcrec.a`,
  runs the real parser + `pcrec_altcls` + `pcrec_discharge_atomic` +
  `pcrec_lower_enc` (the same three-pass prefix `docs/dev/optloop/c2/
  onepass_probe.c` uses) with captures ON, and measures per pattern the
  LEADING and TRAILING fixed-width choice-free segments (bytes, tests,
  zero-width tests, capture writes, literal bytes), whether the whole
  program is such a segment (`det_all`), root `minw`/`maxw`. Its header
  states the `det` predicate exactly. Input `id<TAB>hex`, output TSV.
- `census.py` — the STATIC CENSUS: corpus (every `.rxt` pattern under
  `tests/`, via `--list-source`) + the READ-ONLY sibling pcrec-bench's
  `bench/*/patterns/*.rx`; compiles each with `build/pcrec --features all`
  (byte encoding, default engine), reads the stamps and every `static
  const` table off the emitted C, checks whether the DFA prefilter's
  byte-class partition REFINES each VM class bitmap (question 2), joins
  `segprobe`'s row. Writes `census.tsv` + `summary.json`.
  `PCREC=… PROBE=… CORPUS=… OUT=… BENCH=… python3 census.py`.
- `census.tsv`, `summary.json` — the 2026-09-30 run at `d88374d5`
  (3,746 rows, 3,347 compiled; the 399 refusals are the corpus's own
  refuse-expected rows plus bench patterns needing `-e utf8`/`-i`).
- `dyn.py` — the DYNAMIC SHARE instrument: one pattern, one subject;
  builds the artifact `--coverage` against a find-all driver, reads gcov's
  per-line counts, buckets every executed test line (`if`/`while`/`switch`)
  into VM `lead` (from `rx_L0` to the first loop/choice construct — a
  LOWER bound on the proven segment, since a bounded exact span loop is
  also deterministic), `mid`, `trail`, the DFA prefilter (`dfa`) and the
  search loop. A test LINE is the unit: a `memcmp` line counts once, a
  loop's test line once per iteration.
- `twin.py` — HAND TWINS with an answer-identity check (every span of
  every match hashed) before timing: `detall` (the window is the answer;
  the VM is never entered) and `prefix K LABEL SLOT@OFF…` (the leading
  segment's tests replaced by `scan_position += K` plus its capture
  writes). N alternating trials, medians. Mac timing, directional only.
- `gen_dense.py` — the seeded generator of `secrets.bin` (sparse: the
  bench's t-1m with one token per 4 KB), `secrets_dense.bin` and
  `sshd_dense.bin`.
- `results/` — `dyn_sparse.tsv` (the bench-subject cells), `*.json` (one
  per dyn cell), `twins.md` (the twin table with the box state).

## Reproducing

    make -C ../.. -j4 CC=gcc-16              # build/pcrec + libpcrec.a
    gcc-16 -O2 -I../../lib -I../../src -o /tmp/segprobe segprobe.c ../../build/libpcrec.a
    PCREC=../../build/pcrec PROBE=/tmp/segprobe CORPUS=../.. OUT=/tmp/pfk \
      BENCH=/Users/fdicostanzo/pcrec-bench python3 census.py
    PCREC=../../build/pcrec OUT=/tmp/pfk python3 dyn.py ID 'literal:PAT' SUBJECT
    PCREC=../../build/pcrec OUT=/tmp/pfk python3 twin.py ID 'literal:PAT' SUBJECT prefix K rx_Ln SLOT@OFF

The bench subjects are the sibling repo's own generators run with `--out`
into a scratch directory (`bench/loglines/gen_throughput_subjects.py`,
`bench/email/...`); the capability throughput texts are its committed
`throughput/*.bin`. `secrets_dense.bin`/`sshd_dense.bin` are this study's
own match-dense synthetics (`gen_dense.py`, seeded).
