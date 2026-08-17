# S60 — [M4.6d] THE CLAMP LEFT OFF THE CURSOR'S ITERATION LATTICE.
#
# R26 E1's defect, restored. A stride-W span loop admits only the positions
# `pos, pos+W, pos+2W, ...`; the clamp ASSIGNS a cursor value, so the value it
# assigns must be one of them. `<PREFIX>_MRL_CAP`'s integer division is the
# whole of that rounding. Deleting it lands the cursor between two iteration
# boundaries, and an off-lattice cursor poisons the ENTIRE retreat chain below
# it — every position the retreat visits is also off-lattice, so the correct
# cursor value is deleted from the choice set.
#
# THIS IS NOT "PRUNES TOO MUCH". §4.2 step 3's load-bearing clause is that the
# clamp never INTRODUCES a candidate that was not there, and substitution
# satisfies "removes only doomed candidates" while still changing the answer.
# The measured original: 5 of 8 subjects answered `nomatch` on
# `((?:ab){10,20}){10,50}` where both the unpruned build and python match.
#
# IT IS INVISIBLE AT STRIDE 1, which is the reason this row exists rather than
# being covered by S59. At W = 1 the rounding is the identity and the broken
# clamp emits arithmetically equal code — 855 cells of single-byte-alphabet
# corpus could not distinguish them under any subject. `tests/mrl/patterns.txt`
# carries bodies of width 1, 2 and 3 at lengths on and off the lattice for
# exactly this row, and `run_mrl_tests.sh` §2 additionally asserts that the
# emitted cap CARRIES the stride, so the rounding cannot be removed without
# something saying so.
SAB_ID="S60-mrl-clamp-off-lattice"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="mrldiff mrl"
SAB_DESC="the emitted clamp drops its lattice rounding, assigning the cursor a position the span loop can never occupy: R26 E1's unsound clamp, invisible at stride 1 and wrong above it"
SAB_DOC_FIGURE="docs/design/k23_impl/k23_design.md §4.1 (R26 E1)"
SAB_COUNT=1
SAB_BEFORE='            "    ((p_) + (size_t)(w_) * (((%s_ceil) - (size_t)(mr_) - (p_)) / (size_t)(w_)))\n\n",'
SAB_AFTER='            "    ((%s_ceil) - (size_t)(mr_))  /* SABOTAGE S60: no lattice rounding */\n\n",'
