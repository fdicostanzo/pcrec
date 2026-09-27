# S300 — [PATFACTS] step 3.0: THE `decisions` SECTION DROPS A STAMP
# (src/dump/facts_dump.c: every `<PREFIX>_REQ_WHY` row is skipped).
#
# THE DEFECT IT STANDS FOR: a decisions section that is no longer the
# artifact's own stamp block — the listing claiming the artifact decided
# less than it did. The check parses the EMITTED C file with its own rule
# (the machinery macros excluded by NAME, where the printer excludes
# function-like macros by their `(`), so the two readers share no parser
# (design §11.6 check 4, r1 A12).
#
# `facts` (tests/codegen/run_facts_checks.sh, [facts-decisions]) is its only
# detector.
SAB_ID="S300-facts-decisions-stamp-dropped"
SAB_FILE="src/dump/facts_dump.c"
SAB_SUITES="facts"
SAB_DESC="the --emit-facts decisions section skips every REQ_WHY stamp, so it is no longer the artifact's stamp block — the decisions=stamps check must fail on all three artifacts; no artifact byte moves"
SAB_DOC_FIGURE="facts:1fail/5pass expected (verified by hand before the solo mech run) — [facts-decisions] reports one differing line per artifact (the RX_REQ_WHY row) on the DFA, hybrid and VM witnesses. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S300."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                pcrec_sb_row(&r->dec, cells, 3);'
SAB_AFTER='                if (!strstr(cells[1], "REQ_WHY"))   /* SABOTAGE S300 */
                    pcrec_sb_row(&r->dec, cells, 3);'
