# S168 ([DD-14] wave B+C, design §5.8, §9.3 S-SR13) -- `goto *` COUNT ==
# 1 + THE NUMBER OF EMITTED SHARED CALLEE BODIES.
#
# NO ANSWER CHANGES, AND THAT IS THE ROW'S WHOLE POINT. The frame still
# carries the return label, every return still reaches it, and the emitted
# matcher is behaviourally identical -- a macro and an inline block are the
# same program. **The codegen count is the only detector**, which is S109's
# shape one construct over.
#
# THE INVARIANT THIS DEFENDS IS AN AMENDMENT, not a new claim.
# `src/gen/emit_vm.c`'s opening comment states as a design decision that there
# is "exactly ONE indirect jump in the whole function -- the `goto *` at the
# fail label, which fires once per backtrack and never per byte". `RX_RETURN`
# is a SECOND, and §5.8's amendment is the honest form of the property the
# file actually cares about: the indirect jumps are OFF THE HOT PATH -- one per
# backtrack, one per call return -- and there is still no per-byte dispatch, so
# D13's table-vs-computed-goto arbitration does not arise.
#
# IT ASSERTS THE RELATION AND NOT A CONSTANT, which R34's LENS2-5 refuted in
# BOTH directions: a call-free artifact is 1, a pattern calling ONE group is 2,
# a pattern calling THREE DISTINCT groups is 4 HOWEVER MANY CALL SITES there
# are (the sites share the body), and a wave-G fully-spliced artifact is back
# to 1. MEASURED over 9 prototype configurations in the design's own linkage
# probe: 9 rows, 9 OK, and the rows that matter are the ones a hard-coded "two"
# would fire on -- SPLICE is 1 at every k, and HYBRID at k = 0 is 1.
#
# SO THIS SABOTAGE FIRES ON EXACTLY ONE OF THE RULE'S FOUR FIXTURES, and the
# selectivity is the evidence: `(a)(b)(c)(?1)(?2)(?3)` emits 4 shipped and 2
# under the macro, while `(a)(?1)` and `(a)(?1)(?1)(?1)` stay at 2 and the
# call-free row stays at 1. A rule written as a constant would have passed
# this sabotage three times out of four.
#
# TWO SITES BY CONSTRUCTION (§9.3 says so): the macro has to be DEFINED as
# well as USED, and neither edit alone compiles.
#
# AND IT IS WHY THE SHIPPED EMITTER WRITES THE RETURN OUT INLINE, which is a
# deliberate deviation from §5.1's `RX_RETURN` macro sketch recorded at
# `vm_region`. A macro puts one `goto *` in the definition and NONE at the
# uses, so the artifact's count would be `1 + (has_calls ? 1 : 0)` and the
# relation would be unstateable. The design's own invariant is only checkable
# because the emission is per region.
SAB_ID="S168-return-through-macro"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen recursion"
SAB_DESC="the callee region's return is emitted through a SHARED MACRO instead of inline, so the artifact carries ONE indirect jump for every callee region however many there are -- no answer changes and the codegen count is the only detector"
SAB_DOC_FIGURE="PREDICTED (design 9.3 S-SR13): NO ANSWER CHANGES -- the frame still carries the return label and every return still reaches it. The codegen count is the only detector, and it is S109's shape. [DD-14-RECURSION rule 1] fires on the THREE-DISTINCT-CALLEE row: (a)(b)(c)(?1)(?2)(?3) emits 4 'goto *' shipped and 2 under this sabotage. The one-callee rows stay GREEN, which is exactly why the rule asserts a RELATION and not a constant -- a hard-coded 'two' would have passed this sabotage on three of its four fixtures."
SAB_COUNT=1
SAB_BEFORE='    sb_printf(v->b,
        "    {\n"
        "        const unsigned %s_call_frame = run->call_top;\n"
        "        if (%s_call_frame >= %s_RESUME_FRAMES) return %s_R_INTERNAL;\n"
        "        run->call_top = run->resume_stack[%s_call_frame].call_top;\n"
        "        goto *run->resume_stack[%s_call_frame].call_ret;\n"
        "    }\n",
        v->p, v->p, v->up, v->up, v->p, v->p);'
SAB_AFTER='    /* SABOTAGE S168: one shared macro instead of one inline return */
    sb_printf(v->b, "    %s_RETURN;\n", v->up);'
SAB_FILE2="src/gen/emit_vm.c"
SAB_COUNT2=1
SAB_BEFORE2='    /* The per-search reset (§2.4): slot_values is initialised to UNSET ONCE per
     * SEARCH call, not per start position.'
SAB_AFTER2='    if (v.has_calls)
        sb_printf(c,
            "#define %s_RETURN do {                                       \\\n"
            "        const unsigned %s_call_frame = run->call_top;        \\\n"
            "        if (%s_call_frame >= %s_RESUME_FRAMES) return %s_R_INTERNAL; \\\n"
            "        run->call_top = run->resume_stack[%s_call_frame].call_top;   \\\n"
            "        goto *run->resume_stack[%s_call_frame].call_ret;     \\\n"
            "    } while (0)\n\n",
            v.up, v.p, v.p, v.up, v.up, v.p, v.p);   /* SABOTAGE S168 */
    /* The per-search reset (§2.4): slot_values is initialised to UNSET ONCE per
     * SEARCH call, not per start position.'
