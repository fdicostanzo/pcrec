# memfn wake — kit session hand-off (rewritten 2026-10-08 ~23:30, session reset)

This is the orientation file for the kit session, run as
`/pcrec-memfn-manager` (`.claude/skills/pcrec-memfn-manager/SKILL.md`;
its §1 is the wake order). It is rewritten at every pause and holds the
current state; the history is `journal.md`.

---

## 1. Who you are and where you work

- You are the pcrec-memory-functions kit manager. The pcrec manager
  ("main", session name `pcrecdev1`) files requests in `requests.md`. You
  answer in `responses.md` (you are its only writer). This session's name
  is `pcrecdev3`.
- **Box:** the Linux dev box `pcrec@192.168.1.17`; the repo is
  `/home/pcrec/projects/pcrec`. 16 threads, gcc 15.2, libpcre2 10.46, no
  clang.
  - Bare `timeout` is uutils: use `gnutimeout`.
  - No git identity is configured: commit with
    `git -c user.name="Frank DiCostanzo" -c user.email=frank@dicostanzo.com`.
- **Kit worktree:** `worktrees/memfn`. One branch per delivered unit, cut
  from main. Never merge to main, never push, never `cd` into another tree
  (use `git -C` / absolute paths; a `cd` moves the session cwd).
- **Scratch:** `worktrees/memfn-slot/` (gitignored).
- **Pruning:** `scripts/wtprune --apply NAME` prunes ONE worktree by name.

## 2. Read, in this order

1. `memfn/CLAUDE.md`.
2. `memfn/docs/requests.md`, then `responses.md` (newest `done:` entries
   and notices).
3. The tail of `memfn/docs/journal.md`.
4. `docs/design/memfn/integration.md` §R4.9 (on lane/memfn-r9) and the
   M6 report `docs/dev/lanes/m6_report.md` (on lane/memfn-m6).
5. BOILERPLATE, coding_guide before C, learnings §3 before a check.

## 3. Box and slot rules (this box)

- One heavy suite at a time across BOTH sessions. Ask main for every heavy
  slot (census, identity gate, full G2, make test, mech), and ping main when
  it ends.
- **Light work needs no slot:** make/strict at -j4, single compiles,
  test-memfn-{arms,stamps,rows}, G2 --quick pinned to `taskset -c 12-15`.
- **Landing chain pattern:** one detached script
  `worktrees/memfn-slot/slotN/run.sh` (see slot13/run.sh: census → identity
  gate x7 sets via armjudge.py → full G2 → make test via scripts/perfrun →
  solo mech rows), launched with `setsid nohup`, its trap writes
  `verdict.txt` + `DONE`; wait with a background `until [ -e DONE ]` loop.
  Verdicts from make's `*** [Makefile:N: test-X]` lines. Restore
  docs/dev/artifact_size_log.tsv after make test; never commit it.
- **Every kit lane** runs `python3 scripts/m6read_check_sab_anchors.py`
  before delivering.
- **Blinded G2:** the D27 cell is `worktrees/g2u-cell`; diff it back into
  `worktrees/g2u` (branch g2u), commit there, merge into the kit branch.
- **PACING (Frank via main, 2026-10-08 night):** subscription was at 89%,
  reset 07:00 local. One lane at a time across sessions until the reset.
  After the reset, normal capacity (2 migration : 1 SIMD, D147 add. 11).

## 4. Current state (2026-10-08 ~23:30)

- **R-8 / M7: DONE and MERGED** into main (kit branch lane/memfn-m7 @
  5fc36ccf; main merged 33c02ac9+ and pushed). slot13 green on every stage;
  mismatch_inplace pcrec_floor pinned 2116. Worktrees m7, m7fix, s670cell
  pruned by main. The kit worktree is still on lane/memfn-m7 (merged):
  switch it to the next unit's branch before working.
- **R-10 / M6 (VMSTRIDE only): BUILT** on lane/memfn-m6 @ e48cc296,
  STACKED on an older m7 (00b1f3da). MF_SITE_ABI 8, MF_MAX_TERM 32; shadow
  0 mismatches, 62,216 pairs 0 movers; N6 retired (D147 add. 12). Report
  docs/dev/lanes/m6_report.md (§7 G2 needs, §8 slot chain, 66 mech rows).
  **NEXT (after 07:00):**
  1. Relaunch blinded lane **g2m6** (stopped tonight before writing
     anything; the cell `worktrees/g2u-cell` is refreshed from the m6 tip
     and clean). The cell has no m6_report, so PASTE m6_report §7 into the
     brief (this session's brief did: W in {1,2,3,7,8,9,16,31,32}, the
     strided oracle, guard pages, hooks present/absent, refusals, rows/K1,
     W1/W2, sabotage a/b/c; deliver memfn/tests/G2M6_REPORT.md; sonnet).
     Then ff g2u to lane/memfn-m6, diff the cell into worktrees/g2u,
     commit, merge into lane/memfn-m6.
  2. Merge **main** (now containing M7) into lane/memfn-m6, ALONE, then
     strict. Expect conflicts: S512, manifest/floor literals (C17 floor,
     row_floors), the lanes index, integration.md rev marks.
  3. Ask main for M6's slot (write slot14/run.sh from slot13's shape +
     m6_report §8's mech rows).
- **R-9 (SIMD design): text DONE**, lane/memfn-r9 @ 5a9e8c4c (r9c pass:
  Q-R9-10 shape (c) selector-body rule, Q-R9-11 `freq` column, Q-R9-1..11
  RULED, C18 leg (d) selector-only; old probe numbers labelled as taken on
  the superseded rendering). **NEXT:** a LIGHT re-check panel (2 read-only
  critics: contract/consistency vs D155+add.1, docs staleness), consolidate
  into docs/dev/reviews/2026-10-0N-r9b-memfn-simd.md, then `done: R-9`.
  Rev 4.9 vs the kit tip's rev 4.8 [M7] text must be reconciled at merge.
  Batch 1's build request comes after main files it.
- **Frank discussion, 2026-10-08 night (not a directive, nothing
  scheduled):** a fused "byte x && cond" SIMD form (packed pair, cf. the
  filed `vrun` over `fn-memchr` row, §R4.9.7.1) wins by avoiding memchr
  restart churn; the regime is really "restart frequency". Frank also
  suggested prioritizing SIMD direction by category frequency (memchr /
  memchr2 / class / caseless). We have no population census of site
  categories (requirements.md U-2 names the class-shape gap). If asked: a
  static census of the bench corpus through the MF_TRACE build (cheap),
  then a time-weighted share from the bench (pcrecdev2); priority =
  share x winnable margin over the scalar layer.

**Worktrees:** memfn (kit home), m6, r9d, r4h (untracked r4h_rulings.md:
check before pruning), m4, g2u + g2u-cell (keep), memfn-slot (scratch).
Prune m6 after M6 merges, r9d after R-9.

## 5. Next actions on wake

1. Heartbeat cron at 17,47. ListAgents. Read requests.md for anything new.
   Confirm with main that the pacing hold has lifted.
2. Relaunch g2m6 and the R-9 light re-check panel (both light).
3. After g2m6 lands: merge main into m6, then ask for M6's slot.
