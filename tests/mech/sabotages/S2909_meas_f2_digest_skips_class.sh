# S2909 — span_pick stage 2 unit S2a (lane s2a; docs/design/memfn/span_cards.md rev 1.1 §9 row (s);
# docs/spec/measures.md §2.2¶3a, §3.3¶1a, §4¶2a).
#
# Plant: (s) the format-2 digest skips the header's class.
# Detector: ks_ref.py folds class (measures.md §3.3¶1a): every format-2 fixture refuses to load, and fx-f2-class, apart from fx-f2 by class alone, no longer digests apart in C.
SAB_ID="S2909-meas-f2-digest-skips-class"
SAB_FILE="src/core/ks_measures.c"
SAB_SUITES="knowledge"
SAB_DESC='(s) the format-2 digest skips the header'"'"'s class'
SAB_DOC_FIGURE='MEASURED by lane s2a planted and reverted (docs/dev/lanes/s2a_report.md, the sabotage table); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2909.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    h = pcrec_ks_fnv1a(h, set->hdr[KS_MH_CLASS], strlen(set->hdr[KS_MH_CLASS]) + 1);'
SAB_AFTER='    (void)set;   /* SABOTAGE S2909 */'
