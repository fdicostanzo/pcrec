# Rule-list pilot: verdict (2026-11-02)

- Verdict: PASS at 0 rules. Today's default already passes: held-out 0.9812 of the per-site ideal, no tail site, worst 1.183.
- Best rule list (1 rule) reaches 0.9838 held-out; lists of 2 and 3 rules over-fit and fail on one tail site each.
- So within-engine headroom over the default is about 2% here. Pricing's case is extensibility, not mean speed.
- This is the BASELINE a pricing model must beat; the pricing build still waits for [STREAM].
- Regime: Zen 4, SIMD off, find-all, forceable arms only, engine choice counted not timed.
- 138 timed sites (1 excluded before timing), train 71 / held-out 67, noise 0.42% (median site floor 0.69%).
- Worst sites for one bounded look: P05 1.581, B12 1.280, B05 1.240, C11 1.214, C25 1.183 (held-out worst).
- Run facts: c03's expect miscounted (one requeue), data complete. LOADMAX 2.5 for c02-c16; 659 of 663 groups started at load1 >= 1.5; 4 requeued.
- Details: docs/design/pricing_rulepilot.md "Result (2026-11-02)"; docs/dev/lanes/rulepilot_report.md.
