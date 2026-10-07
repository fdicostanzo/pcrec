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
 * pre-check composite's FUNC parts (precheck.c).
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
 * the caller's `s`, `n` and `lo`. The run compare is pcrec's (`run_cmp`,
 * until M1b) and a multi-byte set's table is pcrec's (`table_name`, rule 7).
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

int ofs_fn_applies(const mf_pred *p, const mf_hooks *def)
{
    if (!def || p->nterm == 0 || p->nterm > MF_MAX_TERM || p->plan_hint >= p->nterm)
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
 * compare, a wider one a probe of pcrec's table, a run pcrec's run compare
 * at the term's offset from the candidate. */
static int verify_chain(mf_art *art, const mf_hooks *h, const mf_pred *p,
                        uint32_t pidx, mf_sink *o)
{
    int first = 1;
    for (unsigned i = 0; i < p->nterm; i++) {
        const mf_term *t = &p->term[i];
        if (scan_only(p, i)) continue;
        o->puts(o->u, first ? "" : " &&\n            ");
        first = 0;
        if (t->kind == MF_T_RUN) {
            if (h && h->run_cmp)
                h->run_cmp(h->u, o, "subject + cand", t->offset,
                           i + pidx * MF_MAX_TERM);
            else if (run_cmp_render(art, t, "subject + cand", t->offset, o))
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

/* The PAIR leapfrog's body: two `memchr` streams, members `a` and `b` of
 * the cube at offset `k`, each holding its one pending hit as an OFFSET
 * (never a pointer, so nothing NULL is compared relationally). `fresh`
 * makes the first iteration search both. */
static int pair_body(mf_art *art, const mf_hooks *h, const mf_pred *p,
                     uint32_t pidx, int maxk, int k, int a, int b, mf_sink *o)
{
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
    if (verify_chain(art, h, p, pidx, o)) return -1;
    o->puts(o->u,   ") return cand;\n"
                    "        pos = cand + 1;\n"
                    "    }\n"
                    "    return n;\n}\n\n");
    return 0;
}

int ofs_fn_define(mf_art *art, const mf_hooks *h, const mf_pred *p,
                  uint32_t pidx, const char *fn, mf_sink *o)
{
    int maxk = max_reach(p), k, a, b;
    ofs_fn_scan(p, &k, &a, &b);
    art->includes |= MF_INC_STRING_H;   /* memchr */

    kit_out(o, "static inline size_t %s(const unsigned char *subject, size_t n, size_t pos", fn);
    if (table_params(art, h, p, 1, o)) return -1;
    o->puts(o->u, ")\n{\n");
    if (b >= 0)
        return pair_body(art, h, p, pidx, maxk, k, a, b, o);
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
    if (verify_chain(art, h, p, pidx, o)) return -1;
    o->puts(o->u,   ") return cand;\n");
    o->puts(o->u,   "        pos = cand + 1;\n"
                    "    }\n"
                    "    return n;\n}\n\n");
    return 0;
}

int ofs_fn_call(mf_art *art, const mf_hooks *h, const mf_pred *p,
                const char *fn, mf_sink *o)
{
    if (!h || !h->s || !h->n || !h->lo)
        return kit_fail(art, "ofsskip: the call needs the s, n and lo hooks");
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

static int ofsskip_applies(const mf_site *s, const mf_hooks *def)
{
    return s->form == MF_FORM_FUNC && s->op == MF_OP_FIND &&
           s->handoff == MF_H_RETURN && s->empty == MF_EMPTY_MISS &&
           s->end_back == 0 && !s->reverse && !s->guard_by_caller &&
           s->pred.fn_ref && def && def->fn_name && ofs_fn_applies(&s->pred, def);
}

/* pcrec's own file-scope text for the predicate (its run compare's word
 * loads, until M1b), then the comment, then the function. */
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
    if (!h->run_cmp && run_cmp_prepare(art, &r->site.pred, o)) return -1;
    if (h->note) h->note(h->u, o, 0);
    legend(h, &r->site.pred, o);
    return ofs_fn_define(art, h, &r->site.pred, 0, r->fn, o);
}

static int ofsskip_use(mf_art *art, uint32_t handle, const mf_hooks *h,
                       mf_sink *o)
{
    site_rec *r = &art->sites[handle - 1];
    if (kit_sink_ok(art, o, "ofsskip")) return -1;
    return ofs_fn_call(art, h, &r->site.pred, r->fn, o);
}

const arm ofsskip_arm = {
    "ofsskip",
    0,
    ofsskip_applies,
    ofsskip_define,
    ofsskip_use,
};
