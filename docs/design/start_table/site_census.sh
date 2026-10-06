#!/usr/bin/env bash
# docs/design/start_table/site_census.sh -- the K35 count behind start_table.md
# §2: every DECISION site (a table or an inline predicate that picks a start
# mechanism) and every READER of one, found BY GREP over src/, never by hand.
# Prints `pattern<TAB>count<TAB>file:line ...`. Read-only. Run from the repo
# root: bash docs/design/start_table/site_census.sh
set -u
cd "${1:-.}"
SRC="src/gen src/opt src/core src/dump src/facts cli"
pat() {   # $1 = label, $2 = grep -E pattern; comment-only lines excluded
  local hits
  hits=$(grep -rnE -- "$2" $SRC --include='*.c' --include='*.h' 2>/dev/null \
         | grep -vE '^[^:]+:[0-9]+:\s*(\*|/\*|//)' )
  printf '%s\t%s\t%s\n' "$1" "$(printf '%s' "$hits" | grep -c .)" \
    "$(printf '%s' "$hits" | cut -d: -f1,2 | tr '\n' ' ')"
}
echo "# tables (first-match row arrays) that select a start mechanism"
pat 'dfa_pfs[] def'            '^static const DfaPf dfa_pfs\[\]'
pat 'req_admits[] def'         '^static const ReqAdmitRow req_admits\[\]'
pat 'req_uses[] def'           '^static const ReqUseRow req_uses\[\]'
pat 'dfa_search_starts[] def'  '^static const DfaSearchStart dfa_search_starts\[\]'
pat 'pcrec_reseed_rows[] def'  '^const PcrecReseedRow pcrec_reseed_rows\[\]'
echo "# inline (non-table) start decisions, and the two route-fixed VM seed lines"
pat 'attempt_cand def'         '^static bool attempt_cand\('
pat 'ENG_ATTEMPT start_max'    'const size_t start_max = %s'
pat 'VM attempt_max'           'const size_t attempt_max = search_from'
pat 'end_window clamp def'     '^void pcrec_emit_end_window_clamp\('
pat 'root minw check'          'root_minw >= PCREC_MINW_MAX'
pat 'hybrid prefilter seed'    'attempt_position = \(size_t\)window\[0\]\[0\]'
pat 'VM no-prefilter seed'     'attempt_position = search_from;'
echo "# selection walks / readers"
pat 'DFA_SELECT_ROUTED(DfaPf'  'DFA_SELECT_ROUTED\(DfaPf'
pat 'dfa_pf_of('               'dfa_pf_of\('
pat 'vm_start_row('            'vm_start_row\('
pat 'req_admit('               '[^_]req_admit\('
pat 'req_use('                 '[^_]req_use\('
pat 'dfa_search_start_of('     'dfa_search_start_of\('
pat 'dfa_search_is_pinned('    'dfa_search_is_pinned\('
pat 'attempt_cand('            'attempt_cand\('
pat 'vm_plan_reseed('          'vm_plan_reseed\('
pat 'pcrec_fact_start_anchor(' 'pcrec_fact_start_anchor\('
pat 'pcrec_fact_end_window('   'pcrec_fact_end_window\('
pat 'pcrec_artifact_has_dfa_scan(' 'pcrec_artifact_has_dfa_scan\('
echo "# emission call sites in the three search bodies"
pat 'end_window_clamp call'    'pcrec_emit_end_window_clamp\(.*cx'
pat 'req_byte_check call'      'pcrec_emit_req_byte_check\(.*cx'
pat 'vm_start_seek call'       'pcrec_emit_vm_start_seek\(.*cx'
pat 'start_zero call'          'pcrec_emit_start_zero\(.*cx'
pat 'startpos_guard call'      'pcrec_emit_startpos_guard\(.*cx'
echo "# --list-axes accessors that project these tables (stream 5)"
pat 'axis accessor'            'pcrec_dfa_axis_(prefilter|match)_cands|pcrec_req_(admit|use)_row\(|pcrec_reseed_rows\['
