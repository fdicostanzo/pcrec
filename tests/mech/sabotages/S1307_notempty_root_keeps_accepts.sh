# S1307 -- [FINDALL-NEXT] I1 (lane i1build; docs/design/findall_iter.md §6.7,
# docs/spec/match_api.md §3.8).
#
# Plant: the notempty root keeps its accepting start threads: the DFA retry accepts the empty match.
# Detector: every dfa-root retry cell repeats an empty match until the driver's cap.
SAB_ID="S1307-notempty-root-keeps-accepts"
SAB_FILE="src/ir/dfa.c"
SAB_SUITES="findall"
SAB_DESC='the notempty root keeps its accepting start threads: the DFA retry accepts the empty match'
SAB_DOC_FIGURE='Owed: the lane queued this row (docs/dev/lanes/i1build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1307.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            vw[v][u].accept = m->noacc ? 0 : acc;'
SAB_AFTER='            vw[v][u].accept = acc;   /* SABOTAGE S1307 */'
