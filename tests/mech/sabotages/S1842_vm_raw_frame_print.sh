# [VMREC] (a), lane vmrec, 2026-10-30: the record-first VM body's own rows
# (docs/dev/lanes/vmrec_report.md, "Structural checks and sabotages";
# design rev 3 mis-typing table, docs/dev/lanes/vmcons3_report.md).
#
# M13, a raw csb print inside the matcher span: the frame's own row tiling (FR_ROW) fails every VM compile; the ST scan cannot see it (the artifact buffer is not the body), which is why the frame tiles itself.
SAB_ID="S1842-vm-raw-frame-print"
SAB_FILE="src/gen/vm_stmt.c"
SAB_SUITES="codegen"
SAB_DESC='pcrec_vm_stmt_frame writes a raw statement into the artifact between two of its frame rows'
SAB_DOC_FIGURE='lane vmrec 2026-10-30, probed by hand on a planted build: internal error on a(b|c)+d --engine=vm (the matcher'\''s span written outside its frame rows); scored by the owed vmrec-mech job'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    FR_ROW(&fw, pcrec_sb_printf(c, "    goto %s_L0;\n\n", p));'
SAB_AFTER='    pcrec_sb_puts(c, "    ;\n");   /* SABOTAGE S1842 */
    FR_ROW(&fw, pcrec_sb_printf(c, "    goto %s_L0;\n\n", p));'
