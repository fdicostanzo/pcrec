/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2, lane memfng2).
 *
 * memfn/tests/g2/g2_ref.c — G2's REFERENCE: a plain scalar byte loop per
 * operation, written from the contract's semantics (integration.md §14.3
 * what each operation returns, §14.4 ranges and empty outcomes, §14.5
 * REQUIRED/OPTIONAL and the result's promise, §14.7 the read limits, §8.3
 * rules 2-5), and from nothing else. It does not include memfn.h, calls no
 * kit function (not even the kit's mf_ref_* reference functions) and never
 * reads kit text: the independent control G2 exists to be.
 *
 * OPTIONAL terms (§14.5): the kit tests the REQUIRED terms plus a subset S
 * of the OPTIONAL ones, "fixed when the site is emitted". The reference
 * does not guess S. It answers for EVERY subset, and the driver keeps, per
 * site, the set of subsets still consistent with every answer the
 * rendered code has given; a call fails when no subset survives it.
 */
#include <string.h>

#include "g2.h"
#include "g2_ref.h"

int g2_ref_defect;   /* W1 witness: a deliberately wrong reference (0 = none) */

static int set_has(const uint8_t *set, unsigned b) { return set[b >> 3] >> (b & 7) & 1; }

/* Rule 2 + §14.7: a term holds at c only if every byte it reads lies in
 * [fl, n). The term reads s[c + off .. c + off + len). */
static int term_holds(const g2_term *t, const uint8_t *s, size_t n, size_t fl, size_t c)
{
    long long start = (long long)c + t->off;
    long long len = t->kind == G2_T_SET ? 1 : (long long)t->len;
    long long lowest = g2_ref_defect == 3 ? 0 : (long long)fl;    /* W1-3: floor ignored */
    if (start < lowest || start + len > (long long)n) return 0;
    if (t->kind == G2_T_SET) return set_has(t->set, s[start]);
    for (long long j = 0; j < len; j++) {
        uint8_t m = t->mask ? t->mask[j] : 0xFF;
        if ((s[start + j] & m) != t->run[j]) return 0;
    }
    return 1;
}

void g2_ref_items(const g2_site *d, g2_items *it)
{
    memset(it, 0, sizeof *it);
    for (int p = 0; p < d->npred; p++) {
        const g2_pred *P = &d->preds[p];
        it->pred_item[p] = -1;
        if (P->need == G2_OPT) it->pred_item[p] = (int8_t)it->nitems++;
        for (int t = 0; t < P->nterm; t++) {
            it->term_item[p][t] = -1;
            if (P->t[t].need == G2_OPT) it->term_item[p][t] = (int8_t)it->nitems++;
        }
    }
}

/* does predicate p hold at c when the OPTIONAL items in S are tested */
static int pred_holds(const g2_site *d, const g2_items *it, int p, uint64_t S,
                      const uint8_t *s, size_t n, size_t fl, size_t c)
{
    const g2_pred *P = &d->preds[p];
    for (int t = 0; t < P->nterm; t++) {
        int item = it->term_item[p][t];
        if (item >= 0 && !(S >> item & 1)) continue;          /* not tested */
        if (!term_holds(&P->t[t], s, n, fl, c)) return 0;
    }
    return 1;
}

/* Q-R7-1 (MF_SITE_ABI 6; memfn.h MF_OP_FIND). A FIND whose every term reads
 * below its candidate (offset + len <= 0 for each, 1 for a SET term; E the
 * largest) never reads the candidate's own byte, so its range is bounded by
 * its READS: c in [lo, n] with c + d <= n, d = max(0, end_back + E); empty
 * iff lo + d > n. Every other FIND, and ALL_PRESENT / SKIP / VERIFY /
 * ON_CAND, keep [lo, n - end_back). ON_CAND is outside the rule by the
 * brief's reading (a visit's own reach is checked as cand + reach <= n). */
int g2_ref_readsbelow(const g2_site *d, long long *E)
{
    if (d->op != G2_OP_FIND || d->handoff == G2_H_ON_CAND || d->npred != 1 || !d->preds) return 0;
    const g2_pred *P = &d->preds[0];
    long long m = -(1LL << 40);
    if (!P->nterm) return 0;
    for (int t = 0; t < P->nterm; t++) {
        long long e = (long long)P->t[t].off + (P->t[t].kind == G2_T_SET ? 1 : (long long)P->t[t].len);
        if (e > 0) return 0;
        if (e > m) m = e;
    }
    *E = m;
    return 1;
}

/* §14.4 + Q-R7-1: the range, hi EXCLUSIVE; 0 when empty */
int g2_ref_range(const g2_site *d, size_t n, size_t lo, size_t *hi)
{
    size_t eb = g2_ref_defect == 1 ? 0 : d->end_back;          /* W1-1 */
    long long E;
    if (g2_ref_defect != 4 && g2_ref_readsbelow(d, &E)) {      /* W1-4: the OLD range */
        long long dd = (long long)eb + E;
        if (dd < 0) dd = 0;
        if (lo > n || (long long)(n - lo) < dd) { *hi = lo; return 0; }
        *hi = n - (size_t)dd + 1;
        return 1;
    }
    if (!(lo + eb < n)) { *hi = lo; return 0; }
    *hi = n - eb;
    return 1;
}

static int range(const g2_site *d, size_t n, size_t lo, size_t *hi) { return g2_ref_range(d, n, lo, hi); }

/* the candidates of predicate p under S, in visiting order (§14.3: ascending,
 * descending if reverse); for SKIP the candidates are the NON-members */
static size_t cands(const g2_site *d, const g2_items *it, int p, uint64_t S,
                    const uint8_t *s, size_t n, size_t lo, size_t hi, size_t fl,
                    size_t *out, size_t cap)
{
    size_t k = 0;
    int rev = d->reverse;
    if (g2_ref_defect == 2) rev = !rev;                          /* W1-2 */
    for (size_t i = 0; i < hi - lo; i++) {
        size_t c = rev ? hi - 1 - i : lo + i;
        int h = pred_holds(d, it, p, S, s, n, fl, c);
        if (d->op == G2_OP_SKIP) h = !h;
        if (h) { if (k < cap) out[k] = c; k++; }
    }
    return k;
}

static int is_member_of(const size_t *v, size_t k, size_t x)
{
    for (size_t i = 0; i < k; i++) if (v[i] == x) return 1;
    return 0;
}

/* Is the kit's outcome `o` the one subset S's contract answer allows? */
static int consistent(const g2_site *d, const g2_items *it, uint64_t S,
                      const uint8_t *s, size_t n, size_t lo, size_t fl,
                      const struct g2_out *o, char *why, size_t whyn)
{
    size_t hi;
    int nonempty = range(d, n, lo, &hi);
    size_t missv = g2_missv(d->miss_mode, n);
    size_t cv[256];
    /* §15.5 (lane g2x): in an ALL_PRESENT ASSIGN only the returned
     * predicate's line writes the result ("every other predicate behaves as
     * ON_MISS"), so a miss may run on_miss with the result unwritten. G2
     * observes that only where its on_miss text leaves and reads no result
     * (noread: the generator's mode-3 text) */
    int unwritten_ok = d->handoff == G2_H_ASSIGN && (d->noread || d->leaves);   /* G2pf2: on_miss_leaves 1 => result UNSPECIFIED on a miss (memfn.h) */    /* lane g2pf: PF cell 1 too */
    int miss_res_ok = o->res == missv || (unwritten_ok && o->res == G2_SENT);

    if (d->handoff == G2_H_ADVANCE) {
        /* §8.3 rule 5 + §14.3: `while (more && member(peek)) step;`, the
         * count capped at span_hi; the hooks are G2's (g2_gen.c fill_hooks) */
        size_t cur = lo;
        unsigned long cnt = d->count_start;
        const g2_term *t = &d->preds[0].t[0];
        for (;;) {
            if (d->has_count && d->span_hi != G2_UNBOUNDED && cnt >= d->span_hi) break;
            if (d->reverse) {
                if (!(cur > fl)) break;
                if (!set_has(t->set, s[cur - 1])) break;
                cur--;
            } else {
                if (!(d->end_back ? cur + 1 < n : cur < n)) break;
                if (!set_has(t->set, s[cur])) break;
                cur++;
            }
            cnt++;
        }
        if (o->res != cur || (d->has_count && o->cnt != cnt)) {
            snprintf(why, whyn, "ADVANCE: cursor %zu count %lu, want %zu / %lu", o->res,
                     o->cnt, cur, cnt);
            return 0;
        }
        return 1;
    }

    /* lane g2pf: the in-place advance (memfn.h `result`: the lvalue written;
     * here its text IS `lo`'s). The outcome is lo's value at the end:
     * empty + NOP leaves lo as it was (lo > n included, nothing written);
     * empty + MISS, or no candidate, leaves the miss value; a hit leaves the
     * position (any occurrence under DISCARD). on_miss, when stated, ran
     * exactly on a miss; with the hook NULL nothing ran. */
    if (d->inplace) {
        int nop_ = d->empty == G2_EMPTY_NOP;
        size_t want_res;
        int want_missed;
        if (!nonempty) {
            want_res = nop_ ? lo : missv;
            want_missed = !nop_;
        } else {
            size_t nc_ = cands(d, it, 0, S, s, n, lo, hi, fl, cv, 256);
            int discard_ = d->use == G2_USE_DISCARD;
            if (nc_ && (discard_ ? is_member_of(cv, nc_ < 256 ? nc_ : 256, o->res) : 1)) {
                want_res = discard_ ? o->res : cv[0];
                want_missed = 0;
            } else {
                want_res = missv;
                want_missed = 1;
            }
        }
        /* G2pf2: a miss under on_miss_leaves 1 leaves the result UNSPECIFIED (memfn.h) */
        if (want_missed && d->leaves && !d->noonmiss && o->missed) return 1;
        if (o->res == want_res && (d->noonmiss || o->missed == want_missed)) return 1;
        snprintf(why, whyn, "IN-PLACE lo: kit lo=%zu missed %d, want lo=%zu missed %d (%s)", o->res,
                 o->missed, want_res, d->noonmiss ? 0 : want_missed, nonempty ? "range" : "empty range");
        return 0;
    }

    if (!nonempty) {
        /* §14.4: MISS = as a miss; NOP = nothing written, nothing run */
        int nop = d->empty == G2_EMPTY_NOP;
        switch (d->handoff) {
        case G2_H_RETURN:
            if (o->res == missv) return 1;
            break;
        case G2_H_BOOL:
            if (o->res == 0) return 1;
            break;
        case G2_H_ASSIGN:
            if (nop ? (o->res == G2_SENT && !o->missed) : (miss_res_ok && (d->noonmiss || o->missed))) return 1;
            break;
        case G2_H_ON_MISS:
            if (o->missed == !nop) return 1;
            break;
        case G2_H_ON_CAND:
            if (o->nlog == 0 && o->missed == !nop && (!nop || o->res == G2_SENT)) return 1;
            break;
        }
        snprintf(why, whyn, "empty range (%s): res %zu missed %d visits %u",
                 nop ? "NOP" : "MISS", o->res, o->missed, o->nlog);
        return 0;
    }

    if (d->op == G2_OP_VERIFY) {
        int h = pred_holds(d, it, 0, S, s, n, fl, lo);
        if (d->handoff == G2_H_BOOL ? (o->res == (size_t)h) : (o->missed == !h)) return 1;
        snprintf(why, whyn, "VERIFY: kit %s, want %d", d->handoff == G2_H_BOOL
                 ? (o->res ? "1" : "0") : (o->missed ? "miss" : "hold"), h);
        return 0;
    }

    int hit;
    size_t want = 0, nc = 0;
    int retp = 0;
    if (d->op == G2_OP_ALL) {
        hit = 1;
        for (int p = 0; p < d->npred && hit; p++) {
            int item = it->pred_item[p];
            if (item >= 0 && !(S >> item & 1)) continue;          /* not tested */
            if (!cands(d, it, p, S, s, n, lo, hi, fl, cv, 1)) hit = 0;
        }
        if (d->ret_pred != 0xFF) {
            retp = d->ret_pred;
            /* "the LEFTMOST position of predicate ret_pred (as FIND would
             * return it)": forward order whatever `reverse` says */
            g2_site fwd = *d;
            fwd.reverse = 0;
            fwd.op = G2_OP_FIND;
            nc = cands(&fwd, it, retp, S, s, n, lo, hi, fl, cv, 256);
            if (hit && nc) want = cv[0];
        }
    } else {
        nc = cands(d, it, 0, S, s, n, lo, hi, fl, cv, 256);
        hit = nc > 0;
        if (hit) want = cv[0];
    }
    int discard = d->use == G2_USE_DISCARD;
    /* a DISCARD result may be ANY occurrence (§14.5 `use`) */
    int pos_ok = hit && (discard ? is_member_of(cv, nc < 256 ? nc : 256, o->res) : o->res == want);

    switch (d->handoff) {
    case G2_H_RETURN:
        if (hit ? pos_ok : o->res == missv) return 1;
        snprintf(why, whyn, "RETURN: kit %zu, want %s%zu", o->res, hit ? "" : "miss ", hit ? want : missv);
        return 0;
    case G2_H_BOOL:
        if (o->res == (size_t)hit) return 1;
        snprintf(why, whyn, "BOOL: kit %zu, want %d", o->res, hit);
        return 0;
    case G2_H_ASSIGN:
        if (hit ? (pos_ok && !o->missed) : (miss_res_ok && (d->noonmiss || o->missed))) return 1;
        snprintf(why, whyn, "ASSIGN: kit %zu missed %d, want %s%zu", o->res, o->missed,
                 hit ? "" : "miss ", hit ? want : missv);
        return 0;
    case G2_H_ON_MISS:
        if (o->missed == !hit) return 1;
        snprintf(why, whyn, "ON_MISS: kit missed %d, want %d", o->missed, !hit);
        return 0;
    case G2_H_ON_CAND: {
        /* §14.3 + rule 2/4: every candidate with cand + reach <= n, in
         * order, none skipped or repeated, until one is accepted */
        size_t vis[256], nv = 0, acc = (size_t)-1;
        for (size_t i = 0; i < nc && i < 256; i++) {
            size_t c = cv[i];
            if (c + d->reach > n) continue;
            vis[nv++] = c;
            int a = d->tok == 1 ? 1 : d->tok == 2 ? 0
                  : (d->acc_mod && (c + o->salt) % d->acc_mod == 0);
            if (a) { acc = c; break; }
        }
        int ok = o->nlog == nv;
        for (size_t i = 0; ok && i < nv && i < G2_LOGMAX; i++) ok = o->log[i] == vis[i];
        if (ok) ok = acc != (size_t)-1 ? (o->res == acc && !o->missed) : o->missed;
        if (ok) return 1;
        snprintf(why, whyn, "ON_CAND: kit visits %u first %zu res %zu missed %d; want visits %zu first %zu accept %zu",
                 o->nlog, o->nlog ? o->log[0] : 0, o->res, o->missed, nv, nv ? vis[0] : 0, acc);
        return 0;
    }
    }
    snprintf(why, whyn, "unknown handoff");
    return 0;
}

uint64_t g2_ref_check(const g2_site *d, const g2_items *it, uint64_t alive,
                      const uint8_t *s, size_t n, size_t lo, size_t fl,
                      const struct g2_out *o, char *why, size_t whyn)
{
    uint64_t keep = 0;
    uint64_t nsub = 1ull << it->nitems;
    why[0] = 0;
    for (uint64_t S = 0; S < nsub; S++) {
        if (!(alive >> S & 1)) continue;
        char w[256];
        if (consistent(d, it, S, s, n, lo, fl, o, w, sizeof w)) keep |= 1ull << S;
        else if (!why[0]) snprintf(why, whyn, "%s", w);
    }
    return keep;
}

/* lane g2m7, MF_OP_MISMATCH (memfn.h): k is the least j in [0, reflen) with
 * lo + j >= n (the subject ended: lo > n included) or fold(s[lo + j]) !=
 * fold(ref[j]); no such j = EQUAL. The only thing asked of the fold is
 * map(a) == map(b), and `map` is the table G2 generated. W1 defects: 5 the
 * fold ignored, 6 the loop stops one byte short of reflen. */
int g2_ref_mismatch(const uint8_t *map, const uint8_t *s, size_t n, size_t lo,
                    const uint8_t *ref, size_t reflen, size_t *k)
{
    size_t stop = reflen;
    if (g2_ref_defect == 6 && stop) stop--;                      /* W1-6 */
    for (size_t j = 0; j < stop; j++) {
        if (lo >= n || j >= n - lo) { *k = j; return 1; }
        uint8_t a = s[lo + j], b = ref[j];
        if (g2_ref_defect != 5) { a = map[a]; b = map[b]; }      /* W1-5: no fold */
        if (a != b) { *k = j; return 1; }
    }
    return 0;
}
