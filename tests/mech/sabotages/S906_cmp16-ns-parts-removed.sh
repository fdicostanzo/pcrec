#!/usr/bin/env bash
# S906 ([COMPOUND] B4, lane cpb4; docs/design/compound.md §E.4 CMP-16) -- the namespace table's `parts` row accepts every prefix, so `-p a__f` compiles a compound whose part symbols can collide with another artifact's.
SAB_ID='S906-cmp16-ns-parts-removed'
SAB_FILE='src/core/compile.c'
SAB_SUITES='compound'
SAB_DESC='the namespace table'\''s `parts` row accepts every prefix, so `-p a__f` compiles a compound whose part symbols can collide with another artifact'\''s'
SAB_DOC_FIGURE='HAND-MEASURED by lane cpb4 2026-10-12 (plant applied to the lane tip, tree rebuilt): @@FIG906@@. The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='static bool ns_parts(const char *p) { return strstr(p, "__") != NULL; }'
SAB_AFTER='static bool ns_parts(const char *p) { (void)p; return false; }   /* SABOTAGE S906 */'
