#!/usr/bin/env bash
# S810 ([REQ-HANDOFF-L1], lane rlhbuild) -- G1 READS NEXT WITHOUT THE
# HANDOFF'S DENY: `cand_read` drops the reader's `under` bits, so PRESENCE's
# dominance question asks NEXT's whole table, whose `handoff` row reads FIRST,
# which reads PRESENCE: the selection re-enters itself and the compiler
# recurses until it dies on every pattern with an emitted pre-check. The
# mechanism the deny-masked read exists for. Detector: every arm that
# compiles such a pattern; prechecks is named.
SAB_ID='S810-g1-reads-reentry'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='prechecks'
SAB_DESC='a selection read ignores its reader'\''s under bits, so G1'\''s read of NEXT re-enters FIRST and PRESENCE: unbounded recursion in the compiler'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/rlhbuild_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S810.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    const CandRow *r = cand_select(slot, s, s->cx->opt->flags |
                                            cand_nodes[reader].under[slot]);'
SAB_AFTER='    const CandRow *r = cand_select(slot, s, s->cx->opt->flags);   /* SABOTAGE S810 */'
