# S182 (S-FB4) — [DD-14.FB] ONE OF THE SEVEN CAPACITY SITES STILL READS THE
# STAMPED MACRO.
#
# §11 item 3 enumerates SEVEN sites that test a depth against a capacity — the
# region-exit `_R_INTERNAL` guard, the `RX_TRAIL`/`RX_PUSH` pair, their two
# tracing twins, and the two `RX_CALL` variants — and this row is why the list
# is enumerated rather than described. Convert six and leave one, and the
# artifact is correct for every caller who uses the default (where the field and
# the macro hold the same number) and wrong for exactly the callers this feature
# exists for.
#
# THE SITE CHOSEN IS THE TRAIL GUARD, deliberately. It is the array design §4
# MEASURES as the one that BINDS first — 8.982 trail entries per nesting level
# against 2.000 frames — so a caller who raised both capacities and got a
# give-up anyway would have no way to tell this row from "the pattern is just
# too deep". tests/recursion/framebuffer.rxt's 1024,8192 cell needs 3,081 trail
# entries and the artifact stamps 3,072: nine short, and a match becomes a
# give-up.
#
# NOTE THAT IT DOES NOT OVER-RUN ANYTHING. Leaving the guard on the stamped
# macro makes the artifact REFUSE early, not write past the end — this direction
# is the safe one. The dangerous direction is the same defect on an artifact
# whose stamped capacity is LARGER than the caller's buffer, which is what
# tests/codegen's [DD-14.FB] structural check covers by asserting that NO guard
# compares against the stamped constant at all.
#
# TWO EDITS, ONE ROW: the format string and its argument list. The macro name
# needs a `%s`, so the site cannot be sabotaged without also feeding the extra
# `v.up` — which is itself a small demonstration of why the seven sites are
# easy to leave half-converted.
SAB_ID="S182-trail-guard-keeps-stamped-macro"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness framebuffer codegen"
SAB_HARNESS_TARGET="tests/recursion/framebuffer.rxt"
SAB_DESC="the untraced RX_TRAIL guard compares run->trail_depth against the stamped <PREFIX>_TRAIL_FRAMES instead of run->trail_cap -- one of the seven capacity sites left unconverted. Identical behaviour for every caller at the default capacity; a caller-supplied trail larger than the stamped one is unreachable past the stamped number"
SAB_DOC_FIGURE="PREDICTED: framebuffer.rxt RED on the 1024,8192 cell (3,081 trail entries needed against a stamped 3,072, so a match becomes a give-up) and framebuffer RED on the mmap ceiling; the default, NULL and 200000,3072 cells GREEN. codegen RED on the [DD-14.FB] no-stale-guard check. Canonical figure owed from run_sabotage_matrix.sh S182."
SAB_COUNT=1
SAB_BEFORE='            "        if (run->trail_depth >= run->trail_cap) return %s_R_FRAMES;    \\\n"
            "        run->trail[run->trail_depth].slot_index = (unsigned)(slot_);               \\\n"
            "        run->trail[run->trail_depth].saved_value = slot_values[(slot_)];                       \\\n"
            "        run->trail_depth++;                                             \\\n"
            "    } while (0)\n"
            "#define %s_SET(slot_, v_) do {                                \\\n"
            "        %s_TRAIL(slot_); slot_values[(slot_)] = (v_);                 \\\n"'
SAB_AFTER='            "        if (run->trail_depth >= %s_TRAIL_FRAMES) return %s_R_FRAMES;    \\\n"
            "        run->trail[run->trail_depth].slot_index = (unsigned)(slot_);               \\\n"
            "        run->trail[run->trail_depth].saved_value = slot_values[(slot_)];                       \\\n"
            "        run->trail_depth++;                                             \\\n"
            "    } while (0)\n"
            "#define %s_SET(slot_, v_) do {                                \\\n"
            "        %s_TRAIL(slot_); slot_values[(slot_)] = (v_);                 \\\n"'
SAB_FILE2="src/gen/emit_vm.c"
SAB_COUNT2=1
SAB_BEFORE2='            v.up, v.up, v.up, v.up, v.up, v.up,
            v.has_linked_calls ? "        run->resume_stack[run->resume_depth]"'
SAB_AFTER2='            v.up, v.up, v.up, v.up, v.up, v.up, v.up,   /* SABOTAGE S182 */
            v.has_linked_calls ? "        run->resume_stack[run->resume_depth]"'
