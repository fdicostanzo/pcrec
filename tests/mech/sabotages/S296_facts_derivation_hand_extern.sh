# S296 — [PATFACTS] step 3.0: A CONSUMER REACHES A DERIVATION THROUGH A HAND
# `extern` (src/gen/emit_vm.c declares `pcrec_end_window` at block scope and
# calls it, WITHOUT including facts/facts_derive.h).
#
# THE ESCAPE THE INCLUDE GRAPH CANNOT SEE (docs/design/patfacts/design.md
# §4.2.3): no `#include` line changes, so assertion 1 stays green, and the
# only trace is an undefined reference in emit_vm.o to a symbol an OWNER
# object defines and facts.h does not declare. The call is pure, its
# descriptor NULL (so it returns the decline at its first test) and its
# result discarded, so no emitted byte and no answer moves. The extern
# carries the derivation's REAL signature: a stale one is a wild call, which
# is a crash and not the defect this row stands for.
#
# `facts` (tests/codegen/run_facts_checks.sh, assertion 2, the link-symbol
# join) is its only detector.
SAB_ID="S296-facts-derivation-hand-extern"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="facts"
SAB_DESC="src/gen/emit_vm.c declares pcrec_end_window with a hand block-scope extern and calls it, bypassing facts.h without including the private header — the link-symbol assertion must fail; no answer and no emitted byte moves"
SAB_DOC_FIGURE="facts:1fail/5pass expected (verified by hand before the solo mech run) — [facts-link] reports gen/emit_vm.c referencing pcrec_end_window; [facts-include] stays green (no include line changed). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S296."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    vm_init(&v, cx, root, &g);
    vm_plan(&v, root, &pl);'
SAB_AFTER='    {   /* SABOTAGE S296: a hand extern bypassing facts.h */
        extern long long pcrec_end_window(const PcrecEnc *, const Ast *,
                                          PfWhyCode *);
        PfWhyCode w;
        (void)pcrec_end_window(NULL, root, &w);
    }
    vm_init(&v, cx, root, &g);
    vm_plan(&v, root, &pl);'
