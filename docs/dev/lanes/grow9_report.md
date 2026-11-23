# grow9 report: growth sweep CPU bounds, per-doubling report, occasional tier, shard fold, pool

Branch lane/grow9 (cut from lane/grow8; main merged in first, commit 9c9fb1ccd: four conflicted files resolved keeping both sides, main's text winning shared lines except grow8's own [GROWTH-SWEEP] row; `make strict` and `make test-plan-lint` clean). Harness only: `tests/growth/`, `tests/ci/` growth files, their CLAUDE.md, a docs/testing.md hunk, the plan row and the history index. No `src/`, `cli/`, `lib/`, `memfn/src` edit. Rulings file `grow9_rulings.md` was empty at launch; last R-n applied: none.

## Summary

- Time bounds are CPU seconds (default tier 300 s, wall hang guard 1,500 s; occasional tier 3,600 s / 14,400 s); a red names the bound that fired.
- `run_growth.py --doubling` reports compile CPU per size on each growth axis and the ratio to the half-size neighbour. After K159 nested `+` is about x2 per level (the STOP RULE's x3.5 is gone). The report surfaced two real superlinear families, below.
- The occasional tier exists (107 cells), but measured after K159 those cells are cheap (25 s CPU at most): the move saves nothing today. Owner question below.
- Shard table re-folded: 76 shards, 0 unmeasured cells, predicted slowest shard 1,491 s against the 2,700 s limit.
- The runner already ran cells in an ordered pool of nproc/2; `-j` added; output identical at -j 1 and -j 8.

## CPU bounds

- The driver (`growth_driver.c`) now prints `cpu=` (its own getrusage, user+sys, all threads) on every `one` line; the runner keeps the largest uncapped compile CPU per cell, and the gcc matcher build's CPU comes from its own watchdog log line.
- The watchdog's `-c` is the CPU bound, `-s` the wall hang guard. A TIMEOUT text now reads "CPU bound: over N CPU seconds" or "WALL hang guard: over N s elapsed ... under the CPU bound". The library stage's per-cell bound is ITIMER_PROF CPU (floor 300 s, margin x20, applied to the cell's CLI compile CPU; the CLI stage writes `growth-cpus-<tree key>.tsv`, replacing the walls file) with a 10x wall guard; exit 123 and 124 as the watchdog's. Tested: a 2 s CPU bound on `group.poss.last.lit@250` printed `cell 0 TIMEOUT cpu-bound=2 wall-guard=20` and exited 123.
- Values and their basis: `run_growth.py --bounds` (BOUNDS_BASIS). MEASURED on the dev box after K159: the costliest default-tier compile is `matrix/group.poss.last.lit@250` at 27.5 s CPU alone (-j2) and 45 s at -j8 (cores shared); `atomic.star.last.lit@250` 33.7 s at -j8; `spine/named@65535` 25 s; gcc on a limit cell's matcher 1.4 s at most. 300 s is 6.7x the worst under load. NOT measured: the cloud runners' speed against this box; the first cloud run of this harness prints `CPU:` lines (slowest cells, headroom against the bound) to re-derive it. The wall guard 1,500 s sits under the cloud job's 2,700 s kill, so a hang names its cell (shard 31 of run 44940630891 was cut with no cell named).
- Before: the single bound was 180 s wall and 180 s CPU, which is what the K159 `+`@15 cells crossed.

## Doubling report

`run_growth.py --doubling` (531 points, 109 s wall at -j 8): spine axes from cells.tsv (n = 500 doubling to the limit cell's n; rows with a `red` stop at 4,000 because K148/K150 start near 8,000), nested-`+` axes (depth 5 to the edge E: the pattern doubles per level, so the neighbour is the previous depth), and matrix depth axes (16, 32, 64, 128, 250) for none/star/plus/poss across the 8 kinds. REPORT line when ratio > x3.0 and the larger point costs >= 0.25 CPU s (x3.0 is 2^1.58, midway between linear and quadratic; 0.25 s keeps the few-ms timer noise under 2%). A REPORT is never a red; a crashed or timed-out point is a FAIL.

Nested `+` after K159 (ratio per level, compile CPU; log `$PCREC_TMPDIR/scratch/grow9/dbl_full.log`): x1.7 to x2.1 at every level up to the edge for ncgroup, group, named, atomic, look, neglook, lookbehind, inline `first.lit` (named@15 2.2 s, lookbehind@15 3.1 s, inline@15 0.17 s); one noisy REPORT (ncgroup depth 15, x3.41 at 0.33 s). K159 is confirmed on the sweep's own axis.

What the report found (52 REPORT lines; none is a regression of this lane's):

| axis | what it shows |
|---|---|
| possessive `*+` depth nests (all 8 kinds, `first.lit` and `last.lit`) | x12 to x15 per doubling of depth: `group.poss.last.lit` 0.03 s at 32, 0.33 s at 64, 5.2 s at 128, 45 s at 250 (27.5 s alone): about n^3.7. This is the costliest default-tier compile. |
| `*` depth nests (group, named, atomic) | the same shape, x10 to x16 per doubling (`atomic.star.last.lit` 33.7 s at 250) |
| character spines `lit`, `[ab]`, `(?:a\|b)`, `\p{L}`-class, `lit_ship` | x3.0 to x3.9 per doubling from n=1,000 to 4,000 (0.25 s to 2.7 s), then the cost DROPS at 8,000 (1.0 s) and is x1.7 to x2.0 beyond: a quadratic step with a cut-over somewhere between 4,000 and 8,000 |
| `spine/named` | x2.3 to x3.5 per doubling from 16,000 to 64,000 (3.6 s, 9.6 s, 33.8 s) |

These are findings for the manager to file (I took no K id: IDS none, no `src/` edit). Cause not investigated.

## Occasional tier

`Cell.occasional` = the named compile-only exceptions (107 cells: 15 in cells.tsv, of which 13 are the NFA-state edges plus `cnt` and `cnt_nest`, and the 92 matrix `+` edges). Excluded from `--list`, the default run, `--shard-check` and the cloud table; `--tier occasional` (or `GROWTH_TIER=occasional bash tests/growth/run_growth.sh`, CLI stage only) runs them with the generous bounds; `--shard` with it is refused. `--pairs` still lists the full population.

Measured here, whole tier, no ladder, -j4, after K159: all 107 pass (5 known-red K148 crashes carried), slowest `spine/named@65535` 25.4 s CPU, `z_cls@131069` 7.6 s, the `+`@15 cells 0.2 to 1.6 s; no matcher is built, so gcc never runs. The ruling's premise (cells that "stay costly by nature after the fix") does not hold for the compile; the costly part (gcc -O0 on tens of MB, about 10 min, 3.4 GB) is the matcher build they decline. Moving them removes their coverage (the K148 ratchet among it) from the default and cloud runs and saves under 2 minutes. OWNER QUESTION (slug `occasional-tier-contents`): keep the tier as built (my lean: no), keep them in the default tier and make the occasional tier the same cells WITH the matcher built, or both. It is a one-line predicate, `Cell.occasional`.

## Shard fold

159 default-tier units that had no green-shard measurement (49 `apportioned`, 110 absent) now carry their seconds from the red shards of both runs (basis `measured-red-shard`; complete for K155-only red shards, a LOWER BOUND for shards 31 and 60, cut before their library stage ended). Table regenerated (`cloud_units_plan.py growth --setup 70 --slots 25 --write`): 76 shards (was 96), 0 unmeasured cells (was 135), per-shard work 278 to 1,301 s, predicted slowest 1,491 s wall, floor `matrix/named.poss.last.lit@250` 1,301 s; `--shard-check` PASS (76 shards, 1,493 cells once each). The two under-predicted cells (`inline.plus.first.lit@15`, `named.plus.first.lit@15`) are occasional now and in no shard; their 733/721 s were pre-K159 (they compile in 0.2/1.6 s now). All weights predate K159, so poss and `+` cells are over-predicted, never under.

## Parallelism

The runner already used a `ThreadPoolExecutor` over independent cells with `ex.map` (ordered output), sized nproc/2 (a cell can hold GBs; box 29 GB). Added `-j` and kept `--jobs`; `-j 1` is the serial control. memfn/tests/parpool.py not needed. `--doubling` uses the same pool size.

## Validation (local, under `scripts/boxlock run --label grow9-...`; nothing runs after 00:30)

- `--selftest`: all four crossing-over verdicts as written.
- `--only depth,spine` (475 runs, 0 failed): -j 1 182.3 s, -j 8 56.6 s (3.2x); verdict lines identical (diff of the output minus the `CPU:` lines is empty).
- `--doubling --doubling-only plus.first.lit,spine/alt_lit,spine/anchors` (113 points): -j 1 36.0 s, -j 8 9.8 s; axis/size/outcome columns identical.
- `--lib` (plain build) on three cells: PASS; the CPU-bound timeout path exercised by hand (above). The ASan library stage is the cloud run's.
- `--tier occasional` whole tier: above. `--shard-check`: PASS. `make -s strict` was clean at the merge; the harness edits touch no C under src/.

## STATE AT HANDOFF

Branch lane/grow9 (tip in the cloudrun line of the handback). Rulings applied: none (file empty). Scratch: /var/tmp/pcrec-pcrec/scratch/grow9/ (logs dbl_full.log, occ_full.log, worst*.log, q_j*.log). Left alone: stale `growth-*` dirs in /var/tmp/pcrec-pcrec (not all mine).
OWED: the FULL default sweep in the cloud, `scripts/cloudrun --owner main --kind growth --name grow9`, branch `cloud/main/growth/grow9` (key `grow9`); it prints the first cloud `CPU:` lines and the per-doubling report on the last shard (76/76), the data to re-derive the 300 s bound. Not run locally: the full default CLI sweep and the ASan library stage.
Open for the owner: `occasional-tier-contents` (above); filing the possessive/star and character-spine findings.
