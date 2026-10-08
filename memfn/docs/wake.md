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

## 4. Current state (2026-10-08, ~00:45)

**Delivered, awaiting main's merge** (main ruled: lands after
[ART-POSS-ARMS] and C5; main merges itself and re-runs rows + codegen if
main moves; do not re-merge):
- `lane/memfn-g2floor` @ 49514207 = N4 (validated: census 379 s at JOBS=16,
  0 would-decline, pcrec floors pinned, make test 680 s with one K37 red,
  fixed e8e3e1d8) + the G2 per-row floor (blinded G2rows via g2u 635c1f11,
  plus manager wiring: build/libpcrec_mftrace.a rule, G2 check (e), g2
  floors pinned; make test-memfn-g2 45.2M/0, 147 s). It supersedes
  lane/memfn-n4.

**Ruled (main, session 97): Q-R4h-1 (a)+(b).** (a) MF_SITE_ABI 5,
caller-owned counter; (b) ONE pcrec layout-normalization mover AFTER C7
(main checks it vs refactor B first). Build NOTHING pcrec-side until C7
merges. §19 row (T4 pricing count) FILED. The R4h edit set is the notice of
2026-10-08 in responses.md.

**In flight:** lane `r4hprep` (opus) in worktrees/r4hprep, branch
lane/r4hprep (from 5b6064c1): kit-only R4h prep (the counter hook, the G3
fields.def classes, Q-G2-5 and the reverse-SKIP comment, fixtures/gate
cases). Light runs only; it reports with docs/dev/lanes/r4hprep_report.md
and lists what the slot must run.

**Rulings to remember:** K-1 (fn_ref is a hook id, 0 refused);
on_miss_leaves = 1 means result UNSPECIFIED on a miss; mf_emit gates both
phases; §19 row 6's rarity half waits for C5b; a test-codegen re-run is a
HEAVY slot (ask first while a make test is live).

**OWED / next:**
1. Review r4hprep, merge into a kit branch, run its slot (identity gate,
   G2 full, make test, mech rows), deliver.
2. After C7 merges: main briefs the normalization mover (b); then R4h
   itself (zero movers on top of it).
3. PF movers (U-2 + a Linux cell in pf_emit_bcls). M7 scope +1 (K94).

**Leftover worktrees:** r4gfix, n2pool, n4 (merged): prune with
`scripts/wtprune --apply NAME...` once idle >120 min. g2u + g2u-cell: keep
(blinded G2). r4hprep: in flight.

## 5. Next actions on wake

1. Cron heartbeat at 17,47. ListAgents: is pcrecdev1 up? Has it merged
   lane/memfn-g2floor?
2. Read r4hprep's report (or its WIP commits if it died) and review it.
3. Continue §4's OWED list in order.
