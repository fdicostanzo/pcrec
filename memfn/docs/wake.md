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

## 4. Current state (2026-10-08, ~01:55)

**On main:** N4 + the G2 per-row floors (lane/memfn-g2floor, merged as
37462a8e, make test 60/60). C5 is merged; C5b is in flight.

**Delivered, awaiting main's merge:** `lane/memfn-r4hprep` @ 5dd86a72. It is
the kit-only R4h prep: MF_SITE_ABI 5 `count_by_caller`, the
CONJ/POSTFIX/EXPR_STMT hook classes, Q-G2-5 recorded. slot9 was fully green:
census 0 would-decline, identity gate 0 movers on 6 streams, G2 full
173.8M/0, make test 718 s, 17 solo mech rows. The done: entry is posted.
Do not add commits to that branch; this wake.md lives on lane/memfn-next.

**Ruled (main, session 97): Q-R4h-1 (a)+(b).** (b) is ONE pcrec
layout-normalization mover AFTER C7, briefed by main after checking it
against refactor B. R4h builds zero-mover on top of it. Build NOTHING
pcrec-side until C7 merges. The §19 row (T4 pricing count) is FILED. The R4h
edit set is responses.md's 2026-10-08 notice.

**R4h's open design items:**
- EDGE's `member` text (`scan_test`) is pasted as a bare `&&` operand and
  exists only at render, so R4h needs a render-time class or a pcrec shape
  promise. Ask main when R4h is briefed.
- The conditional `count` use is caught only by rows check E.

**Rulings to remember:**
- K-1: fn_ref is a hook id, and 0 is refused.
- on_miss_leaves = 1 means the result is UNSPECIFIED on a miss.
- mf_emit gates both phases.
- §19 row 6's rarity half waits for C5b.
- A test-codegen re-run is a HEAVY slot: ask first while a make test is live.
- Heavy slots write a DONE marker plus verdict.txt (main polls them).

**OWED / next:**
1. Wait for main to merge lane/memfn-r4hprep. Then cut the next kit branch
   from main and rebase this wake.md onto it.
2. After C7 merges and main's normalization mover (b) lands: R4h itself,
   zero movers. Use the edit set; split vm_emit_span_scan into VMSPAN plus
   the strided loop; re-pin S214 and S72; solo-run S433, S61 and S39; add
   kit-side rows for the three unplanted bounds; C12 rows 8->6;
   STAY/EDGE/VMSPAN delegated.
3. PF movers (U-2 + a Linux cell in pf_emit_bcls). M7 scope +1 (K94).

**Leftover worktrees:**
- r4gfix: already gone.
- r4hprep: merged into the kit branch. Prune it after main merges it.
- g2u + g2u-cell: keep (blinded G2; the cell has build/libpcrec_mftrace.a).

## 5. Next actions on wake

1. Set the cron heartbeat at 17,47. Run ListAgents and check whether
   pcrecdev1 is up and whether it has merged lane/memfn-r4hprep.
2. If C7 has merged: ask main for the (b) mover's status, then brief R4h.
3. Otherwise, continue item 3 of §4's OWED list, filed work only (D77).
