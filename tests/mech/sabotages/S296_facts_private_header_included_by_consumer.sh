# S296 — [PATFACTS] step 3.0: A CONSUMER INCLUDES THE FACTS-PRIVATE HEADER
# (src/gen/emit_vm.c gains `#include "facts/facts_derive.h"`).
#
# THE DEFECT IT STANDS FOR: an emitter that can see a derivation's
# declaration can call it, and a direct call is a second, unmemoized,
# undenied path to a pattern fact — the parallel mechanism the record exists
# to remove (docs/design/patfacts/design.md §4.2.3). The plant re-inserts NO
# function name and calls nothing: it is the include alone, so the row is
# independent of any grep string (the design's answer to revision 1's
# control-shares-a-source defect, learnings §3).
#
# NOT ANSWER-DETECTABLE by construction — the plant changes no emitted byte
# and no answer. `facts` (tests/codegen/run_facts_checks.sh, assertion 1,
# the include graph against the owner list generated from facts.def) is its
# only detector.
SAB_ID="S296-facts-private-header-included-by-consumer"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="facts"
SAB_DESC="src/gen/emit_vm.c includes facts/facts_derive.h, the facts-private header, without being a facts.def owner — the include-graph assertion must fail; no answer and no emitted byte moves"
SAB_DOC_FIGURE="facts:1fail/5pass expected (verified by hand before the solo mech run) — [facts-include] reports src/gen/emit_vm.c as an includer the owner list does not name; [facts-link] stays green (the include alone references no symbol). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S296."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='#include "enc/enc.h"'
SAB_AFTER='#include "enc/enc.h"
#include "facts/facts_derive.h"   /* SABOTAGE S296: a consumer includes the facts-private header */'
