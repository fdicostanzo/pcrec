# memfn wake — kit session hand-off (rewritten 2026-10-29 ~16:40, going idle)

This file is the kit session's orientation. Run `/pcrec-memfn-manager` and follow its §1 wake order. It is rewritten at every pause and holds the current state; history lives in `journal.md`.

## STEP 0 — what I am waiting for

- **Main merges** `lane/memfn-simdset` @ 83d9a6255 (standalone SIMD find-any kernel, zero movers) and `lane/memfn-r30` (this branch: today's ledger/journal/wake) after its trailgc landing (~18:45), and fixes emit_sweep.py's stale per-arm composition pins in the same step. Main messages the merge sha. Then prune: simdset, r30scope, rq4prep (NOT before job 640 runs: it reads worktrees/rq4prep), s3, s3pair, s3fix, s3m (S3 merged), via `scripts/wtprune` dry run first.
- **Job 697-kit-r30b-heavy** (R-30, `lane/memfn-r30b`), not-before **2026-10-31T09:00** (Saturday), cap 14,400 s, 13 steps. Verdict: `worktrees/.boxqueue/{done,failed}/*-697-kit-r30b-heavy/result` (ignore any `cancelled` entry: an earlier copy was cancelled to move it); red steps `== r30b step NAME rc=N`, N != 0. On green: a fresh sonnet agent (or I) fills `docs/dev/lanes/r30b_report.md` §5 (census) and §9 (checks) from 697's logs; post `done: R-30` with every pcrec-side hunk listed (main's condition; r30b said pcrec's statement did not change); main assigns the abi at merge (94 or later: P4/P1/P10 hold provisional 94-96). A composition-floor red alone is main's pin, not R-30's — read movers first.
- **Job 640-kit-rq4-tieu** (tier-U vrun refresh, `lane/memfn-rq4prep` @ 6e0789d07), not-before **2026-11-01T03:00** (Sunday, after bench W2), latest start 13:40, cap 12,000 s, quiet-gated. Output under worktrees/rq4prep (see rq4prep_report.md). On a result: read ON-OFF per level vs the CURRENT scalar layer; `table.md` with `--prior` compares to slot21, NOT like-for-like — say so. If the layer still pays: draft the bench request text (adapter rows for -fmemfn-simd / --memfn=no-vrun-*, vrun cells, A/A twin, Zen 1 + Zen 4 + Mac) for main to file. If it does not: tell Frank before anything else.
- Monitors: background watcher loops in this session (if it restarted, read the result files by hand). Main = `pcrec_main` (uds:/run/user/1001/cc-socks/4169866.sock; check ListAgents). No lanes alive. Heartbeat cron deleted at idle.

## Rules learned today

- Write `docs/dev/lanes/NAME_deliver.txt` (the DELIVER block) at brief time; without it every lane's lanecheck exits rc=65.
- Never leave a bare `boxlock run` waiter for light checks: queue ONE job (a heavy job already contains the light checks).
- Abi numbers go in LANDING order; main assigns at merge.
- Flags (Frank 2026-10-29): a public deny only where a caller can be slower; wrongness-risk changes get a test-only lever.

## Current state

- **Landed today:** D172 S3 (abi 92, pushed 29efe73cd). Plan: [REQ-PAST-LAST] filed by main from my note (unbounded-distance runs: stop-early by lazy re-find).
- **R-30 (Frank's go, widened option A):** built on lane/memfn-r30b (change 38d3143d5): a run part implied by a later part is dropped (the 8-byte window where the whole-run part exists); the window's word compared first; test-only lever; case 7 instructions 1,279M -> 898M, answers identical, no near-miss row slower; plants S1543-S1548 DETECTED. Validation = 697.
- **Frank's SIMD go:** (1) vrun verdict — tier-U refresh 640 first, bench request only if it pays; (2) kernel DONE (simdset); routing it is a pricing (D176) question — open questions in simdset_report.md; (3) runtime dispatch held until (1) wins. Q-R14-1 was RULED 2026-10-11 (KB at w32 only) — do not re-ask.
- **Next kit work (no build without Frank's go):** D176 pricing build (step-0 census, zen4-grid1 rev 2 night measurement, then build; witnesses in stop_ranking_study.md §5.1 on lane/memfn-stopstudy fc6735cdf, unmerged); 588 per-call allowance timing (OWED from S3, needs a quiet window).

## Who you are / where you work

- Kit manager; `requests.md` is main's, `responses.md` is yours. Box: Linux dev box `/home/pcrec/projects/pcrec`, `gnutimeout`, commit as Frank DiCostanzo <frank@dicostanzo.com>. Never `cd`, never `git stash`; worktrees go via `scripts/wtprune`, branches via `scripts/branchprune`. Kit worktree `worktrees/memfn` = `lane/memfn-r30`. Kit sabotage ids S1540-S1559 (S1543-S1548 used by r30b).
- Box calendar: bench W1 Friday night, W2 Saturday night; main's opt-loop builds Friday/weekend days; Frank on the box Sunday evening.
