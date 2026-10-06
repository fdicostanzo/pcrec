#!/usr/bin/env bash
# S523 ([MEMFN] R4c, lane r4cchecks) -- THE HEX-ESCAPE EXCLUSION IS REMOVED.
#
# C4's negative control: a hex escape in a .rxt subject or a C string is not
# the arch noun. The rule is the backslash in the boundary class `L`; removing
# it makes every hex escape in the corpus a hit AND fails the planted negative
# control. Detector: C4 (arm memfnarch). SAB_REACH: the negative control is
# reached (and green) on the clean tree.
SAB_ID="S523-c4-hex-escape-not-excluded"
SAB_FILE="tests/memfn/arch_blind_check.py"
SAB_SUITES="memfnarch"
SAB_DESC='C4 stops excluding a backslash-prefixed match: hex escapes in .rxt subjects read as the arch noun'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/r4cchecks_report.md §3); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S523.'
SAB_REACH='CC="$CC" TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_arch_blind.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: negative control: hex escapes'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE="L = r'(?<![A-Za-z0-9\\\\])'"
SAB_AFTER="L = r'(?<![A-Za-z0-9])'"
