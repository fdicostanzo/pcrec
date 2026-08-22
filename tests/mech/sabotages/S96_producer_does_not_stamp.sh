# S96 — [M6.4.2] THE PRODUCER DOES NOT STAMP `A_ATOMIC` WITH ITS ROW.
#
# SR-8's CONTRACT, as a row (D67, §5.1). Every AST node a module's producer
# creates carries the registry row it was dispatched on; ONE generic
# `EngineAnalysis` ANDs those rows' `engines` masks over the POST-DISCHARGE
# tree. An UNSTAMPED node contributes ANY_ENGINE — and D67 contract note 2 says
# that default is chosen deliberately, because it fails in the UNSOUND
# direction: a forgotten stamp is a construct that quietly becomes
# DFA-compilable.
#
# WHAT CATCHES IT IS NOT THE DEFAULT, IT IS THE CHECK. The generic assertion in
# `tests/registry/registry_check.c` — every VM_ONLY row with a producer refuses
# `--engine=dfa` BY NAME, on a hand-written witness whose cut BITES — is the
# thing D67 says must keep catching this, and this row is its failing
# direction. It replaced the [M4.7a] tripwire, whose demand ("no VM_ONLY row
# has a producer") SR-8 discharged.
#
# THE ANSWERS DO NOT MOVE on the default engine, which is what makes it a row:
# a cut pattern is still compiled by the VM there (nothing else can), so the
# corpus stays green and only the explicit `--engine=dfa` request silently
# succeeds where it must refuse — producing a DFA artifact that runs the UNCUT
# language.
SAB_ID="S96-producer-does-not-stamp"
SAB_FILE="src/parse/mod_atomic_groups.c"
SAB_SUITES="registry codegen harness atomicdiff"
SAB_HARNESS_TARGET="tests/atomic_groups/atomic_basic.rxt"
SAB_DESC="pcrec_agport_atomic does not call pcrec_ast_stamp, so the A_ATOMIC node carries no registry row and SR-8's generic consultation reads it as ANY_ENGINE. '--engine=dfa (?>a|ab)c' then SUCCEEDS instead of refusing by name, and the DFA artifact runs the UNCUT language -- the default engine's answers are unmoved, which is why the corpus alone cannot see it"
SAB_DOC_FIGURE="PREDICTED: registry's check_engine_capability RED on the '(?>...)' witness; the DEFAULT-engine corpus GREEN (a cut pattern still reaches the VM there). Canonical figure owed from run_sabotage_matrix.sh S96."
SAB_COUNT=1
SAB_BEFORE='    pcrec_ast_stamp(cx, a, rw, at);'
SAB_AFTER='    (void)rw; (void)at;   /* SABOTAGE S96: the node is left unstamped */'
