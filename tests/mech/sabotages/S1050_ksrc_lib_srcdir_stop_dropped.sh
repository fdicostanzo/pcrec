# S1050 — [KNOW-SRC] K1 (docs/design/measure_sets.md rev 3 §9.1, §9.5): THE
# `lib` ROW LOSES ITS SOURCE-DIRECTORY STOP (src/parse/ks_lib.c). A `lib
# "path"` reference resolves against THE FILE THAT WROTE IT first, then each
# `--lib-path` (rxt_format's rule, and the only rule under which a source
# naming its library is portable). With the stop gone the one resolver
# looks only in the `-I`/`--lib-path` directories, so every library beside
# its source stops resolving.
#
# Detector: tests/rxtsource/ (every fixture whose `lib` names a sibling file
# refuses with "names no readable file").
SAB_ID="S1050-ksrc-lib-srcdir-stop-dropped"
SAB_FILE="src/parse/ks_lib.c"
SAB_SUITES="rxtsource"
SAB_DESC="the lib kind's row drops KS_AT_SRCDIR from its stops: a lib \"path\" no longer resolves against the naming file's own directory, only the --lib-path list"
SAB_DOC_FIGURE="rxtsource red on its lib-resolving fixtures. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1050."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    .stops         = KS_STOP_BIT(KS_AT_SRCDIR) | KS_STOP_BIT(KS_AT_DIRS),'
SAB_AFTER='    .stops         = KS_STOP_BIT(KS_AT_DIRS),   /* SABOTAGE S1050 */'
