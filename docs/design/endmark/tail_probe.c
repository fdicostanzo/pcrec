/* D164 census probe: which patterns carry a PATH-FINAL lookahead (or `$`,
 * `\Z`, `(?m)$`, `\z`) that the END_MARK lowering would reach, and what else
 * stands between each pattern and the DFA.  A D77 instrument, NOT a
 * mechanism, never wired into the build.
 *
 * Links libpcrec.a and drives the real parser plus the rewriting prefix
 * compile.c runs before selection (altcls, discharge_atomic, lower_enc: the
 * recipe of docs/dev/optloop/revend/revend_probe.c), with want_caps ON (the
 * default request).  The tail walk is the lowering's own definition
 * (endmark.md §1.2): the root is a tail; a CAT's LAST element (trailing empty
 * elements skipped) inherits it; both arms of an ALT; the body of a CAP or an
 * ATOMIC; the body of a REP whose max is 1.  Nothing else.
 *
 *    gcc -O1 -Ilib -Isrc docs/design/endmark/tail_probe.c build/libpcrec.a \
 *        -o build/scratch/tail_probe
 *
 * stdin : id <TAB> encoding(byte|utf8) <TAB> hex(pattern bytes)
 * stdout: one TSV row per pattern, columns named in the header line.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
#include "core/internal.h"

#define MAXT 64

typedef struct {
    int nlook, nlook_unb, nneg, neol, nmeol, nz, nctx;
    long long look_cwmax;      /* max over tail lookahead bodies, -1 unbounded */
    int look_fixed;            /* every tail lookahead body fixed-width (chars) */
    int look_cap;              /* a tail lookahead body holds a capture */
    int look_vmonly;           /* a tail lookahead body holds a VM-only node */
    int under_cap;             /* a tail lookahead / $ sits inside a capture */
    int under_atomic;
    const Ast *tails[MAXT];    /* the tail positive lookaheads (skip set) */
    int ntails;
} Tail;

static void see_cap(void *ud, const Ast *a) { if (a->k == A_CAP) (*(int *)ud)++; }
static void see_look(void *ud, const Ast *a) { if (a->k == A_LOOK) (*(int *)ud)++; }
static void see_call(void *ud, const Ast *a) { if (a->k == A_CALL) (*(int *)ud)++; }

/* a VM-only node anywhere under `a` (the body's own constructs) */
static void see_vmonly(void *ud, const Ast *a)
{
    if (a->reg && !(a->reg->engines & ENGM_DFA)) (*(int *)ud)++;
}

static void tail_walk(const Ast *a, Tail *t, int cap, int atomic)
{
    for (;;) {
        switch (a->k) {
        case A_CAT:
            /* the last element; a trailing (?:) does not end a path */
            while (a->k == A_CAT && a->r->k == A_EMPTY) a = a->l;
            if (a->k != A_CAT) continue;
            a = a->r;
            continue;
        case A_ALT:
            tail_walk(a->r, t, cap, atomic);
            a = a->l;
            continue;
        case A_CAP:
            cap = 1; a = a->l; continue;
        case A_ATOMIC:
            atomic = 1; a = a->l; continue;
        case A_REP:
            if (a->u.rep.rmax != 1) return;
            a = a->l;
            continue;
        case A_LOOK:
            if (a->u.look.behind) return;
            if (a->u.look.neg) { t->nneg++; return; }
            t->nlook++;
            if (t->ntails < MAXT) t->tails[t->ntails++] = a;
            {
                long long w = pcrec_cwmax(a->l);
                long long mn = pcrec_cwmin(a->l);
                if (w >= PCREC_W_UNBOUNDED) { t->nlook_unb++; t->look_cwmax = -1; }
                else if (t->look_cwmax >= 0 && w > t->look_cwmax) t->look_cwmax = w;
                if (w != mn) t->look_fixed = 0;
                int c = 0; pcrec_ast_visit(a->l, see_cap, &c);
                if (c) t->look_cap = 1;
                int v = 0; pcrec_ast_visit(a->l, see_vmonly, &v);
                if (v) t->look_vmonly = 1;
            }
            if (cap) t->under_cap = 1;
            if (atomic) t->under_atomic = 1;
            return;
        case A_EOL:
            if (a->u.anch.multiline) t->nmeol++; else t->neol++;
            if (cap) t->under_cap = 1;
            return;
        case A_END: t->nz++; return;
        case A_CTX: t->nctx++; return;
        default:
            return;
        }
    }
}

/* the first VM-only node reachable outside the tail lookaheads' OWN stamps
 * (their bodies still count); call bodies are not followed (the walk never
 * reads u.call.body). */
static const char *first_vmonly(const Ast *a, const Tail *t)
{
    int skip = 0;
    for (int i = 0; i < t->ntails; i++) skip |= t->tails[i] == a;
    if (!skip && a->reg && !(a->reg->engines & ENGM_DFA)) return a->reg->syntax;
    switch (a->k) {
    case A_CAT: case A_ALT: {
        const char *r = first_vmonly(a->r, t);
        if (r) return r;
        return first_vmonly(a->l, t);
    }
    case A_CAP: case A_ATOMIC: case A_REP: case A_LOOK:
        return first_vmonly(a->l, t);
    default:
        return NULL;
    }
}

static Ast *parse_lower(const char *pat, Ctx *cx, pcrec_options *defo, int enc)
{
    memset(cx, 0, sizeof(*cx));
    cx->enabled_features = pcrec_enabled_mask();
    pcrec_default_options(defo);
    defo->encoding = enc;
    cx->pat = pat;
    cx->patlen = strlen(pat);
    cx->opt = defo;
    cx->want_caps = true;
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
    }
    return root;
}

int main(void)
{
    char err[256];
    if (pcrec_enabled_set_spec("all", err, sizeof err) != 0) {
        fprintf(stderr, "features: %s\n", err); return 2;
    }
    printf("id\tstatus\tnlook\tnlook_unb\tlook_cwmax\tlook_fixed\tlook_cap\tlook_vmonly"
           "\tunder_cap\tunder_atomic\tnneg\tneol\tnmeol\tnz\tnctx\tnlook_all\tncap\tncall"
           "\tother_vmonly\n");
    char *line = NULL; size_t capn = 0; ssize_t got;
    while ((got = getline(&line, &capn, stdin)) > 0) {
        if (got && line[got - 1] == '\n') line[--got] = 0;
        char *t1 = strchr(line, '\t'); if (!t1) continue; *t1 = 0;
        char *t2 = strchr(t1 + 1, '\t'); if (!t2) continue; *t2 = 0;
        const char *id = line, *encs = t1 + 1, *hex = t2 + 1;
        int enc = strcmp(encs, "utf8") == 0 ? PCREC_ENC_UTF8 : PCREC_ENC_BYTE;
        size_t hn = strlen(hex) / 2;
        char *pat = malloc(hn + 1);
        for (size_t i = 0; i < hn; i++) { unsigned v; sscanf(hex + 2 * i, "%2x", &v); pat[i] = (char)v; }
        pat[hn] = 0;
        Ctx cx; pcrec_options defo;
        Ast *root = parse_lower(pat, &cx, &defo, enc);
        if (!root) {
            printf("%s\trefused\n", id);
        } else {
            Tail t; memset(&t, 0, sizeof t); t.look_fixed = 1;
            tail_walk(root, &t, 0, 0);
            int nla = 0, nc = 0, ncall = 0;
            pcrec_ast_visit(root, see_look, &nla);
            pcrec_ast_visit(root, see_cap, &nc);
            pcrec_ast_visit(root, see_call, &ncall);
            const char *ov = first_vmonly(root, &t);
            printf("%s\tok\t%d\t%d\t%lld\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%s\n",
                   id, t.nlook, t.nlook_unb, t.nlook ? t.look_cwmax : 0, t.nlook ? t.look_fixed : 0,
                   t.look_cap, t.look_vmonly, t.under_cap, t.under_atomic, t.nneg, t.neol, t.nmeol,
                   t.nz, t.nctx, nla, nc, ncall, ov ? ov : "-");
        }
        free(pat);
        fflush(stdout);
    }
    return 0;
}
