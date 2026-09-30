# S434 ([CLS-TREE] S2 review fixes, lane clss2fix, D139) -- THE ONE RANGE
# SPELLING LOSES ITS TOP BYTE.
#
# A MISCOMPILE ON BOTH ENGINES AT ONCE: since D139 a VM class read and a DFA
# scan edge spell a one-interval byte class through the SAME emitter,
# `pcrec_clskit_emit_inline`. The plant writes the span one short
# (`hi - lo - 1`), so every subtract-form range test (`[a-z]`, `\d`) rejects
# its top byte, wherever it is written. The detector is the corpus harness
# on tests/base/d27_captures.rxt (capture-bearing, so VM-routed, with range
# classes whose top bytes the file's subjects exercise).
SAB_ID="S434-clss2fix-range-top-dropped"
SAB_FILE="src/gen/clskit.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/base/d27_captures.rxt"
SAB_DESC="pcrec_clskit_emit_inline spells a range class's span one short (hi - lo - 1), so every subtract-form range test on the VM and on a DFA scan edge rejects its top byte"
SAB_DOC_FIGURE="Read the current figure from a run (lane clss2fix measured it solo at landing; see docs/dev/lanes/clss2_report.md, Review fixes)."
SAB_REACH='"$PCREC" --engine=vm -p rx -o - --pattern "([a-z]+)x"'
SAB_REACH_EXPECT=' - 97) <= 25u'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    else pcrec_sb_printf(c, "(unsigned)(%s - %d) <= %du", byte, lo, hi - lo);'
SAB_AFTER='    else pcrec_sb_printf(c, "(unsigned)(%s - %d) <= %du", byte, lo, hi - lo - 1);'
