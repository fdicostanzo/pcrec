#!/usr/bin/env bash
# S917 ([MEMFN] R17-b' B1, lane fdb1; r17b_prime.md §8.3, §1.5 rule 3) -- AN
# ABSENT SET KEY READ AS 0.
#
# WHAT IT BREAKS. A finder row whose comparator names a key the active set
# does not hold must NOT hold (§1.5 rule 3: an unmeasured quantity is not
# evaluable; measure_sets §4.3: no fallback, no presumed value). The plant
# makes the finder's one lookup (memfn/src/finder.c `fd_lookup`) answer 0 for
# a key the set lacks, so R7's `saving > eps` and R0's `saving <= eps` compare
# a fabricated zero.
#
# WHERE IT IS SEEN. No artifact moves (no finder row is routed at B1). The
# finder check's R-MS1 loop (tests/memfn/finder_check.py D) runs every finder
# site under the full synthetic set and again with each key the decision read
# REMOVED in turn: with the plant the removed key reads 0 and the reading row
# still decides, which the check names. Arm memfnfinder.
SAB_ID="S917-fd-absent-key-read-as-zero"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="memfnfinder"
SAB_DESC="the finder table's lookup answers 0 for a key the measurement set does not hold, so a row reading an unmeasured quantity still decides"
SAB_DOC_FIGURE="HAND-MEASURED by lane fdb1: see docs/dev/lanes/fdb1_report.md (the solo mech run of this row)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return found;
}

/* A template'"'"'s value: expand, then look up. */'
SAB_AFTER='    if (!found) { *v = 0; found = 1; }   /* SABOTAGE S917: an absent key reads 0 */
    return found;
}

/* A template'"'"'s value: expand, then look up. */'
