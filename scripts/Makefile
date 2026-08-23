# scripts/Makefile — self-tests for the scripts in this directory, run ON
# CHANGE rather than per suite run (Frank's ruling, 2026-08-16, settling the
# queued "does test_watchdog.sh join make test?" question: it does not —
# docs/dev/decisions.md D48).
#
# THE WHOLE MECHANISM IS ONE DERIVED PATTERN RULE. A script's self-test lives
# at tests/<script-full-filename>.test and its report at
# tests/<script-full-filename>.testreport, depending on BOTH the test and the
# script — so `make test` here is a no-op when nothing changed and
# mandatory-cheap when something did, which is what makes "re-test on change"
# a property instead of a discipline. Adding a script's self-test requires
# ZERO lines here: drop the .test file in tests/ and the wildcard finds it.
# The stem is the script's FULL filename (extension included) — that is what
# lets one pattern rule serve `watchdog` and a future `mk_d27_cell.sh` alike.
#
# .DELETE_ON_ERROR is load-bearing, not hygiene: without it a failing run
# leaves yesterday's green report satisfying the dependency — a control that
# silently stopped controlling, this project's recorded check-design failure
# mode. A red run must leave NO report.
#
# A test needing files beyond its script adds a dependency-only line below
# the rule (e.g. `tests/foo.testreport: lib/helper.sh`) — the rule itself
# never changes.
#
# Each .test bounds its own runtime with coreutils `timeout` internally where
# it matters (watchdog.test must not be bounded BY watchdog); the recipe's
# outer timeout is the harness-level backstop, per the repo-wide rule.

TESTS   := $(wildcard tests/*.test)
REPORTS := $(TESTS:.test=.testreport)

.PHONY: test clean
test: $(REPORTS)

tests/%.testreport: tests/%.test %
	. ../tests/lib/timeout_bin.sh && "$$TIMEOUT_BIN" 600 bash $< > $@ 2>&1

clean:
	rm -f tests/*.testreport

.DELETE_ON_ERROR:
