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
# ANSWER-DETECTABLE on tests/litscan/litrun.rxt, whose `xyz(a|ab)c`,
# `a[bc]de`, `x(abc)defg` and `abc(?=def)` blocks each put a non-literal
# element right after a run; the harness runs every file on both engines and
# the VM side reads the compare.
#
# [OPT-LITSCAN F5, D127, 2026-09-28] RE-ANCHORED: the floor moved from two
# bytes to three (`src/core/cpset.c`), and this row's own witness,
# `xy(a|ab)c`, is now BELOW it -- its "xy" run no longer takes the compare
# form at all, so the plant would have nothing to lengthen. Widened to
# `xyz(a|ab)c` (the same shape run_ir_listing.sh's S305 witness widened to,
# for the identical reason); SAB_BEFORE/SAB_AFTER follow the floor's own new
# line. Intent unchanged: the run still claims one element too many.
SAB_ID="S304-lit-run-one-byte-too-long"
SAB_FILE="src/core/cpset.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/litrun.rxt"
SAB_DESC="pcrec_lit_run returns one more element than the run of literal bytes whenever the spine continues, so the VM compares the run plus a 0xFF byte and never emits the element it swallowed: every m case whose literal is followed by a capture, class, alternation or lookahead reads nomatch on the VM"
SAB_DOC_FIGURE="PREDICTED (lane s2a, 2026-09-27): DETECTED by the harness on tests/litscan/litrun.rxt (the m cells of the four blocks named in the header). MEASURED 2026-09-27 (lane s2a, single-row mech at b04e7ab3): DETECTED -- reach:ok(1/1), corpus:4fail/83pass on tests/litscan/litrun.rxt. RE-ANCHORED 2026-09-28 (lane litf5, [OPT-LITSCAN] F5/D127): witness widened xy(a|ab)c -> xyz(a|ab)c, anchor follows the len<3 floor; re-run owed at merge. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S304."
# [MECH-REACH] the clean tree compares `xyz` as one run in front of the group.
SAB_REACH='"$PCREC" --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern "xyz(a|ab)c" && grep -qF "!memcmp(subject + scan_position, \"xyz\", 3)" "$REACH_TMP/o.c" && echo REACH-LIT-RUN-EMITTED'
SAB_REACH_EXPECT="REACH-LIT-RUN-EMITTED"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (len < 3) return 0;'
SAB_AFTER='    if (len < 3) return 0;
    if (j + len < n) len++;   /* SABOTAGE S304: the run claims the next element */'
