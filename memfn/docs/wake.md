# memfn kit — wake-up brief

Updated 2026-11-24 ~16:00 (EST) by the kit session ON THE MAC (M1 Max, arm64), before an expected context compaction. The kit runs on the Mac now (owner, 2026-11-23): ONE kit at a time.

## Who you are
The kit manager (`/pcrec-memfn-manager`). Register with `scripts/session_role kit`.
- **The Mac:**
  - the repo is /Users/claude/pcrec;
  - gcc is Homebrew `gcc-16` (tests/lib/cc_resolve.sh); bare `gcc` is Apple clang;
  - there is NO box queue (boxqueue and monread are Linux-only); heavy runs take `worktrees/.mac-suite.lock` (directory form + an `owner` line);
  - `scripts/gestalt` prints a false "GONE: kit" here (main is filing the fix).
- **PUSH** (owner, kit-push, in the skill §0):
  - you may push your own `lane/memfn-*` branches;
  - a CODE delivery also opens ONE PR into main (review and Linux CI only; main merges locally);
  - docs-only: push and message main;
  - tell main the branch and sha at every push.
- **Peers:** main is `pcrec-main`, over Remote Control on the dev box. Nested agents hand back to "main" (that is YOU); their send to "pcrec-memfn" is refused (it is your own name).
- **Reviews:** numbers come from main. The per-review index is `docs/dev/reviews/INDEX.md` (not reviews/CLAUDE.md).
- **lanewatch:** reports a false QUIET (rc 10) when a lane's long runs write only to scratch. Check `$PCREC_TMPDIR/scratch/NAME` mtimes, then re-arm.

## Read in order
1. This file.
2. memfn/docs/journal.md, the 2026-11-24 entries (on each kit branch: the tips below).
3. memfn/docs/responses.md, the 2026-11-24 items.

## STATE (kit branches; worktrees under /Users/claude/pcrec/worktrees/)
- **R-49 is DONE and merged on main.** The arch review memfn/docs/arch_review_2026-11.md is ACCEPTED rev 4 (reviews r91-r93). lane/memfn-arch was pushed at 5d2cfc351, then 55062c6e2 and 4d25fda9a; all are merged by main.
- **Owner ruling D204** (window-file-split, verbatim in the journal): split window.c at NEON V's trigger, ONCE, before NEON V; many small, concisely defined files; a table and the functions that search it go in one file, with only those functions public. The primitives (ARV-5 + ARV-16) move once, in the split, with kit_mass. "Yes on trigger" is the DIRECTION: the BUILD GO comes from Frank after the design re-check.
- **lane/memfn-wsplit** (worktrees/memfn-wsplit): the split DESIGN, docs/design/memfn/window_split.md.
  - rev 1 is merged; review r95 is RULED (a0742283a): NOT READY. FIX-NOW: the cut does not compile as a literal move (W15-W17); no gate runs re-aimed G2 plants (W22); the identity sweep misses the V w32 block (W28); and others.
  - O1-O7 ruled as recommended (O1: split frame/ren).
  - IN FLIGHT: lane **wsplitd2** (opus, worktrees/wsplitd2) writes rev 2 with a CUT ASSEMBLER + gcc-16 -fsyntax-only of every assembled file.
  - NEXT: merge it, then re-check **r98 memfn-winsplit2** (1-2 critics: fix-induced + readiness). Then the build-go summary to Frank via main, with O1-O7 and their numbers.
- **lane/memfn-plantcheck** (worktrees/memfn-plantcheck): the runner-plant check fix (D203 class fix, main's ruling: kit builds all of it).
  - plantfix is merged (tests/lib/plants.py, the [SABANCHOR] plant pass, the 4 re-aims). Review r94 is RULED (c1efbe938): FIX-NOW CA-1..8, GF-1 twin equality YES, GF-2 runner S1540 -> S1544 (confirmed free; the kit range is S1541-S1559), PAR-1/2/3.
  - IN FLIGHT: lane **plantfix2** (opus, worktrees/plantfix2). Its acceptance gate is the 35-mutant harness at /var/tmp/pcrec-claude/scratch/crit-memfn-plantcheck/checkadequacy/h/harness.py.
  - NEXT: review its diff, merge, push lane/memfn-plantcheck plus ONE code PR (`gh pr create`), and message main.
  - OWED on Linux: the 7 pres x86-SIMD plants ("red but not by detector" on aarch64).
- **NEON V (R-48):** HELD until the split lands (D204). It then needs its own architecture note, design, critic round and build go. x86 V is filed for the dev box.
- **Known Mac-only reds (pre-existing):** test-codegen's run_size_term.sh (python 3.9), run_case_spelling_identity.sh and run_residual_twins.sh (Mach-O); make strict rc 2 on the aarch64 targets-check.
- **Heartbeat:** cron 17,47 (session-only; re-create after a restart, not after a compaction).

## Lessons (2026-11-24)
- A peer's ask does not override the skill (the push ask; main withdrew it, and Frank then ruled kit-push).
- Check the repo's own resolver (tests/lib/cc_resolve.sh) before asking whether a tool exists.
- Name censuses miss compile breaks: a MOVE design carries a cut assembler + -fsyntax-only.
- A check needs a standing self-test; a control that lives only as lane evidence is no control.
- Owner words go into the journal VERBATIM, the same day.
