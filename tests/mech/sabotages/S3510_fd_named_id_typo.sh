#!/usr/bin/env bash
# S3510 -- review r75 SLOT-2 (lane bsu2fix): a FIND row's name for fd_brow_is is mis-spelled ("R7W" for "R7w")
# fd_named_id[] is a third spelling of a finder row's id; a typo compiled, refused nothing and made fd_brow_is
# never true for the row, silently turning T-vscan (`[0-9]{25}`, `\d{32}`) back into the inline text, which only
# the opt-in DIFFER floors saw. fd_tables_check (finder.c, called from mf_art_begin beside wf_tables_check)
# now refuses the art, so every artifact compile errors: the codegen suite reds.
SAB_ID="S3510-fd-named-id-typo"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="codegen"
SAB_DESC="fd_named_id spells R7w as R7W: fd_tables_check must refuse every art at mf_art_begin"
SAB_DOC_FIGURE="memfn/src/finder.c fd_tables_check (r75 SLOT-2). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3510."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='[FD_NAMED_R7W] = "R7w"'
SAB_AFTER='[FD_NAMED_R7W] = "R7W"   /* SABOTAGE S3510 */'
