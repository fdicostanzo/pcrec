# S433 ([CLS-TREE] S2 review fixes, lane clss2fix, D139) -- THE SCAN EDGE
# ASKS THE CLASS-FORM TABLE AS IF IT WERE A VM READ.
#
# ANSWER-NEUTRAL: the scan edge's run test is the class table's answer AT
# THE SCAN SITE (`CLSS_SCAN`). The plant passes `CLSS_VM` instead, so the
# VM-only `byte-fold-default` row fires on a scan edge at the default
# positions: a caseless-letter run's edge takes the fold compare where D138
# Q1 holds it at its 256-byte table (and the byte-kit row prices the edge
# against a 32-byte bitmap it never reads). The detector is
# run_tune_dial.sh §3f (the `fold` witness at --tune=0 stamped and spelled
# `fold`, where the table says `bitmap`).
SAB_ID="S433-clss2fix-scan-site-ignored"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="tunedial"
SAB_DESC="scan_choice asks the class-form table at the VM site, so a DFA scan edge's ASCII fold pair takes the VM-only default fold row (the fold compare at --tune=0, where D138 Q1 holds its table)"
SAB_DOC_FIGURE="Read the current figure from a run (lane clss2fix measured it solo at landing; see docs/dev/lanes/clss2_report.md, Review fixes)."
SAB_REACH='"$PCREC" -p rx -o - --pattern "(?i)xa{3,}b"'
SAB_REACH_EXPECT='#define RX_DFA_SCAN_EDGE "bitmap"'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                       NULL, CLSS_SCAN, SCAN_TEST_CALLS };'
SAB_AFTER='                       NULL, CLSS_VM, SCAN_TEST_CALLS };'
