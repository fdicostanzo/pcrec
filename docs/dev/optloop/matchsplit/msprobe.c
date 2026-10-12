/* [MATCH-SPLIT] STEP-0 survey probe -- a D77 instrument, NOT a mechanism,
 * never wired into the build.  COMPILE-ONLY: no subject is matched.
 *
 * It links libpcrec.a and drives the REAL parser, by the recipe
 * docs/dev/optloop/revend/revend_probe.c established (pcrec_parse_info, then
 * altcls / discharge_atomic / lower_enc for the lowered tree).  Two outputs
 * per pattern:
 *
 *   view   the shipped end-anchor walk, copied from src/facts/endwin.c's
 *          `ew_walk` exactly as revend_probe.c copies it, on the LOWERED tree.
 *          A copy of the walk, cross-checked by survey.py against the shipped
 *          `end_pin` fact; a drifted copy shows as a disagreement count.
 *   ast    the RAW parse tree (before altcls/lower_enc, so classes are still
 *          code-point intervals and every node is the parser's own), dumped as
 *          JSON with the CAT/ALT spines FLATTENED to n-ary lists (a long
 *          literal is a deep left spine and the consumer is recursive).  The
 *          path-class analysis (docs/design/match_split_requirements.md
 *          section 2.2) is done by msclass.py over this dump, so the rewriting
 *          passes can never change which paths a pattern has.
 *
 * stdin : id <TAB> encoding(byte|utf8) <TAB> hex(pattern bytes)
 * stdout: id <TAB> status <TAB> view <TAB> json     (status: ok | refused)
 *
 * JSON nodes (all arrays, first element the kind):
 *   ["cat",...] ["alt",...] ["c",[[lo,hi],...]] ["cbig",n]
 *   ["rep",rmin,rmax,greedy,possessive,child] ["e"] ["bol",multiline]
 *   ["eol",multiline] ["end"] ["g"] ["k"] ["ctx",anchor,fn,[[lo,hi],...]] ["cap",no,child]
 *   ["atom",child] ["wc",child] ["bref"] ["var"] ["call"]
 *   ["look",behind,neg,atomic,child]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
#include "core/internal.h"

enum { EW_NONE = 0, EW_EOL, EW_Z, EW_ML };

static int ew_min(int l, int r)
{
    int rank[4] = { 0, 2, 3, 1 };
    return rank[l] <= rank[r] ? l : r;
}

static int ew_max(int l, int r)
{
    int rank[4] = { 0, 2, 3, 1 };
    return rank[l] >= rank[r] ? l : r;
}

static int ew_walk(const Ast *a)
{
    for (;;) {
        switch (a->k) {
        case A_CAT: {
            int r = ew_walk(a->r);
            if (pcrec_cwmax(a->r) != 0) return r;
            if (r == EW_Z) return EW_Z;
            { int l = ew_walk(a->l); return ew_max(l, r); }
        }
        case A_CAP:
        case A_ATOMIC:
        case A_WCLASS:
            a = a->l;
            continue;
        case A_ALT: {
            int l = ew_walk(a->l), r = ew_walk(a->r);
            return ew_min(l, r);
        }
        case A_REP:
            if (a->u.rep.rmin >= 1) { a = a->l; continue; }
            return EW_NONE;
        case A_END:
            return EW_Z;
        case A_EOL:
            return a->u.anch.multiline ? EW_ML : EW_EOL;
        case A_CLASS:
        case A_EMPTY:
        case A_BOL:
        case A_CTX:
        case A_GSTART:
        case A_KRESET:
        case A_LOOK:
        case A_BREF:
        case A_VAR:
        case A_CALL:
            return EW_NONE;
        }
    }
}

static Ast *parse_stage(const char *pat, Ctx *cx, pcrec_options *defo, int enc,
                        int lowered)
{
    memset(cx, 0, sizeof(*cx));
    cx->enabled_features = pcrec_enabled_mask();
    pcrec_default_options(defo);
    defo->encoding = enc;
    cx->pat = pat;
    cx->patlen = strlen(pat);
    cx->opt = defo;
    cx->job = calloc(1, sizeof(Job));
    if (!cx->job) { fprintf(stderr, "out of memory\n"); exit(2); }
    cx->arena.cx = cx;
    Ast *root = NULL;
    if (setjmp(cx->jb) == 0) {
        pcrec_parse_mods_init(cx);
        root = pcrec_parse_info(cx, NULL);
        if (lowered) {
            if (root) root = pcrec_altcls(cx, root);
            if (root) root = pcrec_discharge_atomic(cx, root);
            if (root) root = pcrec_lower_enc(cx, root);
        }
    }
    return root;
}

/* ---- JSON dump ---------------------------------------------------------- */

static void dump(const Ast *a);

/* Flatten a CAT or ALT spine of kind `k` into an n-ary list, iteratively. */
static void dump_nary(const Ast *a, AKind k, const char *tag)
{
    size_t cap = 64, n = 0;
    const Ast **leaf = malloc(cap * sizeof *leaf);
    size_t scap = 64, sn = 0;
    const Ast **stk = malloc(scap * sizeof *stk);
    stk[sn++] = a;
    while (sn) {
        const Ast *x = stk[--sn];
        if (x->k == k) {
            if (sn + 2 > scap) { scap *= 2; stk = realloc(stk, scap * sizeof *stk); }
            stk[sn++] = x->r;     /* pushed first, popped last: l before r */
            stk[sn++] = x->l;
        } else {
            if (n == cap) { cap *= 2; leaf = realloc(leaf, cap * sizeof *leaf); }
            leaf[n++] = x;
        }
    }
    printf("[\"%s\"", tag);
    for (size_t i = 0; i < n; i++) { putchar(','); dump(leaf[i]); }
    putchar(']');
    free(leaf); free(stk);
}

static void dump(const Ast *a)
{
    switch (a->k) {
    case A_CAT: dump_nary(a, A_CAT, "cat"); break;
    case A_ALT: dump_nary(a, A_ALT, "alt"); break;
    case A_CLASS:
        if (a->u.cls.n > 4000) { printf("[\"cbig\",%d]", a->u.cls.n); break; }
        printf("[\"c\",[");
        for (int i = 0; i < a->u.cls.n; i++)
            printf("%s[%u,%u]", i ? "," : "", a->u.cls.iv[i].lo, a->u.cls.iv[i].hi);
        printf("]]");
        break;
    case A_WCLASS:
        printf("[\"wc\","); dump(a->l); putchar(']'); break;
    case A_REP:
        printf("[\"rep\",%d,%d,%d,%d,", a->u.rep.rmin, a->u.rep.rmax,
               a->u.rep.greedy ? 1 : 0, a->u.rep.possessive ? 1 : 0);
        dump(a->l); putchar(']'); break;
    case A_EMPTY: printf("[\"e\"]"); break;
    case A_BOL: printf("[\"bol\",%d]", a->u.anch.multiline ? 1 : 0); break;
    case A_EOL: printf("[\"eol\",%d]", a->u.anch.multiline ? 1 : 0); break;
    case A_END: printf("[\"end\"]"); break;
    case A_GSTART: printf("[\"g\"]"); break;
    case A_KRESET: printf("[\"k\"]"); break;
    case A_CTX:
        printf("[\"ctx\",%d,%d,[", a->u.ctx.anchor ? 1 : 0, (int)a->u.ctx.fn);
        if (!a->u.ctx.anchor && a->u.ctx.n <= 4000)     /* \b/\B's set is the word class: not needed */
            for (int i = 0; i < a->u.ctx.n; i++)
                printf("%s[%u,%u]", i ? "," : "", a->u.ctx.iv[i].lo, a->u.ctx.iv[i].hi);
        printf("]]");
        break;
    case A_CAP: printf("[\"cap\",%d,", a->u.cap.no); dump(a->l); putchar(']'); break;
    case A_ATOMIC: printf("[\"atom\","); dump(a->l); putchar(']'); break;
    case A_BREF: printf("[\"bref\"]"); break;
    case A_VAR: printf("[\"var\"]"); break;
    case A_CALL: printf("[\"call\"]"); break;
    case A_LOOK:
        printf("[\"look\",%d,%d,%d,", a->u.look.behind ? 1 : 0, a->u.look.neg ? 1 : 0,
               a->u.look.atomic ? 1 : 0);
        dump(a->l); putchar(']'); break;
    }
}

int main(void)
{
    char err[256];
    if (pcrec_enabled_set_spec("all", err, sizeof err) != 0) {
        fprintf(stderr, "features: %s\n", err); return 2;
    }
    char *line = NULL; size_t cap = 0; ssize_t got;
    while ((got = getline(&line, &cap, stdin)) > 0) {
        if (got && line[got - 1] == '\n') line[--got] = 0;
        char *t1 = strchr(line, '\t');
        if (!t1) continue;
        *t1 = 0;
        char *t2 = strchr(t1 + 1, '\t');
        if (!t2) continue;
        *t2 = 0;
        const char *id = line, *encs = t1 + 1, *hex = t2 + 1;
        int enc = strcmp(encs, "utf8") == 0 ? PCREC_ENC_UTF8 : PCREC_ENC_BYTE;
        size_t hn = strlen(hex) / 2;
        char *pat = malloc(hn + 1);
        for (size_t i = 0; i < hn; i++) {
            unsigned v; sscanf(hex + 2 * i, "%2x", &v); pat[i] = (char)v;
        }
        pat[hn] = 0;
        Ctx cx; pcrec_options defo;
        Ast *raw = parse_stage(pat, &cx, &defo, enc, 0);
        if (!raw) {
            printf("%s\trefused\t0\t[]\n", id);
        } else {
            Ctx cx2; pcrec_options defo2;
            Ast *low = parse_stage(pat, &cx2, &defo2, enc, 1);
            int view = low ? ew_walk(low) : -1;
            printf("%s\tok\t%d\t", id, view);
            dump(raw);
            putchar('\n');
        }
        free(pat);
        fflush(stdout);
    }
    return 0;
}
