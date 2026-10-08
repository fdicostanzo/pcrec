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

## 4. Current state (2026-10-08 ~13:00)

**On main:** everything through R4h (abi 68 and the frozen ADVANCE target
included).

**R-7 (M4, MLINE) DELIVERED on lane/memfn-m4 @ c1b037d3. Awaiting main's
review and merge.** Report: docs/dev/lanes/m4_report.md (§10 is the
landing).
- Zero movers, no abi event. MF_SITE_ABI 6 (Q-R7-1/2/3), row
  `pf_memchr_back`, PcrecFind generalized, MLINE delegated.
- G2 at ABI 6, written by the blinded lane g2m4 (memfn/tests/G2M4_REPORT.md).
- Floors for `pf_memchr_back`: g2 4109, pcrec 3271.
- slot11 (worktrees/memfn-slot/slot11/verdict.txt) is green. S513 and S525
  were re-pinned UNDETECTED: equivalent mutants once pcrec has no memchr
  (triage reports S513_triage.md and S525_triage.md there).
- make test in slot chains now runs through `scripts/perfrun --label
  <name> -- <log>` (main's [TT-JTUNE]).
- A full make test rewrites docs/dev/artifact_size_log.tsv. Never commit
  it from the kit; restore it.

**Open:** main may send review notes on M4 (as a D-n or a message);
answer them on lane/memfn-m4. Q-G2M4-1..9 are posted as a notice, to be
settled in integration.md §14 at the next contract revision.

**NEXT:** M7 (N7), M6 (N6 + VMSTRIDE), then R4j/M5. Each waits for main to
file its own request. Do not start any before it is filed.

**Rulings to remember:**
- K-1;
- on_miss_leaves;
- mf_emit gates both phases;
- §19 row 6 waits for C5b;
- a test-codegen re-run is a HEAVY slot;
- heavy slots write DONE + verdict.txt;
- merge the new main BEFORE the identity gate;
- `[responses]` commits are single-file.

**Leftover worktrees:**
- r4h is kept only because of its untracked r4h_rulings.md; move that
  file, then prune with scripts/wtprune;
- m4: prune after main merges M4;
- keep g2u and g2u-cell. The cell is at the g2m4 state.

## 5. Next actions on wake

1. Create the cron heartbeat at 17,47. Run ListAgents and check that
   pcrecdev1 is up.
2. Read requests.md for anything new (D-n on M4, or the next M-request),
   and ack it.
