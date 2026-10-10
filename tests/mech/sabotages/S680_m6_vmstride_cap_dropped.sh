#!/usr/bin/env bash
# S680 ([MEMFN] M6, lane m6) -- THE STRIDED CAP LOST (S616's sibling).
# span_hi caps ADVANCE's counter in ITERATIONS (RULED Q-R10-5); the VM's
# bounded strided quantifier states rmax there. The plant drops it at W > 1
# only (VMSPAN keeps its cap): the kit then counts `it_` but never tests it.
# RE-AIMED 2026-10-09 (lane vmlazy, R-12 REPLACE): vm_span_advance takes the
# cap as a parameter (`cap`: rmax for the possessive/greedy scans, rmin for
# the lazy prefix) instead of reading a->u.rep.rmax; same plant, same
# intent. Its reach widens: the lazy prefix at stride > 1 loses its cap too.
SAB_ID="S680-m6-vmstride-cap-dropped"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/base/d27_bodies.rxt"
SAB_DESC='the VM span builder states span_hi UNBOUNDED at stride > 1, so a bounded strided quantifier'"'"'s it_ cap is lost and the strided loop runs past rmax iterations: (ab){2,4} matches more than four blocks'
SAB_DOC_FIGURE="HAND-MEASURED by lane m6 2026-10-08 (plant applied, tree rebuilt; docs/dev/lanes/m6_report.md section 6): harness tests/base/d27_bodies.rxt 4 failed / 155 passed ((ab){2,4} on \"ababababab\" answers (0,10) not (0,8)); over the whole corpus 12 cases (d27_bodies, d27_captures, d27_edge, d27_large_counts, recursion/d27/sr_define). The matrix figure is owed at the slot."
SAB_REACH='"$PCREC" -p rx -o - --pattern "(ab){2,4}"'
SAB_REACH_EXPECT='while ((rx_span_cursor + 2 <= subject_length) && it_ < 4ULL && (subject[rx_span_cursor + 0] == 97) && (subject[rx_span_cursor + 1] == 98)) {'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        .span = cap >= 0 ? (uint64_t)cap : MF_SPAN_UNBOUNDED,
        .indent = "        " };'
SAB_AFTER='        .span = cap >= 0 && stride == 1 ? (uint64_t)cap : MF_SPAN_UNBOUNDED,  /* SABOTAGE S680 */
        .indent = "        " };'
