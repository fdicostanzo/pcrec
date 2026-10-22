/* §2¶2, §6¶5, §7¶4: ${!name} variables through rx_iter_vars. */
#include "t.h"

static int run(const rx_subst_binding *b, const char *s, const rx_var *v, size_t nv, int setvars,
               size_t limit, size_t cap, char *out, size_t *L, size_t *K)
{
    unsigned char *o = malloc(cap ? cap : 1);
    rx_iter it = RX_ITER_INIT((const unsigned char *)s, strlen(s));
    if (setvars) rx_iter_vars(&it, v, nv);
    *L = *K = 55;
    int rc = pcrec_subst(b, &it, limit, o, cap, L, K);
    size_t m = rc == 0 ? *L : 0;
    memcpy(out, o, m); out[m] = 0;
    free(o);
    return rc;
}

int main(void)
{
    rx_subst_binding b, be;
    bind(&b, &rv_info, &sv_subst_info);    /* a -> [${!v}|${!w}|${!v}] */
    bind(&be, &rv_info, &sve_subst_info);  /* a -> [${!v}|${!w}], --unset=error */
    char out[256];
    size_t L, K;
    int rc;
    const unsigned char V[] = "VV", W[] = "w\0w";
    rx_var vs[] = { { "v", V, 2 }, { "w", W, 3 } };

    rc = run(&b, "xay", vs, 2, 1, SIZE_MAX, 64, out, &L, &K);
    CHECK("var.both", rc == 0 && L == 13 && !memcmp(out, "x[VV|w\0w|VV]y", 13), "rc %d L %zu", rc, L);
    rx_var v1[] = { { "v", V, 2 } };
    rc = run(&b, "xay", v1, 1, 1, SIZE_MAX, 64, out, &L, &K);
    CHECK("var.missing.empty", rc == 0 && !strcmp(out, "x[VV||VV]y"), "rc %d out %s", rc, out);
    rx_var vn[] = { { "v", NULL, 99 }, { "w", W, 0 } };
    rc = run(&b, "xay", vn, 2, 1, SIZE_MAX, 64, out, &L, &K);
    CHECK("var.null.p.and.len0", rc == 0 && !strcmp(out, "x[||]y"), "rc %d out %s", rc, out);
    rx_var vd[] = { { "w", (const unsigned char *)"1", 1 }, { "v", (const unsigned char *)"2", 1 },
                    { "v", (const unsigned char *)"3", 1 } };
    rc = run(&b, "xay", vd, 3, 1, SIZE_MAX, 64, out, &L, &K);
    CHECK("var.dup.first.wins", rc == 0 && !strcmp(out, "x[2|1|2]y"), "rc %d out %s", rc, out);
    rx_var vnn[] = { { NULL, V, 2 }, { "v", V, 1 } };
    rc = run(&b, "xay", vnn, 2, 1, SIZE_MAX, 64, out, &L, &K);
    CHECK("var.null.name.skipped", rc == 0 && !strcmp(out, "x[V||V]y"), "rc %d out %s", rc, out);
    rx_var vc[] = { { "V", V, 2 }, { "v ", V, 2 }, { "vv", V, 2 } };
    rc = run(&b, "xay", vc, 3, 1, SIZE_MAX, 64, out, &L, &K);
    CHECK("var.exact.name", rc == 0 && !strcmp(out, "x[||]y"), "rc %d out %s", rc, out);
    rc = run(&b, "xay", NULL, 0, 0, SIZE_MAX, 64, out, &L, &K);
    CHECK("var.no.setter", rc == 0 && !strcmp(out, "x[||]y"), "rc %d out %s", rc, out);
    rc = run(&b, "xay", NULL, 0, 1, SIZE_MAX, 64, out, &L, &K);
    CHECK("var.setter.null", rc == 0 && !strcmp(out, "x[||]y"), "rc %d out %s", rc, out);
    rc = run(&b, "aaa", vs, 2, 1, SIZE_MAX, 0, out, &L, &K);
    CHECK("var.size", rc == PCREC_SUBST_NOSPACE && L == 33 && K == 3, "rc %d L %zu", rc, L);
    /* a long value; sizing counts it */
    static unsigned char big[100000];
    memset(big, 'q', sizeof big);
    rx_var vb[] = { { "v", big, sizeof big } };
    rc = run(&b, "aa", vb, 1, 1, SIZE_MAX, 0, out, &L, &K);
    CHECK("var.big.size", rc == PCREC_SUBST_NOSPACE && L == 2 * (4 + 2 * sizeof big) && K == 2, "rc %d L %zu", rc, L);
    /* a len that would overflow the total: saturates (§4¶2) without reading the value */
    rx_var vh[] = { { "v", V, SIZE_MAX / 2 } };
    rc = run(&b, "a", vh, 1, 1, SIZE_MAX, 0, out, &L, &K);
    CHECK("var.huge.len.saturates", rc == PCREC_SUBST_NOSPACE && L == SIZE_MAX && K == 1, "rc %d L %zu K %zu", rc, L, K);

    /* --unset=error: PCREC_ERR_UNSET_VAR before any output, 0 and 0 */
    rc = run(&be, "xay", vs, 2, 1, SIZE_MAX, 64, out, &L, &K);
    CHECK("var.err.set", rc == 0 && L == 10, "rc %d L %zu", rc, L);
    rc = run(&be, "xay", v1, 1, 1, SIZE_MAX, 64, out, &L, &K);
    CHECK("var.err.missing", rc == PCREC_ERR_UNSET_VAR && L == 0 && K == 0, "rc %d L %zu K %zu", rc, L, K);
    rc = run(&be, "xyz", v1, 1, 1, SIZE_MAX, 64, out, &L, &K);
    CHECK("var.err.nomatch", rc == PCREC_ERR_UNSET_VAR && L == 0 && K == 0, "rc %d (no match: still before any output)", rc);
    rc = run(&be, "xay", v1, 1, 1, 0, 64, out, &L, &K);
    CHECK("var.err.limit0", rc == PCREC_ERR_UNSET_VAR && L == 0 && K == 0, "rc %d (limit 0)", rc);
    rc = run(&be, "xay", vn, 2, 1, SIZE_MAX, 64, out, &L, &K);
    CHECK("var.err.nullp", rc == PCREC_ERR_UNSET_VAR, "rc %d", rc);
    rx_var ve[] = { { "v", (const unsigned char *)"", 0 }, { "w", (const unsigned char *)"", 0 } };
    rc = run(&be, "xay", ve, 2, 1, SIZE_MAX, 64, out, &L, &K);
    CHECK("var.err.empty.is.set", rc == 0 && !strcmp(out, "x[|]y"), "rc %d", rc);
    rc = run(&be, "xay", vs, 2, 0, SIZE_MAX, 64, out, &L, &K);
    CHECK("var.err.no.setter", rc == PCREC_ERR_UNSET_VAR, "rc %d", rc);

    /* rx_subst_ctx_init directly (§7¶4) */
    rx_ctx ctx; rx_var vres[2];
    rx_iter it = RX_ITER_INIT((const unsigned char *)"abc", 3);
    rx_iter_vars(&it, vs, 2);
    rc = rx_subst_ctx_init(&ctx, &it, &b, vres);
    CHECK("ctxinit.fields", rc == 0 && ctx.len == 3 && ctx.ncap == (size_t)rv_info.ncaps && ctx.user == NULL
          && ctx.vars == vres && ctx.nvars == 2 && vres[0].p == V && vres[1].len == 3
          && !strcmp(vres[0].name, "v") && !strcmp(vres[1].name, "w"), "rc %d", rc);
    rx_subst_binding bn; bind(&bn, &ra_info, &s1_subst_info);
    it = RX_ITER_INIT((const unsigned char *)"abc", 3);
    rc = rx_subst_ctx_init(&ctx, &it, &bn, vres);
    CHECK("ctxinit.novars", rc == 0 && ctx.nvars == 0, "rc %d nvars %zu vars %p", rc, ctx.nvars, (void *)ctx.vars);
    /* an iterator that is BOUND keeps its variables */
    it = RX_ITER_INIT((const unsigned char *)"aa", 2);
    rx_iter_vars(&it, vs, 2);
    rv_next(&it, NULL);
    rc = rx_subst_ctx_init(&ctx, &it, &b, vres);
    CHECK("ctxinit.bound", rc == 0 && vres[0].p == V, "rc %d", rc);
    /* the vars an rx pattern reads and the ones the template reads come from the same array */
    DONE();
}
