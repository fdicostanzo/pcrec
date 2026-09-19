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
SAB_DOC_FIGURE="MEASURED 2026-09-19 (adm71 item 3, solo mech run, tree 37e42b8c9d6c1330d3283e49ee688677394e23ab): DETECTED, unexpected: 0 -- reach:ok, codegen:3fail/106pass, corpus:0fail/53pass, atomicdiff:0fail/8pass. Confirms dd8_report.md section 6's own first-ever measured drive of this row (same split at a different pin) rather than superseding it. THE PREDICTION'S atomicdiff HALF DOES NOT HOLD: detection is carried ENTIRELY by codegen's rule 1(a) [M6.4-ATOMIC rule 1] (the ENTRY site's static text disagreeing with the stamp's independent computation, per the row's own two-source design) -- atomicdiff reads 0fail/8pass on BOTH engine axes, not a DEFAULT-red/--engine=vm-green split. Hand-reproduced independently of the mech harness: applying only this edit and compiling the row's own named witness, '(?>a|ab)c|abcd' on \"abcd\", through --emit-main gives the CORRECT answer (0,4) even under the sabotage (and 'x*(?>a|ab)c|abcd' on \"xxxabcd\" gives the correct (3,7)) -- so the SAB_DESC's \"the uncut twin ends at 3\" is the THEORETICAL hazard H3 exists to forbid, not an answer this specific witness/subject pair, or atomicdiff's 8-cell corpus, actually exposes. The row still detects and still proves the two-source form is load-bearing (codegen rule 1(a) fires, rule 1(b)/1(c)/1(d) stay green, per the row's own disjointness claim) -- only the CHANNEL moved from the predicted answer-level one to the structural one."
SAB_COUNT=1
SAB_BEFORE='            v.nclamp == 0 ? ""
              /* H3 site 1 of 3 (the search ENTRY). */
              : v.mrl_win
'
SAB_AFTER='            v.nclamp == 0 ? ""
              : job->fit.prefilter   /* SABOTAGE S88: the stamp reads the H3
                                      * predicate; this site does not */
'
