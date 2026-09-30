# S432 ([CLS-TREE] S2, lane clss2) -- THE KIT'S BYTE FORMS LEAK INTO THE
# DEFAULT POSITION.
#
# ANSWER-NEUTRAL: D131 item 5 rules the kit's byte forms a SIZE-leaning
# `--tune` position only, because under a fair dispatch the byte kit is the
# SLOWEST byte form at every N (+13/+16/+19% vs the bitmap, O-77); the default
# byte-class form stays a table. The plant adds position 0 to the `byte-kit`
# row, so every default VM artifact with a scattered class reads a kit
# matcher. The detectors are run_tune_dial.sh §3e (the `scattered` witness at
# --tune=0 tested as `kit`) and the clskit crosscheck (the restated row's
# positions disagree with clskit.c's).
# RE-ANCHORED 2026-09-30 (lane clss2fix, [CLS-TREE] S2 review fixes, D139):
# the byte-kit row gained its site mask and the smaller-than predicate; the
# plant still adds position 0, intent unchanged.
SAB_ID="S432-clss2-byte-kit-at-default"
SAB_FILE="src/gen/clskit.c"
SAB_SUITES="tunedial clskit"
SAB_DESC="the byte-kit ROWS row lists position 0, so the default position tests scattered byte classes with kit matchers instead of a table (D131 item 5's size-leaning-only placement broken)"
SAB_DOC_FIGURE="Read the current figure from a run (lane clss2 measured it solo at landing; see docs/dev/lanes/clss2_report.md)."
SAB_REACH='"$PCREC" --engine=vm --tune=-2 -p rx -o - --pattern "[aeiou]+x"'
SAB_REACH_EXPECT='#define RX_VM_CLS_KIT 1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      TPOS(TP_M2) | TPOS(TP_M1), CLSS_ALL, P_KIT_SMALLER, CLSF_KIT, CLSD_BYTE_KIT },'
SAB_AFTER='      TPOS(TP_M2) | TPOS(TP_M1) | TPOS(TP_0), CLSS_ALL, P_KIT_SMALLER, CLSF_KIT, CLSD_BYTE_KIT },'
