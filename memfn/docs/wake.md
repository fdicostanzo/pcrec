# memfn wake — kit session hand-off (rewritten 2026-11-02 ~03:00, going idle)

This file is the kit session's orientation. Run `/pcrec-memfn-manager` and follow its §1 wake order. It is rewritten at every pause and holds the current state; history lives in `journal.md`.

## STEP 0 — what I am waiting for

- **vrun bench request** (Frank's SIMD go step 1): job 640 (tier U, pre-S3 tree) says the layer pays; draft `docs/design/memfn/vrun_bench_request.md` on **lane/memfn-vrunreq @ cd7dc0d70** (notice in responses.md). Main merges it, relays it to the bench, and owns the pre-registration and window. On the bench verdict: update tests/memfn/simd_accept.tsv from the transcript (§R4.9.6), answer pc16 / sp-n04-v17 per §7, then [MEMFN-RTDISPATCH] (held until the layer wins).
- **S526-c14 ANOMALY re-aim**: main files it; it may come as an R-n. Pre-existing (7047b69e4 scores its static-assert catch as ANOMALY).
- **Prune leftover:** `worktrees/vrunreq` (branch lane/memfn-vrunreqd, merged into lane/memfn-vrunreq) was kept by wtprune's <120 min quiet gate: `scripts/wtprune --apply --force vrunreq` (only the untracked deliver file), then `scripts/branchprune --apply --kit lane/memfn-vrunreqd`. Also rq4prep (job 640 done; HEAD 6e0789d0 unmerged: look, then --force/--archive if nothing is owed), memfn-r17/r27 (look before --force).
- No lanes alive. No heartbeat. Read result files by hand on wake.

## Rules learned

- ONE STAGE PER JOB (Frank 2026-10-30), chained with `boxqueue after KEY`; about an hour at most.
- Keep job scratch paths SHORT (/var/tmp/pcrec-pcrec/scratch/memfn/...): diagnostics embedding a path have a 256-byte budget (772, 2026-11-01).
- A matrix ANOMALY ("a compile failure is not a catch") can be a plant designed before main's 7047b69e4: check the plant's own design before blaming the change.
- Write `docs/dev/lanes/NAME_deliver.txt` at brief time. Queue jobs, never bare `boxlock run` waiters. A make-driven self-test loses its report on failure: keep output yourself.
- Floors are pinned AT the measured value; re-pin every arm from one measurement. A sweep's ref after a main merge is the merged main.
- Abi numbers go in LANDING order; main assigns. Flags: public deny only where a caller can be slower; wrongness-risk changes get a test-only lever.
- Box: Frank holds 20:00-01:00 daily; main may pull queued jobs earlier onto a free box.

## Current state

- **Landed:** D172 S3 (abi 92); simdset find-any kernel (unrouted); R-30 (abi 94, main 657e23231, 2026-11-02).
- **Pricing:** requirements rev 1 (docs/design/memfn/pricing_requirements.md); placement decided by evidence (main's rule-list pilot, then the bake-off if needed). Frank's open rulings O1-O5. No build without Frank's go.
- **Owed:** 588 per-call allowance timing (from S3, quiet window).

## Who you are / where you work

- Kit manager; `requests.md` is main's, `responses.md` is yours. Kit worktree `worktrees/memfn` = `lane/memfn-vrunreq` (from main 657e23231). Never `cd`, never `git stash`; worktrees via `scripts/wtprune`, branches via `scripts/branchprune --kit`. Kit sabotage ids S1540-S1559 (S1543-S1548 used).
