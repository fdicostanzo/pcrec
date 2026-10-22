# S1450 — the possessive desugar keeps `(?U)`'s inverted default: `(?U)a*+`
# is `(?>a*?)` again and answers (0,0) (K122). Lane langfix2.
SAB_ID="S1450-possessive-keeps-ungreedy"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/atomic_groups/possessive_ungreedy.rxt"
SAB_DESC="p_rep: the possessive suffix no longer forces r->u.rep.greedy, so under (?U) the atomic body is lazy"
SAB_DOC_FIGURE="PREDICTED: most of tests/atomic_groups/possessive_ungreedy.rxt's cells on both engines (every (?U) possessive that can take more than its minimum); the two CONTROL blocks stay green. Canonical figure owed from run_sabotage_matrix.sh S1450."
SAB_COUNT=1
SAB_BEFORE="            r->u.rep.greedy = true;
            size_t plus = cx->pos;"
SAB_AFTER="            size_t plus = cx->pos;   /* SABOTAGE S1450 */"
