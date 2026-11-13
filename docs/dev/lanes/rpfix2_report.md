# rpfix2 report (lane rpfix2, sonnet, 2026-11-12)

## STATE AT HANDOFF

- Branch lane/rpfix, worktree worktrees/rpfix. `python3 -I
  scripts/m6read_check_sab_anchors.py`: 1246 sabotages, `all anchors resolve`
  (was 3 stale: S463, S470, S471).
- REACH_ONLY=1 single-row runs (`bash tests/mech/run_sabotage_matrix.sh ID`):
  S463 REACHED, S470 REACHED, S471 NOT RUN (the run yielded to a queue job); OWED to the cloud mechrows run, as is DETECTED for all three
  report. Reach-only proves the witnesses reach the site; no suite was run
  (evening hold), so DETECTED is owed to the cloud `mechrows` run
  (`rpfix2-rows`, S463,S470,S471).
- Cloud runs dispatched as the last act: `rpfix2` (test), `rpfix2-rows`.
- No edits under src/ or memfn/.

## CHANGES

All in tests/mech/sabotages/, each with a RE-AIMED note:

- S463_handoff_k_minus_one.sh: BEFORE is now the `k`/`whole`/`run` lines plus
  the `[REQ-HANDOFF-L1]` comment line (the `StrBuf round` lines left that
  span). AFTER lowers K only where bounded and positive
  (`k > 0 && k < PCREC_W_UNBOUNDED`), so the unbounded branch is not entered
  by the fault.
- S470_no_clamp.sh: the `if (handoff_position - %s > %lld)` printf now sits
  one level deeper (bounded branch); indentation updated.
- S471_roundup_dropped.sh: the `pcrec_emit_start_zero(... ROUNDUP)` call moved
  into the bounded branch; indentation updated, AFTER `(void)subjvar;`
  re-indented.
