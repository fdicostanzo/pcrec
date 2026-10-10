/* SPDX-License-Identifier: 0BSD
 * Provenance: pcrec 691a8b7c (relicensed 0BSD by its author, D145 addendum 1):
 *   src/gen/emit_dfa.c (ofs_test_emit_fn, ofs_test_emit_pair,
 *   ofsk_emit_verify, ofsk_emit_params, pf_block_ofs's comment), transcribed
 *   (memfn/PROVENANCE.md).
 *
 * memfn/src/ofsskip.c — THE OFFSET-SKIP FUNCTION, a scalar arm born at R4c
 * (integration.md §15.1, §16): a file-scope `static inline size_t` that
 * returns the first position >= `pos` at which every term of one predicate
 * holds, or `n`. Two sites render through it: the offset-skip site itself
 * (`ofsskip_arm`, FIND / FUNC / RETURN, pcrec's prefilter block) and the
 * pre-check composite's FUNC parts (precheck.c). Since R4e'.0b (D155 item
 * 6) the work is the helper `<fn>__body` and the function itself is its
 * SELECTOR, whose whole body is one call (see THE SEAM below).
 *
 * THE FORM. One `memchr` stream on the scanned term (`plan_hint`, and
 * `plan_pos` inside a RUN term), then at each hit the other terms in array
 * order, a failed candidate resuming one position later. A RUN term whose
 * scanned position is a two-member cube takes the PAIR leapfrog instead:
 * one `memchr` stream per member, the nearer hit taken.
 *
 * THE RETURNED POSITION IS THE CONTRACT, not only its comparison with `n`
 * (pcrec's litscan_k82h.md §1.1a): the leftmost position >= `pos` at which
 * every term holds. pcrec's handoff reads it as a scan start, so an arm that
 * returned "some occurrence" would be a correct discard gate and a wrong
 * handoff gate. The pair arm keeps it by taking the LESSER hit and searching
 * both streams fresh per call.
 *
 * EVERY SEARCH IS INSIDE THE GUARDED LOOP: `pos + maxk < n`, maxk the
 * largest byte any term reads, makes every `memchr` length at least 1 and
 * every pointer inside the subject, so no `memchr(NULL, c, 0)` is ever
 * formed on an empty subject. A stream is re-searched iff its hit lies below
 * `pos + k`: after a failed verify `pos = cand + 1`, and a bound of `< pos`
 * would keep the hit that produced `cand` and never advance.
 *
 * The function's parameters and locals are the arm's own names (`subject`,
 * `n`, `pos`, `cand`, `q`; the pair arm's `ha`, `hb`, `fresh`): its scope is
 * its own, so the definition takes no subject or bound hook. The call passes
 * the caller's `s`, `n` and `lo`. The run compare is the kit's own (runcmp.c,
 * since M1b) and a multi-byte set's table is pcrec's (`table_name`, rule 7).
 *
 * The function's miss is its `n` and its reads are bounded by `pos` and `n`,
 * so the arm serves only a site whose `miss` is STATED as `n` (MF_MISS_N, or
 * the `n` hook's own text) and that states no `floor` (K96: lane m1bfix's G2
 * sites, a `((size_t)-1)` miss and a floor above `lo`). Since N3 that is the
 * row contract's, at the end of this file, and the gate's, not this file's
 * code: the define walk DECLINES the row for any other `miss` (an unstated
 * one included, R1) or a stated `floor` (R2), so the site is the generic
 * row's; a call whose hooks do so is REFUSED by `mf_use`'s re-check, naming
 * the field. The ad hoc tests that did both before N3 are deleted.
 */
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#include "kit.h"

/* How many bytes the 256-bit set holds. */
static int set_count(const uint8_t set[32])
{
    int n = 0;
    for (int i = 0; i < 32; i++) n += __builtin_popcount(set[i]);
    return n;
}

/* The set's lowest byte (its only one, where it holds one). */
static int set_first(const uint8_t set[32])
{
    for (int b = 0; b < 256; b++)
        if ((set[b >> 3] >> (b & 7)) & 1) return b;
    return -1;
}

/* The mask byte of RUN term `t` at position `j` (0xFF where exact). */
static int run_mask_at(const mf_term *t, int j)
{
    return t->mask ? t->mask[j] : 0xFF;
}

/* The largest offset from the candidate any term of `p` reads: the loop
 * guard's `maxk`. */
static int max_reach(const mf_pred *p)
{
    int maxk = 0;
    for (unsigned i = 0; i < p->nterm; i++) {
        const mf_term *t = &p->term[i];
        int last = t->offset + (t->kind == MF_T_RUN ? (int)t->run_len : 1) - 1;
        if (last > maxk) maxk = last;
    }
    return maxk;
}

/* Is term `i` the scanned term that is NOT re-verified at the candidate (a
 * SET: the scan proved it)? A scanned RUN term is compared whole. */
static int scan_only(const mf_pred *p, unsigned i)
{
    return i == p->plan_hint && p->term[i].kind == MF_T_SET;
}

/* The function bounds its reads by `pos` and `n` only, so it serves no
 * stated `floor` (§14.7): the row contracts of its two customers say so
 * (ofsskip's, precheck's), and the gate declines such a site before this
 * predicate is asked (N3). pcrec states none at OFS/PRE. */
int ofs_fn_applies(const mf_pred *p, const mf_hooks *def)
{
    if (!def || p->nterm == 0 || p->nterm > MF_MAX_TERM ||
        p->plan_hint >= p->nterm)
        return 0;
    int runs = 0, checked = 0;
    for (unsigned i = 0; i < p->nterm; i++) {
        const mf_term *t = &p->term[i];
        if (t->offset < 0) return 0;
        if (t->kind == MF_T_RUN) {
            if (!run_cmp_sat(t)) return 0;
            runs++;
        } else {
            int c = set_count(t->set);
            if (c == 0 || (c > 1 && (!t->table_ref || !def->table_name))) return 0;
        }
        if (!scan_only(p, i)) checked++;
    }
    const mf_term *sc = &p->term[p->plan_hint];
    if (sc->kind == MF_T_SET && set_count(sc->set) != 1) return 0;
    if (sc->kind == MF_T_RUN) {
        if (p->plan_pos >= sc->run_len) return 0;
        int m = run_mask_at(sc, p->plan_pos);
        /* exact, or a two-member cube whose run byte is its lower member */
        if (m != 0xFF && (__builtin_popcount(~m & 0xFF) != 1 ||
                          (sc->run[p->plan_pos] & ~m & 0xFF)))
            return 0;
    }
    return runs <= 1 && checked > 0;
}

void ofs_fn_scan(const mf_pred *p, int *k, int *a, int *b)
{
    const mf_term *sc = &p->term[p->plan_hint];
    if (sc->kind == MF_T_SET) {
        *k = sc->offset;
        *a = set_first(sc->set);
        *b = -1;
        return;
    }
    int m = run_mask_at(sc, p->plan_pos);
    *k = sc->offset + p->plan_pos;
    *a = sc->run[p->plan_pos];
    *b = m != 0xFF ? (*a | (~m & 0xFF)) : -1;
}

/* The table pcrec names for multi-byte SET term `t`, or NULL after
 * recording why. */
static const char *table_of(mf_art *art, const mf_hooks *h, const mf_term *t)
{
    const char *tbl = h && h->table_name ? h->table_name(h->u, t->table_ref) : NULL;
    if (!tbl || !*tbl)
        kit_fail(art, "ofsskip: no table name for table_ref %u", t->table_ref);
    return tbl;
}

/* The tables the function takes, in the verify chain's order: `, const
 * unsigned char *<table>` in the definition, `, <table>` in a call. */
static int table_params(mf_art *art, const mf_hooks *h, const mf_pred *p,
                        int decl, mf_sink *o)
{
    for (unsigned i = 0; i < p->nterm; i++) {
        const mf_term *t = &p->term[i];
        if (scan_only(p, i) || t->kind != MF_T_SET || set_count(t->set) <= 1)
            continue;
        const char *tbl = table_of(art, h, t);
        if (!tbl) return -1;
        kit_out(o, ", %s%s", decl ? "const unsigned char *" : "", tbl);
    }
    return 0;
}

/* The `if (...)` a candidate must pass: every term but the scanned SET, in
 * the predicate's order (pcrec sends them ascending by offset, so a reader
 * of the artifact sees the pattern's own order). A singleton set is a byte
 * compare, a wider one a probe of pcrec's table, a run the kit's run compare
 * (runcmp.c) at the term's offset from the candidate. */
static int verify_chain(mf_art *art, const mf_hooks *h, const mf_pred *p,
                        mf_sink *o)
{
    int first = 1;
    for (unsigned i = 0; i < p->nterm; i++) {
        const mf_term *t = &p->term[i];
        if (scan_only(p, i)) continue;
        o->puts(o->u, first ? "" : " &&\n            ");
        first = 0;
        if (t->kind == MF_T_RUN) {
            if (run_cmp_render(art, t, "subject + cand", t->offset, o))
                return -1;
        } else if (set_count(t->set) == 1) {
            if (t->offset == 0) kit_out(o, "subject[cand] == %d", set_first(t->set));
            else kit_out(o, "subject[cand + %d] == %d", t->offset, set_first(t->set));
        } else {
            const char *tbl = table_of(art, h, t);
            if (!tbl) return -1;
            if (t->offset == 0) kit_out(o, "%s[subject[cand]]", tbl);
            else kit_out(o, "%s[subject[cand + %d]]", tbl, t->offset);
        }
    }
    return first ? kit_fail(art, "ofsskip: an empty verify chain") : 0;
}

/* ---- THE FUNCTION'S BODY, a selected row table: fn_rows[] -----------------
 *
 * integration.md §R4.9.2.1, step R4e'.0 (the seam): the function's text is
 * ONE first-match table, `fn_rows[]`, walked by the kit's shared walk
 * (kit_walk) over the calling site, its define hooks and the predicate. Each
 * row has a SLOT, the question it answers:
 *   BODY    which scalar loop is the function's body: `fn-pair` (the scanned
 *           position is a two-member cube: the PAIR leapfrog) above
 *           `fn-memchr` (otherwise: one `memchr` stream), the slot's floor,
 *           reached only where `fn-pair` did not hold;
 *   PREFIX  which guarded per-level helper DEFINITIONS sit at file scope
 *           beside the body (D155). BORN EMPTY: an empty slot renders zero
 *           bytes, and SIMD rows arrive as its rows (batch 1).
 * BODY is asked first, so the floor is known before any PREFIX row is asked,
 * and the PREFIX walk is handed the chosen BODY row and its helper's name.
 * Neither row calls, wraps or splices the other: the seam (ofs_fn_define)
 * owns the order, and each row writes only its own slot. Both BODY rows are
 * scalar and move no byte, so neither has an options.def deny. */

enum { FN_BODY, FN_PREFIX };

/* The walk's input is kit.h's `fn_in` (shared with the PREFIX rows' file,
 * vrun.c). One row: its slot, its predicate over the input and the text it
 * writes (BODY rows), or its declaration (PREFIX rows: the SIMD rows, whose
 * predicate is prefix_holds over the declaration and whose text the seam
 * frames, R4e' batch 1); and its contract. */
typedef struct fn_row {
    int slot;
    int (*holds)(const fn_in *x);
    int (*render)(mf_art *art, const mf_hooks *h, const fn_in *x, mf_sink *o);
    const gate_contract *ct;
    const mf_formdecl *decl;
} fn_row;

/* fn-pair's body: two `memchr` streams, members `a` and `b` of the cube at
 * offset `k`, each holding its one pending hit as an OFFSET (never a
 * pointer, so nothing NULL is compared relationally). `fresh` makes the
 * first iteration search both. */
static int pair_body(mf_art *art, const mf_hooks *h, const fn_in *x, mf_sink *o)
{
    const mf_pred *p = x->p;
    int maxk = x->maxk, k = x->k, a = x->a, b = x->b;
    kb at, len;
    kb_init(&at, art->a);
    kb_init(&len, art->a);
    if (k) { kb_printf(&at, "pos + %d", k); kb_printf(&len, "n - pos - %d", k); }
    else   { kb_puts(&at, "pos");          kb_puts(&len, "n - pos"); }
    if (at.oom || len.oom) return kit_fail(art, "ofsskip: out of memory");
    const char *lim = at.p;   /* the re-search bound: a hit below pos + k is stale */

    o->puts(o->u, "    size_t ha = 0, hb = 0;\n"
                  "    int fresh = 1;\n");
    kit_out(o, "    while (pos + %d < n) {\n", maxk);
    o->puts(o->u,   "        size_t cand;\n");
    kit_out(o, "        if (fresh || ha < %s) {\n"
               "            const void *q = memchr(subject + %s, %d, %s);\n"
               "            ha = q ? (size_t)((const unsigned char *)q - subject) : n;\n"
               "        }\n", lim, at.p, a, len.p);
    kit_out(o, "        if (fresh || hb < %s) {\n"
               "            const void *q = memchr(subject + %s, %d, %s);\n"
               "            hb = q ? (size_t)((const unsigned char *)q - subject) : n;\n"
               "        }\n", lim, at.p, b, len.p);
    o->puts(o->u,   "        fresh = 0;\n"
                    "        cand = ha < hb ? ha : hb;\n"
                    "        if (cand >= n) return n;\n");
    if (k) kit_out(o, "        cand -= %d;\n", k);
    kit_out(o, "        if (cand + %d >= n) return n;\n", maxk);
    o->puts(o->u,   "        if (");
    if (verify_chain(art, h, p, o)) return -1;
    o->puts(o->u,   ") return cand;\n"
                    "        pos = cand + 1;\n"
                    "    }\n"
                    "    return n;\n}\n\n");
    return 0;
}

/* fn-memchr's body: one `memchr` stream on byte `a` at offset `k`. */
static int memchr_body(mf_art *art, const mf_hooks *h, const fn_in *x, mf_sink *o)
{
    const mf_pred *p = x->p;
    int maxk = x->maxk, k = x->k, a = x->a;
    kit_out(o, "    while (pos + %d < n) {\n", maxk);
    o->puts(o->u,   "        size_t cand;\n");
    /* THE memchr FORM. `pos + maxk < n` above implies `pos + k < n`, so the
     * pointer is inside the subject and the length is non-zero. No `+ 0`
     * at k == 0: an unsigned `>= 0` would be a -Wtype-limits finding. */
    if (k == 0)
        kit_out(o, "        const void *q = memchr(subject + pos, %d, n - pos);\n", a);
    else
        kit_out(o, "        const void *q = memchr(subject + pos + %d, %d, n - pos - %d);\n",
                k, a, k);
    o->puts(o->u,   "        if (!q) return n;\n");
    if (k == 0)
        o->puts(o->u, "        cand = (size_t)((const unsigned char *)q - subject);\n");
    else
        kit_out(o, "        cand = (size_t)((const unsigned char *)q - subject) - %d;\n", k);
    kit_out(o, "        if (cand + %d >= n) return n;\n", maxk);
    o->puts(o->u,   "        if (");
    if (verify_chain(art, h, p, o)) return -1;
    o->puts(o->u,   ") return cand;\n");
    o->puts(o->u,   "        pos = cand + 1;\n"
                    "    }\n"
                    "    return n;\n}\n\n");
    return 0;
}

/* The scanned position is a two-member cube (today's `b >= 0`). */
static int pair_holds(const fn_in *x)
{
    return x->b >= 0;
}

/* The slot's floor: every predicate ofs_fn_applies admits scans one byte
 * where fn-pair did not hold (ofs_fn_scan), and first-match order puts this
 * row below it. */
static int memchr_holds(const fn_in *x)
{
    (void)x;
    return 1;
}

static const gate_contract fn_pair_ct, fn_memchr_ct;

/* A PREFIX row's predicate, walk tests 3-5 of §R4.9.2.3 over its
 * declaration (tests 1-2, the deny and the gate, are kit_walk's): REACH,
 * the site's proven span is not shorter than the row's derived reach (an
 * unbounded span passes); OVER, the chosen BODY row is one the row sits
 * over; APPLIES, the row's own shape. The define sink must offer the
 * bracket ops (a host that cannot count guarded bytes gets none). As built,
 * REACH and OVER are this predicate's first two conjuncts, not walk tests
 * of their own: they read the declaration and the chosen BODY row, which
 * only this table has; the verdict is the same PRED_FALSE. */
static int prefix_holds(const mf_formdecl *d, const fn_in *x)
{
    if (!x->brackets) return 0;
    uint32_t reach = d->reach(x->site, x->p);
    if (x->site->span_hi != MF_SPAN_UNBOUNDED && x->site->span_hi < reach)
        return 0;
    int over = 0;
    for (const char *const *o = d->over; *o && !over; o++)
        over = x->body_row && strcmp(*o, x->body_row) == 0;
    return over && d->applies(x->site, x->p);
}

static const fn_row fn_rows[] = {
    { FN_BODY, pair_holds,   pair_body,   &fn_pair_ct,   NULL },
    { FN_BODY, memchr_holds, memchr_body, &fn_memchr_ct, NULL },
    /* FN_PREFIX (R4e' batch 1, §R4.9.2.4): the SIMD rows, first match, the
       widest level first; a chosen row's narrower rungs are its NAMED ones */
    { FN_PREFIX, NULL, NULL, &vrun_w32_ct, &vrun_w32_decl },
    { FN_PREFIX, NULL, NULL, &vrun_w16_ct, &vrun_w16_decl },
};
#define NFN (sizeof fn_rows / sizeof fn_rows[0])

static const gate_contract *fn_ct(size_t i)
{
    return fn_rows[i].ct;
}

static int fn_slot(size_t i)
{
    return fn_rows[i].slot;
}

static int fn_row_holds(size_t i, const void *x)
{
    return fn_rows[i].decl ? prefix_holds(fn_rows[i].decl, x) : fn_rows[i].holds(x);
}

/* A SIMD row's options.def name: its `--memfn=no-<name>` deny (walk test 1).
 * The BODY rows move no byte and have none. */
static const char *fn_opt(size_t i)
{
    return fn_rows[i].decl ? fn_rows[i].decl->opt : NULL;
}

static const kit_table fn_table = { "fn", NFN, fn_ct, fn_slot, NULL, fn_row_holds, fn_opt };

const gate_contract *fn_row_contract(size_t i)
{
    return i < NFN ? fn_rows[i].ct : NULL;
}

/* The row slot `slot` chooses for predicate `x` of site `handle`, NULL when
 * none does. A BODY with no row is an error (the slot has a floor); an empty
 * PREFIX is the ordinary answer, and renders nothing. */
static const fn_row *fn_select(mf_art *art, uint32_t handle, const mf_hooks *h,
                               const fn_in *x, int slot)
{
    gate_in in = { &art->sites[handle - 1].site, h, NULL };
    gate_tctx tc = { art, "fn", handle, MF_PH_DEFINE, &in, slot == FN_PREFIX };
    gate_verdict why = { 0, 0 };
    size_t i = kit_walk(&fn_table, slot, &in, MF_PH_DEFINE, art->denies, x, &tc, &why);
    if (i < NFN) return &fn_rows[i];
    if (slot == FN_BODY) {
        char f[200];
        gate_describe(f, sizeof f, &why, &in);
        kit_fail(art, "ofsskip: no fn row serves the function's body: %s",
                 f[0] ? f : "(no row applies; the slot lost its floor)");
    }
    return NULL;
}

/* The PREFIX row named `name` (a declaration's rung), NFN when none. */
static size_t fn_row_named(const char *name)
{
    for (size_t i = 0; i < NFN; i++)
        if (fn_rows[i].decl && strcmp(fn_rows[i].decl->opt, name) == 0) return i;
    return NFN;
}

/* The RENDERED rungs, top-down (§R4.9.2.3 "the ladder"): the chosen PREFIX
 * row, then each rung its declaration NAMES, re-asked walk tests 1-5 by
 * kit_ask (a rung that fails is skipped, and traced). Their count. */
static unsigned fn_rungs(mf_art *art, uint32_t handle, const mf_hooks *h,
                         const fn_in *x, const fn_row *top,
                         const fn_row *rung[MF_NLEVEL])
{
    unsigned nr = 0;
    rung[nr++] = top;
    gate_in in = { &art->sites[handle - 1].site, h, NULL };
    gate_tctx tc = { art, "fn", handle, MF_PH_DEFINE, &in, 1 };
    for (const char *const *r = top->decl->rungs; *r && nr < MF_NLEVEL; r++) {
        size_t i = fn_row_named(*r);
        if (i < NFN && kit_ask(&fn_table, i, &in, MF_PH_DEFINE, art->denies, x, &tc))
            rung[nr++] = &fn_rows[i];
    }
    return nr;
}

/* `static inline size_t <name>(const unsigned char *subject, size_t n,
 * size_t pos[, tables])` and the opening brace: the one head every piece of
 * the function shares, so every call forwards the same argument list. */
static int fn_head(mf_art *art, const mf_hooks *h, const mf_pred *p,
                   const char *name, mf_sink *o)
{
    kit_out(o, "static inline size_t %s(const unsigned char *subject, size_t n, size_t pos", name);
    if (table_params(art, h, p, 1, o)) return -1;
    o->puts(o->u, ")\n{\n");
    return 0;
}

/* `    return <callee>(subject, n, pos[, tables]);`, the one call a selector
 * arm makes. */
static int fn_call_line(mf_art *art, const mf_hooks *h, const mf_pred *p,
                        const char *callee, mf_sink *o)
{
    kit_out(o, "    return %s(subject, n, pos", callee);
    if (table_params(art, h, p, 0, o)) return -1;
    o->puts(o->u, ");\n");
    return 0;
}

/* `<fn>__<level stamp>`, a rung's helper name ([D155]; levels.def's token). */
static const char *fn_level_name(mf_art *art, const char *fn, const fn_row *r)
{
    kb b;
    kb_init(&b, art->a);
    kb_printf(&b, "%s__%s", fn, kit_level(r->decl->level)->stamp);
    if (b.oom) { kit_fail(art, "ofsskip: out of memory"); return NULL; }
    return b.p;
}

/* One rung's GUARDED BLOCK (§R4.9.2.5 piece 2), bracketed whole by the
 * sink's simd_open/simd_close (§R4.9.2.4): `#if <guard>`, the level's
 * `#include` (once per artifact per level), the helper's head (the
 * function's own, renamed), the row's body (its entry test falls to
 * `fall`), `#endif` and a blank line. */
static int fn_level_block(mf_art *art, const mf_hooks *h, const fn_in *x,
                          const fn_row *r, const char *name, const char *fall,
                          mf_sink *o)
{
    const mf_level *lv = kit_level(r->decl->level);
    o->simd_open(o->u, (int)r->decl->level);
    kit_out(o, "#if %s\n", lv->guard);
    if (!(art->simd_inc & 1u << r->decl->level)) {
        kit_out(o, "#include <%s>\n", lv->header);
        art->simd_inc |= 1u << r->decl->level;
    }
    if (fn_head(art, h, x->p, name, o) || r->decl->render(art, h, x, r->decl, fall, o))
        return -1;
    o->puts(o->u, "#endif\n\n");
    o->simd_close(o->u);
    return 0;
}

/* THE SELECTOR, the function `fn` itself (D155 addendum 1, Q-R9-10 shape
 * (c)): a function that does work never contains `#if`; the selector's
 * whole body is the choice, one call per arm and nothing else. With no
 * PREFIX row rendered that is the one plain call to `callee`, the SIMD-off
 * FUNC. With rungs, the levels are `#if`/`#elif` arms above that call, top
 * level first (the preprocessor's first match is the table's), and the call
 * is the `#else` arm's line byte for byte (floor rule (c), §R4.9.2.5). The
 * bracketed bytes are the chain's guarded part, `#if` through `#else`, and
 * the `#endif`; the head, the `#else` arm's call and the brace are the
 * SIMD-off FUNC's own (§R4.9.2.4). */
static int fn_selector(mf_art *art, const mf_hooks *h, const mf_pred *p,
                       const char *fn, const char *callee,
                       const fn_row *const *rung, const char *const *names,
                       unsigned nr, mf_sink *o)
{
    if (fn_head(art, h, p, fn, o)) return -1;
    if (nr) {
        o->simd_open(o->u, (int)rung[0]->decl->level);
        for (unsigned j = 0; j < nr; j++) {
            kit_out(o, "#%s %s\n", j ? "elif" : "if", kit_level(rung[j]->decl->level)->guard);
            if (fn_call_line(art, h, p, names[j], o)) return -1;
        }
        o->puts(o->u, "#else\n");
        o->simd_close(o->u);
    }
    if (fn_call_line(art, h, p, callee, o)) return -1;
    if (nr) {
        o->simd_open(o->u, (int)rung[0]->decl->level);
        o->puts(o->u, "#endif\n");
        o->simd_close(o->u);
    }
    o->puts(o->u, "}\n\n");
    return 0;
}

/* MEMFN_FORMS' token for the FUNC (§R4.9.2.3 "The stamp"): `<form>@<level>`
 * per RENDERED rung, top-down, `+`-joined; comma-joined in site order. */
static void fn_note_form(mf_art *art, const fn_row *const *rung, unsigned nr)
{
    kb_printf(&art->forms, "%s%s@", art->forms.len ? "," : "", rung[0]->decl->form);
    for (unsigned j = 0; j < nr; j++)
        kb_printf(&art->forms, "%s%s", j ? "+" : "", kit_level(rung[j]->decl->level)->stamp);
}

/* THE SEAM (integration.md §R4.9.2.5, step R4e'.0b): the BODY walk, then the
 * PREFIX walk (handed the BODY row and its helper's name), then the text in
 * its fixed order: the BODY row's loop as the helper `<fn>__body`, the
 * PREFIX row's helpers, then the selector `<fn>`. The helper keeps the
 * function's head and loop byte for byte, renamed; the selector forwards
 * the same arguments. */
int ofs_fn_define(mf_art *art, uint32_t handle, const mf_hooks *h,
                  const mf_pred *p, const char *fn, mf_sink *o)
{
    fn_in x = { p, max_reach(p), 0, 0, 0, &art->sites[handle - 1].site, NULL, NULL,
                o->simd_open && o->simd_close };
    ofs_fn_scan(p, &x.k, &x.a, &x.b);
    art->includes |= MF_INC_STRING_H;   /* memchr */
    /* both bodies write `memchr(`; an error from here on is sticky */
    if (mf_art_note_libc(art, "memchr")) return -1;

    kb body_fn;
    kb_init(&body_fn, art->a);
    kb_printf(&body_fn, "%s__body", fn);
    if (body_fn.oom) return kit_fail(art, "ofsskip: out of memory");
    x.body_fn = body_fn.p;

    const fn_row *body = fn_select(art, handle, h, &x, FN_BODY);
    if (!body) return -1;
    x.body_row = body->ct->row;
    const fn_row *prefix = fn_select(art, handle, h, &x, FN_PREFIX);
    const fn_row *rung[MF_NLEVEL];
    const char *names[MF_NLEVEL];
    unsigned nr = prefix ? fn_rungs(art, handle, h, &x, prefix, rung) : 0;
    for (unsigned j = 0; j < nr; j++)
        if (!(names[j] = fn_level_name(art, fn, rung[j]))) return -1;

    if (fn_head(art, h, p, x.body_fn, o) || body->render(art, h, &x, o)) return -1;
    /* the level blocks in ASCENDING order (the rungs reversed): each helper
       is defined before the one that falls through to it */
    for (unsigned j = nr; j-- > 0;)
        if (fn_level_block(art, h, &x, rung[j], names[j],
                           j + 1 < nr ? names[j + 1] : x.body_fn, o))
            return -1;
    if (fn_selector(art, h, p, fn, x.body_fn, rung, names, nr, o)) return -1;
    if (nr) fn_note_form(art, rung, nr);
    return 0;
}

int ofs_fn_call(mf_art *art, const mf_hooks *h, const mf_pred *p,
                const char *fn, mf_sink *o)
{
    if (!h || !h->s || !h->n || !h->lo)
        return kit_fail(art, "ofsskip: the call needs the `s`, `n` and `lo` hooks");
    kit_out(o, "%s(%s, %s, %s", fn, h->s, h->n, h->lo);
    if (table_params(art, h, p, 0, o)) return -1;
    o->puts(o->u, ")");
    return 0;
}

/* ---- the offset-skip site's own arm (FIND / FUNC / RETURN) --------------- */

/* What the function tests at offset `o`, for the legend: 0 where nothing;
 * else `*byte` is the one byte tested there or -1 for several, `*count` how
 * many, `*inrun` whether a RUN term covers it. The scanned offset first,
 * then a run, then a set: the order of pcrec's `ofs_test_at`. */
static int legend_at(const mf_pred *p, int o, int *byte, int *count, int *inrun)
{
    int k, a, b;
    ofs_fn_scan(p, &k, &a, &b);
    *inrun = 0;
    for (unsigned i = 0; i < p->nterm; i++) {
        const mf_term *t = &p->term[i];
        if (t->kind == MF_T_RUN && o >= t->offset && o < t->offset + (int)t->run_len)
            *inrun = 1;
    }
    if (o == k) {
        *byte = b >= 0 ? -1 : a;
        *count = b >= 0 ? 2 : 1;
        return 1;
    }
    for (unsigned i = 0; i < p->nterm; i++) {
        const mf_term *t = &p->term[i];
        if (t->kind == MF_T_RUN && o >= t->offset && o < t->offset + (int)t->run_len) {
            int m = run_mask_at(t, o - t->offset);
            *byte = m == 0xFF ? t->run[o - t->offset] : -1;
            *count = 1 << __builtin_popcount(~m & 0xFF);
            return 1;
        }
    }
    for (unsigned i = 0; i < p->nterm; i++) {
        const mf_term *t = &p->term[i];
        if (t->kind == MF_T_SET && t->offset == o) {
            *count = set_count(t->set);
            *byte = *count == 1 ? set_first(t->set) : -1;
            return 1;
        }
    }
    return 0;
}

/* The block's comment: which byte, or how many, every offset tests, and
 * the frozen deny literals that remove the block. */
static void legend(const mf_hooks *h, const mf_pred *p, mf_sink *o)
{
    if (!o->cmt_open || !o->cmt_open(o->u, h->comment_tier)) return;
    int maxk = max_reach(p), k, a, b, run = 0;
    ofs_fn_scan(p, &k, &a, &b);
    for (unsigned i = 0; i < p->nterm; i++) run |= p->term[i].kind == MF_T_RUN;
    o->puts(o->u,
        "---- THE OFFSET-k CANDIDATE-START SKIP ---------------------------\n"
        " * Every match of this pattern carries a byte from a known set at each\n"
        " * of these offsets FROM ITS OWN START, so a position that fails any\n"
        " * one of them cannot begin a match and the transition loop need not\n"
        " * be entered there (docs/design/offset_k_skip.md):\n"
        " *\n");
    for (int off = 0; off <= maxk; off++) {
        int byte, count, inrun;
        if (!legend_at(p, off, &byte, &count, &inrun)) continue;
        kit_out(o, " *   offset %-2d  ", off);
        if (byte >= 0) {
            o->puts(o->u, "exactly ");
            if (o->legend_byte) o->legend_byte(o->u, (uint8_t)byte);
            else kit_out(o, "%d", byte);
            kit_out(o, " (%d)", byte);
        } else {
            kit_out(o, "one of %d bytes", count);
        }
        if (off == k) o->puts(o->u, "   <- SCANNED FOR");
        if (inrun) o->puts(o->u, "   (the run, one compare)");
        o->puts(o->u, "\n");
    }
    o->puts(o->u,
        " *\n"
        " * The scan is one pass for the offset marked above; the others are\n"
        " * checked on each candidate before the loop is entered, and a failed\n"
        " * candidate resumes the scan one position later, so no position is\n"
        " * examined twice and none is skipped. Returns the first position >=\n"
        " * `pos` that satisfies every test, or `n` when there is none.\n"
        " *\n"
        " * SPEED ONLY: it refuses exactly the starts the stepped scan would\n"
        " * refuse, so no answer depends on it. Compile with -fno-offset-skip\n");
    o->puts(o->u, run
        ? " * or -fno-run-prefilter to emit the same matcher without it.\n"
        : " * to emit the same matcher without it.\n");
    if (o->cmt_close) o->cmt_close(o->u);
}

/* The site's shape. Its `miss` (stated as `n`), its `floor` (none) and its
 * name (`fn_ref` stated, `fn_name` offered) are the contract's, which the
 * gate reads before this (N3). */
static int ofsskip_applies(const mf_site *s, const mf_hooks *def)
{
    return s->form == MF_FORM_FUNC && s->op == MF_OP_FIND &&
           s->handoff == MF_H_RETURN && s->empty == MF_EMPTY_MISS &&
           s->end_back == 0 && !s->reverse && !s->guard_by_caller &&
           ofs_fn_applies(&s->pred, def);
}

/* The word-load helpers the predicate's run compare needs (runcmp.c), pcrec's
 * own note if it gives one, then the comment, then the function. */
static int ofsskip_define(mf_art *art, uint32_t handle, const mf_hooks *h,
                          mf_sink *o)
{
    site_rec *r = &art->sites[handle - 1];
    if (kit_sink_ok(art, o, "ofsskip")) return -1;
    if (!h || !h->fn_name)
        return kit_fail(art, "ofsskip: a FUNC site needs the fn_name hook");
    r->fn = h->fn_name(h->u, r->site.pred.fn_ref);
    if (!r->fn || !*r->fn)
        return kit_fail(art, "ofsskip: fn_name gave no name for fn_ref %u",
                        r->site.pred.fn_ref);
    if (run_cmp_prepare(art, &r->site.pred, o)) return -1;
    if (h->note) h->note(h->u, o, 0);
    legend(h, &r->site.pred, o);
    return ofs_fn_define(art, handle, h, &r->site.pred, r->fn, o);
}

static int ofsskip_use(mf_art *art, uint32_t handle, const mf_hooks *h,
                       mf_sink *o)
{
    site_rec *r = &art->sites[handle - 1];
    if (kit_sink_ok(art, o, "ofsskip")) return -1;
    return ofs_fn_call(art, h, &r->site.pred, r->fn, o);
}

/* ---- the contract ([MEMFN-ROWCON] N1; enforced since N3) ----------------
 *
 * `uses`: the fields the text reads with no reading of its own left
 * unstated; `serves`: per field, the classes the text is right for (MF_ANY:
 * irrelevant to the text). Each cites the code above that justifies it, by
 * function (N3 replaced the line citations: deleting the ad hoc K96 tests
 * moved every line below them). Read only for some shapes, and so held by
 * the predicate rather than declared: `table_name` (a multi-byte SET term:
 * ofs_fn_applies at define, table_of at the call). The run compare's own
 * fields are its rows' (runcmp.c). */
static const gate_use ofsskip_uses[] = {
    /* ofsskip_define names the function: fn_name(fn_ref); the function's
       miss is its `n` (ofs_fn_define's `return n;`), right only for a miss
       STATED as `n` (K96's miss half; R1 declines an unstated one) */
    { CM(FUNC), CM(RETURN), MF_PH_DEFINE, FM(fn_name) | FM(fn_ref) | FM(miss), GATE_ALWAYS },
    /* ofs_fn_call pastes s, n and lo; the call's value on a miss is `n` */
    { CM(FUNC), CM(RETURN), MF_PH_USE, FM(s) | FM(n) | FM(lo) | FM(miss), GATE_ALWAYS },
};

static const gate_contract ofsskip_ct = {
    "arms", "ofsskip", ofsskip_uses, sizeof ofsskip_uses / sizeof ofsskip_uses[0], {
    [FLD_form]            = CM(FUNC),                 /* ofsskip_applies */
    [FLD_op]              = CM(FIND),                 /* ofsskip_applies */
    [FLD_handoff]         = CM(RETURN),               /* ofsskip_applies */
    [FLD_reverse]         = CM(NO),                   /* ofsskip_applies; the memchr stream
                                                         is forward (ofs_fn_define) */
    [FLD_empty]           = CM(E_MISS),               /* ofsskip_applies; an empty range fails
                                                         the loop guard and returns n */
    [FLD_end_back]        = CM(ZERO),                 /* ofsskip_applies; the loop reads to n */
    [FLD_pred]            = CM(NONNEG),               /* ofs_fn_applies refuses offset < 0;
                                                         reads from cand up (verify_chain) */
    [FLD_preds]           = MF_ANY,                   /* not read: a FIND reads s->pred */
    [FLD_ret_pred]        = MF_ANY,                   /* not read (ALL_PRESENT's) */
    [FLD_guard_by_caller] = CM(NO),                   /* ofsskip_applies; the function bounds
                                                         its own reads (`cand + maxk >= n`) */
    [FLD_on_miss_leaves]  = MF_ANY,                   /* not read; 0 off ON_MISS/ASSIGN (site_check) */
    [FLD_span_hi]         = MF_ANY,                   /* not read: a proven fact the text needs not */
    [FLD_denies]          = CM(NONE) | CM(RUN_OVERLAP), /* verify_chain renders runs through the
                                                         run compare, whose walk reads them with a
                                                         fallback per domain (runcmp.c rows[]) */
    [FLD_fn_ref]          = CM(REF),                  /* ofsskip_define: fn_name(fn_ref) */
    [FLD_table_ref]       = CM(NONE) | CM(REF),       /* ofs_fn_applies: a multi-byte set needs
                                                         one; a singleton and a run read none */
    [FLD_s]               = CM(IDENT),                /* ofs_fn_call: raw in the call's argument
                                                         list, where a top-level comma would split it */
    [FLD_n]               = CM(IDENT),                /* ofs_fn_call, as s */
    [FLD_lo]              = CM(IDENT),                /* ofs_fn_call, as s */
    [FLD_floor]           = 0,                        /* the function reads nothing below `pos`
                                                         and takes no floor: a stated floor is
                                                         declined at define, refused at the call
                                                         (K96's floor half; R2) */
    [FLD_result]          = MF_ANY,                   /* not read: RETURN is the call's value */
    [FLD_result_decl]     = MF_ANY,                   /* not read */
    [FLD_miss]            = CM(MISS_N),               /* the function returns its `n` on a miss
                                                         (ofs_fn_define, pair_body) */
    [FLD_on_miss]         = MF_ANY,                   /* not read: a FUNC RETURN runs no statement */
    [FLD_step]            = MF_ANY,                   /* not read (ADVANCE's) */
    [FLD_more]            = MF_ANY,                   /* not read (ADVANCE's) */
    [FLD_peek]            = MF_ANY,                   /* not read (ADVANCE's) */
    [FLD_cursor]          = MF_ANY,                   /* not read (ADVANCE's) */
    [FLD_count]           = MF_ANY,                   /* not read (ADVANCE's) */
    [FLD_count_start]     = MF_ANY,                   /* not read (ADVANCE's) */
    [FLD_count_by_caller] = MF_ANY,                   /* not read (ADVANCE's; 0 off ADVANCE, site_check) */
    [FLD_stride]          = MF_ANY,                   /* not read (ADVANCE's; unstated off ADVANCE) */
    [FLD_on_cand]         = MF_ANY,                   /* not read (ON_CAND's) */
    [FLD_on_cand_reach]   = MF_ANY,                   /* not read (ON_CAND's) */
    [FLD_member]          = MF_ANY,                   /* not read: the set's bits are the truth, a
                                                         singleton compared, a wider set pcrec's
                                                         table (verify_chain, rule 7) */
    [FLD_table_name]      = MF_ANY,                   /* table_of names the table, any name */
    [FLD_fn_name]         = MF_ANY,                   /* ofsskip_define names the function, any name */
    [FLD_note]            = MF_ANY,                   /* ofsskip_define: pcrec's own writer, as given */
    [FLD_note_tag]        = MF_ANY,                   /* not read */
    [FLD_indent]          = MF_ANY,                   /* not read: the definition is file scope */
    [FLD_comment_tier]    = MF_ANY,                   /* legend: handed to cmt_open as given */
    [FLD_policy]          = MF_ANY,                   /* scalar: right under every policy (R4e' batch 1) */
}};

const arm ofsskip_arm = {
    "ofsskip",
    0,
    ofsskip_applies,
    ofsskip_define,
    ofsskip_use,
    &ofsskip_ct,
};

/* ---- fn_rows[]' contracts ------------------------------------------------
 *
 * What a BODY row's text reads beyond the predicate the walk hands it. The
 * site's shape, its name, its miss and its hooks' spelling are the calling
 * arm's (ofsskip_ct above, precheck.c's two), which the arms walk checked
 * before this walk runs; the body is the same text under all three, so it
 * serves every class of a field it does not read (MF_ANY). The predicate is
 * the walk's input, the site's `pred` (ofsskip) or one of its `preds`
 * (precheck), held to offset >= 0 by ofs_fn_applies, so the site-level
 * `pred`/`preds` classes are not the body's to read. The two rows read the
 * same fields (both end in verify_chain), so they share one `serves`; each
 * is its own contract only because the trace names the row by it. No row
 * USES an unstated field: the walk passes the define hooks the calling arm
 * was given. */
#define FN_BODY_SERVES \
    [FLD_form]            = MF_ANY,                   /* the calling arm's */ \
    [FLD_op]              = MF_ANY,                   /* the calling arm's */ \
    [FLD_handoff]         = MF_ANY,                   /* the calling arm's: RETURN, ON_MISS or \
                                                         ASSIGN read the same function */ \
    [FLD_reverse]         = CM(NO),                   /* the memchr streams are forward */ \
    [FLD_empty]           = MF_ANY,                   /* an empty range fails the loop guard and \
                                                         returns n, whatever the caller does with it */ \
    [FLD_end_back]        = MF_ANY,                   /* the calling arm's: the body reads to n */ \
    [FLD_pred]            = MF_ANY,                   /* the walk's input (above) */ \
    [FLD_preds]           = MF_ANY,                   /* the walk's input (above) */ \
    [FLD_ret_pred]        = MF_ANY,                   /* the calling arm's */ \
    [FLD_guard_by_caller] = MF_ANY,                   /* the body bounds its own reads */ \
    [FLD_on_miss_leaves]  = MF_ANY,                   /* the calling arm's */ \
    [FLD_span_hi]         = MF_ANY,                   /* not read */ \
    [FLD_denies]          = CM(NONE) | CM(RUN_OVERLAP), /* verify_chain renders runs through the \
                                                         run compare, whose walk reads them with a \
                                                         fallback per domain (runcmp.c rows[]) */ \
    [FLD_fn_ref]          = MF_ANY,                   /* the calling arm names the function */ \
    [FLD_table_ref]       = CM(NONE) | CM(REF),       /* verify_chain: a multi-byte set's table */ \
    [FLD_s]               = MF_ANY,                   /* the call's (ofs_fn_call); the body reads \
                                                         its own `subject` */ \
    [FLD_n]               = MF_ANY,                   /* as s: its own `n` */ \
    [FLD_lo]              = MF_ANY,                   /* as s: its own `pos` */ \
    [FLD_floor]           = 0,                        /* the body reads nothing below `pos`: no \
                                                         stated floor is served (K96's floor half) */ \
    [FLD_result]          = MF_ANY,                   /* not read */ \
    [FLD_result_decl]     = MF_ANY,                   /* not read */ \
    [FLD_miss]            = MF_ANY,                   /* the body returns its `n`; what a caller's \
                                                         miss means is the calling arm's */ \
    [FLD_on_miss]         = MF_ANY,                   /* not read */ \
    [FLD_step]            = MF_ANY,                   /* not read (ADVANCE's) */ \
    [FLD_more]            = MF_ANY,                   /* not read (ADVANCE's) */ \
    [FLD_peek]            = MF_ANY,                   /* not read (ADVANCE's) */ \
    [FLD_count]           = MF_ANY,                   /* not read (ADVANCE's) */ \
    [FLD_count_start]     = MF_ANY,                   /* not read (ADVANCE's) */ \
    [FLD_count_by_caller] = MF_ANY,                   /* not read (ADVANCE's) */ \
    [FLD_on_cand]         = MF_ANY,                   /* not read (ON_CAND's) */ \
    [FLD_on_cand_reach]   = MF_ANY,                   /* not read (ON_CAND's) */ \
    [FLD_member]          = MF_ANY,                   /* not read: a singleton is compared, a wider \
                                                         set is pcrec's table (verify_chain) */ \
    [FLD_table_name]      = MF_ANY,                   /* table_of names the table, any name */ \
    [FLD_fn_name]         = MF_ANY,                   /* the calling arm names the function */ \
    [FLD_note]            = MF_ANY,                   /* not read: the calling arm's */ \
    [FLD_note_tag]        = MF_ANY,                   /* not read */ \
    [FLD_indent]          = MF_ANY,                   /* not read: file scope */ \
    [FLD_comment_tier]    = MF_ANY,                   /* not read: the body writes no comment */ \
    [FLD_policy]          = MF_ANY,                   /* scalar: right under every policy (R4e' batch 1) */

static const gate_contract fn_pair_ct = {
    "fn", "fn-pair", NULL, 0, {
    FN_BODY_SERVES
}};

static const gate_contract fn_memchr_ct = {
    "fn", "fn-memchr", NULL, 0, {
    FN_BODY_SERVES
}};

#undef FN_BODY_SERVES
