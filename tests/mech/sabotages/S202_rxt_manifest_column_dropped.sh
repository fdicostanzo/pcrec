# S202 (S-C11) — [DD-13b.W1.1] the `encoding` column disappears from
# `--list-source`'s declared header while every row still carries its
# value, so the dump stops SAYING what it is still emitting.
#
# THE ROW IS ABOUT A DIFFERENTIAL THAT SILENTLY STOPS COMPARING. Both
# dumps in the C1 differential are new code by one author. A change that
# dropped a directive key from both emitters would leave the two dumps
# byte-identical to each other and the differential would go on passing
# while quietly covering one directive less — the check would be measuring
# a smaller thing and reporting the same green.
#
# SO THE DETECTOR IS THE FIELD MANIFEST AND NOTHING ELSE, and this plant is
# built to prove that. It touches the COLUMN LIST only: the rows still have
# fifteen fields with the same values, so leg A and leg B still agree byte
# for byte, the per-row field count still passes, and the diff has nothing
# to report. What fails is the manifest's comparison of the emitted header
# against its own pinned list of column names — the table contract's
# GENERATOR AGREEMENT rule, which exists so a producer and its checker
# cannot disagree in silence.
SAB_ID="S202-rxt-manifest-column-dropped"
SAB_FILE="src/parse/rxt_source.c"
SAB_SUITES="rxtsource"
SAB_DESC="the `encoding` name is removed from --list-source's column list, so the emitted header declares 14 columns while every data row still carries 15 fields; the rows are unchanged and only the manifest can see it"
SAB_COUNT=1
SAB_BEFORE='    "features_only", "encoding", "engine", "budget_steps", "budget_frames",'
SAB_AFTER='    "features_only", "engine", "budget_steps", "budget_frames",   /* SABOTAGE S202 */'
