# S2900 — span_pick stage 2 unit S2a (lane s2a; docs/design/memfn/span_cards.md rev 1.1 §9 row (a);
# docs/spec/measures.md §2.2¶3a, §3.3¶1a, §4¶2a).
#
# Plant: (a) the format-2 values digest skips noise_e6: two format-2 sets apart by one noise hash alike.
# Detector: every format-2 fixture's load (ks_ref.py, written from measures.md §3.3¶1a, digests the noise; the C recompute no longer matches the file's values_digest) and the pair check (fx-f2-noise must digest apart from fx-f2).
SAB_ID="S2900-meas-f2-digest-skips-noise"
SAB_FILE="src/core/ks_measures.c"
SAB_SUITES="knowledge"
SAB_DESC='(a) the format-2 values digest skips noise_e6: two format-2 sets apart by one noise hash alike'
SAB_DOC_FIGURE='MEASURED by lane s2a planted and reverted (docs/dev/lanes/s2a_report.md, the sabotage table); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2900.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        h = pcrec_ks_fnv1a(h, b, noise ? 18 : 10);'
SAB_AFTER='        h = pcrec_ks_fnv1a(h, b, 10);   /* SABOTAGE S2900 */'
