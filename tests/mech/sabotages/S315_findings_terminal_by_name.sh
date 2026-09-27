# S315 — [FINDINGS] B2 F-11: THE CHAIN'S TERMINAL IS RESOLVED BY NAME
# (src/parse/rxt_find.c, `pcrec_find_chain_build`): the implicit `default`
# every chain ends in is looked up through the stops like any name, so an
# `-I` directory holding a `default.rxt` silently moves every artifact built
# with that `-I` — including compiles that name no analysis and passed `-I`
# only for `lib` (design §0.6: the terminal is the BUILT-IN default by
# identity; §16 Q1, ruled).
#
# Detector: run_findings_tests.sh §6 #9 (an unnamed compile with an -I dir
# holding default.rxt must be byte-identical to one without the -I).
SAB_ID="S315-findings-terminal-by-name"
SAB_FILE="src/parse/rxt_find.c"
SAB_SUITES="findings"
SAB_DESC="the chain's implicit default terminal is found by a name lookup through S1/S2/S3 instead of by identity, so a default.rxt in any -I directory moves every compile that names no analysis — the accident design §0.6 rules out"
SAB_DOC_FIGURE="findings red on §6 [#9] (the -I dir holding default.rxt moved an unnamed compile) and on the fixtures chained through A/. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S315."
SAB_REACH='python3 "$TREE/tests/findings/res_fixtures.py" "$REACH_TMP/r" && mkdir -p "$REACH_TMP/x" "$REACH_TMP/y" && "$PCREC" -p rx -o "$REACH_TMP/x/a.c" --pattern "abc" && "$PCREC" -p rx -I "$REACH_TMP/r/A" -o "$REACH_TMP/y/a.c" --pattern "abc" && cmp -s "$REACH_TMP/x/a.c" "$REACH_TMP/y/a.c" && echo REACH-FINDINGS-TERMINAL-IDENTITY'
SAB_REACH_EXPECT="REACH-FINDINGS-TERMINAL-IDENTITY"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (!have_default &&
        pcrec_find_store_link("default", PCREC_FIND_STOP_DEFAULT, &links[n]))
        n++;'
SAB_AFTER='    if (!have_default && find_bundle(&w, "default", 0, &links[n], &s) == 0)   /* SABOTAGE S315 */
        n++;'
