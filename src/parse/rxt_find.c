/* src/parse/rxt_find.c — ANALYSIS RESOLUTION: from a bundle NAME to the
 * chain of bundles a compile reads its rates from ([FINDINGS] B2;
 * docs/design/findings/design.md §4, docs/spec/findings.md §5).
 *
 * THREE STOPS, SEARCHED IN ORDER, AND NOTHING ELSE (R13):
 *   S1  the bundles defined in the compiling `.rxt` FILE itself (or a
 *       library caller's `analysis_source`) — never its `include "path"`
 *       fragments and never its `lib` closure (D123-8 item 3);
 *   S2  `DIR/<name>.rxt` for each `-I DIR` in order, the directory entry
 *       matched EXACTLY so a case-insensitive filesystem cannot answer
 *       `log` with `Log.rxt` [r2 M-S6]. A file that exists but defines no
 *       bundle, or a bundle of another name, FALLS THROUGH with a note (a
 *       `lib` library beside it is the common case) [r2 M-S4]; a file
 *       defining two is refused [r2 M-S5];
 *   S3  the store built into libpcrec.
 * No environment variable, no cwd-relative default, no home directory.
 *
 * THE CHAIN (§4.3): the selected bundle, then its `include`, then that
 * bundle's `include`, ..., then the BUILT-IN `default` by identity (§0.6).
 * A bundle including ITS OWN NAME resolves from the stop AFTER the one it
 * was found at — gcc's `#include_next`, the copy-edit-shadow case (§0.4);
 * any other repeat of a (bundle, stop) pair is a cycle and refused.
 *
 * WHY IT IS A PARSE-LAYER FILE. Resolution opens and parses `.rxt` files,
 * which is this layer's job; the chain it produces is plain data defined
 * in `src/core/findings.h`, which the accessor reads without knowing any
 * file was involved. Every link's blocks are COPIED into the caller's
 * arena, so the parses it made are freed before it returns and a chain
 * outlives every file it was read from.
 *
 * EAGER: every name is resolved before the compile, so a bad name refuses
 * even a pattern that would never ask a query — predictability over
 * laziness (§4.3).
 *
 * [KNOW-SRC] K1: THE STOP LOOP IS THE KNOWLEDGE MODULE'S. One link's lookup
 * (`find_bundle`) is `pcrec_ks_resolve` driven by the analysis kind's row
 * (src/parse/ks_analysis.c: the exact entry match, the S2 fall-through note
 * and the two-bundle refusal are its COLUMNS); this file keeps what is the
 * analysis kind's own — the chain, `#include_next`, the cycle and depth
 * refusals, the terminal — and builds a link from wherever the resolver
 * landed (measure_sets.md §9.7 K1; K2 deleted the pre-K1 loop and its
 * both-ways debug check). */

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/internal.h"
#include "core/ksrc.h"
#include "enc/enc.h"

/* One resolution in progress: where to look, where to put the answer, and
 * where a refusal goes. */
typedef struct {
    Arena              *a;
    const RxtSource    *s1;      /* S1, or NULL */
    const char *const  *dirs;    /* S2, `ndirs` of them */
    size_t              ndirs;
    pcrec_error        *err;
    bool                notes;   /* print the non-fatal notes (§9) */
} FindWalk;

/* Fills `err` with a formatted refusal and returns -1. */
static int find_fail(FindWalk *w, const char *fmt, ...)
    __attribute__((format(printf, 2, 3)));
static int find_fail(FindWalk *w, const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(w->err->msg, sizeof w->err->msg, fmt, ap);
    va_end(ap);
    w->err->pos = 0;
    return -1;
}

/* An arena copy of `s[0..n)`, NUL-terminated. */
static const char *find_strndup(Arena *a, const char *s, size_t n)
{
    char *d = pcrec_arena_alloc(a, n + 1);
    memcpy(d, s, n);
    d[n] = 0;
    return d;
}

/* The bundle's own row in `src`, or NULL. */
static const RxtRow *bundle_row(const RxtSource *src, const char *name)
{
    for (size_t i = 0; i < src->nrows; i++)
        if (src->rows[i].kind == RXT_DECL_ANALYSIS &&
            !strcmp(src->rows[i].name, name))
            return &src->rows[i];
    return NULL;
}

/* The link for bundle row `row` of `src`: its `include` with the brackets
 * stripped, and every data block of the bundle copied into the walk's
 * arena. */
static void link_from_source(FindWalk *w, const RxtSource *src,
                             const RxtRow *row, PcrecFindStop stop,
                             const char *location, PcrecFindLink *out)
{
    size_t nb = 0, k = 0;
    PcrecFindTblBlock *bl;
    memset(out, 0, sizeof *out);
    out->bundle = find_strndup(w->a, row->name, strlen(row->name));
    out->stop = stop;
    out->location = location;
    if (row->value && row->value[0])
        out->include = find_strndup(w->a, row->value + 1,
                                    strlen(row->value) - 2);
    for (size_t i = 0; i < src->nfblocks; i++)
        if (!strcmp(src->fblocks[i].bundle, row->name)) nb++;
    if (!nb) return;
    bl = pcrec_arena_alloc(w->a, nb * sizeof *bl);
    for (size_t i = 0; i < src->nfblocks; i++) {
        const RxtFindBlock *fb = &src->fblocks[i];
        PcrecFindServe *sv;
        unsigned long long *c;
        if (strcmp(fb->bundle, row->name) != 0) continue;
        sv = pcrec_arena_alloc(w->a, (fb->nserves ? fb->nserves : 1) * sizeof *sv);
        for (size_t j = 0; j < fb->nserves; j++) {
            sv[j].query = find_strndup(w->a, fb->serves[j].query,
                                       strlen(fb->serves[j].query));
            sv[j].encs = find_strndup(w->a, fb->serves[j].encs,
                                      strlen(fb->serves[j].encs));
            sv[j].via = find_strndup(w->a, fb->serves[j].via,
                                     strlen(fb->serves[j].via));
        }
        c = NULL;
        if (fb->counts) {
            c = pcrec_arena_alloc(w->a, 256 * sizeof *c);
            memcpy(c, fb->counts, 256 * sizeof *c);
        }
        if (fb->ncps) {
            PcrecFindCp *cp = pcrec_arena_alloc(w->a, fb->ncps * sizeof *cp);
            memcpy(cp, fb->cps, fb->ncps * sizeof *cp);
            bl[k].cps = cp;
        }
        bl[k].ncps = fb->ncps;
        bl[k].bundle = out->bundle;
        bl[k].kind = find_strndup(w->a, fb->kind, strlen(fb->kind));
        bl[k].line = fb->line;
        bl[k].serves = sv;
        bl[k].nserves = fb->nserves;
        bl[k].counts = c;
        /* [WINDOW-E1] the stanza a query's provenance is read from */
        bl[k].prov_source = fb->prov_source
            ? find_strndup(w->a, fb->prov_source, strlen(fb->prov_source)) : NULL;
        bl[k].prov_bytes = fb->prov_bytes ? strtoull(fb->prov_bytes, NULL, 10) : 0;
        bl[k].prov_fidelity = fb->prov_fidelity
            ? find_strndup(w->a, fb->prov_fidelity, strlen(fb->prov_fidelity)) : NULL;
        k++;
    }
    out->blocks = bl;
    out->nblocks = nb;
}

/* The resolver's allocator: the walk's arena. */
static void *find_alloc(void *a, size_t n)
{
    return pcrec_arena_alloc(a, n);
}

/* The two stops that are this walk's own data: does the compiling file (S1)
 * or the store (S3) define bundle `name`? */
static bool find_has(void *ctx, KsAt at, const char *name)
{
    const FindWalk *w = ctx;
    PcrecFindLink tmp;
    if (at == KS_AT_S1) return bundle_row(w->s1, name) != NULL;
    return pcrec_find_store_link(name, PCREC_FIND_STOP_STORE, &tmp);
}

/* §9's fall-through note, on stderr. */
static void find_note(void *ctx, const char *text)
{
    (void)ctx;
    fprintf(stderr, "pcrec: note: %s\n", text);
}


/* `find(name, from)` of design §4.3: the first stop >= `from` defining
 * `name`, into `*out` and `*at` (the stop index space is ksrc.h's `KsAt`:
 * 0 S1, 1..ndirs the `-I` directories, ndirs + 1 the store, so `next(s)` is
 * always `s + 1`). -1 with the refusal filled. The stop loop
 * is `pcrec_ks_resolve`'s; the link is built here from where it landed. */
static int find_bundle(FindWalk *w, const char *name, size_t from,
                       PcrecFindLink *out, size_t *at)
{
    KsAlloc al = { find_alloc, w->a };
    KsErr kerr;
    KsWalk kw = {
        .kind = &pcrec_ks_analysis, .dirs = w->dirs, .ndirs = w->ndirs,
        .s1 = w->s1 != NULL, .srcdir = "", .alloc = &al, .ctx = w,
        .has = find_has, .note = w->notes ? find_note : NULL, .err = &kerr
    };
    KsHit hit;
    int rc = 0;
    switch (pcrec_ks_resolve(&kw, KS_REQ_NAME, name, from, &hit)) {
    case KS_RES_ABSENT:
        pcrec_ks_refuse_unknown(&kw, name);
        rc = find_fail(w, "%s", kerr.msg);
        break;
    case KS_RES_ERROR:
        rc = find_fail(w, "%s", kerr.msg);
        break;
    case KS_RES_FOUND:
        switch (hit.at) {
        case KS_AT_S1:
            link_from_source(w, w->s1, bundle_row(w->s1, name),
                             PCREC_FIND_STOP_SOURCE, NULL, out);
            break;
        case KS_AT_DIRS: {
            RxtSource *src = hit.doc;
            link_from_source(w, src, bundle_row(src, name),
                             PCREC_FIND_STOP_DIR, hit.path, out);
            pcrec_rxt_source_free(src);
            break;
        }
        case KS_AT_STORE:
            pcrec_find_store_link(name, PCREC_FIND_STOP_STORE, out);
            break;
        case KS_AT_SRCDIR:   /* not an analysis stop (its row's `stops`) */
            rc = find_fail(w, "internal error: analysis '%s' resolved at a "
                           "source-directory stop", name);
            break;
        }
        *at = hit.stop;
        break;
    }
    return rc;
}

int pcrec_find_chain_build(Arena *a, const char *name, const RxtSource *s1,
                           const char *const *dirs, bool notes,
                           PcrecFindChain *out, pcrec_error *err)
{
    enum { CAP = PCREC_MAX_FIND_CHAIN + 1 };
    FindWalk w = { a, s1, dirs, 0, err, notes };
    PcrecFindLink *links = pcrec_arena_alloc(a, CAP * sizeof *links);
    size_t at[CAP], n = 0, s = 0;
    bool have_default = false;
    if (dirs) while (dirs[w.ndirs]) w.ndirs++;
    out->links = links;
    out->n = 0;
    if (name) {
        if (!pcrec_ks_name_ok(name, strlen(name)))
            return find_fail(&w, "analysis '%s': analysis names are LOWERCASE "
                             "— a letter a-z, then a-z, 0-9, '_' or '-'",
                             name);
        if (find_bundle(&w, name, 0, &links[0], &at[0]) != 0) return -1;
        n = 1;
        while (links[n - 1].include) {
            const char *inc = links[n - 1].include;
            size_t start = !strcmp(inc, links[n - 1].bundle) ? at[n - 1] + 1 : 0;
            PcrecFindLink next;
            if (find_bundle(&w, inc, start, &next, &s) != 0) return -1;
            for (size_t i = 0; i < n; i++)
                if (at[i] == s && !strcmp(links[i].bundle, next.bundle)) {
                    char msg[sizeof err->msg];
                    size_t k = 0;
                    msg[0] = 0;
                    for (size_t j = i; j < n && k + 1 < sizeof msg; j++)
                        k += (size_t)snprintf(msg + k, sizeof msg - k, "%s -> ",
                                              links[j].bundle);
                    return find_fail(&w, "analysis include cycle: %s%s",
                                     msg, next.bundle);
                }
            if (n == PCREC_MAX_FIND_CHAIN)
                return find_fail(&w, "analysis '%s': its include chain "
                                 "exceeds PCREC_MAX_FIND_CHAIN (%d links)",
                                 name, PCREC_MAX_FIND_CHAIN);
            links[n] = next;
            at[n++] = s;
        }
    }
    /* THE TERMINAL, BY IDENTITY (§0.6) — not added twice when an explicit
     * `include <default>` already reached the store's default. */
    for (size_t i = 0; i < n; i++)
        if (links[i].stop == PCREC_FIND_STOP_STORE &&
            !strcmp(links[i].bundle, "default"))
            have_default = true;
    if (!have_default &&
        pcrec_find_store_link("default", PCREC_FIND_STOP_DEFAULT, &links[n]))
        n++;
    out->n = n;
    return 0;
}

/* Does any link of `chain` declare any query (the vocabulary,
 * `pcrec_find_query`) under encoding `enc`? */
static bool chain_serves_enc(const PcrecFindChain *chain, const char *enc)
{
    const PcrecFindQuery *q;
    for (size_t i = 0; (q = pcrec_find_query(i)); i++)
        if (pcrec_find_chain_answer(chain, q->tag, enc, NULL, NULL))
            return true;
    return false;
}

void pcrec_find_resolve(Ctx *cx, bool notes)
{
    const pcrec_options *o = cx->opt;
    const RxtSource *s1 = cx->defs ? cx->defs->file : NULL;
    RxtSource *owned = NULL;
    pcrec_error ferr = { 0 };
    int rc;
    /* [K113] a compound part reads its walk's chain, never a second
       resolution of the same options (a file or an -I stop could change
       between); the walk printed the notes */
    if (cx->emit_in && cx->emit_in->meas) {
        cx->job->find.chain = *cx->emit_in->meas->chain;
        return;
    }
    if (o->analysis_source) {
        if (o->analysis_source_len > PCREC_MAX_FIND_BUNDLE_BYTES)
            pcrec_ctx_fail(cx, 0, "analysis_source: %zu bytes, over "
                           "PCREC_MAX_FIND_BUNDLE_BYTES (%llu)",
                           o->analysis_source_len,
                           (unsigned long long)PCREC_MAX_FIND_BUNDLE_BYTES);
        owned = pcrec_rxt_source_parse_buf("analysis_source",
                                           o->analysis_source,
                                           o->analysis_source_len, &ferr);
        if (!owned) pcrec_ctx_fail(cx, 0, "%s", ferr.msg);
        s1 = owned;
    }
#ifdef PCREC_KS_TRACE
    /* The lookup trace's ATTEMPT marker (findings.h): every record after it
     * belongs to this attempt. */
    fprintf(stderr, "KSTRACE\tanalysis\t-\tresolve\t-\n");
#endif
    rc = pcrec_find_chain_build(&cx->arena, o->analysis, s1, o->analysis_dirs,
                                notes, &cx->job->find.chain, &ferr);
    if (owned) pcrec_rxt_source_free(owned);
    if (rc != 0) pcrec_ctx_fail(cx, 0, "%s", ferr.msg);
    /* §9: the SELECTED chain declaring nothing under this `-e` leaves the
     * caller's evident intent unmet while a correct fallback exists — so a
     * note, computed at resolution and independent of the pattern. With no
     * analysis selected, `default`'s `byte`-only declaration is the normal
     * case and says nothing. */
    if (notes && o->analysis) {
        const char *enc = pcrec_enc_by_id(o->encoding)->name;
        if (!chain_serves_enc(&cx->job->find.chain, enc))
            fprintf(stderr, "pcrec: note: analysis '%s' declares no query "
                    "under -e %s; every rate reader takes its "
                    "no-information answer\n", o->analysis, enc);
    }
}
