#!/usr/bin/env bash
# cloud_failures.sh — the ONE extractor of a cloud shard log's failing lines ([CLOUD-SUITE], lane cloudmon).
# Used by the final verdict (cloud_gather.sh record -> errors.txt), the early alert (scripts/queuewatch
# CLOUD-SHARD-RED) and `scripts/cloudrun --status`, so a shape one of them misses is missed by none.
#
#   cloud_failures.sh [MAX] < LOG      the failing lines of LOG, in order, at most MAX (default 60), any
#       leading GitHub log timestamp (`2026-11-11T16:20:14.1234567Z `) removed. A line is failing when it has:
#         - the upper-case word FAIL / FAILED / FAILURE(S) not glued to a letter on the left (`FAIL:`,
#           `AXIS FAIL:`, `FAIL[name]:`, `  FAIL — utfcheck arm`, `-futf-check arm ...: FAIL — ...`,
#           `name|FAIL|keys_base=..`, `ADD FAILED`, `HARNESS FAILURE`, `GCC-FAILED`, `run_axes.sh: FAILED`);
#         - make's `*** [...] Error N`;   - `FATAL:`;   - `##[error]` (the runner's own step failure);
#         - a sanitizer's `runtime error:` / `ERROR: AddressSanitizer|LeakSanitizer` / `SUMMARY: ... Sanitizer`.
#       NOT failing: a PASS:/OK line (they may mention a count of failures), lower-case `fail=N` / `checks failed: 0`
#       tallies, `SKIPPED`, and a `0 FAIL` / `FAIL=0` / `FAIL: 0` count; nor a mech matrix ROW (a line opening with a
#       sabotage id then a tab or two spaces: its description/tally prose says FAIL/`compliance-FAIL` on a row that was
#       DETECTED -- run 43108213213 read four DETECTED rows red; a row that is wrong gets its own `FAIL: mech row` line). Derived from the FAIL forms our suites print
#       (survey in tests/ci/cloud_failures.test) and the real shards of runs 43053543333 (s8) and 43069897443 (s7).
set -u
max=${1:-60}
sed -E 's/^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z //' \
  | grep -E '(^|[^A-Za-z])FAIL(ED|URES?)?([^a-z]|$)|\*\*\* \[.*\] Error|FATAL:|^##\[error\]|runtime error:|ERROR: (Address|Leak)Sanitizer|SUMMARY: .*Sanitizer' \
  | grep -vE '^S[-0-9A-Za-z_]+([[:space:]]{2,}|'"$(printf '\t')"')|^[[:space:]]*(PASS|OK)([^A-Za-z]|$)|(^|[^0-9])0 FAIL|FAIL(ED|URES?)?[:= ]+0([^0-9]|$)' \
  | head -"$max"
