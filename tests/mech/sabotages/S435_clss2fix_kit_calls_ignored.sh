# S435 ([CLS-TREE] S2 review fixes, lane clss2fix, D139 item 1) -- THE
# BYTE-KIT ROW PRICES THE KIT AS IF IT WERE WRITTEN ONCE.
#
# ANSWER-NEUTRAL: a kit matcher is `static inline`, so every read of the
# class inlines it, while a table is paid once; `byte-kit`'s smaller-than
# predicate multiplies the kit by the read count (`ClsSelectIn.calls`). The
# plant pins the count to 1, so a class read twice keeps a kit that is
# larger than its table. The detector is the clskit crosscheck (the
# restatement's SEL lines at calls=2 disagree).
SAB_ID="S435-clss2fix-kit-calls-ignored"
SAB_FILE="src/gen/clskit.c"
SAB_SUITES="clskit"
SAB_DESC="kit_smaller ignores the read count and prices the kit written once, so a byte class read at several sites keeps a kit matcher larger than its table"
SAB_DOC_FIGURE="Read the current figure from a run (lane clss2fix measured it solo at landing; see docs/dev/lanes/clss2_report.md, Review fixes)."
SAB_REACH='"$PCREC" --engine=vm --tune=-2 -p rx -o - --pattern "([^\"\\\\]+)\"([^\"\\\\]+)\""'
SAB_REACH_EXPECT='#define RX_VM_CLS_KIT 0'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    long long calls = s->in->calls > 0 ? s->in->calls : 1;'
SAB_AFTER='    long long calls = 1;'
