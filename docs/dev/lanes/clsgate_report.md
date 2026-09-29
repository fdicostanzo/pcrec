# lane clsgate — [CLS-TREE] S0 load-gate self-refusal, cause and fix

2026-09-29, sonnet, study tooling only (nothing under `src/`, `cli/`,
`lib/`, `tests/`). Branch `lane/clsgate`, worktree `worktrees/clsgate`.

## Problem

The [CLS-TREE] S0 timing session (bench I-119 → pcrec-bench's O-75) was
REFUSED twice on ubuntubudu, `pcrec-bench` branch `scratch/clstree-s0`
(`0d7392c`): `studies/cls_tree_study`'s load gate tripped MID-RUN, at
load1 0.61 (attempt 1, 1,157 `bench2.tsv` lines) and load1 0.52 (attempt 2,
3,852 lines). Attempt 2's pre-wait load1 was 0.07 with nothing else of
pcrec-bench's own running on the box (README.md in that branch: "Attempt 2
had nothing else of ours running").

## Diagnosis, with evidence

`bench.py`'s old gate (`loadavg()` + an instant `sys.exit`) was checked
**once per SET**, not once per timed unit: `main()` looped over the k53
population's 12 sets, and for each set it (a) compiled a fresh `.c` file —
`bitmap1` + `refbs` + three kit `lam` policies + (`--whole`) the
`page2w`/`page3w` wholeset arms — then (b) ran the resulting binary once per
regime (5 regimes under `bench2`), each run doing 7 arms × 11 rounds × 1M
probes of interleaved timing. The load check sat only between sets, so a
set's own build+run work never had a chance to be judged mid-flight, and
the NEXT set's check read whatever the PREVIOUS set's own CPU usage had
just pushed load1 to.

That is the cause: **the harness's own sustained, single-core CPU work
(gcc -O2 compiles + the timing binaries' tight loops) was elevating load1
via its own recent activity, not via anything else running on the box.** A
1-minute load average is an exponential moving average with a ~1-minute
time constant; continuous single-core work with no idle gaps drives it
toward 1.0 regardless of external contention. Attempt 2's own numbers are
exactly that curve: pre-wait load1 0.07 → refused at 0.52 after 10 of 12
sets (3,852 / 385 rows-per-set ≈ 10.0), with confirmed-idle surroundings.

Direct measurement on the Mac (gcc-16, `bench.gen()` + compile, all 12 k53
sets, `--whole`) confirms the mechanism's shape, not its exact magnitude
(the two boxes differ): compile time is small and not the driver (~0.25 s
per set, 2.9 s total for all 12), while the five regime *runs* per set are
the sustained load (member/mixed/ascii/full/runs measured at
0.89/0.51/0.18/0.37/0.24 s on one set — ~2.2 s of continuous CPU work per
set, times 12 sets with zero idle gap built in between). ubuntubudu's own
compute is presumably slower or under different contention, but the
qualitative mechanism — sustained work with no cooldown pushing a 1-minute
EWMA up regardless of anything else running — matches attempt 2's
trajectory precisely, and there is no `BUILD FAIL`/`RUN FAIL`/`ANSWER
MISMATCH` line in either attempt's log, so nothing else was wrong.

`bench_bytes.py` had the identical shape at a coarser grain (one check per
N in `{4,16,32}`) and inherited the same elevated load1 from `bench2`'s
immediately-preceding run in the executor's `run.sh` (no cooldown between
`make bench2` and `make bench2-bytes`), so it refused instantly too, on
both attempts.

## Fix

`studies/cls_tree_study/loadgate.py` (new file) is the ONE gate both
`bench.py` and `bench_bytes.py` now use (`wait_for_quiet`). The 0.5
threshold is UNCHANGED (Frank's 2026-09-11 ruling, calibrated for headless
ubuntubudu — never loosened here). What changed:

1. **Build phase separated from timing phase.** Both scripts now compile
   every arm for every unit (every set in `bench.py`, every N in
   `bench_bytes.py`) BEFORE any timing starts, so a compile never straddles
   a gate check.
2. **The gate is checked immediately before EACH timed unit** (one
   set×regime run in `bench.py`, one N's run in `bench_bytes.py`) instead
   of once per set/N, and it **polls for quiet rather than refusing on the
   first over-threshold reading** — `wait_for_quiet(max_load, bound_s=600,
   poll_s=10, tag)` logs every reading and waits up to `--max-load-wait`
   seconds (default 600 = 10 min) before refusing. A self-inflicted spike
   (the harness's own preceding work) decays within a poll cycle or two
   once the harness is idle waiting on the gate; genuine sustained external
   contention does not decay and still reaches the bound, still refuses,
   still reports its load readings — same honesty as before, just no
   longer triggered by the harness measuring itself.
3. **No own-PID-tree exclusion was needed or built.** The brief allowed
   excluding the harness's own process tree from the reading "only if the
   readings prove it is the cause AND there is a clean way (e.g. sampling
   load after a cool-down sleep)". The bounded wait-and-poll IS that clean
   way — it does not need to fingerprint which PIDs caused a reading, it
   just waits for the reading to fall, which a self-inflicted spike does
   on its own once the harness stops feeding it work. A separate
   fingerprinting mechanism would be a second, more fragile gate answering
   a question the wait loop already answers, and during an ACTUAL timed
   run the harness's own CPU use is the thing being measured, not noise to
   subtract.

Both scripts gained `--max-load-wait` (default 600.0) and `--max-load-poll`
(default 10.0) CLI flags; `--max-load` (0.5) is unchanged in meaning and
default.

## Verification

- `python3 -m py_compile bench.py bench_bytes.py loadgate.py` — clean.
- **Mac smoke, correctness only** (`--max-load 99` to bypass the gate for
  the smoke itself — never for a result; Darwin timing is never citable):
  - `bench.py --population k53 --sets 'L,^L' --lams 0,16 --rounds 2
    --regimes member,mixed --out smoke_bench.tsv` — wrote 34 rows (2 sets ×
    2 regimes × 4 arms × 2 rounds + refbs-excluded header math checks out),
    checksums agreed, no `ANSWER MISMATCH`.
  - `bench_bytes.py --ns 4,16 --lam 16 --rounds 2 --smoke --out
    smoke_bytes2.tsv` — wrote 18 rows (2 Ns × 4 arms × 2 rounds + header),
    checksums agreed.
  - Bounded-wait behavior isolated: `bench.py --sets L --lams 0 --rounds 1
    --regimes member --max-load 0.001 --max-load-wait 8 --max-load-poll 2`
    — logged 4 readings at 0/2/4/6 s elapsed, then refused at 8 s with
    `load1 1.66 >= 0.00 after waiting 8s ... (bound 8s, 4 readings, last
    reading 1.66)`, exit code 1. Confirms the poll-and-log path AND the
    honest-refusal-at-bound path both work.
  - Smoke output files removed after verification (session scratch, never
    committed; `results/*.tsv` is not gitignored so they were deleted by
    hand rather than left for `git status` to flag).

No `make test`/battery run — this lane touches only `studies/`, out of
scope for `make`/`make test` per `studies/CLAUDE.md`.

## Docs updated

- `docs/design/cls_tree_design.md` §7(b): the executor brief now (1)
  extracts the pcrec tree via `git -C ~/pcrec archive <COMMIT> | tar -x -C
  /var/tmp/clstree_s0/pcrec` and records the pin from that command rather
  than `git log` inside the extracted tree (which has no `.git` — this is
  what pcrec-bench's own `run.sh` had already worked out was necessary,
  O-73/pcrecdev1, but the design note's own brief still said `cd <pcrec
  checkout>` / `git log -1`); (2) states the new wait-then-refuse gate
  behavior in place of "refuses at load1 ≥ 0.5 and never caveats"; (3)
  adds an expected wall-time estimate (a few minutes, gate-quiet case,
  derived from the Mac timing above) and notes the `gnutimeout` budgets
  already had slack for the gate's bounded wait.
- `studies/cls_tree_study/README.md`: item 5's REFUSES description updated
  to describe the poll-then-refuse gate; the `make bench` comment line
  updated to match.
- `studies/cls_tree_study/CLAUDE.md`: `bench.py`/`bench_bytes.py` entries
  describe the new gating; new `loadgate.py` entry added.

## Deliverable

`lane/clsgate` branch, this report committed. No `src/`/`cli/`/`lib/`/
`tests/` changes (out of this lane's scope by brief). Validation: the smoke
runs above (COMPLETE, numbers inline); no full ubuntubudu re-run performed
from this lane — that is the next executor session, using the corrected
§7(b) brief.
