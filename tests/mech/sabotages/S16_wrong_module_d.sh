# S16 — \d's registry row is given the WRONG module name (classes -> misc).
# The parser renders its diagnostic FROM this same table, so a hand-written
# test that reads the same table cannot see this (tests/reject/CLAUDE.md's
# SR-4 table, row 1). Documented result: 2 hand-written reject checks fail,
# 0 iterated (the iterated loop reads the same wrong table and agrees with
# it — this IS the circularity SR-4 documents as unclosed).
#
# RETAGGED 2026-08-12 (MOD-0.8c slice 1) with `registry` and `pc3`, and here
# the interesting cell is the ZERO. Both suites' documentation states, in
# prose, that they cannot see this edit: tests/registry/CLAUDE.md — "the same
# wrong module name written into BOTH parse.c and registry.c passed 116/116
# here" — because the parser renders the diagnostic from the row the check
# reads, and "module names are pcrec's own taxonomy and no outside authority
# can check them", which is PC-3's stated limit too. Wiring the arms turns two
# prose claims into two measured cells that a future change would have to move
# on purpose. MEASURED 2026-08-12: registry_check 0fail/168pass and PC-3
# 0fail/154pass, exactly as both files predicted in prose.
#
# ONE THING THE PROSE DID NOT PREDICT, and the arm found it: the registry cell
# reads `+compliance-FAIL`, because compliance_section.py --check renders
# docs/pcre2_compliance.md's index FROM the table and the module name is in it.
# That is a DRIFT detector, not a control — tests/registry/CLAUDE.md says so
# and names the remedy its own failure message prints (`--write`), which
# regenerates the doc from the wrong table and turns it green. So the honest
# reading of this row is: three nets see the edit, and only tests/reject/'s
# hand-written literals (5 fail) would still fail after someone did what the
# other one tells them to do.
SAB_ID="S16-wrong-module-d"
SAB_FILE="src/parse/registry.c"
SAB_SUITES="reject registry pc3"
SAB_DESC="ESC('d', ...) module changed from 'classes' to 'misc' (wrong but plausible)"
SAB_DOC_FIGURE="tests/reject/CLAUDE.md: 2 hand-written fail, 0 iterated"
# [MECH-REACH, 2026-08-25] THIS ROW DECLARES ITS WITNESS'S REACH.
# THE WITNESS: the diagnostic NAMES THE MODULE, which is the exact field
# this row corrupts (`classes` -> `misc`). The probe is the same construct
# S15 uses and deliberately so -- both rows rest on `\d` still reaching the
# escape doorway as an unbuilt registry row, and when that stops being true
# BOTH go blind together, which is the fact worth being told once.
SAB_REACH='"$PCREC" --features none -p rx -o "$REACH_TMP/o0.c" -- "\\d"'
SAB_REACH_EXPECT="\\d requires module 'classes' (pattern offset 0)"
SAB_COUNT=1
# ANCHOR MOVED at [DD-11.1] (caught by scripts/m6read_check_sab_anchors.py on
# the same branch): see S15's identical note -- the `\d` row now goes
# through `ESC_SET_D` (one trailing `d_def` argument) rather than `ESC_SET`.
# The SABOTAGE is unchanged -- it still swaps the module name only.
SAB_BEFORE="ESC_SET_D('d', \"\\\\d\", classes, ANY_ENGINE, \"any decimal digit\", QF_YES, \"set 10\", pcrec_cls_digit_esc, 0, d_def),"
SAB_AFTER="ESC_SET_D('d', \"\\\\d\", misc, ANY_ENGINE, \"any decimal digit\", QF_YES, \"set 10\", pcrec_cls_digit_esc, 0, d_def),"
