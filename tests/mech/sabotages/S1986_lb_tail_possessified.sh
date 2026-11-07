# S1986 ([VLOOKBEHIND] stage 1, design §7 W3b; review r4 F10) -- THE BODY'S
# TRAILING GREEDY QUANTIFIER GIVES ONE BACK. Planted at the parse hook: a
# branch that is, or ends in, a quantifier gets it marked possessive (no
# frame inside it), the design's own sabotage wording. Narrower than S1985,
# which takes every backtrack; this takes only the tail's give-back.
SAB_ID="S1986-lb-tail-possessified"
SAB_FILE="src/parse/mod_lookaround.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='a lookbehind branch that is or ends in a quantifier gets it possessified, so the end-check cannot make it give one back'
SAB_DOC_FIGURE='MEASURED (lane vlbfix, tools/review/plant.sh + harness on the target): 53 pass / 1 fail, W3b alone (line 33: (?<=a{1,2})a on aaa [1-2] -> [2-3], the design'\''s predicted [2-3] only); clean 54/0.'
SAB_COUNT=1
SAB_BEFORE='        a->u.look.nbranch = info.nbr;
        la_lb_raise(cx, w, info.nbr);'
SAB_AFTER='        a->u.look.nbranch = info.nbr;
        la_lb_raise(cx, w, info.nbr);
        for (const Ast *t = body; ; t = t->l) {   /* SABOTAGE S1986 */
            const Ast *b = t->k == A_ALT ? t->r : t;
            if (b->k == A_REP) ((Ast *)b)->u.rep.possessive = true;
            if (b->k == A_CAT && b->r->k == A_REP) ((Ast *)b->r)->u.rep.possessive = true;
            if (t->k != A_ALT) break;
        }'
