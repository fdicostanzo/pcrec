/* [PF-KNOW] (D140) — THE PROVEN-SEGMENT PROBE.  A throwaway analyzer, never
 * wired into the build.  For each pattern it measures how much of the VM
 * program an EXACT hybrid prefilter's proof covers, statically:
 *
 *   The hybrid's forward+reverse DFA pair proves `s[start,end)` is in the
 *   capture-erased language (engine_m4.md 6.1).  Every VM test that lies on a
 *   FIXED-WIDTH, CHOICE-FREE segment at the START of the program is then
 *   implied (every accepting path passes it at a known offset), and so is the
 *   symmetric segment at the END (known offset from `end`).  Anything past
 *   the first choice point (alternation, a repeat with a choice, a
 *   lookaround, a backreference, a call) is NOT implied: the DFA does not say
 *   which branch the winning path took or where a repeat stopped.
 *
 * det(a) — "deterministic, fixed width":
 *   A_CLASS / A_WCLASS       one byte / one character, one test
 *   A_EMPTY                  width 0
 *   A_BOL A_EOL A_END A_CTX A_GSTART   zero-width tests the DFA also decides
 *   A_KRESET                 zero-width, one slot write (\K)
 *   A_CAP                    det iff body det; two slot writes
 *   A_CAT                    det iff both sides det
 *   A_REP rmin == rmax       det iff body det (width rmin * w)
 *   A_ATOMIC                 det iff body det (a cut over no choice is a no-op)
 *   everything else          not det
 *
 * Leading segment: walk the top-level concatenation from the left taking det
 * nodes; on the first non-det node DESCEND if it is A_CAP/A_ATOMIC (body) or
 * A_CAT (left spine), else stop.  Trailing segment: the mirror.  `det_all`
 * means the root is det — the whole program is implied and every capture is
 * at a constant offset from `start`.
 *
 * Build (never by `make`):
 *   gcc -O2 -Ilib -Isrc -o segprobe studies/pf_know/segprobe.c build/libpcrec.a
 * Input : one record per line, `id<TAB>hex-encoded pattern bytes`.
 * Output: one TSV row per record. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
#include "core/internal.h"

typedef struct {
    long long w;      /* bytes (chars under utf8 for A_WCLASS) */
    long tests;       /* consuming single-character tests */
    long zw;          /* zero-width tests (^ $ \b \z \G) */
    long sets;        /* slot writes (2 per capture, 1 per \K) */
    long lits;        /* of `tests`, those that are a single literal byte */
    long litrun;      /* longest run of consecutive literal bytes */
    long currun;
} Seg;

static int enc_utf8;
static bool kind_alt, kind_repc, kind_look, kind_bref, kind_call, kind_atomic,
            kind_var, kind_wcls, kind_ctx;

static bool is_lit(const Ast *a)
{
    return a->k == A_CLASS && a->u.cls.n == 1 && a->u.cls.iv[0].lo == a->u.cls.iv[0].hi;
}

/* det(a) and, when det, the segment measure of the whole node. */
static bool det(const Ast *a, Seg *s)
{
    switch (a->k) {
    case A_CLASS: case A_WCLASS:
        s->w += 1; s->tests += 1;
        if (is_lit(a)) { s->lits += 1; s->currun += 1; if (s->currun > s->litrun) s->litrun = s->currun; }
        else s->currun = 0;
        return true;
    case A_EMPTY: return true;
    case A_BOL: case A_EOL: case A_END: case A_CTX: case A_GSTART:
        s->zw += 1; s->currun = 0; return true;
    case A_KRESET: s->sets += 1; return true;
    case A_CAP: { Seg t = *s; if (!det(a->l, &t)) return false; t.sets += 2; *s = t; return true; }
    case A_ATOMIC: { Seg t = *s; if (!det(a->l, &t)) return false; *s = t; return true; }
    case A_CAT: { Seg t = *s; if (!det(a->l, &t) || !det(a->r, &t)) return false; *s = t; return true; }
    case A_REP: {
        if (a->u.rep.rmin != a->u.rep.rmax) return false;
        Seg one = {0}; if (!det(a->l, &one)) return false;
        /* Scale the body's measure by the count rather than walking it
         * `rmin` times: a nested exact repeat is a product of counts. */
        long long k = a->u.rep.rmin;
        bool alllit = one.tests > 0 && one.lits == one.tests && one.zw == 0 && one.sets == 0;
        s->w += one.w * k; s->tests += one.tests * k; s->zw += one.zw * k;
        s->sets += one.sets * k; s->lits += one.lits * k;
        if (alllit) { s->currun += one.w * k; if (s->currun > s->litrun) s->litrun = s->currun; }
        else { if (one.litrun > s->litrun) s->litrun = one.litrun; s->currun = 0; }
        return true;
    }
    default: return false;
    }
}

/* The leading segment: take det nodes off the left spine, descend through a
 * non-det A_CAP / A_ATOMIC / A_CAT, stop at anything else. */
static void lead(const Ast *a, Seg *s)
{
    for (;;) {
        Seg t = *s;
        if (det(a, &t)) { *s = t; return; }
        if (a->k == A_CAT) {
            Seg u = *s;
            if (det(a->l, &u)) { *s = u; a = a->r; continue; }
            a = a->l; continue;
        }
        if (a->k == A_CAP) { s->sets += 1; a = a->l; continue; }   /* the OPEN write */
        if (a->k == A_ATOMIC) { a = a->l; continue; }
        return;
    }
}
static void trail(const Ast *a, Seg *s)
{
    for (;;) {
        Seg t = *s;
        if (det(a, &t)) { *s = t; return; }
        if (a->k == A_CAT) {
            Seg u = *s;
            if (det(a->r, &u)) { *s = u; a = a->l; continue; }
            a = a->r; continue;
        }
        if (a->k == A_CAP) { s->sets += 1; a = a->l; continue; }   /* the CLOSE write */
        if (a->k == A_ATOMIC) { a = a->l; continue; }
        return;
    }
}

static void kinds(const Ast *a)
{
    if (!a) return;
    switch (a->k) {
    case A_ALT: kind_alt = true; break;
    case A_REP: if (a->u.rep.rmin != a->u.rep.rmax) kind_repc = true; break;
    case A_LOOK: kind_look = true; break;
    case A_BREF: kind_bref = true; break;
    case A_CALL: kind_call = true; break;
    case A_ATOMIC: kind_atomic = true; break;
    case A_VAR: kind_var = true; break;
    case A_WCLASS: kind_wcls = true; break;
    case A_CTX: kind_ctx = true; break;
    default: break;
    }
    if (a->k != A_BREF && a->k != A_CALL) { kinds(a->l); kinds(a->r); }
}

static Ast *parse_lower(const char *pat, size_t len, Ctx *cx, pcrec_options *defo, int enc)
{
    memset(cx, 0, sizeof(*cx));
    cx->enabled_features = pcrec_enabled_mask();
    cx->want_caps = true;
    pcrec_default_options(defo);
    defo->encoding = enc;
    cx->pat = pat; cx->patlen = len; cx->opt = defo;
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

int main(int argc, char **argv)
{
    char err[256];
    int enc = PCREC_ENC_BYTE;
    for (int i = 1; i < argc; i++)
        if (!strcmp(argv[i], "-e") && i + 1 < argc && !strcmp(argv[i+1], "utf8"))
            { enc = PCREC_ENC_UTF8; enc_utf8 = 1; i++; }
    if (pcrec_enabled_set_spec("all", err, sizeof err) != 0) {
        fprintf(stderr, "features: %s\n", err); return 2;
    }
    printf("id\tstatus\tncap\tkinds\tdet_all\tchoice_free\tlead_w\tlead_tests\tlead_zw\tlead_sets\tlead_lits\tlead_litrun"
           "\ttrail_w\ttrail_tests\ttrail_zw\ttrail_sets\ttrail_lits\ttrail_litrun\tminw\tmaxw\n");
    char *line = NULL; size_t cap = 0; ssize_t got;
    while ((got = getline(&line, &cap, stdin)) > 0) {
        if (got && line[got-1] == '\n') line[--got] = 0;
        if (!got) continue;
        char *tab = strchr(line, '\t'); if (!tab) continue;
        *tab = 0;
        const char *id = line, *hex = tab + 1;
        size_t hn = strlen(hex) / 2;
        char *pat = malloc(hn + 1);
        for (size_t i = 0; i < hn; i++) { unsigned v; sscanf(hex + 2*i, "%2x", &v); pat[i] = (char)v; }
        pat[hn] = 0;
        Ctx cx; pcrec_options defo;
        Ast *root = parse_lower(pat, hn, &cx, &defo, enc);
        if (!root) {
            printf("%s\trefused\t0\t-\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\n", id);
        } else {
            kind_alt = kind_repc = kind_look = kind_bref = kind_call = kind_atomic = kind_var = kind_wcls = kind_ctx = false;
            kinds(root);
            Seg all = {0}; bool da = det(root, &all);
            Seg L = {0}; lead(root, &L);
            Seg T = {0}; trail(root, &T);
            if (da) { L = all; T = all; }
            char kb[128] = ""; 
            if (kind_alt) strcat(kb, "alt,");
            if (kind_repc) strcat(kb, "repc,");
            if (kind_look) strcat(kb, "look,");
            if (kind_bref) strcat(kb, "bref,");
            if (kind_call) strcat(kb, "call,");
            if (kind_atomic) strcat(kb, "atomic,");
            if (kind_var) strcat(kb, "var,");
            if (kind_wcls) strcat(kb, "wcls,");
            if (kind_ctx) strcat(kb, "ctx,");
            if (!kb[0]) strcpy(kb, "-"); else kb[strlen(kb)-1] = 0;
            bool cf = !kind_alt && !kind_repc && !kind_look && !kind_bref && !kind_call && !kind_var;
            long long mw = pcrec_minw(root), xw = pcrec_cwmax(root);
            printf("%s\tok\t%d\t%s\t%d\t%d\t%lld\t%ld\t%ld\t%ld\t%ld\t%ld\t%lld\t%ld\t%ld\t%ld\t%ld\t%ld\t%lld\t%lld\n",
                   id, (int)cx.ncap, kb, da ? 1 : 0, cf ? 1 : 0,
                   L.w, L.tests, L.zw, L.sets, L.lits, L.litrun,
                   T.w, T.tests, T.zw, T.sets, T.lits, T.litrun, mw, xw);
        }
        pcrec_arena_free(&cx.arena);
        free(cx.job);
        free(pat);
    }
    free(line);
    return 0;
}
