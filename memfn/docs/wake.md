# memfn wake — kit session hand-off (rewritten 2026-10-29, going idle)

This file is the kit session's orientation. Run `/pcrec-memfn-manager` and follow its §1 wake order. It is rewritten at every pause and holds the current state; history lives in `journal.md`.

## STEP 0 — what I am waiting for (idle since 2026-10-29 ~11:00)

- **Job 622-kit-s3m-heavy** (D172 S3 on `lane/memfn-s3m` @ aab7cf1be + one job-script commit; abi 92) is QUEUED in the box queue behind main's 500-502 p48, 681 ic3-mech and 690 jobs.
  - Its own gate: cap = seconds to 19:30 at START (max 21,600); `--ready` refuses when < 11,000 s remain or between 10-29 16:00 and 10-30T14:00. So it runs today (ending by 19:30) or from 2026-10-30 14:00 by itself.
  - Monitor: a background shell loop (gnutimeout 40h) that exits when `worktrees/.boxqueue/{done,failed}/*-622-kit-s3m-heavy/result` exists and prints it. If the session restarted, read that file by hand.
  - Verdict: `result` (`verdict=`); red steps are `== s3 step NAME rc=N` with N != 0 in its job.log. Logs under `worktrees/s3m/build/s3/heavy622/`. Census UNEXPECTED movers are FINDINGS (predicted_movers.tsv came from main 0d3765c87), never blind re-pins.
- **Who messages me:** main = `pcrec_main` (uds:/run/user/1001/cc-socks/4169866.sock; check ListAgents). Nothing else is alive: no lanes, no other watchers. Heartbeat cron deleted at idle.

## Next action per trigger

- **622 GREEN:** fill S283's SAB_DOC_FIGURE (reads "OWED 2026-10-29 (lane s3m)") from 622's mech step; post `done: R-29/S3 — branch lane/memfn-s3m @ <tip>, report docs/dev/lanes/s3_report.md Part 12, validation 622 <verdict>` in responses.md; SendMessage main. Main re-pins the recursion-identity (B) pin to the landing merge. abi 92 holds unless a pcrec byte-mover lands first (main tells me; S3 then takes the next number).
- **622 RED:** a read-only triage lane first, then a fix lane with NO box access that stages ONE job (dry run); clear the slot with main before queueing.
- **S3 landed:** (a) propose to main a QUIET-box slot for the tier-U vrun refresh (rq4 harness, slot21 arm set, ~3.6 h; docs/design/memfn/probes/rq4/) — a night tail after a bench window (~00:30-04:30) or a daytime block with main's builds paused; (b) launch the kit-only SIMD lane: "find any of 2-3 arbitrary bytes" kernel + measurement card + G2 against the scalar byte loop, NOT routed (pricing consumes it); (c) then R-30 on `lane/memfn-r30`.
- **Box calendar (main, 10-29):** bench 19:30-00:00 tonight; main's full suite 00:00-~13:00 10-30; bench W1 Friday night, W2 Saturday night; Frank off the box until Sunday evening.

## 1. Who you are and where you work

- You are the pcrec-memory-functions kit manager. `requests.md` is main's (only main writes it); `responses.md` is yours.
- **Box:** the Linux dev box, repo `/home/pcrec/projects/pcrec`. `gnutimeout`. Commit with `-c user.name="Frank DiCostanzo" -c user.email=frank@dicostanzo.com`.
- **Never `cd`**, never `git stash`. Remove worktrees only with `scripts/wtprune`, branches with `scripts/branchprune`.
- **Kit worktree:** `worktrees/memfn` = branch `lane/memfn-r30` (from main b05ccfc0b), carrying today's responses/journal/wake commits. Main merges it whenever.
- **Kit sabotage-id range:** S1540-S1559.
- **Box courtesy:** lanes edit without the box and put every check into ONE queued job; no back-to-back boxlock chains.

## 2. Current state

- **abi:** main 91; S3 holds 92.
- **Open requests:** R-29/S3 (validating, above); R-30 (acked, queued after S3: at a VM re-find site whose landmark is the whole run, one ask — case 7 `url-tld-fix`).
- **Frank's SIMD go (2026-10-29, posted in responses.md as a proposed D147 addendum):** (1) verdict on the vrun family (14 CANDIDATE lines, tests/memfn/simd_accept.tsv); interim order (mine, main agreed): tier-U refresh after S3 first, then the bench request text for main ONLY if the layer still pays (the bench needs adapter rows for -fmemfn-simd / --memfn=no-vrun-*, vrun cells, an A/A twin, Zen 1 + Zen 4 + Mac); (2) the small-set kernel after S3; (3) runtime dispatch held until (1) wins.
- **Settled, do not re-ask:** Q-R14-1 was RULED 2026-10-11 (KB at w32 only; R-16 built it).
- **Withdrawn:** main's ADVANCE sequence-widening draft (D161 add. 17: reverse DFA at the landmark is the scaffolding; EDGE ADVANCE per looping state). Later: more EDGE sites (pcrec lane p48).
- **Stop ranking / pricing (D176):** ruled, not built; after S3. Witnesses in stop_ranking_study.md §5.1 (lane/memfn-stopstudy fc6735cdf, unmerged).

## 3. Prune when quiet

s3, s3pair, s3fix (after s3m lands), stopstudy (after main merges the study), and the older delivered memfn-* lanes listed by `scripts/wtprune` (dry run first).
