/* [START-SET] THE CENSUS'S FIRST-SET PROBE — a D77 instrument, NOT a
 * mechanism and never wired into the build (docs/design/startset.md §2).
 *
 * Computes, per pattern, the AST-level START SET: an OVER-approximation of
 * the bytes a NON-EMPTY match's first consumed byte can be, looking THROUGH
 * every zero-width node, plus whether the pattern can match EMPTY (in which
 * case no byte test is a necessary condition and the set is "all").
 *
 * It links libpcrec.a and reconstructs the shipped pipeline prefix exactly
 * as docs/dev/optloop/reqrunenc/reqrunenc_probe.c does (parse, altcls,
 * discharge_atomic, lower_enc -- that file's header says why all three), so
 * the tree is the emitters' tree and every A_CLASS is a BYTE class.
 *
 * SOUNDNESS DIRECTION: the set may only be too LARGE. Every node the walk
 * cannot see through (backreference, subroutine call, ${var}) widens to all
 * 256 bytes AND nullable -- possessify.c's own conservative arm for the same
 * kinds. Zero-width nodes (anchors, \b-family A_CTX, \G, \K, lookaround) are
 * EMPTY + nullable: they consume nothing, so the first consumed byte comes
 * from what follows, and dropping a gate only admits MORE strings. That is
 * the over-approximation, and the VM re-tests every gate at every attempt.
 *
 * Usage: printf 'id\\t<hex pattern>\\n' | fs_probe [-e utf8]
 * Out:   id status nullable popcount set_hex(64) cont_bytes
 */
#include "core/internal.h"
#include <setjmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct { uint8_t f[32]; int nullable; } Fs;

static Ctx *G;

static Fs fs_none(void) { Fs r; memset(r.f, 0, 32); r.nullable = 1; return r; }
static Fs fs_all(void)  { Fs r; memset(r.f, 0xff, 32); r.nullable = 1; return r; }
static void uni(uint8_t *d, const uint8_t *s) { for (int i = 0; i < 32; i++) d[i] |= s[i]; }

static Fs walk(const Ast *a);

/* l then r: FIRST(l) plus FIRST(r) when l can be empty. */
static Fs cat(Fs l, Fs r)
{
    Fs o = l;
    if (l.nullable) uni(o.f, r.f);
    o.nullable = l.nullable && r.nullable;
    return o;
}

static Fs walk(const Ast *a)
{
    /* A_CAT spines are as long as the pattern: walk them iteratively, right
     * operand recursively (pcrec's A_CAT is left-leaning). */
    if (a->k == A_CAT) {
        const Ast *t = a; int n = 0;
        while (t->k == A_CAT) { n++; t = t->l; }
        const Ast **rs = malloc(sizeof(*rs) * (size_t)n);
        t = a; for (int i = n - 1; i >= 0; i--) { rs[i] = t->r; t = t->l; }
        Fs acc = walk(t);
        for (int i = 0; i < n && acc.nullable; i++) acc = cat(acc, walk(rs[i]));
        free(rs);
        return acc;
    }
    switch (a->k) {
    case A_CAT: break; /* handled above */
    case A_CLASS: { Fs r; pcrec_cls_bits(G, a, r.f); r.nullable = 0; return r; }
    case A_WCLASS: case A_CAP: case A_ATOMIC: return walk(a->l);
    case A_ALT: { Fs l = walk(a->l), r = walk(a->r); uni(l.f, r.f);
                  l.nullable = l.nullable || r.nullable; return l; }
    case A_REP: { Fs b = walk(a->l); if (a->u.rep.rmin < 1) b.nullable = 1; return b; }
    case A_EMPTY: case A_BOL: case A_EOL: case A_END: case A_CTX:
    case A_GSTART: case A_KRESET: case A_LOOK:
        return fs_none();
    case A_BREF: case A_CALL: case A_VAR:
        return fs_all();
    }
    return fs_all();
}

static Ast *parse_lower(const char *pat, Ctx *cx, pcrec_options *defo, int enc)
{
    memset(cx, 0, sizeof(*cx));
    cx->enabled_features = pcrec_enabled_mask();
    pcrec_default_options(defo);
    defo->encoding = enc;
    cx->pat = pat; cx->patlen = strlen(pat); cx->opt = defo;
    cx->job = calloc(1, sizeof(Job));
    if (!cx->job) { fprintf(stderr, "out of memory\n"); exit(2); }
    cx->arena.cx = cx;
    Ast *root = NULL;
    if (setjmp(cx->jb) == 0) {
        pcrec_parse_mods_init(cx);
        root = pcrec_parse_info(cx, NULL);
        if (root) root = pcrec_altcls(cx, root);
        if (root) root = pcrec_discharge_atomic(cx, root);
        if (root) root = pcrec_lower_enc(cx, root);
    } else root = NULL;
    return root;
}

int main(int argc, char **argv)
{
    char err[256];
    volatile int enc = PCREC_ENC_BYTE;   /* live across the setjmp in parse_lower */
    if (argc > 2 && !strcmp(argv[1], "-e") && !strcmp(argv[2], "utf8")) enc = PCREC_ENC_UTF8;
    if (pcrec_enabled_set_spec("all", err, sizeof err) != 0) { fprintf(stderr, "features: %s\n", err); return 2; }
    printf("id\tstatus\tnullable\tpopcount\tset_hex\tcont_bytes\n");
    char *line = NULL; size_t cap = 0; ssize_t got;
    while ((got = getline(&line, &cap, stdin)) > 0) {
        if (line[got - 1] == '\n') line[--got] = 0;
        char *tab = strchr(line, '\t'); if (!tab) continue; *tab = 0;
        const char *id = line, *hex = tab + 1;
        size_t hn = strlen(hex) / 2; char *pat = malloc(hn + 1);
        for (size_t i = 0; i < hn; i++) { unsigned v; sscanf(hex + 2 * i, "%2x", &v); pat[i] = (char)v; }
        pat[hn] = 0;
        Ctx cx; pcrec_options defo;
        Ast *root = parse_lower(pat, &cx, &defo, enc);
        G = &cx;
        if (!root) printf("%s\trefused\t-\t-1\t-\t-\n", id);
        else {
            Fs r; if (setjmp(cx.jb) == 0) r = walk(root); else r = fs_all();
            int pc = 0, cont = 0;
            for (int b = 0; b < 256; b++) if (r.f[b >> 3] >> (b & 7) & 1) { pc++; if (b >= 0x80 && b < 0xc0) cont++; }
            printf("%s\tok\t%d\t%d\t", id, r.nullable, pc);
            for (int i = 0; i < 32; i++) printf("%02x", r.f[i]);
            printf("\t%d\n", cont);
        }
        pcrec_arena_free(&cx.arena); free(cx.job); free(pat);
    }
    free(line);
    return 0;
}
