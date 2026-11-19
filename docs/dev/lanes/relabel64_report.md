# relabel64 report

STATE: complete

## STATE AT HANDOFF
Comment-only relabel of WF_SPAN_HEAD in memfn/src/window.c is committed (9c90d78e9). The enum value stays 64. No rulings file entries were applied (none read). Build and strict both ran clean.

## CHANGE
memfn/src/window.c, THE DEFAULT HEAD comment only: "UNMEASURED DEFAULT" became "MEASURED: 64, label grid top, CHOSEN", citing run fcards-zen4-1 (frozen 33fec79b3, Zen 4, 2026-11-19): rule R1 picked h* = 64, card C3 complete at H(64) after its re-run. Kept: default width 32 means no span loops; R5 near-miss losses of H(64) against L (hex500 about 82 vs 41 ns/B; today's text I about 130). `enum { WF_SPAN_HEAD = 64 };` untouched. See `git show 9c90d78e9`.

## CHECKS RUN
- `boxlock run ... watchdog -s 1800 -- nice make -C <worktree> -j8`: rc 0, log /var/tmp/pcrec-pcrec/scratch/relabel64/build.log
- `boxlock run ... watchdog -s 1800 -- make -C <worktree> strict`: rc 0, log /var/tmp/pcrec-pcrec/scratch/relabel64/strict.log
- No make test, no timing (as briefed).

## FOR THE MANAGER
- Branch: lane/memfn-relabel64
- Code tip: 9c90d78e9 (the report commit follows it)
- REBUILT_BUILD: /home/pcrec/projects/pcrec/worktrees/relabel64/build (contains executable pcrec)
