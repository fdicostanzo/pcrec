# S130 ([M6.6.2] wave D, design §9.3 S-LA15) — `.behind` IS READ.
#
# **RE-HOMED AT WAVE D, AND IT IS NOW LIVE.** The row was written out at wave
# B+C (R33 C2-8 required all three flag rows written rather than promised) and
# scored UNDETECTED there BY CONSTRUCTION: what `.behind` SELECTS is §3.4's
# back-step and end-check, and neither existed — `pcrec_laport_group` declined
# the three `(?<` tails at `WANT_RESULT`, so no `A_LOOK` with `behind == true`
# could be built at all, and `vm_look`'s only read of the flag was a LOUD
# `ctx_fail` whose deletion was unobservable because nothing could reach it. A
# sabotage of an unreachable guard is not a detector, and wave B+C's report
# said so rather than letting a matrix reader take it for a finding.
#
# WAVE D LANDED THE BACK-STEP AND THE ANCHOR MOVED WITH IT, exactly as that
# header said it must: `SAB_BEFORE` is now the emission that BRANCHES on
# `.behind`, and the sabotage emits the LOOKAHEAD shape for both directions —
# body forward from the cursor, no back-step, no end-check. That is precisely
# the silent miscompile the retired `ctx_fail` existed to make impossible while
# the wave was half-landed.
#
# THE ARTIFACT STILL COMPILES AND STILL ANSWERS, which is what makes this a
# detector rather than an anomaly: `behind` is still read by the entry label's
# role text, the slots are still allocated, and `vm_count_slots`' extra
# per-branch pushes become an over-count (safe). A lookbehind simply becomes a
# LOOKAHEAD, so `(?<=a)b` matches "ab" at 0 where the truth is (1,2).
#
# [M6.6.2 wave E2] `laexpand` ADDED TO THIS ROW, and it was MEASURED before it
# was assigned (2026-08-24, one laexpand-only mech run per row: 8 of the
# module's 15 rows DETECTED, 7 UNDETECTED — the table is in
# tests/mech/CLAUDE.md). What the substitution driver sees here that the
# module's own corpus does not is DEPTH: 8,260 libpcre2-verified cells
# belonging to a module that already ships, re-expressed as lookarounds. For
# this row, three expansions are LOOKBEHINDS (`(?<=\w)`, `(?<!\w)`, `(?<=\n)`),
# so a lookbehind emitted with the lookahead shape inspects the wrong side
# of the cursor on the `\b`, `\B` and `(?m)^` populations.
SAB_ID="S130-look-ignores-behind"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness lookaround laexpand"
SAB_HARNESS_TARGET="tests/lookaround"
SAB_DESC="vm_look stops reading Ast.u.look.behind, so a LOOKBEHIND is emitted with the lookAHEAD shape — the body runs FORWARD from the cursor with no back-step and no end-check, and the assertion inspects the bytes after the cursor instead of the ones before it"
SAB_DOC_FIGURE="PREDICTED: every (?<= , (?<! and (?<* cell goes red — lookbehind.rxt, lookbehind_widths.rxt, startpos.rxt and nonatomic_behind.rxt all RED, workbudget.rxt RED — while every lookAHEAD cell (lookahead.rxt, captures.rxt, quantified.rxt, nonatomic_ahead.rxt) stays GREEN. Canonical figure owed from run_sabotage_matrix.sh S130."
SAB_COUNT=1
SAB_BEFORE='    if (behind) {
        vm_look_behind(v, a, okl, mslot, pslot);
    } else {
        const int bodyl = vm_label(v);
        vm_goto(v, bodyl);
        vm_emit(v, bodyl, a->l, okl);
    }'
SAB_AFTER='    {   /* SABOTAGE S130: .behind is not read — the lookAHEAD shape for both */
        const int bodyl = vm_label(v);
        vm_goto(v, bodyl);
        vm_emit(v, bodyl, a->l, okl);
    }'
