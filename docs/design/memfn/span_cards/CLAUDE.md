# docs/design/memfn/span_cards/ — evidence for span_cards.md (span_pick stage 2)

Design evidence for `../span_cards.md`, never built or run by pcrec's make. Python only, no timing.

## Files

Each drill prints its inputs; `python3 -I <drill>`.

- `drill.py` — §3.4-§3.5's estimator and gates implemented literally from the note's text (cells, control
  normalization, the anchor, A/A, trimmed spread, cost gate, bimodal test, paired NULL rule, drift), run on
  §3.5's constructed outcomes and on one end-to-end example from cells.
- `place_drill.py` — §3.2/§3.5: the unit gate's refusal and HELD rates under placement (rev 1's fixed
  offset vs rev 1.1's per-launch draw), and the drift check's power.
- `coverage_drill.py` — §3.4 step 6 and §6: the trimmed spread's consistency factor (K_TRIM) and the
  new-draw departure rate per z over the within-launch share f.
- `floor_drill.py` — §2.3/§3.5: the per-hit cost a `delta` row resolves under the paired NULL rule, vs rev
  1's FRG floor.
- `j1_drill.py` — §3.6's pre-registered J1 sweep rule: outcome shares with no effect, with a true effect,
  and under placement.
- `tree_drill.py REPO` — counts read off the tree: the key population, the jobs' points and box time,
  check C's population, the embed's bytes (§2.4, §3.7, §3.8).

## Later (S2c, S2e)

- `slot/` — the stage-2 slot harness (driver, subject generator, per-launch linking and placement, the
  control, the slot's estimator, job scripts): evidence for one run, retired when M3's driver implements
  `docs/spec/measures.md`'s new sections 3.4-3.5. `slot/j1/` holds J1's cells, verdict and `j1_rule.py`
  (J1's evidence home; not in the set). `slot/movers.py` writes `measure_store/movers/0002.tsv` (S2e).
