# docs/dev/summaries/prior_cost_inputs/ — the generator behind the prior-cost inputs report

Produces `../2026-10-11-prior-cost-inputs.html` (lane pcureport, 2026-10-11):
Frank's report on the [PRIOR-COST-UNIFY] family's INPUT FORMULAS as shipped
at main `e7a69b78` (abi 75). Run from the repository root:

    python3 docs/dev/summaries/prior_cost_inputs/gen_report.py

## Files

- `data.py` — the CONTENT as data: the ten derived members (question,
  formula as math and as the C at file:line, inputs, constants, NONE
  answer), the hand-listed candidates, every hand-set constant with unit,
  provenance and box (chart A), the family map (chart C), and rev 2's
  adapters A1-A5 with DELIBERATE/INCIDENTAL and reach. Hand-verified
  against the code; a line move in `src/` makes it stale, nothing checks it.
- `gen_report.py` — renders the one self-contained HTML (inline SVG, CSS,
  JS; no fetches). Chart B's boundaries are COMPUTED by replicating the
  shipped integer arithmetic (`req_landmark_admits`, `model_cost`,
  `verify_cost`); it reads `src/findings/default.rxt` for the prior rug and
  asserts the table still sums to 10^6.
- `reach_probe.py` — the adapters' reach, from STAMPS: every corpus
  `pattern` line (emit_sweep.py's enumerator, imported), compiled
  `-p rx --features all -o -` at `-e byte`, plus a `-fno-req-handoff`
  twin of every `handoff` artifact. About 3 s on the Linux dev box.
  `python3 .../reach_probe.py build/pcrec . > reach.tsv 2> summary`.
- `reach_summary.tsv` — that probe's counts at `e7a69b78`, read by the
  generator (the per-pattern TSV is not committed; it regenerates).

Palette: the dataviz skill's reference slots 1-3, validated all-pairs in
both modes with its `validate_palette.py` (light aqua sits below 3:1, so
every chart carries direct labels and a table view).
