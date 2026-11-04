#!/usr/bin/env bash
# S1097 (lane b3a, [MEMFN] R17-b' B3a) -- SN-6: the set-leads port leads on an EQUALLY rare set pick; caught by the -e utf8 x.*abc tie witness
# span_pick unit 1b (lane sp1b) RE-ANCHORED: cube_mass became the one mass primitive kit_mass; the
# same `<` of the set-leads compare is planted `<=` (intent unchanged).
# span_pick unit 1c (lane sp1c) RE-ANCHORED: the set pick's position is its own span's set and the
# run's side the run member's mass (`sc.mass`); the same `<` is planted `<=` (intent unchanged).
SAB_ID="S1097-leads-not-strict"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="candoracle"
SAB_DESC="SN-6: the set-leads port leads on an EQUALLY rare set pick; caught by the -e utf8 x.*abc tie witness"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            out->set_leads = kit_mass(rate, s->pspans[best].term[0].set, 1, KIT_MASS_SUM) <'
SAB_AFTER='            out->set_leads = kit_mass(rate, s->pspans[best].term[0].set, 1, KIT_MASS_SUM) <=   /* SABOTAGE S1097 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane sp1c (re-anchor; docs/dev/lanes/sp1c_report.md): the row's plant on a git archive of 439c263c8, built, tests/codegen/run_cand_oracle.sh: candoracle:16fail/149pass DETECTED (clean 0fail/178pass). Earlier: lane b3afix, candoracle:11fail/121pass at ebfb5a88a."
