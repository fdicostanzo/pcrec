# S1490 — the re-entry walk stops at EVERY nested lookaround, a lookbehind
# too, so `((?<=(?2)))(a(?<=(?1)))` (group 2 re-enters group 1 through its
# own lookbehind; libpcre2 10.46 err 125) compiles again (K127's
# nested-lookbehind cells; S1455 cannot see this direction). Lane langfix3.
SAB_ID="S1490-lookbehind-recursion-skips-nested-lookbehind"
SAB_FILE="src/opt/callgraph.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/recursion/inlookaround_self.rxt"
SAB_DESC="cg_length_calls returns at every A_LOOK, a lookbehind too"
SAB_DOC_FIGURE="PREDICTED: the four nested-lookbehind perr blocks compile and fail; every other block stays green. Canonical figure owed from run_sabotage_matrix.sh S1490."
SAB_COUNT=1
SAB_BEFORE="        case A_LOOK:
            if (a->u.look.behind) { a = a->l; continue; }
            return;"
SAB_AFTER="        case A_LOOK:   /* SABOTAGE S1490: a nested lookbehind's calls do not count */
            return;"
