# [OPTLOOP.1-NOCAPSVIEW] (2026-09-23, lane nocapsview, sonnet)

Delivers `docs/dev/optloop/cycle1_nocaps_view.md`: the nocaps-vs-nocaps
half of D119's two-class-pure-ledger ruling (`decisions.md` addendum,
2026-09-23), paired with `cycle1_caps_view.md`'s caps-vs-caps half.

Step 1 classifies the roster from `testees/*/configs.toml`'s own
`captures` field, never guessed from a name; no UNKNOWN rows.
`pcrec-nocaps` is the only pcrec nocaps config; `pcre2-dfa` is the only
algorithmic nocaps competitor (`vectorscan` excluded, SIMD/boolean-grain).

BEFORE (pin `25b1984f`): 100/110 win-or-tie (reproduces
`cycle1_caps_view.md` §2's totals exactly, a cross-check). AFTER (pin
`8d716693`): 104/110, losing score 4.7066 → 1.4094. Six BEFORE losses flip
to wins. Two flip WIN → catastrophic LOSS: `winpath-near-miss`/thr
(+113,334%) and `email-nested-plus`/thr (+72,253%) — independently
reproduces `cycle1_ledger_reading.md` §5's required-byte-absent
floor-entry cost to within 25 ns; its consequence is nocaps-specific,
since `pcre2-dfa`'s near-instant reject is the one competitor fast enough
for the new floor cost to flip a win into an 87× loss. `pcre2-dfa` is
absent from the AFTER report's roster; its BEFORE numbers are reused as
the AFTER competitor reference, flagged as an assumption (§0/§5).

No `src/`/`tests/`/`docs/spec/` changes. Reproduction:
`docs/dev/optloop/nocapsview/` (own CLAUDE.md).
