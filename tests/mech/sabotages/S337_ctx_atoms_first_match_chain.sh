# S337 ([UCP] U2) -- THE OLD FIRST-MATCH IF-CHAIN, RESTORED OVER OVERLAPPING SETS.
#
# THE CLAIM (ucp_design.md §2.4, r1 GEN-1): a byte's context is its ATOM, the
# vector of its memberships in EVERY set on the machine's context list, so
# two overlapping sets (V ⊂ W: a vowel lookbehind beside `\b`; a partial
# overlap: `(?<=[0-9a-f])x(?=[a-z_])`) partition the alphabet into all their
# intersections. The pre-U2 `upc_of_class` was a PRIORITY if-chain — the
# first set a byte was in won — which was exact only while the sets were
# disjoint.
#
# THE SABOTAGE makes the membership vector a first match: a byte gets the
# bit of the FIRST list entry it is in and no other, so V∩W collapses onto V.
# `(?<=[aeiou])x\b` on "axa" then reads the trailing `a` as "not a word
# character" and matches, where libpcre2 answers nomatch; the partial-overlap
# witness loses its `a-f` bytes' second bit the same way.
SAB_ID="S337-ctx-atoms-first-match-chain"
SAB_FILE="src/ir/dfa.c"
SAB_SUITES="ctxnode"
SAB_DESC="a byte's context atom takes only the FIRST context set it is in (the pre-U2 priority if-chain), so overlapping sets collapse V∩W onto one of them"
SAB_DOC_FIGURE="ctxnode arm: tests/ucp/ctxnode.rxt's overlap witnesses (\`(?<=[aeiou])x\\b\` on \"axa\"/\"axe\", \`(?<=[0-9a-f])x(?=[a-z_])\`) disagree with libpcre2. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S337."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o0.c" --pattern "(?<=[aeiou])x\\b" >/dev/null 2>&1 && grep -c "define RX_ENGINE \"dfa\"" "$REACH_TMP/o0.c"'
SAB_REACH_EXPECT="1"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (ctx_entry_live(d, k) && cls_has(d->ctx[k].bits, b)) v |= 1u << k;'
SAB_AFTER='        if (ctx_entry_live(d, k) && cls_has(d->ctx[k].bits, b)) return 1u << k;   /* SABOTAGE S337 */'
