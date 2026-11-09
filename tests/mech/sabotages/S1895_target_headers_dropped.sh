# S1895 ([XARCH-DEV] U3, lane u3crit; review 2026-11-08-r5-xarch X-2) -- the target headers' render writes nothing: a compound part's own `#include <string.h>` is then the first one, inside the shell's region, so a gcc consumer that #includes a v3 compound artifact and then calls a fortified memcpy fails to compile ("inlining failed ... target specific option mismatch").
# Detector (arm memfntargets): tests/memfn/run_targets.sh section 4b's `fortify` consumer cell (measured red on the pre-fix build).
SAB_ID="S1895-target-headers-dropped"
SAB_FILE="src/gen/memfn_targets.c"
SAB_SUITES="memfntargets"
SAB_DESC="the target headers ahead of the region are never written, so a compound part's <string.h> is first read inside the region and a consumer's fortified memcpy after the artifact fails to compile"
SAB_DOC_FIGURE="memfntargets: run_targets.sh's consumer fortify cell reads red. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1895."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return string_h && !cx->job->string_h ? "#include <string.h>\n" : "";'
SAB_AFTER='    return "";   /* SABOTAGE S1895 */'
