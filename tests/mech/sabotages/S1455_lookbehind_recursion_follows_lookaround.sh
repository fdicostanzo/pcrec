# S1455 — the re-entry walk follows calls inside nested lookarounds, so the
# libpcre2-accepted controls (`(?<=a(?=(?R)))x`'s kin, `((?<=(?2))a)(b(?=(?1)))`)
# are refused (K127's other boundary). Lane langfix2.
SAB_ID="S1455-lookbehind-recursion-follows-lookaround"
SAB_FILE="src/opt/callgraph.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/recursion/inlookaround_self.rxt"
SAB_DESC="cg_length_calls descends into A_LOOK like any single-child node"
SAB_DOC_FIGURE="PREDICTED: the ACCEPTED control whose re-entry is reached only through a lookahead in group 2 is refused and fails; the perr blocks stay green. Canonical figure owed from run_sabotage_matrix.sh S1455."
SAB_COUNT=1
SAB_BEFORE="        case A_LOOK:
        case A_CLASS: case A_EMPTY: case A_EOL:
        case A_CTX: case A_GSTART: case A_KRESET:
        case A_BREF: case A_VAR:
            return;
        case A_CAP: case A_REP: case A_ATOMIC: case A_WCLASS:"
SAB_AFTER="        case A_CLASS: case A_EMPTY: case A_EOL:
        case A_CTX: case A_GSTART: case A_KRESET:
        case A_BREF: case A_VAR:
            return;
        case A_LOOK:   /* SABOTAGE S1455: a nested lookaround's calls count */
        case A_CAP: case A_REP: case A_ATOMIC: case A_WCLASS:"
