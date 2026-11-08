# S1882 ([RUN-POS-SET] stage 1, lane altbuild; docs/design/alt_normal_form.md
# §5 stage 1 S-i, re-picked by r7 SND-1 to a RIGHT slot) -- THE ISLAND'S SET
# READING ENUMERATES ONLY THE LOWEST MEMBER.
#
# The island reads a wide class as its code-point set, split canonically into
# boxes; the plant keeps only the first box, so `[éà]`'s words are `c3 a0`
# alone. `x(?:1[éà]|q2|r3)y` on the VM (island 1 in both builds) then fails
# `x1éy`, which libpcre2 matches (0,5). Answer witness:
# tests/utf8/altnf_lowering.rxt block 3 (`engine vm`).
# RE-ANCHORED 2026-11-06 (lane altfix, review r5 altcode SLOT-2): the box
# alternation is built by the shared `pcrec_spine_build` inside
# `vm_isl_set_split`; the plant still keeps the lowest box only.
SAB_ID="S1882-island-set-lowest-member"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/utf8/altnf_lowering.rxt"
SAB_DESC="the VM island's set reading of a wide class keeps only its first box, so an island over x(?:1[éà]|q2|r3)y has no word for é"
SAB_DOC_FIGURE="PREDICTED: tests/utf8/altnf_lowering.rxt red on block 3 (m x1\\xc3\\xa9y 0 5 fails)."
SAB_REACH='"$PCREC" -e utf8 -p rx --engine=vm -o - --pattern "x(?:1[éà]|q2|r3)y" | grep -o "RX_VM_ALT_ISLANDS 1"'
SAB_REACH_EXPECT='RX_VM_ALT_ISLANDS 1'
SAB_REACH_POP='tests/utf8/altnf_lowering.rxt|^pattern x\(\?:1\[éà\]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return pcrec_spine_build(v->cx, A_ALT, box, nb);'
SAB_AFTER='    return pcrec_spine_build(v->cx, A_ALT, box, 1);   /* SABOTAGE S1882: the lowest box only */'
