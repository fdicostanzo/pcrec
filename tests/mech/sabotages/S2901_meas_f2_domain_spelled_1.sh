# S2901 — span_pick stage 2 unit S2a (lane s2a; docs/design/memfn/span_cards.md rev 1.1 §9 row (b);
# docs/spec/measures.md §2.2¶3a, §3.3¶1a, §4¶2a).
#
# Plant: (b) the format-2 digest domain is spelled pcrec-meas-1.
# Detector: ks_ref.py's digest (domain pcrec-meas-2) differs from C's on every format-2 fixture: each refuses to load (R1-R5, the pairs).
SAB_ID="S2901-meas-f2-domain-spelled-1"
SAB_FILE="src/core/ks_measures.c"
SAB_SUITES="knowledge"
SAB_DESC='(b) the format-2 digest domain is spelled pcrec-meas-1'
SAB_DOC_FIGURE='MEASURED by lane s2a planted and reverted (docs/dev/lanes/s2a_report.md, the sabotage table); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2901.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    KS_DOMAIN("pcrec-meas-2"), KS_SUB_NONE, meas_fold2'
SAB_AFTER='    KS_DOMAIN("pcrec-meas-1"), KS_SUB_NONE, meas_fold2   /* SABOTAGE S2901 */'
