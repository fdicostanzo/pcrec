# S1580 -- [M4-SUBST] lane substr1fix (review 2026-10-24-r1-subst-code TPL-1;
# docs/spec/subst_api.md §2¶5).
#
# Plant: an escape naming a code point above 0x7F binds no encoding.
# Witness: the `x1`-`x5` cells of tests/subst-extended/cells.tsv (`<\xe9>`, `<\o{351}>` ...
# compiled under utf8, used with a byte rx): the check must refuse them MISMATCH.
# Reach (K35): token S1580; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1580-escape-binds-no-encoding"
SAB_FILE="src/parse/subst_template.c"
SAB_SUITES="subst"
SAB_DESC='an escape naming a code point above 0x7F binds no encoding'
SAB_DOC_FIGURE='Owed: lane substr1fix queued this row (docs/dev/lanes/substland_report.md, substr1fix STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1580.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (v > 0x7F) ps->t->enc_bound = true;'
SAB_AFTER='    if (0) ps->t->enc_bound = true;   /* SABOTAGE S1580 */'
