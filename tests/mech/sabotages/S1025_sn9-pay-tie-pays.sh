#!/usr/bin/env bash
# S1025 (SN-9; [MEMFN] R17-b' B1, lane fdb1; r17b_prime.md §8.3 [rev3 D9], §2.5)
# -- THE PAY RULE'S T1 TIE PAYS.
#
# WHAT IT BREAKS. A dispatch interval pays only where every measured point's
# saving LOWER bound beats the call charge's UPPER bound STRICTLY: a tie does
# not pay (§2.5 [D9]: equality is "not measurable", so a T1 tie declines). The
# plant turns the strict compare into `>=` (memfn/src/finder.c `fd_pay`).
#
# WHERE IT IS SEEN. The pay rule's arithmetic grid (tests/memfn/
# finder_check.py H, arm memfnfinder): operands at, one below and one above
# every boundary, the expected bits computed independently; the T1 ties read
# 1 under the plant.
SAB_ID="S1025-sn9-pay-tie-pays"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="memfnfinder"
SAB_DESC="the pay rule's T1 compares with >= so a saving that exactly equals the dispatch charge pays"
SAB_DOC_FIGURE="HAND-MEASURED by lane fdb1: see docs/dev/lanes/fdb1_report.md (the solo mech run of this row)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            if (!(p->saving[i] - p->saving_floor[i] > p->call + p->call_floor)) t1 = 0;'
SAB_AFTER='            if (!(p->saving[i] - p->saving_floor[i] >= p->call + p->call_floor)) t1 = 0;   /* SABOTAGE S1025 */'
