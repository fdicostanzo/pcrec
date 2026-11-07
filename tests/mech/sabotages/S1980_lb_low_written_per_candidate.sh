# S1980 ([VLOOKBEHIND] stage 1, design §7 W12 (a)) -- ONE TRAILED WRITE PER
# EVALUATION. The trail term is O(1) per varying branch because LO_i is written
# once; a write per candidate grows the trail with every candidate tried and
# overruns the term. Depends on K134's compaction trigger (design §7 W12): a
# K134 change that re-arms compaction can turn this row green and must re-aim it.
# RE-PLANTED 2026-11-06 (lane vlbfix, review r4 F9): the first plant MOVED the
# write to L_try_i, writing the CANDIDATE into LO_i, so the exhaustion test
# compared against a moving bound and 22 cells failed as wrong answers, never
# as a trail overrun. This plant keeps the once-per-evaluation write and adds
# a second, trailed write of LO_i's OWN value at every candidate: no answer
# can move except through the trail. MEASURED: it overruns at TWO candidates
# already, so W12 (a)'s nine-candidate cells are not what discriminates.
SAB_ID="S1980-lb-low-written-per-candidate"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='LO_i is re-written (its own value, trailed) at L_try_i, once per candidate, on top of its once-per-evaluation write'
SAB_DOC_FIGURE='MEASURED (lane vlbfix, tools/review/plant.sh + harness on the target): 36 pass / 18 fail, every failure "test binary GAVE UP (frames)", none a wrong answer: lines 19 39 45 52 80 124 130 149 156 162 169 185 229, W12 (a) (149, 156) among them and two-candidate cells first ((?<=a{1,2})x on abx, line 19; (?<!ab?)x, line 39); clean 54/0.'
SAB_COUNT=1
SAB_BEFORE='    vm_lbl(v, L->try_[i], "lookbehind: try this candidate start");'
SAB_AFTER='    vm_lbl(v, L->try_[i], "lookbehind: try this candidate start");
    vm_set(v, lox, vm_slot_expr(v, lox), "SABOTAGE S1980");'
