# S363 ([CLS-TREE] S1, lane clss1) -- THE SELECTION TABLE PICKS A ROW WHOSE
# PREDICATE IS FALSE.
#
# The brief's fourth S1 row. D131's `0`/`+1` row takes `P3` only where `K`
# has at least 16 sections AND `P3` costs at most 1.26x `K`. The plant drops
# the section-count conjunct, so `mid-page3` fires on sets whose `K` is a
# handful of sections and pays for no dispatch tree. Every emitted form is
# still a CORRECT matcher, so the differential stays green by construction:
# only crosscheck.py's independent restatement of the table can see it.
SAB_ID="S363-clskit-row-predicate-false"
SAB_FILE="src/gen/clskit.c"
SAB_SUITES="clskit"
SAB_DESC="the mid gate drops its section-count conjunct, so the 0/+1/+2 positions choose P3 on sets whose K has fewer than 16 sections (a row fires whose predicate is false)"
SAB_DOC_FIGURE="MEASURED solo 2026-09-29 at 52d63c9f (lane clss1): clskit:1fail/4pass DETECTED -- the cross-check alone, as predicted; the differential, the law and the census stay green."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return s->k->nsec >= PLACE.mid_min_sections
        && whole(s, CLSF_PAGE3) * 100 <= (long long)PLACE.z_mid_pct * s->k->bytes;'
SAB_AFTER='    return whole(s, CLSF_PAGE3) * 100 <= (long long)PLACE.z_mid_pct * s->k->bytes;'
