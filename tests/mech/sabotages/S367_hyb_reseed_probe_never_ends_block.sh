# S367 — [OPT-HYB-RESEED] THE PROBE REMOVED (src/gen/emit_vm.c, the adaptive
# retry's text): the step block's length is set to UINT_MAX the first time a
# short probe would have doubled it, so once a call enters step mode it never
# re-seeds again. A dense-then-sparse subject then steps every remaining
# position — the pre-abi-47 defect, reached through the adaptive row.
#
# THE PLANT KEEPS EVERY STRING THE STRUCTURAL CHECKS READ: the step-mode exit
# `if (reseed_steps_left > 0) reseed_steps_left--;`, the probe's block
# assignment `reseed_steps_left = reseed_block;` and both prefilter call sites
# all survive. Only the BUDGET arm of tests/codegen/run_codegen_tests.sh's
# [OPT-HYB-RESEED] block can see it: under --step-budget=2000 the framed
# witness '(?<=a|é)x' on 40 dense failing candidates then 20,000
# non-candidates gives up `steps` instead of answering nomatch. The answer
# corpus stays green — no subject there is long enough to exhaust a budget —
# which is why the row names only the codegen arm.
SAB_ID="S367-hyb-reseed-probe-never-ends-block"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen"
SAB_DESC="the adaptive retry's step block never ends: a short probe sets the next block to UINT_MAX, so after two short re-seed gaps a call steps every remaining position and a dense-then-sparse subject walks to the end one VM attempt at a time -- the [OPT-HYB-RESEED] defect reintroduced behind the adaptive row, with every structurally-checked string intact"
SAB_DOC_FIGURE="MEASURED 2026-09-29 (lane reseed): DETECTED, reach:ok(1/1),codegen:2fail/123pass -- the [OPT-HYB-RESEED] budget arm ('40 dense failing candidates then 20,000 non-candidates answered steps, expected nomatch') and [SABANCHOR] (the plant removes this row's own anchor from the sabotaged tree). Every structural [OPT-HYB-RESEED] check stays green. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S367."
SAB_REACH='"$PCREC" --features all -p rx -e utf8 -o "$REACH_TMP/o.c" --pattern "(?<=a|é)x" && grep -qF "#define RX_VM_RESEED \"adaptive\"" "$REACH_TMP/o.c" && grep -qF "reseed_steps_left = reseed_block;" "$REACH_TMP/o.c" && echo REACH-ADAPTIVE-PROBE'
SAB_REACH_EXPECT="REACH-ADAPTIVE-PROBE"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            "                if (reseed_block < %u) reseed_block *= 2;\n"'
SAB_AFTER='            "                if (reseed_block < %u) reseed_block = (unsigned)-1;\n"   /* SABOTAGE S367 */'
