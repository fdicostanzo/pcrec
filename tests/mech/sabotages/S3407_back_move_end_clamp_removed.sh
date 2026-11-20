# S3407 (lane l3feat2, 2026-11-20; span_arms L3, docs/design/span_arms.md §14.4 L3 and §5.7) --
# W-L16 (review r51 READYL3-4, a SAFETY witness): the K < 0 move's end clamp is removed. The kit
# verifies only a stretch of the run (`Content-` here, inside the 16-byte lookbehind), so on a subject
# that ends inside the lookbehind the hit plus 16 passes the subject's end and the attempt starts there.
# Detector: tests/litscan/spanarms.rxt (the L3 blocks, both routes).
SAB_ID="S3407-back-move-end-clamp-removed"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='the K < 0 move loses its end clamp, so a hit whose run ends past the subject moves the start beyond the subject'\''s end'
SAB_DOC_FIGURE="MEASURED UNDETECTED at landing (lane l3feat2, 2026-11-20; spanarms.rxt 0 of 2130 cells red): the clamp is defence in depth today. On the VM route the run finder verifies the whole run, so hit + 16 never passes the end; on the default route the kit verifies only Content- but the start-byte prefilter the moved position is handed to begins with if (search_from > subject_length) return 0, so the moved start answers NOMATCH there too, and no byte past the subject is read (so asan has nothing to see either). The row stays as a planted record of that redundancy: a later consumer of the moved position that lacks such a guard turns it DETECTED, and the matrix reports NOW DETECTED."
SAB_REACH='"$PCREC" --features all -p rx --engine=vm -o "$REACH_TMP/o.c" --pattern '\''(?<=Content-Length: )\d'\'' && grep -q '\''^#define RX_REQ_HANDOFF "-16"$'\'' "$REACH_TMP/o.c" && echo REACH-WL16'
SAB_REACH_EXPECT='REACH-WL16'
SAB_EXPECT=UNDETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_printf(c, "%sif (%s - %s < %lld) " REQ_ON_MISS "\n", ind, len, hit, -k);'
SAB_AFTER='        (void)len;   /* SABOTAGE S3407: the end clamp removed */'
