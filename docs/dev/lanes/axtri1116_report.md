# axtri1116 — triage of the red cloud axes run of lane/covs2b (run 43979627350)

Lane axtri1116 (opus), 2026-11-16, worktree branch lane/axtri1116 cut from lane/covs2b @ 3ec992759.

## STATE AT HANDOFF

STATE: done. Verdict: cause class (c), infrastructure. The runner for shard 4 lost contact with GitHub. No fix was needed, so this branch has no code change: its only commit adds this report and its history-index line on top of 3ec992759.
Rulings file `docs/dev/lanes/axtri1116_rulings.md`: empty at handoff, so no R-n was applied.
OWED: none (box queue). The cloud axes run on this branch's tip is named under CLOUD RUN DISPATCHED. The manager reads its verdict.

## THE FAILURE

- Run 43979627350 (workflow "Cloud", branch cloud/main/axes/covs2b-axes, commit df4d38bdb). Premise test: `gh run view --json jobs` lists exactly two failed jobs, `shard (4/20)` and `gather`, as expected.
- `gather` failed only because shard 4 did. Its verdict lines: `shard_job_result=failure`, the other 19 shards `rc=0`, and `RED: shard 4/20 MISSING: no result (cancelled, timed out, or the runner died before it recorded)`.
- Shard 4 has no make verdict line at all. `--log-failed` holds only the gather job (69 lines; the grep `'\*\*\* \[(Makefile:[0-9]+: )?test-'` matches nothing), and `gh run view --job 133692607615 --log` is empty.
- In shard 4 the step "Run the shard" never concluded, and no later step ran: neither the record step nor the upload.
- The job's check-run annotation reads, verbatim: `The hosted runner lost communication with the server. Anything in your workflow that terminates the runner process, starves it for CPU/Memory, or blocks its network access can cause this error.`
- Shard 4 ran from 23:29:12 to 00:55:15 (86 min). The job limit is 150 min (cloud_kinds.tsv axes `limit_min`), so it was not a timeout.

## CAUSE

Class (c): an infrastructure flake. The runner died; the branch did not fail a check. The evidence:

1. The failure carries no test signal. A hung case in run_axes.sh is killed by its per-unit `scripts/watchdog -s 3600`, which produces a normal red with a log. A failed assert produces a red make line. Shard 4 produced neither: the runner itself vanished.
2. Nothing on the branch plausibly changes shard 4's cost or memory. Shard 4 holds `--memfn=no-vrun-trim`, `--vm-entry-shape=1`, `-fno-end-window`, `-fno-lit-run` and `-fno-premul-table` (tests/ci/cloud_axes_shards.tsv).
   - The kit's raise 9d4907a16 reports 0 movers at the default and at width 32. MF_WSPAN_POS/MF_WREACH size no compiler array: a grep for `[MF_WSPAN_POS` finds only memfn test generators. Runs longer than 32 are admitted only at `--window-search-width` above 32, and no axes unit sets that.
   - The core asserts fail fast; they cannot hang.
   - abi 109 moves 0 default bytes.
3. Shard 4 has always been the long tail.
   - On earlier runs it took 46 to 73 min: e436038 72 min, d3wire-tip 46 min, covs2a 73 min, and the kit's span4k at 60c2958ae 72 min, green.
   - In this run every shard ran slow: shard 1 took 4476 s against a 3072 s plan (gather printed `REWEIGHT-DUE`). Shard 4 had run 86 min when contact was lost.
   - The time and the CPU mix (EPYC 7763 runners are the slow ones) fit runner variance, not a hang.

Residual, stated honestly: no shard-4 log exists. So "starves it for memory" cannot be excluded from the evidence, because run_axes.sh's watchdogs bound wall time only, not RSS. No mechanism for that was found on the branch. The re-run below settles it.

Tip question: the tip 3ec992759 adds covs2c, whose position writers take the Ctx and refuse a j past the span's len (code, 0 movers), and covs2e (docs). Neither adds work to shard 4's units. Nothing ties the failure to the commit, so nothing carries forward to the tip. The tip had no axes verdict of its own until the run below.

## FIX

None. Class (c) needs no code change, and nothing was edited under src/, memfn/, tests/ or the pins. No allowlist row was added, so delegation rule 7 did not come into play. No abi event; default bytes unmoved.

## VALIDATION

- Premise test: `gh run view 43979627350 --json jobs` lists exactly `shard (4/20)` and `gather` as failures (confirmed).
- Gather's verdict: `RED: shard 4/20 MISSING`; shards 1-3 and 5-20 `rc=0`.
- Shard 4's annotation: runner lost communication (quoted above). Its step list shows "Run the shard" never concluded.
- Shard-4 durations compared across five earlier axes runs (43955499773, 43936837886, 43908234585, 43901245088, 43805634947): 46-73 min.
- The raise's array usage checked by grep (memfn/include/memfn.h, memfn/src, src/).
- No local suite or test-axes was run, per the brief's box rule (owner's evening hold). No local build was needed, because no code changed. Whole-kind validation is the cloud run below.

## CLOUD RUN DISPATCHED

`scripts/cloudrun --owner main --kind axes --name axtri1116-axes --ref lane/axtri1116` pushes branch `cloud/main/axes/axtri1116-axes` at this branch's tip: 3ec992759 plus this report commit, so the code is identical to 3ec992759. It is a fresh full axes run. The axes kind takes no `--rows` (`cloud_kinds.sh takes-rows axes` rc=2), so no narrower kind exists.

`gh run rerun 43979627350 --failed` (RUNS.md's infra form) was NOT used. It would re-test only df4d38bdb, and the tip has covs2c's code on top. The fresh run on the tip gives the verdict that counts. The verdict reaches main as CLOUD-DONE.

## LEFT OPEN

- If `axtri1116-axes` comes back with shard 4 MISSING again, the second runner death on the same content would no longer read as a flake. It would point at memory starvation in one of shard 4's five units.
  - The next step would be to give run_axes.sh's per-unit watchdog an RSS bound (`-m`), so that a runaway turns into a named red instead of a dead runner. That is a harness change, filed here as a conditional, not built.
- REWEIGHT-DUE (slowest 4476 s against a 3072 s plan) was printed by gather. The axes shard table may want a reweight (`tests/ci/cloud_reweight.sh`). That is the manager's call; it is not part of this red.
- RUNS.md orders a cloud TEST run before AXES. Whether the tip 3ec992759 has its own green test-kind run is the manager's to check; this lane dispatched axes as briefed.
