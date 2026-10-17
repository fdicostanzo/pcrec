#!/usr/bin/env bash
# S1097 (lane b3a, [MEMFN] R17-b' B3a) -- SN-6: the set-leads port leads on an EQUALLY rare set pick; caught by the -e utf8 x.*abc tie witness
SAB_ID="S1097-leads-not-strict"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="candoracle"
SAB_DESC="SN-6: the set-leads port leads on an EQUALLY rare set pick; caught by the -e utf8 x.*abc tie witness"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            out->set_leads = cube_mass(rate, (unsigned)q, 0xFFu) <'
SAB_AFTER='            out->set_leads = cube_mass(rate, (unsigned)q, 0xFFu) <=   /* SABOTAGE S1097 */'
