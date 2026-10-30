# memfn wake — kit session hand-off (rewritten 2026-10-30 ~evening, going idle)

This file is the kit session's orientation. Run `/pcrec-memfn-manager` and follow its §1 wake order. It is rewritten at every pause and holds the current state; history lives in `journal.md`.

## STEP 0 — what I am waiting for

- **Prune leftovers:** `worktrees/simdset` (merged as 09917055b; wtprune kept it only for its fresh build/simdset mtime) then `scripts/branchprune --apply --kit lane/memfn-simdset`. Still NOT rq4prep before job 640 runs (it reads worktrees/rq4prep). s3m/wsc1/r27 read "uncommitted changes" in wtprune: look before any `--force`.
- **Job 697-kit-r30b-heavy** (R-30, `lane/memfn-r30b`), not-before **2026-10-31T09:00** (Saturday), cap 14,400 s, 13 steps. Verdict: `worktrees/.boxqueue/{done,failed}/*-697-kit-r30b-heavy/result` (ignore the older `cancelled` entry); red steps `== r30b step NAME rc=N`, N != 0. On green: a fresh sonnet agent (or I) fills `docs/dev/lanes/r30b_report.md` §5 (census) and §9 (checks) from 697's logs; post `done: R-30` with every pcrec-side hunk listed; main assigns the abi at merge (94 or later). A composition-floor red: the per-arm pins were re-pinned 38/88 on 10-30 (simdset), so read movers first. r30b is cut from main 1f5574fac — it may need a main merge before delivery (main moved: abi 93, simdset).
- **Job 640-kit-rq4-tieu** (tier-U vrun refresh, `lane/memfn-rq4prep` @ 6e0789d07), not-before **2026-11-01T03:00** (Sunday, after bench W2), latest start 13:40, cap 12,000 s, quiet-gated. On a result: ON-OFF per level vs the CURRENT scalar layer; `table.md --prior` compares to slot21, NOT like-for-like — say so. If the layer pays: draft the bench request text for main. If not: tell Frank first.
- No watcher loops survive this session: read the result files by hand on wake. Main = `pcrec_main` (check ListAgents). No lanes alive. Heartbeat cron deleted at idle.
- Main heads-up (Frank, not live yet): the box queue will order jobs by UNSHARDED run length, ~1 h shards, timed runs preferred at night. Main tells the kit before it goes live.

## Rules learned

- Write `docs/dev/lanes/NAME_deliver.txt` (the DELIVER block) at brief time; without it every lane's lanecheck exits rc=65.
- Never leave a bare `boxlock run` waiter for light checks: queue ONE job (`scripts/boxqueue add --name PRIO-kit-NAME script`, script with --dry-run/--ready and `boxqueue:` declarations; scratch copies in /var/tmp/pcrec-pcrec/scratch/memfn/).
- A job step that runs a `make`-driven self-test loses its report on failure (.DELETE_ON_ERROR): keep the output yourself.
- A floor below its measured value hides its own +1 plant (the --engine=vm pin, 10-30). After a population move, re-pin EVERY arm from one measurement.
- A sweep's ref after a main merge is the merged main, never the lane's old cut point.
- Abi numbers go in LANDING order; main assigns at merge. Flags (Frank 2026-10-29): a public deny only where a caller can be slower; wrongness-risk changes get a test-only lever.

## Current state

- **Landed:** D172 S3 (abi 92, pushed 29efe73cd); simdset standalone find-any kernel (main 09917055b, NOT ROUTED, unpushed until main's fsfix landing) with the COMPOSITION_EXTRA_PINS re-pin; r30 notes (6997f5b67).
- **R-30 (Frank's go, widened option A):** built on lane/memfn-r30b (change 38d3143d5): case 7 1,279M -> 898M instructions, answers identical, plants S1543-S1548 DETECTED. Validation = 697.
- **Frank's SIMD go:** (1) vrun verdict — job 640 first, bench request only if it pays; (2) kernel DONE (simdset; open questions in simdset_report.md: pricing route, form hash, timing driver, ops-table unification, NEON); (3) runtime dispatch held until (1) wins. Q-R14-1 RULED 2026-10-11 (KB at w32 only) — do not re-ask.
- **Next kit work (no build without Frank's go):** D176 pricing build (step-0 census, zen4-grid1 rev 2 night measurement; witnesses in stop_ranking_study.md §5.1 on lane/memfn-stopstudy fc6735cdf, unmerged); 588 per-call allowance timing (OWED from S3, quiet window).

## Who you are / where you work

- Kit manager; `requests.md` is main's, `responses.md` is yours. Box: Linux dev box `/home/pcrec/projects/pcrec`, `gnutimeout`, commit as Frank DiCostanzo <frank@dicostanzo.com>. Never `cd` (a hook blocks it, even inside heredocs — write scripts with the Write tool), never `git stash`; worktrees go via `scripts/wtprune`, branches via `scripts/branchprune --kit`. Kit worktree `worktrees/memfn` = `lane/memfn-wake1030` (this hand-off; deliver to main for merge). Kit sabotage ids S1540-S1559 (S1543-S1548 used by r30b).
- Box calendar: bench W1 Friday night, W2 Saturday night; main's opt-loop builds Friday/weekend days; Frank on the box Sunday evening.
