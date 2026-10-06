/* [OPT-REVEND] THE END-ANCHOR CENSUS PROBE -- a D77 instrument, NOT a
 * mechanism, never wired into the build.
 *
 * It links libpcrec.a and drives the REAL parser and the same rewriting
 * prefix compile.c runs above the end-window fact (altcls, discharge_atomic,
 * lower_enc -- the recipe docs/dev/optloop/reqrunenc/reqrunenc_probe.c
 * established and documents the reason for).  Its end-anchor walk is a
 * COPY of src/facts/endwin.c's `ew_walk`, with ONE addition: a multiline
 * `$` is reported as its own level (EW_ML) instead of collapsing to "none",
 * so the census can count the (?m)-tail population the shipped fact
 * declines.  The driver cross-checks the probe against the shipped fact:
 * for every row the probe calls end-anchored-and-not-ML, the compiler's own
 * `--emit-facts` end_window row must NOT read decline:not-end-anchored (and
 * vice versa), so a drifted copy shows as a disagreement count, not a
 * silent skew.
 *
 * stdin : id <TAB> encoding(byte|utf8) <TAB> hex(pattern bytes)
 * stdout: id status view cwmax minw lead_unb gstart look_tail
 *   view      0 none, 1 EOL ($, \Z), 2 Z (\z), 3 ML (every alternative ends
 *             in $ but at least one is a (?m) $, so no end pin)
 *   cwmax     maximum width in CHARACTERS, -1 = unbounded
 *   minw      minimum width in bytes
 *   lead_unb  1 when some alternative BEGINS with an unbounded repeat (the
 *             leading-.* family: the reverse walk's extent is the whole
 *             line/subject on a subject the pattern keeps matching)
 *   gstart    1 when \G appears anywhere
 *   look_tail 1 when the walk answered none only because the final factor is
 *             a lookaround (a trailing (?=\z) pins the end; endwin.c declines
 *             it) -- a near-miss population, counted not chased
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
#include "core/internal.h"

enum { EW_NONE = 0, EW_EOL, EW_Z, EW_ML };

static int ew_min(int l, int r)
{
    /* the weakest of two branches; ML sits between NONE and EOL */
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

/* Does some alternative BEGIN with an unbounded repeat?  Iterative down the
 * left spine; zero-width leading factors are skipped. */
static int lead_unb(const Ast *a)
{
    for (;;) {
        switch (a->k) {
        case A_CAT: {
            const Ast *l = a->l;
            if (pcrec_cwmax(l) == 0) { a = a->r; continue; }
            a = l;
            continue;
        }
        case A_CAP:
        case A_ATOMIC:
        case A_WCLASS:
            a = a->l;
            continue;
        case A_ALT:
            if (lead_unb(a->r)) return 1;
            a = a->l;
            continue;
        case A_REP:
            if (a->u.rep.rmax < 0) return 1;
            a = a->l;
            continue;
        case A_BREF: case A_CALL: case A_VAR:
            return 1;
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_CTX: case A_GSTART: case A_KRESET: case A_LOOK:
            return 0;
        }
    }
}

static void see_g(void *ud, const Ast *a)
{
    if (a->k == A_GSTART) *(int *)ud = 1;
}

/* Is the LAST factor of the top spine a lookaround? */
static int look_tail(const Ast *a)
{
    while (a->k == A_CAP || a->k == A_ATOMIC) a = a->l;
    while (a->k == A_CAT) {
        a = a->r;
        while (a->k == A_CAP || a->k == A_ATOMIC) a = a->l;
    }
    return a->k == A_LOOK;
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
    printf("id\tstatus\tview\tcwmax\tminw\tlead_unb\tgstart\tlook_tail\n");
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
        Ast *root = parse_lower(pat, &cx, &defo, enc);
        if (!root) {
            printf("%s\trefused\t0\t-1\t0\t0\t0\t0\n", id);
        } else {
            int g = 0;
            pcrec_ast_visit(root, see_g, &g);
            int v = ew_walk(root);
            long long w = pcrec_cwmax(root);
            printf("%s\tok\t%d\t%lld\t%lld\t%d\t%d\t%d\n", id, v,
                   w >= PCREC_W_UNBOUNDED ? -1LL : w, pcrec_minw(root),
                   lead_unb(root), g, v == EW_NONE ? look_tail(root) : 0);
        }
        free(pat);
        fflush(stdout);
    }
    return 0;
}
