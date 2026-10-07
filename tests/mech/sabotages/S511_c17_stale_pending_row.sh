#!/usr/bin/env bash
# S511 ([MEMFN] R4a, lane memfnmanifest) -- A STALE PENDING ROW.
#
# The (?m)^ skip's `memchr(` in `emit_attempt` is respelled as a call the
# vocabulary does not know (the shape a REPLACE commit has when it moves the
# search into the kit and forgets to flip the row): the MLINE row stays
# `pending` while its emitter spells nothing. Detector: C17 rule 4.
# SAB_REACH_POP asserts the MLINE row is `pending` and names `emit_attempt`.
# RE-AIMED 2026-10-06 ([MEMFN] R4c REPLACE, lane r4ccore): the plant was the
# PRE row's one-byte pre-check (`emit_req_one_byte`) until PRE went
# `delegated` at R4c; it moved to MLINE, a still-pending one-form emitter.
# Intent unchanged: the emitter stops spelling its one form while its row
# stays pending (rule 4).
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
