# S88 — [M6.4.2] RULE H3 IS APPLIED AT THE STAMP AND NOT AT THE CODE.
#
# THIS ROW IS R31 E3's FINDING, AS A ROW. The design's FIRST form of H3 said:
# edit `v.mrl_win = job->fit.prefilter` to `&& !has_atomic(root)`, and the
# artifact's own `RX_VM_PRUNE_CEILING` stamp is the check. Measured refutation:
# `v.mrl_win` is read at the `--emit-ir` description and at the STAMP, and
# NOWHERE ELSE. The two lines that BUILD the ceiling — the search entry's
# `window_end = min(window[0][1], n)` and the retry recompute — were gated on
# `prefn` and `v.nclamp > 0` and never on that flag. So the proposed edit flips
# the stamp to "subject-end" and leaves the ceiling LIVE, and a check asserting
# on the stamp would have been GREEN on a matcher silently losing matches.
#
# *A check that agrees with the bug is worse than no check*, and this row is
# what keeps the two-source form of `[M6.4-ATOMIC rule 1]` honest.
#
# WHAT IT IS THE FAILING DIRECTION OF: rule 1(a), and ONLY 1(a). The
# disjointness is the point — a row that turned BOTH halves red would not
# prove the two sources are needed.
#
# MEASURED before the row was written, by making exactly this edit on a live
# tree (`x*(?>a|ab)c|abcd`, a CLAMPING R3a pattern):
#     half-done edit : stamp "subject-end"   window[0][1] assignments left: 2
#     as shipped     : stamp "subject-end"   window[0][1] assignments left: 0
SAB_ID="S88-atomic-ceiling-stamp-only"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen harness atomicdiff"
SAB_HARNESS_TARGET="tests/atomic_groups/atomic_ceiling.rxt"
SAB_DESC="RULE H3's predicate is read by the STAMP but not by the two lines that build the ceiling, so a cut-bearing artifact stamps \"subject-end\" while still clamping to the prefilter's UNCUT window end. Silent match loss in the DEFAULT engine on the R3a family -- '(?>a|ab)c|abcd' on \"abcd\" is (0,4) and the uncut twin ends at 3 -- with the artifact's own stamp saying the ceiling is off"
SAB_DOC_FIGURE="PREDICTED: codegen rule 1(a) RED and rule 1(b) GREEN (the disjointness is the row's point); atomicdiff's DEFAULT arm RED with its --engine=vm arm GREEN, which is the hazard's own signature. Canonical figure owed from run_sabotage_matrix.sh S88."
SAB_COUNT=1
SAB_BEFORE='            v.nclamp == 0 ? ""
              /* H3 site 1 of 3 (the search ENTRY). */
              : v.mrl_win
'
SAB_AFTER='            v.nclamp == 0 ? ""
              : job->fit.prefilter   /* SABOTAGE S88: the stamp reads the H3
                                      * predicate; this site does not */
'
