#!/usr/bin/env bash
# S685 ([MEMFN] M6, lane m6) -- THE LAZY LOOP'S VOCABULARY LINE LOST.
# RULED Q-R10-7: the VM cursor rung's lazy rmin prefix is listed `pending`
# (VMLAZY) with its own vocabulary line (span-count). The plant blinds the
# line: C17 rule 4 fires (a pending row whose emitter spells nothing).
# RETIRED 2026-10-09 (lane vmlazy, R-12 REPLACE, Q-R12-2/Q-R12-6): VMLAZY's
# row is DELETED (its instances are VMSPAN/VMSTRIDE's), so no pending row
# needs the span-count line: this row's population is gone and it is
# DECLARED UNREACHED. The line itself is KEPT at C12 ceiling 0 as a re-spell
# tripwire, whose own row is S709. The REACH_POP below asks for a VMLAZY
# pending row: the day one is listed again this row reads NOW REACHED and
# must be re-aimed (or a successor row written for the next pending site).
SAB_ID="S685-m6-span-count-vocab-lost"
SAB_FILE="tests/memfn/search_vocab.tsv"
SAB_SUITES="memfnmanifest"
SAB_DESC='the search vocabulary forgets the counted span loop (line span-count), so the pending VMLAZY row'"'"'s emitter (vm_cursor_rep, the lazy rmin prefix) spells no form C17 sees: the form escapes the static half'
SAB_DOC_FIGURE="HAND-MEASURED by lane m6 2026-10-08 (plant applied, tree rebuilt; docs/dev/lanes/m6_report.md section 6): memfnmanifest 1 failed / 12 passed (C17 rule 4: vm_cursor_rep, pending VMLAZY, spells no vocabulary form). The matrix figure is owed at the slot."
SAB_REACH='bash "$TREE/tests/memfn/run_site_manifest.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: rule 4: vm_cursor_rep (pending: VMLAZY) spells 1 form(s)'
SAB_REACH_POP='tests/memfn/site_manifest.tsv|^VMLAZY[[:space:]]+vm_cursor_rep[[:space:]].*[[:space:]]pending[[:space:]]|1'
SAB_EXPECT=UNREACHED
SAB_EXPECT_REASON='VMLAZY was deleted at R-12 REPLACE (lane vmlazy, Q-R12-2): no pending row is spelled through the span-count line any more, so blinding the line has no pending row to starve; the REACH_POP reads NOW REACHED if a VMLAZY pending row returns'
SAB_COUNT=1
SAB_BEFORE='span-compare	span-count	'
SAB_AFTER='span-compare	span-count-SABOTAGE-S685	^$NEVER'
