# S175 — [DD-14 wave G] SPLICE ELIGIBILITY ADMITS A RECURSIVE CALLEE.
#
# Design §6.3 condition 1: a call site splices only if the callee is NOT IN A
# CYCLE. It is one array lookup — `reaches(i, i)` over the transitive closure —
# and everything downstream rests on it. `src/ir/nfa.c` inlines a spliced
# callee's fragment and calls the result EXACT; `src/opt/select_engine.c` lets
# a spliced call reach the DFA engine; `vm_splice` emits the callee's body at
# the site. Every one of those is a finite operation only because the callee's
# inlining terminates.
#
# THE PREDICTION IS NOT "A WRONG ANSWER", IT IS "NO ANSWER", and that is the
# whole reason this row needs its own guard on the product side. Without one,
# a spliced recursive callee recurses for ever in `vm_count_slots` — which
# charges nothing, so `PCREC_MAX_VM_NODES` never fires — and takes the C stack
# with it. A HANG IS THE ONE FAILURE A SABOTAGE MATRIX CANNOT REPORT: the row
# would look like an infrastructure timeout rather than a detection, and a
# matrix that cannot tell those apart has stopped being evidence.
#
# So wave G ships a splice-DEPTH counter in both walks, bounded by the number
# of call targets, and this row is what says it is load-bearing rather than
# defensive decoration. Under the sabotage a recursive callee's expansion is
# computed (its own `splice` flag is still false when its self-edge is read, so
# the expansion looks small), it passes the size budget, and the guard turns
# the resulting infinite descent into a NAMED internal error at compile time.
SAB_ID="S175-eligibility-splices-a-cycle"
SAB_FILE="src/opt/callgraph.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion/leftrec.rxt"
SAB_DESC="cg_eligibility stops settling cyclic targets first, so reaches(i,i) never disqualifies anyone and a RECURSIVE callee is marked CALL_SPLICE. Its expansion looks small (its own splice flag is still false when the self-edge is read), it passes the size budget, and the emitter is then asked to inline a callee that contains itself."
SAB_DOC_FIGURE="PREDICTED: every recursive pattern in tests/recursion/ REFUSES TO COMPILE with 'a spliced subroutine call nested more than N deep, so the splice eligibility rule admitted a cycle' -- leftrec.rxt, whole.rxt's (?R) cells, mrl.rxt, slotfamilies.rxt and quantified.rxt all red as pattern-compile failures rather than as wrong answers. WITHOUT the splice-depth guard the same sabotage HANGS instead, which is the reading this row exists to make impossible; the guard is the product-side line that turns it into a diagnostic. The NON-recursive corpus stays green, which is the pair that names the failure. Canonical figure owed from run_sabotage_matrix.sh S175."
SAB_COUNT=1
SAB_BEFORE='        done[i] = pcrec_callgraph_reaches(cg, i, i);   /* cyclic: exp stays INF */'
SAB_AFTER='        done[i] = false;   /* SABOTAGE S175 */'
