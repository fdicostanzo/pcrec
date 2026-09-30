# S370 — [OPT-HYB-RESEED] THE SECOND BLOCK NEVER ENDS (src/gen/emit_vm.c, the
# adaptive retry's text): where the first step block would double the next
# one, the plant sets it to UINT_MAX. The FIRST block still ends in its probe
# re-seed; if that probe's gap is short, the call enters the second block and
# never re-seeds again, so a dense-then-sparse subject steps every remaining
# position — the pre-abi-47 defect, reached through the adaptive row. (A
# plant that removed the probe exit itself — a step count that never reaches
# zero — would change the step-exit text the structural checks read; a plant
# that removed only the doubling is benign. This one is the case between.)
#
# THE PLANT KEEPS EVERY STRING THE STRUCTURAL CHECKS READ, the calibration
# literals included (the `< %u` cap test survives; only the assignment
# after it moves): the step-mode exit, the block start and both prefilter
# call sites all survive. Only the BUDGET arm of
# tests/codegen/run_codegen_tests.sh's [OPT-HYB-RESEED] block can see it:
# under --step-budget=2000 the framed witness '(?<=a|é)x' on 40 dense failing
# candidates then 20,000 non-candidates gives up `steps` instead of answering
# nomatch. The answer corpus stays green — no subject there is long enough
# to exhaust a budget — which is why the row names only the codegen arm.
SAB_ID="S370-hyb-reseed-probe-never-ends-block"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen"
SAB_DESC="the adaptive retry's second step block never ends: where the first block would double the next one it sets it to UINT_MAX, so a call whose first block's probe gap is short steps every remaining position and a dense-then-sparse subject walks to the end one VM attempt at a time -- the [OPT-HYB-RESEED] defect reintroduced behind the adaptive row, with every structurally-checked string intact"
SAB_DOC_FIGURE="OWED (lane reseedfix re-anchor, 2026-09-30) -- prior: MEASURED 2026-09-29 (lane reseed): DETECTED, reach:ok(1/1),codegen:2fail/123pass -- the [OPT-HYB-RESEED] budget arm ('40 dense failing candidates then 20,000 non-candidates answered steps, expected nomatch') and [SABANCHOR] (the plant removes this row's own anchor from the sabotaged tree). Every structural [OPT-HYB-RESEED] check stays green. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S370."
SAB_REACH='"$PCREC" --features all -p rx -e utf8 -o "$REACH_TMP/o.c" --pattern "(?<=a|é)x" && grep -qF "#define RX_VM_RESEED \"adaptive\"" "$REACH_TMP/o.c" && grep -qF "else { reseed_steps = reseed_block;" "$REACH_TMP/o.c" && echo REACH-ADAPTIVE-PROBE'
SAB_REACH_EXPECT="REACH-ADAPTIVE-PROBE"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            "            else { reseed_steps = reseed_block; if (reseed_block < %u) reseed_block *= 2; }\n"'
SAB_AFTER='            "            else { reseed_steps = reseed_block; if (reseed_block < %u) reseed_block = (unsigned)-1; }\n"   /* SABOTAGE S370 */'
