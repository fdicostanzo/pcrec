/* tests/findings/findings_probe.c — reads the findings seam's DATA out of the
 * shipped library for tests/findings/run_findings_tests.sh, which judges it
 * against sources this program does not share ([FINDINGS] B1).
 *
 *   findings_probe names              the store's bundle names, one per line,
 *                                     from the embedded TEXT's own index
 *   findings_probe text NAME          bundle NAME's embedded text, raw bytes
 *   findings_probe normalize          stdin: lines of 256 counts; stdout: the
 *                                     library's normalization of each (256 ppm
 *                                     on one line), or "error N"
 *   findings_probe table              the PRE-PARSED table, one line per block
 *   findings_probe reparse            the same shape, from a fresh parse of the
 *                                     embedded text through the library's own
 *                                     reader (buffer mode) — the agreement
 *                                     check diffs the two
 *   findings_probe default-digest     the default's byte-rate digest, as the
 *                                     library computes it
 *
 * A block line is `bundle kind line nserves serve;serve;… ROWS`, each serve
 * `query|encs|via`; ROWS is `c0,c1,…,c255` for a `freq` block and
 * `U+HHHH:count,…` (ascending) for a `cpfreq` block ([FINDINGS] B5). */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

static void block_line(const char *bundle, const char *kind, size_t line,
                       size_t nserves, const char *const *q,
                       const char *const *e, const char *const *v,
                       const unsigned long long *counts,
                       const PcrecFindCp *cps, size_t ncps)
{
    printf("%s %s %zu %zu ", bundle, kind, line, nserves);
    for (size_t j = 0; j < nserves; j++)
        printf("%s%s|%s|%s", j ? ";" : "", q[j], e[j], v[j]);
    printf(" ");
    for (int b = 0; counts && b < 256; b++)
        printf("%s%llu", b ? "," : "", counts[b]);
    for (size_t j = 0; j < ncps; j++)
        printf("%sU+%04lX:%llu", j ? "," : "", (unsigned long)cps[j].cp,
               cps[j].count);
    printf("\n");
}

int main(int argc, char **argv)
{
    size_t n;
    const PcrecFindTblBlock *tbl = pcrec_find_store_blocks(&n);
    if (argc < 2) return 2;
    if (!strcmp(argv[1], "names")) {
        for (size_t k = 0; pcrec_find_store_name(k); k++)
            printf("%s\n", pcrec_find_store_name(k));
        return 0;
    }
    if (!strcmp(argv[1], "reparse")) {
        for (size_t k = 0; pcrec_find_store_name(k); k++) {
            const char *name = pcrec_find_store_name(k);
            size_t len;
            const char *text = pcrec_find_store_text(name, &len);
            pcrec_error err;
            RxtSource *src = pcrec_rxt_source_parse_buf(name, text, len, &err);
            if (!src) { printf("PARSE-FAILED %s: %s\n", name, err.msg); return 1; }
            for (size_t i = 0; i < src->nfblocks; i++) {
                const RxtFindBlock *fb = &src->fblocks[i];
                const char *q[16], *e[16], *v[16];
                for (size_t j = 0; j < fb->nserves && j < 16; j++) {
                    q[j] = fb->serves[j].query;
                    e[j] = fb->serves[j].encs;
                    v[j] = fb->serves[j].via;
                }
                block_line(fb->bundle, fb->kind, fb->line, fb->nserves, q, e, v,
                           fb->counts, fb->cps, fb->ncps);
            }
            pcrec_rxt_source_free(src);
        }
        return 0;
    }
    if (!strcmp(argv[1], "table")) {
        for (size_t i = 0; i < n; i++) {
            const char *q[16], *e[16], *v[16];
            for (size_t j = 0; j < tbl[i].nserves && j < 16; j++) {
                q[j] = tbl[i].serves[j].query;
                e[j] = tbl[i].serves[j].encs;
                v[j] = tbl[i].serves[j].via;
            }
            block_line(tbl[i].bundle, tbl[i].kind, tbl[i].line, tbl[i].nserves,
                       q, e, v, tbl[i].counts, tbl[i].cps, tbl[i].ncps);
        }
        return 0;
    }
    if (!strcmp(argv[1], "text") && argc > 2) {
        size_t len;
        const char *t = pcrec_find_store_text(argv[2], &len);
        if (!t) return 1;
        fwrite(t, 1, len, stdout);
        return 0;
    }
    if (!strcmp(argv[1], "normalize")) {
        unsigned long long c[256];
        uint32_t ppm[256];
        for (;;) {
            int b, r;
            for (b = 0; b < 256; b++) if (scanf("%llu", &c[b]) != 1) break;
            if (b == 0) return 0;
            if (b != 256) return 1;
            r = pcrec_find_normalize(c, ppm);
            if (r) { printf("error %d\n", r); continue; }
            for (b = 0; b < 256; b++) printf("%s%u", b ? " " : "", ppm[b]);
            printf("\n");
        }
    }
    if (!strcmp(argv[1], "default-digest")) {
        uint32_t ppm[256];
        for (size_t i = 0; i < n; i++)
            if (!strcmp(tbl[i].bundle, "default") &&
                pcrec_find_normalize(tbl[i].counts, ppm) == 0) {
                printf("%016llx\n",
                       (unsigned long long)pcrec_find_byte_rate_digest(ppm));
                return 0;
            }
        return 1;
    }
    return 2;
}
