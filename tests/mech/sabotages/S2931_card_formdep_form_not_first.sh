#!/usr/bin/env bash
# S2931 -- span_pick stage 2 unit S2c, sabotage (n) (docs/design/memfn/span_cards.md §2.4, §9's S2c row;
# lane memfn-s2c). A kit-grid@3 CARD WITH A kit:form. DEP AND `form` NOT ITS FIRST DIM.
#
# Plant: verify_cmp@3's dims `form;cls;pass` become `cls;form;pass`: its rows' first token would be a
# class, not the form id its deps hash.
# Detector: tests/memfn/finder_check.py check C's card guard (arm memfnfinder), in the card-table walk
# over every table and every ver (no set holds a kit-grid@3 row yet, so only the CARD walk sees it).
SAB_ID="S2931-card-formdep-form-not-first"
SAB_FILE="memfn/data/cards/kit-grid.tsv"
SAB_SUITES="memfnfinder"
SAB_DESC='a kit-grid@3 card names kit:form. deps while its first dim is not form'
SAB_DOC_FIGURE='MEASURED by lane memfn-s2c (sub-lane fh) planted and reverted by hand; exact re-run: bash tests/mech/run_sabotage_matrix.sh S2931.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='kit	verify_cmp	3	form;cls;pass	'
SAB_AFTER='kit	verify_cmp	3	cls;form;pass	'
