# memfn wake — kit session hand-off (rewritten 2026-10-23 at Frank's /close)

This file is the kit session's orientation. Run `/pcrec-memfn-manager` and follow its §1 wake order. The file is rewritten at every pause and holds the current state; history lives in `journal.md`.

## 1. Who you are and where you work

- You are the pcrec-memory-functions kit manager (`pcrecdev3`). Main is `pcrecdev1`; find it with ListAgents.
- `requests.md` is main's and only main writes it. `responses.md` is yours and only you write it.
- **Box:** the Linux dev box, repo `/home/pcrec/projects/pcrec`. Use `gnutimeout`. Commit with `-c user.name="Frank DiCostanzo" -c user.email=frank@dicostanzo.com`.
- **Never `cd`** and **never `git stash`**. Remove worktrees only with `scripts/wtprune`.
- **Guide:** `docs/dev/guide/` (README, coding, architecture, style, critics, addenda/kit.md is yours to grow). Lane briefs and critics read it.
- **Critic rounds:** the `pcrec-critic` skill (design | code | both; one opus coordinator; results travel as files). Append framework notes to `docs/dev/meta/coordinator_framework.md`.
- **Kit sabotage-id range:** S1540-S1559 (S1540 is used).
- **Before stopping a lane:** check that its detached runs survive or have ended (TaskStop can kill them).
- **A lane that ENDS before a message reaches it misses it.** Send a GO for a stopped lane to a fresh lane, after TaskStopping the old one.

## 2. Read, in this order

1. `memfn/CLAUDE.md`.
2. `responses.md` on the kit branch. Its 2026-10-23 notices carry every ruling of the day.
3. The journal tail (the 2026-10-23 entries).
4. `docs/dev/lanes/s3_report.md`, Parts 7-8 then Part 9 if present, on branch `lane/memfn-s3pair` (worktree `worktrees/s3pair`).
5. The reviews `docs/dev/reviews/2026-10-23-r1-memfn-s3-code.md` and `-r2-memfn-s3-c1-code.md`.
6. `docs/design/memfn/stop_ranking_study.md` rev 2 (branch `lane/memfn-stopstudy`).

## 3. Current state

- **Kit branch:** `lane/memfn-s3` in `worktrees/memfn`, containing main up to f5a8de54c plus the journal, responses and reviews. Main merges it whenever (docs only).
- **Main:** the iterators landed and took **abi 84** (b8c66a739). D176 holds the stop-ranking rulings.

### D172 S3 (REPORT routed by default): BUILT, not landed

- **Branch:** `lane/memfn-s3pair` @ 36422a84e. The S3 commit is bc675b020 (one byte-moving commit, abi 84 PROVISIONAL). It must become **85** at landing: merge main into the branch first, then the D76/D94 grep ritual.
- **It contains:**
  - E-find asks Table B honestly (C1);
  - PAIR widened to any two-byte window stop (Frank: "widen two pair s3 now");
  - Table D a kit_table;
  - D174 wording;
  - the test-axes memfn arm fixed (14 = 14);
  - the window_site rev 3.3 DRAFT (ranked goals). Rev 3.2 stays the design of record until accepted.
- **Answers:** clean. diff_r2 is 7,200 cases with 0 bad; G2 10,042/0; plants 18/18 red; codegen 16/16; wreply 112/0.
- **TRAILING CHECKS, to fix before the next heavy run** (no answer change):
  1. **The census twin rule** (census.py and census_r2.py): a facts row for encoding E moves iff that task's E-twin artifact moved, judged both ways. Job 606 had 165 rows (byte `end_window used yes→no` on utf8 block-option tasks) and census_r2 had 19 (byte `RX_MEMFN_LIBC none→memchr` for `(?i)k` etc.). It is PARTLY written in the UNVERIFIED WIP 36422a84e.
  2. test-cpset-structure CHECK 3: re-record `(?i)HeLLo` EMITTED_BYTES in tests/codegen/manifests/m5_stage1_stamps.tsv (r49 instructions). NOT done.
  3. test-encoding-checks:
     - cover_pick's reader for the window find text: WIP;
     - the K50 undeclared-form list gains `(?i)\bcat\b`: NOT done;
     - PROVE the 4 of 237 byte/utf8 identity pairs differ only in the window text: NOT done; STOP if not.
  - Brief a FRESH lane from this list. Each section is rerun under boxlock, one at a time.
- **Then:**
  1. Replace `lane/memfn-s3w` with s3pair (s3w is superseded).
  2. The heavy job: `s3_job_587-kit-s3-heavy` in the s3pair tree, queued as a new number above main's.
  3. A `pcrec-critic both` round on the final S3.
  4. 588 timing, with the stratified sample IN the bar and foobar match/real capped at 1.052, in a slot main grants.
  5. done: R-29's S3 to main.
- **Known S3 limits, filed or judged:**
  - caseless words next to `\b` lose vrun with SIMD on (a SIMD-thread finding);
  - same-set windows re-read 1.1-2.5 bytes/byte on dense input (R2-2, measure in 588);
  - `(?<=[Qq])ab` declines cover (a missed win; fixed by D176 Q1);
  - a 2+-member stop below the candidate has no row.

### Stop ranking (D176): RULED, not built

- Q1: one priced choice in Table A over position × method. Costs live in ONE visible table (the measurement set via --list-measurements, relative to the walk, raw readings as provenance, stamped per artifact). An option changes a cost only via a visible key or row.
- Q2: D-hors becomes a priced method; HORS_MIN is deleted.
- Q3: measure this box now (memchr, pair and Horspool-probe cards plus verify, as zen4-grid1 rev 2, in a night window, after the step-0 census, after S3 lands). The library/script goes into [MEASURE-SET].
- Q4: one decider for presence and stop; spans with an UNBOUNDED offset are sent for presence.
- Q5: fixed-point integers.
- Q6: PAIR widening, now done inside S3; the SIMD kernel stays filed.
- Truncation: state the whole literal unless a stated reason.
- Standing rule: a new method adds its measurement card.

### Other

- [FLAG-SPELL] (main's): `(?i)abc` and `(?i:abc)` produce different VM programs.
- The r27c hex8 reading was delivered. Frank's call on an HRS design pass was superseded by S3's D-hors and D176.

**Nothing is running.** No lanes, no watchers, no crons. Frank's battery holds the box until ~08:00 2026-10-24; no timing until main says.

## 4. Next actions on wake

1. Read §2. Ask main whether the battery is done and the box is free.
2. Brief a fresh lane for the trailing checks (§3 list) on s3pair, starting from WIP 36422a84e.
3. Merge main into s3pair, renumber the abi to 85, then the heavy, then the critic round, then 588.
4. Prune when merged and quiet: wsc1-8, wsmain, wsframe, r28, r28m, r27b, r27c, uwin*, b4p, crit-memfn-s3-c1, s3 (after s3pair replaces it), stopstudy (after main merges the study).
