#!/usr/bin/env bash
# S477 ([K82] (B), lane k82hbuild) -- DD12a(i)'s HANDOFF EXCISION IS WIDENED.
#
# Detector: the excision's own 8-line ceiling (HANDOFF_MAX_LINES): a widened
# end anchor spans the rest of the function and is reported as a selection
# incoherence on every handoff pair.
SAB_ID="S477-dd12a-excision-widened"
SAB_FILE="tests/codegen/run_encoding_checks.sh"
SAB_SUITES="encoding"
SAB_DESC='DD12a(i)'\''s handoff-block excision runs to the function'\''s closing brace instead of the block'\''s own last line, which would hide the rest of the search body from the comparison'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/k82hbuild_report.md §6); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S477.'
SAB_REACH='"$PCREC" --features all -p rx -e utf8 -o "$REACH_TMP/o.c" --pattern '\''(?i)straße'\'' && grep -q '\''if (handoff_position - search_from > 2) {'\'' "$REACH_TMP/o.c" && echo REACH-UTF8-BLOCK'
SAB_REACH_EXPECT='REACH-UTF8-BLOCK'
SAB_REACH_POP='tests/codegen/run_encoding_checks.sh|HANDOFF_MAX_LINES = 8|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='HANDOFF_CLOSE_RE = re.compile(r'\''^\s*handoff_position = search_from;$'\'')'
SAB_AFTER='HANDOFF_CLOSE_RE = re.compile(r'\''^}$'\'')  # SABOTAGE S477'
