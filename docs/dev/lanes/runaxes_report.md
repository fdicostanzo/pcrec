# runaxes report (2026-10-16) -- DELIVERED

Branch lane/runaxes, base c2b6e927b (= lane/memfn-fd; no src/cli/lib differs from main 063b4a4b4).

## Classification (population READ from `pcrec --list-axes` memfn section; 6 rows x 2 layers)
Counts = distinct corpus patterns (4,624) whose `-p rx --features all` artifact differs from the same layer's base; floor = measured; byte|utf8 x c-default|c-vm. Transcript: runaxes_measure.log.

| row | default (SIMD-off) | -fmemfn-simd | witness |
|---|---|---|---|
| precheck-assign-byte | DIFFER 176\|0 byte, 244\|0 utf8 | same | `((?:a(?!b)\|ab)(?:cd){0,3}b)` (c-default) |
| vrun-w32 | ASSERT_ZERO | DIFFER 20\|19 byte, 15\|15 utf8 | `(?i)cat` |
| vrun-w16 | ASSERT_ZERO | DIFFER 20\|19, 15\|15 | `(?i)cat` |
| vrun-kb | ASSERT_ZERO | DIFFER 20\|19, 15\|15 | `(?i)cat` |
| vrun-trim | ASSERT_ZERO | DIFFER 20\|19, 15\|15 | `(?i)cat` |
| vrun-pad | ASSERT_ZERO | DIFFER 19\|18, 14\|14 | `(?i)cat` |

REFUSES: no `--memfn=no-NAME` is refused; the arm's REFUSES controls are the unknown name and the bare force spelling of every kind=deny row (both refused). Exact floors are in `MEMFN_CLASS` (tests/axes/memfn_arm.py).

## Measuring command
`taskset -c 12-15 python3 -I tests/axes/memfn_arm.py --pcrec build/pcrec --root . --jobs 4 --measure --cell 'NAME|default|--memfn=no-NAME' --cell 'NAME|simd|-fmemfn-simd --memfn=no-NAME' ...` (6 rows).

## Plant / unplanted
- Unplanted: `MEMFN_REACH_ONLY=1 MEMFN_EVERY=40 AXES=--memfn bash tests/axes/run_axes.sh` -> memfn arm OK, 132 passed / 0 failed (6 s). Full corpus: 160 passed / 0 failed.
- Planted: `bash tests/mech/run_sabotage_matrix.sh S1026` -> DETECTED, `axesmemfn:36fail/96pass`.

## Answer identity
`AXES=--memfn bash tests/axes/run_axes.sh` (full corpus, taskset 12-15, detached; log runaxes_axes_run.log, 4247 s): all 12 jobs agree=62360/62360, 0 mismatches/lost/gained/refused/give-up flips; reach OK. "all axes answer-identical to default". NO FINDING (no deny changes an answer).

## Checklist
1. population read from --list-axes, classified, floors measured at base: run_axes.sh [RUNAXES] block, MEMFN_CLASS, table above.
2. DIFFER rows name witnesses that differ in that run: MEMFN_CLASS witnesses, checked per run (132/160 checks).
3. Planted: S1026 (tests/mech/sabotages/, mech arm axesmemfn, tests/mech/CLAUDE.md + vocabulary entry) red; unplanted green.
4. Docs: run_axes.sh header, tests/axes/CLAUDE.md "The --memfn= arm", docs/testing.md paragraph.
