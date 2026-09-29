/* tests/clskit/clskit_driver.c — [CLS-TREE] S1's driver for the kit in
 * src/gen/clskit.c: it EMITS the kit's matchers for a population, as C the
 * differential then compiles, and DUMPS the kit's sectionings and table
 * choices for crosscheck.py to compare against the study.
 *
 *   clskit_driver emit POPFILE OUTDIR    one checker .c per CHUNK, plus a
 *                                        census of every form emitted
 *   clskit_driver dump POPFILE           SEC / SEL / ATOMS lines
 *
 * THE REFERENCE IS NOT THE KIT'S. Each checker carries every set's interval
 * list as plain arrays written here, from the population file, and walks
 * them with a sequential pointer. No line of src/gen/clskit.c produces it,
 * so a kit bug cannot corrupt both sides (learnings.md §3).
 *
 * VARIANTS PER SET. `K` at λ 0/4/16/256 (4 is the table's), six
 * leaf-restricted sectionings (each allows one leaf form plus `ALL`, so
 * every leaf form is emitted over every set it fits rather than only where
 * the size search happens to pick it), and the whole-set forms `P3`, `P2`,
 * `B1`. `P2`/`B1` are emitted only where their table is at most
 * WHOLE_CAP bytes (a 139 KB bitmap per set would make the checkers
 * hundreds of MB of source); the census counts the skips so the population
 * that WAS checked is stated rather than implied. The atom form is emitted
 * for every byte set the shared table covers.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/internal.h"
#include "gen/clskit.h"

enum { MAXSET = 4096, MAXCOMP = 1024 };
static const long long WHOLE_CAP = 40000;
static const unsigned LAMS[] = { 0, 4, 16, 256 };

typedef struct {
    int idx;
    char kind[16], name[64];
    PcrecCpRange *iv;
    int n, chunk;
    int atom_index;
} Set;

typedef struct { int c, a, b; char op[8]; } Comp;

static Set sets[MAXSET];
static int nset, nchunk;
static Comp comps[MAXCOMP];
static int ncomp;

/* Read the population file into `sets`/`comps`. */
static void load(const char *path)
{
    FILE *f = fopen(path, "r");
    char *line = NULL;
    size_t cap = 0;
    if (!f) { perror(path); exit(2); }
    while (getline(&line, &cap, f) > 0) {
        if (!strncmp(line, "CHUNK", 5)) { nchunk++; continue; }
        if (!strncmp(line, "COMP ", 5)) {
            Comp *c = &comps[ncomp++];
            sscanf(line + 5, "%d %d %d %7s", &c->c, &c->a, &c->b, c->op);
            continue;
        }
        if (strncmp(line, "SET ", 4)) continue;
        Set *s = &sets[nset++];
        int off = 0;
        sscanf(line + 4, "%d %15s %63s %n", &s->idx, s->kind, s->name, &off);
        s->chunk = nchunk - 1;
        s->atom_index = -1;
        int cap_iv = 16;
        s->iv = malloc(sizeof *s->iv * (size_t)cap_iv);
        char *p = line + 4 + off;
        unsigned lo, hi;
        int used;
        while (sscanf(p, "%x:%x%n", &lo, &hi, &used) == 2) {
            if (s->n == cap_iv) s->iv = realloc(s->iv, sizeof *s->iv * (size_t)(cap_iv *= 2));
            s->iv[s->n++] = (PcrecCpRange){ lo, hi };
            p += used;
        }
    }
    free(line);
    fclose(f);
}

/* The shared atom table over the byte population: the largest prefix of
 * the byte sets whose partition fits (the study's N = 4/16/32 shape). */
static ClsAtomTable atoms;
static int atom_n;

static void build_atoms(Arena *a)
{
    const PcrecCpRange *sv[MAXSET];
    int nv[MAXSET], m = 0, who[MAXSET];
    for (int i = 0; i < nset; i++)
        if (!strcmp(sets[i].kind, "byte")) { who[m] = i; sv[m] = sets[i].iv; nv[m] = sets[i].n; m++; }
    for (atom_n = m; atom_n > 0; atom_n--)
        if (pcrec_clskit_atoms(a, sv, nv, atom_n, &atoms)) break;
    for (int k = 0; k < atom_n; k++) sets[who[k]].atom_index = k;
    printf("ATOMS byte_sets=%d shared=%d natoms=%d\n", m, atom_n, atom_n ? atoms.natoms : 0);
}

/* The leaf-restricted variants: one leaf form each (ALL is always added). */
static const ClsLeaf ONLY[] = { CLSK_RANGES, CLSK_MASK64, CLSK_CUBES, CLSK_BITMAP,
                                CLSK_PAGE64, CLSK_BSEARCH };

static long long leaf_census[CLSK_NLEAF], form_census[CLSF_NFORM], skipped[CLSF_NFORM];

/* Count one sectioning's leaves into the census. */
static void census_kit(const ClsKit *k)
{
    for (int s = 0; s < k->nsec; s++) leaf_census[k->sec[s].leaf]++;
    form_census[CLSF_KIT]++;
}

/* One variant: emit it into `c` and register it in the VARS table text. */
static void add_var(StrBuf *vars, int si, const char *fn, const char *var)
{
    pcrec_sb_printf(vars, "    { %d, \"%s\", %s },\n", si, var, fn);
}

/* Write one chunk's checker program. */
static void emit_chunk(const char *outdir, int ch)
{
    Arena a = { NULL, NULL };
    StrBuf c = { 0 }, vars = { 0 }, setsb = { 0 };
    char path[4096];
    int nin = 0;

    pcrec_sb_puts(&c, "#include <stdio.h>\n#include <string.h>\n\n");
    for (int i = 0; i < nset; i++)
        if (sets[i].chunk == ch && sets[i].atom_index >= 0) {
            pcrec_clskit_emit_atom_table(&c, "atom_tab", &atoms);
            break;
        }
    for (int i = 0; i < nset; i++) {
        Set *s = &sets[i];
        if (s->chunk != ch) continue;
        nin++;
        /* the reference: plain arrays, written here and nowhere else */
        pcrec_sb_printf(&c, "static const unsigned s%d_lo[%d] = {", s->idx, s->n ? s->n : 1);
        for (int t = 0; t < s->n; t++) pcrec_sb_printf(&c, "%s%uu,", t % 12 ? " " : "\n    ", s->iv[t].lo);
        if (!s->n) pcrec_sb_puts(&c, "0");
        pcrec_sb_printf(&c, "\n};\nstatic const unsigned s%d_hi[%d] = {", s->idx, s->n ? s->n : 1);
        for (int t = 0; t < s->n; t++) pcrec_sb_printf(&c, "%s%uu,", t % 12 ? " " : "\n    ", s->iv[t].hi);
        if (!s->n) pcrec_sb_puts(&c, "0");
        pcrec_sb_puts(&c, "\n};\n");
        pcrec_sb_printf(&setsb, "    { %d, \"%s\", s%d_lo, s%d_hi, %d },\n", s->idx, s->name, s->idx, s->idx, s->n);

        for (size_t l = 0; l < sizeof LAMS / sizeof LAMS[0]; l++) {
            ClsKit k;
            char fn[96], var[32];
            pcrec_clskit_partition(&a, s->iv, s->n, LAMS[l], 0, &k);
            snprintf(fn, sizeof fn, "s%d_k%u", s->idx, LAMS[l]);
            snprintf(var, sizeof var, "K%u", LAMS[l]);
            pcrec_clskit_emit_kit(&c, fn, &k);
            add_var(&vars, s->idx, fn, var);
            census_kit(&k);
        }
        for (size_t o = 0; o < sizeof ONLY / sizeof ONLY[0]; o++) {
            ClsKit k;
            char fn[96], var[32];
            pcrec_clskit_partition(&a, s->iv, s->n, 4, 1u << ONLY[o], &k);
            snprintf(fn, sizeof fn, "s%d_only%zu", s->idx, o);
            snprintf(var, sizeof var, "only-%s", pcrec_clskit_leaf_name(ONLY[o]));
            pcrec_clskit_emit_kit(&c, fn, &k);
            add_var(&vars, s->idx, fn, var);
            census_kit(&k);
        }
        for (ClsForm f = CLSF_PAGE3; f <= CLSF_BITMAP1; f++) {
            char fn[96];
            if (f != CLSF_PAGE3 && pcrec_clskit_whole_bytes(&a, f, s->iv, s->n) > WHOLE_CAP) {
                skipped[f]++;
                continue;
            }
            snprintf(fn, sizeof fn, "s%d_%s", s->idx, pcrec_clskit_form_name(f));
            pcrec_clskit_emit_whole(&c, &a, fn, f, s->iv, s->n);
            add_var(&vars, s->idx, fn, pcrec_clskit_form_name(f));
            form_census[f]++;
        }
        if (s->atom_index >= 0) {
            char fn[96];
            snprintf(fn, sizeof fn, "s%d_ATOM", s->idx);
            pcrec_clskit_emit_atom(&c, fn, "atom_tab", &atoms, s->atom_index);
            add_var(&vars, s->idx, fn, "ATOM");
            form_census[CLSF_ATOM]++;
        }
    }
    if (!nin) { pcrec_arena_free(&a); return; }

    pcrec_sb_puts(&c, "\ntypedef int (*fn_t)(unsigned);\n"
                      "static const struct { int set; const char *var; fn_t fn; } VARS[] = {\n");
    pcrec_sb_puts(&c, vars.p ? vars.p : "");
    pcrec_sb_puts(&c, "};\nstatic const struct { int idx; const char *name; const unsigned *lo, *hi; int n; } SETS[] = {\n");
    pcrec_sb_puts(&c, setsb.p);
    pcrec_sb_puts(&c, "};\n");
    /* compositions whose result lives in this chunk */
    pcrec_sb_puts(&c, "static const struct { int c, a, b; char op; } COMPS[] = {\n");
    int nc = 0;
    for (int q = 0; q < ncomp; q++)
        if (sets[comps[q].c].chunk == ch) {
            pcrec_sb_printf(&c, "    { %d, %d, %d, '%c' },\n", comps[q].c, comps[q].a, comps[q].b, comps[q].op[0]);
            nc++;
        }
    if (!nc) pcrec_sb_puts(&c, "    { -1, -1, -1, 0 },\n");
    pcrec_sb_printf(&c, "};\nenum { NCOMP = %d };\n", nc);
    pcrec_sb_puts(&c, "#include \"checker_main.inc\"\n");

    snprintf(path, sizeof path, "%s/chunk_%03d.c", outdir, ch);
    FILE *f = fopen(path, "w");
    if (!f) { perror(path); exit(2); }
    fwrite(c.p, 1, c.len, f);
    fclose(f);
    pcrec_sb_free(&c);
    pcrec_sb_free(&vars);
    pcrec_sb_free(&setsb);
    pcrec_arena_free(&a);
}

/* Print the sectionings (every λ) and the table's choices (every position,
 * no deny and each single row deny) for crosscheck.py. */
static void dump(void)
{
    int nrows;
    const ClsRow *rows = pcrec_clskit_rows(&nrows);
    for (int r = 0; r < nrows; r++)
        printf("ROW %d %s %s deny=%d | %s\n", r, rows[r].name,
               pcrec_clskit_form_name(rows[r].form), (int)rows[r].deny, rows[r].pred_desc);
    for (int i = 0; i < nset; i++) {
        Set *s = &sets[i];
        Arena a = { NULL, NULL };
        for (size_t l = 0; l < sizeof LAMS / sizeof LAMS[0]; l++) {
            ClsKit k;
            pcrec_clskit_partition(&a, s->iv, s->n, LAMS[l], 0, &k);
            printf("SEC %d %u %lld", s->idx, LAMS[l], k.bytes);
            for (int t = 0; t < k.nsec; t++)
                printf(" %d:%s", k.sec[t].first, pcrec_clskit_leaf_name(k.sec[t].leaf));
            printf("\n");
        }
        printf("WHOLE %d %lld %lld %lld\n", s->idx,
               pcrec_clskit_whole_bytes(&a, CLSF_PAGE3, s->iv, s->n),
               pcrec_clskit_whole_bytes(&a, CLSF_PAGE2, s->iv, s->n),
               pcrec_clskit_whole_bytes(&a, CLSF_BITMAP1, s->iv, s->n));
        ClsKit kk;
        pcrec_clskit_partition(&a, s->iv, s->n, pcrec_clskit_kit_lambda(), 0, &kk);
        for (int tune = -2; tune <= 2; tune++)
            for (int d = 0; d < CLSD_NDENY; d++) {
                ClsSelectIn in = { tune, d ? 1u << d : 0, d == 0 ? NULL : &kk };
                ClsChoice ch;
                pcrec_clskit_select(&a, s->iv, s->n, &in, &ch);
                printf("SEL %d %d %d %s %s\n", s->idx, tune, d, rows[ch.row].name,
                       pcrec_clskit_form_name(ch.form));
            }
        pcrec_arena_free(&a);
    }
}

int main(int argc, char **argv)
{
    Arena a = { NULL, NULL };
    if (argc < 3) { fprintf(stderr, "usage: clskit_driver emit|dump POPFILE [OUTDIR]\n"); return 2; }
    load(argv[2]);
    build_atoms(&a);
    if (!strcmp(argv[1], "dump")) { dump(); return 0; }
    if (strcmp(argv[1], "emit") || argc < 4) { fprintf(stderr, "clskit_driver: bad mode\n"); return 2; }
    for (int ch = 0; ch < nchunk; ch++) emit_chunk(argv[3], ch);
    printf("CHUNKS %d SETS %d COMPS %d\n", nchunk, nset, ncomp);
    for (int l = 0; l < CLSK_NLEAF; l++)
        printf("LEAF %s %lld\n", pcrec_clskit_leaf_name((ClsLeaf)l), leaf_census[l]);
    for (int f = 0; f < CLSF_NFORM; f++)
        printf("FORM %s %lld skipped=%lld\n", pcrec_clskit_form_name((ClsForm)f), form_census[f], skipped[f]);
    return 0;
}
