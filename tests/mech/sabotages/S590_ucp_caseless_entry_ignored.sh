# S590 ([K94]) — THE EMITTER'S CASELESS-ENTRY CHOICE IGNORES UCP: the
# K94 fix reverted.
#
# Under `--ucp` the byte encoding reads bytes as Latin-1, and a caseless
# backreference must fold what the `--ucp` classes fold. `vm_caseless_entry`
# (src/gen/emit_vm.c) picks the seam's UCP caseless entry when UCP is in force
# at the construct and the encoding's table carries one. THIS ROW MAKES BOTH
# ARMS NAME THE PLAIN ENTRY, which is the pre-fix behaviour exactly: the
# artifact carries the ASCII-only compare and `(\xe9)\1` -i --ucp misses
# \xe9\xc9 where libpcre2 10.46 matches.
SAB_ID="S590-ucp-caseless-entry-ignored"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="brefdiff harness"
SAB_HARNESS_TARGET="tests/backrefs/caseless_ucp.rxt"
SAB_DESC="The VM emitter's caseless seam-entry choice ignores UCP, so a --ucp byte artifact carries the ASCII-only caseless span compare. A caseless backreference then misses Latin-1 case pairs (0xE9 vs 0xC9) that libpcre2 and pcrec's own --ucp classes fold"
SAB_DOC_FIGURE="PREDICTED: the caseless_ucp.rxt Latin-1 cells RED; brefdiff section 9c RED (no Latin-1 fold table in the --ucp artifact). Canonical figure owed from run_sabotage_matrix.sh S590."
SAB_COUNT=1
SAB_BEFORE="        ? PCREC_ENCE_SPAN_CASELESS_UCP : PCREC_ENCE_SPAN_CASELESS;"
SAB_AFTER="        ? PCREC_ENCE_SPAN_CASELESS : PCREC_ENCE_SPAN_CASELESS;   /* SABOTAGE S590 */"
