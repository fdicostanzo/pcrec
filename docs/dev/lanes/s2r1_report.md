# s2r1 report: rule (1) census, default vs alt-union-run

STATE: stopped (PREMISE TEST failed; no census run)

## STATE AT HANDOFF
Stopped at the brief's PREMISE TEST. No rulings file entries (s2r1_rulings.md empty). No edits outside this report.
Built build/pcrec-harness and build/pcrec in this worktree (main 370aab9fe).

## METHOD
`build/pcrec-harness --features all [--harness=alt-union-run] [-fno-altcls-merge -fno-altcls-factor] -e byte --emit-facts --pattern P`, reading RX_REQ_RUN / RX_REQ_WHY.

## CENSUS
Premise patterns, default vs lever, with and without altcls denied (RX_REQ_RUN):
- `cat|dog`: `[6364][616f][6774]`, both, both denies. The DEFAULT already states the run (the stage-3 set-position walk, WHY=untestable). The lever changes nothing.
- `(?:abc|xyz)q`: `[6178][6279][637a]71@3`, identical in all four cells.
- Lever DOES move equal-width alternations that sit in a context, with altcls denied (tests/codegen/run_facts_checks.sh [facts-ahead]): `xy(?:ab|ac)zw` default `61627a77@2/fffeffff`, lever `787961627a77@4/fffffffeffff` (longer run, prefix xy included).
So the brief's premise ("lever states a run, default does not" for those two patterns) is false: the default already states them. The lever's effect is to extend a run THROUGH an equal-width alternation, not to create one for a bare alternation.

## MOVERS BY CLASS
Not measured (stop rule).

## UNEXPECTED
The premise mismatch itself. The corpus-wide census still looks drivable with no code change: the lever is a CLI flag, and emit_sweep.py takes `--extra=--harness=alt-union-run` (the `--ident-arm` list has no arm for it; an arm would need `--extra=...` by hand, with `--bin` pointing at build/pcrec-harness).

## RECOMMENDATION
No ON/OFF recommendation yet. Re-brief with the corrected premise (movers are runs extended through equal-width alternations, e.g. `xy(?:ab|ac)zw`; compare with `-fno-altcls-*` denied and not), then the census is one emit_sweep run through scripts/boxlock.
