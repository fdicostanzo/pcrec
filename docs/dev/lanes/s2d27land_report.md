# s2d27land report (2026-11-14)

## STATE AT HANDOFF
Branch s2d27, commit 14432e5f9 (+ this report's commit). Rulings file
s2d27land_rulings.md: none present. Validation job
300-s2d27land-check is QUEUED (not yet read): `make strict`, then
`make -k test-corpus test-registry test-rxtsource`. Verdict by
`grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'` on its log; see OWED.

## PLACEMENT
- tests/litscan/d27/partd_{decline,deny_stretch,dominated,r_by_role,required}.rxt
  (5 files, 26 blocks, 143 cases), beside litscan's REQ_RUN / handoff
  witnesses; `tests/<dir>/d27/` is the corpus's D27 convention. litscan/CLAUDE.md updated.
- Author's report: docs/dev/lanes/s2d27_report.md.
- Census pins re-pinned in tests/rxtsource/run_rxtsource_tests.sh (predicted:
  CENSUS/RUNSH files +5, blocks +26, lines +143; C3_PASS/VERIFIABLE +142,
  C3_SKIP/PCRE2ONLY +1). C3_FILES left at 180 (unknown rule); the queued
  run corrects any misprediction.

## VALIDATION
- tests/harness/run.sh tests/litscan/d27: 143 passed, 0 failed, 0 compile failures.
- verify_rxt.py per file: 4 files ALL CHECKS PASSED; partd_required.rxt passed
  after the fix below (1 pcre2-only skip).

## FINDING: verify_rxt.py ignores `oracle none`
`oracle none <reason>` (rxt_format 3.1 p2: "a counted skip") is parsed and
shape-checked by verify_rxt.py but NOT acted on: the block went to python re
and hung >12 min on the exponential subject (the author's expectation is right;
the block simply was not skipped). Fix applied to the block's annotation, not
the expectation: `# pcre2-only` before its pattern (kept the `oracle none`
line). Caveat: rxt_format 3 p3 asks every pcre2-only mark to have an
upstream_issues.md entry; this is not a python/PCRE2 divergence but a python
cost blowup.

## OWED
- Queued job result (rxtsource census/C3 pins, registry, test-corpus, strict).
- Decision: make verify_rxt.py honour `oracle none <reason>` as a counted skip
  (then drop the `# pcre2-only` mark), or accept the mark.
