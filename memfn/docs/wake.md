# memfn wake — kit session hand-off (rewritten 2026-10-07 late night; new Linux dev box)

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
  from main. Never merge to main, never push, never `cd` into another tree.
- **Scratch:** `worktrees/memfn-slot/` (gitignored). The session scratchpad
  can vanish mid-session, so do not rely on it.

## 2. Read, in this order

1. `memfn/CLAUDE.md`.
2. `memfn/docs/requests.md`, then `responses.md` (the newest `done:` entries
   and notices).
3. The tail of `memfn/docs/journal.md`.
4. `docs/design/memfn/row_contracts.md` rev 4.1 (§4 floors, §5 steps);
   `docs/design/memfn/integration.md` §22 (R4g done; R4h next in order) and
   §19 (row 6 is revised per main's ruling).
5. BOILERPLATE, coding_guide before C, learnings §3 before a check.

## 3. Box and slot rules (this box)

- One heavy suite at a time across BOTH sessions. Ask main for every heavy
  slot (census, identity gate, full G2, make test, mech), and ping main when
  it ends. Main's lanes queue behind and ahead of you.
- **Light work needs no slot:** make/strict at -j4, single compiles,
  test-memfn-{arms,stamps,rows}, G2 --quick pinned to `taskset -c 12-15`.
- **Landing chain pattern:** one detached script in
  `worktrees/memfn-slot/slotN/run.sh` (census → identity gate → full G2 →
  make test → solo mech), watched by Monitor on its log. Read the verdicts
  from make's `*** [Makefile:N: test-X]` lines.
- **Mech scope:** main's rule (b) for a src-touching migration: rows
  anchored in the changed definitions, plus kit-file rows, plus re-pinned
  rows. A kit-only unit uses rows_for.sh.
- **Every kit lane** runs `python3 scripts/m6read_check_sab_anchors.py`
  before delivering (S570 slipped once).
- **Blinded G2:** the D27 cell is `worktrees/g2u-cell`. Refresh its build/
  and memfn.h/integration.md from the kit tip before each blinded brief. Diff
  it back into `worktrees/g2u` (branch g2u), commit there, then merge into
  the kit branch.

## 4. Current state (2026-10-07, ~23:00)

**On main (all merged and pushed):**
- [MEMFN-ROWCON] N1, N2, F2 (the kit notes its libc calls), MF_MISS_N, G2u
  (blinded, with K-1's contract text), N3 (the gate ENFORCES), and G2u3;
- R-6 (main's: pcrec states MF_MISS_N);
- R4g (PF migrates; the pffind arm; r4gfix; the G2pf families).
Main tip at the last merge: d33e1d55.

**Delivered, awaiting main's merge:** `lane/memfn-n2pool` (n2_census one
pool across arms, byte-identical; done: posted).

**In progress: N4** on `lane/memfn-n4` (from n2pool), merged from lane n4:
rows.tsv (13 rows), per-row signatures with controls, row_floors.tsv
(PLACEHOLDERS), REACH_DROPPED, `make test-memfn-rows` (70/0). strict,
build and arms pass. **Queued 4th for a slot** (main's message, ~1-1.5 h).
The slot does:
1. the full census from the repo root:
   `N2_LOCK=… OUT=… CC=gcc JOBS=16 bash docs/design/memfn/probes/rowcon/n2_census.sh`.
   Expect `== N2 DONE rc=0 would_decline=0 floors=…floor_placeholder=… ==`.
   **REPORT ITS WALL TIME in done:** (main asked; it is the first real
   measurement of the pool fix).
2. `n2_report.py OUT --floors tests/memfn/row_floors.tsv --propose`, then
   pin the values by hand and commit;
3. make test on the pinned tip.
Then post done:. The G2 per-row column of row_floors.tsv needs G2 to count
per row (n4_report §7): a blinded follow-up.

**Rulings to remember:**
- K-1: a FUNC site's name is site.pred.fn_ref; fn_ref 0 is refused.
- on_miss_leaves = 1 → result UNSPECIFIED on a miss.
- mf_emit gates both phases; mf_define/mf_use do not re-select.
- §19 row 6's rarity half is deferred after C5b. The decision stays
  pcrec's; the kit gets text only.

**OWED / next:**
- After N4: the G2 per-row floor column (blinded).
- R4h (M3, the scan edge's loop + VMSPAN; check remodel overlap with
  main's C5+ first: post its edit set like R4g's).
- PF movers (trigger: U-2 + a Linux cell in pf_emit_bcls).
- M7 scope +1 (K94).

**Leftover worktrees:** r4gfix, g2u (+ g2u-cell, keep), n2pool, n4. Prune
with `scripts/wtprune --apply NAME…` (NAMES ONLY: a bare --apply would
also remove main's lanes) once they are merged and >120 min idle.

## 5. Next actions on wake

1. Cron heartbeat at 17,47. ListAgents: is pcrecdev1 up?
2. Check whether N4's slot ran (worktrees/memfn-slot/slot8 if launched) and
   whether n2pool and N4 are merged.
3. Continue from §4's OWED list. Post each R4h-class edit set to main before
   building.
