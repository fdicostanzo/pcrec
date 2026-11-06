# docs/design/memfn/span_cards/ — evidence for span_cards.md (span_pick stage 2)

Design evidence for `../span_cards.md`, never built or run by pcrec's make. Python only, no timing.

## Files

- `drill.py` — §3.4-§3.5's estimator and gates implemented literally from the note's text, run on the
  constructed outcomes of §3.5's table (clean, one outlier, bimodal, A/A above spread and gate, delta
  NULL cases, drift). `python3 -I drill.py`.
- `j1_drill.py` — §3.6's pre-registered J1 sweep rule: outcome shares with no effect and with a true effect.
- `coverage_drill.py` — §6's coverage factor: the trimmed spread's consistency factor (K_TRIM) and the
  one-card equal-price departure rate per z.

## Later (S2c)

- `slot/` — the stage-2 slot harness (driver, subject generator, the slot's estimator, job scripts):
  evidence for one run, retired when M3's driver implements `docs/spec/measures.md`'s new sections 3.4-3.5.
