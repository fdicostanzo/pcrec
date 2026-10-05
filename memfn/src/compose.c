/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text; no third-party source
 *   (memfn/PROVENANCE.md).
 *
 * memfn/src/compose.c — K2, the composer: the per-artifact state (mf_art),
 * the define/use split (integration.md §14.0), the first-match selection
 * over the arm table, and the artifact-level queries (helpers, includes,
 * stamps, vocabulary). The text of a site is the selected arm's; this file
 * decides only WHICH arm and keeps the handles honest.
 *
 * At R4a the table has one row, the generic scalar row (generic.c), and
 * pcrec calls none of this: the code links and nothing emits through it.
 */
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#include "kit.h"

/* ---- kb ------------------------------------------------------------------ */

void kb_init(kb *b, mf_arena *a)
{
    memset(b, 0, sizeof *b);
    b->a = a;
}

/* Grows to hold `need` more bytes plus a terminator, by doubling; the old
 * block stays in the arena (the arena owns it). */
static int kb_reserve(kb *b, size_t need)
{
    if (b->oom) return 0;
    if (b->len + need + 1 <= b->cap) return 1;
    size_t cap = b->cap ? b->cap : 256;
    while (cap < b->len + need + 1) cap *= 2;
    char *p = b->a->alloc(b->a->u, cap);
    if (!p) { b->oom = 1; return 0; }
    if (b->len) memcpy(p, b->p, b->len);
    p[b->len] = '\0';
    b->p = p;
    b->cap = cap;
    return 1;
}

void kb_putn(kb *b, const char *s, size_t n)
{
    if (!kb_reserve(b, n)) return;
    memcpy(b->p + b->len, s, n);
    b->len += n;
    b->p[b->len] = '\0';
}

void kb_puts(kb *b, const char *s)
{
    kb_putn(b, s, strlen(s));
}

void kb_printf(kb *b, const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    int need = vsnprintf(NULL, 0, fmt, ap);
    va_end(ap);
    if (need < 0 || !kb_reserve(b, (size_t)need)) return;
    va_start(ap, fmt);
    vsnprintf(b->p + b->len, (size_t)need + 1, fmt, ap);
    va_end(ap);
    b->len += (size_t)need;
}

int kit_fail(mf_art *art, const char *fmt, ...)
{
    if (art && !art->err[0]) {
        va_list ap;
        va_start(ap, fmt);
        vsnprintf(art->err, sizeof art->err, fmt, ap);
        va_end(ap);
    }
    return -1;
}

/* ---- the selection table --------------------------------------------------
 *
 * First passing row wins (the house's first-match idiom). Every row before
 * the last will carry its own `--memfn=no-NAME` deny when it lands (D144
 * item 4); the generic row has none, so no deny can leave a site without
 * code (§14.6). */
static const arm *const arms[] = {
    &generic_arm,
};

static const arm *select_arm(const mf_site *s)
{
    for (size_t i = 0; i < sizeof arms / sizeof arms[0]; i++)
        if (arms[i]->applies(s)) return arms[i];
    return NULL;
}

/* ---- the per-site vocabulary rules ----------------------------------------
 *
 * NULL iff the site is one the vocabulary describes, else why not. These
 * are the contract's rules, not an arm's: every arm renders every site that
 * passes, the generic row included (§8.2 "Totality"). (op, handoff, term
 * kinds) is mf_vocab_has's table; the form follows from the handoff. */

/* 1 iff `v` names a member of an enum whose members run 0..last: a field
 * outside its enum is refused like any other shape outside the vocabulary,
 * never given some reading (F3). */
static int in_enum(unsigned v, unsigned last)
{
    return v <= last;
}

/* Adds the term kinds one predicate uses to *kinds (MF_TK_* bits); 0 if a
 * term is malformed (sets *why). */
static int pred_kinds(const mf_pred *p, uint32_t *kinds, const char **why)
{
    if (p->nterm == 0) { *why = "a predicate with no terms (nterm 0)"; return 0; }
    if (p->nterm > MF_MAX_TERM) { *why = "nterm > MF_MAX_TERM"; return 0; }
    if (!in_enum(p->need, MF_OPTIONAL)) { *why = "predicate need outside mf_need"; return 0; }
    for (unsigned t = 0; t < p->nterm; t++) {
        const mf_term *tm = &p->term[t];
        if (tm->offset < -MF_MAX_BACK) { *why = "term offset < -MF_MAX_BACK"; return 0; }
        if (!in_enum(tm->need, MF_OPTIONAL)) { *why = "term need outside mf_need"; return 0; }
        if (tm->kind == MF_T_SET) {
            *kinds |= MF_TK_SET;
        } else if (tm->kind == MF_T_RUN) {
            if (tm->run_len == 0) { *why = "RUN term of length 0"; return 0; }
            if (!tm->run) { *why = "RUN term without bytes"; return 0; }
            /* a run byte with a bit its mask clears can never hold; the
             * literal formula would render a test that is always false */
            if (tm->mask)
                for (uint32_t j = 0; j < tm->run_len; j++)
                    if (tm->run[j] & (uint8_t)~tm->mask[j]) {
                        *why = "RUN byte has bits outside its mask";
                        return 0;
                    }
            *kinds |= MF_TK_RUN;
        } else {
            *why = "unknown term kind";
            return 0;
        }
    }
    return 1;
}

static const char *site_check(const mf_site *s)
{
    const char *why = NULL;
    uint32_t kinds = 0;
    if (!in_enum(s->form, MF_FORM_FUNC)) return "form outside mf_form";
    if (!in_enum(s->empty, MF_EMPTY_EXCLUDED)) return "empty outside mf_empty";
    if (!in_enum(s->use, MF_USE_DISCARD)) return "use outside mf_use_kind";
    if (!in_enum(s->consumer, MF_C_ENGINE)) return "consumer outside mf_consumer";
    if (s->end_back > 1) return "end_back is not 0 or 1";
    if (s->op == MF_OP_ALL_PRESENT) {
        if (s->npred && !s->preds) return "ALL_PRESENT without preds";
        for (unsigned i = 0; i < s->npred; i++)
            if (!pred_kinds(&s->preds[i], &kinds, &why)) return why;
        if (s->ret_pred != MF_NO_PRED && s->ret_pred >= s->npred)
            return "ret_pred outside preds";
        /* the handoff is ASSIGN/RETURN iff ret_pred names a pred (§R4.6.1 4) */
        int valued = s->handoff == MF_H_RETURN || s->handoff == MF_H_ASSIGN;
        if (valued != (s->ret_pred != MF_NO_PRED))
            return "ret_pred must be set exactly for RETURN/ASSIGN";
        if (s->reverse) return "ALL_PRESENT has no reverse reading";
    } else if (!pred_kinds(&s->pred, &kinds, &why)) {
        return why;
    }
    if (s->op == MF_OP_SKIP && (s->pred.nterm != 1 || s->pred.term[0].kind != MF_T_SET))
        return "SKIP takes exactly one SET term";
    if (s->op == MF_OP_SKIP && s->pred.term[0].offset != 0)
        return "SKIP's SET term is at offset 0 (the candidate's own byte)";
    if (!mf_vocab_has(s->op, s->handoff, kinds))
        return "(op, handoff, term kinds) is not in the vocabulary";

    int stmt = s->handoff == MF_H_ASSIGN || s->handoff == MF_H_ON_MISS
            || s->handoff == MF_H_ON_CAND || s->handoff == MF_H_ADVANCE;
    if (stmt != (s->form == MF_FORM_STMT))
        return stmt ? "this handoff is a STMT form" : "this handoff is an EXPR or FUNC form";
    if (s->empty == MF_EMPTY_NOP && s->form != MF_FORM_STMT)
        return "an EXPR or FUNC site cannot write nothing on an empty range";
    if (s->empty == MF_EMPTY_MISS && s->handoff == MF_H_ADVANCE)
        return "ADVANCE has no miss to give an empty range";
    if (s->guard_by_caller) {
        if (!(s->op == MF_OP_VERIFY && s->form == MF_FORM_EXPR))
            return "guard_by_caller is for an EXPR VERIFY only";
        for (unsigned t = 0; t < s->pred.nterm; t++)
            if (s->pred.term[t].offset < 0)
                return "guard_by_caller needs every term offset >= 0";
    }
    return NULL;
}

/* ---- mf_art -------------------------------------------------------------- */

mf_art *mf_art_begin(mf_arena *a, const char *prefix, uint32_t policy,
                     uint64_t denies)
{
    mf_art *art = a->alloc(a->u, sizeof *art);
    if (!art) return NULL;
    memset(art, 0, sizeof *art);
    art->a = a;
    art->prefix = prefix ? prefix : "mf";
    art->policy = policy;
    art->denies = denies;
    return art;
}

const char *mf_art_error(const mf_art *art)
{
    return art && art->err[0] ? art->err : NULL;
}

/* The record behind `handle`, or NULL after recording why. */
static site_rec *rec_of(mf_art *art, uint32_t handle, const char *who)
{
    if (handle == 0 || handle > art->nsites) {
        kit_fail(art, "%s: handle %u was never defined", who, handle);
        return NULL;
    }
    return &art->sites[handle - 1];
}

/* Writes a finished buffer to the sink; fails loudly on a dropped write. */
static int flush_to(mf_art *art, kb *b, mf_sink *out, const char *who)
{
    if (b->oom) return kit_fail(art, "%s: out of memory", who);
    if (b->len) {
        if (!out || !out->puts)
            return kit_fail(art, "%s: no sink to write to", who);
        out->puts(out->u, b->p);
    }
    return 0;
}

int mf_define(mf_art *art, const mf_site *s, const mf_hooks *def,
              mf_sink *file_scope, uint32_t *handle)
{
    if (art->err[0]) return -1;
    if (s->abi != MF_SITE_ABI)
        return kit_fail(art, "mf_define: site abi %u, kit abi %u", s->abi,
                        (unsigned)MF_SITE_ABI);
    const char *why = site_check(s);
    if (why)
        return kit_fail(art, "mf_define: outside the vocabulary: %s", why);
    const arm *row = select_arm(s);
    if (!row)
        return kit_fail(art, "mf_define: no arm applies (the generic row must)");

    if (art->nsites == art->cap) {
        uint32_t cap = art->cap ? art->cap * 2 : 8;
        site_rec *grown = art->a->alloc(art->a->u, cap * sizeof *grown);
        if (!grown) return kit_fail(art, "mf_define: out of memory");
        if (art->nsites) memcpy(grown, art->sites, art->nsites * sizeof *grown);
        art->sites = grown;
        art->cap = cap;
    }
    uint32_t h = ++art->nsites;
    site_rec *r = &art->sites[h - 1];
    memset(r, 0, sizeof *r);
    r->site = *s;
    r->arm = row;

    kb file;
    kb_init(&file, art->a);
    if (row->define(art, h, def, &file)) return -1;
    if (flush_to(art, &file, file_scope, "mf_define")) return -1;
    *handle = h;
    return 0;
}

int mf_use(mf_art *art, uint32_t handle, const mf_hooks *use, mf_sink *body,
           mf_result *res)
{
    if (art->err[0]) return -1;
    site_rec *r = rec_of(art, handle, "mf_use");
    if (!r) return -1;
    kb text;
    kb_init(&text, art->a);
    if (r->arm->use(art, handle, use, &text)) return -1;
    if (flush_to(art, &text, body, "mf_use")) return -1;
    r->used = 1;
    if (res) {
        memset(res, 0, sizeof *res);
        snprintf(res->form_id, sizeof res->form_id, "%s", r->arm->id);
        res->handle = handle;
    }
    return 0;
}

int mf_emit(mf_art *art, const mf_site *s, const mf_hooks *h, mf_sink *body,
            mf_sink *file_scope, mf_result *res)
{
    uint32_t handle;
    if (mf_define(art, s, h, file_scope, &handle)) return -1;
    return mf_use(art, handle, h, body, res);
}

int mf_call(mf_art *art, uint32_t handle, const mf_hooks *h, mf_sink *body)
{
    if (art->err[0]) return -1;
    site_rec *r = rec_of(art, handle, "mf_call");
    if (!r) return -1;
    if (r->site.form != MF_FORM_FUNC)
        return kit_fail(art, "mf_call: handle %u is not a FUNC site", handle);
    return mf_use(art, handle, h, body, NULL);
}

int mf_art_end(mf_art *art)
{
    if (art->err[0]) return -1;
    for (uint32_t i = 0; i < art->nsites; i++)
        if (!art->sites[i].used)
            return kit_fail(art, "mf_art_end: handle %u defined, never used",
                            i + 1);
    return 0;
}

/* The generic row declares no helper, so there is nothing to flush; a row
 * that needs one records it on the art and this writes it (§14.8). */
int mf_flush_helpers(mf_art *art, mf_sink *file_scope)
{
    (void)file_scope;
    return art->err[0] ? -1 : 0;
}

uint32_t mf_includes(const mf_art *art)
{
    return art->includes;
}

/* The kit's stamps are born at R4a′ (`<PREFIX>_MEMFN_FORMS`/`_LIBC`); until
 * then the kit writes none. */
int mf_stamps(const mf_art *art, mf_sink *out)
{
    (void)out;
    return art->err[0] ? -1 : 0;
}

/* ---- the vocabulary -------------------------------------------------------
 *
 * (op, handoff) pairs the kit renders, in some form, and the term kinds each
 * takes. generic_check holds the per-site rules; this is the same table at
 * DELEG_SITES' granularity (§8.2: a site whose op the vocabulary lacks is a
 * pcrec build failure, never a silent fallback). */
static const struct { mf_op op; mf_handoff h; uint32_t kinds; } vocab[] = {
    { MF_OP_FIND,        MF_H_RETURN,  MF_TK_SET | MF_TK_RUN },
    { MF_OP_FIND,        MF_H_BOOL,    MF_TK_SET | MF_TK_RUN },
    { MF_OP_FIND,        MF_H_ASSIGN,  MF_TK_SET | MF_TK_RUN },
    { MF_OP_FIND,        MF_H_ON_MISS, MF_TK_SET | MF_TK_RUN },
    { MF_OP_FIND,        MF_H_ON_CAND, MF_TK_SET | MF_TK_RUN },
    { MF_OP_SKIP,        MF_H_RETURN,  MF_TK_SET },
    { MF_OP_SKIP,        MF_H_ASSIGN,  MF_TK_SET },
    { MF_OP_SKIP,        MF_H_ADVANCE, MF_TK_SET },
    { MF_OP_VERIFY,      MF_H_BOOL,    MF_TK_SET | MF_TK_RUN },
    { MF_OP_VERIFY,      MF_H_ON_MISS, MF_TK_SET | MF_TK_RUN },
    { MF_OP_ALL_PRESENT, MF_H_RETURN,  MF_TK_SET | MF_TK_RUN },
    { MF_OP_ALL_PRESENT, MF_H_BOOL,    MF_TK_SET | MF_TK_RUN },
    { MF_OP_ALL_PRESENT, MF_H_ASSIGN,  MF_TK_SET | MF_TK_RUN },
    { MF_OP_ALL_PRESENT, MF_H_ON_MISS, MF_TK_SET | MF_TK_RUN },
};

int mf_vocab_has(mf_op op, mf_handoff h, uint32_t term_kinds)
{
    for (size_t i = 0; i < sizeof vocab / sizeof vocab[0]; i++)
        if (vocab[i].op == op && vocab[i].h == h)
            return (term_kinds & ~vocab[i].kinds) == 0;
    return 0;
}
