/* src/parse/ks_analysis.c — [KNOW-SRC] the ANALYSIS kind's row
 * (docs/design/measure_sets.md rev 3 §9.2, §9.5): the analysis object of
 * D162, resolved by `--analysis NAME`, the `analysis` config line and
 * `--list-analysis`, from the compiling file (S1), `-I DIR/<name>.rxt` (S2)
 * and the built-in store (S3).
 *
 * The row is a parse-layer TU because its file probe is the `.rxt` reader;
 * the kind-independent resolver it plugs into is `src/core/ksrc.c`. Its
 * include chain (`include`, the self-name `#include_next`, the terminal
 * `default`) is NOT here: that is this kind's own semantics and stays in
 * `rxt_find.c`, which asks the resolver for one link at a time. */

#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

#include "core/internal.h"
#include "core/ksrc.h"

/* Stop S2's file probe: `path` refused over PCREC_MAX_FIND_BUNDLE_BYTES
 * (never truncated), parsed, and its bundles counted; FOUND hands the parse
 * (an `RxtSource *`) to the caller, who frees it. */
static KsFile analysis_probe(const char *path, const char *name, void **doc,
                             size_t *nitems, KsErr *err)
{
    struct stat sb;
    pcrec_error perr = { 0 };
    RxtSource *src;
    bool named = false;
    size_t n = 0;
    if (stat(path, &sb) == 0 &&
        (unsigned long long)sb.st_size > PCREC_MAX_FIND_BUNDLE_BYTES) {
        snprintf(err->msg, sizeof err->msg, "%s: %llu bytes, over "
                 "PCREC_MAX_FIND_BUNDLE_BYTES (%llu): an analysis file is "
                 "refused, never truncated",
                 path, (unsigned long long)sb.st_size,
                 (unsigned long long)PCREC_MAX_FIND_BUNDLE_BYTES);
        return KS_FILE_ERROR;
    }
    src = pcrec_rxt_source_parse(path, &perr);
    if (!src) {
        snprintf(err->msg, sizeof err->msg, "%s", perr.msg);
        return KS_FILE_ERROR;
    }
    for (size_t i = 0; i < src->nrows; i++)
        if (src->rows[i].kind == RXT_DECL_ANALYSIS) {
            n++;
            if (!strcmp(src->rows[i].name, name)) named = true;
        }
    *nitems = n;
    if (n > 1 || !named) {
        pcrec_rxt_source_free(src);
        return n > 1 ? KS_FILE_MULTI : KS_FILE_OTHER;
    }
    *doc = src;
    return KS_FILE_FOUND;
}

const KsKind pcrec_ks_analysis = {
    .kind          = "analysis",
    .suffix        = ".rxt",
    .stops         = KS_STOP_BIT(KS_AT_S1) | KS_STOP_BIT(KS_AT_DIRS) |
                     KS_STOP_BIT(KS_AT_STORE),
    .flag_classify = KS_CLS_NAME_ONLY,
    .list_classify = KS_CLS_NAME_ELSE_FILE,
    .revs          = false,
    .s2_mismatch   = KS_S2_FALLTHROUGH_NOTE,
    .s2_multi      = KS_S2_REFUSE,
    .entry_match   = KS_ENTRY_EXACT,
    .join          = KS_JOIN_SLASH,
    .bare_view     = KS_VIEW_SHIPPED,
    .r4            = KS_R4_EXEMPT,
    .list_surface  = KS_LIST_CLI,
    .cli_flag      = "--analysis",
    .cfg_line      = "analysis",
    .list_flag     = "--list-analysis",
    .noun          = "analysis",
    .nouns         = "analyses",
    .item_noun     = "bundle",
    .item          = &pcrec_find_rows_role,
    .stamp         = &pcrec_find_rate_role,
    .probe         = analysis_probe,
};
