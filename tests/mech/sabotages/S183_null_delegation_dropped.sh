# S183 (S-FB5) — [DD-14.FB] `<prefix>_search_in` NO LONGER SPECIAL-CASES A NULL
# DESCRIPTOR.
#
# Spec §10.3 defines `buf == NULL` to be EXACTLY a call to the un-suffixed
# entry — "not '"'"'similar to'"'"', not '"'"'equivalent in observable behaviour'"'"' — the same
# call". Drop the line that makes it one and the `_in` entry dereferences a null
# descriptor'"'"'s fields, or (as here) binds a null pointer at capacity 0 and gives
# up on the first push. Either way the whole compatibility story of §10.3 —
# "one call site and a runtime choice" — is gone.
#
# THE OTHER HALF OF THE DELEGATION IS CHECKED STRUCTURALLY, NOT HERE, and the
# two halves need different instruments. This row is the delegation being
# DROPPED, which changes answers and a cell can see. The delegation being
# REVERSED (`<prefix>_search` implemented as `<prefix>_search_in(..., NULL)`)
# changes NO answer at all — it costs the `_in` entry its small stack frame,
# because it would then own the default arrays and C cannot declare a local
# conditionally — so tests/codegen'"'"'s [DD-14.FB] block asserts the direction on
# the emitted text instead.
SAB_ID="S183-null-delegation-dropped"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness framebuffer codegen"
SAB_HARNESS_TARGET="tests/recursion/framebuffer.rxt"
SAB_DESC="the emitted <prefix>_search_in drops its NULL-descriptor delegation line, so a NULL descriptor binds a null resume stack at capacity 0 instead of meaning 'use the stamped default'. Spec 10.3 defines the NULL case to BE the un-suffixed call"
SAB_DOC_FIGURE="PRE-VALIDATED (2026-08-25): DETECTED, 12pass/4fail -- every frames-buffer=null cell in the file crashes (exit 139), across all THREE patterns including the DFA-selected one, which also shows the null route reaching that engine's inert _in entry. No default or buffered cell is affected. Canonical figure owed from run_sabotage_matrix.sh S183."
SAB_COUNT=1
SAB_BEFORE='        "    %s_run_state run;\n"
        "    if (!buffers) return %s(subject, subject_length, search_from, capture_spans);\n"
        "    %s_run_state_bind(&run, buffers->frames, buffers->nframes,\n"
        "                            buffers->trail,  buffers->ntrail);\n"
        "    return %s_run(subject, subject_length, search_from, capture_spans, &run);\n"
        "}\n\n",
        g.searchfn, v.p, v.p, v.p, v.up, v.up, g.searchfn,
        g.searchfn, v.p, v.p, g.searchfn, v.p, g.searchfn);'
SAB_AFTER='        "    %s_run_state run;\n"
        "    %s_run_state_bind(&run, buffers->frames, buffers->nframes,\n"
        "                            buffers->trail,  buffers->ntrail);\n"
        "    return %s_run(subject, subject_length, search_from, capture_spans, &run);\n"
        "}\n\n",
        g.searchfn, v.p, v.p, v.p, v.up, v.up, g.searchfn,
        g.searchfn, v.p, v.p, v.p, g.searchfn);   /* SABOTAGE S183 */'
