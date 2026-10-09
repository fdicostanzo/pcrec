#!/usr/bin/env bash
# S673 ([MEMFN] M7, lane m7) -- A BACKEND SPELLS ITS COMPARE LOOP AGAIN.
#
# integration.md §17.6's "a replaced form re-added to an emitter", one seam
# over: since M7 the byte backend's exact span compare (`defs_bref`,
# src/enc/enc_byte.c) carries the site token PCREC_ENC_SITE where the loop
# sat and the kit renders the loop (D58 addendum 2). The plant puts the old
# loop text back and drops the token. N7 is `delegated`, so C17 must see a
# span-compare form spelled where no pending row names it (rule 1), and C12
# must see a span-index form with no ceiling row (its rows were deleted at
# M7's REPLACE). It also fails every exact backreference compile loudly (the
# seam refuses a rendered loop with no token), which is the seam's own
# guard, not this row's detector. Arms memfnmanifest, memfnforms. S524's
# analogue.
SAB_ID="S673-m7-backend-respells-loop"
SAB_FILE="src/enc/enc_byte.c"
SAB_SUITES="memfnmanifest memfnforms"
SAB_DESC="the byte backend's exact span compare spells its own loop again (s[at + i]) instead of the kit's site token, while N7 is delegated"
SAB_DOC_FIGURE="HAND-MEASURED by lane m7 2026-10-08 (plant applied, tree rebuilt; docs/dev/lanes/m7_report.md section 6): memfnmanifest 1 failed / 12 passed (C17 rule 1), memfnforms 1 failed / 3 passed (C12: a span-index form with no ceiling row). The matrix figure is owed at the slot."
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "(a+)\1"'
SAB_REACH_EXPECT='        if (at + i >= n || s[at + i] != ref[i])'
SAB_REACH_POP='tests/memfn/site_manifest.tsv|^N7[[:space:]]+pcrec_memfn_span_site,emit_residual_defs[[:space:]].*[[:space:]]delegated[[:space:]]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"                       const unsigned char *ref, size_t reflen, size_t at)\n"
"{\n"
PCREC_ENC_SITE      /* [MEMFN] M7: the kit'"'"'s compare loop (sites_byte) */'
SAB_AFTER='"                       const unsigned char *ref, size_t reflen, size_t at)\n"
"{\n"
"    size_t i;\n"
"    for (i = 0; i < reflen; i++) {\n"
"        if (at + i >= n || s[at + i] != ref[i])\n"
"            return -(ptrdiff_t)i - 1;\n"
"    }\n"  /* SABOTAGE S673 */'
