/* tests/clskit/clskit_driver.c — [CLS-TREE] S1's driver for the kit in
 * src/gen/clskit.c: it EMITS the kit's matchers for a population, as C the
 * differential then compiles, and DUMPS the kit's sectionings and table
 * choices for crosscheck.py to compare against the study.
 *
 *   clskit_driver emit POPFILE OUTDIR    checker .c compile units (variants packed
 *                                        by bytes), plus a census of every form emitted
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
/* Emitted-text budget per compile unit. gcc's -O1 time on these units is
 * ~0.8 s/MB on the Mac's gcc-16 and about the same per CPU-second on gcc-15;
 * on CI's gcc-13.3 it is ~10x that (a 1.2 s-on-the-Mac unit exceeded the
 * 10 s GENCPU in run 36704000526, while the same units RUN only ~1.7-2x
 * slower there), so a unit is sized for the SLOWEST supported compiler: 0.25 MB
 * is ~0.2-0.4 s here (content-dependent, worst measured 0.6 s at 0.39 MB) and ~2-4 s on
 * gcc-13, inside D45's budget with margin. */
static const long long CHUNK_BYTES = 250000;
/* Run-cost budget per unit: checker variants (each is checked over every code
 * point, ~4 ms) plus 2 per composition (the law pass). MEASURED on ubuntubudu
 * solo, 2026-09-29: ~4.1 ms per variant, so 500 is ~2 s against the 10 s
 * GENRUNTIMEOUT -- the headroom is what a full-suite -j load eats; the byte
 * budget alone let a unit of 118 small sets (1550 variants) run 6.4 s. */
static const long long CHUNK_VARS = 500;
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
static int nset, ngroup;   /* ngroup: populations.py's CHUNK markers = atomic groups */
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
        if (!strncmp(line, "CHUNK", 5)) { ngroup++; continue; }
        if (!strncmp(line, "COMP ", 5)) {
            Comp *c = &comps[ncomp++];
            sscanf(line + 5, "%d %d %d %7s", &c->c, &c->a, &c->b, c->op);
            continue;
        }
        if (strncmp(line, "SET ", 4)) continue;
        Set *s = &sets[nset++];
        int off = 0;
        sscanf(line + 4, "%d %15s %63s %n", &s->idx, s->kind, s->name, &off);
        s->chunk = ngroup - 1;
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

/* One checker VARIANT: its function text and its VARS row. `law` marks the
 * variants (K4, P3) the composition law reads, which must share a compile
 * unit with the COMPS rows that name them; every other variant is free to
 * land in any unit that also carries its set's reference arrays. */
typedef struct {
    int pos, law, atom;   /* pos: index into sets[] */
    StrBuf text, var;
} Item;

/* A set's reference arrays and its SETS row, written once and copied into
 * every unit that holds one of the set's variants. */
typedef struct { StrBuf ref, row; } SetText;

static Item *items;
static int nitem, capitem;
static SetText settext[MAXSET];
static StrBuf grpcomps[MAXSET];   /* per group: its COMPS rows */
static int grpncomps[MAXSET];
static int grphascomps[MAXSET];

/* Start a variant of set `pos` and return it; the caller emits into ->text. */
static Item *add_item(int pos, const char *fn, const char *var)
{
    if (nitem == capitem) items = realloc(items, sizeof *items * (size_t)(capitem = capitem ? capitem * 2 : 256));
    Item *it = &items[nitem++];
    memset(it, 0, sizeof *it);
    it->pos = pos;
    it->law = grphascomps[sets[pos].chunk] && (!strcmp(var, "K4") || !strcmp(var, "P3"));
    pcrec_sb_printf(&it->var, "    { %d, \"%s\", %s },\n", sets[pos].idx, var, fn);
    return it;
}

/* Emit group `ch`: each set's reference arrays, every variant as its own
 * item, and the group's COMPS rows. Groups are the unit populations.py
 * guarantees a composition's operands and result share; pack_chunks() below
 * decides which compile unit each item lands in. */
static void emit_group(int ch)
{
    Arena a = { NULL, NULL };

    for (int q = 0; q < ncomp; q++)
        if (sets[comps[q].c].chunk == ch) {
            pcrec_sb_printf(&grpcomps[ch], "    { %d, %d, %d, '%c' },\n", comps[q].c, comps[q].a, comps[q].b, comps[q].op[0]);
            grpncomps[ch]++;
            grphascomps[ch] = 1;
        }
    for (int i = 0; i < nset; i++) {
        Set *s = &sets[i];
        StrBuf *c = &settext[i].ref;
        if (s->chunk != ch) continue;
        /* the reference: plain arrays, written here and nowhere else */
        pcrec_sb_printf(c, "static const unsigned s%d_lo[%d] = {", s->idx, s->n ? s->n : 1);
        for (int t = 0; t < s->n; t++) pcrec_sb_printf(c, "%s%uu,", t % 12 ? " " : "\n    ", s->iv[t].lo);
        if (!s->n) pcrec_sb_puts(c, "0");
        pcrec_sb_printf(c, "\n};\nstatic const unsigned s%d_hi[%d] = {", s->idx, s->n ? s->n : 1);
        for (int t = 0; t < s->n; t++) pcrec_sb_printf(c, "%s%uu,", t % 12 ? " " : "\n    ", s->iv[t].hi);
        if (!s->n) pcrec_sb_puts(c, "0");
        pcrec_sb_puts(c, "\n};\n");
        pcrec_sb_printf(&settext[i].row, "    { %d, \"%s\", s%d_lo, s%d_hi, %d },\n", s->idx, s->name, s->idx, s->idx, s->n);

        for (size_t l = 0; l < sizeof LAMS / sizeof LAMS[0]; l++) {
            ClsKit k;
            char fn[96], var[32];
            pcrec_clskit_partition(&a, s->iv, s->n, LAMS[l], 0, &k);
            snprintf(fn, sizeof fn, "s%d_k%u", s->idx, LAMS[l]);
            snprintf(var, sizeof var, "K%u", LAMS[l]);
            pcrec_clskit_emit_kit(&add_item(i, fn, var)->text, fn, &k);
            census_kit(&k);
        }
        for (size_t o = 0; o < sizeof ONLY / sizeof ONLY[0]; o++) {
            ClsKit k;
            char fn[96], var[32];
            pcrec_clskit_partition(&a, s->iv, s->n, 4, 1u << ONLY[o], &k);
            snprintf(fn, sizeof fn, "s%d_only%zu", s->idx, o);
            snprintf(var, sizeof var, "only-%s", pcrec_clskit_leaf_name(ONLY[o]));
            pcrec_clskit_emit_kit(&add_item(i, fn, var)->text, fn, &k);
            census_kit(&k);
        }
        for (ClsForm f = CLSF_PAGE3; f <= CLSF_BITMAP1; f++) {
            char fn[96];
            if (f != CLSF_PAGE3 && pcrec_clskit_whole_bytes(&a, f, s->iv, s->n) > WHOLE_CAP) {
                skipped[f]++;
                continue;
            }
            snprintf(fn, sizeof fn, "s%d_%s", s->idx, pcrec_clskit_form_name(f));
            pcrec_clskit_emit_whole(&add_item(i, fn, pcrec_clskit_form_name(f))->text, &a, fn, f, s->iv, s->n);
            form_census[f]++;
        }
        if (s->atom_index >= 0) {
            char fn[96];
            snprintf(fn, sizeof fn, "s%d_ATOM", s->idx);
            Item *it = add_item(i, fn, "ATOM");
            it->atom = 1;
            pcrec_clskit_emit_atom(&it->text, fn, "atom_tab", &atoms, s->atom_index);
            form_census[CLSF_ATOM]++;
        }
    }
    pcrec_arena_free(&a);
}

/* One compile unit under construction: a set of items plus the COMPS rows of
 * the groups whose law variants it holds. */
typedef struct {
    int *it, nit;
    char in_set[MAXSET];
    int setorder[MAXSET], nset_in;
    int cgroup[MAXSET], ncg;
    int atom;
    long long bytes, vars;
} Pack;

/* The bytes a set's reference text adds to `p` (0 once it is already in). */
static long long ref_cost(const Pack *p, int pos)
{
    return p->in_set[pos] ? 0 : (long long)settext[pos].ref.len;
}

/* Put item `k` into `p`, with its set's reference arrays if they are new. */
static void pack_add(Pack *p, int k)
{
    Item *it = &items[k];
    p->bytes += ref_cost(p, it->pos) + (long long)it->text.len;
    if (!p->in_set[it->pos]) { p->in_set[it->pos] = 1; p->setorder[p->nset_in++] = it->pos; }
    p->it[p->nit++] = k;
    p->vars++;
    p->atom |= it->atom;
}

/* Write one compile unit. */
static void write_chunk(const char *outdir, int index, const Pack *p)
{
    StrBuf c = { 0 };
    char path[4096];
    int nc = 0;

    pcrec_sb_puts(&c, "#include <stdio.h>\n#include <string.h>\n\n");
    if (p->atom) pcrec_clskit_emit_atom_table(&c, "atom_tab", &atoms);
    for (int k = 0; k < p->nset_in; k++) pcrec_sb_puts(&c, settext[p->setorder[k]].ref.p);
    for (int k = 0; k < p->nit; k++) pcrec_sb_puts(&c, items[p->it[k]].text.p ? items[p->it[k]].text.p : "");
    pcrec_sb_puts(&c, "\ntypedef int (*fn_t)(unsigned);\n"
                      "static const struct { int set; const char *var; fn_t fn; } VARS[] = {\n");
    for (int k = 0; k < p->nit; k++) pcrec_sb_puts(&c, items[p->it[k]].var.p);
    pcrec_sb_puts(&c, "};\nstatic const struct { int idx; const char *name; const unsigned *lo, *hi; int n; } SETS[] = {\n");
    for (int k = 0; k < p->nset_in; k++) pcrec_sb_puts(&c, settext[p->setorder[k]].row.p);
    pcrec_sb_puts(&c, "};\n");
    pcrec_sb_puts(&c, "static const struct { int c, a, b; char op; } COMPS[] = {\n");
    for (int k = 0; k < p->ncg; k++) {
        pcrec_sb_puts(&c, grpcomps[p->cgroup[k]].p);
        nc += grpncomps[p->cgroup[k]];
    }
    if (!nc) pcrec_sb_puts(&c, "    { -1, -1, -1, 0 },\n");
    pcrec_sb_printf(&c, "};\nenum { NCOMP = %d };\n", nc);
    pcrec_sb_puts(&c, "#include \"checker_main.inc\"\n");

    snprintf(path, sizeof path, "%s/chunk_%03d.c", outdir, index);
    FILE *f = fopen(path, "w");
    if (!f) { perror(path); exit(2); }
    fwrite(c.p, 1, c.len, f);
    fclose(f);
    pcrec_sb_free(&c);
}

/* Emit every group, then pack its variants into compile units by their
 * emitted BYTES (and, second, by RUN COST -- CHUNK_VARS): gcc's time on a
 * unit follows the text it is handed, not the number of sets or intervals in
 * it, and follows it at a rate that depends on the gcc VERSION (~0.8 s/MB at
 * -O1 on the Mac's gcc-16; ~5-10x that on CI's gcc-13, see the budget note by
 * CHUNK_BYTES). The atomic part of a group is only its LAW bundle -- the K4
 * and P3 variants of every set in a group that has compositions, with the
 * group's COMPS rows, because the law compares a result's variant against its
 * operands' in one process. Every other variant of a set is checked against
 * that set's own reference alone, so it may land in any unit carrying the
 * set's reference arrays (copied into each). Returns the number of units. */
static int pack_chunks(const char *outdir, long long budget, long long vbudget)
{
    int nunit = 0;
    Pack p;
    int *done, *slot;

    for (int g = 0; g < ngroup; g++) emit_group(g);
    done = calloc((size_t)(nitem ? nitem : 1), sizeof *done);
    slot = malloc(sizeof *slot * (size_t)(nitem ? nitem : 1));
    memset(&p, 0, sizeof p);
    p.it = slot;
#define FLUSH() do { if (p.nit) { write_chunk(outdir, nunit++, &p); \
        memset(p.in_set, 0, sizeof p.in_set); p.nit = p.nset_in = p.ncg = p.atom = 0; p.bytes = p.vars = 0; } } while (0)
    for (int g = 0; g < ngroup; g++) {
        /* the law bundle first: all or nothing, so it is added as a whole */
        if (grphascomps[g]) {
            long long bytes = 0, vars = 2LL * grpncomps[g];
            char seen[MAXSET] = { 0 };
            for (int k = 0; k < nitem; k++)
                if (items[k].law && sets[items[k].pos].chunk == g) {
                    bytes += (long long)items[k].text.len;
                    if (!seen[items[k].pos]) { seen[items[k].pos] = 1; bytes += (long long)settext[items[k].pos].ref.len; }
                    vars++;
                }
            if (p.nit && (p.bytes + bytes > budget || p.vars + vars > vbudget)) FLUSH();
            for (int k = 0; k < nitem; k++)
                if (items[k].law && sets[items[k].pos].chunk == g) { pack_add(&p, k); done[k] = 1; }
            p.cgroup[p.ncg++] = g;
            p.vars += 2LL * grpncomps[g];
        }
        for (int k = 0; k < nitem; k++) {
            if (done[k] || sets[items[k].pos].chunk != g) continue;
            long long bytes = ref_cost(&p, items[k].pos) + (long long)items[k].text.len;
            if (p.nit && (p.bytes + bytes > budget || p.vars + 1 > vbudget)) FLUSH();
            pack_add(&p, k);
            done[k] = 1;
        }
    }
    FLUSH();
#undef FLUSH
    for (int k = 0; k < nitem; k++) { pcrec_sb_free(&items[k].text); pcrec_sb_free(&items[k].var); }
    for (int i = 0; i < nset; i++) { pcrec_sb_free(&settext[i].ref); pcrec_sb_free(&settext[i].row); }
    for (int g = 0; g < ngroup; g++) pcrec_sb_free(&grpcomps[g]);
    free(done);
    free(slot);
    return nunit;
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
    long long budget = argc > 4 ? atoll(argv[4]) : CHUNK_BYTES;
    int nunit = pack_chunks(argv[3], budget, argc > 5 ? atoll(argv[5]) : CHUNK_VARS);
    printf("CHUNKS %d SETS %d COMPS %d VARIANTS %d\n", nunit, nset, ncomp, nitem);
    for (int l = 0; l < CLSK_NLEAF; l++)
        printf("LEAF %s %lld\n", pcrec_clskit_leaf_name((ClsLeaf)l), leaf_census[l]);
    for (int f = 0; f < CLSF_NFORM; f++)
        printf("FORM %s %lld skipped=%lld\n", pcrec_clskit_form_name((ClsForm)f), form_census[f], skipped[f]);
    return 0;
}
