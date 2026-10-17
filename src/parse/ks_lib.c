/* src/parse/ks_lib.c — [KNOW-SRC] the `lib` kind's row
 * (docs/design/measure_sets.md rev 3 §9.1, §9.5): a `.rxt` source's
 * `lib "path"` reference, resolved over the naming file's own directory and
 * then each `--lib-path`/`-I` directory — the SAME `-I` list the analysis
 * row reads, which is why it is a row of the one resolver and not a third
 * loop.
 *
 * RESOLVE-ONLY: no item, no stamp, no probe, no listing. The file it finds
 * is a library that the `.rxt` reader parses as a source (rxt_source.c's
 * closure walk). Its two divergences from the analysis row are columns,
 * kept for zero movers and listed rather than copied: `entry_match =
 * probe-exists` (a stat of the joined path, so a case-insensitive
 * filesystem can answer `Defs.rxt` for `defs.rxt` — finding F12) and
 * `join = clean` (no doubled '/'). */

#include "core/ksrc.h"

const KsKind pcrec_ks_lib = {
    .kind          = "lib",
    .suffix        = ".rxt",
    .stops         = KS_STOP_BIT(KS_AT_SRCDIR) | KS_STOP_BIT(KS_AT_DIRS),
    .flag_classify = KS_CLS_FILE_ONLY,
    .list_classify = KS_CLS_FILE_ONLY,
    .revs          = false,
    .s2_mismatch   = KS_S2_REFUSE,
    .s2_multi      = KS_S2_REFUSE,
    .entry_match   = KS_ENTRY_PROBE_EXISTS,
    .join          = KS_JOIN_CLEAN,
    .bare_view     = KS_VIEW_CANONICAL,
    .r4            = KS_R4_EXEMPT,
    .list_surface  = KS_LIST_NONE,
    .noun          = "lib",
    .nouns         = "libs",
    .item_noun     = "library",
};
