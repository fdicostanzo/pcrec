# docs/dev/optloop/s4/k82cost/ — K82 cause (B)'s cost-model instruments (lane `k82cost`, 2026-10-04)

The numbers behind `docs/design/litscan_k82b.md`. Reference material, never
built or run by `make`. Scripts take their paths from argv/the environment;
their scratch output trees (subjects, artifacts, binaries) are never
committed. The subjects come from `../k82diag/gen.py` (sha256-checked
against the bench manifests).

- `k82b_model.py` — the expected-cost model (design §1) over the 11 K82 /
  C3-customer cells × 4 rate sources (NONE, the shipped `weblog`/`log`
  bundles from a `lane/findb4` checkout, and the bench subject itself as the
  exemplar). It prints, per source: the markov1 run bits, the re-PICKed scan
  member, the W window on which the run block pays, and the per-guard Δ at
  64 KiB for M = 0 and M = occurrences. `k82b_model.py FINDB4_TREE SUBJ_DIR
  [linux|mac]`. Its transcripts are `model_linux.out` and `model_mac.out`.
- `k82b_sens.py` / `sens.out` — the 2x / 0.5x sensitivity sweep of `f`, `s`,
  `β` and E (design §1.4). It execs the model with its `main()` stripped.
- `k82b_census.py` — over every pcrec-bench export: the run-bearing emitted
  pre-checks on proof-free routes, each with its break-even E* against its
  fallback and the verdict under an illustrative per-form E row (design
  §2.4). Env: `PCREC BENCH FINDB4 SRC=builtin|weblog|log W=bytes`. Its
  transcripts are `census_<src>.out` (64 KiB) and `census_<src>_W<W>.out`.
- `memchr_cal.c` / `memchr_cal.mac.out` — the calibration probe for the
  machine terms: `f` (ns per memchr call), `β` (ns per byte) and `s` (ns per
  stop: re-search plus a 3-byte masked compare). The Mac run is committed.
  The ubuntubudu run is OWED: `gcc -O2 -o memchr_cal memchr_cal.c &&
  taskset -c 2 ./memchr_cal`.
- `twin_t3.py` / `drv_findall.c` / `t3_mac.out` — twin T3, the HANDOFF: the
  gate's candidate becomes the DFA's scan start (less the run's fixed offset)
  instead of being discarded, plus the find-all timing driver and the Mac
  transcript (design §0 item 4, §5 Q1). It is valid ONLY for a run at a
  bounded offset from the match start; `union-select`'s T3 would be unsound
  and was not timed.
