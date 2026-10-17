#!/usr/bin/env bash
# S1091 ([MEMFN] R17-b' B2, lane c1017) -- A KIND LISTED, NEVER OBSERVED.
#
# C17 rule 5 compares the manifest's `kinds` column with the consumer kinds
# the traced corpus pass saw each DELEG_SITES row's door calls state
# (tests/memfn/site_census.py door_kinds: the trace record's site_kind
# field). The plant adds DFA_ATTEMPT, a real mf_site_kind that only the
# MLINE and PRE sites state, to the PF row: the column now lists a kind no
# PF site stated over the pass (a stale column, or a corpus without its
# witness: K35, the column is the population). Detector: rule 5, one FAIL.
# Expectations come from the design (r17b_prime.md §3.1 row B2): PF states
# four kinds, none of them DFA_ATTEMPT.
# SAB_REACH_POP asserts the PF row lists exactly the four kinds before the
# plant, ahead of the budget column.
SAB_ID="S1091-c17-kind-listed-never-observed"
SAB_FILE='tests/memfn/site_manifest.tsv'
SAB_SUITES="memfnmanifest"
SAB_DOC_FIGURE='Validated by plant at lane c1017 (2026-10-17): memfnmanifest 1 failed / 18 passed (rule 5 on PF/DFA_ATTEMPT). Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1091.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH_POP='tests/memfn/site_manifest.tsv|^PF[[:space:]]+[^[:space:]]+[[:space:]]+FIND/ASSIGN[[:space:]]+DFA_SCAN,DFA_HAT,HYB_PF,VM_ATTEMPT[[:space:]]+scan[[:space:]]|1'
SAB_DESC='the PF manifest row also lists DFA_ATTEMPT, a kind no PF site states over the corpus pass: a listed-never-observed kind'
SAB_BEFORE=$'\tFIND/ASSIGN\tDFA_SCAN,DFA_HAT,HYB_PF,VM_ATTEMPT\tscan\t'
SAB_AFTER=$'\tFIND/ASSIGN\tDFA_SCAN,DFA_HAT,HYB_PF,VM_ATTEMPT,DFA_ATTEMPT\tscan\t'
