# mbread — M-B reduced (2026-09-23, lane mbread, sonnet)

Reduces pcrec-bench lane `b76optloop`'s block (C) raw timing
(`docs/dev/lanes/b76optloop_report.md`, commit `efec5366`) into
`captures_via_dfa_survey.md` §3.6's VM-pass share for the 17
capture-forced hybrid `capability` patterns. See
`docs/dev/optloop/onepass_census.md` "M-B — measured" for the full
table, per-pattern breakdown, and verdict reasoning.

**Verdict: SPLIT.** Throughput regime clears the ~10% "not the cost" bar
cleanly (population median 0.00%, IQR [0.00%, 0.90%]); match regime does
not (median 32.75%, IQR [22.24%, 45.06%] — above the ~25% floor, below
the 50% "has a target" ceiling). Per-pattern: 5 of 16 clean NOT-THE-COST,
3 of 16 clean HAS-A-TARGET, 8 of 16 land in the gap the rule doesn't
resolve; `date-nested-plus` has no own-subject data (MISSING per the ask)
and its throughput cells are below display precision.

**Flagged, not resolved**: every `own`/match subject is a tiny
hand-authored literal (5-93 bytes, `bench/capability/gen_subjects.py`) —
plausibly dominated by fixed per-call overhead rather than genuine
capture-assignment cost, which is a likely explanation for why the match
regime sits in the ambiguous middle instead of clearing a threshold.
Next measurement: re-run the match arm at larger subject sizes (same
literal repeated/embedded) to see whether the share converges down as
overhead amortizes.

Deliverables: the census section above; `docs/dev/optloop/c2/onepass_mb.py`
(reducer, re-runnable) + `onepass_mb.tsv` (127 rows: cell/pattern_median/
pattern_throughput_median/pattern_match_share/population kinds); this
report; `docs/dev/optloop/c2/CLAUDE.md` entry.

Cross-checked one row by hand (`wild-secrets-aws-access-key-id`, t-1m:
3.6277/3.1684 → 12.66%, matches script). Docs-only; no `src`/`tests`
touched; no build, no timing (all numbers already timed on ubuntubudu by
the bench lane).
