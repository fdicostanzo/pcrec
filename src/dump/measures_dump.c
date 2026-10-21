/* src/dump/measures_dump.c — [MEASURE-SET] M0 `--list-measurements`
 * (docs/spec/measures.md §6; docs/design/measure_sets.md §5, §9.2 part 6):
 * the sets index, and one set's CANONICAL view (a loadable set: §9.6's
 * round trip) or DECODED view (the loaded document field by field, R5's
 * subject). The views are the kind row's writers; this file resolves the
 * set and renders the index. The per-target, `readers` and `stale` views
 * are M1's and later (§10.1). */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"
#include "core/ks_measures.h"
#include "core/ksrc.h"

static int meas_sb_write(void *ctx, const char *p, size_t n)
{
    StrBuf *sb = ctx;
    for (size_t i = 0; i < n; i++) pcrec_sb_putc(sb, p[i]);
    return 0;
}

/* The index: one row per committed set, in the store's order (§5.1's
 * columns that exist at M0). */
static void list_index(StrBuf *sb)
{
    static const char *const cols[] = {
        "id", "rev", "class", "box", "tier", "composite", "method",
        "default_for", "rows", "null_rows", "values_digest", "source",
    };
    pcrec_sb_puts(sb, "# pcrec measurement sets (spec: docs/spec/measures.md)\n"
                      "#section sets\n#");
    for (size_t i = 0; i < sizeof cols / sizeof *cols; i++)
        pcrec_sb_printf(sb, "%s%s", i ? "\t" : "", cols[i]);
    pcrec_sb_putc(sb, '\n');
    for (size_t i = 0; i < pcrec_meas_store_count(); i++) {
        const KsMeasSet *s = pcrec_meas_store_set(i, NULL, NULL);
        char rev[16], rows[24], nulls[24], hex[17];
        size_t nn = 0;
        for (size_t r = 0; r < s->nrows; r++) nn += s->rows[r].value_e6 == KS_MEAS_EMPTY;
        snprintf(rev, sizeof rev, "%u", s->rev);
        snprintf(rows, sizeof rows, "%zu", s->nrows);
        snprintf(nulls, sizeof nulls, "%zu", nn);
        pcrec_ks_meas_hex(s->digest, hex);
        {
            const char *cells[] = {
                s->hdr[KS_MH_ID], rev, s->hdr[KS_MH_CLASS], s->hdr[KS_MH_BOX],
                s->hdr[KS_MH_TIER], s->hdr[KS_MH_COMPOSITE], s->hdr[KS_MH_METHOD],
                pcrec_meas_default_for(s), rows, nulls, hex, "store",
            };
            pcrec_sb_row(sb, cells, sizeof cells / sizeof *cells);
        }
    }
}

char *pcrec_meas_list(const char *ref, const char *const *dirs, const char *view,
                      pcrec_error *err)
{
    StrBuf sb = { 0 };
    Arena a = { 0 };
    PcrecMeasHit hit;
    KsErr kerr = { { 0 } };
    KsOut out = { meas_sb_write, &sb };
    int rc;
    memset(err, 0, sizeof *err);
    if (!ref) {
        if (view) {
            snprintf(err->msg, sizeof err->msg,
                     "--view applies to --list-measurements=X, one set");
            return NULL;
        }
        list_index(&sb);
        return pcrec_sb_take(&sb);
    }
    if (pcrec_meas_find(&a, ref, dirs, &hit, err) != 0) {
        pcrec_arena_free(&a);
        return NULL;
    }
    rc = pcrec_ks_view_write(&pcrec_ks_measures, view ? view : "canonical", &out,
                             hit.set, &kerr);
    pcrec_arena_free(&a);
    if (rc != 0) {
        snprintf(err->msg, sizeof err->msg, "%s", kerr.msg);
        pcrec_sb_free(&sb);
        return NULL;
    }
    return pcrec_sb_take(&sb);
}
