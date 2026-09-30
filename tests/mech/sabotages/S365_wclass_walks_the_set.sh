# S365 ([CLS-TREE] S3, lane s3build) -- A READER WALKS THE WIDE CLASS'S SET
# INSTEAD OF ITS BYTE CHILD.
#
# S3's one hazard with a wrong ANSWER (r54 E1, docs/dev/cls_s3_reader_
# inventory.md §4): a reader that adds `case A_WCLASS:` to the label list of
# its `A_CLASS` arm compiles, and hands the node to `pcrec_cls_bits`, which
# renders `u.cls`. The set lives in the distinct `u.wcls`, but a union member
# at the same offset reads back the same interval list, and a set confined to
# U+0080..U+00FF (`é`) renders as a VALID 32-byte bitmap of the wrong bytes
# (0xE9 is not a byte of `é`'s encoding). No range check can see that.
#
# The plant is `vm_emit_node`'s own arm, the forward emission: the shared
# label list the inventory's SEM-1 names. It must FAIL LOUDLY, and it does,
# through the kind guard `pcrec_cls_bits` gained at S3 -- W4's witness
# `x[é]y` (-e utf8, --engine=vm) refuses with "pcrec_cls_bits was handed a
# wide class". The witness is a spine ITEM on purpose: at a spine head the
# see-through hands the flattener the child and `vm_emit` never meets the
# wrapper, so `[é]x` is NOT a witness for this row (measured).
#
# MEASURED 2026-09-29 without the guard as well, to know what the guard buys:
# plant + `cls_kind_guard` deleted -> `x[é]y` COMPILES and answers nomatch on
# "x\xc3\xa9y" where the clean artifact answers (0,4). A silent miscompile;
# the guard is the whole difference between that and this row's refusal.
#
# RE-ANCHORED at [CLS-TREE] S4 (lane s4build, 2026-09-29): the arm now asks
# `vm_wcls_bytes` first and only its BYTE route walks the child (a
# multi-member wide class takes one decode + kit test). The plant keeps the
# row's claim on that route: it hands the node to `pcrec_cls_bits` -- the SET
# -- before emitting. `x[é]y` is a one-member class, so it is on the byte
# route and still W4's witness; the kind guard refuses it.
SAB_ID="S365-wclass-walks-the-set"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="wclass"
SAB_DESC="vm_emit_node's A_WCLASS arm shares A_CLASS's label list, so the forward walk renders the wide class's code-point SET through pcrec_cls_bits instead of emitting its byte child"
SAB_DOC_FIGURE="RE-MEASURED solo 2026-09-30 at the s4build tip (re-anchored): wclass:3fail/14pass DETECTED. MEASURED solo-plant 2026-09-29 at the S3 tip: wclass:2fail/8pass DETECTED -- [5b] (the census's shared-arm rule) and [W4] (x[é]y refuses by the kind guard); W1-W3 stay green, because their wrappers sit at spine heads the see-through already handles."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    case A_WCLASS: {
        if (vm_wcls_bytes(v->cx, a)) {
            vm_emit_node(v, entry, a->l, next);
            return;
        }'
SAB_AFTER='    case A_WCLASS: {
        if (vm_wcls_bytes(v->cx, a)) {
            uint8_t sab_bits[32];
            pcrec_cls_bits(v->cx, a, sab_bits);
            vm_emit_node(v, entry, a->l, next);
            return;
        }'
