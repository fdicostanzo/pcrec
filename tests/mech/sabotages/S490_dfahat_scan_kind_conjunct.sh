#!/usr/bin/env bash
# S490 ([START-SET] stage 3; docs/design/startset.md §6.3, sound-F7) -- F's
# SCAN-KIND conjunct removed.
#
# A DECLARED EQUIVALENT MUTANT, scored UNDETECTED (the ss3 D6 panel's
# checks-M2, lane ssfix3; S219's shape; it was declared UNREACHED with a probe
# that could never flip on the clean tree). The conjunct is a belt: every
# caller of the predicate (`dfa_pfs[]`'s selection, `cand_rows[]`'s since C3, `pf_scan_set_of`, G1's
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
SAB_DOC_FIGURE='DECLARED EQUIVALENT (the argument above). MEASURED 2026-10-06 (lane ssfix3, solo, 3b7ba538): UNDETECTED (EXPECTED), reach:ok(1/1), dfahatstruct:0fail/32pass. See (docs/dev/lanes/ssbuild3_report.md, Panel fixes): read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S490.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(?m)^(?:ab|\bcd)'\'' && grep -q '\''^#define RX_DFA_SCAN "attempt"'\'' "$REACH_TMP/o.c" && grep -q '\''rx_seed_state\['\'' "$REACH_TMP/o.c" && "$PCREC" --features all -p rx -o "$REACH_TMP/h.c" --pattern '\''\b(?:true|false)\b'\'' && grep -q '\''^#define RX_DFA_PREFILTER "first-'\'' "$REACH_TMP/h.c" && echo REACH-ATTEMPT-SEEDED-AND-HAT'
SAB_REACH_EXPECT='REACH-ATTEMPT-SEEDED-AND-HAT'
SAB_EXPECT=UNDETECTED
SAB_COUNT=1
# RE-AIMED 2026-10-07 (lane stc3, [START-TABLE] C3, start_table.md §3.5,
# sound-n5): the conjunct reads the one route derivation, `cand_route_of`,
# since C3 (it is one of the fifteen `job->engine` tests). The EQUIVALENCE
# argument is RE-VERIFIED under its moved premise: before C3 it was "every
# caller of the predicate is reached on ENG_UNANCH machines only"; since C3
# the predicate is reached only through `cand_rows[]`'s N5/N6 (`routes` =
# CR_DFA) and the `u.pf.scan_set` hook of those two rows, and every NEXT
# walk that can reach them is on `cand_route_of(cx) == CAND_ROUTE_DFA`
# (dfa_pf_of, scan_state_written and dfa_form_derive are all on ENG_UNANCH
# bodies; the ATTEMPT walk, attempt_next_of, is CR_ATTEMPT and the `routes`
# column excludes N5/N6 there), so the conjunct is still always true where
# it runs and the planted compiler still emits the clean compiler's bytes.
SAB_BEFORE='    if (cand_route_of(s->cx) != CAND_ROUTE_DFA) return false;
    if (!dfa_needs_seed(s->d)) return false;'
SAB_AFTER='    /* SABOTAGE S490: the scan-kind conjunct removed */
    if (!dfa_needs_seed(s->d)) return false;'
