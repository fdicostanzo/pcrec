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
#
# RE-ANCHORED 2026-08-26 (lane srAnchor): [OPT-1]'"'"'s two-tier default entry
# (`vm_emit_default_entry`) rewrote the un-suffixed entries this same
# `sb_printf` call shares a format string with, which shrank the arg list
# threaded to the bind/return/close tail this row edits (the `_in` entry
# itself is unchanged in MEANING -- [OPT-1] never touches it). The BEFORE/AFTER
# text below is re-derived from `git show HEAD:src/gen/emit_vm.c` at the
# `_search_in` bind site (~line 9488) and is still unique at SAB_COUNT=1: its
# tail line (`return %s_run(subject, subject_length, ...)`) names arguments no
# other of the six `_in`/deep/fast bind sites shares.
SAB_ID="S179-searchin-stamped-capacity"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness framebuffer codegen"
SAB_HARNESS_TARGET="tests/recursion/framebuffer.rxt"
SAB_DESC="the emitted <prefix>_search_in binds <PREFIX>_RESUME_FRAMES as its resume capacity instead of the caller's buffers->nframes. The pointer is still the caller's, so nothing faults and nothing is emitted differently -- the caller simply cannot raise the ceiling, which is the whole of what D71 item 2 asked for"
SAB_DOC_FIGURE="PRE-VALIDATED (2026-08-25, sabotaged emitter vs tests/recursion/framebuffer.rxt): DETECTED, 15pass/1fail. The failing cell is line 61, the 512,400000 one -- and it is the ONLY cell in that file that sees this row. The 1024,8192 cell does NOT: pinning the resume capacity at the stamped 2048 gives that cell MORE frames than it asked for and it still matches. So the detector is the cell added to stop cell 3 being read as 'the trail is the only real capacity', which is a better argument for that cell than the one it was written with. RE-VALIDATED 2026-08-26 (lane srAnchor) after re-anchoring past [OPT-1]'s two-tier entry: run_sabotage_matrix.sh S179 -- DETECTED, corpus:1fail/15pass (the harness arm, unchanged 15pass/1fail signature), framebuf:3fail/3pass, codegen:0fail/105pass."
SAB_COUNT=1
SAB_BEFORE='        "    %s_run_state_bind(&run, buffers->frames, buffers->nframes,\n"
        "                            buffers->trail,  buffers->ntrail);\n"
        "    return %s_run(subject, subject_length, search_from, capture_spans, &run);\n"
        "}\n\n",
        g.searchfn, v.p, v.p, g.searchfn, v.p, g.searchfn);'
SAB_AFTER='        "    %s_run_state_bind(&run, buffers->frames, %s_RESUME_FRAMES,\n"
        "                            buffers->trail,  buffers->ntrail);\n"
        "    return %s_run(subject, subject_length, search_from, capture_spans, &run);\n"
        "}\n\n",
        g.searchfn, v.p, v.p, g.searchfn, v.p, v.up, g.searchfn);   /* SABOTAGE S179 */'
