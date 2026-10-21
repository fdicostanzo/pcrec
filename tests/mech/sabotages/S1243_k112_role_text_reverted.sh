# S1243 — [MEASURE-SET] M0 (lane m0build; docs/design/measure_sets.md rev 3 §8.5,
# §9.6; docs/spec/measures.md).
#
# Plant: K112's rider reverted: the ^/\A role string is the stale 'attempt_position of subject' again.
# Detector: tests/codegen/run_ir_listing.sh's per-pattern byte baselines (5a226443, b936fffc, d5c12bc9 carry the row).
SAB_ID="S1243-k112-role-text-reverted"
SAB_FILE="src/core/ctxfn.def"
SAB_SUITES="irlisting"
SAB_DESC='K112'"'"'s rider reverted: the ^/\A role string is the stale '"'"'attempt_position of subject'"'"' again'
SAB_DOC_FIGURE='MEASURED at the M0 head by the lane'"'"'s solo runs: see docs/dev/lanes/m0build_report.md §5 (the owed mech rows). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1243.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='          "^ start of subject (absolute offset 0)")'
SAB_AFTER='          "^ attempt_position of subject (absolute offset 0)")   /* SABOTAGE S1243 */'
