# S263 — [OPT-ANCHOR-VM] THE VM'S ATTEMPT-LOOP START BOUND IS EMITTED AS
# `subject_length` WHERE THE PREDICATE SAYS `search_from` (src/gen/emit_vm.c),
# so an artifact that has PROVED only one start position can match still walks
# every one of them.
#
# THIS ROW'S DETECTOR IS THE STAMP, AND THAT IS A PROPERTY OF THE MECHANISM
# RATHER THAN A GAP IN THE SUITE. Every attempt the bound removes is an
# attempt the artifact would have RUN AND FAILED — the pattern is `^`- or
# `\G`-anchored, so the assertion fails at every start position but the first.
# Deleting the bound therefore changes RUN TIME and nothing a caller can
# observe: no differential, no oracle, no corpus cell and no `.rxt`
# expectation anywhere in this tree can see this plant. `corpus:0fail` beside
# a red `prechecks` is this row working, not a half-detection.
#
# WHAT THE PLANT LEAVES INTACT IS WHAT MAKES IT FIND THE RIGHT CHECK. The
# stamp still reads `"anchored"`, the declaration is still emitted, and the
# loop still reads the name — so an artifact-level grep for `attempt_max`, or
# for the stamp's value, stays green. Only the BICONDITIONAL between the stamp
# and the bound's own right-hand side moves, which is what
# tests/codegen/run_prechecks.sh §1.1b asserts and why it asserts the text
# rather than the predicate (docs/dev/learnings.md §3).
#
# It is also why the plant is not the tempting one. Inverting the emission
# CONDITION (`!= PCREC_SANCH_NONE` -> `==`) would put the bound on artifacts
# that did NOT prove it and delete real matches — a loud, answer-level
# failure, and a test of a different claim. The sound-direction plant is the
# one that measures whether this mechanism has a detector at all.
SAB_ID="S263-vm-anchor-bound-subject-length"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="prechecks harness"
SAB_DESC="the VM search loop's start bound is emitted as 'attempt_max = subject_length' instead of 'attempt_max = search_from', so an artifact whose every match provably begins at offset 0 (or at the caller's startpos) still runs an attempt at every start position — a pure cost regression with NO answer-level detector anywhere in the tree, which is why this is a STAMP-vs-TEXT row and why a green corpus arm beside a red prechecks arm is the row working"
SAB_DOC_FIGURE="MEASURED 2026-09-22 (solo mech run, tree be7e8ef366ae238ed6c9c5d8625c0ca039112cdc — the mechanism's own landing commit, where tests/codegen/run_prechecks.sh carried only its §1): DETECTED, unexpected: 0 — reach:ok(1/1), prechecks:4fail/19pass, corpus:0fail/28960pass. The four reds are §1.1b on the four bounded witnesses (^abc, \\Aabc, ^(a|b)+\$, \\Gabc), each reporting 'stamps \"anchored\" but the emitted loop is not bounded by attempt_max'; the three unanchored witnesses stay green because the plant cannot reach them. THE CORPUS ARM'S ZERO IS THE POINT AND NOT A HALF-DETECTION: 28,960 cases, every one unaffected, because the bound removes only attempts that would have run and failed. The prechecks DENOMINATOR grows as the batch's other two sections land (19 pass here, 50 at [OPT-ENDWIN]'s landing, 110 at [OPT-REQBYTE]'s) — the FOUR reds are this row's own figure and do not move with it. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S263."
SAB_REACH='"$PCREC" --features all --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern "^(a)b" && grep -q "^#define RX_VM_START \"anchored\"" "$REACH_TMP/o.c" && grep -q "const size_t attempt_max = search_from;" "$REACH_TMP/o.c" && echo REACH-VM-START-BOUND-EMITTED'
SAB_REACH_EXPECT="REACH-VM-START-BOUND-EMITTED"
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_puts(c, "    const size_t attempt_max = search_from;\n");'
SAB_AFTER='        pcrec_sb_puts(c, "    const size_t attempt_max = subject_length;\n");   /* SABOTAGE S263: the bound the predicate proved, thrown away */'
