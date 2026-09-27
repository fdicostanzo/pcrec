# S305 — [OPT-LITSCAN] S2a THE SLOT WALK AND THE EMISSION DISAGREE ABOUT
# WHERE A RUN ENDS (src/gen/emit_vm.c, `vm_count_slots`'s A_CAT arm): the
# pre-pass skips one element PAST each literal run, so whatever follows a run
# on its spine is never counted, while `vm_cat` still emits it.
#
# THIS IS R5's DEFECT PLANTED ON PURPOSE (patfacts design §8.2: "the cost and
# slot walks re-derive shape questions and have disagreed before"). The cure
# is that the three readers ask ONE function; this row is a reader that
# stops trusting its answer. What follows a run can carry slots and resume
# points, and an uncounted resume point means PCREC_MAX_VM_RESUME_POINTS is
# checked against a number smaller than the program it bounds — the
# `resume-points` comparison in tests/codegen/run_ir_listing.sh, whose sweep
# carries `xy(a|ab)c` (tests/litscan/litrun.rxt) for exactly this: a run,
# then a capture over a two-branch chain that pushes one frame.
#
# The cost walk's twin plant is not a row: an A_CLASS run costs nothing and
# the element after it is sized against the default frame capacity on every
# witness tried, so it moves no stamp or answer this tree can read
# (docs/dev/lanes/s2a_report.md).
SAB_ID="S305-lit-run-slot-walk-overskips"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="irlisting"
SAB_DESC="vm_count_slots skips the spine element after every literal run, so the slot/resume-point pre-pass under-counts what vm_cat emits after a run: xy(a|ab)c's pre-pass counts 0 resume points against 1 emitted RX_PUSH"
SAB_DOC_FIGURE="PREDICTED (lane s2a, 2026-09-27): DETECTED by run_ir_listing.sh's resume-points under-count check on xy(a|ab)c. MEASURED: see docs/dev/lanes/s2a_report.md. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S305."
# [MECH-REACH] the witness takes the run arm and pushes after it.
SAB_REACH='"$PCREC" --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern "xy(a|ab)c" && grep -qF "!memcmp(subject + scan_position, \"xy\", 2)" "$REACH_TMP/o.c" && grep -q "RX_PUSH(" "$REACH_TMP/o.c" && echo REACH-RUN-THEN-PUSH'
SAB_REACH_EXPECT="REACH-RUN-THEN-PUSH"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            if (len) { j += len; continue; }
            vm_count_slots(v, el[j], repl, false);'
SAB_AFTER='            if (len) { j += len + 1; continue; }   /* SABOTAGE S305 */
            vm_count_slots(v, el[j], repl, false);'
