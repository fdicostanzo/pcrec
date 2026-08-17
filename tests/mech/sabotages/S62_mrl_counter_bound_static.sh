# S62 — [M4.6d] THE COUNTER RUNG'S BOUND MADE COMPILE-TIME ONLY.
#
# This is the defect the build lane actually shipped first, restored as a row
# so it cannot come back unannounced.
#
# On the counter rung ONE emitted body copy serves every trip, so the emitter's
# compile-time view of "how many mandatory iterations still follow" tops out at
# `K + residue`. The truth is `count - stv[ctr] - j`, and it lives in a TRAILED
# slot rather than in the emitter. §4.5 designed that runtime expression;
# `Vm.fdyn` is it. Dropping it leaves the copies with the within-trip constant:
# on `(a{1,3}){65}` that is NINE bytes of follow where the real one is 65, and
# nine bytes of slack leaves the whole ambiguous decomposition of a 65-byte
# subject unpruned. The artifact returns RX_ERR_STEPS — K23, on a shape
# squarely in K23's population, out of the fix for K23.
#
# THE TRIP GUARD'S OWN RUNTIME TERM IS LEFT INTACT, deliberately: it is a
# separate call site, and leaving it means this row tests the PER-COPY bound
# rather than "the counter rung lost its expression". A sabotage that removes
# both would pass for the same reasons and tell you less about which site
# matters.
#
# NOTHING ELSE SEES IT, which is why §1b exists as its own acceptance cell.
# The differential agrees (both arms explore the same space and both give up),
# the corpus has no such shape unless someone put one there, and the §1 cell
# uses the design note's own exemplar, which reaches its collapse through the
# CURSOR rung and answers either way. That blindness is the row's point:
# every instrument derived from the emitter's model inherited the model the
# bug was in.
SAB_ID="S62-mrl-counter-bound-static"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="mrl"
SAB_DESC="the counter rung's per-copy follow-min drops its runtime term and keeps the within-trip constant (K + residue), so a mandatory phase far longer than K goes unpruned and K23 returns on (a{1,3}){65}"
SAB_DOC_FIGURE="tests/mrl/run_mrl_tests.sh §1b; k23_design.md §4.5, §14.6"
SAB_COUNT=1
SAB_BEFORE='                    dyn = vm_dyn_add(v, v->fdyn,
                                     vm_rolef(v, "%lld * ((ptrdiff_t)%d - stv[%d])",
                                              bw, count - (i + 1), ctr));'
SAB_AFTER='                    dyn = NULL;  /* SABOTAGE S62 */'
