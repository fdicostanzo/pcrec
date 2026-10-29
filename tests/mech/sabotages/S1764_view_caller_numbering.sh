# S1764 ([INLINE-C] stage 3, inline_c.md S-IC32) -- THE DEFINITION-SITE
# VIEW USES THE CALLER'S NUMBERING: a site inside a composed definition
# reads the caller's group k where the definition's own group k belongs.
# Witness: tests/code/run_code_tests.sh arm 13's view run (group 1 'a' in
# a caller whose own group 1 is 'x').
SAB_ID="S1764-view-caller-numbering"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="code"
SAB_DESC="vm_callout fills the view from the caller's slots 2k/2k+1 instead of the definition's mapped groups"
SAB_REACH='printf '\''target t = u\n\npattern (x)(?&d)\nname u\nfeatures recursion,named-groups\n\npattern (a)(?C`c: return RX_PASS;`)\nname d\n'\'' > "$REACH_TMP/v.rxt"; "$PCREC" --allow-code=c -o "$REACH_TMP" "$REACH_TMP/v.rxt" && grep -c "_co_view\[1\]\[0\] = slot_values" "$REACH_TMP/t.c"'
SAB_REACH_EXPECT='1'
SAB_COUNT=1
SAB_BEFORE='                v->p, k, 2 * a->u.callout.view_map[k],
                v->p, k, 2 * a->u.callout.view_map[k] + 1);'
SAB_AFTER='                v->p, k, 2 * k,
                v->p, k, 2 * k + 1); /* SABOTAGE S1764 */'
