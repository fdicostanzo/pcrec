#!/usr/bin/env bash
# S845 ([CAND-PATH-READS], lane s845row) -- FIRST LOSES ITS DECLARED PATH
# READS: the plant drops `CAND_PATH_READS` from FIRST's `reads` in
# `cand_nodes[]`. FIRST's `handoff` row still calls `cand_path_members`, whose
# walk selects LOCATE (and RECOVER, FINISH), but the graph no longer declares
# the edge. The trace build's nested-read check (`cand_nested_read`) holds every
# selection made inside a running predicate to a declared edge, so each checked
# decision that reaches the path aborts `CANDORACLE undeclared-read FIRST
# LOCATE` (23 failures by hand over the dfa/attempt/vm witnesses). S844 is the
# sibling row: it plants the cycle the declared edges let the self-check see;
# this one plants the undeclared edge itself. Detector (arm candoracle):
# tests/codegen/run_cand_oracle.sh. REACH: the unplanted trace build is green
# and the planted one prints the named message (pathreads_report.md s845row).
SAB_ID='S845-first-drops-path-reads'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle'
SAB_DESC='the start table'\''s FIRST node no longer declares its PATH reads, so the trace build'\''s nested-read check aborts with an undeclared read of LOCATE'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/pathreads_report.md s845row); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S845.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                                        CAND_PATH_READS } },'
SAB_AFTER='                                        } },   /* SABOTAGE S845 */'
