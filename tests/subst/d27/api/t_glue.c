/* §6: the glue's returns, *outlen/*nsubst on every path, limit, sizing, NULLs. */
#include "t.h"

int main(void)
{
    rx_subst_binding b, b2, bk, bs, bx1, be;
    bind(&b, &ra_info, &s1_subst_info);    /* (a)(b)? -> [$1] */
    bind(&b2, &ra_info, &s2_subst_info);   /* <$0> */
    bind(&bk, &rk_info, &s0_subst_info);   /* a\Kb -> $0 */
    bind(&bs, &rs_info, &s0_subst_info);   /* (.*a){12}, step budget 1000 */
    bind(&bx1, &rx1_info, &s2_subst_info); /* x|(.*a){12} */
    bind(&be, &ra_info, &se1_subst_info);  /* [$1|$2], --unset=error */
    char out[512];
    size_t L, K;
    int rc;

    rc = glue(&b2, "xaby", 4, SIZE_MAX, 64, out, &L, &K);
    CHECK("glue.basic", rc == 0 && !strcmp(out, "x<ab>y") && L == 6 && K == 1, "rc %d out %s", rc, out);
    /* out == NULL sizes only and returns 0 (§6¶2) */
    rx_iter it = RX_ITER_INIT((const unsigned char *)"xaby", 4);
    L = K = 77;
    rc = pcrec_subst(&b2, &it, SIZE_MAX, NULL, 0, &L, &K);
    CHECK("glue.size.null", rc == 0 && L == 6 && K == 1, "rc %d L %zu K %zu", rc, L, K);
    it = RX_ITER_INIT((const unsigned char *)"xaby", 4);
    rc = pcrec_subst(&b2, &it, SIZE_MAX, NULL, 1000, &L, &K);
    CHECK("glue.size.null.bigcap", rc == 0 && L == 6, "rc %d L %zu (out NULL with cap > 0)", rc, L);
    /* the §6¶3 retry, literally */
    {
        const unsigned char *s = (const unsigned char *)"zabaz";
        size_t n = 5, cap = 2;
        unsigned char *o = malloc(cap);
        rx_iter it0 = RX_ITER_INIT(s, n), it2 = it0;
        size_t len, k;
        int r = pcrec_subst(&b2, &it2, SIZE_MAX, o, cap, &len, &k);
        CHECK("retry.first", r == PCREC_SUBST_NOSPACE && len == 9 && k == 2, "rc %d len %zu k %zu", r, len, k);
        if (r == PCREC_SUBST_NOSPACE && len != SIZE_MAX) {
            unsigned char *big = malloc(len ? len : 1);
            it2 = it0;
            r = pcrec_subst(&b2, &it2, SIZE_MAX, big, len, &len, &k);
            CHECK("retry.second", r == 0 && len == 9 && !memcmp(big, "z<ab><a>z", 9), "rc %d len %zu", r, len);
            free(big);
        }
        free(o);
    }
    /* §9 row 1: a* -> [$0] on "bab" needs 11 */
    rx_subst_binding bas; rx_subst_run rr[2];
    {
        int bad;
        pcrec_subst_bind(&bas, &ra_info, &s2_subst_info, rr, 2, NULL, 0, &bad);
    }
    /* NULL subject with n = 0 (match_api is silent on NULL; the glue reads none of it) */
    it = RX_ITER_INIT(NULL, 0);
    L = K = 9;
    rc = pcrec_subst(&b2, &it, SIZE_MAX, (unsigned char *)out, 64, &L, &K);
    CHECK("glue.null.subject", rc == 0 && L == 0 && K == 0, "rc %d L %zu K %zu", rc, L, K);
    it = RX_ITER_INIT(NULL, 0);
    rc = pcrec_subst(&b2, &it, 0, NULL, 0, &L, &K);
    CHECK("glue.null.everything", rc == 0 && L == 0 && K == 0, "rc %d", rc);
    /* empty subject, cap 0, out non-NULL: 0 */
    rc = glue(&b2, "", 0, SIZE_MAX, 0, out, &L, &K);
    CHECK("glue.empty.cap0", rc == 0 && L == 0 && K == 0, "rc %d", rc);
    /* every capacity 0..need: NOSPACE below, 0 at need; *outlen = need, *nsubst = full count */
    const char *S = "zabzazabz";        /* (a)(b)? -> [$1]: z[a]z[a]z[a]z  = 13 */
    for (size_t cap = 0; cap <= 14; cap++) {
        char id[40]; snprintf(id, sizeof id, "glue.cap%zu", cap);
        rc = glue(&b, S, 9, SIZE_MAX, cap, out, &L, &K);
        CHECK(id, (cap < 13 ? rc == PCREC_SUBST_NOSPACE : rc == 0) && L == 13 && K == 3,
              "rc %d L %zu K %zu", rc, L, K);
    }
    rc = glue(&b, S, 9, SIZE_MAX, 13, out, &L, &K);
    CHECK("glue.cap.exact.text", rc == 0 && !strcmp(out, "z[a]z[a]z[a]z"), "out %s", out);

    /* limit: 0 copies and leaves FRESH; 1 runs one search; N */
    for (size_t lim = 0; lim <= 4; lim++) {
        static const char *want[] = { "zabzazabz", "z[a]zazabz", "z[a]z[a]zabz", "z[a]z[a]z[a]z", "z[a]z[a]z[a]z" };
        char id[40]; snprintf(id, sizeof id, "glue.limit%zu", lim);
        rc = glue(&b, S, 9, lim, 64, out, &L, &K);
        CHECK(id, rc == 0 && !strcmp(out, want[lim]) && K == (lim < 3 ? lim : 3), "rc %d out %s K %zu", rc, out, K);
    }
    /* limit 0 leaves the iterator FRESH: setters still apply afterwards */
    it = RX_ITER_INIT((const unsigned char *)S, 9);
    rc = pcrec_subst(&b, &it, 0, (unsigned char *)out, 64, &L, &K);
    rx_iter_at(&it, 4);
    rc = pcrec_subst(&b, &it, SIZE_MAX, (unsigned char *)out, 64, &L, &K);
    out[rc == 0 ? L : 0] = 0;
    CHECK("glue.limit0.fresh.setter", rc == 0 && !strcmp(out, "zabz[a]z[a]z") && K == 2, "rc %d out %s", rc, out);
    /* limit 1 runs exactly one search: a give-up in the 2nd search is not reached */
    rc = glue(&bx1, "x aaaaaaaaaaabbbbbbbbbbbbbbbbbbbbbbb", 36, 1, 128, out, &L, &K);
    CHECK("glue.limit1.one.search", rc == 0 && K == 1 && !strncmp(out, "<x> aaa", 7), "rc %d K %zu", rc, K);
    /* the iterator's give-up ends it: its code, 0 and 0 */
    L = K = 5;
    rc = glue(&bx1, "x aaaaaaaaaaabbbbbbbbbbbbbbbbbbbbbbb", 36, SIZE_MAX, 128, out, &L, &K);
    CHECK("glue.giveup", rc >= PCREC_ERR_FLOOR && rc <= -2 && L == 0 && K == 0, "rc %d L %zu K %zu", rc, L, K);
    rc = glue(&bs, "aaaaaaaaaaabbbbbbbbbbbbbbbbbbbb", 31, SIZE_MAX, 128, out, &L, &K);
    CHECK("glue.giveup.first", rc >= PCREC_ERR_FLOOR && rc <= -2 && L == 0 && K == 0, "rc %d", rc);
    it = RX_ITER_INIT((const unsigned char *)"x aaaaaaaaaaabbbbbbbbbbbbbbbbbbbbbbb", 36);
    rc = pcrec_subst(&bx1, &it, SIZE_MAX, NULL, 0, &L, &K);
    CHECK("glue.giveup.sizing", rc <= -2 && rc >= PCREC_ERR_FLOOR && L == 0 && K == 0, "rc %d", rc);
    rc = glue(&bx1, "x aaaaaaaaaaabbbbbbbbbbbbbbbbbbbbbbb", 36, SIZE_MAX, 1, out, &L, &K);
    CHECK("glue.giveup.beats.nospace", rc <= -2 && rc >= PCREC_ERR_FLOOR && L == 0 && K == 0,
          "rc %d L %zu (a give-up after the output stopped fitting)", rc, L);

    /* --unset=error: UNSET, 0 and 0, even when out is too small */
    L = K = 5;
    rc = glue(&be, "abaa", 4, SIZE_MAX, 64, out, &L, &K);
    CHECK("glue.unset", rc == PCREC_SUBST_UNSET && L == 0 && K == 0, "rc %d L %zu K %zu", rc, L, K);
    rc = glue(&be, "abaa", 4, SIZE_MAX, 0, out, &L, &K);
    CHECK("glue.unset.beats.nospace", rc == PCREC_SUBST_UNSET && L == 0 && K == 0, "rc %d", rc);
    rc = glue(&be, "abaa", 4, 1, 64, out, &L, &K);
    CHECK("glue.unset.notreached", rc == 0 && !strcmp(out, "[a|b]aa"), "rc %d out %s", rc, out);

    /* \K: span starts after the previous end */
    rc = glue(&bk, "abab", 4, SIZE_MAX, 64, out, &L, &K);
    CHECK("glue.bsk", rc == 0 && !strcmp(out, "abab") && K == 2, "rc %d out %s", rc, out);

    /* a non-FRESH iterator handed to the glue: ENDED and BOUND (contract: FRESH) */
    it = RX_ITER_INIT((const unsigned char *)S, 9);
    while (ra_next(&it, NULL)) {}
    L = K = 5;
    rc = pcrec_subst(&b, &it, SIZE_MAX, (unsigned char *)out, 64, &L, &K);
    printf("INFO glue.ended.iterator rc=%d L=%zu K=%zu\n", rc, L, K);
    CHECK("glue.ended.iterator.not.neg1", rc != -1, "rc %d", rc);
    /* a setter on a BOUND iterator: the iterator refuses with PCREC_ERR_ITER */
    it = RX_ITER_INIT((const unsigned char *)S, 9);
    ptrdiff_t c1[RA_NCAPS][2];
    ra_next(&it, c1);
    rx_iter_at(&it, 0);
    L = K = 5;
    rc = pcrec_subst(&b, &it, SIZE_MAX, (unsigned char *)out, 64, &L, &K);
    CHECK("glue.iter.refused", rc == PCREC_ERR_ITER && L == 0 && K == 0, "rc %d L %zu K %zu", rc, L, K);
    /* a zeroed iterator struct */
    rx_iter zi; memset(&zi, 0, sizeof zi);
    rc = pcrec_subst(&b, &zi, SIZE_MAX, (unsigned char *)out, 64, &L, &K);
    CHECK("glue.iter.zeroed", rc == PCREC_ERR_ITER && L == 0 && K == 0, "rc %d", rc);
    /* rx_iter_at past n / mid-char */
    it = RX_ITER_INIT((const unsigned char *)S, 9);
    rx_iter_at(&it, 10);
    rc = pcrec_subst(&b, &it, SIZE_MAX, (unsigned char *)out, 64, &L, &K);
    printf("INFO glue.at.past.n rc=%d L=%zu K=%zu\n", rc, L, K);
    CHECK("glue.at.past.n", rc < 0 ? (L == 0 && K == 0) : 1, "rc %d L %zu", rc, L);
    rx_subst_binding bu; bind(&bu, &ru2_info, &s2_subst_info);
    it = RX_ITER_INIT((const unsigned char *)"\xc3\xa9x", 3);
    rx_iter_at(&it, 1);
    rc = pcrec_subst(&bu, &it, SIZE_MAX, (unsigned char *)out, 64, &L, &K);
    CHECK("glue.at.midchar", rc == PCREC_ERR_STARTPOS && L == 0 && K == 0, "rc %d", rc);
    /* rx_iter_at: the subject before the start is copied as gap (pcre2_substitute copies [0, startoffset)) */
    rx_subst_binding bg; bind(&bg, &rg_info, &s2_subst_info);
    it = RX_ITER_INIT((const unsigned char *)"aaa", 3);
    rx_iter_at(&it, 1);
    rc = pcrec_subst(&bg, &it, SIZE_MAX, (unsigned char *)out, 64, &L, &K);
    out[rc == 0 ? L : 0] = 0;
    CHECK("glue.at.prefix", rc == 0 && !strcmp(out, "a<a><a>") && K == 2, "rc %d out %s", rc, out);
    rx_subst_binding bG; bind(&bG, &rgg_info, &s2_subst_info);
    it = RX_ITER_INIT((const unsigned char *)"xaab", 4);
    rx_iter_at(&it, 1);
    rc = pcrec_subst(&bG, &it, SIZE_MAX, (unsigned char *)out, 64, &L, &K);
    out[rc == 0 ? L : 0] = 0;
    CHECK("glue.at.G", rc == 0 && !strcmp(out, "x<a><a>b"), "rc %d out %s", rc, out);
    rx_subst_binding blb; bind(&blb, &rlb_info, &s2_subst_info);
    it = RX_ITER_INIT((const unsigned char *)"ab", 2);
    rx_iter_at(&it, 1);
    rc = pcrec_subst(&blb, &it, SIZE_MAX, (unsigned char *)out, 64, &L, &K);
    out[rc == 0 ? L : 0] = 0;
    CHECK("glue.at.lookbehind", rc == 0 && !strcmp(out, "a<b>"), "rc %d out %s", rc, out);
    it = RX_ITER_INIT((const unsigned char *)"aaa", 3);
    rx_iter_at(&it, 3);
    rc = pcrec_subst(&bg, &it, SIZE_MAX, (unsigned char *)out, 64, &L, &K);
    out[rc == 0 ? L : 0] = 0;
    CHECK("glue.at.n", rc == 0 && !strcmp(out, "aaa") && K == 0, "rc %d out %s", rc, out);

    /* saturation through the glue: limit 0 with n = SIZE_MAX (no search, the tail is counted, never read) */
    it = RX_ITER_INIT((const unsigned char *)"x", SIZE_MAX);
    L = K = 5;
    rc = pcrec_subst(&b, &it, 0, NULL, 0, &L, &K);
    /* substfix: F8 was a DOC finding; §6¶2 now says a size past size_t is NOSPACE with SIZE_MAX */
    CHECK("glue.saturate.null.out", rc == PCREC_SUBST_NOSPACE && L == SIZE_MAX,
          "rc %d L %zu: §6¶2 a saturated size is NOSPACE with *outlen SIZE_MAX", rc, L);
    it = RX_ITER_INIT((const unsigned char *)"x", SIZE_MAX - 1);
    rc = pcrec_subst(&b, &it, 0, NULL, 0, &L, &K);
    CHECK("glue.nosat.max-1", rc == 0 && L == SIZE_MAX - 1, "rc %d L %zu", rc, L);
    it = RX_ITER_INIT((const unsigned char *)"x", SIZE_MAX);
    rc = pcrec_subst(&b, &it, 0, (unsigned char *)out, 8, &L, &K);
    CHECK("glue.saturate.out", rc == PCREC_SUBST_NOSPACE && L == SIZE_MAX && K == 0, "rc %d L %zu", rc, L);

    /* never -1, and the codes are below PCREC_ERR_ITER (§8¶1) */
    CHECK("codes.values", PCREC_SUBST_NOSPACE == -11 && PCREC_SUBST_BADSPAN == -12 && PCREC_SUBST_RENDER == -13
          && PCREC_SUBST_UNSET == -14 && PCREC_SUBST_MISMATCH == -15 && PCREC_SUBST_MISSING_REF == -16
          && PCREC_ERR_UNSET_VAR == -8 && PCREC_SUBST_NOSPACE < PCREC_ERR_ITER, "code values");

    /* PCREC_SUBST_PAIRS is compiled per TU: see t_pairs_*.c */
    (void)bas;
    DONE();
}
