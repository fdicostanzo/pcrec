# S102 (design row S-BR14) — A DFA PREFILTER IS ATTACHED TO A BACKREF PATTERN.
#
# THE WRONG-ANSWER ROW, and R32 C4 added it because the first design's
# eighteen rows had none. Every other row in this module's family fails as a
# REFUSAL, a hang or a structural mismatch; this one changes an ANSWER, and it
# changes it on a population no refusal-shaped check can see.
#
# WHY IT IS WRONG. `engine_m4.md` §6.1's hybrid needs the forward+reverse DFA
# pair to hand the VM the EXACT anchored window. For a capture-only pattern
# that is STRUCTURAL — `(a|b)` and `(?:a|b)` build the identical `Ast` (D31),
# so the prefilter's DFA IS the pattern's DFA. A backreference has no such
# identity: APPROACH §2's "backrefs -> their referenced sub-pattern" is a real
# approximation, and MEASURED over 12,786 distinct subject-family pairs its
# leftmost SPAN differs from the true one on up to 389 subjects in one family.
# `(["'])[^"']*\1` on "\"''" is truly (1,3) and the erasure says (0,2); a VM
# anchored to (0,2) does not find the (1,3) match.
#
# WHAT CATCHES IT is `run_backref_diff.sh` §8, whose population is exactly the
# subjects on which the two spans DIVERGE AND whose erased window fails to
# CONTAIN the true match — EXACTLY 3, asserted, one per family (see that
# script's §8 comment block: the design's five-cell list had one detector),
# because this sabotage is INVISIBLE on any subject where they agree.
SAB_ID="S102-prefilter-on-backref"
SAB_FILE="src/opt/select_engine.c"
SAB_SUITES="brefdiff harness"
SAB_HARNESS_TARGET="tests/backrefs"
SAB_DESC="EngineFit.prefilter is no longer forced false for a backref-bearing pattern, so the capture-erased DFA pair is built and hands the VM a window computed for a DIFFERENT language. The failure is a WRONG SPAN on the subjects where the erasure's leftmost match differs from the true one -- and on every other subject the answers are identical, which is why only run_backref_diff.sh's span-divergence section can see it"
SAB_DOC_FIGURE="PREDICTED: brefdiff RED in §8 (the span-divergence section). Canonical figure owed from run_sabotage_matrix.sh S102."
SAB_COUNT=1
SAB_BEFORE='        fit.prefilter = has_bref ? false'
SAB_AFTER='        fit.prefilter = false ? false   /* SABOTAGE S102 */'
