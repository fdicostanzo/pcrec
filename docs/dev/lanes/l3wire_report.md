# l3wire: the L3 D27 witnesses wired into `make test`

## Summary

The blinded author's L3 witnesses (`tests/lookaround/d27_l3/`) now ride the suite the way L1's do: the
136 witnesses' answers through `test-corpus`, the listing half through `make test-lookaround`, F1-F4 as
declared limits with plan rows. No `src/` edit, no witness expectation edited. Two comment-only edits
to the author's `.rxt` (below), the rxtsource census re-pinned, and `check_listing.py` generalized (a
directory argument, never a copy).

## Answers in the corpus

`bash tests/harness/run.sh tests/lookaround/d27_l3/l3d27_witnesses.rxt`: 13,722 cases passed, 0
failed, 0 compile failures (both engines, as the file's blocks declare them): the author's own count.
No answer disagreement. The file is picked up by `test-corpus` and `test-rxtsource` by name-globbing.
Two build-side comment-only edits, as l1ffix did for L1: the HEAD lines `description` and `oracle`
became `#` comments (the keyword census refuses them), and the 28 blocks whose pattern holds non-ASCII
text carry `# pcre2-only` (python `re` mis-reads them: 702 spurious failures otherwise); verify_rxt.py
then passes (11,646 cells PASS, 1,152 pcre2-only, 924 no-python-expression). `test-rxtsource`
re-pinned: CENSUS 343/7549/115552, RUNSH 319/7549/115552, C3_PASS/SKIP/PCRE2ONLY/NOPYTHON/VERIFIABLE
each by exactly this file's delta; 300 checks passed, 0 failed.

## Listing check

`tests/lookaround/d27_l1/check_listing.py PCREC [DIR]`: the profile is picked by the listing's header
(L1: one row per witness; L3: one row per witness x encoding x config def/vm/vmpf/dfa, comparing run,
K, why and `req_set_maxoff`). The limit rules are shared. L1 output unchanged (88 rows, 29 limits).
`make test-lookaround` runs it over `d27_l3`: 453 records list as recorded, 4 witnesses at a named
limit. Sabotage: dropping A17's limit row turns it red ("fails the spec ... names no limit").

## Limits

`l3d27_limits.tsv`: A35 run-cap (F1), A15 meet-wide (F2), A17 nested-head (F3), A45 class-one (F4).
These are the author's four LIMIT-status witnesses. A84 is named in F1's prose but its record meets
the spec, so it names no limit (the check forbids one). F5/F6 (C03, C05, INFO) name none.

## Plan rows

Children of [REQ-LOOKAROUND]: [L3-RUN-CAP], [L3-MEET-WIDE], [L3-NESTED-HEAD], [L3-CLASS-ONE]; each
trigger: L2's design or a bench pattern reaching the shape. plan_lint: 0 violations.

## Validation dispatched

`make test-lookaround` green locally (rc 0); corpus section for the new .rxt green; rxtsource green.
Cloud `make test` run named l3wire-test on the tip sha (see the reply).

## STATE AT HANDOFF

Rulings file: none applied (no R-n). Branch l3d27, one commit on top of 4e12d4517.
OWED: none (the cloud make test on 8a4bc96d6 is dispatched as cloud/main/test/l3wire-test; its verdict arrives via queuewatch)
