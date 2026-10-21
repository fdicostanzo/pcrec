/* tests/knowledge/meas_store_check.c OUTDIR — [MEASURE-SET] M0 the embedded
 * store against itself (docs/design/measure_sets.md §8.3's secondary checks):
 * for every set built into libpcrec, writes its embedded TEXT to
 * OUTDIR/<id>@<rev>.text (the runner compares it with the committed file,
 * byte for byte), the DECODED view of its PRE-PARSE to OUTDIR/<name>.pre and
 * the decoded view of a FRESH parse of the embedded text to OUTDIR/<name>.fresh
 * (equal iff the pre-parse is what the one reader reads from that text), and
 * prints one line per set: `<name> TAB <digest> TAB <rows>`.
 *
 * Both decodes run the one C reader, so this catches a stale or mis-generated
 * `.inc` and nothing about the reader itself; the reader's interpretation is
 * R5's (ks_ref.py). */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

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

int main(int argc, char **argv)
{
    KsAlloc al = { chk_alloc, NULL };
    int bad = 0;
    if (argc != 2) {
        fprintf(stderr, "usage: meas_store_check OUTDIR\n");
        return 2;
    }
    for (size_t i = 0; i < pcrec_meas_store_count(); i++) {
        const char *text, *name = pcrec_meas_store_name(i);
        size_t len;
        const KsMeasSet *pre = pcrec_meas_store_set(i, &text, &len), *fresh;
        char path[4096], hex[17];
        FILE *f;
        KsErr err;
        snprintf(path, sizeof path, "%s/%s.text", argv[1], name);
        if (!(f = fopen(path, "w")) || fwrite(text, 1, len, f) != len) {
            perror(path);
            return 2;
        }
        fclose(f);
        if (pcrec_ks_meas_parse(&al, text, len, name, &fresh, &err)) {
            fprintf(stderr, "meas_store_check: the embedded text of %s does not "
                    "parse: %s\n", name, err.msg);
            bad = 1;
            continue;
        }
        if (decode_to(argv[1], name, "pre", pre) || decode_to(argv[1], name, "fresh", fresh))
            bad = 1;
        pcrec_ks_meas_hex(pre->digest, hex);
        printf("%s\t%s\t%zu\n", name, hex, pre->nrows);
    }
    return bad;
}
