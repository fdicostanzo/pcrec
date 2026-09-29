# S360 ([CLS-TREE] S1, lane clss1) -- A LEAF OFF BY ONE AT A SECTION SEAM.
#
# The design's first named S1 sabotage (cls_tree_design.md §6, S1 row). The
# kit matcher's dispatch tree splits sections at their boundaries; the right
# half's `if (cp < BASE) return 0;` refuses the gap between two sections.
# Planted one too high, it refuses the right section's FIRST code point,
# which is always a member (a section's base is its first interval's lo).
# Nothing in the tree calls the kit at S1, so only the `clskit` arm can see
# it: the differential compares every emitted matcher against a reference on
# every code point.
SAB_ID="S360-clskit-seam-off-by-one"
SAB_FILE="src/gen/clskit.c"
SAB_SUITES="clskit"
SAB_DESC="the kit's dispatch tree refuses the first code point of every right-hand section (seam test one too high), so a member at each section seam reads as a non-member"
SAB_DOC_FIGURE="MEASURED solo 2026-09-29 at 52d63c9f (lane clss1): clskit:3fail/2pass DETECTED (3 of the section's 5 checks red; a correct DECISION with a wrong EMISSION)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_sb_printf(c, "%sif (cp < %uu) return 0;\n", ind, k->iv[k->sec[m + 1].first].lo);'
SAB_AFTER='    pcrec_sb_printf(c, "%sif (cp < %uu) return 0;\n", ind, k->iv[k->sec[m + 1].first].lo + 1);'
