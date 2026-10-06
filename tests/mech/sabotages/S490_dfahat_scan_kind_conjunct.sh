#!/usr/bin/env bash
# S490 ([START-SET] stage 3; docs/design/startset.md §6.3, sound-F7) -- F's
# SCAN-KIND conjunct removed.
#
# A DECLARED EQUIVALENT MUTANT, scored UNDETECTED (the ss3 D6 panel's
# checks-M2, lane ssfix3; S219's shape; it was declared UNREACHED with a probe
# that could never flip on the clean tree). The conjunct is a belt: every
# caller of the predicate (`dfa_pfs[]`'s selection, `pf_scan_set_of`, G1's
# `dfa_cand_scan`, the re-seed density) is reached on ENG_UNANCH machines
# only, where the conjunct is true, so the plant line runs and changes
# nothing: the planted compiler emits the clean compiler's bytes. The guarded
# population is real (a seeded ATTEMPT-scan machine, `(?m)^` with a `\b`).
# Arm `dfahatstruct` is the byte-identity observable ([dfa-deny], [dfa-movers]
# BY ID over the corpus); an attempt-scan machine the plant admitted would read
# DETECTED (UNEXPECTED). The REACH probe pairs the guarded population with an
# unanchored hat mover that runs the plant line.
SAB_ID='S490-dfahat-scan-kind-conjunct'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='dfahatstruct'
SAB_DESC='the DFA hat'\''s predicate no longer requires the unanchored forward scan; an equivalent mutant while every caller is reached on ENG_UNANCH machines only'
SAB_DOC_FIGURE='DECLARED EQUIVALENT (the argument above); MEASURED by the solo run at the ssfix3 landing (docs/dev/lanes/ssbuild3_report.md, Panel fixes): read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S490.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(?m)^(?:ab|\bcd)'\'' && grep -q '\''^#define RX_DFA_SCAN "attempt"'\'' "$REACH_TMP/o.c" && grep -q '\''rx_seed_state\['\'' "$REACH_TMP/o.c" && "$PCREC" --features all -p rx -o "$REACH_TMP/h.c" --pattern '\''\b(?:true|false)\b'\'' && grep -q '\''^#define RX_DFA_PREFILTER "first-'\'' "$REACH_TMP/h.c" && echo REACH-ATTEMPT-SEEDED-AND-HAT'
SAB_REACH_EXPECT='REACH-ATTEMPT-SEEDED-AND-HAT'
SAB_EXPECT=UNDETECTED
SAB_COUNT=1
SAB_BEFORE='    if (s->cx->job->engine != PCREC_ENG_UNANCH) return false;
    if (!dfa_needs_seed(s->d)) return false;'
SAB_AFTER='    /* SABOTAGE S490: the scan-kind conjunct removed */
    if (!dfa_needs_seed(s->d)) return false;'
