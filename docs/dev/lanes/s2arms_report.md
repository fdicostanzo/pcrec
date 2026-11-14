# s2arms report

## STATE AT HANDOFF
Commit on lane/s2arms (from main 370aab9fe): re-pins in scripts/emit_sweep.py and tests/axes/memfn_arm.py, no emitted byte moved. No rulings file was written (no later rulings). Re-run arms sweep and REACH stage queued as the last act (batch key b202611140752593761835); cloud axes dispatched after.

## ARMS
Red batch b20261114073238151348, arms stage rc=1 (744 s). Exactly ONE red line: `utf8 -fmemfn-simd=x86-64 c-vm differ=13/13 floor=15` (DIFFER FLOOR 13 < 15). It is NOT a run-verify-wide line (those four cells passed: pins were provisional 1, measured far above). Not a crash or missing file; arms.tsv was written (build-emitsweep/arms.tsv, 93 rows); `--emit-pins` output (arms_pins.tsv) was NOT written because the red ended the run before write_pins.
Cause: [RUN-POS-SET] stage 3 states a utf8 caseless `s`/`k` as a wide position, so vrun declines those runs by design; memfn_arm.py's vrun comment already records six corpus patterns leaving the utf8 reach (cloud axes 43535669918: utf8 12/13 against 15/15). The c-vm utf8 simd-deny count fell 15 -> 13 for the same reason; the manifest `(?i)cat` still differs; the byte cells and utf8 c-default (40 >= 15) are above their floors. Expected, not a regression.

## PINS
- scripts/emit_sweep.py `("utf8","-fmemfn-simd=x86-64","c-vm")`: 15 -> 13 (S2 wide-position vrun decline, above).
- scripts/emit_sweep.py `--memfn=no-run-verify-wide` four cells, PROVISIONAL 1 -> measured: byte c-default 58, utf8 c-default 99, byte c-vm 117, utf8 c-vm 181 (stamp floors left 0; measured stamp 16/26/43/48 not pinned, the table's convention).
- tests/axes/memfn_arm.py run-verify-wide (both layers): 1 -> byte c-default 58, byte c-vm 117, utf8 c-default 99, utf8 c-vm 181. `memfn_arm.py --measure` (run-verify-wide default + simd x86-64-v3 cells) gave the same counts at both layers.
- Not re-pinned: vrun-kb/pad/trim simd floors (measured vrun-kb 36/37/16/17 vs floors 20/19/15/15; not red, the axes run is their judge).
- No docs quote these numbers (grep of docs/spec, docs/testing.md, part_d.md: no hits).

## REACH
The `reach` stage (REACH_ONLY=1 run_sabotage_matrix.sh S1923 ... S265) was cancelled by the red; re-queued unchanged in the new batch.

## OWED
- Verdicts of the queued arms and reach batch and of the cloud axes run (via queuewatch). If the arms sweep reds on another floor, that is a follow-up lane.
- Many other DIFFER_PINS floors sit well below their measured counts (historical, only moved when red); not touched here.
