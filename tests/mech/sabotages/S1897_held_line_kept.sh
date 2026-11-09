# S1897 ([XARCH-DEV] U3, lane u3d27; D27 region suite F1) -- the target headers' render takes out each held mark but KEEPS the part's header line after it, so the line stays inside the region (the header is then included twice, once ahead of the region and once inside it). match_api.md §6.3.10¶15.
# Detector (arm memfntargets): tests/memfn/run_targets.sh section 4b's F1 checks (includes-inside, twice).
SAB_ID="S1897-held-line-kept"
SAB_FILE="src/gen/memfn_stamps.c"
SAB_SUITES="memfntargets"
SAB_DESC="the render drops a held mark but keeps the header line it held, inside the region"
SAB_DOC_FIGURE="memfntargets: run_targets.sh's F1 checks read red. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1897."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        rest = eol + 1;'
SAB_AFTER='        rest = h + strlen(held);   /* SABOTAGE S1897 */'
