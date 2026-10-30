# [VMREC] (a), lane vmrec, 2026-10-30: the record-first VM body's own rows
# (docs/dev/lanes/vmrec_report.md, "Structural checks and sabotages";
# design rev 3 mis-typing table, docs/dev/lanes/vmcons3_report.md).
#
# the ST row with no other net: no byte moves, no answer moves, tiling never fires; only the static one-writer scan reads it.
SAB_ID="S1849-vm-body-named-outside-writer"
SAB_FILE="src/gen/emit_comb.c"
SAB_SUITES="stmtwriter"
SAB_DESC='a second emitter names the VM body buffer (a read that writes nothing), so the body has a second module that can reach it'
SAB_DOC_FIGURE='lane vmrec 2026-10-30, probed by hand on a planted build: the scan names src/gen/emit_comb.c; the build and every answer unchanged by construction; scored by the owed vmrec-mech job'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='{
    return e == PCREC_ENTRY_SEARCH ? g->searchfn'
SAB_AFTER='{
    (void)sizeof(((Job *)0)->vmsb);   /* SABOTAGE S1849 */
    return e == PCREC_ENTRY_SEARCH ? g->searchfn'
