#!/usr/bin/env bash
# S516 ([MEMFN] R4a′, lane memfnstamp) -- ONE ARTIFACT FAMILY WITHOUT THE LINES.
#
# D81: a stamp is present on EVERY artifact of its family. The VM emitter
# stops writing the stamps' mark, and the finishing pass's "no single mark"
# internal error is disabled (site 2), so VM artifacts compile and ship with
# neither MEMFN line while DFA artifacts keep both. Detector: C11's presence
# check, arm memfnstamps. (Site 1 alone is caught louder still: the compile
# fails with the internal error, and the census's vm floor fires.)
# NOTE 2026-10-07 ([MEMFN] M1b, lane m1b): the mark now carries THREE kit
# lines (RUN_WORDS joined MEMFN_FORMS and MEMFN_LIBC); the plant's VM
# artifacts lose all three. The anchor is unchanged (the deleted
# pcrec_emit_runcmp_stamp call sat on the line above it). Intent unchanged.
SAB_ID="S516-c11-family-missing-stamps"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="memfnstamps"
SAB_DESC='VM artifacts lose both MEMFN stamp lines (the mark is not written and its absence is not refused); DFA artifacts keep them'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/memfnstamp_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S516.'
SAB_REACH='"$PCREC" -p rx -o - --pattern "a(b|c)+d" | grep -o -e "RX_ENGINE \"vm\"" -e "RX_MEMFN_FORMS"'
SAB_REACH_EXPECT='RX_ENGINE "vm"
RX_MEMFN_FORMS'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_emit_memfn_mark(&job->csb);'
SAB_AFTER='    /* SABOTAGE S516: the VM family writes no stamp mark */'
SAB_FILE2="src/gen/memfn_stamps.c"
SAB_COUNT2=1
SAB_BEFORE2='    if (!ok)
        pcrec_ctx_fail(cx, 0, "internal error: the artifact holds no single "'
SAB_AFTER2='    if (!ok && 0) /* SABOTAGE S516 */
        pcrec_ctx_fail(cx, 0, "internal error: the artifact holds no single "'
