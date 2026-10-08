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
 * The table holds the scalar arms R4c, M1b and R4g migrated (ofsskip.c,
 * precheck.c, runcmp.c, pffind.c) above the generic scalar row (generic.c), which
 * applies to every site. Each arm carries its contract (`uses`/`serves`,
 * [MEMFN-ROWCON]); the gate (gate.c) reads it before the arm's predicate
 * and, since N3, ENFORCES: a row whose verdict fails is DECLINED and the
 * walk moves on, a site no row serves is REFUSED naming the fields, and the
 * chosen arm is re-checked at every use, a use it does not serve REFUSED
 * naming the fields (no re-selection: the definition is written).
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

/* Writes a finished buffer to the sink; fails loudly on a dropped write. */
int kit_flush(mf_art *art, kb *b, mf_sink *out, const char *who)
{
    if (b->oom) return kit_fail(art, "%s: out of memory", who);
    if (b->len) {
        if (!out || !out->puts)
            return kit_fail(art, "%s: no sink to write to", who);
        out->puts(out->u, b->p);
    }
    return 0;
}

int kit_sink_ok(mf_art *art, const mf_sink *o, const char *who)
{
    if (!o || !o->puts || !o->vprintf)
        return kit_fail(art, "%s: the sink offers no puts/vprintf", who);
    return 0;
}

void kit_out(mf_sink *o, const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    o->vprintf(o->u, fmt, ap);
    va_end(ap);
}

/* ---- the selection table --------------------------------------------------
 *
 * First passing row wins (the house's first-match idiom). Every row before
 * the last will carry its own `--memfn=no-NAME` deny when it lands (D144
 * item 4); the generic row has none, so no deny can leave a site without
 * code (§14.6). The rows above it are the SCALAR ARMS born at R4c's, M1b's
 * and R4g's migrations (integration.md §15, §16, §R4.8): pcrec's offset-skip
 * block, its pre-check, its run compare and its prefilter find, transcribed. They are not
 * byte-moving changes, so they carry no deny of their own: the artifacts
 * they render are the ones pcrec wrote before them, and the identity gates
 * say so (§9.3). The pre-check is one renderer as two rows (N3's split, by
 * handoff: precheck.c), each with its own contract; the prefilter find is
 * two renderers as five rows (split by end_back and the term's offset:
 * pffind.c; M4 added pf_memchr_back, R-7). The MISMATCH (M7, R-8) is ONE
 * renderer (mismatch.c) as two rows: `mismatch_inplace` here for the
 * in-place fold, the generic row for the exact and expression folds. */
static const arm *const arms[] = {
    &ofsskip_arm,
    &precheck_arm,
    &precheck_assign_arm,
    &runcmp_arm,
    &pf_memchr_arm,
    &pf_memchr_bounded_arm,
    &pf_walk_arm,
    &pf_walk_bounded_arm,
    &pf_memchr_back_arm,
    &mismatch_inplace_arm,
    &generic_arm,
};

/* The first row the gate passes AND whose predicate holds. The gate reads
 * each row's contract before its predicate ([MEMFN-ROWCON] N3,
 * row_contracts.md §2): a failing row is DECLINED and its predicate is not
 * asked. NULL when no row serves; `*why` is then the last declined row's
 * verdict (the generic row's, the table's total fallback), whose fields the
 * refusal names. `gphases` is what the gate reads in this walk: MF_PH_DEFINE
 * for mf_define; MF_PH_DEFINE | MF_PH_USE for a one-call entry (mf_emit),
 * which holds the use hooks at selection time, so a row whose use-time
 * fields the hooks fail to serve is DECLINED here instead of chosen and then
 * refused by mf_use's re-check. The trace still labels the walk `define`. */
/* Row `a`'s predicate columns over the site and its define hooks. */
static int arm_holds(const arm *a, const mf_site *s, const mf_hooks *def)
{
    return (!a->miss_leaves || s->on_miss_leaves) && a->applies(s, def);
}

static const arm *select_arm(const mf_art *art, const mf_site *s,
                             const mf_hooks *def, unsigned gphases,
                             gate_verdict *why)
{
    gate_in in = { s, def, NULL };
    gate_tctx tc = { art, "arms", art->nsites + 1, MF_PH_DEFINE, &in };
    const gate_contract *mc = NULL;     /* trace only: the row the gate moved off */
    gate_verdict mv = { 0, 0 };
    gate_trace_sel(&tc);
    for (size_t i = 0; i < sizeof arms / sizeof arms[0]; i++) {
        gate_verdict v = gate_check(arms[i]->ct, gphases, &in);
        if (v.r1 | v.r2) {
            int held = GATE_TRACING && arm_holds(arms[i], s, def);
            if (held && !mc) { mc = arms[i]->ct; mv = v; }
            gate_trace_row(&tc, arms[i]->ct,
                           held ? "DECLINED:PRED_HOLDS" : "DECLINED", 0, &v);
            *why = v;
            continue;
        }
        if (arm_holds(arms[i], s, def)) {
            gate_trace_row(&tc, arms[i]->ct, "CHOSEN", 0, &v);
            gate_trace_end(&tc, arms[i]->ct, &v, mc, &mv);
            return arms[i];
        }
        gate_trace_row(&tc, arms[i]->ct, "PRED_FALSE", 0, &v);
    }
    gate_trace_end(&tc, NULL, why, mc, &mv);
    return NULL;
}

const gate_contract *kit_arm_contract(size_t i)
{
    return i < sizeof arms / sizeof arms[0] ? arms[i]->ct : NULL;
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
            *kinds |= MF_TK_RUN;
        } else if (tm->kind == MF_T_REF) {
            *kinds |= MF_TK_REF;    /* its operands are hooks: no data to check */
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
    if (!in_enum(s->empty, MF_EMPTY_AT_N)) return "empty outside mf_empty";
    if (!in_enum(s->use, MF_USE_DISCARD)) return "use outside mf_use_kind";
    if (!in_enum(s->consumer, MF_C_ENGINE)) return "consumer outside mf_consumer";
    if (s->end_back > 1) return "end_back is not 0 or 1";
    if (s->on_miss_leaves != 0 && s->on_miss_leaves != 1)
        return "on_miss_leaves is not 0 or 1";
    if (s->on_miss_leaves && s->handoff != MF_H_ON_MISS && s->handoff != MF_H_ASSIGN &&
        s->handoff != MF_H_ON_DIFF)
        return "on_miss_leaves is for an ON_MISS/ASSIGN/ON_DIFF site only";
    if (s->count_by_caller > 1) return "`count_by_caller` is not 0 or 1";
    if (s->count_by_caller && s->handoff != MF_H_ADVANCE)
        return "`count_by_caller` is for an ADVANCE site only (Q-R4h-1 (a))";
    if (!in_enum(s->fold_kind, MF_FOLD_UCP)) return "`fold_kind` outside mf_fold";
    if (s->fold_kind && s->op != MF_OP_MISMATCH)
        return "`fold_kind` is for a MISMATCH site only (Q-R8-4)";
    if (s->op == MF_OP_MISMATCH) {
        /* F8's shape (RULED Q-R8-2/4/5, MF_VOCAB 3): one REQUIRED REF term at
           offset 0, forward over [lo, n), its empty reference EQUAL, and an
           on_miss that leaves the kit's loop */
        const mf_pred *p = &s->pred;
        if (p->nterm != 1 || p->term[0].kind != MF_T_REF)
            return "MISMATCH takes exactly one REF term (`pred`)";
        if (p->term[0].offset != 0 || p->term[0].need != MF_REQUIRED)
            return "MISMATCH's REF term is REQUIRED at offset 0 (`pred`)";
        if (s->reverse) return "MISMATCH has no reverse reading (`reverse`)";
        if (s->end_back) return "MISMATCH reads [lo, n): `end_back` is 0";
        if (s->empty != MF_EMPTY_NOP)
            return "MISMATCH's empty reference is EQUAL: `empty` is NOP";
        if (s->handoff == MF_H_ON_DIFF && s->on_miss_leaves != 1)
            return "ON_DIFF's on_miss must leave the kit's loop (`on_miss_leaves` 1)";
    }
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
            || s->handoff == MF_H_ON_CAND || s->handoff == MF_H_ADVANCE
            || s->handoff == MF_H_ON_DIFF;
    if (stmt != (s->form == MF_FORM_STMT))
        return stmt ? "this handoff is a STMT form" : "this handoff is an EXPR or FUNC form";
    if (s->empty == MF_EMPTY_NOP && s->form != MF_FORM_STMT)
        return "an EXPR or FUNC site cannot write nothing on an empty range";
    if ((s->empty == MF_EMPTY_MISS || s->empty == MF_EMPTY_AT_N) &&
        s->handoff == MF_H_ADVANCE)
        return "ADVANCE has no miss to give an empty range (`empty`)";
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
    gate_trace_art(art);
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

/* mf_define's body, over the phases the selection gate reads. */
static int define_sel(mf_art *art, const mf_site *s, const mf_hooks *def,
                      mf_sink *file_scope, uint32_t *handle, unsigned gphases)
{
    if (art->err[0]) return -1;
    if (s->abi != MF_SITE_ABI)
        return kit_fail(art, "mf_define: site abi %u, kit abi %u", s->abi,
                        (unsigned)MF_SITE_ABI);
    const char *why = site_check(s);
    if (why)
        return kit_fail(art, "mf_define: outside the vocabulary: %s", why);
    /* the compile's denies are one value (RULED Q-M1b-1): a site's text and
       the art's helpers and stamps read the same ones */
    if (s->denies != art->denies)
        return kit_fail(art, "mf_define: site denies 0x%llx are not the art's 0x%llx",
                        (unsigned long long)s->denies,
                        (unsigned long long)art->denies);
    gate_verdict declined = { 0, 0 };
    const arm *row = select_arm(art, s, def, gphases, &declined);
    if (!row) {
        /* the generic row applies to every site, so only the gate can leave
           a site with no row: name what it declined (ruling (d)) */
        gate_in in = { s, def, NULL };
        char f[200];
        gate_describe(f, sizeof f, &declined, &in);
        return kit_fail(art, "mf_define: no row serves this site: %s",
                        f[0] ? f : "(no row applies; the generic row must)");
    }

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

    if (row->define(art, h, def, file_scope)) return -1;
    *handle = h;
    return 0;
}

int mf_define(mf_art *art, const mf_site *s, const mf_hooks *def,
              mf_sink *file_scope, uint32_t *handle)
{
    return define_sel(art, s, def, file_scope, handle, MF_PH_DEFINE);
}

int mf_use(mf_art *art, uint32_t handle, const mf_hooks *use, mf_sink *body,
           mf_result *res)
{
    if (art->err[0]) return -1;
    site_rec *r = rec_of(art, handle, "mf_use");
    if (!r) return -1;
    /* the gate's re-check of the chosen row against the use hooks: the
       definition is written, so a use it does not serve is REFUSED, naming
       the fields; it cannot re-select (N3) */
    gate_in in = { &r->site, use, NULL };
    gate_tctx tc = { art, "arms", handle, MF_PH_USE, &in };
    gate_verdict v = gate_check(r->arm->ct, MF_PH_USE, &in);
    gate_trace_sel(&tc);
    gate_trace_row(&tc, r->arm->ct, "RECHECK", 0, &v);
    gate_trace_end(&tc, r->arm->ct, &v, NULL, NULL);
    if (v.r1 | v.r2) {
        char f[200];
        gate_describe(f, sizeof f, &v, &in);
        return kit_fail(art, "mf_use: row `%s` does not serve this use of handle %u: %s",
                        r->arm->ct->row, handle, f);
    }
    if (r->arm->use(art, handle, use, body)) return -1;
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
    /* define and use hooks are the same here: select over both phases */
    if (define_sel(art, s, h, file_scope, &handle, MF_PH_DEFINE | MF_PH_USE))
        return -1;
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

uint32_t mf_includes(const mf_art *art)
{
    return art->includes;
}

/* §R4.3.3: sorted insertion, so mf_stamps writes the list as it stands. */
int mf_art_note_libc(mf_art *art, const char *name)
{
    if (art->err[0]) return -1;
    if (!kit_is_ident(name))
        return kit_fail(art, "mf_art_note_libc: not a C identifier");
    uint32_t at = 0;
    while (at < art->nlibc) {
        int c = strcmp(art->libc[at], name);
        if (c == 0) return 0;
        if (c > 0) break;
        at++;
    }
    if (art->nlibc == art->libc_cap) {
        uint32_t cap = art->libc_cap ? art->libc_cap * 2 : 8;
        const char **grown = art->a->alloc(art->a->u, cap * sizeof *grown);
        if (!grown) return kit_fail(art, "mf_art_note_libc: out of memory");
        if (art->nlibc) memcpy(grown, art->libc, art->nlibc * sizeof *grown);
        art->libc = grown;
        art->libc_cap = cap;
    }
    size_t len = strlen(name);
    char *copy = art->a->alloc(art->a->u, len + 1);
    if (!copy) return kit_fail(art, "mf_art_note_libc: out of memory");
    memcpy(copy, name, len + 1);
    memmove(art->libc + at + 1, art->libc + at,
            (art->nlibc - at) * sizeof *art->libc);
    art->libc[at] = copy;
    art->nlibc++;
    return 0;
}

/* RUN_WORDS is the run compare's count (runcmp.c). MEMFN_FORMS is "none": no
 * arm the table holds renders differently from its SIMD-off self (every arm
 * is a scalar arm), so every artifact equals its SIMD-off compile (Q55; the
 * id list is R4f's). */
int mf_stamps(const mf_art *art, mf_sink *out)
{
    if (art->err[0]) return -1;
    if (!out || !out->stamp || !out->stamp_int)
        return kit_fail((mf_art *)art, "mf_stamps: the sink offers no stamp/stamp_int op");
    kb libc;
    kb_init(&libc, art->a);
    for (uint32_t i = 0; i < art->nlibc; i++)
        kb_printf(&libc, "%s%s", i ? "," : "", art->libc[i]);
    if (libc.oom) return kit_fail((mf_art *)art, "mf_stamps: out of memory");
    out->stamp_int(out->u, "RUN_WORDS", art->words);
    out->stamp(out->u, "MEMFN_FORMS", "none");
    out->stamp(out->u, "MEMFN_LIBC", art->nlibc ? libc.p : "none");
    return 0;
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
    { MF_OP_MISMATCH,    MF_H_ON_DIFF, MF_TK_REF },  /* MF_VOCAB 3 (M7, R-8) */
};

int mf_vocab_has(mf_op op, mf_handoff h, uint32_t term_kinds)
{
    for (size_t i = 0; i < sizeof vocab / sizeof vocab[0]; i++)
        if (vocab[i].op == op && vocab[i].h == h)
            return (term_kinds & ~vocab[i].kinds) == 0;
    return 0;
}
