/* src/core/ksrc_kinds.c — [KNOW-SRC] THE KINDS TABLE: every knowledge kind's
 * row, assembled (docs/design/measure_sets.md rev 3 §9.2, §9.5). A declared
 * first-match table; [LIST-TABLES] lists it once that row opens.
 *
 * It lives at the LIBRARY tier and only libpcrec compiles it, so the kind-
 * independent parts (`ksrc.c`) stay free of every row's dependencies: the
 * analysis row brings the `.rxt` reader, and a tool that links the parts
 * alone (`pcrec-measure`, §7.1) brings its own one-row table instead of this
 * one. The rows are defined in their own TUs (src/parse/ks_analysis.c,
 * src/parse/ks_lib.c, src/core/ks_measures.c since [MEASURE-SET] M0);
 * `picks` and `evaluator-params` join when their steps build (§9.8). */

#include <string.h>

#include "core/internal.h"
#include "core/ks_measures.h"
#include "core/ksrc.h"

const KsKind *const pcrec_ks_kinds[] = { &pcrec_ks_analysis, &pcrec_ks_lib,
                                         &pcrec_ks_measures };

const KsKind *pcrec_ks_kind(const char *name)
{
    for (size_t i = 0; i < sizeof pcrec_ks_kinds / sizeof *pcrec_ks_kinds; i++)
        if (!strcmp(pcrec_ks_kinds[i]->kind, name)) return pcrec_ks_kinds[i];
    return NULL;
}
