# S147 ([DD-14] wave B+C, design SS9.3 S-SR5) -- THE CALLEE INHERITS THE
# CALLER'S CAPTURE ENVIRONMENT.
#
# THE CLAIM (design SS3.1, MEASURED, one cell):
#
#     ^(a)(b\1)(?2)$  on "ababa"  ->  (0,5) g1=(0,1) g2=(1,3)
#
# Group 2's body is `b\1`. The call RE-RAN it and `\1` was still "a" -- so a
# call is NOT a fresh capture environment. The control is the same pattern on
# "abab", which is NOMATCH: an unset-and-empty `\1` would have matched it, so
# the pair separates "inherited" from "unset" rather than merely reporting a
# span. The same holds under `PCRE2_MATCH_UNSET_BACKREF`, where an unset
# reference matches empty and the two designs would differ by LENGTH rather
# than by match/no-match -- still nomatch.
#
# THE SABOTAGE IS THE SMALLEST EDIT THAT EXPRESSES THE OTHER DESIGN. The call
# site's save is a TRAILED SELF-WRITE -- `RX_SET(s, slot_values[s])` -- which
# parks the value on the trail and leaves the slot alone. Writing
# `PCREC_UNSET` instead parks the same value and CLEARS the slot, which is
# exactly "the callee gets a fresh environment" and nothing else: the trail
# still carries what the return needs, the offsets are unmoved, and the
# capacity is unchanged. A row that removed the writes entirely would break
# the restore too and be caught by S143's population instead of by this one's.
SAB_ID="S147-call-zeroes-env"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion"
SAB_DESC="The call site ZEROES W's slots instead of parking their values, so the callee starts from a fresh capture environment -- a backreference inside a called body then reads UNSET where it must read the caller's group"
SAB_DOC_FIGURE="PREDICTED (design 9.3 S-SR5): ^(a)(b\\\\1)(?2)\$ on \"ababa\" goes from (0,5) to nomatch. captures.rxt carries it with its \"abab\" control, which an unset-and-empty \\\\1 would have matched."
SAB_COUNT=1
SAB_BEFORE='            snprintf(val, sizeof val, "slot_values[%s_%s]", v->up, nm);
        else
            snprintf(val, sizeof val, "slot_values[%d]", a->u.call.save[j]);'
SAB_AFTER='            snprintf(val, sizeof val, "PCREC_UNSET");   /* SABOTAGE S147 */
        else
            snprintf(val, sizeof val, "PCREC_UNSET");'
