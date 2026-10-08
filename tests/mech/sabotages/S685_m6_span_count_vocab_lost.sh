#!/usr/bin/env bash
# S685 ([MEMFN] M6, lane m6) -- THE LAZY LOOP'S VOCABULARY LINE LOST.
# RULED Q-R10-7: the VM cursor rung's lazy rmin prefix is listed `pending`
# (VMLAZY) with its own vocabulary line (span-count). The plant blinds the
# line: C17 rule 4 fires (a pending row whose emitter spells nothing).
SAB_ID="S685-m6-span-count-vocab-lost"
SAB_FILE="tests/memfn/search_vocab.tsv"
SAB_SUITES="memfnmanifest"
SAB_DESC='the search vocabulary forgets the counted span loop (line span-count), so the pending VMLAZY row'"'"'s emitter (vm_cursor_rep, the lazy rmin prefix) spells no form C17 sees: the form escapes the static half'
SAB_DOC_FIGURE="HAND-MEASURED by lane m6 2026-10-08 (plant applied, tree rebuilt; docs/dev/lanes/m6_report.md section 6): F685. The matrix figure is owed at the slot."
SAB_REACH='bash "$TREE/tests/memfn/run_site_manifest.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: rule 4: vm_cursor_rep (pending: VMLAZY) spells 1 form(s)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='span-compare	span-count	'
SAB_AFTER='span-compare	span-count-SABOTAGE-S685	^$NEVER'
