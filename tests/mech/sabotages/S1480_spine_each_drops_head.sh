# S1480 ([DD-10], lane dd10fix) -- PCREC_SPINE_EACH stops one element early: it never yields the spine's
# HEAD (the leftmost element of a concatenation or alternation). Every walk on the iterator then forgets one
# branch or factor: pcrec_minw over-reports an alternation's minimum (unsound), sa_walk/ew_walk_marked
# intersect fewer branches and claim anchors that do not hold, rb_walk drops a branch from the required set.
# The control that the one shared loop is the one every converted site relies on. Detectors: the mrl arm's
# acceptance cells and the corpus (harness).
SAB_ID="S1480-spine-each-drops-head"
SAB_FILE="src/core/internal.h"
SAB_SUITES="mrl harness"
SAB_DESC='PCREC_SPINE_EACH ends at the last spine node instead of yielding the head below it, so every converted walk skips the leftmost branch or factor'
SAB_DOC_FIGURE='src/core/internal.h PCREC_SPINE_EACH; exact re-run: bash tests/mech/run_sabotage_matrix.sh S1480.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='         e##_at_ = e##_at_->k == (kind) ? e##_at_->l : NULL)'
SAB_AFTER='         e##_at_ = e##_at_->k == (kind) && e##_at_->l->k == (kind) ? e##_at_->l : NULL)   /* SABOTAGE S1480 */'
