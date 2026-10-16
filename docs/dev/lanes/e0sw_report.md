# e0sw report: integration prep of lane/e0b + lane/swfix (2026-10-16, sonnet)

Branch `lane/e0sw`, from main c0918ecc4. Nothing merged to main. The full
`make test` is OWED: armed behind `.lift` (below), not run by this lane.

## Merges
1. `git merge lane/e0b` (f6fef2ec1): ONE conflict, `docs/dev/lanes/CLAUDE.md`
   (the brief expected none): main's tail gained `wcfix_report`/`cmprev4_report`
   index lines and e0b appended `e0build_report`. Both are pure appends at the
   same spot, so both were kept (mechanical). Merge commit f47e29d2b.
2. `git merge lane/swfix` (6c81f60ac): clean (`ort`, no conflicts).

## Strict and cheap suites (tip of lane/e0sw)
| check | result |
|---|---|
| `make -j16`, `make strict` | rc 0 / rc 0 |
| `make test-plan-lint` | rc 0 |
| `make test-spec-history` | rc 0 |
| `make test-compound` | rc 0 (includes e0b's new E0 rank check) |
| `make test-memfn-rows` | rc 0 |
| `make test-registry` | rc 0 |
| `make test-rxtsource` | rc 0 |
| `scripts/m6read_check_sab_anchors.py` | 733 rows / 757 anchor sites, all resolve |
| `make test-codegen` | RED once, then fixed (below); the fixed script re-ran standalone green: `bash tests/codegen/run_codegen_tests.sh`, `checks failed: 0` |

No sabotage-count pin moved: S1008 (e0b) and S1047/S1048 (swfix) are distinct
ids and the anchor sweep and registry suite read them without re-pinning.
Not run: the mech matrix itself and swfix's `emitsweep` mech arm; both belong
to the full chain.

## Fix (one commit)
`[K37]` in `tests/codegen/run_codegen_tests.sh`: e0b's new line
`tests/compound/run_compound_unit.sh:57` (`CC="$CC" python3 .../check_entry_ranks.py "$DRIVE" "$PCREC" ...`)
is an unbounded-looking `$PCREC` site. Its only subprocess call is the drive
with `timeout=3600` python-side, and the `PCREC` argument is documentation only,
so the same python-side-bound allowlist pattern that covers `check_entries.py`
was widened to `check_(entries|entry_ranks)` and its reason text extended.
Bookkeeping only; no test logic changed.

## Armed run
`build/v/run.sh` (gitignored, in the worktree): loops `sleep 30` until
`worktrees/e0sw/.lift` exists, then
`scripts/perfrun --label e0sw -- <worktree>/build/v/test.log`, then writes
`rc=<make rc>` to `build/v/DONE` (rc captured as `rc=$?` on its own line).
Launched detached with `setsid nohup`; live PID in `build/v/waiter.pid`
(the PID of the bash process, not of the setsid wrapper). `.lift` is NOT
created: the manager creates it when the box slot opens. Read the verdict
with `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' build/v/test.log` plus the
perfrun note `build/v/test.log.perfrun` (triage rule in BOILERPLATE).
