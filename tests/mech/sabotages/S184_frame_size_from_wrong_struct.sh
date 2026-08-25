# S184 (S-FB6) — [DD-14.FB] `<PREFIX>_RESUME_FRAME_SIZE` IS STAMPED FROM THE
# TRAIL ENTRY'"'"'S LAYOUT.
#
# The sizing macros are STAMPED LITERALS rather than `sizeof` expressions, and
# they have to be: design §5.4 keeps the two structs `.c`-private, so a `sizeof`
# in the header would name a type the header does not declare. A stamped literal
# is a number that can be wrong, and this row is it being wrong in the way that
# does the most damage — 16 where the truth is 40, so a caller who divides its
# reservation by the macro over-counts the capacity by 2.5x and hands the
# matcher a buffer two and a half times smaller than it was told it was.
#
# WHAT CATCHES IT, AND WHERE. The design'"'"'s own §11 table proposes an ASan cell
# that allocates `N * RX_RESUME_FRAME_SIZE` bytes and runs to the ceiling. That
# would work, and it is the second line of defence. The FIRST is that the
# artifact reconciles the two sources itself: `_Static_assert(sizeof(<prefix>_frame)
# == <PREFIX>_RESUME_FRAME_SIZE, ...)` sits beside the struct definitions, so
# this row does not produce a subtly under-allocated buffer at run time — it
# produces a GENERATED FILE THAT DOES NOT COMPILE, with a message naming the
# macro. That is the same discipline as every other "two sources that could
# disagree" site in this tree, and it converts a caller-side heap overrun into a
# build failure.
#
# So the expected signature is unusually broad: every suite that COMPILES a VM
# artifact goes red, including the corpus, and it goes red at the C compiler
# rather than at an assertion.
SAB_ID="S184-frame-size-from-wrong-struct"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness framebuffer codegen"
SAB_HARNESS_TARGET="tests/recursion/framebuffer.rxt"
SAB_DESC="the emitted <PREFIX>_RESUME_FRAME_SIZE is computed from the TRAIL entry's member list instead of the resume frame's, stamping 16 where the truth is 40. A caller sizing a reservation from the macro would over-count its capacity by 2.5x; the artifact's own _Static_assert turns that into a compile error instead"
SAB_DOC_FIGURE="PRE-VALIDATED (2026-08-25): DETECTED, 0pass/16fail -- the whole file, at the GENERATED-CODE COMPILE, with the _Static_assert naming RX_RESUME_FRAME_SIZE. Not one under-allocated buffer at run time: the artifact refuses to build. Canonical figure owed from run_sabotage_matrix.sh S184."
SAB_COUNT=1
SAB_BEFORE='        bufs.resume_frame_size = vm_layout(frame_fields, nframe_fields, &fa);
        bufs.trail_frame_size  = vm_layout(trail_fields, ntrail_fields, &ta);'
SAB_AFTER='        bufs.resume_frame_size = vm_layout(trail_fields, ntrail_fields, &fa);
        bufs.trail_frame_size  = vm_layout(trail_fields, ntrail_fields, &ta);   /* SABOTAGE S184 */'
