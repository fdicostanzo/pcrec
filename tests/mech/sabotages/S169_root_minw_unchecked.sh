# S169 ([DD-14.EMPTY], wave E; design SS4.4b + SS12 P-12) -- THE ROOT
# MINIMUM-WIDTH CHECK AT THE SEARCH ENTRY.
#
# THE CLAIM. When the whole pattern's `pcrec_minw` is at the analysis ceiling,
# `<prefix>_search` answers NOMATCH before pushing a single frame. P-12 rules
# that SS4.4b's Kleene-from-infinity fixpoint REACHING infinity is a LEGAL
# COMPILE meaning the language is EMPTY, and this is the one site that honours
# that ruling for every shape rather than for the shapes that happen to carry
# a quantifier.
#
# WHAT IT REPLACED, WHICH IS WHY THE ROW'S SIGNATURE IS A SPLIT ONE. Before
# wave E the ruling was honoured only where an MRL clamp got EMITTED, and a
# clamp is emitted at a QUANTIFIER. So `^(a?(?1)b)$` answered NOMATCH in O(1)
# because of its `a?`, while `^((?1)a)$` and the indirect p/q cycle -- the same
# empty language, the same infinite root minw -- held no quantifier at all and
# RAN UNTIL THE FRAME BUFFER GAVE UP. Under this sabotage exactly TWO of
# leftrec.rxt's three empty-language cells go red and the third stays green,
# because the third is the one that never needed this site. A row that took
# all three down would be sabotaging the MRL machinery, not this check.
#
# MEASURED, and the measurement is where the mechanism's SITE came from.
# `pcrec_minw` reads a call's contribution off `u.call.minw`, which
# `pcrec_callgraph_build` fills; that pass runs AFTER `pcrec_select_engine`.
# Asked at engine selection the three siblings answer 1, 1 and 0 -- the arena's
# zero, sound but useless, and a root check placed there can never fire. Asked
# in the emitter they answer PCREC_MINW_MAX (2^40) on all three. The plan row
# [DD-14.EMPTY] named engine selection as the site and was WRONG about it.
#
# WHY THE EMITTED CODE IS A WIDTH COMPARISON AND NOT `return 0`. The ceiling is
# reached by two routes -- the fixpoint's genuine infinity and `mrl_sat_*`
# SATURATION on a merely enormous minimum -- and the value cannot tell them
# apart. `if (remaining < ROOT_MINW) return 0;` is exactly right on both; an
# unconditional return would be a miscompile on the second for a subject of
# 2^40 bytes, which `size_t` can represent. Sabotaging the emission (rather
# than the comparison) is therefore the honest cut: it removes the SITE, which
# is what the row is about.
SAB_ID="S169-root-minw-unchecked"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion/leftrec.rxt"
SAB_EXPECT=DETECTED
SAB_DESC="the search entry stops emitting the ROOT minimum-width check, so an empty-language pattern with no quantifier to carry an MRL clamp runs until the resume-frame buffer gives up instead of answering NOMATCH"
SAB_DOC_FIGURE="PREDICTED: leftrec.rxt's DIRECT cell (^((?1)a)\$ on \"a\") and its INDIRECT cell (the p/q two-node cycle on \"ab\") revert from a ruled NOMATCH to PCREC_ERR_FRAMES -- their wave-B+C expectation, which wave E replaced. The NULLABLE-PREFIX cell (^(a?(?1)b)\$ on \"ab\") stays GREEN under the same sabotage, because its \`a?\` emits an MRL clamp and it never depended on this site. TWO RED, ONE GREEN is the signature; three red means the MRL machinery was cut instead. MEASURED on the landed build: all three roots report pcrec_minw = 1099511627776 (PCREC_MINW_MAX) once pcrec_callgraph_build has run, and exactly four of the corpus's 2,568 distinct patterns reach that ceiling -- all four call-bearing."
SAB_COUNT=1
SAB_BEFORE='     * them is call-bearing, so no call-free artifact gains a byte. */
    if (root_minw >= PCREC_MINW_MAX)'
SAB_AFTER='     * them is call-bearing, so no call-free artifact gains a byte. */
    if (0) /* SABOTAGE S169: the root minw check is never emitted */'
