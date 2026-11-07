#!/usr/bin/env bash
# S2933 -- span_pick stage 2 unit S2c, review 2026-11-06 r9 G4 (EMIT-1/SLOT-6/HOUSE-2, ruled FOLD; lane
# s2cfix). A FORM ID'S HASH COVERS ONLY ITS CANONICAL INSTANCE.
#
# Plant: formhash.c's mf_form_hash folds only the canonical instance of an id (r9's finding: a kit change to
# rc-words w3's or settest cn's text alone would leave the id's recorded dep matching, so those rows' prices
# go stale silently).
# Detector: tests/memfn/finder_check.py check B (arm memfnfinder): mf_form_hash(id) equals the fold of its
# instances' site texts, folded by the check itself from `--site-text` ("is not the fold of its N instances'
# site texts", for settest and rc-words).
SAB_ID="S2933-formhash-fold-canonical-only"
SAB_FILE="memfn/src/formhash.c"
SAB_SUITES="memfnfinder"
SAB_DESC='mf_form_hash folds only an id'"'"'s canonical instance: a change to another instance moves no dep'
SAB_DOC_FIGURE='MEASURED by lane s2cfix, planted and reverted by hand (test-memfn-finder red, then green); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2933.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (strcmp(entries[i].id, form_id)) continue;'
SAB_AFTER='        if (strcmp(entries[i].id, form_id) || !entries[i].canon) continue;   /* SABOTAGE S2933 */'
