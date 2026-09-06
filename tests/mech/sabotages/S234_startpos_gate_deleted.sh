# S234 — [K50] THE IR BOUNDARY GATE IS NOT BUILT, i.e. K50's own defect
# restored.
#
# `nfa_wrap_unanchored` builds a SECOND split state whose pattern branch sits
# behind an `N_CSTART` gate, so the positions the self-loop generates are the
# encoding's character boundaries. Skip the whole block and the wrap is its
# pre-K50 self, stepping one BYTE — which is exactly the bug: under `-e utf8`
# a pattern that can match empty answers at an offset INSIDE a character.
#
# WHY THIS IS THE ROW WORTH PLANTING, and not a stylistic one: the edit is a
# REVERSION rather than an invention. It is what the file said for the whole
# of [M5.0] stage 2, it compiles cleanly, and it changes nothing under `byte`
# — so every byte-identity gate, the whole `.rxt` corpus outside
# `tests/utf8/`, `make test-axes` and both engines' own agreement with each
# other stay green. Both engines answered `(2,2)` for a milestone; the reason
# nothing caught K50 is that they were wrong TOGETHER.
#
# WHAT SEES IT: `tests/utf8/run_startbnd_diff.sh` §5, whose cells are pinned
# to libpcre2 10.46's answer rather than to the other engine, and
# `tests/utf8/axis11_startpos_boundary.rxt` through the `harness` arm.
# MEASURED at the landing: §5 goes red on 4 of its 7 cells (the three DFA
# self-loop widths and the forced-DFA one) and the corpus file fails its `\B`
# cells; the ENG_ATTEMPT cell stays green, which is correct — that site is a
# different mechanism and has its own row (S235).
SAB_ID="S234-startpos-gate-deleted"
SAB_FILE="src/ir/nfa.c"
SAB_SUITES="startbnd harness"
SAB_HARNESS_TARGET="tests/utf8/axis11_startpos_boundary.rxt"
SAB_DESC="nfa_wrap_unanchored skips the character-boundary gate, so the unanchored DFA's start-anywhere self-loop offers the pattern at every BYTE offset again — K50's own defect, which changes nothing under the byte encoding and which both engines used to agree on"
SAB_DOC_FIGURE="docs/dev/known_issues.md K50 (site 1); docs/design/utf8_design.md 5.5's refutation box; docs/design/utf8_measurements/out/startbnd.txt 1"
SAB_COUNT=1
SAB_REACH='"$PCREC" -p rx -e utf8 --features assertions -o - -- "\\B" | grep -o "forward_next_state" | head -1'
SAB_REACH_EXPECT='forward_next_state'
SAB_BEFORE='    if (e && e->start_cls) {'
SAB_AFTER='    if (0 && e && e->start_cls) {   /* SABOTAGE S234 */'
