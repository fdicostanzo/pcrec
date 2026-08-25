# S179 (S-FB1) — [DD-14.FB] `<prefix>_search_in` BINDS THE STAMPED CAPACITY
# INSTEAD OF THE CALLER'"'"'S `nframes`.
#
# The single most likely way to build this feature and have it look finished:
# the descriptor arrives, the POINTER is taken from it, and the CAPACITY comes
# from the constant that was there before. Every pre-existing corpus cell still
# passes — they all run at the stamped default, where the two numbers are equal
# — and every structural check passes too, because the entry, the descriptor,
# the five macros and the delegation are all present and correct. What is gone
# is the FEATURE: a caller who reserves 128 MB gets 2048 frames.
#
# WHY IT NEEDED A CELL WRITTEN FOR IT. Nothing in this tree before [DD-14.FB]
# could see this row, because nothing called an entry with a capacity DIFFERENT
# from the stamped one. `tests/recursion/framebuffer.rxt`'"'"'s buffered cell is the
# detector by construction: n = 343 needs 686 frames and 3,081 trail entries,
# the block hands over 1024 and 8192, and under this row the artifact still
# stops where it stamped.
SAB_ID="S179-searchin-stamped-capacity"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness framebuffer codegen"
SAB_HARNESS_TARGET="tests/recursion/framebuffer.rxt"
SAB_DESC="the emitted <prefix>_search_in binds <PREFIX>_RESUME_FRAMES as its resume capacity instead of the caller's buffers->nframes. The pointer is still the caller's, so nothing faults and nothing is emitted differently -- the caller simply cannot raise the ceiling, which is the whole of what D71 item 2 asked for"
SAB_DOC_FIGURE="PREDICTED: framebuffer.rxt RED on the buffered cell that exceeds the stamped capacity; the NULL and default cells GREEN and codegen GREEN, because the surface is all present and only the number is wrong. Canonical figure owed from run_sabotage_matrix.sh S179."
SAB_COUNT=1
SAB_BEFORE='        "    %s_run_state_bind(&run, buffers->frames, buffers->nframes,\n"
        "                            buffers->trail,  buffers->ntrail);\n"
        "    return %s_run(subject, subject_length, search_from, capture_spans, &run);\n"
        "}\n\n",
        g.searchfn, v.p, v.p, v.p, v.up, v.up, g.searchfn,
        g.searchfn, v.p, v.p, g.searchfn, v.p, g.searchfn);'
SAB_AFTER='        "    %s_run_state_bind(&run, buffers->frames, %s_RESUME_FRAMES,\n"
        "                            buffers->trail,  buffers->ntrail);\n"
        "    return %s_run(subject, subject_length, search_from, capture_spans, &run);\n"
        "}\n\n",
        g.searchfn, v.p, v.p, v.p, v.up, v.up, g.searchfn,
        g.searchfn, v.p, v.p, g.searchfn, v.p, v.up, g.searchfn);   /* SABOTAGE S179 */'
