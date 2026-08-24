# S148 ([DD-14] wave B+C, design SS9.3 S-SR6) -- `W` EXCLUDES SLOTS 0 AND 1,
# WHICH IS WHERE `\K` LIVES.
#
# THE ROW FOR THE DESIGN THE MEASUREMENTS KILLED. The tempting one-line
# implementation of "put the capture state back" is a TRAIL REWIND to the call
# frame's mark, and it is a MISCOMPILE -- because a rewind restores everything
# the callee wrote, and design SS3.4(b) MEASURED that `\K` is NOT restored by a
# return:
#
#     ^(a\Kb)(?1)$                on "abab" -> (3,4)
#     ^(?(DEFINE)(?<g>a\Kb))(?&g)$ on "ab"   -> (1,2)
#     ^(a(?1)?\Kb)$               on "aabb" -> (3,4)
#
# A `\K` inside a called body MOVES THE REPORTED MATCH START, and the last one
# executed on the successful path wins -- the OUTER level's, after the inner
# level's has already fired. So `\K` is a PATH FACT, not capture state, and it
# survives the return.
#
# AND pcrec SPELLS `\K` AS A WRITE TO `RX_SLOT_WHOLE_START` (STRUCTURAL,
# measured on an artifact for `(a\Kb)+c`), which is SLOT 0 -- group 0's start.
# So the exclusion is a pair of INDICES rather than a family, and this row is
# what makes that pair load-bearing rather than decorative.
#
# THE SABOTAGE IS TWO CHARACTERS and touches nothing else: the builder's two
# `k = 2` starts become `k = 0`. Every family stays in `W`, every offset stays
# compile-time, the capacity is unchanged -- only the pair that carries the
# reported start joins the set.
SAB_ID="S148-w-includes-slot0"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion/kreset.rxt"
SAB_DESC="W is built from slot 0 upward instead of slot 2, so a return RESTORES RX_SLOT_WHOLE_START -- which is where pcrec spells \\K -- and undoes a \\K the callee crossed"
SAB_DOC_FIGURE="PREDICTED (design 9.3 S-SR6): ^(a\\Kb)(?1)\$ on \"abab\" answers (0,4) where 10.46 answers (3,4). kreset.rxt is the file and it declares features assertions,recursion, which is why the target is scoped to it."
SAB_COUNT=1
SAB_BEFORE='            int n = 0;
            for (int k = 2; k < nstate; k++) if (w[k]) n++;
            int *lst = arena_alloc(&cx->arena, (size_t)(n ? n : 1) * sizeof *lst);
            int q = 0;
            for (int k = 2; k < nstate; k++) if (w[k]) lst[q++] = k;'
SAB_AFTER='            /* SABOTAGE S148: slots 0 and 1 become members */
            int n = 0;
            for (int k = 0; k < nstate; k++) if (w[k]) n++;
            int *lst = arena_alloc(&cx->arena, (size_t)(n ? n : 1) * sizeof *lst);
            int q = 0;
            for (int k = 0; k < nstate; k++) if (w[k]) lst[q++] = k;'
