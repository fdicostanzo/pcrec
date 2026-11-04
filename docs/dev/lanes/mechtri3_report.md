# mechtri3 report: triage of the full suite's mech red (run 20261103_4bd002e20)

Trailer: `mech run COMPLETE: 1102 rows (unexpected: 1, undetected: 18, unreached: 17, anomalies: 23)`; stage rc=2.
rc=2 comes from the ONE unexpected row, S512. The 18 UNDETECTED are all declared-expected, the 16 other UNREACHED are all
declared-expected, and the 23 ANOMALYs do not turn the stage red (10-27 run: anomalies 31, mech green). No (b) real miss.

## Failures

| row | outcome | class | cause | new since 10-27 | fix |
|---|---|---|---|---|---|
| S512-c17-row-below-floor | UNREACHED (unexpected) | (a) stale | p1build 8936a8156 listed the LMHIT site and raised C17_ROW_FLOOR 14 -> 15; the row's REACH_POP still read `=14`, so the witness no longer reached the plant | y | POP re-pinned to `=15` (row file only) |
| S86-kreset-write-untrailed | ANOMALY BUILD-FAILED | (a) stale | vmrec b88e0dda3 removed `v->b`/`b`; the plant's direct `pcrec_sb_printf(b, ...)` no longer builds | y | re-aimed: vm_stmt.c pair (below) |
| S709-vmlazy-counted-loop-respelled | ANOMALY BUILD-FAILED | (a) stale | same (vmrec); plant printed from emit_vm.c | y | re-aimed into vm_r_span (vm_stmt.c) |
| S41-ir-label-drift | ANOMALY BUILD-FAILED | (a) stale | same (vmrec); `v->b` | no (was on the 11 stale) | re-aimed: `pcrec_vm_b_label(v->sb, ...)` without `vm_ev` |
| S53-counter-untrailed | ANOMALY BUILD-FAILED | (a) stale | same; was `stv` undeclared on 10-27, now `v->b` | no | re-aimed: vm_stmt.c pair |
| S56-counter-empty-guard | ANOMALY BUILD-FAILED | (a) stale | same | no | re-aimed: `pcrec_vm_b_branch(v->sb, vm_condf(...))` |
| S57-counter-trip-local | ANOMALY BUILD-FAILED | (a) stale | same | no | re-aimed: vm_stmt.c pair |
| S1822-lmwalk-row1-body-route | UNREACHED (EXPECTED) | (d) declared | p1build dc6a40dfb declared it | y (new row) | none |
| S917, S919 | UNREACHED (EXPECTED) | (d) declared | span_pick 1f, as briefed | no (witness text changed only) | none |
| S1029 S1126 S1160 S121 S475 S479 S496 S497 S685 S891 S895 S901 S904 | UNREACHED (EXPECTED) | (d) declared | each carries its own EXPECTED text; all were on 10-27 | no | none |
| S1119 S1141 S1352 S150 S151 S152 S153 S160 S178 S219 S487 S489 S490 S525 S602 S903 S-U6 S-U9 | UNDETECTED (EXPECTED) | declared | each points at its SAB_DOC_FIGURE; all were on 10-27 (S1255, S1256 left the list) | no | none |
| S07-ts1-errno, S1112-partlayout-p2-dropped, S184-frame-size-from-wrong-struct, S1242-ks-measures-includes-internal, S989-ksrc-parts-include-internal | ANOMALY (plant does not compile) | (c) designed compile-time catches, none on the 12-id MECH-NOCOMPILE list; the classifier cannot tell them from stale plants | on the 10-27 list of 6 designed catches (S526 has since gone) | no | none (plan row: runner needs a per-row declaration) |
| S1152 S1159 S1174 S231 S272 S666 S676 S707 S719 S739 | ANOMALY (-Werror in the plant) | (c) kind A, ALL ten are on MECH-NOCOMPILE's list of 12 (S135 and S1418, the other two, no longer score ANOMALY) | no | none (described only) |
| S271-var-emit-arm-ignores-caseless, S403-clspack-respell-skipped | ANOMALY (plant does not compile) | (c)/(a): `rx_span_match_caseless` / `rx_class_bitmap0` undeclared in the generated C (the emitted names moved). NOT on the MECH-NOCOMPILE kind-A list (they are in its "11 stale"); described only, as the plants need a generated-text re-anchor outside this lane's scope | no | none |

No (b) (a sabotage the suite no longer detects while its code still runs). No (e) tool fault, no (f) flake/timeout seen
(mech.log has no FATAL or timeout line).

New since 10-27 (from a diff of the two logs' non-DETECTED sets): S512 (unexpected), S1822 (declared), S86 and S709 (stale).
Gone since 10-27: S106 S1084 S135 S1418 S36 S448 S51 S526 S677 S678 (anomalies cleared) and S1255 S1256 (undetected cleared).

## Dispositions

Re-aimed in place, ids kept, commit 6ea484eaf on lane/mechtri3. Each plant was applied to a scratch copy of HEAD with
tests/mech/lib/replace.py and the compiler built (`make all`): all six BUILD-FAILED plants now BUILD-OK; the S86 plant's
emitted text was checked (`slot_values[0] = (ptrdiff_t)scan_position;` for `(?:a\K|ax)c`). The detection arms were NOT run.

- S512: REACH_POP `^C17_ROW_FLOOR=14` -> `=15`, header note added.
- vmrec made emission record-first (`v->sb`; no raw printf), so S53/S57/S86 are now a two-file pair: the emit_vm.c site marks
  its `vm_set` source with a leading `\x01`, and vm_r_set (src/gen/vm_stmt.c) prints a marked source as a plain
  `slot_values[n] = src;` store instead of the trailed SET. Same defect as before: value written, old value not trailed.
- S709: plant moved to vm_r_span (vm_stmt.c), which prints `while (it_ < %dUL) {` (with a `break`, so the planted loop is finite).
- S56: `pcrec_vm_b_branch` replaces the raw print. S41: `pcrec_vm_b_label` alone (label printed, no listing event).

Re-validation: queued `322-main-mechtri3` (rows S41 S512 S53 S56 S57 S709 S86, runs in the lane worktree; expected all 7
DETECTED). Its script: $PCREC_TMPDIR/scratch/mechtri3/jobs/mech.sh (--dry-run passed). Caveat to read the verdict against:
S53, S57 and S709 have not been seen to emit their planted text with the quick patterns tried (routing), so a
DETECTED vs UNREACHED/UNDETECTED outcome on those three is the real check; an UNREACHED means the REACH witness needs a
different pattern.

Suggestions, not done: MECH-NOCOMPILE should add S271 and S403 to its inventory (generated-text names moved).

## STATE AT HANDOFF

- Branch lane/mechtri3 at 6ea484eaf plus this report; rulings file empty (no entry applied).
- Owed run: 322-main-mechtri3 queued (box queue), verdict not yet read. Nothing else running from this lane.
- Scratch under $PCREC_TMPDIR/scratch/mechtri3/ (job script, plant build trees t_*, logs).
