# memfn kit — wake-up brief

Rewritten 2026-11-05 ~23:55, updated 11-06 01:35 by a fresh kit session (pcrec-memfn [174c0c]). Committed docs win on any conflict.

## Who you are
The kit manager (`/pcrec-memfn-manager`). Main is the pcrec manager session `pcrec-main`. Frank rules, sometimes directly to the kit.
Kit worktree: worktrees/memfn on branch lane/memfn-k1102 (main 20fb73159 merged + kit journal/review commits).

## Read in order
1. This file.
2. The memfn/docs/journal.md tail (11-05 15:20 onward: 1d landed, 1e built, reviewed, fixed).
3. docs/design/memfn/span_pick.md REV 5.2, the design of record.
4. Review docs/dev/reviews/2026-11-05-r2-memfn-sp1e.md (rulings), and r1 (1d) before it.
5. D186 + addenda, D187, manifesto principle 9.

## CURRENT STATE: SPAN_PICK STAGE 1 COMPLETE (1e landed 11-06, main a65debe9d)
There is no open kit work. Stages 2-3 wait for Frank's GO via main; do not cut them without it.
Todo on a quiet pass: `scripts/wtprune --apply --force sp1efix` (it was kept only for build/ age plus the test-written artifact_size_log.tsv), then `scripts/branchprune --kit` for lane/memfn-sp1e and sp1efix.
The history below is kept for context.
Landed on main: 1a, 1f, 1g, 1b, 1c, 1d (20fb73159).
- **1e:** lane/memfn-sp1e @ 9cf199ed3 (sp1e accc55eeb + fix lane sp1efix, fast-forwarded). Reports: docs/dev/lanes/sp1e_report.md and sp1efix_report.md.
  - Zero movers. MF_SITE_ABI 23. MF_CLASS_V 7 -> 8 (D-hors joins ahead of PRES rows). Ratchet R20 3 -> 2; stage-1 kit-row total 4 -> 3.
- **Gates 430-439** (keys kit-sp1e2-*, TREE=worktrees/sp1efix; job files in /var/tmp/pcrec-pcrec/scratch/memfn/sp1efix/). Frank lifted tonight's 20:00-01:00 hold via main ("Box is free for you to schedule tonight"), so they run now.
  - 430-434 GREEN. 435 ident3 started 23:24, then 436 make test, then 437-439 mech.
  - Watcher: scratch/memfn/kitmgr/watch_sp1e2.sh (polls queue.log END lines after its baseline; exits on the first non-green or on 439's END).
  - Open: S1079's hand figure 6/3155 vs the review's 3/3160. Job 437's mech is the figure of record; read it there.
  - Three renderer pairs have no witness (UNREACHED in rows_check); say so in the done line.
- On all green: post `done:` for 1e in responses.md (branch lane/memfn-sp1e @ 9cf199ed3, reports, job logs + verdicts) and message main. On a red: launch a triage lane before reading the log.
- Do not touch worktrees/sp1e or sp1efix until the gates are read.

## After 1e merges
Stage 1 is complete. Stages 2-3 need Frank's GO via main; do not cut them without it. PLAN items for later units: 1d review's F4/F9/F10/F12 (filed by main as [SP1D-*]); 1e review's F5+F6+F9 renderer table (unit 3.0), F10 D-hors floor measurement, F11 anchor check over run_g2_win.sh.

## Box rules
- Frank holds 20:00-01:00 daily unless he says otherwise (lifted for 11-05 only). Main's ruled holds win.
- Jobs only through scripts/boxqueue. Kill only with scripts/safekill. Never use /tmp.
- Never commit a header or ABI change while a run is in flight.

## Lessons (recent)
- A watcher must read queue.log END lines for the current run only; cancelled jobs in done/ false-fire.
- A scratch-queue `boxqueue add` needs `--no-start`, or it arms a runner.
- A new tests/**/run_*.sh must pass K35 (LC_ALL=C) and TT-9 (san_scripts or san_excluded); run `make test-codegen` before delivering one.
- The queue monitor relays to the job owner's session; after a session change, tell main the new session name.
