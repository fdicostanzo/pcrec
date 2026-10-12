/* tests/compound/compound_drive.c — [COMPOUND] the internal driver behind
 * tests/compound/run_compound_unit.sh (docs/design/compound.md §F, B0).
 *
 * It links `build/libpcrec.a` and includes `src/core/internal.h`, because what
 * it drives is INTERNAL: no `pcrec_options` field and no CLI flag carries an
 * entry request, so the only way to ask for one is the driver-tier input
 * `PcrecEmitIn` through `pcrec_compile_driver`.
 *
 *   compound_drive entries OUTDIR [--enc utf8] [--utf-check] < PATTERNS
 *
 * PATTERNS is `id<TAB>hex-pattern` per line. For each pattern it writes the
 * plain artifact (`OUTDIR/<id>.plain.c/.h`, the default request) and one
 * artifact per request in `reqs[]` (`OUTDIR/<id>.<req>.c/.h`), all in the
 * paired-header form, at `--features all` and `-p rx`. Each line of stdout is
 * `id<TAB>req<TAB>ok|refused<TAB>exported<TAB>kept`, the last two the
 * REQUEST's own name lists (comma-joined entry suffixes), so the runner can
 * hold the artifact to what was asked without reading the closure the
 * compiler computed. A pattern the plain compile refuses prints one
 * `plain refused` line and is skipped.
 *
 * Exit 0 unless the driver itself breaks (a refusal is a row, not an error);
 * 2 on bad usage or I/O. */
#include "core/internal.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* The entry suffixes, in PcrecEntry order (public rows only). */
static const char *const entry_suffix[PCREC_ENTRY_PUBLIC_N] = {
    "search", "search_in", "match", "match_in", "match_caps",
    "match_caps_in", "next_pos", "valid_upto", "var_valid", "info", "main",
};

/* The requests B0 drives: the reduced public set, and the part-shaped
 * requests (nothing exported, the controller's needs kept). */
static const struct {
    const char *name;
    PcrecEntryReq req;
} reqs[] = {
    { "export-search", { PCREC_ENTRY_BIT(PCREC_ENTRY_SEARCH), 0 } },
    { "keep-search",   { 0, PCREC_ENTRY_BIT(PCREC_ENTRY_SEARCH) } },
    { "keep-f",        { 0, PCREC_ENTRY_BIT(PCREC_ENTRY_SEARCH) |
                            PCREC_ENTRY_BIT(PCREC_ENTRY_NEXT_POS) |
                            PCREC_ENTRY_BIT(PCREC_ENTRY_VALID_UPTO) } },
};

/* Writes `mask`'s entry suffixes comma-joined ("-" for none). */
static void put_names(unsigned mask)
{
    int n = 0;
    for (int e = 0; e < PCREC_ENTRY_PUBLIC_N; e++)
        if (mask & PCREC_ENTRY_BIT(e)) printf("%s%s", n++ ? "," : "", entry_suffix[e]);
    if (!n) putchar('-');
}

/* Decodes a hex string into a NUL-terminated buffer; NULL on a bad digit. */
static char *unhex(const char *h)
{
    size_t n = strlen(h);
    if (n % 2) return NULL;
    char *p = malloc(n / 2 + 1);
    if (!p) return NULL;
    for (size_t i = 0; i < n / 2; i++) {
        unsigned v;
        if (sscanf(h + 2 * i, "%2x", &v) != 1) { free(p); return NULL; }
        p[i] = (char)v;
    }
    p[n / 2] = 0;
    return p;
}

/* Writes `text` to OUTDIR/NAME. */
static int put_file(const char *dir, const char *name, const char *text)
{
    char path[4096];
    snprintf(path, sizeof path, "%s/%s", dir, name);
    FILE *f = fopen(path, "w");
    if (!f) return -1;
    fputs(text, f);
    return fclose(f);
}

/* Compiles `pat` under `req` (NULL: the default) into OUTDIR/<id>.<tag>.c/.h;
 * returns 0, or -1 on a refusal (message in `err`). */
static int compile_one(const char *dir, const char *id, const char *tag,
                       const char *pat, const pcrec_options *base,
                       const PcrecEntryReq *req, pcrec_error *err, int *ioerr)
{
    char hname[512], cname[512];
    snprintf(hname, sizeof hname, "%s.%s.h", id, tag);
    snprintf(cname, sizeof cname, "%s.%s.c", id, tag);
    pcrec_options o = *base;
    o.header_name = hname;
    PcrecEmitIn in = { req };
    pcrec_output out;
    if (pcrec_compile_driver(pat, &o, &out, err, NULL, NULL, NULL, NULL, NULL,
                             req ? &in : NULL) != 0)
        return -1;
    if (put_file(dir, cname, out.c_src) || put_file(dir, hname, out.h_src))
        *ioerr = 1;
    pcrec_output_free(&out);
    return 0;
}

/* The `entries` subcommand (B0). */
static int drive_entries(int argc, char **argv)
{
    if (argc < 1) return 2;
    const char *dir = argv[0];
    pcrec_options base;
    pcrec_default_options(&base);
    base.prefix = "rx";
    base.features = "all";
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--enc") && i + 1 < argc && !strcmp(argv[i + 1], "utf8")) {
            base.encoding = PCREC_ENC_UTF8; i++;
        } else if (!strcmp(argv[i], "--utf-check")) {
            base.flags |= PCREC_FORCE_UTF_CHECK;
        } else {
            fprintf(stderr, "compound_drive: unknown option '%s'\n", argv[i]);
            return 2;
        }
    }
    char line[1 << 16];
    int ioerr = 0;
    while (fgets(line, sizeof line, stdin)) {
        char *tab = strchr(line, '\t');
        if (!tab) continue;
        *tab = 0;
        char *hex = tab + 1;
        hex[strcspn(hex, "\r\n")] = 0;
        char *pat = unhex(hex);
        if (!pat) { fprintf(stderr, "compound_drive: bad hex for %s\n", line); return 2; }
        pcrec_error err;
        if (compile_one(dir, line, "plain", pat, &base, NULL, &err, &ioerr) != 0) {
            printf("%s\tplain\trefused\t-\t-\n", line);
            free(pat);
            continue;
        }
        for (size_t r = 0; r < sizeof reqs / sizeof *reqs; r++) {
            int rc = compile_one(dir, line, reqs[r].name, pat, &base, &reqs[r].req,
                                 &err, &ioerr);
            printf("%s\t%s\t%s\t", line, reqs[r].name, rc ? "refused" : "ok");
            put_names(reqs[r].req.exported);
            putchar('\t');
            put_names(reqs[r].req.kept);
            putchar('\n');
            if (rc) fprintf(stderr, "compound_drive: %s %s refused: %s\n",
                            line, reqs[r].name, err.msg);
        }
        free(pat);
    }
    return ioerr ? 2 : 0;
}

int main(int argc, char **argv)
{
    if (argc >= 2 && !strcmp(argv[1], "entries")) return drive_entries(argc - 2, argv + 2);
    fprintf(stderr, "usage: compound_drive entries OUTDIR [--enc utf8] [--utf-check] < PATTERNS\n");
    return 2;
}
