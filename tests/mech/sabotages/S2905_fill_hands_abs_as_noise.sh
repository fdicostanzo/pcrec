# S2905 — span_pick stage 2 unit S2a (lane s2a; docs/design/memfn/span_cards.md rev 1.1 §9 row (f);
# docs/spec/measures.md §2.2¶3a, §3.3¶1a, §4¶2a).
#
# Plant: (f) the fill hands abs_ns_e6 as the noise (the S983 column-swap class at the seam).
# Detector: tests/compound/run_part_measures.sh (C): fx-f2's abs_ns_e6 and noise_e6 differ on every handed measured row, so the noise digest differs from ks_ref.py handed (the count alone would not see it).
SAB_ID="S2905-fill-hands-abs-as-noise"
SAB_FILE="src/gen/memfn_sites.c"
SAB_SUITES="compound"
SAB_DESC='(f) the fill hands abs_ns_e6 as the noise (the S983 column-swap class at the seam)'
SAB_DOC_FIGURE='MEASURED by lane s2a planted and reverted (docs/dev/lanes/s2a_report.md, the sabotage table); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2905.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                                          measured ? r->noise_e6 : 0 };'
SAB_AFTER='                                          measured ? strtoll(r->col[KS_MR_abs_ns_e6], NULL, 10) : 0 };   /* SABOTAGE S2905 */'
