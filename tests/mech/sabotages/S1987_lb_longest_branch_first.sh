# S1987 ([VLOOKBEHIND] stage 1, design §7 W10; review r4 F10) -- WRITTEN
# BRANCH ORDER BEATS LENGTH. Planted at the parse hook: a two-branch body
# whose second branch is longer is swapped (AST and width table together), so
# the longer branch is tried first. vlbbuild judged reversing the emitter's
# walk too wide a plant; the spine at the hook is one site.
SAB_ID="S1987-lb-longest-branch-first"
SAB_FILE="src/parse/mod_lookaround.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='a two-branch lookbehind body tries its longer branch first (the branches and their widths swapped at the parse hook)'
SAB_DOC_FIGURE='MEASURED (lane vlbfix, tools/review/plant.sh + harness on the target): 52 pass / 2 fail, W10 (line 116: g1 (1,2) -> unset, g2 unset -> (0,2)); clean 54/0.'
SAB_COUNT=1
SAB_BEFORE='        a->u.look.nbranch = info.nbr;
        la_lb_raise(cx, w, info.nbr);'
SAB_AFTER='        a->u.look.nbranch = info.nbr;
        la_lb_raise(cx, w, info.nbr);
        if (info.nbr == 2 && w[1].hi > w[0].hi) {   /* SABOTAGE S1987: the longer branch first */
            Ast *t = body->l; body->l = body->r; body->r = t;
            LookWidth x = w[0]; w[0] = w[1]; w[1] = x;
        }'
