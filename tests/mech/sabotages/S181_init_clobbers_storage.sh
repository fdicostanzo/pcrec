# S181 (S-FB3) — [DD-14.FB] `<prefix>_run_state_init` RE-ZEROES THE STORAGE
# FIELDS IT WAS TOLD NOT TO TOUCH.
#
# §11 item 4 of docs/design/frame_buffer_design.md names this as the mistake the
# initialiser'"'"'s own shape invites: it writes every field it knows about, and
# after this wave there are four fields it must NOT write, because
# `<prefix>_run_state_bind` has already pointed them at storage and runs BEFORE
# it. The design calls it "§5.6 site 5a'"'"'s exact failure mode one field further
# along" — the same class as the missing `call_top` initialiser [DD-14] wave B+C
# found, in the opposite direction.
#
# IT BREAKS THE DEFAULT PATH TOO, and that is worth saying rather than treating
# as a stronger result: the un-suffixed entries bind their own
# `<prefix>_run_buffers` through the SAME function, so this row is not subtle
# and every VM cell in the tree goes red. Its value is not that it is hard to
# catch; it is that the ORDER (bind, then init, and init keeps its hands off) is
# a real constraint with a real detector, written down where someone editing the
# initialiser will meet it.
SAB_ID="S181-init-clobbers-storage"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness framebuffer stackdepth codegen"
SAB_HARNESS_TARGET="tests/recursion/framebuffer.rxt"
SAB_DESC="<prefix>_run_state_init zeroes run->resume_stack and run->resume_cap after <prefix>_run_state_bind has set them. Every VM match then runs with a NULL resume stack of capacity 0, so the first push gives up -- through the caller's buffers AND through the artifact's own default storage, which the un-suffixed entries bind the same way"
SAB_DOC_FIGURE="PRE-VALIDATED (2026-08-25): DETECTED, 8pass/8fail -- every VM cell in framebuffer.rxt, through both the default and the buffered entries, since the un-suffixed entries bind their own storage the same way. The 8 that pass are the DFA-selected block, whose engine has no run state. Canonical figure owed from run_sabotage_matrix.sh S181."
SAB_COUNT=1
SAB_BEFORE='        "    run->resume_depth = 0; run->trail_depth = 0;\n",'
SAB_AFTER='        "    run->resume_depth = 0; run->trail_depth = 0;\n"
        "    run->resume_stack = 0; run->resume_cap = 0;   /* SABOTAGE S181 */\n",'
