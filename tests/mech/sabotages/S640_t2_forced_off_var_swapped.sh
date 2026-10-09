#!/usr/bin/env bash
# S640 ([DEC-FALLBACK] B2, lane decfbB2) -- T2's forced-off and var rows swapped, so -fno-prefilter a${v}b would list no-engine-vm instead of no-fno-prefilter.
# S-T2g. Detector at B2: the listing oracle on --emit-ir -fno-prefilter a${v}b (fbt (d) or-l-varff); from B4 the check_ir_value row.
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
SAB_ID='S640-t2-forced-off-var-swapped'
SAB_FILE='src/opt/select_engine.c'
SAB_SUITES='fallbacktable'
SAB_DESC="T2's var row defers to -fno-prefilter (as if it sat below forced-off), so -fno-prefilter a\${v}b would list no-fno-prefilter instead of no-variable"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S640. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# [DEC-FALLBACK] B4 (lane decfbB4, 2026-10-08) RE-AIMED, INTENT RE-VERIFIED.
# Re-anchored only: T2's rows gained their `note` cell (the listing's
# prose, moved verbatim from the --emit-ir chain), so each row is now four
# lines. The plant still swaps the forced-off and var rows. With the
# oracle's admit sites retired, the detectors are fbt (a)'s adm-varoff
# record and run_prefilter_tests.sh §7's check_ir_value row.
# [DEC-VAR-ATTRIB] (lane decattr, 2026-10-09) RE-AIMED, INTENT RE-VERIFIED.
# The contract INVERTED by ruling: the var row is a construct row AHEAD of
# forced-off, so -fno-prefilter a${v}b lists no-variable (no flag changes a
# variable's route). The rows are no longer adjacent, so a swap has no
# one-hunk text; the same claim is planted as the var row DEFERRING to the
# flag. Detectors: run_prefilter_tests.sh §7b's "var-vs-forced-off order"
# row and fbt (a)'s adm-varoff record.
SAB_BEFORE='static bool pfa_var(const PfAdmitSel *s)  { return (s->kinds & PF_KIND_VAR) != 0; }'
SAB_AFTER='static bool pfa_var(const PfAdmitSel *s)  { return (s->kinds & PF_KIND_VAR) != 0 && !s->force_off; }   /* SABOTAGE S640 */'
