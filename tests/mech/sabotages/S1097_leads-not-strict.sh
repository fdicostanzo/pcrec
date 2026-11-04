#!/usr/bin/env bash
# S1097 (lane b3a, [MEMFN] R17-b' B3a) -- SN-6: the set-leads port leads on an EQUALLY rare set pick; caught by the -e utf8 x.*abc tie witness
# span_pick unit 1b (lane sp1b) RE-ANCHORED: cube_mass became the one mass primitive kit_mass; the
# same `<` of the set-leads compare is planted `<=` (intent unchanged).
SAB_ID="S1097-leads-not-strict"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="candoracle"
SAB_DESC="SN-6: the set-leads port leads on an EQUALLY rare set pick; caught by the -e utf8 x.*abc tie witness"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            out->set_leads = kit_mass(rate, &qp, 1, KIT_MASS_SUM) <'
SAB_AFTER='            out->set_leads = kit_mass(rate, &qp, 1, KIT_MASS_SUM) <=   /* SABOTAGE S1097 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane b3afix: see docs/dev/lanes/b3a_report.md §9 (the solo mech run of this row, candoracle:11fail/121pass DETECTED at ebfb5a88a)."
