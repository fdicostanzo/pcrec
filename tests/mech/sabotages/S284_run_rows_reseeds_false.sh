# S284 — [OPT-LITSCAN] S1 THE RUN ROWS CLAIM NOT TO WRITE THE STATE
# (src/gen/emit_dfa.c, `dfa_pfs[]`): `reseeds = false` on both run rows,
# whose emitters ARE `pf_emit_ofs[_bounded]` and DO reseed on a seeded
# machine. litscan_s1.md §7.1 row (j), a HARD delivery-bar item (R3-11).
#
# WHY IT SHIPS UNDETECTED (EXPECTED), on S219's precedent — the check was
# BUILT and RUN, and this is its logged outcome, not a choice made in
# advance. The field's one consumer is src/opt/scanedge.c's precondition (8):
# a scan-edge chain head may not be a SEED TARGET on a machine whose
# prefilter reseeds. Under the plant (8) stops firing on run-row machines, so
# the plant is reachable only where a run-row artifact has a forward seed
# table AND a would-be chain head that is a seed target. MEASURED
# (docs/dev/optloop/s1/rowj_reach.py + rowj_reach_output.txt, a real build
# with this plant): of 151 corpus and 94 bench run-row artifact-configs, 2
# carry a forward seed table (bench wild-secrets-github-pat, both auto
# configs, 0 edges either way) and the plant moves 0 artifacts of either
# population; 21 constructed seeded run-row patterns (leading \b/\B, counted
# runs before and after the run) move 0 too. DERIVATION: a seed target is a
# start-state variant `s1u[u]`, a state that has consumed no byte of the
# match; a chain head is a state inside a collapsible counted run. A run row
# needs the run PINNED — every byte from the candidate start to the run at a
# fixed offset — so any counted run before the run has a fixed width and its
# states follow the start states rather than coinciding with them, and a run
# after the pin is entered only past the run's own bytes. No run-row machine
# can make a start variant a head. The detectors that WOULD see it are
# tests/codegen/run_scan_edge_census.sh §4 (P3 over reseeding prefilters, run
# rows included) and dfa_form_derive's precondition-(8) read-back — the
# latter reads the same field, so it cannot, which is recorded here rather
# than discovered.
SAB_ID="S284-run-rows-reseeds-false"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="scanedge harness"
SAB_HARNESS_TARGET="tests/offsetskip/run_pinned.rxt"
SAB_EXPECT=UNDETECTED
SAB_DESC="the run-pinned rows declare reseeds = false though their emitters reseed a seeded machine, so scanedge.c's precondition (8) stops refusing a chain head that is a seed target on those machines — unreachable on every run-row machine the corpus, the bench and 21 constructed witnesses produce"
SAB_DOC_FIGURE="MEASURED 2026-09-25 (lane s1build, a scratch build with this plant, docs/dev/optloop/s1/rowj_reach_output.txt): 0 artifacts moved over 151 corpus + 94 bench run-row artifact-configs (2 seeded, both wild-secrets-github-pat) and 21 constructed seeded witnesses. Expected verdict UNDETECTED (EXPECTED) with reach:ok. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S284."
# [MECH-REACH] the site IS exercised: a seeded run-row machine with a scan edge.
SAB_REACH='"$PCREC" --features all -p rx -fcomments -o "$REACH_TMP/o.c" --pattern "\\bat /user[0-9]{2,50}x" && grep -q "^#define RX_DFA_PREFILTER \"run-pinned-bounded\"" "$REACH_TMP/o.c" && grep -q "rx_forward_seed_state" "$REACH_TMP/o.c" && grep -q "SCAN EDGE" "$REACH_TMP/o.c" && echo REACH-SEEDED-RUN-ROW-WITH-EDGE'
SAB_REACH_EXPECT="REACH-SEEDED-RUN-ROW-WITH-EDGE"
SAB_COUNT=1
SAB_BEFORE='      pf_tables_ofs,  pf_block_ofs, pf_emit_ofs_bounded,    true,  true  },
    { { "run-pinned",          PCREC_NO_OFFSET_SKIP | PCREC_NO_RUN_PREFILTER, pf_run_applies         },
      pf_tables_ofs,  pf_block_ofs, pf_emit_ofs,            true,  true  },'
SAB_AFTER='      pf_tables_ofs,  pf_block_ofs, pf_emit_ofs_bounded,    false, true  },   /* SABOTAGE S284 */
    { { "run-pinned",          PCREC_NO_OFFSET_SKIP | PCREC_NO_RUN_PREFILTER, pf_run_applies         },
      pf_tables_ofs,  pf_block_ofs, pf_emit_ofs,            false, true  },'
