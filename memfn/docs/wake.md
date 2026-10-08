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

## 4. Current state (2026-10-08, ~09:45)

**On main:**
- N4 + G2 per-row floors (37462a8e);
- R4h prep (MF_SITE_ABI 5, hook classes);
- the frozen ADVANCE target;
- main's layout normalization (c4c37af8, abi 67) and [NULLABLE-ANCH] (abi 68).

**Delivered, awaiting main's merge:** `lane/memfn-r4h` @ 1428d550, R4h (M3).
STAY, EDGE and VMSPAN are delegated; zero movers, no abi event.
- slot10: identity gate 0 movers, G2 full 173.8M/0, make test 655 s, 18 mech
  rows clean.
- The census re-run after `generic` became a `pcrec` row in rows.tsv: rc 0.

Do not add commits to that branch; this wake.md is on lane/memfn-post-r4h.

**Rulings to remember:**
- K-1: fn_ref is a hook id, 0 refused.
- on_miss_leaves = 1 means the result is UNSPECIFIED on a miss.
- mf_emit gates both phases.
- §19 row 6's rarity half waits for C5b; the §19 T4-count row is FILED.
- A test-codegen re-run is a HEAVY slot.
- Heavy slots write DONE + verdict.txt.
- Merge the new main into a kit branch BEFORE its identity gate (main tells
  you the sha).

**OWED / next** (each needs a request or trigger from main, D77):
1. Main merges lane/memfn-r4h. Then cut the next kit branch from main.
2. Per integration.md §22, after R4h:
   - M4 (MLINE, zero movers, C12 memchr 1 -> 0);
   - M6 (N6 + VMSTRIDE, needs an MF_VOCAB bump);
   - R4j/M5 (planner live);
   - M7 (N7).
   Wait for main to file the request (R-n). The in-loop MOVERS
   (U-3 + a class-run Linux cell) stay untriggered.
3. PF movers (U-2 + a Linux cell in pf_emit_bcls). M7 scope +1 (K94).

**Leftover worktrees:**
- prune with `scripts/wtprune --apply NAME` once merged and idle:
  r4hprep, advtarget, r4h;
- keep g2u + g2u-cell.

## 5. Next actions on wake

1. Cron heartbeat at 17,47. ListAgents; check whether lane/memfn-r4h is merged.
2. Read requests.md for a new R-n.
3. Continue §4.
