# s2d27fix report

## STATE AT HANDOFF
Fix committed on branch s2d27; no rulings file entries. Re-validation (make strict + `make -k test-corpus test-registry test-rxtsource`) exceeded the ~4 min foreground budget (test-corpus alone), so it is QUEUED as job 301-s2d27fix-check (source docs/dev/lanes/s2d27fix_check.job): OWED. Verdict: grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' in its job.log.

## CAUSE
The single red was `FAIL: keyword census: COLLISION — oracle=1` (job 300-s2d27land-check log). tests/litscan/d27/partd_required.rxt line 31 began with the word `oracle` (`oracle none python re backtracks ...`), a word the grown grammar wants as a keyword; the census refuses any corpus line that starts with one. Not an answer disagreement; no expectation involved.

## FIX
Deleted that one line (the explanatory text already sits in the block's F4 comment and the `# pcre2-only` annotation stays). No expectation, pin or count touched (it was not a case line). Filed K145 (tooling) in docs/dev/known_issues.md: verify_rxt.py hangs on a block carrying `oracle none` (python re backtracks exponentially); not fixed.

## VALIDATION
Premise confirmed: exactly one FAIL line in the job log. Foreground run timed out in test-corpus at 280 s (no verdict). Queued check OWED.

## OWED
Job 301-s2d27fix-check: expect test-rxtsource green (keyword census), test-corpus and test-registry green.
