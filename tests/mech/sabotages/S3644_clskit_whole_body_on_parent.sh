# S3644 -- [ARENA-SCOPES] SCOPE-4 (lane scope4, 2026-11-27): pcrec_clskit_emit_whole
# runs its body on the PARENT arena again (the pre-SCOPE-4 shape: the scope opens
# and closes around nothing, the scratch stays in the attempt arena to its end).
#
# Nothing is wrong at run time, and no L2/L4 rule can see which arena a body
# runs on. DECLARED NETS (r107 A: only what is true): (1) `make alloc` W7/W6's
# exact pins move, because the body's first allocation no longer opens the
# scope's child block (an allocation-COUNT net, incidental: the pin pins counts,
# not lifetimes); read from a run, not assumed. (2) memgate `peak` under
# MG_ENC=1 MG_ENG=2 reads the 108 movers go back to 0: that is NOT a mech suite
# and is not scored here (the lane report cites the command).
SAB_ID="S3644-clskit-whole-body-on-parent"
SAB_FILE="src/gen/clskit.c"
SAB_SUITES="resource"
SAB_DESC="pcrec_clskit_emit_whole's body routed back to the parent arena: alloc_check's exact W6/W7 allocation pins may move (incidental count net, see the header); memgate peak with MG_ENC=1 MG_ENG=2 is the real net and is outside the mech suites"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3644."
SAB_COUNT=1
SAB_BEFORE='    emit_whole_body(c, pcrec_scope_arena(&sc), fn, f, iv, n);'
SAB_AFTER='    emit_whole_body(c, parent, fn, f, iv, n);   /* SABOTAGE S3644 */'
