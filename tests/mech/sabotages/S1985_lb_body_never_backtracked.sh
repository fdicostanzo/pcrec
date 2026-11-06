# S1985 ([VLOOKBEHIND] stage 1, design §7 W3; review r4 F10) -- THE END-CHECK
# BACKTRACKS INTO THE BODY. A candidate whose body's first path ends short of
# the cursor must retry the body's other paths before the next candidate.
# The plant wraps a one-branch body in an atomic group at the parse hook (one
# site; the count pass and the emitter both read the AST, so no slot drift),
# so the body's first success is its only one. vlbbuild found no one-edit
# EMITTER plant (the cut is the body's frame structure); the AST is the site.
SAB_ID="S1985-lb-body-never-backtracked"
SAB_FILE="src/parse/mod_lookaround.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='a one-branch lookbehind body is made atomic at the parse hook, so the end-check never backtracks into it'
SAB_DOC_FIGURE='MEASURED (lane vlbfix, tools/review/plant.sh + harness on the target): 49 pass / 5 fail, W3 (line 25: match 3 4 -> nomatch), W3b (line 33: [1-2] -> [2-3]) and W1 (line 12: g1 (0,2) -> (1,2)); clean 54/0.'
SAB_COUNT=1
SAB_BEFORE='        a->u.look.nbranch = info.nbr;
        la_lb_raise(cx, w, info.nbr);'
SAB_AFTER='        a->u.look.nbranch = info.nbr;
        la_lb_raise(cx, w, info.nbr);
        if (info.nbr == 1) {   /* SABOTAGE S1985: the body is never backtracked into */
            Ast *g = pcrec_ast_node(cx, A_ATOMIC);
            g->l = body;
            a->l = g;
        }'
