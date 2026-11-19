# Lane r45e report: R-45 reply rev 5 (main's check r45read, Q2-Q5 as the kit answered)

Lane r45e (opus), 2026-11-16. DESIGN ONLY: no code, no timing, no box jobs, no build.
Worktree `worktrees/r45`, branch `lane/memfn-r45` (started at fee80b67b).
Input: main's check `git show lane/r45read:docs/dev/lanes/r45read_report.md` (C1-C11, Q1-Q5),
the kit's answers Q2-Q5 that main accepted, the owner's three rulings and main's five answers
(all 2026-11-16, via the brief).

## Summary

- `docs/design/memfn/r45_reply.md` is now rev 5. It opens with a "Changes in rev 5" table keyed
  by Q and C id.
- **Q2 / C10.** The dominance-cycle clause is recorded as RULED by the kit manager in §0, R1,
  the night order (step 1 commits this text) and §8. "awaits our ruling" is gone everywhere.
- **Q3 / C1, C8.** "The stability trade" is replaced by "Which sites move".
  - Population: EVERY window site, cover or not. That means covers, pre-check run spans,
    reseed and prefix alternatives, and any site in `WF_STATES`.
  - Predicate: a site is a possible mover if one of its stated spans has a stretch of two or
    more consecutive positions with byte-identical sets of two or more members, and that
    stretch reaches an offset at or past h\*.
  - Every window span pcrec states today has 32 positions or fewer. So h\* >= 32 moves nothing.
  - Main's sweep predicts movers from pcrec's OWN statements: offsets, member sets, member
    counts, adjacent-set equality, and h\*. The prediction is a superset, so a stretch of a
    one-bit cube such as `[aA]` is predicted but does not move. Red is a move outside the
    prediction.
  - uuid (`k` = 36) has no cover today. It is a width event, not a form mover.
- **Q4 / C6.** The cards now time cover_cap.md §11.4's five regimes, NOT-WARM and
  `short-subject-search` included, by §11.4's methods, plus uniform random bytes. R1's worst
  cell ranges over all of them.
  - A bound is derived: H(64) is I at every C1-C2 cell, so W(h\*) <= (1 + f) x min W, which is
    about 1 + f.
  - Every §11.4 B cell is at length 24-64 or is a literal. So a loss the loop form causes moves
    h, never the width default.
  - Added cost, UNMEASURED: 360 arm-cells in C1-C2 (720 -> 1080, +50 %), 48 in C3, 26 in C5,
    plus A/A. That is about 440 cells, each at least 5 launches.
  - A void cell is re-run once. A cell void twice counts as a loss for every head whose text
    differs from I in it.
  - If the bench's NOT-WARM or short-subject method cannot run on the kit's harness, those
    cells run on the bench. That is a bench-only question for main to relay.
- **Q5 / C3.** Every place now says the width cells run on the REBUILT binary after the
  identity check: "The procedure", the rev-1 F12 row, the rev-3 FREEZE NOTE row, the head
  lever's bench bullet (rev 4's lever-binary alternative is withdrawn) and §7.
- **Rulings recorded as RULED** in §0, "Scope" (plan A of record), §4, §5's abi paragraph,
  Goal 4, §7 (rewritten as "The questions, all RULED") and §8:
  - the owner's three: forms now, keep-short-spans no, near-miss-fix-later no;
  - main's five, each YES, with night-order-edits unconditional;
  - the kit's dominance-cycle clause.
- §8 is rewritten: 37 lines inside the fence (limit 40).
- **Drills.** The R1 steps (1)-(4) did not change. Rev 5 adds only R1's input regimes and the
  twice-void reading, and no drill involves either. Rev 4's script
  (`/var/tmp/pcrec-pcrec/scratch/memfn/r45d/drills.py`) was re-run with `python3 -I`. The
  output (`/var/tmp/pcrec-pcrec/scratch/memfn/r45e/drills.out`) is byte-identical to r45d's
  `drills.out` (`diff` empty, rc 0).
- **Index.** `docs/design/memfn/CLAUDE.md` gets the rev 5 line (11,350 B; the size check
  passes). This report is indexed in `docs/dev/history/claude_md/docs__dev__lanes.md`.
- **Finding for the manager.** That index has no line for `r45d_report.md`. Lane r45d did not
  add one, and this lane did not add it on r45d's behalf.

## Fixes by id

- **Q2 / C10 (kit's).** Applied in §0 "Readiness", the R1 row step (3), night order step 1,
  §7 "dominance-cycle" and the §8 READY and (3) lines.
- **Q3 / C1 (kit's).** Applied in §3 "Which sites move". The §3 cover_cap edits gain the
  §11.1 prediction edit. Its wording is main's (r45read E13).
- **Q3 / C8 (kit's).** Applied in the same section: the uuid bullet.
- **Q4 / C6 (kit's).** Applied in:
  - the card table's C1 regimes (C2, C3 and C5 inherit them; C3's "NOT-WARM where the bench
    supplies" is folded in);
  - the R1 input column;
  - "Why each choice": why R1 reads every regime, with the bound, and the void reading;
  - "The procedure": the regimes' methods and the added cost;
  - §6 Q1;
  - the §11.4 "Regimes" edit for main.
- **Q5 / C3 (kit's).** Applied in "The procedure" ("Which harness and which binary"), the F12
  and FREEZE NOTE rows, the head lever's bench bullet, and §7 "The order of the timings".
- **C4 (kit's part).** §4 now states that the forms are not a near-miss fix: every form
  restarts one byte later, so the O(n·k) count is unchanged. The kit step of EMITTED-2's order
  is therefore empty until the skip's trigger fires. The cover_cap.md sentences are main's
  (E7).
- **C5 (kit's part).** §7 "forms-now-or-next" states the predicted outcome plainly: on a tie,
  the landing ships today's bytes at every span of 64 or fewer positions and loops only past
  64.
- **C7 (kit's part).** "The option" explains why `no-span-loop` is the G1 deny every
  byte-moving kit row carries (D144 item 4), not the dial's always-inline option, which stays
  a dial cell. cover_cap.md §11.3's sentence is main's (E14).
- **C11 (kit's part).** The §11.6.1 edit text now has two steps: (4a) the cards, then (4b) h\*
  compiled in plus the identity check. Whether (4b) gets its own review is listed in §7 as
  main's call.
- **C2 (main's).** B4 and a pcrec bound for reach 64 are main's. The reply's fact is
  unchanged: the kit names no 32/64 bound.
- **C9 (main's).** The B5 plant and the §11.6.3 rows are main's. The reply already specifies
  two rows.
- **Not addressed.** r45read Q1 (who respells pcrec's callers and tests on the kit's build
  branch) was outside this brief. §7 says so.

## STATE AT HANDOFF

- STATE: done. Commits on `lane/memfn-r45`:
  - e76b5279b: deliver file, unchanged;
  - c93dbf848: rev 5, the CLAUDE.md line and the history index;
  - the report commit after it.
- RULINGS FILE: `docs/dev/lanes/r45e_rulings.md` was empty at start and empty when re-read
  before handoff. Last entry applied: none.
- No `memfn/docs/requests.md` or `responses.md` edits, no code, no timing, no box jobs.
- lanecheck: rc=1 on ONE issue only: the untracked `r45d.done` at the worktree root. It is a
  prior lane's pass record, not this lane's, and it was present at start. The lane neither
  commits nor deletes it (the deliver file has no `dirty-ok`). The manager removes it or adds
  `dirty-ok: r45d.done`, and lanecheck then has nothing else to report.
- OWED: none
