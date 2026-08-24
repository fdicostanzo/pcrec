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
# **THE FIRST VERSION OF THIS SABOTAGE COULD NOT EXPRESS H-NEVER, AND THE
# MATRIX SAID SO.** It wrote `PCREC_UNSET` into the |W| saves instead of the
# slots' own values -- which reads like "the callee gets a fresh environment"
# and is not, because **`W` is EXACTLY the set the callee writes**. Clearing
# those slots clears only what the callee immediately overwrites, so the
# inheritance cell `^(a)(b\1)(?2)$` still matched: `W(2)` holds group 2's
# slots, group 1's are not in it, and `\1` inside the callee read the caller's
# group exactly as it should. Scored **UNDETECTED, corpus 0fail/306pass**, and
# the finding is about the ROW rather than the compiler -- this project's own
# "prove your instrument is live before trusting a negative result", one level
# down.
#
# THE CORRECTED SABOTAGE CLEARS THE COMPLEMENT: every capture slot the callee
# does NOT write. The |W| saves are LEFT INTACT, so the trail still carries
# what the return needs, the offsets are unmoved and the capacity is
# unchanged; the only change is what the callee can SEE, which is the whole of
# the hypothesis. A row that removed the saves entirely would break the
# restore too and be caught by S143's population instead of by this one's.
SAB_ID="S147-call-zeroes-env"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion"
SAB_DESC="The call site ZEROES W's slots instead of parking their values, so the callee starts from a fresh capture environment -- a backreference inside a called body then reads UNSET where it must read the caller's group"
SAB_DOC_FIGURE="PREDICTED (design 9.3 S-SR5): ^(a)(b\\\\1)(?2)\$ on \"ababa\" goes from (0,5) to nomatch. captures.rxt carries it with its \"abab\" control, which an unset-and-empty \\\\1 would have matched."
SAB_COUNT=1
SAB_BEFORE='    vm_goto(v, v->rgn_lbl[idx]);
    vm_lbl(v, ret, "the call returned; continue here");'
SAB_AFTER='    /* SABOTAGE S147: the callee gets a FRESH capture environment.
     * Every capture slot NOT already parked by the |W| saves above is
     * cleared, which is exactly H-NEVER -- the hypothesis SS3.1 had to build
     * a callout probe to refute, because it produces the same after-the-fact
     * table as H-RESTORE. */
    for (int zz = 2; zz < 2 * (v->ngroups + 1); zz++) {
        bool inw = false;
        for (int jj = 0; jj < a->u.call.nsave; jj++)
            if (a->u.call.save[jj] == zz) inw = true;
        if (!inw) vm_set(v, zz, "PCREC_UNSET", "SABOTAGE S147");
    }
    vm_goto(v, v->rgn_lbl[idx]);
    vm_lbl(v, ret, "the call returned; continue here");'
