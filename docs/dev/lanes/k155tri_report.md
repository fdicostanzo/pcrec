# k155tri report

STATE: delivered, validation OWED (two queued jobs)

## Summary
The RED `200-k155fix-codegen` (make test-codegen, rc=2) was one failing check, [SABANCHOR]. The branch's own change moved the text S256 anchors on. It is a stale pin the branch owed a re-anchor for; emitted bytes are untouched.

## Diagnosis
Log: worktrees/.boxqueue/failed/20261124T112903.423578240-200-k155fix-codegen/job.log, verdict `make: *** [Makefile:737: test-codegen] Error 1`; the one FAIL line is [SABANCHOR]. `scripts/m6read_check_sab_anchors.py` reports 1 stale anchor of 1407 rows: S256_sb_ctx_nomem_neutered.sh, src/core/sb.c, ANCHOR NOT FOUND. Re-run alone in the worktree: same one row, nothing else. The branch rewrote `sb_grow`'s heap-failure arm into the `sb_nomem` helper, so the 4-line SAB_BEFORE block no longer exists.

## Class
- Defect class: a sabotage row's source anchor not re-derived after the branch edited the anchored lines (stale pin).
- Rule: tests/mech/sabotages/CLAUDE.md Conventions (anchors re-derived from live source); the lane's own emit sweep could not see it because it is a source-text pin, not an emitted byte.
- Siblings: the whole-tree checker (`python3 scripts/m6read_check_sab_anchors.py`) covers all 1407 rows; the branch touches 17 src files and only this one row went stale. 6 rows anchor src/core/sb.c (`grep -l 'SAB_FILE="src/core/sb.c"' tests/mech/sabotages/*.sh`), the other 5 still resolve.
- Class-level fix shape: the checker already is the class gate; the lane step is "run it after editing any file a sabotage row names" (SAB_FILE grep), before queueing codegen.

## Fix
S256 re-anchored at `sb_nomem`'s `if (sb->cx) pcrec_ctx_nomem(sb->cx);` (the one place the nomem route now lives; same neutering, same intent). Checker after: "all anchors resolve". Commit 078107e4e. No src change, no new mechanism, no emitted-byte change, within R-1..R-3.

## STATE AT HANDOFF
Rulings applied: none (k155tri_rulings.md empty).
OWED, queued by key (non-timing, refuse-after 19:30):
- `200-k155fix-codegen` (re-queue, same key; verdict = `*** [..test-codegen] Error` lines absent)
- `200-k155fix-mech-s256` (detection of the re-anchored S256; expect `== mech run COMPLETE: 1 rows` with 0 undetected)
Job scripts: $PCREC_TMPDIR/scratch/k155tri/. The other queued jobs (asan, ubsan, mg-*) untouched.
