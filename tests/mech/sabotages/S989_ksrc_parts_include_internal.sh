# S989 — [KNOW-SRC] K0 (docs/design/measure_sets.md rev 3 §8.5, §9.2): THE
# KIND-INDEPENDENT PARTS PICK UP THE COMPILER'S TYPES (src/core/ksrc.c
# includes core/internal.h). Nothing in the library notices — it compiles
# with -Ilib like every other TU — but the parts' dependency rule is what
# lets `pcrec-measure` (§7.1) link them without the `.rxt` parser, `Arena`
# and `PcrecSb`.
#
# Detector: tests/core/ksrc_deps_check.sh (run by run_core_tests.sh): (a)
# the quoted include lines are core/ksrc.h only, (b) ksrc.c compiles with
# -Isrc alone and calls nothing `pcrec_`.
SAB_ID="S989-ksrc-parts-include-internal"
SAB_FILE="src/core/ksrc.c"
SAB_SUITES="core"
SAB_DESC="src/core/ksrc.c includes core/internal.h: the dependency-free parts now drag in the compiler's header (and through it lib/pcrec.h), the edge §9.2 keeps out so a parts-only tool links nothing else of src/"
SAB_DOC_FIGURE="core red on ksrc_deps_check (a) the include scan and (b) the -Isrc-alone compile. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S989."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='#include "core/ksrc.h"'
SAB_AFTER='#include "core/internal.h"   /* SABOTAGE S989 */
#include "core/ksrc.h"'
