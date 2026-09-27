# S304 — [OPT-LITSCAN] S2a THE LITERAL RUN IS ONE ELEMENT TOO LONG
# (src/core/cpset.c, `pcrec_lit_run`): wherever a run of two or more literal
# bytes has a spine element after it, the fact claims that element too, as a
# byte it is not (`lit_byte` of a non-literal is -1, stored as 0xFF).
#
# THE FACT IS THE ONE DEFINITION ALL THREE READERS ASK (patfacts design §8.2),
# so the plant moves emission, the cost walk and the slot walk together — the
# emitted compare is one byte longer than the literal and the element it
# swallowed (a capture, a choice point, a class) is never emitted at all.
# Nothing structural can disagree with itself here; what sees it is an ANSWER:
# every subject that holds the literal fails the compare on the 0xFF.
#
# ANSWER-DETECTABLE on tests/litscan/litrun.rxt, whose `xy(a|ab)c`,
# `a[bc]de`, `x(abc)defg` and `abc(?=def)` blocks each put a non-literal
# element right after a run; the harness runs every file on both engines and
# the VM side reads the compare.
SAB_ID="S304-lit-run-one-byte-too-long"
SAB_FILE="src/core/cpset.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/litrun.rxt"
SAB_DESC="pcrec_lit_run returns one more element than the run of literal bytes whenever the spine continues, so the VM compares the run plus a 0xFF byte and never emits the element it swallowed: every m case whose literal is followed by a capture, class, alternation or lookahead reads nomatch on the VM"
SAB_DOC_FIGURE="PREDICTED (lane s2a, 2026-09-27): DETECTED by the harness on tests/litscan/litrun.rxt (the m cells of the four blocks named in the header). MEASURED: see docs/dev/lanes/s2a_report.md. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S304."
# [MECH-REACH] the clean tree compares `xy` as one run in front of the group.
SAB_REACH='"$PCREC" --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern "xy(a|ab)c" && grep -qF "!memcmp(subject + scan_position, \"xy\", 2)" "$REACH_TMP/o.c" && echo REACH-LIT-RUN-EMITTED'
SAB_REACH_EXPECT="REACH-LIT-RUN-EMITTED"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (len < 2) return 0;'
SAB_AFTER='    if (len < 2) return 0;
    if (j + len < n) len++;   /* SABOTAGE S304: the run claims the next element */'
