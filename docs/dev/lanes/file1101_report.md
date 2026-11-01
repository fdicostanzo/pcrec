# file1101 report: six owed plan rows and a lesson (docs only)

No build, no run (bench timing window 2026-11-01 until 17:50); edits and grep only. `plan_lint.py`: 264 rows, 0 violations.

1. [IFACE-PUSH] candidate (a)+(b): docs/design/plan_row_bodies/IFACE-PUSH.md; small row [PIN-MSG-DEPTH] in plan.md Backlog. SHA: see commit "file1101: items 1-4, 6".
2. [INLINE-C] FYIs (i)-(iii): docs/design/plan_row_bodies/INLINE-C.md. (ii) AGREES with the spec (match_api.md §11.9: `ctx->user` is `NULL` at a code site), so a note, no K row. (iii) is a pcrec-side check owed, no lane.
3. [X-NEL-RAW]: plan.md Backlog, with the exact .rxt case (`pattern-esc "(?x)a\x85b"`, `m "ab" 0 2`, `n "a\x85b"`); NOT run. Spec §3.2 already promises the byte skip under `-e byte`.
4. [LM-SPINE-DEPTH]: plan.md Boonies. The functions are NOT on main; they are on branch lane/p1build (worktrees/p1build/src/gen/lmwalk.c: lm_flatten line 57, lm_maxw line 80).
5. Lesson 3.ac in docs/dev/learnings.md (job 624/758, lane axtri).
6. [QORDER]: plan.md Backlog, STATE:not-started, starts after the bench window 2026-11-01 17:50; [QUEUE-CAPKILL] kept as its own row and referenced (fold-in noted in both).

## STATE AT HANDOFF

All six items filed and committed on lane/file1101. Rulings file: last entry applied = "(none yet)". Nothing owed. Not merged.
