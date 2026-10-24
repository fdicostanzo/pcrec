/* §2¶3, §4¶23, §7¶4: ${!name} variables through rx_iter_vars and the context
 * setup.  substb2: unset handling is the run-time PCREC_SUBST_STRICT flag, and
 * the setup (pcrec_subst_ctx_init) is where a strict unset variable is refused. */
#include "t.h"

/* one find-all with variables: replace-all for `all`, the recipe for a limit */
static int run(const struct pcrec_subst_info *t, unsigned flags, const char *s, const rx_var *v, size_t nv,
               int setvars, size_t limit, size_t cap, char *out, size_t *L)
{
    unsigned char *o = malloc(cap ? cap : 1);
    rx_iter it = RX_ITER_INIT((const unsigned char *)s, strlen(s));
    if (setvars) rx_iter_vars(&it, v, nv);
    *L = 0;
    size_t k = 0;
    int rc = limit == SIZE_MAX ? sub_all_it(&rv_info, t, NULL, flags, &it, o, cap, L)
                               : sub_limit(&rv_info, t, NULL, flags, &it, limit, o, cap, L, &k);
    size_t m = rc >= 0 ? *L : 0;
    memcpy(out, o, m); out[m] = 0;
    free(o);
    return rc;
}

int main(void)
{
    const struct pcrec_subst_info *sv = &sv_subst_info;    /* a -> [${!v}|${!w}|${!v}] */
    const struct pcrec_subst_info *se = &sve_subst_info;   /* a -> [${!v}|${!w}] */
    const unsigned ST = PCREC_SUBST_STRICT;
    char out[256];
    size_t L;
    int rc;
    const unsigned char V[] = "VV", W[] = "w\0w";
    rx_var vs[] = { { "v", V, 2 }, { "w", W, 3 } };

    rc = run(sv, 0, "xay", vs, 2, 1, SIZE_MAX, 64, out, &L);
    CHECK("var.both", rc == 1 && L == 13 && !memcmp(out, "x[VV|w\0w|VV]y", 13), "rc %d L %zu", rc, L);
    rx_var v1[] = { { "v", V, 2 } };
    rc = run(sv, 0, "xay", v1, 1, 1, SIZE_MAX, 64, out, &L);
    CHECK("var.missing.empty", rc == 1 && !strcmp(out, "x[VV||VV]y"), "rc %d out %s", rc, out);
    rx_var vn[] = { { "v", NULL, 99 }, { "w", W, 0 } };
    rc = run(sv, 0, "xay", vn, 2, 1, SIZE_MAX, 64, out, &L);
    CHECK("var.null.p.and.len0", rc == 1 && !strcmp(out, "x[||]y"), "rc %d out %s", rc, out);
    rx_var vd[] = { { "w", (const unsigned char *)"1", 1 }, { "v", (const unsigned char *)"2", 1 },
                    { "v", (const unsigned char *)"3", 1 } };
    rc = run(sv, 0, "xay", vd, 3, 1, SIZE_MAX, 64, out, &L);
    CHECK("var.dup.first.wins", rc == 1 && !strcmp(out, "x[2|1|2]y"), "rc %d out %s", rc, out);
    rx_var vnn[] = { { NULL, V, 2 }, { "v", V, 1 } };
    rc = run(sv, 0, "xay", vnn, 2, 1, SIZE_MAX, 64, out, &L);
    CHECK("var.null.name.skipped", rc == 1 && !strcmp(out, "x[V||V]y"), "rc %d out %s", rc, out);
    rx_var vc[] = { { "V", V, 2 }, { "v ", V, 2 }, { "vv", V, 2 } };
    rc = run(sv, 0, "xay", vc, 3, 1, SIZE_MAX, 64, out, &L);
    CHECK("var.exact.name", rc == 1 && !strcmp(out, "x[||]y"), "rc %d out %s", rc, out);
    rc = run(sv, 0, "xay", NULL, 0, 0, SIZE_MAX, 64, out, &L);
    CHECK("var.no.setter", rc == 1 && !strcmp(out, "x[||]y"), "rc %d out %s", rc, out);
    rc = run(sv, 0, "xay", NULL, 0, 1, SIZE_MAX, 64, out, &L);
    CHECK("var.setter.null", rc == 1 && !strcmp(out, "x[||]y"), "rc %d out %s", rc, out);
    rc = run(sv, 0, "aaa", vs, 2, 1, SIZE_MAX, 0, out, &L);
    CHECK("var.size", rc == PCREC_SUBST_NOSPACE && L == 33, "rc %d L %zu", rc, L);
    /* a long value; sizing counts it */
    static unsigned char big[100000];
    memset(big, 'q', sizeof big);
    rx_var vb[] = { { "v", big, sizeof big } };
    rc = run(sv, 0, "aa", vb, 1, 1, SIZE_MAX, 0, out, &L);
    CHECK("var.big.size", rc == PCREC_SUBST_NOSPACE && L == 2 * (4 + 2 * sizeof big), "rc %d L %zu", rc, L);
    /* a len that would overflow the total: NOSPACE with *len SIZE_MAX (§10¶8), without reading the value */
    rx_var vh[] = { { "v", V, SIZE_MAX / 2 } };
    rc = run(sv, 0, "a", vh, 1, 1, SIZE_MAX, 0, out, &L);
    CHECK("var.huge.len.saturates", rc == PCREC_SUBST_NOSPACE && L == SIZE_MAX, "rc %d L %zu", rc, L);
    /* the same through the recipe's own sink, counting the loop (§6¶2) */
    {
        rx_iter it = RX_ITER_INIT((const unsigned char *)"xay", 3);
        rx_iter_vars(&it, vh, 1);
        size_t k = 0;
        L = 0;
        rc = sub_limit(&rv_info, sv, NULL, 0, &it, 1, NULL, 0, &L, &k);
        printf("INFO var.huge.len.recipe rc=%d L=%zu (the caller's own sink: the wrap is the recipe's to handle)\n", rc, L);
    }

    /* PCREC_SUBST_STRICT: ERR_UNSET_VAR at the setup, before any output (§4¶23, §7¶4) */
    rc = run(se, ST, "xay", vs, 2, 1, SIZE_MAX, 64, out, &L);
    CHECK("var.err.set", rc == 1 && L == 10, "rc %d L %zu", rc, L);
    rc = run(se, ST, "xay", v1, 1, 1, SIZE_MAX, 64, out, &L);
    CHECK("var.err.missing", rc == PCREC_ERR_UNSET_VAR && L == 0, "rc %d L %zu", rc, L);
    rc = run(se, ST, "xyz", v1, 1, 1, SIZE_MAX, 64, out, &L);
    CHECK("var.err.nomatch", rc == PCREC_ERR_UNSET_VAR && L == 0, "rc %d (no match: still before any output)", rc);
    rc = run(se, ST, "xay", v1, 1, 1, 0, 64, out, &L);
    CHECK("var.err.limit0", rc == PCREC_ERR_UNSET_VAR && L == 0, "rc %d (limit 0)", rc);
    rc = run(se, ST, "xay", vn, 2, 1, SIZE_MAX, 64, out, &L);
    CHECK("var.err.nullp", rc == PCREC_ERR_UNSET_VAR, "rc %d", rc);
    rx_var ve[] = { { "v", (const unsigned char *)"", 0 }, { "w", (const unsigned char *)"", 0 } };
    rc = run(se, ST, "xay", ve, 2, 1, SIZE_MAX, 64, out, &L);
    CHECK("var.err.empty.is.set", rc == 1 && !strcmp(out, "x[|]y"), "rc %d", rc);
    rc = run(se, ST, "xay", vs, 2, 0, SIZE_MAX, 64, out, &L);
    CHECK("var.err.no.setter", rc == PCREC_ERR_UNSET_VAR, "rc %d", rc);
    rc = run(se, 0, "xay", v1, 1, 1, SIZE_MAX, 64, out, &L);
    CHECK("var.err.default.blank", rc == 1 && !strcmp(out, "x[VV|]y"), "rc %d out %s (without the flag: blank)", rc, out);

    /* pcrec_subst_ctx_init directly (§7¶4) */
    rx_ctx ctx; rx_var vres[2];
    int bad;
    rx_iter it = RX_ITER_INIT((const unsigned char *)"abc", 3);
    rx_iter_vars(&it, vs, 2);
    rc = pcrec_subst_ctx_init(&ctx, &it, &rv_info, sv, NULL, vres, 0, &bad);
    CHECK("ctxinit.fields", rc == 0 && ctx.len == 3 && ctx.ncap == (size_t)rv_info.ncaps && ctx.user == NULL
          && ctx.vars == vres && ctx.nvars == 2 && vres[0].p == V && vres[1].len == 3
          && !strcmp(vres[0].name, "v") && !strcmp(vres[1].name, "w"), "rc %d", rc);
    rc = pcrec_subst_ctx_init(&ctx, &it, &rv_info, se, NULL, vres, ST, &bad);
    CHECK("ctxinit.strict.set", rc == 0, "rc %d", rc);
    it = RX_ITER_INIT((const unsigned char *)"abc", 3);
    rx_iter_vars(&it, v1, 1);
    rc = pcrec_subst_ctx_init(&ctx, &it, &rv_info, se, NULL, vres, ST, &bad);
    CHECK("ctxinit.strict.unset", rc == PCREC_ERR_UNSET_VAR, "rc %d", rc);
    rc = pcrec_subst_ctx_init(&ctx, &it, &rv_info, se, NULL, vres, 0, &bad);
    CHECK("ctxinit.default.unset", rc == 0 && vres[1].p == NULL && vres[1].len == 0, "rc %d", rc);
    it = RX_ITER_INIT((const unsigned char *)"abc", 3);
    rc = pcrec_subst_ctx_init(&ctx, &it, &ra_info, &s1_subst_info, NULL, vres, 0, &bad);
    CHECK("ctxinit.novars", rc == 0 && ctx.nvars == 0 && ctx.vars == NULL, "rc %d nvars %zu vars %p", rc, ctx.nvars, (const void *)ctx.vars);
    /* an iterator that is BOUND keeps its variables */
    it = RX_ITER_INIT((const unsigned char *)"aa", 2);
    rx_iter_vars(&it, vs, 2);
    rv_next(&it, NULL);
    rc = pcrec_subst_ctx_init(&ctx, &it, &rv_info, sv, NULL, vres, 0, &bad);
    CHECK("ctxinit.bound", rc == 0 && vres[0].p == V, "rc %d", rc);
    DONE();
}
