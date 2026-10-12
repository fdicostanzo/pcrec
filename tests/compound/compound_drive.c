/* tests/compound/compound_drive.c — [COMPOUND] the internal driver behind
 * tests/compound/run_compound_unit.sh (docs/design/compound.md §F, B0).
 *
 * It links `build/libpcrec.a` and includes `src/core/internal.h`, because what
 * it drives is INTERNAL: no `pcrec_options` field and no CLI flag carries an
 * entry request, so the only way to ask for one is the driver-tier input
 * `PcrecEmitIn` through `pcrec_compile_driver`.
 *
 *   compound_drive entries OUTDIR [--enc utf8] [--utf-check] < PATTERNS
 *   compound_drive parts OUTDIR PREFIX [ARM...] < WITNESSES
 *   compound_drive selfcheck
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
 * `parts` (B1, compound.md §A.5): WITNESSES is `id<TAB>P-hex<TAB>Q-hex|-`
 * per line. For each it writes the plain artifact of P at prefix `pp`
 * (`<id>.plain.c`, self-contained) and the split client's two parts at
 * prefix PREFIX: F = P bounded to one attempt (`<id>.f.c`) and Q = the
 * given text (`<id>.q.c`; B2 derives it instead), both compiled guards-off
 * as compound.md §A.1's table states them. ARMs: `--enc utf8`,
 * `--utf-check`, `--guard none|align` (the PARENT's options; the parts
 * clear them). Each line of stdout is `id<TAB>part<TAB>ok|refused<TAB>msg`.
 *
 * `selfcheck` (B1): `pcrec_comp_part_check` over parts that state every
 * field and parts that leave one unstated or inconsistent, each expected
 * verdict asserted; and `pcrec_compile_part` refusing an unstated part.
 *
 * Exit 0 unless the driver itself breaks (a refusal is a row, not an error;
 * `selfcheck` exits 1 on a wrong verdict); 2 on bad usage or I/O. */
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
    PcrecEmitIn in = { req, NULL, PCREC_PB_UNSTATED };
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

/* The split client's two parts (compound.md §A.1's table): F is the
 * pattern bounded to one attempt, Q the derived pattern; both DFA, both
 * guards-off, the controller's prologue owning the guard and the check. */
#define SPLIT_GUARDS_OFF_SET   PCREC_NO_STARTPOS_GUARD
#define SPLIT_GUARDS_OFF_CLEAR (PCREC_FORCE_UTF_CHECK | PCREC_FORCE_STARTPOS_ALIGN)
static const CompPart split_f = {
    "f", &pcrec_derive_none, SPLIT_GUARDS_OFF_SET, SPLIT_GUARDS_OFF_CLEAR,
    PCREC_PE_DFA, PCREC_PB_ONE_ATTEMPT,
    PCREC_PART_NEED_SEARCH | PCREC_PART_NEED_NEXT_POS | PCREC_PART_NEED_VALID_UPTO,
};
static const CompPart split_q = {
    "q", &pcrec_derive_none, SPLIT_GUARDS_OFF_SET, SPLIT_GUARDS_OFF_CLEAR,
    PCREC_PE_DFA, PCREC_PB_NONE, PCREC_PART_NEED_SEARCH,
};

/* Writes one part (or the plain artifact) of pattern `pat`. */
static void drive_part(const char *dir, const char *id, const char *tag,
                       const char *pat, const pcrec_options *o,
                       const CompPart *part, int *ioerr)
{
    pcrec_output out;
    pcrec_error err;
    int rc = part ? pcrec_compile_part(pat, o, part, &out, &err)
                  : pcrec_compile(pat, o, &out, &err);
    printf("%s\t%s\t%s\t%s\n", id, tag, rc ? "refused" : "ok", rc ? err.msg : "-");
    if (rc) return;
    char name[512];
    snprintf(name, sizeof name, "%s.%s.c", id, tag);
    if (put_file(dir, name, out.c_src)) *ioerr = 1;
    pcrec_output_free(&out);
}

/* The `parts` subcommand (B1). */
static int drive_parts(int argc, char **argv)
{
    if (argc < 2) return 2;
    const char *dir = argv[0];
    pcrec_options parent;
    pcrec_default_options(&parent);
    parent.prefix = argv[1];
    parent.features = "all";
    for (int i = 2; i < argc; i++) {
        if (!strcmp(argv[i], "--enc") && i + 1 < argc && !strcmp(argv[i + 1], "utf8")) {
            parent.encoding = PCREC_ENC_UTF8; i++;
        } else if (!strcmp(argv[i], "--utf-check")) {
            parent.flags |= PCREC_FORCE_UTF_CHECK;
        } else if (!strcmp(argv[i], "--guard") && i + 1 < argc) {
            if (!strcmp(argv[i + 1], "none")) parent.flags |= PCREC_NO_STARTPOS_GUARD;
            else if (!strcmp(argv[i + 1], "align")) parent.flags |= PCREC_FORCE_STARTPOS_ALIGN;
            else return 2;
            i++;
        } else {
            fprintf(stderr, "compound_drive: unknown option '%s'\n", argv[i]);
            return 2;
        }
    }
    pcrec_options plain = parent;
    plain.prefix = "pp";
    /* The controller reads F's subject validator only under the parent's
     * `-futf-check` (compound.md §A.4's edge), so that is F's need. */
    CompPart f = split_f;
    if (!pcrec_opt_has(&parent, PCREC_FORCE_UTF_CHECK))
        f.need &= ~PCREC_PART_NEED_VALID_UPTO;
    char line[1 << 16];
    int ioerr = 0;
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\r\n")] = 0;
        char *f1 = strchr(line, '\t');
        if (!f1) continue;
        *f1++ = 0;
        char *f2 = strchr(f1, '\t');
        if (!f2) continue;
        *f2++ = 0;
        char *p = unhex(f1), *q = strcmp(f2, "-") ? unhex(f2) : NULL;
        if (!p || (strcmp(f2, "-") && !q)) { fprintf(stderr, "compound_drive: bad hex\n"); return 2; }
        drive_part(dir, line, "plain", p, &plain, NULL, &ioerr);
        drive_part(dir, line, "f", p, &parent, &f, &ioerr);
        if (q) drive_part(dir, line, "q", q, &parent, &split_q, &ioerr);
        free(p);
        free(q);
    }
    return ioerr ? 2 : 0;
}

/* The `selfcheck` subcommand (B1): every unstated or inconsistent field is
 * refused by the table-build self-check, the two split parts pass it, and
 * the part compile refuses an unstated part rather than compiling it. */
static int drive_selfcheck(void)
{
    CompPart bad[8];
    const char *what[8];
    int n = 0;
#define BAD(field_edit, label) \
    do { bad[n] = split_f; field_edit; what[n++] = (label); } while (0)
    BAD(bad[n].engine = PCREC_PE_UNSTATED, "engine unstated");
    BAD(bad[n].bound = PCREC_PB_UNSTATED, "bound unstated");
    BAD(bad[n].derive = NULL, "derive unstated");
    BAD(bad[n].flags_set |= PCREC_FORCE_UTF_CHECK, "a flag set and cleared");
    BAD(bad[n].need = PCREC_PART_NEED_NEXT_POS, "need without search");
    BAD(bad[n].role = "", "empty role");
    BAD(bad[n].role = "abcd", "role over 3");
    BAD(bad[n].role = "F", "role not [a-z0-9]");
#undef BAD
    int fails = 0;
    for (int i = 0; i < n; i++) {
        const char *why = pcrec_comp_part_check(&bad[i]);
        printf("%s\t%s\t%s\n", why ? "refused" : "ACCEPTED", what[i], why ? why : "-");
        if (!why) fails++;
    }
    const CompPart *good[2] = { &split_f, &split_q };
    for (int i = 0; i < 2; i++) {
        const char *why = pcrec_comp_part_check(good[i]);
        printf("%s\tsplit part %s\t%s\n", why ? "REFUSED" : "accepted", good[i]->role,
               why ? why : "-");
        if (why) fails++;
    }
    pcrec_options o;
    pcrec_default_options(&o);
    pcrec_output out;
    pcrec_error err;
    int rc = pcrec_compile_part("abc", &o, &bad[0], &out, &err);
    printf("%s\tcompile of an unstated part\t%s\n", rc ? "refused" : "COMPILED",
           rc ? err.msg : "-");
    if (!rc) { fails++; pcrec_output_free(&out); }
    return fails ? 1 : 0;
}

int main(int argc, char **argv)
{
    if (argc >= 2 && !strcmp(argv[1], "entries")) return drive_entries(argc - 2, argv + 2);
    if (argc >= 2 && !strcmp(argv[1], "parts")) return drive_parts(argc - 2, argv + 2);
    if (argc == 2 && !strcmp(argv[1], "selfcheck")) return drive_selfcheck();
    fprintf(stderr, "usage: compound_drive entries OUTDIR [--enc utf8] [--utf-check] < PATTERNS\n"
                    "       compound_drive parts OUTDIR PREFIX [ARM...] < WITNESSES\n"
                    "       compound_drive selfcheck\n");
    return 2;
}
