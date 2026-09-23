# [OPTLOOP.1-NOCAPSVIEW] (2026-09-23, lane nocapsview, sonnet)

Delivers `docs/dev/optloop/cycle1_nocaps_view.md`, the nocaps-vs-nocaps
half of D119's two-class-pure-ledger ruling. **REVISED** after two
follow-ups: pcrec-bench's own authoritative classification table
(I-99/I-100, `e8c5a12`/`5435ac6`/`e8d6109`) replaces Step 1's earlier
`configs.toml` read and moves `rust-default` from caps into the NOCAPS
scored class (a ruling, not a factual correction — its driver calls one
`captures_at` per call, declared a fixed cost); and Frank's standing
cross-class anomaly query (I-101, `7f440dd`) is added as §6.

With `rust` now a scored NOCAPS competitor: BEFORE 87/113 win-or-tie
(77.0%), AFTER 92/113 (81.4%), losing score 7.6062 → 4.0091. `rust` is
the losing competitor on 17/26 BEFORE and 18/21 AFTER rows. Batch 1's
mechanisms still land (8 flips to win); 3 flip the other way, including
the two floor-entry catastrophes (`winpath-near-miss`/thr,
`email-nested-plus`/thr — now 256×/215× against the wider set).

§6 (I-101): 40/29 cells show a capturing competitor beating `auto-nocaps`,
but 30/25 are `pcre2-jit` (non-algorithmic, excluded elsewhere). Real
population: 10 BEFORE / 4 AFTER non-JIT anomalies; two AFTER ones are §3's
floor-entry cells, two (`wild-waf-crs-942140-dbnames`,
`-942360-concat-sqli`, both losing to `re2`) persist both pins,
unrelated to batch 1 — flagged for cycle 2.

Flag: `cycle1_caps_view.md`'s CAPS table still scores `rust` as caps and
is unrevised (out of scope, owned by `capsview`). No `src/`/`tests/`/
`docs/spec/` changes. Reproduction: `docs/dev/optloop/nocapsview/`.
