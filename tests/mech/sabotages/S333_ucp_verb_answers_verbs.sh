# S333 ([UCP] U0) -- `(*UCP)` ANSWERS MODULE `verbs` AGAIN.
#
# THE CLAIM (ucp_design.md §1.2, D130 Q2; O-71): `(*UCP)` is owned by module
# `ucp`, and before U0 it answered "requires module 'verbs'" -- a module
# `--features all` cannot satisfy, i.e. the wrong OWNER, which is D26's exact
# tier. The fix is a name row the `(*` doorway resolves by NAME
# (mod_verbs.c's `pcrec_registry_verb_name_row`, the alpha-lookaround rows'
# own mechanism).
#
# THE SABOTAGE renames the row's NAME (`tail`), the minimal edit that breaks
# the resolution without touching the row's other facts: the lookup misses,
# the doorway's own catch-all answers, and the diagnostic names `verbs` again.
# Every row that still parses is unchanged, which is what makes it silent to
# every answer check -- only a pin on the MODULE NAME can see it.
SAB_ID="S333-ucp-verb-answers-verbs"
SAB_FILE="src/parse/registry.c"
SAB_SUITES="reject"
SAB_DESC="the (*UCP) name row's tail no longer matches, so (*UCP) resolves to the (* catch-all and answers \"requires module 'verbs'\" again"
SAB_DOC_FIGURE="reject: the (*UCP) rows expecting module 'ucp' fail (red). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S333."
SAB_REACH='"$PCREC" --features none -p rx -o "$REACH_TMP/o0.c" --pattern "(*UCP)a" 2>&1'
SAB_REACH_EXPECT="requires module 'ucp'"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='{RK_VERB, REG_SEL_ANY, "UCP", "(*UCP)a", M_ucp, FLAV_PCRE2, ANY_ENGINE,'
SAB_AFTER='{RK_VERB, REG_SEL_ANY, "UCPX", "(*UCP)a", M_ucp, FLAV_PCRE2, ANY_ENGINE, /* SABOTAGE S333 */'
