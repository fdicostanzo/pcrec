# S178 — [DD-14 wave G] THE DISCHARGED ROOT IS NOT PUBLISHED.
#
# `pcrec_discharge_atomic` rewrites IN PLACE for every node except the ROOT: its
# `A_ATOMIC` arm returns `a->l`, the spliced-in body, so a pattern whose whole
# tree IS a dischargeable atomic group gets a DIFFERENT root pointer back.
#
# **THAT RETURN VALUE WAS DROPPED ON THE FLOOR FOR THE WHOLE OF [M6.4.2].** The
# call lived inside `pcrec_select_engine`, which assigned it to a LOCAL: the
# analyses in that pass therefore judged the DISCHARGED tree while
# `src/core/compile.c`'s `root` — the one every later pass and both emitters
# walk — still carried the `A_ATOMIC`. Wave G's pass reorder hoisted the call
# into `compile.c` (the call graph has to run after every rewriting pass, and
# engine selection after the call graph), and publishing the root is what that
# hoist made possible. This row is the drop, put back.
#
# ============================================================================
# ITS PREDICTION IS *UNDETECTED*, AND THE SEARCH IS THE POINT OF THE ROW
# ============================================================================
# A row that predicts a red cell and finds none has measured something; a row
# that quietly expects nothing has not. So the search is recorded:
#
#   MEASURED at the wave, shipped build against a build of the PRE-HOIST commit
#   85361cd, `--engine=vm`, same output basename so the `#include` line cannot
#   confound the diff — SIX patterns whose ROOT node is a dischargeable
#   `A_ATOMIC`:
#
#       (?>[^"]*)   (?>a*+)   (?>(?:ab)*)   (?>[^x]*)x   (?>a|ab)   (?>[^"]*+")
#
#   **Every one emits a BYTE-IDENTICAL artifact.**
#
# AND THE REASON IS STRUCTURAL RATHER THAN LUCKY, which is what makes the
# expectation safe to write down. The discharge fires exactly where possessify's
# §2.2 verdict proves the cut dead — and that is the same condition `vm_lifts`
# tests: a group whose cut is dead is LIFTED onto the possessive rung, and a
# lifted group "allocates NO mark of its own — the rung below allocates it"
# (`vm_count_slots`' own arm). So `(?>a*)` and `a*` emit the same program
# whether the `A_ATOMIC` was deleted before the emitter saw it or lifted away by
# the emitter itself, and the drop had no reachable consequence.
#
# WHAT THE FIX BUYS is that the two trees can no longer DISAGREE — engine
# selection judged one and the emitter walked another, which is the shape
# §4.4c's "two programs for one group" describes one construct over, and which a
# future rewrite with no lift equivalent would turn into a real divergence with
# no check standing under it. This row is that check, waiting.
SAB_ID="S178-root-discharge-dropped"
SAB_FILE="src/core/compile.c"
SAB_SUITES="harness atomicdiff"
SAB_HARNESS_TARGET="tests/atomic_groups"
SAB_EXPECT=UNDETECTED
SAB_DESC="compile.c stops PUBLISHING the discharged root, so a pattern whose whole tree is a dischargeable atomic group is judged by engine selection as discharged and EMITTED as undischarged -- the [M6.4.2] drop wave G's pass hoist fixed, put back."
SAB_DOC_FIGURE="PREDICTED **UNDETECTED**, with the search recorded rather than the expectation asserted: six patterns whose ROOT is a dischargeable A_ATOMIC ((?>[^\"]*), (?>a*+), (?>(?:ab)*), (?>[^x]*)x, (?>a|ab), (?>[^\"]*+\")) emit BYTE-IDENTICAL artifacts before and after the fix, because the discharge fires exactly where vm_lifts lifts -- a lifted group allocates no mark of its own, so the deleted-before and lifted-away spellings are the same program. The row exists because the property it defends (engine selection and the emitter walk ONE tree) has no other check, and a future rewrite with no lift equivalent would make the drop a real divergence. Canonical figure owed from run_sabotage_matrix.sh S178."
SAB_COUNT=1
SAB_BEFORE='    root = pcrec_discharge_atomic(&cx, root);'
SAB_AFTER='    pcrec_discharge_atomic(&cx, root);   /* SABOTAGE S178: the root is not published */'
