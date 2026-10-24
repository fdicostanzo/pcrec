/* §6, §10: the glue is retired into rx_subst_replace_all (§10¶6-¶10) and the
 * recipes (§6¶2-¶3): the returns, *len on every path, limits, sizing, NULLs.
 * substb2: was pcrec_subst with limit, *outlen and *nsubst. */
#include "t.h"

#define UNTOUCHED ((size_t)0x5a5a5a5a)

int main(void)
{
    char out[512];
    size_t L, K;
    int rc;
    const struct rx_info *ra = &ra_info;

    /* replace-all: the match count, *len the length (§10¶7) */
    rc = rall(ra, &s2_subst_info, NULL, 0, "xaby", 4, 64, out, &L);
    CHECK("glue.basic", rc == 1 && !strcmp(out, "x<ab>y") && L == 6, "rc %d out %s", rc, out);
    /* out == NULL with cap == 0 only sizes (§10¶7) */
    L = UNTOUCHED;
    rc = sub_all(ra, &s2_subst_info, NULL, 0, (const unsigned char *)"xaby", 4, NULL, 0, &L);
    CHECK("glue.size.null", rc == 1 && L == 6, "rc %d L %zu", rc, L);
    /* out == NULL with cap > 0 is MISMATCH (§10¶7), where R3's glue sized */
    L = UNTOUCHED;
    rc = sub_all(ra, &s2_subst_info, NULL, 0, (const unsigned char *)"xaby", 4, NULL, 1000, &L);
    CHECK("glue.size.null.bigcap", rc == PCREC_SUBST_MISMATCH && L == UNTOUCHED, "rc %d L %zu", rc, L);
    /* the §10¶8 retry: NOSPACE with *len the total, then a FRESH iterator into a buffer that fits */
    {
        const unsigned char *s = (const unsigned char *)"zabaz";
        size_t n = 5, cap = 2;
        unsigned char *o = malloc(cap);
        size_t len;
        int r = sub_all(ra, &s2_subst_info, NULL, 0, s, n, o, cap, &len);
        CHECK("retry.first", r == PCREC_SUBST_NOSPACE && len == 9, "rc %d len %zu", r, len);
        if (r == PCREC_SUBST_NOSPACE && len != SIZE_MAX) {
            unsigned char *big = malloc(len ? len : 1);
            r = sub_all(ra, &s2_subst_info, NULL, 0, s, n, big, len, &len);
            CHECK("retry.second", r == 2 && len == 9 && !memcmp(big, "z<ab><a>z", 9), "rc %d len %zu", r, len);
            free(big);
        }
        free(o);
    }
    /* NULL subject with n = 0 */
    L = UNTOUCHED;
    rc = sub_all(ra, &s2_subst_info, NULL, 0, NULL, 0, (unsigned char *)out, 64, &L);
    CHECK("glue.null.subject", rc == 0 && L == 0, "rc %d L %zu", rc, L);
    rc = sub_all(ra, &s2_subst_info, NULL, 0, NULL, 0, NULL, 0, &L);
    CHECK("glue.null.everything", rc == 0 && L == 0, "rc %d", rc);
    /* empty subject, cap 0, out non-NULL: 0 matches, 0 bytes */
    rc = rall(ra, &s2_subst_info, NULL, 0, "", 0, 0, out, &L);
    CHECK("glue.empty.cap0", rc == 0 && L == 0, "rc %d", rc);
    /* every capacity 0..need: NOSPACE below, the count at need; *len = need (§10¶8) */
    const char *S = "zabzazabz";        /* (a)(b)? -> [$1]: z[a]z[a]z[a]z  = 13 */
    for (size_t cap = 0; cap <= 14; cap++) {
        char id[40]; snprintf(id, sizeof id, "glue.cap%zu", cap);
        rc = rall(ra, &s1_subst_info, NULL, 0, S, 9, cap, out, &L);
        CHECK(id, (cap < 13 ? rc == PCREC_SUBST_NOSPACE : rc == 3) && L == 13, "rc %d L %zu", rc, L);
    }
    rc = rall(ra, &s1_subst_info, NULL, 0, S, 9, 13, out, &L);
    CHECK("glue.cap.exact.text", rc == 3 && !strcmp(out, "z[a]z[a]z[a]z"), "out %s", out);

    /* limit: the per-match recipe counting the loop (§6¶2, §6¶3): 0 copies and leaves FRESH; N */
    for (size_t lim = 0; lim <= 4; lim++) {
        static const char *want[] = { "zabzazabz", "z[a]zazabz", "z[a]z[a]zabz", "z[a]z[a]z[a]z", "z[a]z[a]z[a]z" };
        char id[40]; snprintf(id, sizeof id, "glue.limit%zu", lim);
        rc = rlim(ra, &s1_subst_info, NULL, 0, S, 9, lim, 64, out, &L, &K);
        out[rc == 0 ? L : 0] = 0;
        CHECK(id, rc == 0 && !strcmp(out, want[lim]) && K == (lim < 3 ? lim : 3), "rc %d out %s K %zu", rc, out, K);
    }
    /* limit 0 leaves the iterator FRESH: setters still apply afterwards */
    rx_iter it = RX_ITER_INIT((const unsigned char *)S, 9);
    rc = sub_limit(ra, &s1_subst_info, NULL, 0, &it, 0, (unsigned char *)out, 64, &L, &K);
    rx_iter_at(&it, 4);
    rc = sub_all_it(ra, &s1_subst_info, NULL, 0, &it, (unsigned char *)out, 64, &L);
    out[rc >= 0 ? L : 0] = 0;
    CHECK("glue.limit0.fresh.setter", rc == 2 && !strcmp(out, "zabz[a]z[a]z"), "rc %d out %s", rc, out);
    /* limit 1 runs exactly one search: a give-up in the 2nd search is not reached (§6¶3: it.rc read only at the end) */
    rc = rlim(&rx1_info, &s2_subst_info, NULL, 0, "x aaaaaaaaaaabbbbbbbbbbbbbbbbbbbbbbb", 36, 1, 128, out, &L, &K);
    CHECK("glue.limit1.one.search", rc == 0 && K == 1 && !strncmp(out, "<x> aaa", 7), "rc %d K %zu", rc, K);
    /* the iterator's give-up ends the find-all: its code, *len untouched, no tail (§10¶9) */
    L = UNTOUCHED;
    unsigned char o128[128];
    rc = sub_all(&rx1_info, &s2_subst_info, NULL, 0, (const unsigned char *)"x aaaaaaaaaaabbbbbbbbbbbbbbbbbbbbbbb", 36, o128, 128, &L);
    CHECK("glue.giveup", rc >= PCREC_ERR_FLOOR && rc <= -2 && L == UNTOUCHED, "rc %d L %zu", rc, L);
    L = UNTOUCHED;
    rc = sub_all(&rs_info, &s0_subst_info, NULL, 0, (const unsigned char *)"aaaaaaaaaaabbbbbbbbbbbbbbbbbbbb", 31, o128, 128, &L);
    CHECK("glue.giveup.first", rc >= PCREC_ERR_FLOOR && rc <= -2 && L == UNTOUCHED, "rc %d L %zu", rc, L);
    L = UNTOUCHED;
    rc = sub_all(&rx1_info, &s2_subst_info, NULL, 0, (const unsigned char *)"x aaaaaaaaaaabbbbbbbbbbbbbbbbbbbbbbb", 36, NULL, 0, &L);
    CHECK("glue.giveup.sizing", rc <= -2 && rc >= PCREC_ERR_FLOOR && L == UNTOUCHED, "rc %d", rc);
    L = UNTOUCHED;
    unsigned char o1[1];
    rc = sub_all(&rx1_info, &s2_subst_info, NULL, 0, (const unsigned char *)"x aaaaaaaaaaabbbbbbbbbbbbbbbbbbbbbbb", 36, o1, 1, &L);
    CHECK("glue.giveup.beats.nospace", rc <= -2 && rc >= PCREC_ERR_FLOOR && L == UNTOUCHED,
          "rc %d L %zu (a give-up after the output stopped fitting)", rc, L);
    /* the recipe agrees (§6¶2): the code, no tail */
    rc = rlim(&rx1_info, &s2_subst_info, NULL, 0, "x aaaaaaaaaaabbbbbbbbbbbbbbbbbbbbbbb", 36, SIZE_MAX, 128, out, &L, &K);
    CHECK("glue.giveup.recipe", rc <= -2 && rc >= PCREC_ERR_FLOOR, "rc %d", rc);

    /* RX_SUBST_STRICT: UNSET, *len untouched, even when out is too small (§10¶9) */
    L = UNTOUCHED;
    rc = rall(ra, &se1_subst_info, NULL, RX_SUBST_STRICT, "abaa", 4, 64, out, &L);
    CHECK("glue.unset", rc == PCREC_SUBST_UNSET && L == 0, "rc %d L %zu (rall zeroes L first)", rc, L);
    L = UNTOUCHED;
    {
        unsigned char *ob = malloc(64);
        rc = sub_all(ra, &se1_subst_info, NULL, RX_SUBST_STRICT, (const unsigned char *)"abaa", 4, ob, 64, &L);
        CHECK("glue.unset.untouched", rc == PCREC_SUBST_UNSET && L == UNTOUCHED, "rc %d L %zu", rc, L);
        free(ob);
    }
    rc = rall(ra, &se1_subst_info, NULL, RX_SUBST_STRICT, "abaa", 4, 0, out, &L);
    CHECK("glue.unset.beats.nospace", rc == PCREC_SUBST_UNSET, "rc %d", rc);
    rc = rall(ra, &se1_subst_info, NULL, 0, "abaa", 4, 64, out, &L);
    CHECK("glue.unset.default.blank", rc == 3 && !strcmp(out, "[a|b][a|][a|]"), "rc %d out %s (§4¶23: blank by default)", rc, out);
    rc = rlim(ra, &se1_subst_info, NULL, RX_SUBST_STRICT, "abaa", 4, 1, 64, out, &L, &K);
    out[rc == 0 ? L : 0] = 0;
    CHECK("glue.unset.notreached", rc == 0 && !strcmp(out, "[a|b]aa"), "rc %d out %s", rc, out);

    /* \K: a span starts after the previous end */
    rc = rall(&rk_info, &s0_subst_info, NULL, 0, "abab", 4, 64, out, &L);
    CHECK("glue.bsk", rc == 2 && !strcmp(out, "abab"), "rc %d out %s", rc, out);

    /* an iterator that is neither FRESH nor BOUND is PCREC_ERR_ITER (§10¶7) */
    it = RX_ITER_INIT((const unsigned char *)S, 9);
    while (ra_next(&it, NULL)) {}
    L = UNTOUCHED;
    rc = sub_all_it(ra, &s1_subst_info, NULL, 0, &it, (unsigned char *)out, 64, &L);
    CHECK("glue.ended.iterator", rc == PCREC_ERR_ITER && L == UNTOUCHED, "rc %d", rc);
    /* a setter on a BOUND iterator: the iterator refuses */
    it = RX_ITER_INIT((const unsigned char *)S, 9);
    ptrdiff_t c1[RA_NCAPS][2];
    ra_next(&it, c1);
    rx_iter_at(&it, 0);
    L = UNTOUCHED;
    rc = sub_all_it(ra, &s1_subst_info, NULL, 0, &it, (unsigned char *)out, 64, &L);
    CHECK("glue.iter.refused", rc == PCREC_ERR_ITER && L == UNTOUCHED, "rc %d L %zu", rc, L);
    /* a zeroed iterator struct */
    rx_iter zi; memset(&zi, 0, sizeof zi);
    L = UNTOUCHED;
    rc = sub_all_it(ra, &s1_subst_info, NULL, 0, &zi, (unsigned char *)out, 64, &L);
    CHECK("glue.iter.zeroed", rc == PCREC_ERR_ITER && L == UNTOUCHED, "rc %d", rc);
    /* rx_iter_at past n / mid-char */
    it = RX_ITER_INIT((const unsigned char *)S, 9);
    rx_iter_at(&it, 10);
    L = UNTOUCHED;
    rc = sub_all_it(ra, &s1_subst_info, NULL, 0, &it, (unsigned char *)out, 64, &L);
    printf("INFO glue.at.past.n rc=%d L=%zu\n", rc, L);
    CHECK("glue.at.past.n", rc < 0 ? L == UNTOUCHED : 1, "rc %d L %zu", rc, L);
    it = RX_ITER_INIT((const unsigned char *)"\xc3\xa9x", 3);
    rx_iter_at(&it, 1);
    L = UNTOUCHED;
    rc = sub_all_it(&ru2_info, &s2_subst_info, NULL, 0, &it, (unsigned char *)out, 64, &L);
    CHECK("glue.at.midchar", rc == PCREC_ERR_STARTPOS && L == UNTOUCHED, "rc %d", rc);
    /* rx_iter_at: the subject before the start is copied as gap */
    it = RX_ITER_INIT((const unsigned char *)"aaa", 3);
    rx_iter_at(&it, 1);
    rc = sub_all_it(&rg_info, &s2_subst_info, NULL, 0, &it, (unsigned char *)out, 64, &L);
    out[rc >= 0 ? L : 0] = 0;
    CHECK("glue.at.prefix", rc == 2 && !strcmp(out, "a<a><a>"), "rc %d out %s", rc, out);
    it = RX_ITER_INIT((const unsigned char *)"xaab", 4);
    rx_iter_at(&it, 1);
    rc = sub_all_it(&rgg_info, &s2_subst_info, NULL, 0, &it, (unsigned char *)out, 64, &L);
    out[rc >= 0 ? L : 0] = 0;
    CHECK("glue.at.G", rc == 2 && !strcmp(out, "x<a><a>b"), "rc %d out %s", rc, out);
    it = RX_ITER_INIT((const unsigned char *)"ab", 2);
    rx_iter_at(&it, 1);
    rc = sub_all_it(&rlb_info, &s2_subst_info, NULL, 0, &it, (unsigned char *)out, 64, &L);
    out[rc >= 0 ? L : 0] = 0;
    CHECK("glue.at.lookbehind", rc == 1 && !strcmp(out, "a<b>"), "rc %d out %s", rc, out);
    it = RX_ITER_INIT((const unsigned char *)"aaa", 3);
    rx_iter_at(&it, 3);
    rc = sub_all_it(&rg_info, &s2_subst_info, NULL, 0, &it, (unsigned char *)out, 64, &L);
    out[rc >= 0 ? L : 0] = 0;
    CHECK("glue.at.n", rc == 0 && !strcmp(out, "aaa"), "rc %d out %s", rc, out);

    /* §10¶7's other MISMATCH shapes */
    {
        const unsigned char *s = (const unsigned char *)"xaby";
        rx_iter i2 = RX_ITER_INIT(s, 4);
        rx_var vres[1];
        rx_subst_piece pc[64 * S2_PIECES];
        rx_subst_out o = { .pc = pc, .cap = 64 * S2_PIECES };
        rx_ctx ctx;
        int bad;
        unsigned char ob[16];
        rx_subst_ctx_init(&ctx, &i2, ra, &s2_subst_info, NULL, vres, 0, &bad);
        L = UNTOUCHED;
        rc = rx_subst_replace_all(ra->next_n, &i2, &s2_subst_info, &ctx, NULL, RX_SUBST_GAPS, &o, ob, 16, &L);
        CHECK("glue.flags.gaps", rc == PCREC_SUBST_MISMATCH && L == UNTOUCHED, "rc %d (flags takes STRICT only)", rc);
        i2 = RX_ITER_INIT(s, 4);
        rc = rx_subst_replace_all(ra->next_n, &i2, &s2_subst_info, &ctx, NULL, 0x4, &o, ob, 16, &L);
        CHECK("glue.flags.unknown", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
        rx_ctx c2 = ctx; c2.len = 3;
        i2 = RX_ITER_INIT(s, 4);
        rc = rx_subst_replace_all(ra->next_n, &i2, &s2_subst_info, &c2, NULL, 0, &o, ob, 16, &L);
        CHECK("glue.ctx.len.mismatch", rc == PCREC_SUBST_MISMATCH, "rc %d (ctx->len is not the iterator's)", rc);
        i2 = RX_ITER_INIT(s, 4);
        rc = rx_subst_replace_all(NULL, &i2, &s2_subst_info, &ctx, NULL, 0, &o, ob, 16, &L);
        CHECK("glue.no.next_n", rc == PCREC_SUBST_MISMATCH, "rc %d (next_n NULL)", rc);
        i2 = RX_ITER_INIT(s, 4);
        rc = rx_subst_replace_all(ra->next_n, &i2, &s2_subst_info, NULL, NULL, 0, &o, ob, 16, &L);
        CHECK("glue.no.ctx", rc == PCREC_SUBST_MISMATCH, "rc %d (a NULL argument)", rc);
        rx_subst_out o0 = { .pc = pc, .cap = S2_PIECES - 1 };
        i2 = RX_ITER_INIT(s, 4);
        rc = rx_subst_replace_all(ra->next_n, &i2, &s2_subst_info, &ctx, NULL, 0, &o0, ob, 16, &L);
        CHECK("glue.cap.below.P", rc == PCREC_SUBST_MISMATCH, "rc %d (o->cap below P: k == 0)", rc);
        /* the batch is the least of 64, o->cap / P, RX_SUBST_BATCH_PAIRS / ncap (substland2: the bound renamed, D175): one piece-set at a time still works */
        rx_subst_out o1p = { .pc = pc, .cap = S2_PIECES };
        i2 = RX_ITER_INIT((const unsigned char *)"zabaz", 5);
        rx_subst_ctx_init(&ctx, &i2, ra, &s2_subst_info, NULL, vres, 0, &bad);
        rc = rx_subst_replace_all(ra->next_n, &i2, &s2_subst_info, &ctx, NULL, 0, &o1p, ob, 16, &L);
        CHECK("glue.batch.of.one", rc == 2 && L == 9 && !memcmp(ob, "z<ab><a>z", 9), "rc %d L %zu", rc, L);
    }

    /* §10¶10 equivalence with §6¶4: replace-all and the batch recipe agree (the differential runs it over the corpus) */
    /* never -1, and the codes are below PCREC_ERR_ITER (§8¶1; -13 is reserved) */
    CHECK("codes.values", PCREC_SUBST_NOSPACE == -11 && PCREC_SUBST_BADSPAN == -12
          && PCREC_SUBST_UNSET == -14 && PCREC_SUBST_MISMATCH == -15 && PCREC_SUBST_MISSING_REF == -16
          && PCREC_ERR_UNSET_VAR == -8 && PCREC_SUBST_NOSPACE < PCREC_ERR_ITER
          && RX_SUBST_GAPS == 1u && RX_SUBST_STRICT == 2u, "code and flag values");
    DONE();
}
