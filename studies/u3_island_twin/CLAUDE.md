# studies/u3_island_twin/ -- [UCP] U3's D77 trigger: the island hand-twin

Lane `u3twin` (2026-09-30, sonnet, measurement only; nothing under `src/`,
`cli/`, `lib/`). Backs `docs/design/ucp_measurements/u3_island_twin.md` and
`docs/dev/lanes/u3twin_report.md`. Never built or run by pcrec's make.
Reads `../cls_tree_study/` (its kit/section/wholeset generators are imported,
not copied) and `../../build/pcrec` (the base artifacts). Writes only `out/`
(gitignored) and `results/`.

## What it does
Builds the CHARACTER-STEPPED "island" form of ucp_design.md s3 by hand and
proves it answer-identical, then times it against what pcrec emits today.

- `cm.py`       the character machine and its C emitter (island tokens in the
                reserved top range, one unsigned stop compare, decode, vector,
                scalar and by-class accept, seed from the char before `from`,
                repaired back_step).
- `f1.py`       F1 twins: the machine is COMPUTED from a flat pcrec byte
                artifact (`-fno-scan-edge -fno-premul-table
                -fno-anchored-dfa -fno-prefilter`), never re-derived from the
                pattern. `f2.py` F2 twins: hand-derived machines for patterns
                with no all-byte form (x1, x2, x3).
- `providers.py` the vector producers (kit lambda=4, page3w, bitmap1).
- `gen_bases.py` today's artifacts; `build_twins.py`; `subjects.py`.
- `oracle.py` / `oracle_remote.py`  libpcre2 answers, local or 10.46 over ssh
                stdin (nothing written on the remote box).
- `check.py`    correctness (arms x libpcre2 x each other; `SAN=1` sanitizers;
                `ORACLE=remote`). `controls.py` failing-direction controls.
                `reach.py` island/ill-formed REACH of the correctness set.
- `bench.c`, `run_bench.py`, `summarize.py`, `bundle.sh`  timing (house
                protocol, load gate, null-control arm, answer checksums).
- `results/`    committed TSVs (correctness, controls, reach) plus the
                ubuntubudu timing run: `bench_ubuntubudu.tsv` (raw per-round),
                `bench_summary.tsv`, `bench.log`.

Read the memo before the numbers; see README.md for the run recipe.
