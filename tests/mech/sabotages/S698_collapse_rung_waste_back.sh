#!/usr/bin/env bash
# S698 ([DEC-COLLAPSE-WASTE], lane decattr, 2026-10-09) -- the collapse rungs
# stop asking whether the collapse can help (`fit_collapse_can_help` answers
# true), so classes (i) and (ii) (no collapsible repeat; nullable but not
# empty_admits) buy back their wasted attempt: the exact machine is rebuilt
# and fails again before the drop row fires. Every final ENGINE_SEL token is
# unchanged by construction (the drop row still fires last), so the
# detectors are the attempt SEQUENCES, hand-written in fbt (a) (seq-ovfii,
# seq-look, seq-ovfpf, seq-pfcdrop, seq-pfcbcat: one row where the plant
# makes two), plus the VM_PREFILTER_WHY figure the wasted attempt carries.
SAB_ID='S698-collapse-rung-waste-back'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="both collapse rungs are offered again on attempts the collapse cannot help (no collapsible repeat, or nullable but not empty_admits), so each such compile rebuilds the failed exact machine once more before dropping the prefilter"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S698. docs/dev/lanes/decattr_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (!cx->job || !(pcrec_fact_kinds(cx) & PF_KIND_COLLAPSIBLE_REP)) return false;'
SAB_AFTER='    if (cx->job) return true;   /* SABOTAGE S698 */
    if (!cx->job || !(pcrec_fact_kinds(cx) & PF_KIND_COLLAPSIBLE_REP)) return false;'
