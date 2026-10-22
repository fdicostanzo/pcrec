# memfn wake — kit session hand-off (rewritten 2026-10-22 at Frank's /close)

This file is the kit session's orientation. Run `/pcrec-memfn-manager` and follow its §1 wake order. The file is rewritten at every pause and holds the current state; history lives in `journal.md`.

## 1. Who you are and where you work

- You are the pcrec-memory-functions kit manager (`pcrecdev3`). Main is `pcrecdev1`; find it with ListAgents.
- `requests.md` is main's and only main writes it. `responses.md` is yours and only you write it.
- **Box:** the Linux dev box, repo `/home/pcrec/projects/pcrec`. Use `gnutimeout`. Commit with `-c user.name="Frank DiCostanzo" -c user.email=frank@dicostanzo.com`.
- **Never `cd`**, and **never `git stash`**: the stash list is shared by every worktree.
- Remove worktrees only with `scripts/wtprune`.
- **Rulings to a BUSY lane go in its worktree rulings file** (`<lane>_rulings.md`) plus a one-line pointer message. SendMessage alone went unread twice on 2026-10-22.
- **Every queue job's `--ready)` branch starts with main's hold:** `case "$(bash /home/pcrec/projects/pcrec/scripts/boxqueue state i2build-parity 2>/dev/null)" in pending*|running*) echo held; exit 75;; esac`.

## 2. Read, in this order

1. `memfn/CLAUDE.md`.
2. `requests.md` (newest R-29, R-28) and `responses.md` on main.
3. The tail of `journal.md`, on branch `lane/memfn-ws`.
4. `docs/design/memfn/window_site.md` rev 3.2, which is the D172 design and R-29.
5. Lane reports `docs/dev/lanes/wsc1..wsc7_report.md`: the D172 build.

## 3. Current state

- **Versions:** MF_SITE_ABI is 19 on main and 20 on the D172 branch. MF_VOCAB 4, MF_CLASS_V 5. pcrec abi 82; D172 S2 has no pcrec abi event.
- **D172 S2 (R-29): all six commits are BUILT; the final validation is OWED.**
  - **Branch chain:** wsc1 → wsc2 → wsc3 (these three are merged into `lane/memfn-ws` @ 87fad066d) → wsc4 → wsc5 → wsc6 → **wsc7 @ 170c5fac6 = the landing tip**.
  - **Job 583-kit-wsc7-heavy is QUEUED** at 170c5fac6. Logs: `worktrees/wsc7/build/wsc7/heavy/` and `worktrees/.boxqueue/{done,failed}/<TS>-583-kit-wsc7-heavy/job.log`. Green means all of:
    - `== wsc7 heavy: 0 step(s) failed`;
    - five `emit_sweep: DONE rc=0`, each artifact stream at movers=0;
    - the facts stream's `DECLARED MOVES` at about 3,356 patterns (span_facts `used` yes→no);
    - `== mech run COMPLETE: 155 rows (unexpected: 0`;
    - `mech-reach-only: DONE`;
    - an empty `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'` on `worktrees/wsc7/build/wsc7/heavy/maketest.make.log`.
  - **If 583 is green:**
    1. merge wsc7 into `lane/memfn-ws` (`git merge` ALONE, then `make strict`);
    2. post `done: R-29` in responses.md with the sha;
    3. SendMessage main. Main runs its review lane on the pcrec-side commits plus the D94 ritual, then merges.
    Points for main's review: commits 4-5 were red on the G7 lever fence only (fixed forward in 6-t1); 6-p3..6-t2 carried the end_back red (fixed in 6-p4); R2 was built as the FALLBACK (general form FILED); the renderer interface move is FILED.
  - **If 583 is red:** launch a TRIAGE lane before reading the log.
- **Next after the landing:** S3 = B1, REPORT routed by default. It is a pcrec abi event plus a deny row in the same commit, with D-hors (stop mass ≥ ~146k ppm, PROVISIONAL). The acceptance bar is in window_site §6: scalar layer, against DEF, five named capped losses. Frank: "we need this regardless of where hex lands".
- **R-28:** DONE, `lane/memfn-r28` @ 4e49ed417. Main merges it after its dd10/dd10b lanes. Its one red, the variant tag floors, is base-level; the re-pin is main's (bisect job 577).
- **Job 584-kit-r27c-probe is QUEUED.** It times Frank's hex8 ideas: PB (boundary pair: left context + S_0, with c=lo checked once), PC (a second in-core probe), PBC, and the classes random and utf8 (generated). Table: `worktrees/r27c/build/r27c/job/r27c_table.md`. Completion line `== r27c COMPLETE rows=3450 launches=5`. Next: fill r27c_report.md's RESULT section and bring Frank the reading. Does "least predicted mass among single/pair/probe" pick each winner? If PB wins, it becomes one declared row plus the start-of-subject rule, after the D172 landing.
- **Unmerged kit branches:** lane/memfn-ws (with wsc4-7 to come), lane/memfn-r28, lane/memfn-r27b and lane/memfn-r27c (measurement records).
- **Nothing is running except jobs 583 and 584 in the queue.** No lanes, no crons, no watchers.

**OWED (carried):**
- the five PRES rows' g2 floors are PLACEHOLDER;
- D2 is retired in D172 6-k2;
- candoracle's reach gap is on main's list;
- F-4 (pf_walk's K96 gap) is FILED;
- the renderer interface move to a kit-internal struct is FILED;
- R2's general form (every exact stretch stated, the kit picks) is FILED.

## 4. Next actions on wake

1. Read 583's verdict, then land D172 S2 (§3).
2. Read 584's table and bring Frank the reading.
3. After main merges D172 S2: brief S3 (B1).
4. Prune delivered worktrees with `scripts/wtprune` once they are merged and quiet: wsc1-7, r28m, r28m0, vb-*, uwin*, b4p, r27b, r27c.
