# S1455 — the re-entry walk follows calls inside nested lookarounds, so the
# libpcre2-accepted controls (`(?<=a(?=(?R)))x`'s kin, `((?<=(?2))a)(b(?=(?1)))`)
# are refused (K127's other boundary). Lane langfix2; re-anchored by lane
# langfix3 (a nested lookbehind is now followed, a lookahead still not).
SAB_ID="S1455-lookbehind-recursion-follows-lookaround"
SAB_FILE="src/opt/callgraph.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/recursion/inlookaround_self.rxt"
SAB_DESC="cg_length_calls descends into every A_LOOK, a lookahead too"
SAB_DOC_FIGURE="PREDICTED: the ACCEPTED controls whose re-entry is reached only through a lookahead (group 2's (?=(?1)) and (?!(?1))) are refused and fail; the perr blocks stay green. Canonical figure owed from run_sabotage_matrix.sh S1455."
SAB_COUNT=1
SAB_BEFORE="        case A_LOOK:
            if (a->u.look.behind) { a = a->l; continue; }
            return;"
SAB_AFTER="        case A_LOOK:   /* SABOTAGE S1455: a nested lookahead's calls count */
            a = a->l; continue;"
