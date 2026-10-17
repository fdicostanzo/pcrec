# fdclass report (lane fdclass, 2026-10-17, sonnet)

Branch `lane/fdclass` off `lane/b1fix` (f74bb0b7b, the B1 tip). Closes the
memfn arm's red on R17-b' B1's rows (b1fix_report.md "Findings, not fixed"):
`MEMFN_CLASS` had no entry for `fd-r0`, `fd-r5`, `fd-r8`, `fd-ndisp`, `fd-d1`.

## Method (runaxes_report.md, copied exactly)

`taskset -c 0-7 python3 -I tests/axes/memfn_arm.py --pcrec build/pcrec --root . --jobs 8 --measure --cell 'NAME|default|--memfn=no-NAME' --cell 'NAME|simd|-fmemfn-simd --memfn=no-NAME' ...`
for the five rows (10 cells, the layers run_axes.sh builds: every row at
`default` and `simd`). Distinct corpus patterns (4,624), one compile per
pattern per pass, `-p rx --features all`; byte base nothing, utf8 base `-e utf8`;
streams c-default and c-vm; count = patterns whose artifact differs from the
same layer's base without the deny. 1m40s wall. Log kept at
`build/fdclass_measure.log` (gitignored).

## The five measurements (all at B1, f74bb0b7b)

| row | layer | byte c-default | byte c-vm | utf8 c-default | utf8 c-vm | refused | class |
|---|---|---|---|---|---|---|---|
| fd-r0 | default / simd | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 | ASSERT_ZERO |
| fd-r5 | default / simd | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 | ASSERT_ZERO |
| fd-r8 | default / simd | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 | ASSERT_ZERO |
| fd-ndisp | default / simd | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 | ASSERT_ZERO |
| fd-d1 | default / simd | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 | ASSERT_ZERO |

Each cell is "differ of 4624". Transcript excerpt (verbatim):

```
fd-d1                  default  byte  c-default differ=    0 refused=   0 of 4624  first=[]
fd-d1                  simd     utf8  c-vm      differ=    0 refused=   0 of 4624  first=[]
fd-r0                  default  byte  c-default differ=    0 refused=   0 of 4624  first=[]
fd-r8                  simd     byte  c-default differ=    0 refused=   0 of 4624  first=[]
fd-ndisp               simd     utf8  c-default differ=    0 refused=   0 of 4624  first=[]
real	1m39.865s
```

All 40 rows (5 rows x 2 layers x 2 encodings x 2 streams) read
`differ=0 refused=0 of 4624`. This matches fdb1_report.md: no `fd_rows[]` row
is routed at B1, so every deny is artifact-identical, and the emit_sweep
arms' differ 0 for the same denies.

## Verdicts

- Ten `ASSERT_ZERO` entries added to `MEMFN_CLASS` (tests/axes/memfn_arm.py),
  one comment block naming the measurement, the tip and the report. No
  silent default: a row with no measured class stays RED (the population
  check); these were measured, not presumed.
- `MEMFN_REACH_ONLY=1 bash tests/axes/run_axes.sh` (taskset 0-7): `memfn arm:
  OK`, **245 passed / 0 failed** (22 cells, 11 kit rows; log
  `build/fdclass_reach.log`). It was 164/11 before.
- `make strict`: rc 0, clean.
- `make test-codegen`: rc 0, `run_group: 16/16 scripts passed`, no
  `*** [... test-` line; K37 PASS ("1274 site(s) ... is bounded").

## fd-d1's class changes at B2 (RE-MEASURE OWED AT B2's LANDING)

`fd-d1` is ASSERT_ZERO **only because B1 routes nothing**. lane/fdb2 routes D1,
and its OFF arm is D1w's table walk (options.def's comment: "`fd-d1` flips to
DIFFER at B2"): the deny then moves roughly 1,004 sites to D1w's walk, so
`("fd-d1", "default")` and `("fd-d1", "simd")` become DIFFER with measured
floors and a named witness. B2's landing must re-measure it with the method
above and replace both entries; leaving them ASSERT_ZERO will turn the arm red
(the ASSERT_ZERO check fails on any differ), which is the intended alarm. B2
was not edited here. The same holds for the others: `fd-r0`/`fd-r5`/`fd-ndisp`
at B4, `fd-r8` at B6; the comment in `MEMFN_CLASS` says so, and each landing
re-measures its rows.

## Commits

See `git log lane/fdclass`: the `MEMFN_CLASS` entries, then this report and its
index line.
