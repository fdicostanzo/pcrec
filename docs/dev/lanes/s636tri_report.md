# s636tri: mech row S636 read UNDETECTED on main; detection gap closed (2026-10-13)

Lane s636tri (sonnet), branch `lane/s636tri` off main f3aecbe71. Tests and a
mech row only: no `src/`, `lib/`, `cli/` change, no `docs/spec/` hunk, no abi
event.

## Diagnosis: a detection gap, not an unreached site, not an equivalent mutant

Before (main f3aecbe71, solo `tests/mech/run_sabotage_matrix.sh S636`):
`fallbacktable:0fail/143pass  UNDETECTED -- ZERO CHECKS FAILED`.

The plant turns drop-anchored's `.sets` sdr cell from `FIT_SDR_TO_ANCHORED`
into `FIT_SDR_KEEP`. Evidence, from hand-built trace compilers (clean and
planted, `-DPCREC_CAND_TRACE`):

- The site IS reached. `\p{L}` -e utf8 -fno-start-landing (the old `seq-anch`
  witness) still takes `drop-anchored@size`; it is not the mechwit family
  (that family needed a deny flag removed, this one still has it).
- The artifact does not move. Planted and clean output are byte-identical
  modulo the `-o` basename on `\p{L}` and on the three mechwit chains
  (`\p{L}\p{N}\p{Lu}`, `\p{N}\p{L}\p{Lu}`, `\p{L}\p{N}\p{Ll}`).
- The only visible effect is the trace tuple: `sdr=1` clean, `sdr=0` planted.

Why: the row's old reader moved. `build_anchored_dfa` used to read
`size_drop_rung`; [OPT-REVEND] L2 (LR-S12) made it read `Ctx.anchored_dropped`,
the row's FIRED bit (`compile.c` ~250, ~1863). What `sdr` still feeds is the
ladder's ordinal: `fit_premul_applies` (`< SDR_NO_PREMUL`) and the prefilter
rung (`< SDR_NO_PREFILTER`) treat NONE and NO_ANCHORED alike, `fit_anchored_applies`
cannot be offered again (`anchored_ok` goes false once the machine is
dropped), and select_engine.c:1276 only guards an impossible state. So the
plant is not an equivalent mutant (the tuple moves), but no suite read the
tuple's `sdr=` field for this row: B2's both-derivations oracle (the original
detector) was retired at B5, and the B3 `run_anchored_match.sh` K53 cell reads
the artifact, which no longer depends on this cell.

## Fix

`tests/codegen/run_fallback_table.sh` (a) SEQUENCES:

- `fstate seq-anch 1 'sdr=1'` on the existing witness.
- New DEFAULT-PATH witness `seq-anchland`: `\p{N}\p{L}\p{Lu}` -e utf8, no deny
  flag, `drop-anchored@size`, plus `fstate seq-anchland 1 'sdr=1'`. Size
  margins: 1,301,271 B with the anchored machine (30% over the 1,000,000 B
  cap), 761,331 B after the drop (24% under); `\p{L}` alone fits on
  `landing` (581,697 B) so it cannot reach the row at defaults.

Suite: `checks passed: 146 / failed: 0` on the clean tree (was 143/0).
No other file pins that count (grep: only historical lane reports cite it).

`tests/mech/sabotages/S636_...sh`: header comment and `SAB_DESC` rewritten to
the truth (the artifact no longer moves); a `SAB_REACH` probe added (asserts
`RX_ENGINE_SEL "size-cap-retry"` and `RX_DFA_MATCH "search-filter"` on the
default-flags chain). Anchors unchanged.

Why a trace-tuple detector is acceptable here: the plant is trace-only by
construction, so the trace tuple is the only observation point; the sibling
`fstate` checks (`cr=`, `latch=`, `restart=`) in the same section do the same.

After: `reach:ok(2/2),fallbacktable:2fail/144pass  DETECTED`, mech run
COMPLETE `unexpected 0, undetected 0, unreached 0, anomalies 0` at 1af4864b9.

## Neighbours (not touched)

S637 (drop-anchored note lost) sits on the same row; it was not read
UNDETECTED here. Dead-in-artifact after L2 and only ordinal-visible: the
drop-premul and drop-prefilter sdr cells ARE still read (`<` comparisons), so
they are not the same family.
