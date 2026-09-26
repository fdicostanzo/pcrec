# S281 — [OPT-LITSCAN] S1 CLAUSE 4 DROPPED (src/gen/emit_dfa.c,
# `pf_run_applies_common`): the run rows no longer decline an artifact whose
# model selection ALREADY verifies the whole run (class A), so keyword
# `in|instanceof` takes `run-pinned` instead of keeping `offset-set`.
# litscan_s1.md §7.1 row (h).
#
# ANSWER-INVISIBLE: the run row's test is sound on class A too, so no cell
# moves; the plant changes which form a whole class stamps, and that is
# exactly the population the design ruled stays on offset-set. The detector
# is structural.
SAB_ID="S281-run-row-clause4-dropped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks"
SAB_DESC="the run-pinned rows' clause 4 is dropped, so class A artifacts (whose offset-set selection already verifies the pinned run) move to run-pinned: keyword in|instanceof stamps run-pinned / 0,1* instead of offset-set / 0,1*"
SAB_DOC_FIGURE="MEASURED 2026-09-25 (lane s1build, single-row mech): DETECTED -- reach:ok(1/1), prechecks:1fail/288pass (§5.10: in|instanceof stamps run-pinned where offset-set / 0,1* / dominated is expected). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S281."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "in|instanceof" && grep -q "^#define RX_DFA_PREFILTER \"offset-set\"" "$REACH_TMP/o.c" && grep -q "^#define RX_REQ_WHY \"dominated\"" "$REACH_TMP/o.c" && echo REACH-CLASS-A-KEYWORD'
SAB_REACH_EXPECT="REACH-CLASS-A-KEYWORD"
SAB_COUNT=1
SAB_BEFORE='        if (ofs_test_verifies_run(s->cx, &t, o)) return false;'
SAB_AFTER='        if (0 && ofs_test_verifies_run(s->cx, &t, o)) return false;   /* SABOTAGE S281 */'
