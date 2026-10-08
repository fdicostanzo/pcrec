# S616 ([MEMFN] R4h, M3, lane r4h) -- THE VM SPAN LOOP LOSES ITS `it_` CAP.
#
# WHAT IT BREAKS. A bounded quantifier on the VM's cursor rung at stride 1
# (`[a-z]{2,9}` under `--engine=vm`) is one ADVANCE site of DELEG_SITES row
# VMSPAN: pcrec declares `it_` (0 at the loop, `count_start` 0) and reads
# it after, and the kit's loop advances it and tests the cap, `it_ <
# <rmax>ULL`. The plant drops that conjunct for sites whose counter starts
# at 0, so the span scan runs the class past rmax and the rung takes a
# continuation the quantifier forbids.
#
# KIT-SIDE, SCOPED BY A SITE FACT. The conjunct is memfn/src/generic.c's
# stmt_advance, shared by every capped ADVANCE site; `count_start` 0 is the
# VM span's (the scan edge's counter is 1 after pcrec's peeled step: S214 is
# that one, on the same line with the opposite scope).
#
# THE FAILURE MODE IS A FALSE MATCH. `(a)[a-z]{2,9}x` under `--engine=vm`
# on "abbbbbbbbbbbbx" (twelve letters) matches where python `re` answers no
# match. Hybrid artifacts hide it (the DFA prefilter's window is exact), so
# the detector is a corpus that runs the VM on its own.
SAB_ID="S616-r4h-vmspan-it-cap-dropped"
SAB_FILE="memfn/src/generic.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/possessify/possessify.rxt"
SAB_DESC="the kit's ADVANCE render drops the 'it_ < <rmax>ULL' cap on the VM span loop (sites whose counter starts at 0), so a bounded quantifier on the VM cursor rung scans past rmax: '(a)[a-z]{2,9}x' under --engine=vm matches \"abbbbbbbbbbbbx\", a FALSE MATCH"
SAB_DOC_FIGURE="HAND-MEASURED by lane r4h (plant applied, tree rebuilt): tests/possessify/possessify.rxt 26 failed / 3511 passed; tests/base/bounded_repeats.rxt and tests/counterk 0 (hybrid or counter rung). The matrix's own figure is owed at the slot."
SAB_REACH='"$PCREC" -p rx --engine=vm -o - --pattern "(a)[a-z]{2,9}x"'
SAB_REACH_EXPECT='&& it_ < 9ULL && ('
SAB_COUNT=1
SAB_BEFORE='    if (capped) kb_printf(b, " && %s < %lluULL", cnt, (unsigned long long)s->span_hi);'
SAB_AFTER='    if (capped && h->count_start != 0)  /* SABOTAGE S616: the VM span'"'"'s it_ cap is gone */
        kb_printf(b, " && %s < %lluULL", cnt, (unsigned long long)s->span_hi);'
