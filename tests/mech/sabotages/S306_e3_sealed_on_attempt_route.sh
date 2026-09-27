# S306 — [PATFACTS] step 3.4 THE E3 SEAL LEAKS TO THE ENG_ATTEMPT ARM
# (src/core/compile.c): `pcrec_facts_seal_e3` is also called where the
# forward NFA is NOT wrapped, so the k-set walk and the run pin are derived
# over an anchored-attempt machine whose meaning is not the pin's contract
# (design §3, r1 A3: "E3 is sealed only where the forward NFA is WRAPPED").
#
# THE PLANT IS BEHAVIOURALLY NEUTRAL TODAY, which is why it needs a row: no
# pass asks an E3 fact on the ENG_ATTEMPT route (`unanch_start` is reached
# only from ENG_UNANCH), so every artifact is byte-identical and every answer
# stays right. What moves is the record's claim about the route — the
# `--emit-facts` rows turn `derived` where they must read `absent`,
# `decline:attempt-unwrapped-nfa` — and the first E3 consumer that runs on
# that route (S2b, `[OPT-VMSEED]`) would read a walk over the wrong machine.
# Detector: `tests/codegen/run_facts_checks.sh` [facts-e3], whose route oracle
# is the artifact's own `RX_DFA_SCAN` stamp.
SAB_ID="S306-e3-sealed-on-attempt-route"
SAB_FILE="src/core/compile.c"
SAB_SUITES="facts"
SAB_DESC="the E3 seal is also written in the ENG_ATTEMPT arm, where the forward NFA is never wrapped: the k-set walk and the pin are derived over an anchored-attempt machine and listed as derived where the route must decline them"
SAB_DOC_FIGURE="facts:1fail expected — [facts-e3] reports both attempt-route witnesses (^abc; the hybrid ^foo(?=bar)baz) listing kset_walk/run_pin as derived where RX_DFA_SCAN \"attempt\" implies absent/decline:attempt-unwrapped-nfa; every other facts check stays green. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S306."
# [MECH-REACH] the site answers: `^abc` takes the ENG_ATTEMPT arm.
SAB_REACH='"$PCREC" -p rx -o "$REACH_TMP/o.c" --pattern "^abc" && grep -q "^#define RX_DFA_SCAN \"attempt\"" "$REACH_TMP/o.c" && echo REACH-ATTEMPT-ARM'
SAB_REACH_EXPECT="REACH-ATTEMPT-ARM"
SAB_REACH_POP="tests/codegen/run_facts_checks.sh|^    'E3W[[:space:]].*[[:space:]]attempt[[:space:]]|2"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                cx.job->engine = PCREC_ENG_ATTEMPT;
'
SAB_AFTER='                cx.job->engine = PCREC_ENG_ATTEMPT;
                pcrec_facts_seal_e3(&cx);   /* SABOTAGE S306 */
'
