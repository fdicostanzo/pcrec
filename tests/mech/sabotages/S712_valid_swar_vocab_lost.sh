#!/usr/bin/env bash
# S712 ([MEMFN] R-12, lane vmlazy) -- THE VALID ROW'S VOCABULARY LINE LOST
# (S685's successor). RULED Q-R12-5: `$_valid_upto`'s ASCII SWAR skip is
# listed `pending` (row VALID) with its own vocabulary line (swar-hibit). The
# plant blinds the line: C17 rule 4 fires (a pending row whose emitter spells
# nothing), and C12's swar-hibit ceiling row goes STALE (memfnforms).
SAB_ID="S712-valid-swar-vocab-lost"
SAB_FILE="tests/memfn/search_vocab.tsv"
SAB_SUITES="memfnmanifest memfnforms"
SAB_DESC='the search vocabulary forgets the word-at-a-time high-bit skip (line swar-hibit), so the pending VALID row'"'"'s emitter (u8_defs_valid_upto, the ASCII SWAR skip) spells no form C17 sees: the form escapes the static half'
SAB_DOC_FIGURE="HAND-MEASURED by lane vmlazy 2026-10-09 (one mech row, solo): see docs/dev/lanes/vmlazy_report.md §5. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S712."
SAB_REACH='bash "$TREE/tests/memfn/run_site_manifest.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: rule 4: u8_defs_valid_upto (pending: VALID) spells 1 form(s)'
SAB_REACH_POP='tests/memfn/site_manifest.tsv|^VALID[[:space:]]+u8_defs_valid_upto[[:space:]].*[[:space:]]pending[[:space:]]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='word-skip	swar-hibit	'
SAB_AFTER='word-skip	swar-hibit-SABOTAGE-S712	^$NEVER'
