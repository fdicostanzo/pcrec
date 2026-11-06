# S1883 ([RUN-POS-SET] stage 1, lane altbuild; docs/design/alt_normal_form.md
# §5 stage 1 S-i2, re-picked by r7 SND-1 to a RIGHT slot) -- THE ISLAND'S
# ADMISSION PREDICATE ON THE SET IS DROPPED.
#
# Today's admission, stated on the set: a wide class is an island source iff
# every box of its canonical split is a single string. The plant splits the
# set member by member instead, which admits a class whose canonical split
# holds a byte RANGE (`[éè]`, one box `c3 [a8-a9]`). Enumerating a range's
# members is SOUND, so no answer can move: a COUNT witness.
# `x(?:1[éè]|q2|r3)y` stamps RX_VM_ALT_ISLANDS 0 in the correct build and 1
# under the plant (tests/codegen/run_wclass_census.sh [N1]).
SAB_ID="S1883-island-set-admission-dropped"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="wclass"
SAB_DESC="the VM island splits a wide class member by member instead of by its canonical boxes, so a class whose split holds a byte range gains an island today's admission declines (answers unchanged; the island census moves)"
SAB_DOC_FIGURE="PREDICTED: wclass:1fail -- [N1] x(?:1[éè]|q2|r3)y reads RX_VM_ALT_ISLANDS 1 where 0."
SAB_REACH='"$PCREC" -e utf8 -p rx --engine=vm -fno-cls-kit -o - --pattern "x(?:1[éè]|q2|r3)y" | grep -o "RX_VM_ALT_ISLANDS 0"'
SAB_REACH_EXPECT='RX_VM_ALT_ISLANDS 0'
SAB_REACH_POP='tests/codegen/run_wclass_census.sh|\[N1\]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        Ast **box = pcrec_lower_boxes(v->cx, iv, n, &nb);'
SAB_AFTER='        Ast **box = pcrec_arena_alloc(&v->cx->arena, (size_t)(VM_ISL_MAX_WORDS + 2) * sizeof *box);
        nb = 0;   /* SABOTAGE S1883: one box per member, the admission dropped */
        for (int i = 0; i < n && nb <= VM_ISL_MAX_WORDS; i++)
            for (unsigned c = iv[i].lo; c <= iv[i].hi && nb <= VM_ISL_MAX_WORDS; c++) {
                PcrecCpRange r = { c, c };
                int k;
                box[nb++] = pcrec_lower_boxes(v->cx, &r, 1, &k)[0];
            }'
