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
 *   compound_drive derive OUTDIR < CASES
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
 * (`<id>.plain.c`, self-contained), P as an ordinary artifact at prefix
 * `nb` whose emission request bounds it to one attempt (`<id>.nb.c`, B4's
 * general bound) and the split client's two parts at
 * prefix PREFIX: F = P bounded to one attempt (`<id>.f.c`) and Q = the
 * given text (`<id>.q.c`; B2 derives it instead), both compiled guards-off
 * as compound.md §A.1's table states them. ARMs: `--enc utf8`,
 * `--utf-check`, `--guard none|align` (the PARENT's options; the parts
 * clear them). Each line of stdout is `id<TAB>part<TAB>ok|refused<TAB>msg`.
 *
 * `selfcheck` (B1): `pcrec_comp_part_check` over parts that state every
 * field and parts that leave one unstated or inconsistent, each expected
 * verdict asserted; and `pcrec_compile_part` refusing an unstated part.
 * (B4) the row table's self-check on the shipped `compound_rows[]` and on
 * planted faults, and `compound_place[]`'s rows for split's parts.
 * (B2) the registry's attempt-scope column: every row stating it, by name,
 * and `pcrec_ast_crosses_attempts` over a node carrying such a row and one
 * that does not.
 *
 * `derive` (B2, compound.md §B.1): CASES is `id<TAB>enc<TAB>P-hex<TAB>TQ-hex|-`
 * per line, TQ the twin's own derivation of Q (`-`: the twin says never or
 * declines). For each it compiles Q AS A PART with the split derivation
 * (`<id>.q.c`, prefix `rq`, engine AUTO so a VM-routed Q still compiles for
 * the comparison) and, where given, the twin's Q text as a plain artifact
 * (`<id>.tq.c`, prefix `tq`), both guards-off at `--features all`. Each line
 * of stdout is `id<TAB>ok|declined|refused<TAB>killed<TAB>killed_g<TAB>
 * pruned<TAB>kept_never<TAB>never<TAB>has_g<TAB>msg<TAB>p_ok`, the
 * derivation's own report and whether P compiles plainly at all.
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
    PcrecEmitIn in = { .req = req, .bound = PCREC_PB_UNSTATED };
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
    { CG_IDENTITY },
};
static const CompPart split_q = {
    "q", &pcrec_derive_none, SPLIT_GUARDS_OFF_SET, SPLIT_GUARDS_OFF_CLEAR,
    PCREC_PE_DFA, PCREC_PB_NONE, PCREC_PART_NEED_SEARCH, { CG_IDENTITY },
};

/* Writes one part (or the plain artifact) of pattern `pat`. */
static void drive_part(const char *dir, const char *id, const char *tag,
                       const char *pat, const pcrec_options *o,
                       const CompPart *part, int *ioerr)
{
    pcrec_output out;
    pcrec_error err;
    int rc = part ? pcrec_compile_part(pat, o, part, NULL, &out, &err)
                  : pcrec_compile(pat, o, &out, &err);
    printf("%s\t%s\t%s\t%s\n", id, tag, rc ? "refused" : "ok", rc ? err.msg : "-");
    if (rc) return;
    char name[512];
    snprintf(name, sizeof name, "%s.%s.c", id, tag);
    if (put_file(dir, name, out.c_src)) *ioerr = 1;
    pcrec_output_free(&out);
}

/* Writes pattern `pat` as an ORDINARY artifact (prefix `nb`, no part mode)
 * whose emission request bounds its search to one attempt (B4's soft item,
 * compound.md §A.5: the bound is a request field, part mode only its first
 * reader), into OUTDIR/<id>.nb.c. */
static void drive_bounded(const char *dir, const char *id, const char *pat,
                          const pcrec_options *parent, int *ioerr)
{
    pcrec_options o = *parent;
    o.prefix = "nb";
    o.header_name = NULL;
    const PcrecEmitIn in = { .bound = PCREC_PB_ONE_ATTEMPT };
    pcrec_output out;
    pcrec_error err;
    int rc = pcrec_compile_driver(pat, &o, &out, &err, NULL, NULL, NULL, NULL,
                                  NULL, &in);
    printf("%s\tnb\t%s\t%s\n", id, rc ? "refused" : "ok", rc ? err.msg : "-");
    if (rc) return;
    char name[512];
    snprintf(name, sizeof name, "%.200s.nb.c", id);
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
        drive_bounded(dir, line, p, &parent, &ioerr);
        drive_part(dir, line, "f", p, &parent, &f, &ioerr);
        if (q) drive_part(dir, line, "q", q, &parent, &split_q, &ioerr);
        free(p);
        free(q);
    }
    return ioerr ? 2 : 0;
}

/* The `derive` subcommand (B2). */
static int drive_derive(int argc, char **argv)
{
    if (argc != 1) return 2;
    const char *dir = argv[0];
    const CompPart cmp_q = {
        "q", &pcrec_derive_split_q_row, SPLIT_GUARDS_OFF_SET, SPLIT_GUARDS_OFF_CLEAR,
        PCREC_PE_AUTO, PCREC_PB_NONE, PCREC_PART_NEED_SEARCH, { CG_IDENTITY },
    };
    char line[1 << 16];
    int ioerr = 0;
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\r\n")] = 0;
        char *f[4] = { line, NULL, NULL, NULL };
        for (int i = 1; i < 4; i++) {
            f[i] = strchr(f[i - 1], '\t');
            if (!f[i]) break;
            *f[i]++ = 0;
        }
        if (!f[3]) continue;
        char *p = unhex(f[2]), *tq = strcmp(f[3], "-") ? unhex(f[3]) : NULL;
        if (!p) { fprintf(stderr, "compound_drive: bad hex\n"); return 2; }
        pcrec_options o;
        pcrec_default_options(&o);
        o.features = "all";
        if (!strcmp(f[1], "utf8")) o.encoding = PCREC_ENC_UTF8;
        o.prefix = "rq";
        PcrecDeriveReport rep;
        memset(&rep, 0, sizeof rep);
        pcrec_output out;
        pcrec_error err;
        /* Does P compile at all: a part refusal only counts as P's when the
         * plain compile refuses too. */
        int p_ok = pcrec_compile(p, &o, &out, &err) == 0;
        if (p_ok) pcrec_output_free(&out);
        int rc = pcrec_compile_part(p, &o, &cmp_q, &rep, &out, &err);
        printf("%s\t%s\t%d\t%d\t%d\t%d\t%d\t%d\t%s\t%d\n", f[0],
               !rc ? "ok" : rep.decline ? "declined" : "refused", rep.killed,
               rep.killed_g, rep.pruned_arms, rep.kept_never, rep.never, rep.has_g,
               rc ? err.msg : "-", p_ok);
        char name[512];
        if (!rc) {
            snprintf(name, sizeof name, "%.200s.q.c", f[0]);
            if (put_file(dir, name, out.c_src)) ioerr = 1;
            pcrec_output_free(&out);
        }
        if (tq) {
            o.prefix = "tq";
            o.flags |= SPLIT_GUARDS_OFF_SET;
            if (pcrec_compile(tq, &o, &out, &err) == 0) {
                snprintf(name, sizeof name, "%.200s.tq.c", f[0]);
                if (put_file(dir, name, out.c_src)) ioerr = 1;
                pcrec_output_free(&out);
            }
        }
        free(p);
        free(tq);
    }
    return ioerr ? 2 : 0;
}

/* The `selfcheck` subcommand (B1): every unstated or inconsistent field is
 * refused by the table-build self-check, the two split parts pass it, and
 * the part compile refuses an unstated part rather than compiling it. */
static int drive_selfcheck(void)
{
    CompPart bad[9];
    const char *what[9];
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
    BAD(bad[n].groups.kind = CG_UNSTATED, "groups unstated");
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
    int rc = pcrec_compile_part("abc", &o, &bad[0], NULL, &out, &err);
    printf("%s\tcompile of an unstated part\t%s\n", rc ? "refused" : "COMPILED",
           rc ? err.msg : "-");
    if (!rc) { fails++; pcrec_output_free(&out); }

    /* B4: the row table's self-check holds on the shipped table, and refuses
     * each planted fault: an empty admission, a CC_PRE conjunct after a
     * CC_POST one, a repeated id, a part that is an in-Job row
     * (compound_place row 3), a combinator operand of the wrong entry type,
     * an unstated group map. */
    {
        const char *t = pcrec_compound_tables_check();
        printf("%s\tthe shipped compound_rows[]\t%s\n", t ? "REFUSED" : "accepted", t ? t : "-");
        if (t) fails++;
        const CompRow *row0 = pcrec_compound_row(0);
        if (!row0 || pcrec_compound_row(1)) {
            printf("FAIL\tthe table is not exactly one row\n");
            fails++;
        } else {
            CompConj cj[8];
            CompPart pt[2];
            CompRow r;
            int nc = row0->nconj < 8 ? row0->nconj : 8;
#define PLANT(edit, label)                                                   \
            do {                                                             \
                memcpy(cj, row0->conj, (size_t)nc * sizeof *cj);             \
                memcpy(pt, row0->parts, 2 * sizeof *pt);                     \
                r = *row0; r.conj = cj; r.parts = pt;                        \
                edit;                                                        \
                const char *w = pcrec_compound_rows_check(&r, 1);            \
                printf("%s\t%s\t%s\n", w ? "refused" : "ACCEPTED", label,   \
                       w ? w : "-");                                         \
                if (!w) fails++;                                             \
            } while (0)
            PLANT(r.nconj = 0, "an empty admission");
            PLANT((cj[0].phase = CC_POST), "a CC_PRE conjunct after a CC_POST one");
            PLANT((cj[1].id = cj[0].id), "two conjuncts sharing an id");
            PLANT((pt[0].derive = &pcrec_derive_none, pt[0].flags_set = 0,
                   pt[0].flags_clear = 0, pt[0].engine = PCREC_PE_AUTO,
                   pt[0].bound = PCREC_PB_NONE),
                  "a part placed on compound_place row 3 (an in-Job row)");
            PLANT((pt[0].bound = PCREC_PB_NONE), "a first-nonzero operand of the wrong entry type");
            PLANT((pt[1].groups.kind = CG_UNSTATED), "an unstated group map");
#undef PLANT
            int p0 = pcrec_compound_place(&row0->parts[0]), p1 = pcrec_compound_place(&row0->parts[1]);
            printf("%s\tsplit's parts place on rows %d (f) and %d (q)\n",
                   p0 == 2 && p1 == 1 ? "ok" : "FAIL", p0, p1);
            if (p0 != 2 || p1 != 1) fails++;
        }
    }

    /* B2: the attempt-scope column, read off the registry, and the predicate
     * that reads it off a node's row. */
    const RegRow *xa = NULL, *plain_row = NULL;
    int nxa = 0;
    for (int k = 0; k < RK_COUNT; k++) {
        size_t nr;
        const RegRow *rows = pcrec_registry((RegKind)k, &nr);
        for (size_t i = 0; rows && i < nr; i++) {
            if (rows[i].flags & RF_CROSSES_ATTEMPTS) {
                printf("column\t%s\t%s\n", rows[i].syntax ? rows[i].syntax : "?",
                       rows[i].module ? rows[i].module : "?");
                nxa++;
                xa = &rows[i];
            } else if (!plain_row) {
                plain_row = &rows[i];
            }
        }
    }
    if (nxa < 1) { printf("FAIL\tno row states the attempt-scope column\n"); fails++; }
    if (xa && plain_row) {
        Ast leaf, cat;
        memset(&leaf, 0, sizeof leaf);
        memset(&cat, 0, sizeof cat);
        leaf.k = A_EMPTY;
        cat.k = A_CAT; cat.l = &leaf; cat.r = &leaf;
        leaf.reg = plain_row;
        bool off = pcrec_ast_crosses_attempts(&cat);
        leaf.reg = xa;
        bool on = pcrec_ast_crosses_attempts(&cat);
        printf("%s\tcrosses_attempts reads the column (off=%d on=%d)\n",
               !off && on ? "ok" : "FAIL", off, on);
        if (off || !on) fails++;
    }
    return fails ? 1 : 0;
}

int main(int argc, char **argv)
{
    if (argc >= 2 && !strcmp(argv[1], "entries")) return drive_entries(argc - 2, argv + 2);
    if (argc >= 2 && !strcmp(argv[1], "parts")) return drive_parts(argc - 2, argv + 2);
    if (argc == 2 && !strcmp(argv[1], "selfcheck")) return drive_selfcheck();
    if (argc >= 2 && !strcmp(argv[1], "derive")) return drive_derive(argc - 2, argv + 2);
    fprintf(stderr, "usage: compound_drive entries OUTDIR [--enc utf8] [--utf-check] < PATTERNS\n"
                    "       compound_drive parts OUTDIR PREFIX [ARM...] < WITNESSES\n"
                    "       compound_drive selfcheck\n"
                    "       compound_drive derive OUTDIR < CASES\n");
    return 2;
}
