# S282 — [OPT-LITSCAN] S1 THE DENY FIELD IS 32 BITS AGAIN (src/gen/emit_dfa.c,
# `DfaCand.deny`): litscan_s1.md R4's own defect, planted. `unsigned deny`
# truncates the run rows' `PCREC_NO_OFFSET_SKIP | PCREC_NO_RUN_PREFILTER`
# (bits 16 and 32) to bit 16, so `-fno-run-prefilter` parses, lands in the
# flags word and removes nothing. §7.1 row (i).
#
# ANSWER-INVISIBLE, which is the point: the denied build is answer-identical
# either way, so `make test-axes` cannot see a deny that does nothing. gcc's
# `-Woverflow` on the initializer is a WARNING only under the default build;
# the detector is structural.
SAB_ID="S282-deny-field-32bit"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks registry"
SAB_DESC="DfaCand.deny narrows back to unsigned, so the run-pinned rows' bit-32 deny (PCREC_NO_RUN_PREFILTER) is truncated away: -fno-run-prefilter removes nothing and router still stamps run-pinned under it"
SAB_DOC_FIGURE="MEASURED 2026-09-25 (lane s1build, single-row mech): DETECTED -- reach:ok(1/1), prechecks:2fail/287pass (§5.10: /user|/users and [ab]/user under -fno-run-prefilter still take the run row), registry:0fail/226pass (the registry arm is tests/registry/registry_check, which does not read --list-axes deny cells; axes_registry_check.sh is not a mech arm). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S282."
SAB_REACH='"$PCREC" --features all -p rx -fno-run-prefilter -o "$REACH_TMP/o.c" --pattern "/user|/users" && grep -q "^#define RX_DFA_PREFILTER \"memchr\"" "$REACH_TMP/o.c" && echo REACH-RUN-PREFILTER-DENY'
SAB_REACH_EXPECT="REACH-RUN-PREFILTER-DENY"
SAB_COUNT=1
SAB_BEFORE='    uint64_t    deny;         /* a set bit in cx->opt->flags REMOVES this entry */'
SAB_AFTER='    unsigned    deny;         /* SABOTAGE S282: 32 bits again */'
