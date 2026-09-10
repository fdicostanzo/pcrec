# `tt4m_batch_customers.md` — [TT-4M-TIME]'s enumeration half (2026-09-10, lane rpkg)

Chartered because a from-memory count of `HARNESS_BATCH`'s customers was
wrong once (docs/dev/dev_journal.md, the [TT-4M-TIME] CORRECTION entry:
Frank named `san`'s `run_san_group` re-invocation of `run.sh` under
`GENCFLAGS` after the manager's own first count missed it — per-case-exec
census and per-pattern-compile lever conflated). This memo answers the
question by GREP, not by memory: every place in the tree that either (a)
re-invokes `tests/harness/run.sh` — the one file `HARNESS_BATCH` actually
lives in — or (b) runs its own per-pattern `gcc`/`pcrec` compile loop
outside `run.sh` entirely, which is the same LEVER even where the env var
cannot literally reach it today. Read-only: nothing under `src/`/`tests/`
changed to produce this list (the possessify/sed and gen_timeout fixes
landing alongside it in this lane are separate, unrelated items).

Method: `grep -rn 'harness/run\.sh'` and `grep -rn 'HARNESS_BATCH'` over
the whole tree (excluding `worktrees/` and `.git/`), then each hit was
read to separate a REAL invocation (`bash .../run.sh ...` or a variable
that resolves to it) from a comment/doc-prose mention. Every row below
cites the exact invocation site; re-grep before trusting a count here —
this is a snapshot at commit `2d0471a3` (this lane's branch point plus
its first four commits), not a live view.

## Category 1 — direct `tests/harness/run.sh` re-invokers

These are `HARNESS_BATCH`'s literal customers: each can set the env var on
its own `bash tests/harness/run.sh` call today, mechanically, the same way
`tests/axes/run_axes.sh` already does. "Batched?" states the CURRENT tree
state, verified by `grep -n HARNESS_BATCH` on the file named, not a guess.

| # | site | driven by | population | batched? |
|---|---|---|---|---|
| 1 | `tests/size/run_size_log.sh:57` | `Makefile:259` `test-corpus` (part of plain `make test`, every merge) | the WHOLE `.rxt` corpus | NO |
| 2 | `tests/lib/san_scripts.txt:27` names `tests/harness/run.sh`, dispatched by `tests/lib/run_san_group.sh` | `Makefile:1300` (`san`), and the parallel `UBSAN_ENV`/`ASAN_ENV` for-loops at `Makefile:1204`/`1232` (`ubsan`/`asan`) — all under sanitizer `GENCFLAGS` | the whole corpus, once per sanitizer axis | NO (`Makefile`'s `SAN_ENV`/`UBSAN_ENV`/`ASAN_ENV`, `Makefile:1182/1210/1270`, do not set it) |
| 3 | `tests/axes/run_axes.sh:478` (baseline), `:548` (per-axis loop) | `make test-axes` (opt-in), `scripts/battery.sh`'s axes stage | the whole corpus, once per baseline + ~13 axes | YES — forwarded verbatim (`tests/axes/run_axes.sh:140/179/477/547/889`), landed 2026-09-10 lane `axbatch`; `scripts/battery.sh:153` carries a prepared-but-dormant `HARNESS_BATCH=64` activation line (no-merge-mid-battery rule) |
| 4 | `tests/axes/run_ksweep.sh:91` (baseline), `:105` (per-K) | `make test-ksweep` (opt-in) | the whole corpus, once per baseline + each `--unroll=K` value | NO |
| 5 | `tests/known_fail/run_known_fail.sh:53` | `make test-known-fail` (part of `make test`) | `tests/known_fail/*.rxt` — deliberately near-empty by project convention (see `tests/known_fail/CLAUDE.md`); LOW VALUE even if wired | NO |
| 6 | `tests/mech/run_sabotage_matrix.sh:1952` | `make mech` (opt-in, ~50 min at `PROCS=4`) | one `run.sh` call per (sabotage row × target `.rxt` file) — the tree-rebuild-per-sabotage shape, dozens of sabotages × several target files each | NO — likely the HIGHEST-VALUE unclaimed customer here given `make mech`'s own runtime; not measured by this memo (enumeration only, no timing run) |
| 7 | `tests/mech/sabotages/S205_rxt_escape_index_not_value.sh:26` | `SAB_REACH`, one reach probe inside `make mech` | one file, one pattern | NO — trivial population, not worth batching |
| 8 | `tests/rxtsource/run_rxtsource_tests.sh:378,388` | `make test-rxtsource` (part of `make test`), the C1 three-parser identity proof | `xargs -a "$FILES"` over the WHOLE corpus (one `run.sh --dump` per file) | NO |
| 8b | `tests/rxtsource/run_rxtsource_tests.sh:1163,1200,1256,1282,1307,1354,1369,1435,1455,1568,1728` | same suite, later sections | one or two fixed `.rxtin`/`.rxt` fixture files per call — trivial population each | NO — not worth batching individually; listed for completeness since each is a genuine invocation, not a comment |

Row 8/8b's own file is a heavy user of the STRING "run.sh" in comments and
diagnostic prose (dozens of hits) beyond its actual `$RUNSH` call sites —
confirmed by checking `grep -n '"\$RUNSH"\|\$RUNSH '` rather than the bare
string, which is what separates rows 8/8b from noise.

## Category 2 — gen-compiles-per-pattern outside `run.sh`

These run their own per-pattern `pcrec` + `gcc` loop, never touching
`tests/harness/run.sh`, so `HARNESS_BATCH` (an env var `run.sh` alone
reads) cannot reach them as shipped. They are customers of the same LEVER
— fewer gcc invocations for many small patterns — not of the flag itself.
Nothing here is proposed to be built; this is the enumeration `[TT-4M-TIME]`
owes, not a design.

| # | site | driven by | population | note |
|---|---|---|---|---|
| 9 | `tests/bench/run_bench.sh:560` (`for entry in "${GCC_TIME_PATTERNS[@]}"`) | `make bench` | the COMPILE-SPEED/GCC-TIME budget patterns | NOT a real candidate: `docs/testing.md`'s D45 section excludes `tests/bench` from the shared compile helper explicitly BECAUSE "its budgets ARE its measurement" — batching would corrupt the per-pattern timing signal this loop exists to produce, the opposite of what every other row here wants |
| 10 | `tests/fuzz/fuzz.py:691` (`compile_with_pcrec`), driven by `pool.map(process_one, range(args.patterns))` at `:1097` | `make test-capturediff` (fixed-seed slice, part of `make test`) and `make fuzz` (manual campaign, `Makefile:1373`) | one `pcrec`+`gcc` compile per fuzzed pattern, up to `args.patterns` (already worker-pool-parallelized via `--jobs`, not gcc-invocation-batched) | genuine candidate for an ANALOGOUS python-side batching mechanism if one is ever built; python, so today's bash-only `HARNESS_BATCH` cannot reach it regardless of wiring |

## Category 3 — found by the same grep sweep, NOT customers

Named so a future re-count does not re-flag them as missed:

- **The six single-process differential drivers** `tt4_measurement.md`
  Stage A2 already identified (`assertions`, `rungselect`, `counterk`,
  `backrefs`, `mrl`, `altcls`): each compiles ONE differential binary (a
  handful of `gen_cc` calls total, confirmed by the call-site counts in
  this lane's own research — 1-5 sites per file, not one per corpus
  pattern) and sweeps many patterns/subjects AT RUNTIME inside that one
  process. No per-pattern gcc loop exists to batch.
- **`tests/cli/run_cli_tests.sh`, `tests/codegen/run_codegen_tests.sh`**
  — the two highest `gen_cc` call-site counts found (15 and 10), both
  fixed, hand-enumerated CLI/structural cases, not a corpus sweep — each
  `gen_cc` call is a distinct, deliberately different SCENARIO, not a
  repetition over a pattern list. Nothing to batch: batching's whole
  saving is amortizing gcc's fixed per-invocation cost over MANY
  interchangeable compiles, and these compiles are not interchangeable.
- **`tests/harness/run.sh` itself** (11 `gen_cc`-adjacent hits) — this is
  the mechanism, not a customer of it.

## What this memo does not answer

Whether wiring rows 1, 2, 4, 6 or 8 is worth the effort — that is a
measurement question (`[TT-4M-TIME]`'s timing half), not this
enumeration's. Row 6 (`make mech`) is named as the most promising
candidate on population size and existing runtime alone; no number in this
memo backs that beyond the population column.
