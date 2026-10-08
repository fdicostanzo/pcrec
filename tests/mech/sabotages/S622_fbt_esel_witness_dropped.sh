#!/usr/bin/env bash
# S622 ([DEC-FALLBACK] S-I4, dec_fallback.md §4.4; drafted at B0, numbered at
# B1, lane decfbB1) -- the observed-stamp leg loses its one
# `overflowed-prefilter` witness, so a value match_api.md §6.3 lists is
# stamped by no witness: the leg B5's registry-source retirement stands
# behind would certify a set it no longer observes.
# Detector (arm fallbacktable): tests/codegen/run_fallback_table.sh (b)'s
# K35 floor for that value.
SAB_ID='S622-fbt-esel-witness-dropped'
SAB_FILE='tests/codegen/run_fallback_table.sh'
SAB_SUITES='fallbacktable'
SAB_DESC="run_fallback_table.sh (b) drops its overflowed-prefilter witness, so the ENGINE_SEL value has no witness and only the K35 floor can say so"
SAB_DOC_FIGURE='B0 drafted the plant (docs/dev/lanes/decfbB0b_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S622.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE="wit sel-ovfpf         lowdfa  'overflowed-prefilter'      default \"\$OVFPF\""
SAB_AFTER=": # SABOTAGE S622: the overflowed-prefilter witness dropped"
