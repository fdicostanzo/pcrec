# memfn wake — kit session hand-off (rewritten 2026-10-24 at Frank's /close)

This file is the kit session's orientation. Run `/pcrec-memfn-manager` and follow its §1 wake order. It is rewritten at every pause and holds the current state; history lives in `journal.md`.

## 1. Who you are and where you work

- You are the pcrec-memory-functions kit manager (`pcrecdev3`). Main is `pcrecdev1`; find it with ListAgents.
- `requests.md` is main's and only main writes it. `responses.md` is yours and only you write it.
- **Box:** the Linux dev box, repo `/home/pcrec/projects/pcrec`. Use `gnutimeout`. Commit with `-c user.name="Frank DiCostanzo" -c user.email=frank@dicostanzo.com`.
- **Never `cd`** and **never `git stash`**. Remove worktrees only with `scripts/wtprune`.
- **Guide:** `docs/dev/guide/` (README, coding, architecture, style, critics; addenda/kit.md is yours to grow).
- **Critic rounds:** the `pcrec-critic` skill (one opus coordinator; results travel as FILES; spawned critics' replies get lost).
- **Kit sabotage-id range:** S1540-S1559.
- **BOX COURTESY (2026-10-24, learned the hard way):** a lane that chains `scripts/boxlock run` steps back to back starves main's box queue, and a BUSY lane may never read SendMessage. `scripts/boxlock run` now yields to pending queue jobs (main's change; `PCREC_BOXLOCK_JUMP=1` overrides it, is audited, and needs a reason). Prefer: lanes edit without the box and put every check into ONE queued job.
- **Before stopping a lane:** check that its detached runs survive or have ended.

## 2. Read, in this order

1. `memfn/CLAUDE.md`.
2. `responses.md` on the kit branch: the 2026-10-24 notices carry Frank's rulings (the EMIT-4 wart kept, the renames, the bar's per-call allowance).
3. The journal tail (2026-10-24 entries).
4. `docs/dev/reviews/2026-10-24-r1-memfn-s3-final-code.md`, including its "Rulings" section.
5. `docs/dev/lanes/s3_report.md` Parts 9-11 on `lane/memfn-s3fix` (worktree `worktrees/s3fix`).
6. `docs/design/memfn/stop_ranking_study.md` §5.1 (branch `lane/memfn-stopstudy` @ fc6735cdf): the pricing acceptance witnesses.

## 3. Current state

- **Kit branch:** `lane/memfn-s3` in `worktrees/memfn` @ 1198f18a0 (docs only: journal, responses, the 2026-10-24 review and critics.md lessons). Main merges it whenever.
- **abi:** main is at 84 (the iterators). S3 holds **85** (main confirmed; [EMIT-BIDI] takes 86 after it).

### D172 S3 (REPORT routed by default): FIXED, validating

- **Branch:** `lane/memfn-s3fix` @ e5362a59c, on top of `lane/memfn-s3pair` @ cc4f54eb2 (main 0d3765c87 merged in, abi 85). s3fix supersedes s3pair, and both supersede s3w.
- **Job 621-kit-s3-heavy: RUNNING in the box queue** (started 16:30). Logs are in `worktrees/s3fix/build/s3/heavy621/` and `worktrees/.boxqueue/{done,failed}/*-621-kit-s3-heavy/job.log`. The verdict is in `result`; red steps are the `== s3 step NAME rc=N` lines with N != 0. The s3fix tree is dirty only in `docs/dev/artifact_size_log.tsv`, which the job's make test writes. Leave it.
- **Job 620** (cc4f54eb2): red on axes_memfn only (stale floors; triage in `s3_evidence/tri620.md`). It is fixed in s3fix.
- **Final critic round:** no answer findings in ~5M differential cases. Rulings:
  - EMIT-1, the find-all quadratic: FIXED. The two-stream look-ahead is bounded, doubles from 128, and applies to every two-byte search. There is NO new deny.
  - EMIT-4, the 3+-member set-stop walk: KEPT as D176's test (Frank: "Leave the wart. Its fix is the test for pricing").
  - The deny rows are renamed `no-window-search` / `no-window-skip`. The stamp "cover" goes to [IFACE-PUSH].
  - window_site rev 3.3 is ACCEPTED. Goal 2 = no slower than DEF beyond the relative floor OR a MEASURED per-call layout allowance (ns/call). There are no per-pattern caps, and the known gaps are listed.
- **OWED on S3:**
  1. Read 621's verdict. If red: a triage lane (read-only), then a fix lane with NO box access that queues one job.
  2. CHECK-5's PAIR floors (row_floors.tsv) are still PLACEHOLDER; they need the N2 census.
  3. 588 timing: ask main for a window (main clears it with Frank; the box is shared). 588 now measures the per-call allowance from DEF layout variants and an 11-row BASE two-stream term against main's compiler. The bound's dense-text cost (`(?i)hello` journal 1.85 -> 2.23 instructions per byte vs the old build) is judged there; if it fails, it is a finding for Frank.
  4. done: R-29's S3 to main (merge lane/memfn-s3fix).

### Stop ranking / pricing (D176): RULED, not built

- The witnesses are in study §5.1. Desk reading: pricing fixes `[<>&]x`, `[xqz]ab`, `[jqz]uery`. `[.,;]\d`, `[QXZ]{2}` and dense hex also need the old DFA scan as a priced method row, a measured verify cost, and the subject's byte-rate bundle; dense hex is tested under both the default and a dense-hex prior.
- Order after S3: step-0 census, then the zen4-grid1 rev 2 night measurement, then the build.
- Frank asked "simd first to provide rows?" Answered no: pricing first, SIMD rows join later with their cards; a memchr3-like method is the trigger to watch.

**Nothing of the kit's is running except job 621 in the queue.** No lanes, no watchers, no crons.

## 4. Next actions on wake

1. Read 621's verdict (above). Tell main the result.
2. Green: ask main for the 588 window; then deliver S3.
3. Prune when merged and quiet: wsc1-8, wsmain, wsframe, r28, r28m, r27b, r27c, uwin*, b4p, s3, s3pair (after s3fix lands), stopstudy (after main merges the study).
