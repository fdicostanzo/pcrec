# pcureport — report for Frank: the [PRIOR-COST-UNIFY] family's input formulas

Lane `pcureport`, 2026-10-11, branch `lane/pcureport` from main `e7a69b78`
(abi 75). Report only: nothing under `src/`, `tests/`, `docs/spec/` moved.

## Deliverable

- `docs/dev/summaries/2026-10-11-prior-cost-inputs.html` — one
  self-contained page (inline SVG/CSS/JS, no external fetches, light/dark
  toggle, hover tooltips, a table view under every chart).
- `docs/dev/summaries/prior_cost_inputs/` — `gen_report.py` (renders it),
  `data.py` (the content, verified against the code), `reach_probe.py` +
  `reach_summary.tsv` (adapter reach from stamps), own CLAUDE.md.
- `docs/dev/summaries/CLAUDE.md` entry.

## Validation

- Every formula re-read in the code at `e7a69b78`; line numbers match rev
  2's. Chart B's boundaries are computed by replicating the shipped integer
  arithmetic (`req_landmark_admits`, `model_cost`, `verify_cost`).
- Palette: dataviz reference slots 1-3, `validate_palette.py --pairs all`:
  light PASS (CVD 9.2, normal 24.0; aqua contrast WARN → table views and
  direct labels), dark all PASS.
- Rendered with headless Firefox (profile and HOME in the worktree's
  `build/scratch`), light and dark; three label collisions found and fixed
  (R4 flip labels, the #4/#7 y-axis titles, #7's clipped end labels, the
  map's clipped last column).
- Reach probe: 5,194 compiling corpus pattern lines, `-e byte`, ~3 s.

## Findings (section 4 of the page, plainest first)

1. The three VERDICT members ask three different questions in three
   units: #4 compares jump lengths in bytes with no constant; #3 compares a
   mean gap in bytes against a Mac-measured crossover and only picks the
   starting state of a retry arm that runs either way; #7 is the only cost
   model (cycles/byte, five constants, 2× bar). No cost constant has two
   readers (shared: only the 2 ppm prior floor and the 16-bit run floor).
2. Real overlaps: #3 with #4 (both "mean bytes between stops vs a byte
   distance") and the six PICKs (already one primitive). #7 and G1 do not fit.
3. Adapters: A2 has zero corpus reach (0 of 181 handoff artifacts); A5's
   "no scan = 10^6" yields 16 of 35 corpus `adaptive-dense` answers; A1 pairs
   a documented UP rounding (#4) with undocumented truncation (#7); A3 is a
   stated choice with an unexamined consequence (105 asks); A4 is a rule.
4. `C_VERIFY`/`C_MISPRED` have no measurement record (rev 2 §3.2 says
   MEASURED, Zen 1); `C_ENTER` is half assumed; `C_MEMCHR` ships 0.06 vs a
   measured 0.055 c/B.
5. The unified cost cannot be evaluated today: `stop_reentry` is unmeasured
   everywhere, and the existing constants sit on two boxes in two units.

Two corrections to rev 2 for the manager: the `C_VERIFY`/`C_MISPRED`
provenance label (§3.2), and A2's reach (the handoff row sits below the
offset rows in first-match order; corpus reach 0).
