# pcap88 — [CORPUS-PCAP]: cap the harness worker default to the box's own performance-core count (2026-09-28)

Brief: plan.md row [CORPUS-PCAP] (docs/dev/lanes/tri87_report.md §6,
docs/dev/lanes/tt4m2_report.md's P=8 knee). Build candidate (1) only — a
darwin-aware worker-concurrency default, routed through ONE shared
mechanism rather than a per-site patch. Candidate (2) (a serialized
retry on TIMED OUT) explicitly NOT built; report whether residual-tail
evidence exists to warrant it.

## What was built

`tests/lib/procs_default.sh` — a new shared helper, the same
single-implementation shape `tests/lib/ncpu.sh`/`timeout_bin.sh` already
established, answering a DIFFERENT question from `ncpu.sh`'s `$NCPU`
("how many CPUs does this box have" — total capacity, still the right
answer for a load-average ratio). This file answers "how many concurrent
WORKERS should a parallel test section default to":

1. `PROCS_DEFAULT` already in the environment — trusted as-is.
2. darwin with `sysctl -n hw.perflevel0.physicalcpu` present — that count
   (measured 8 on this box; total `nproc`/`$NCPU` is 10 — 8 performance +
   2 efficiency cores).
3. otherwise `tests/lib/ncpu.sh`'s `$NCPU` (Linux/CI/an Intel Mac —
   unchanged there, since the physical core count already equals `nproc`).

Dual-mode: **sourceable** (`. "$ROOT_DIR/tests/lib/procs_default.sh"`,
sets `$PROCS_DEFAULT`, the same convention `ncpu.sh` call sites use) and
**directly executable** (`bash tests/lib/procs_default.sh` prints the
number — for a Makefile recipe's `$$(...)` substitution). Self-locating
in either mode via `$0` (no `ROOT_DIR` needed when executed standalone).
Verified directly: prints `8` executed bare on this box, `8` from a
different cwd, `8` sourced with `$ROOT_DIR` set, and an explicit
`PROCS_DEFAULT=3` override is honoured in executed mode too.

## Sites found and routed (grep -rn for every `nproc`-default expression
## in Makefile + tests/)

**Makefile** — all 17 occurrences of `$$(nproc)` (identical literal, one
`sed` pass): `test-corpus` (line 378, `run_size_log.sh`), `test-reject`
(416), eleven `GROUP_PROCS=` `run_group.sh` targets (490, 536, 678, 692,
705, 721, 744, 784, 866, 1090), `UBSAN_ENV`/`ASAN_ENV`/`SAN_ENV` (1386,
1434, 1495), `test-axes`'s `run_form_census.sh` call (1591), `mech:`'s
`run_sabotage_matrix.sh` call (1608). Three prose comments describing
these defaults updated to match (404-406, 929-933, 1511-1516).

**Scripts whose own `PROCS`/`JOBS`/`NSHARD` fallback read `nproc`
directly** (each now sources `procs_default.sh` and reads
`$PROCS_DEFAULT` instead of shelling to `nproc`):
- `tests/size/run_size_log.sh` (`PROCS`; this is `test-corpus`'s actual
  worker-fanout site — the Makefile's own `PROCS=` env var reaches it
  concretely, so both this file's internal fallback AND the Makefile line
  needed the fix, or a bare-script invocation would still default to
  `nproc`)
- `tests/registry/run_definitions_oracle.sh`, `tests/registry/run_pc4.sh`
  (`JOBS`, halved — `PROCS_DEFAULT / 2`, was `$NCPU / 2`)
- `tests/mech/run_sabotage_matrix.sh` (`JOBS`/`INNER_PROCS`'s `ncpu` input)
- `tests/lib/run_san_group.sh` (its own `INNER_PROCS` division — no
  `ROOT_DIR` in this file at all, so it invokes `procs_default.sh` as a
  subprocess via `$(dirname "${BASH_SOURCE[0]}")` rather than sourcing it)
- `tests/axes/run_axes.sh`, `tests/lookaround/run_expansion_diff.sh`,
  `tests/anchored/run_anchored_diff.sh` (`PROCS`/`NSHARD`)
- `tests/codegen/run_lookaround_identity.sh` (`JOBS`)
- `tests/codegen/run_dfa_uniform_fold.sh`, `run_dfa_stamps.sh`,
  `run_form_census.sh`, `run_anchored_match.sh`, `run_vm_frameless.sh`,
  `run_search_pinned.sh` (`NSHARD`)

**Deliberately NOT touched** (a different question — total capacity for
a load-average ratio, or a diagnostic print, never a worker-fanout
width): `tests/lib/ncpu.sh` itself (unchanged, `procs_default.sh`'s own
fallback), `tests/lib/load_guard.sh`, `tests/lib/loadavg.sh`,
`scripts/battery.sh`, `tests/bench/run_bench.sh` and
`tests/bench/compare/compare.sh`'s own `nproc` mentions, and the
Makefile's `-j$(nproc)` prose (build parallelism, not the harness's
worker-fanout question this row is about). Historical/dated measurement
prose (a specific past run's own numbers, e.g. `docs/testing.md`'s
"Measured on the project box (12 cores)..." paragraph, `tests/axes/
CLAUDE.md`'s "at the default PROCS=nproc=12") left as the record of what
was actually measured at the time, not edited to read as a live claim.

An explicit `PROCS=`/`JOBS=`/`NSHARD=` still overrides every one of these
sites, unchanged — nothing above touches that override path.

## Docs updated in the same change

- `docs/testing.md`: the shard-count line in "codegen structural checks"
  (§ around line ~618) and a new dated note under "The boxes" naming the
  8P+2E split, the tt4m2 knee, and the new default's Linux-unchanged
  behaviour.
- `tests/lib/CLAUDE.md`: `ncpu.sh`'s entry corrected (no longer claims to
  be wired into the sites this lane moved to `procs_default.sh`) and a
  new `procs_default.sh` entry with the full site list.
- `tests/mech/CLAUDE.md` and `Makefile`'s own inline comments: the
  "`JOBS` defaults to nproc/PROCS" claims corrected.

## Validation

- `make -j8 CC=gcc-16 all` — clean build, no warnings.
- `make strict CC=gcc-16` — "strict: whole tree compiles clean with
  -Werror -Wshadow".
- `bash -n` on every edited shell script — no syntax errors.
- `make -n` dry-run on every touched recipe (`test-corpus`, `test-reject`,
  `test-codegen`, `test-anchored-match`) — `$$(nproc)` correctly expands
  to `$(bash tests/lib/procs_default.sh)` in each.
- `make test-registry CC=gcc-16` — run twice (once backgrounded, once
  foreground to get an authoritative exit code): **exit 0**, every
  section's own "checks passed: N / checks failed: 0" trailer intact
  (226+210+138+34+54, PC-3/PC-4/definitions-oracle/limits/axes-registry
  all green), no `*** [test-registry] Error` line either run.
- `VALIDATE_ONLY=1 bash tests/mech/run_sabotage_matrix.sh` — **"333
  definition(s) valid, 0 rows measured"** — confirms `run_sabotage_
  matrix.sh`'s new `procs_default.sh` sourcing (added ahead of `PROCS`
  parsing) doesn't break field validation for any of the 333 sabotage
  rows.

**OWED, still running when this report was written** (log paths + the
line to watch for; both are `tests/lib/run_group.sh` sections, which
buffer each script's full output and print it all at once only once
every script in the group has finished — no partial output to read
before then):
- `tests/lib/run_group.sh`: line 25's own prose (`PROCS=$${PROCS:-$$(nproc)}`)
  corrected to name `procs_default.sh`.
- `make test-anchored-match CC=gcc-16` — log
  `/tmp/pcap88_scratch/test-anchored-match.log` — watch for `EXIT=0` (the
  script's own trailing `echo`) and no `*** [test-anchored-match] Error`
  line.
- `make test-codegen CC=gcc-16` — log
  `/tmp/pcap88_scratch/test-codegen.log` — same watch (`EXIT=0`, no
  `*** [test-codegen] Error`).
- **`make test CC=gcc-16`, the full battery** — launched detached as this
  lane's last act (`nohup caffeinate -s -- bash -c 'make test CC=gcc-16;
  echo "EXIT=$?"' > /tmp/pcap88_scratch/test-full.log 2>&1 & disown`), log
  `/tmp/pcap88_scratch/test-full.log`. Watch for the completion trailer
  (`sections ran: N/M`) followed by `EXIT=0`, or a `*** [test-X] Error`
  naming the first red section. Per BOILERPLATE, `make test` alone runs
  ≈100 min on this box; size the wait accordingly.

**Expected-green shape** (per the brief): the only accepted darwin red is
`test-codegen`'s `nm` line (a pre-existing, unrelated darwin difference —
see docs/testing.md's own "known darwin reds" notes); zero `TIMED OUT` is
the hoped result across `test-corpus`/`test-reject` at the new PROCS=8
default. Wall time vs the ~110-150 min baseline: not yet measured (owed
with the full run above) — the primary lever here is REMOVING
oversubscription, and `tt4m2_report.md`'s own P=8-vs-higher comparison
already measured the wall cost of capping there as 0-5%, so no
regression in total wall time is expected; the finding this run should
confirm is the TIMED OUT count going to zero, not a faster corpus.

## Residual-tail question (candidate 2 — NOT built)

**No residual-tail evidence was found in this lane's own work, and none
existed in the diagnosis this row rests on.** tri87's report (§4/§5)
measured EVERY named TIMED OUT case's real cost at 2-3 orders of
magnitude under the 10s `GENRUNTIMEOUT` budget, both at the pin that
produced the reds and at a later one — there is no case in either
population whose real cost sits anywhere near the budget once
contention is removed, which is the whole basis for tri87's "occasional
multi-second-to-ten-second SPIKE on trivial work" reading rather than "a
witness scaling toward its budget." Since candidate (1) removes the
oversubscription tri87 measured as the cause directly (capping at the
box's own measured P=8 knee rather than fanning out to `nproc`=10), and
`tt4m2_report.md`'s own P=8-vs-higher comparison is the source of the
"0-5% wall, up to 15% CPU-to-contention cost above it" figure that
motivated this fix, there is no measured population left over that
candidate (1) would fail to reach. Recommend candidate (2) stay filed
per D77 (build under measured need): the trigger would be a NEW `TIMED
OUT` population appearing even at `PROCS<=8` on this box (or the
equivalent knee on a future box) — nothing measured here or in tri87
suggests that population exists today.

## plan.md

Not edited (per brief — the manager flips STATE tags). Row
`[CORPUS-PCAP]`: candidate (1) is now BUILT and validated as above;
`make test-corpus`/`make test-reject`/full `make test` TIMED-OUT-count
confirmation is OWED (see log paths above). Candidate (2) stays filed,
un-triggered, per the residual-tail finding above.

## Commits

`lane/pcap88`, one commit (`41e6f20b`): the helper, every site, the docs.
This report is a second commit.
