# axtri3: triage of the full suite's axes red (run 20261103_4bd002e20)

STATE: complete except the owed re-validation job.

## Failures

Source: build/full_suite/20261103_4bd002e20/axes.log (trailer rc=2). The only red is the `--memfn=` arm reach (`make: *** [Makefile:2171: test-axes] Error 1`, "checks failed: 6"). No other axis failed.

| check | failure line | class | cause | fix |
|---|---|---|---|---|
| memfn arm reach, fd-pres-pick @default and @simd byte/c-default | `FAIL: fd-pres-pick @default byte/c-default: DIFFER FLOOR 144 < 168` | (a) stale floor | P1's landmark walk (dc6a40dfb, D184) takes corpus patterns the presence pick served; they stamp "landmark-walk" and are byte-identical with and without the deny, so fewer patterns differ | floor 168 -> 144 |
| same, utf8/c-default | `FAIL: fd-pres-pick @default utf8/c-default: DIFFER FLOOR 225 < 232` | (a) | same | floor 232 -> 225 |
| same at @simd (2 lines) | identical counts at both layers | (a) | same | same pins (one table entry serves both layers) |
| precheck-assign-byte @default and @simd byte/c-default | `FAIL: precheck-assign-byte @default byte/c-default: DIFFER FLOOR 153 < 155` | (a) | same landing (the byte assign is pre-landmark-byte, tests/memfn/pins/arms.tsv) | floor 155 -> 153; utf8 219 -> 220 (measured 220, not failing) |

The "6" counts: 2 + 2 (pick, both layers) and 2 (assign byte, both layers).

## Dispositions

- All six are class (a), one cause. This is the same movement lane pinbis/pinbis2 explained for the emit_sweep `no-fd-pres-pick` floors (ef179b9f4, 167/231 -> 142/224; docs/dev/lanes/pinbis_report.md; journal session 128): R-30 moved nothing, P1's landmark walk dc6a40dfb moves 35 byte / 18 utf8 corpus patterns off the presence pick. The memfn_arm floors (168/232) were last pinned at s3fix (c8a0f8961, 2026-10-24) and never re-read after P1. Measured here 144/225 over 5017 distinct patterns, consistent with the emit_sweep figures 142/224 (a different population).
- No (b): the arm's answers-identical sweep and witnesses passed; only differ-count floors fell, and every other memfn cell (window-search 863/628, pres-set-lead, fd-pres-g1) is at or above its floor. No (c) or (d).
- Re-pin: tests/axes/memfn_arm.py MEMFN_CLASS, floors = the measured counts, population = the memfn-arm reach's distinct corpus patterns, default engine (c-vm stays 0). Commit on lane/axtri3 (commit message names the population). A comment block records the cause.
- Not done by me: I did not re-run the arm (box held by the suite).

## STATE AT HANDOFF

- Branch lane/axtri3: one commit (memfn_arm re-pin) plus this report.
- OWED: queue job 320-main-axtri3 (cap 3600, est 1800; script copy of /var/tmp/pcrec-pcrec/scratch/axtri3/320-main-axtri3) = `make -j16` then `AXES=--memfn bash tests/axes/run_axes.sh` in worktrees/axtri3. Green = rc 0 and no `FAIL:` / `AXIS FAIL` lines in its log; the memfn arm line reads OK. Dry-run passed at enqueue.
- Rulings file docs/dev/lanes/axtri3_rulings.md: re-read at report time, no entries.
