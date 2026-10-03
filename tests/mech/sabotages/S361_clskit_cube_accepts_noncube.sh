# S361 ([CLS-TREE] S1, lane clss1) -- cube_of ACCEPTS A NON-CUBE.
#
# The design's second named S1 sabotage. `cube_of` computes the one cube
# that contains every member of a section (val = AND of members, care = the
# agreeing bits) and must then prove the cube spills onto no NON-member
# inside the span. The plant deletes that exact check and keeps only the
# O(k) spill budget, which is a necessary condition and not a sufficient
# one: {0, 4, 5} over a span of 6 passes the budget with cube {0,1,4,5}, and
# the emitted `(x & care) == val` then claims 1. CUBES wins every section it
# is offered on at the table's λ, so a wrongly-offered cube is emitted.
#
# RE-AIMED 2026-10-03 ([OPT-LITSCAN] S4 C0, lane s4build): the cube moved to
# `src/core/cpset.c` as `pcrec_cube_of` (litscan_s4.md §1.2, one definition
# parameterized by the domain), and clskit's `cube_of` is now its caller over
# the section's own span. The anchor travelled verbatim (same column), so
# only SAB_FILE moved. Under the run facts' ABSOLUTE domain (base 0, w 256)
# the plant is inert by arithmetic -- the O(k) budget is exact there, csize
# must equal nmem -- so the detector is still the kit's section form, and
# S442 is the absolute reader's own row.
SAB_ID="S361-clskit-cube-accepts-noncube"
SAB_FILE="src/core/cpset.c"
SAB_SUITES="clskit"
SAB_DESC="pcrec_cube_of (clskit cube_of's callee) keeps only its O(k) spill budget and drops the exact containment check, so a section that is not one cube is emitted as one and claims non-members inside its span"
SAB_DOC_FIGURE="MEASURED solo 2026-09-29 at 52d63c9f (lane clss1): clskit:4fail/1pass DETECTED -- the differential goes red, and so does the cross-check, because a wrongly-offered cube also moves the sectioning away from the study's."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    for (unsigned x = 0; x < w; x++)
        if ((x & c) == v && !((mem[x >> 6] >> (x & 63)) & 1)) return false;'
SAB_AFTER='    /* SABOTAGE S361: the exact containment check is gone. */'
