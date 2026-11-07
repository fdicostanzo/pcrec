/* tests/knowledge/meas_store_check.c OUTDIR — [MEASURE-SET] M0 the embedded
 * store against itself (docs/design/measure_sets.md §8.3's secondary checks):
 * for every set built into libpcrec, writes its embedded TEXT to
 * OUTDIR/<id>@<rev>.text (the runner compares it with the committed file
 * stripped of its `cells` rows by the runner's own awk, byte for byte: the
 * embed is cell-less, measures.md §8¶2), the DECODED view of its PRE-PARSE to OUTDIR/<name>.pre and
 * the decoded view of a FRESH parse of the embedded text to OUTDIR/<name>.fresh
 * (equal iff the pre-parse is what the one reader reads from that text), and
 * prints one line per set: `<name> TAB <digest> TAB <rows>`.
 *
 * THE RAW-ROW COMPARE (span_cards.md §4.5, [rev1.1 KSGEN]): the decoded view
 * shows only what a view prints, and a format-1 view prints no parsed noise,
 * so a ksgen that left KsMeasRow.noise_e6 out of the pre-parse (C's zero
 * where a fresh parse holds KS_MEAS_EMPTY) decoded identically. Every set is
 * therefore ALSO compared field by field, pre-parse against fresh parse: the
 * set's format, rev, composite, digest and counts, every KsMeasRow field (the
 * noise as an integer) and every table cell. A difference prints and fails.
 *
 * Built with -DMSC_TABLE='"PATH"', it checks a FIXTURE store instead: PATH is
 * a `scripts/ksgen.c measures` output, and the set texts are the FILE
 * arguments after OUTDIR, in the table's order (tests/knowledge/mfixtures.py's
 * format-2 `store/`, so the format-2 pre-parse is exercised before any
 * committed set is format 2).
 *
 * Both sides run the one C reader, so this catches a stale or mis-generated
 * `.inc` and nothing about the reader itself; the reader's interpretation is
 * R5's (ks_ref.py).
 *
 * It also holds KS_MEAS_MAX (src/core/ks_measures.h) and the kit's
 * MF_MEASURE_MAX (memfn.h) to one value: the two homes of one bound, neither
 * of which may read the other (span_cards.md §4.1), so a drifted copy fails
 * this file's build. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/internal.h"
#include "../../memfn/include/memfn.h"

_Static_assert(KS_MEAS_MAX == MF_MEASURE_MAX,
               "KS_MEAS_MAX (ks_measures.h) and MF_MEASURE_MAX (memfn.h) are one bound");

#ifdef MSC_TABLE
#include MSC_TABLE
#endif

static void *chk_alloc(void *ctx, size_t n)
{
    void *p = calloc(1, n ? n : 1);
    (void)ctx;
    if (!p) { perror("calloc"); exit(2); }
    return p;
}

static int chk_write(void *ctx, const char *p, size_t n)
{
    return fwrite(p, 1, n, ctx) != n;
}

/* Writes `set`'s decoded view to DIR/NAME.SUFFIX. */
static int decode_to(const char *dir, const char *name, const char *suffix,
                     const KsMeasSet *set)
{
    char path[4096];
    FILE *f;
    KsErr err;
    KsOut o;
    int rc;
    snprintf(path, sizeof path, "%s/%s.%s", dir, name, suffix);
    if (!(f = fopen(path, "w"))) { perror(path); return -1; }
    o = (KsOut){ chk_write, f };
    rc = pcrec_ks_view_write(&pcrec_ks_measures, "decoded", &o, set, &err);
    fclose(f);
    if (rc) fprintf(stderr, "meas_store_check: %s: %s\n", name, err.msg);
    return rc;
}

/* 0 iff table `what` holds the same cells in `a` and `b` (`w` wide). */
static int tab_same(const char *name, const char *what, const KsMeasTab *a,
                    const KsMeasTab *b, size_t w)
{
    if (a->nrows != b->nrows) {
        fprintf(stderr, "meas_store_check: %s: %s: %zu rows pre-parsed, %zu fresh\n",
                name, what, a->nrows, b->nrows);
        return 1;
    }
    for (size_t i = 0; i < a->nrows * w; i++)
        if (strcmp(a->cells[i], b->cells[i])) {
            fprintf(stderr, "meas_store_check: %s: %s cell %zu: '%s' pre-parsed, '%s' fresh\n",
                    name, what, i, a->cells[i], b->cells[i]);
            return 1;
        }
    return 0;
}

/* The raw-row compare: 0 iff every field of `pre` equals `fresh`'s. */
static int raw_same(const char *name, const KsMeasSet *pre, const KsMeasSet *fresh)
{
    int bad = 0;
    if (pre->format != fresh->format || pre->rev != fresh->rev ||
        pre->composite != fresh->composite || pre->digest != fresh->digest ||
        pre->nrows != fresh->nrows) {
        fprintf(stderr, "meas_store_check: %s: set fields differ (format %u/%u, rev %u/%u, "
                "composite %u/%u, rows %zu/%zu)\n", name, pre->format, fresh->format,
                pre->rev, fresh->rev, pre->composite, fresh->composite, pre->nrows, fresh->nrows);
        return 1;
    }
    for (int h = 0; h < KS_MEAS_NHDR; h++)
        if (strcmp(pre->hdr[h], fresh->hdr[h])) {
            fprintf(stderr, "meas_store_check: %s: header %d differs\n", name, h);
            bad = 1;
        }
    for (size_t r = 0; r < pre->nrows; r++) {
        const KsMeasRow *p = &pre->rows[r], *f = &fresh->rows[r];
        for (size_t j = 0; j < KS_MEAS_NROWCOL; j++)
            if (strcmp(p->col[j], f->col[j])) {
                fprintf(stderr, "meas_store_check: %s: row %zu column %zu differs\n", name, r, j);
                bad = 1;
            }
        if (p->value_e6 != f->value_e6 || p->unit_code != f->unit_code ||
            p->status_code != f->status_code || p->noise_e6 != f->noise_e6) {
            fprintf(stderr, "meas_store_check: %s: row %s: value_e6 %lld/%lld unit %u/%u "
                    "status %u/%u noise_e6 %lld/%lld (pre-parsed/fresh)\n", name,
                    p->col[KS_MR_key], (long long)p->value_e6, (long long)f->value_e6,
                    p->unit_code, f->unit_code, p->status_code, f->status_code,
                    (long long)p->noise_e6, (long long)f->noise_e6);
            bad = 1;
        }
    }
    return bad | tab_same(name, "cards", &pre->cards, &fresh->cards, KS_MEAS_NCARD) |
           tab_same(name, "cells", &pre->cells, &fresh->cells, pcrec_ks_meas_cell_w(pre)) |
           tab_same(name, "members", &pre->members, &fresh->members, KS_MEAS_NMEMBER);
}

/* Checks one set: its text written out, a fresh parse decoded beside the
 * pre-parse's decode, the raw-row compare, and its line printed. */
static int check_one(const char *dir, const char *name, const KsMeasSet *pre,
                     const char *text, size_t len)
{
    KsAlloc al = { chk_alloc, NULL };
    const KsMeasSet *fresh;
    char path[4096], hex[17];
    FILE *f;
    KsErr err;
    snprintf(path, sizeof path, "%s/%s.text", dir, name);
    if (!(f = fopen(path, "w")) || fwrite(text, 1, len, f) != len) {
        perror(path);
        exit(2);
    }
    fclose(f);
    if (pcrec_ks_meas_parse(&al, text, len, name, &fresh, &err)) {
        fprintf(stderr, "meas_store_check: the embedded text of %s does not "
                "parse: %s\n", name, err.msg);
        return 1;
    }
    if (decode_to(dir, name, "pre", pre) || decode_to(dir, name, "fresh", fresh) ||
        raw_same(name, pre, fresh))
        return 1;
    pcrec_ks_meas_hex(pre->digest, hex);
    printf("%s\t%s\t%zu\n", name, hex, pre->nrows);
    return 0;
}

#ifdef MSC_TABLE
/* The fixture store: entry i of the generated table against FILE i. */
static int check_all(int argc, char **argv)
{
    size_t n = sizeof pcrec_meas_store_tbl / sizeof *pcrec_meas_store_tbl;
    int bad = 0;
    (void)pcrec_meas_defaults;
    if ((size_t)argc - 2 != n) {
        fprintf(stderr, "meas_store_check: the table has %zu sets, %d files given\n", n, argc - 2);
        return 2;
    }
    for (size_t i = 0; i < n; i++) {
        FILE *f = fopen(argv[2 + i], "rb");
        static char buf[1 << 20];
        size_t len;
        if (!f) { perror(argv[2 + i]); return 2; }
        len = fread(buf, 1, sizeof buf, f);
        fclose(f);
        bad |= check_one(argv[1], pcrec_meas_store_tbl[i].name, pcrec_meas_store_tbl[i].set,
                         buf, len);
    }
    return bad;
}
#else
/* The store built into libpcrec. */
static int check_all(int argc, char **argv)
{
    int bad = 0;
    if (argc != 2) {
        fprintf(stderr, "usage: meas_store_check OUTDIR\n");
        return 2;
    }
    for (size_t i = 0; i < pcrec_meas_store_count(); i++) {
        const char *text;
        size_t len;
        const KsMeasSet *pre = pcrec_meas_store_set(i, &text, &len);
        bad |= check_one(argv[1], pcrec_meas_store_name(i), pre, text, len);
    }
    return bad;
}
#endif

int main(int argc, char **argv)
{
    if (argc < 2) {
        fprintf(stderr, "usage: meas_store_check OUTDIR [FILE...]\n");
        return 2;
    }
    return check_all(argc, argv);
}
