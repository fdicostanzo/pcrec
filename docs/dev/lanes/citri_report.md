# citri (2026-10-13) — CI red since 2026-10-10: `make strict` on gcc 13

Lane citri, sonnet. Triage of GitHub Actions CI failing on every push to main.
Branch `lane/citri`, one source commit (`fa80ac9f0`) plus this report.

## Verdict

CI has been red since 2026-10-10 because `make strict` (CI step 10, before
`make test`) fails on ubuntu-latest's gcc 13.3 with
`src/parse/rxt_source.c:783:21: error: 'one' may be used uninitialized
[-Werror=maybe-uninitialized]` (declared at :758, in `row_check`). It is a
false positive: `row_key` writes `*key` on every `return 0` path. The
`"Process completed with exit code 2"` the brief quotes is `make strict`'s
failure, not `make test`'s; that is why `build/ci_test.log` never exists (the
`make test` step is skipped; the upload step warns "No files were found").

## First bad run / commit, last green run

- Last green: run 38018323798, 2026-10-10T02:48Z, sha `1cb95b69b`, 72 min total,
  so `make strict` and `make test` both ran.
- First red: run 38029095714, 2026-10-10T05:54Z, sha `2b093cdf3`, failed in
  `make strict` after 31 s. The ten runs between are all `cancelled`
  (a push cancels the running job), so run history alone cannot narrow the
  63-commit range further.
- First bad COMMIT: `081480e16` ("[RXT-READERS] one oracle/var grammar across
  the three legs", 2026-10-10 01:26 -0400), found by compiling
  `src/parse/rxt_source.c` at `081480e16^` (clean) and `081480e16` (error)
  with gcc 13.4. The commit only ADDS `var_line_ok` and a call to it; it does
  not touch `row_check`/`row_key` (those date from 2026-09-26/28). It moved
  gcc 13's inlining/analysis so that `row_key` is now seen through `row_check`
  and the `n == 2 && j < 2` loop in the byte-key branch (writes `*key` only on
  `j == 1`) is judged able to fall through with `*key` unset. A function-body
  change elsewhere in the TU is enough; this is gcc's heuristic moving, not a
  semantic change.
- Not a runner change: all three runs I read (38018323798 green,
  38029095714 and 38331362131 red) ran on image ubuntu-24.04 20261004.327.1,
  gcc 13.3.0-6ubuntu2~24.04.1.
- Since 05:54Z on 10-10: 87 failed, 10 cancelled, 0 green. Every failure that
  I spot-checked (38029095714, 38036701099, 38057186988, 38331362131) fails in
  the same step.

## Local reproduction

The dev box's gcc is 15.2, which does not warn, so `make strict` is green here
even on the broken tree. I fetched Ubuntu's gcc 13.4.0 `.deb`s (apt-get
download, extracted with `dpkg -x` into `build/gcc13/`, gitignored, no install,
no root) and ran it through a wrapper (`build/gcc13/gcc13`).

Before (main at the lane's base):

    build/gcc13/gcc13 -O2 -g -Wall -Wextra -std=gnu11 -Ilib -Isrc -Wshadow -Werror \
        -c -o /dev/null src/parse/rxt_source.c
    -> the CI's exact error at :783:21 / :758:23, rc 1

Bisect on that one file: `081480e16^` rc 0, `081480e16` rc 1.

After the fix: `make strict CC=$PWD/build/gcc13/gcc13` compiles the WHOLE tree
(LIBSRCS, cli, analyze, scripts/findgen.c, the KITSRCS) clean under
`-Werror -Wshadow`, i.e. no second gcc-13-only warning is hiding behind this
one (the strict loop stops at the first error, so this was not known before).
gcc 15.2: `make strict` clean, `make test-rxtsource` 298 passed / 0 failed.
Reproduction here is gcc 13.4 against CI's 13.3 (the closest available);
CI itself is the final check.

## Fix

`src/parse/rxt_source.c`: `unsigned long one = 0;` in `row_check`, with a
one-line comment. Zero behaviour change (every `r == 0` path writes it; `key`
two lines up is already `= 0`). Chosen over restructuring `row_key` because the
warning is a compiler limitation; a rewrite would be a larger diff for the same
effect. No runner-side or ci.yml change was needed.

## What CI still cannot cover / not verified

- `make test` has not run on CI since 2026-10-10 02:48Z (`strict` fails
  first). Whether it still fits and is green on gcc 13.3 after ~3 days of
  merges (hundreds of commits, many new suites) is UNKNOWN; expect a second
  round of CI-only reds (gcc 13 vs 15/16 behaviour, D45 CPU budgets on the
  hosted runner, as in `citri` 2026-09-30 / `nltriage`) once strict passes.
  Do not assume the first green strict means a green run.
- Dev boxes build with gcc 15.2 (Linux) / gcc-16 (Mac), neither of which
  reproduces gcc 13 warnings. Only CI exercises gcc 13.3. A cheap local
  guard is the extraction recipe above; the Makefile does not automate it.
- CI runs only the per-push tier (no ubsan/asan/lint/mech/test-axes).

## Why nobody saw it for 24+ h (facts only; no change made)

- `ci.yml` has no notifier of its own (no issue/Slack/mail step); the README
  has a status badge only. Failure email, if any, is GitHub's per-user
  default to the pusher/actor (`fdicostanzo`, all runs); whether it is
  enabled or read is not visible from `gh`.
- A red that never recovers is not a state change, and a fast failure (31 s)
  at a step the dev boxes cannot reproduce looks like noise. The history is
  mostly `cancelled` (263 of the last 400 runs; each push cancels the previous
  run), so green runs were already rare: 39 successes of 400.
- Nothing in the repo's session/wake routine checked CI status before
  `a70548bd6` (the `pcrec-manager` skill's step 0b, added 2026-10-13).
- The job needs ~30 s to fail but ~40-70 min to pass, so the cancel-on-push
  concurrency group means a green run requires 40+ quiet minutes after a push,
  while a red one is delivered almost immediately.
