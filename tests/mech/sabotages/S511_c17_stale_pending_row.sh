#!/usr/bin/env bash
# S511 ([MEMFN] R4a, lane memfnmanifest) -- A STALE PENDING ROW.
#
# The one-byte pre-check's `memchr(` is respelled as a call the vocabulary
# does not know (the shape a REPLACE commit has when it moves the search
# into the kit and forgets to flip the row): the PRE row stays `pending`
# while its emitter, `emit_req_one_byte`, spells nothing. Detector: C17
# rule 4. SAB_REACH_POP asserts the row is `pending` and names that emitter.
# RE-AIMED 2026-10-06 ([MEMFN] R4c REPLACE, lane r4ccore): PRE went `delegated` at R4c, so the stale-pending plant moves to a still-pending one-form emitter: MLINE's (`emit_attempt`, the (?m)^ skip). Intent unchanged: the emitter stops spelling its one form while its row stays pending (rule 4).
SAB_ID="S511-c17-stale-pending-row"
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES="memfnmanifest"
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/memfnmanifest_report.md §4); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S511.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH_POP='tests/memfn/site_manifest.tsv|^MLINE[[:space:]]+emit_attempt[[:space:]].*[[:space:]]pending[[:space:]]|1'
SAB_DESC='emit_attempt stops spelling memchr( (respelled as a kit-style call) while the MLINE manifest row stays pending: a stale row'
SAB_BEFORE='"            const void *q = memchr(subject + start, %d, "'
SAB_AFTER='"            const void *q = pcrec_mf_find(subject + start, %d, "  /* SABOTAGE S511 */'
