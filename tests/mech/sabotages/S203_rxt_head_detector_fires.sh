# S203 (S-C12) — [DD-13b.W1.1] run.sh's head detector fires on EVERY file,
# including the 179 whose first line is already `pattern`.
#
# THIS IS THE ROW THAT GUARDS THE 179. INV-COMPAT's argument is that every
# existing corpus file takes a byte-identical code path — no
# `--list-source` call, no boundary to be told, nothing between the file
# and the arm chain that reads it. This plant is that argument being false:
# 179 extra pcrec invocations appear, and each file's body start comes from
# a parser instead of from the top of the file.
#
# CAUGHT BY C0a, AND SPECIFICALLY BY ITS TWO SOURCES DISAGREEING. The
# external count of how pcrec was actually invoked goes to 179; the
# independent census of head-bearing files, which scans the raw bytes and
# never asks the harness, stays 0. Neither number alone is the finding —
# the check reports the DISAGREEMENT as a failure in its own right,
# because "the harness called out when it should not" and "a corpus file
# grew a head" are different events and only the pair distinguishes them.
#
# A COUNTER MAINTAINED BY run.sh ITSELF COULD NOT SEE THIS, which is why
# the count is taken by a wrapper around the binary: a counter inside the
# script that decides whether to call shares a source with what it counts.
SAB_ID="S203-rxt-head-detector-fires"
SAB_FILE="tests/harness/run.sh"
SAB_SUITES="rxtsource harness"
SAB_DESC="run.sh treats every file as head-bearing, so all 179 corpus files take the --list-source path they are supposed to skip entirely"
SAB_COUNT=1
SAB_BEFORE='    if [ -n "$head_probe" ] && [ "$head_probe" != "pattern" ]; then'
SAB_AFTER='    if [ -n "$head_probe" ]; then   # SABOTAGE S203: every file looks head-bearing'
