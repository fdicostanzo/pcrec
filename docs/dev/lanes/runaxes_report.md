# runaxes report (2026-10-16) -- STATUS, NOT DELIVERED

Branch lane/runaxes (base c2b6e927b). Session closed before the classes were measured.

## Done (committed, WIP 7fccac2c4 + this commit)
- tests/axes/memfn_arm.py: reach checker (population from --list-axes memfn section == MEMFN_CLASS rows, cell flags carry the spelling, DIFFER floor/witness, ASSERT_ZERO, REFUSES, null arm, unknown-name and bare-force refusal controls, --measure mode).
- tests/axes/run_axes.sh: [RUNAXES] block (cells composed once from --list-axes; 2 layers per row = 12 answer jobs; AXES=--memfn selects; MEMFN_REACH_ONLY=1 / MEMFN_EVERY=K), reach after the job loop, summary line, header text (term 4). bash -n clean; NOT yet run end to end.
- S1026 (tests/mech/sabotages/S1026_*.sh) + mech arm axesmemfn in run_sabotage_matrix.sh + tests/mech/CLAUDE.md; tests/axes/CLAUDE.md; docs/testing.md paragraph.

## Remaining
1. MEMFN_CLASS in memfn_arm.py is EMPTY: fill from the measurement below (floor = measured count per (enc,stream); witnesses: (?i)cat for the vrun rows at layer simd, byte c-default/c-vm; precheck-assign-byte witness from its first= list, e.g. ((?:a(?!b)|ab)(?:cd){0,3}b)).
2. Run S1026 plant red / unplanted green (mech arm axesmemfn), then AXES=--memfn run_axes.sh pinned taskset -c 12-15 detached (answer-identity verdict; none run yet).
3. Re-fill this report with the table, commands, checklist.

## Measurement in flight (detached nohup, pinned 12-15)
Log: build/rascratch/measure_full.log (48 of 48 lines when last read; each line = one (cell,enc,stream), differ over 4624 distinct corpus patterns). Command: python3 -I tests/axes/memfn_arm.py --pcrec build/pcrec --root . --jobs 4 --measure --cell 'NAME|default|--memfn=no-NAME' --cell 'NAME|simd|-fmemfn-simd --memfn=no-NAME' for the 6 rows (args in build/rascratch/cellargs.txt). Complete when 48 lines.
Partial so far: precheck-assign-byte differs 176 (byte c-default) / 244 (utf8 c-default) at both layers, 0 at c-vm; vrun-kb at default 0. Provisional classes: precheck-assign-byte DIFFER at both layers; vrun-* ASSERT_ZERO at default, DIFFER at simd (witness (?i)cat, hand-verified for all five vrun rows on the default and vm engines). No FINDING (answer difference) observed yet; jobs not run.
