# S1476 (lane cfcount) -- `X+` SENT TO A ONE-TRIP COUNTER AT K=1.
#
# `vm_counter_fits` accepts an unbounded repeat when its mandatory count is
# both >= K and >= 2. The plant drops the `>= 2` term, which is the predicate
# as it stood before this lane: at K=1 every `X+` takes the counter rung, whose
# init and trip writes add two trail entries per entry for the one body copy
# the frames rung emits anyway. ANSWER-IDENTICAL (the counter's iteration count
# is exact at any K), so only a structural or size assertion can be red.
#
# THE DETECTORS are run_size_term.sh §3's cells: the direct one (the rung stamp
# of `(?:ab|b)+c` at --unroll=1 must not carry COUNTER) and the consequence
# (NEST8's lower declared capacity at K=1 drops K=1 below the §3.3a floor, so
# the term ships K=2 instead of 1).
SAB_ID="S1476-counter-fits-xplus-at-k1"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="sizeterm"
SAB_DESC="vm_counter_fits loses its rmin >= 2 term, so at K=1 every unbounded X+ takes a one-trip counter; answers are unchanged, the rung stamp and NEST8's capacity (and with it the size term's K) move"
SAB_DOC_FIGURE="PREDICTED: sizeterm 2 fail (section 3: '(?:ab|b)+c' takes the counter rung at --unroll=1; NEST8 carries K=2, not 1). Measured by hand on lane cfcount before the row existed: the pre-fix compiler stamps RX_VM_RUNGS 0x10u (COUNTER) on '(?:ab|b)+c' at --unroll=1, and NEST8 ships RX_UNROLL_K 2. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1476."
SAB_REACH='"$PCREC" -p rx --features all --engine=vm --unroll=1 -o "$REACH_TMP/r1.c" --pattern "(?:ab|b)+c" && grep -h "define RX_VM_RUNGS" "$REACH_TMP/r1.c"'
SAB_REACH_EXPECT="#define RX_VM_RUNGS 0x4u"
SAB_REACH_POP="tests/codegen/run_size_term.sh|^rung_counter\(\) |1"
SAB_COUNT=1
SAB_BEFORE='    if (a->u.rep.rmax < 0) return a->u.rep.rmin >= v->unroll_k && a->u.rep.rmin >= 2;'
SAB_AFTER='    if (a->u.rep.rmax < 0) return a->u.rep.rmin >= v->unroll_k;   /* SABOTAGE S1476 */'
