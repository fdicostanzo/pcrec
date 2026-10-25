# S1583 -- [M4-SUBST] lane substr1fix (review 2026-10-24 r1 subst, HOUSE-1;
# docs/spec/subst_api.md §2¶2).
#
# Plant: the shared group-name rule takes a non-ASCII digit (\p{Nd}) in the
# LEADING position, on both sides at once (pcrec_group_name_cp is the one rule).
# Witness: run_subst_tests.sh's one-grammar loop (U+0663 first: libpcre2
# refuses `(?<NAME>x)`, so both the pattern and the template must refuse).
SAB_ID="S1583-group-name-digit-first"
SAB_FILE="src/parse/mod_named_groups.c"
SAB_SUITES="subst"
SAB_DESC='the group-name rule takes a non-ASCII digit first'
SAB_DOC_FIGURE='Owed: lane substr1fix queued this row (docs/dev/lanes/substland_report.md, substr1fix STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1583.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return r != 0 || first ? r : ng_in_prop("ND", cp);'
SAB_AFTER='    return r != 0 ? r : ng_in_prop("ND", cp);   /* SABOTAGE S1583 */'
