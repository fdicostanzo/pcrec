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

## 4. Current state (2026-10-08 afternoon, session reset at Frank's request)

**On main:** everything through R4h:
- N4 and the G2 per-row floors;
- R4h prep (MF_SITE_ABI 5);
- the frozen ADVANCE target;
- R4h (STAY/EDGE/VMSPAN delegated);
- main's abi 68.

**In progress: M4 (R-7, MLINE), BUILT on lane/memfn-m4 @ 9c7b848e
(fast-forwarded from lane/m4; strict clean). It is NOT YET DELIVERED.**
Main acked the plan and gave sabotage ids S617-S619. Report:
docs/dev/lanes/m4_report.md.
- **Phase A (kit only), MF_SITE_ABI 6:**
  - Q-R7-1: a FIND whose terms all read below the candidate is bounded by its
    reads, so it reaches n;
  - Q-R7-2: `MF_EMPTY_AT_N`;
  - Q-R7-3: LOOP_EXIT on_miss (the generic row refuses it);
  - new row `pf_memchr_back`.
- **Phase B:**
  - `PcrecFind` was generalized (site id, term offset, floor), not cloned;
  - MLINE is delegated (10/3);
  - C12 is 5 rows / 7 forms, and no `memchr(` remains outside the kit.
- **Evidence:** shadow comparator 0 mismatches over 693 MLINE sites. After
  REPLACE, 26,268 corpus pairs gave 0 movers, and 33 witness compiles were
  byte-identical.
- **Sabotage:**
  - S82 unchanged; S524 re-pinned; S511 re-aimed to VMSTRIDE;
  - S617-S619 added on a new mech arm `memfnarms`.
- **BLOCKER: make test-memfn-g2 is RED ON PURPOSE** (19,294 fails over 46
  sites, plus check (b)). G2's oracle still uses the old FIND range, and
  nothing chooses `pf_memchr_back`.

**NEXT (in order):**
1. **A blinded G2 lane in worktrees/g2u-cell.** Refresh the cell from the
   lane/memfn-m4 tip first: memfn.h, integration.md, memfn/docs/
   trace_format.md, build/ (pcrec, libpcrec.a, and `make
   build/libpcrec_mftrace.a`).
   - Brief: m4_report.md §7. It needs the read-bounded range, an AT_N family
     at offset -1 that reaches `pf_memchr_back`, LOOP_EXIT handling, and
     FLOOR_ROWS 13 -> 14.
   - Afterwards: diff the cell back into worktrees/g2u (branch g2u), commit,
     merge into lane/memfn-m4, then pin `pf_memchr_back`'s g2_floor from its
     row-chosen count.
2. Merge main into lane/memfn-m4 (alone), then run strict.
3. Ask main for a heavy slot and run `worktrees/memfn-slot/slot11/run.sh`.
   It is already written, with 38 mech rows, and writes the DONE and
   verdict.txt markers.
   - Expect census reason_stale 0. pcrec_floor for `pf_memchr_back` is
     PLACEHOLDER: pin it from the census `--propose`, then re-run the
     rows check.
4. Post done: R-7 and send main the verdict.
5. Then M7 (N7), M6 (N6 + VMSTRIDE), and R4j/M5. Each waits for main to
   file its own request.

**Rulings to remember:**
- K-1;
- on_miss_leaves;
- mf_emit gates both phases;
- §19 row 6 waits for C5b; the §19 T4-count row is FILED;
- a test-codegen re-run is a HEAVY slot;
- heavy slots write DONE + verdict.txt;
- merge the new main BEFORE the identity gate.

**Leftover worktrees:**
- r4h is kept only because of its untracked r4h_rulings.md; move that file
  into docs/dev/lanes/ (ignored), then prune;
- m4: prune after M4 is delivered;
- keep g2u and g2u-cell.

## 5. Next actions on wake

1. Create the cron heartbeat at 17,47. Run ListAgents and check that
   pcrecdev1 is up.
2. Do §4 NEXT item 1: brief the blinded G2 lane (sonnet; the g2rows brief
   from 2026-10-08 is the model, and the G2 brief rules are in the skill §4).
