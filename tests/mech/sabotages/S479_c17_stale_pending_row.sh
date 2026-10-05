#!/usr/bin/env bash
# S479 ([MEMFN] R4a, lane memfnmanifest) -- A STALE PENDING ROW.
#
# The one-byte pre-check's `memchr(` is respelled as a call the vocabulary
# does not know (the shape a REPLACE commit has when it moves the search
# into the kit and forgets to flip the row): the PRE row stays `pending`
# while its emitter, `emit_req_one_byte`, spells nothing. Detector: C17
# rule 4. SAB_REACH_POP asserts the row is `pending` and names that emitter.
SAB_ID="S479-c17-stale-pending-row"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="memfnmanifest"
SAB_DESC='emit_req_one_byte stops spelling memchr( (respelled as a kit-style call) while the PRE manifest row stays pending: a stale row'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/memfnmanifest_report.md §4); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S479.'
SAB_REACH_POP='tests/memfn/site_manifest.tsv|^PRE[[:space:]]+emit_req_one_byte[[:space:]].*[[:space:]]pending[[:space:]]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"%s    !memchr(%s + %s, %d, %s - %s))\n"'
SAB_AFTER='"%s    !pcrec_mf_find(%s + %s, %d, %s - %s))\n"  /* SABOTAGE S479 */'
