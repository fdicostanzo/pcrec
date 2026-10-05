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
# carries `xyz(a|ab)c` (tests/litscan/litrun.rxt) for exactly this: a run,
# then a capture over a two-branch chain that pushes one frame.
#
# The cost walk's twin plant is not a row: an A_CLASS run costs nothing and
# the element after it is sized against the default frame capacity on every
# witness tried, so it moves no stamp or answer this tree can read
# (docs/dev/lanes/s2a_report.md).
#
# [OPT-LITSCAN F5, D127, 2026-09-28] RE-ANCHORED: the floor moved from two
# bytes to three, and the row's own witness (`xy(a|ab)c`) no longer takes
# the compare form at all, so `run_ir_listing.sh`'s PATTERNS array (and this
# row) widened it to `xyz(a|ab)c` -- the identical run-then-push shape, one
# byte longer, still above the new floor. Intent unchanged.
SAB_ID="S305-lit-run-slot-walk-overskips"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="irlisting"
SAB_DESC="vm_count_slots skips the spine element after every literal run, so the slot/resume-point pre-pass under-counts what vm_cat emits after a run: xyz(a|ab)c's pre-pass counts 0 resume points against 1 emitted RX_PUSH"
SAB_DOC_FIGURE="PREDICTED (lane s2a, 2026-09-27): DETECTED by run_ir_listing.sh's resume-points under-count check on xy(a|ab)c. MEASURED 2026-09-27 (lane s2a, single-row mech at b04e7ab3): DETECTED -- reach:ok(1/1), irlist:2fail/153pass (the resume-points under-count on xy(a|ab)c). RE-ANCHORED 2026-09-28 (lane litf5, [OPT-LITSCAN] F5/D127): witness widened xy(a|ab)c -> xyz(a|ab)c; re-run owed at merge. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S305."
# [MECH-REACH] the witness takes the run arm and pushes after it.
# RE-POINTED 2026-10-05 (lane r1mtriage): the run arm's COMPARE is no longer
# spelled memcmp since [OPT-HYB-RESEED-FORM] A1 (rsform, abi 56: overlapping
# rx_w2 word compares), so the probe read MISSING. It now greps the run arm's
# ADVANCE (one `scan_position += 3` jump), which no compare respelling moves
# and which the per-byte arm never emits. Intent unchanged.
SAB_REACH='"$PCREC" --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern "xyz(a|ab)c" && grep -qF "{ scan_position += 3; goto rx_L" "$REACH_TMP/o.c" && grep -q "RX_PUSH(" "$REACH_TMP/o.c" && echo REACH-RUN-THEN-PUSH'
SAB_REACH_EXPECT="REACH-RUN-THEN-PUSH"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            if (len) { j += len; continue; }
            vm_count_slots(v, el[j], repl, false);'
SAB_AFTER='            if (len) { j += len + 1; continue; }   /* SABOTAGE S305 */
            vm_count_slots(v, el[j], repl, false);'
