# j4fix report — TIMED-SHAPE crash on J4's null bases

## Summary

The full slot sabotage table's CONTROL was red: the unplanted tree's J4 dry run crashed in link.py
(`TypeError: 'NoneType' object is not subscriptable` at `timed_shape_check(..., fc[0])`). Fixed in
`docs/design/memfn/span_cards/slot/link.py`: the arms that reach that call with no cell are J4's null verify bases;
they are now keyed by a new `timed_form(a, fc)` (form `null`, a declared `TIMED_CALLEES` row allowing no callee),
and every other cell-less site wrapper refuses instead of being silently skipped or loosened. All FIDELITY-1
refusals (section symbol, cold split, indirect call/jmp, external outside the row, a function the object defines)
apply to the null bases unchanged. Harness code only: no emitted TU text moved, so nothing any timing arm times or
records changed (STOP RULE not reached).

Premise test: `run.py dry J4` on 963befa92 reproduced the TypeError (log
`/var/tmp/pcrec-pcrec/scratch/memfn/j4fix/j4pre.out`, rc 1).

## Cause

Lane mcfixb's de4413cbb (r6 FIDELITY-1) changed the call to `timed_shape_check(a.name, o, sym, fc[0])` to key the
callee allowlist on the cell's form. `render()` returns `fc = None` for J4's null bases (`base.null.<cls>`, kind
`verify`, form `null`): a null base is its class arm's WRAP_CMP text with the compare removed, so it has no cell
(no cell-text hash, no cell_text.tsv row) — but its TU still carries `SLOT_GATE_TU`, so it takes the shape-check
branch. The J4 plan adds the null bases first, so arm 0 crashed. The other cell-less arms (J5 `enter`, J1 `j1`)
are whole artifacts without the gate split and never reach that branch; `ctl` (form `walk`) has a cell. No other
reader of `fc` assumes non-None (grep: `render`'s own recursive call discards it; the cell-text block is guarded by
`if fc:`; the shape self-test passes a form string; est.py/run.py/art.py/d197_rule.py never touch `fc`).

What the null bases time: the class arm's candidate pointer-bump loop with `slot_null(first load)` in place of the
compare (a load kept through an empty asm). Their legitimate callees: NONE — the J4 dry run's arm-0 object
(`a0_time`, pre-fix scratch) disassembles with no call/jmp relocation at all; `slot_ld`'s fixed-size memcpy inlines.

## Fix

- `link.py`: `TIMED_CALLEES` gains the declared row `("null", ())` (J4's null bases: no call). New
  `timed_form(a, fc)`: the cell's form when there is a cell; `null` for a `verify`/`null` arm; otherwise a
  `TIMED-SHAPE ... a site wrapper with no cell and no TIMED_CALLEES key` refusal. `build_objs` calls
  `timed_shape_check(a.name, o, sym, timed_form(a, fc))`.
- `link.py shape-selftest`: two new cases resolved through `timed_form(Arm, None)` exactly as build_objs does: a
  J4 null-base control (inline, ok) and the plant `[S3220] a J4 null base with an out-of-line callee` (an external
  `mf_ext` call), REFUSED `external mf_ext (form null's TIMED_CALLEES row allows none)`. Self-test: 9 cases, 0 wrong.
- `sabotage.sh` row (m6) S3221: `timed_form`'s null branch returns None (the null base unkeyed, "any external");
  detected by the shape self-test's S3220 case going WRONG. Row added to the default list.
- slot/CLAUDE.md: the null row, the selftest's cases, the m6 row.
- `sabotage.sh` rows k and m1 re-anchored on current text (see Full table).

Validation (logs under `/var/tmp/pcrec-pcrec/scratch/memfn/j4fix/`):
- est selftest: `== est SELFTEST ok: 68 cases, 0 wrong` (est.out)
- d197 drill: `== d197 DRILL ok: 51 cases, 0 wrong` (d197.out)
- link shape selftest: `== link SHAPE SELFTEST ok: 9 cases, 0 wrong`
- dry J4 rc 0 (j4.out; 35 arms, 7 launches, gates and round checks ok), JMB rc 0, JMH rc 0, J2 rc 0
  (dry_*.out); no TIMED-SHAPE refusal on any arm
- tests/memfn/run_arch_blind.sh: 17 passed, 0 failed; `make strict` rc 0
- sabotage m5 m6 alone: 2 DETECTED, 0 MISSED (controls J2, est, shape green)

## Full table

`sabotage.sh` with no row filter, once, in the foreground under `gnutimeout 2700` at eaba9ae9c (log
`/var/tmp/pcrec-pcrec/scratch/memfn/j4fix/full.log`). Every control GREEN (J2, est, J3, J4, plan, JMB, JMH, d197,
d197e2e, shape — J4 being the one that had been red). Final line:

    == slot sabotage: 64 DETECTED, 2 MISSED of 66 rows

The two non-detections were neither mine, and both were stale since mcfixb/mcfixc:
- **k MISSED** (wanted CELL-TEXT MISMATCH). The plant rendered walk's arm from libc's row, and since r6's
  TIMED_CALLEES the timed-shape check refuses that first (`TIMED-SHAPE ctl: a0_time calls external memchr (form
  walk's TIMED_CALLEES row allows none)`): a correct refusal, but from a different check than the one the row
  tests. Re-anchored with the same intent ("an arm rendered from another entry row's text: cell-text refuses"),
  flipped round: the libc arm rendered from walk's row (its facts too, so walk's `mf_tbl` table is emitted). Walk's
  inline site calls nothing, so the shape check passes and the cell-text check is what refuses. Re-run alone:
  `k DETECTED (J2 dry run rc 3: CELL-TEXT MISMATCH kit.find_byte.libc: site text bc7b2e02f06fe955, the hash of the
  instance its key names (libc -) d7672e87c1dd6d97)`, `1 DETECTED, 0 MISSED of 1 rows` (re2.log).
- **m1 PLANT FAILED** (counted as MISSED): its anchor `        if got != pin:` became `        elif got != pin:` in
  mcfixc's r7 RULE-2 (a6b7ea344). Re-anchored on the `elif`. Re-run alone: `m1 DETECTED (est ...: [r6 FIDELITY-3]
  two keys' cells swapped after finalize: refused by the record's cells pin WRONG)` (re.log).

The new row m6 (S3221) was DETECTED in the full table. With k and m1 re-run, all 66 rows are DETECTED, 0 PLANT
FAILED, 0 MISSED. (The full table was not re-run after the two re-anchors; per the brief, only those rows were.)

## STATE AT HANDOFF

STATE: done. Branch lane/memfn-mcfixb. Rulings file j4fix_rulings.md: empty at every checkpoint; last entry
applied: none. IDs used: S3220 (shape-selftest plant), S3221 (sabotage row m6); S3222-S3223 unused.
OWED: none
