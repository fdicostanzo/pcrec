# S422 — [PF-DROP] (D135) THE RUNG FIRES AND THE ARTIFACT DOES NOT SAY WHY.
#
# `<PREFIX>_VM_PREFILTER_WHY` (src/gen/emit_vm.c) is the one stamp that
# tells a prefilter the size-cap ladder dropped from one the caller denied
# with `-fno-prefilter`: both read `RX_VM_PREFILTER "none"`. Skip it and the
# rescued artifact still compiles, still answers, still reads
# `RX_ENGINE_SEL "size-cap-retry"` — and names no rung, D81's `_WHY`
# convention broken on exactly the artifact it exists for.
#
# WHAT SEES IT: the resource section's [PF-DROP] WHY cell, and its
# identity cell (the rescued artifact must be -fno-prefilter's PLUS this
# line; without it the two are equal but for RX_ENGINE_SEL, which the
# identity cell tolerates — so the WHY cell is the one that goes red), and
# run_prefilter_collapse.sh's K41 control.
SAB_ID="S422-prefilter-drop-unstamped"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="resource pfcollapse"
SAB_DESC="the VM emitter never writes <PREFIX>_VM_PREFILTER_WHY, so an artifact whose prefilter the size-cap ladder dropped is indistinguishable, stamp for stamp, from a caller's own -fno-prefilter but for RX_ENGINE_SEL"
SAB_DOC_FIGURE="PREDICTED (lane pfdrop, 2026-09-30): resource [PF-DROP] WHY cell red; pfcollapse K41 -fno-prefilter-collapse control red. docs/spec/match_api.md §6.3's <PREFIX>_VM_PREFILTER_WHY"
SAB_COUNT=1
SAB_REACH='"$PCREC" -e utf8 -p rx -o - --pattern "(\p{Xwd})" 2>/dev/null | grep -o "VM_PREFILTER_WHY" | head -1'
SAB_REACH_EXPECT='VM_PREFILTER_WHY'
SAB_BEFORE='    if (cx->size_drop_rung == SDR_NO_PREFILTER)
        pcrec_sb_stampf(c, v->up, "VM_PREFILTER_WHY",'
SAB_AFTER='    if (cx->size_drop_rung == SDR_NO_PREFILTER && 0)   /* SABOTAGE S422 */
        pcrec_sb_stampf(c, v->up, "VM_PREFILTER_WHY",'
