#!/usr/bin/env bash
# S1070 ([COMPOUND] E0c, lane e0c; docs/design/compound_entries.md §4.1, §5.1 E0c; docs/dev/lanes/e0c_report.md) -- the forward emitter's CALLER binding (the VM's `_in` entries) forwards to the un-suffixed sibling on EVERY descriptor, so the caller's storage is never bound.
SAB_ID='S1070-e0c-forward-caller-descriptor-ignored'
SAB_FILE='src/gen/emit_comb.c'
SAB_SUITES='harness framebuffer'
SAB_DESC='every VM <prefix>_*_in entry treats a non-NULL descriptor as NULL and runs on the stamped default storage; a caller cannot raise or lower the capacity (D71 item 2, spec §10.3)'
SAB_DOC_FIGURE='HAND-MEASURED by lane e0c 2026-10-16 (plant applied to a git-archive HEAD tree): corpus (tests/recursion/framebuffer.rxt) 1fail/15pass, framebuf 3fail/3pass. The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_HARNESS_TARGET='tests/recursion/framebuffer.rxt'
SAB_COUNT=1
SAB_BEFORE='        "    if (!buffers) return %s(%s%s);\n"'
SAB_AFTER='        "    if (buffers || !buffers) return %s(%s%s);   /* SABOTAGE S1070 */\n"'
