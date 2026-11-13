#!/usr/bin/env bash
# S1909 (lane sae1fix, 2026-11-09; review 2026-11-09-r3-sae1 CHECK-1) -- A
# COMPOUND PART DROPS THE RESTORED ARMS.
#
# A split artifact's parts are compiled by src/core/compound.c, which hands
# each the walking attempt's inherited set (`PcrecMeasInherit`); the restored
# walk arms ride it (`walk_arms`). This plant drops them there, so under
# `--harness=restore=empty` the top compile is restored and the part is not (a
# half-restored artifact; `make test-axes`' internal arm then compares the new
# form with itself on every split artifact). Detector:
# tests/codegen/run_facts_checks.sh [facts-arm], the `RX__Q_REQ_RUN` cells.
SAB_ID="S1909-compound-part-drops-restored-arms"
SAB_FILE="src/core/compound.c"
SAB_SUITES="facts"
SAB_DESC="a compound part's walk is compiled without the restored arms of the walking attempt, so the harness lever leaves split artifacts half-restored"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/sae1fix_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1909."
SAB_REACH='"$(dirname "$PCREC")/pcrec-harness" --features all --harness=restore=empty -p rx --emit-main -o /dev/stdout --pattern "^a|abcd(?:\\b)*efgh\$" | grep -qF "RX__Q_REQ_RUN \"61626364\"" && echo REACH-PART-RESTORED'
SAB_REACH_EXPECT="REACH-PART-RESTORED"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                                            ? w->cx->emit_in->harness->walk_arms : 0 };'
SAB_AFTER='                                            ? 0 : 0 };   /* SABOTAGE S1909 */'
# RE-AIMED REACH (lane sar1fix, 2026-11-09, review r5): the restored part's
# halves tie and go to the rarer scan byte: `abcd` at 1.
# RE-AIMED REACH (lane k382n, 2026-11-12; cloud mech 43261368093 shard 5
# UNREACHED): under K38-2 no search of this artifact reads a run position, so
# the restored part's run prints without its `@` (match_api.md §6.3.7¶7's @
# table, row 3): `"61626364"`, the quoted text the unrestored part's
# `"6162636465666768"` does not contain. Same cell, same detector; verified
# by single compiles on the tip (restored part `61626364`) and with the plant
# (`6162636465666768`).
