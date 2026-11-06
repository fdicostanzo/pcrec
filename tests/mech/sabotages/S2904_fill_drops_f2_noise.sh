# S2904 — span_pick stage 2 unit S2a (lane s2a; docs/design/memfn/span_cards.md rev 1.1 §9 row (e);
# docs/spec/measures.md §2.2¶3a, §3.3¶1a, §4¶2a).
#
# Plant: (e) the fill hands every row UNMEASURED, dropping a format-2 set's parsed noise.
# Detector: tests/compound/run_part_measures.sh (C): fx-f2's MFMEAS MEASURED count is 0 (it must be > 0) and its noise digest differs from ks_ref.py handed.
SAB_ID="S2904-fill-drops-f2-noise"
SAB_FILE="src/gen/memfn_sites.c"
SAB_SUITES="compound"
SAB_DESC='(e) the fill hands every row UNMEASURED, dropping a format-2 set'"'"'s parsed noise'
SAB_DOC_FIGURE='MEASURED by lane s2a planted and reverted (docs/dev/lanes/s2a_report.md, the sabotage table); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2904.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        bool measured = r->noise_e6 != KS_MEAS_EMPTY;'
SAB_AFTER='        bool measured = false;   /* SABOTAGE S2904 */'
