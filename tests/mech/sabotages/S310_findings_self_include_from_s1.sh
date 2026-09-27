# S310 — [FINDINGS] B2 F-4: A SELF-INCLUDE RESOLVES FROM THE FIRST STOP
# (src/parse/rxt_find.c, `pcrec_find_chain_build`): `include <x>` inside the
# bundle `x` restarts the search at S1 instead of at the stop AFTER the one
# `x` was found at — so the copy-edit-shadow case (design §0.4: "my `log` is
# the shipped `log` plus my own run table") finds ITSELF and is refused as an
# include cycle, where gcc's `#include_next` semantics reach the next
# definition of the name.
#
# Detector: run_findings_tests.sh §6 #3 (an -I `default.rxt` including
# <default> must compile and answer `byte` from the shipped default).
SAB_ID="S310-findings-self-include-from-s1"
SAB_FILE="src/parse/rxt_find.c"
SAB_SUITES="findings"
SAB_DESC="a bundle's include of its own name restarts the search at the first stop, so it finds itself and is refused as an include cycle — include_next (design §0.4, §4.3) broken, and the copy-edit-shadow customization impossible"
SAB_DOC_FIGURE="findings red on §6 [#3] (the self-including default does not compile: an include cycle) and on every fixture chained through it. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S310."
SAB_REACH='python3 "$TREE/tests/findings/res_fixtures.py" "$REACH_TMP/r" && "$PCREC" -p rx -I "$REACH_TMP/r/A" --analysis default -o "$REACH_TMP/a.c" --pattern "abc" && grep -q "^#define RX_FINDINGS \"byte-rate=default:1822fb973b95a4da\"" "$REACH_TMP/a.c" && echo REACH-FINDINGS-INCLUDE-NEXT'
SAB_REACH_EXPECT="REACH-FINDINGS-INCLUDE-NEXT"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            size_t start = !strcmp(inc, links[n - 1].bundle) ? at[n - 1] + 1 : 0;'
SAB_AFTER='            size_t start = 0;   /* SABOTAGE S310: include_next dropped */'
