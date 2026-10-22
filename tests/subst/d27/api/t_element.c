/* §4: the element called directly, with hand-made caps and cursors. */
#include "t.h"

static rx_ctx mkctx(const char *s, size_t n, size_t ncap)
{
    rx_ctx c; memset(&c, 0, sizeof c);
    c.subject = (const unsigned char *)s; c.len = n; c.ncap = ncap;
    return c;
}

int main(void)
{
    rx_subst_binding b, bo;
    bind(&b, &ra_info, &s1_subst_info);          /* [$1] over (a)(b)? : ncaps 3 */
    bind(&bo, &ra_info, &s2_subst_info);
    const char *s = "xxabyyab";
    rx_ctx ctx = mkctx(s, 8, 3);
    ptrdiff_t caps[4][3][2] = {
        { { 2, 4 }, { 2, 3 }, { 3, 4 } },
        { { 6, 8 }, { 6, 7 }, { 7, 8 } },
    };
    unsigned char out[64];
    rx_subst_cur cur;
    int rc;

    /* k = 0 checks the call and renders nothing (§4¶1) */
    cur = (rx_subst_cur){ 0, 0, 1 };
    memset(out, 0xEE, sizeof out);
    rc = s1_render(&b, &ctx, (const ptrdiff_t (*)[2])caps, 0, RX_SUBST_GAPS, out, 64, &cur);
    CHECK("el.k0", rc == 0 && cur.w == 0 && cur.prev == 0 && cur.fits == 1 && out[0] == 0xEE, "rc %d w %zu", rc, cur.w);
    rc = s1_render(&b, &ctx, NULL, 0, RX_SUBST_GAPS, out, 64, &cur);
    CHECK("el.k0.capsNULL", rc == 0, "rc %d", rc);
    rc = s1_render(&b, &ctx, NULL, 0, 0x2, out, 64, &cur);
    CHECK("el.k0.badflag", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    rc = s1_render(&bo, &ctx, NULL, 0, RX_SUBST_GAPS, out, 64, &cur);
    CHECK("el.k0.otherbinding", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    /* flags (§4¶3, §4¶4) */
    for (unsigned f = 2; f; f <<= 1) {
        cur = (rx_subst_cur){ 0, 0, 1 };
        rc = s1_render(&b, &ctx, (const ptrdiff_t (*)[2])caps, 1, f | RX_SUBST_GAPS, out, 64, &cur);
        if (rc != PCREC_SUBST_MISMATCH || cur.w) { CHECK("el.flags.each", 0, "flag %#x rc %d", f, rc); break; }
        if (f == 0x80000000u) CHECK("el.flags.each", 1, "%s", "");
    }
    /* ncap mismatch, unbound, other artifact's binding */
    ctx.ncap = 2;
    rc = s1_render(&b, &ctx, (const ptrdiff_t (*)[2])caps, 1, RX_SUBST_GAPS, out, 64, &cur);
    CHECK("el.ncap", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    ctx.ncap = 3;
    rx_subst_binding z; memset(&z, 0, sizeof z);
    rc = s1_render(&z, &ctx, (const ptrdiff_t (*)[2])caps, 1, RX_SUBST_GAPS, out, 64, &cur);
    CHECK("el.unbound", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    rc = s2_render(&b, &ctx, (const ptrdiff_t (*)[2])caps, 1, RX_SUBST_GAPS, out, 64, &cur);
    CHECK("el.other.artifact", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);

    /* rendering k = 2 with gaps; then the tail via rx_subst_put (§7¶5) */
    cur = (rx_subst_cur){ 0, 0, 1 };
    rc = s1_render(&b, &ctx, (const ptrdiff_t (*)[2])caps, 2, RX_SUBST_GAPS, out, 64, &cur);
    rx_subst_put(&cur, out, 64, ctx.subject + cur.prev, ctx.len - cur.prev);
    CHECK("el.k2.gaps", rc == 0 && cur.w == 10 && !memcmp(out, "xx[a]yy[a]", 10) && cur.prev == 8,
          "rc %d w %zu out %.*s", rc, cur.w, (int)cur.w, out);
    cur = (rx_subst_cur){ 0, 0, 1 };
    rc = s1_render(&b, &ctx, (const ptrdiff_t (*)[2])caps, 2, 0, out, 64, &cur);
    CHECK("el.k2.nogaps", rc == 0 && cur.w == 6 && !memcmp(out, "[a][a]", 6), "rc %d w %zu", rc, cur.w);
    /* split across calls == one call */
    cur = (rx_subst_cur){ 0, 0, 1 };
    rc = s1_render(&b, &ctx, (const ptrdiff_t (*)[2])caps, 1, RX_SUBST_GAPS, out, 64, &cur);
    rc |= s1_render(&b, &ctx, (const ptrdiff_t (*)[2])caps[1], 1, RX_SUBST_GAPS, out, 64, &cur);
    CHECK("el.split", rc == 0 && cur.w == 10 && !memcmp(out, "xx[a]yy[a]", 10), "rc %d w %zu", rc, cur.w);

    /* sizing: out NULL, cursor fits 0 */
    cur = (rx_subst_cur){ 0, 0, 0 };
    rc = s1_render(&b, &ctx, (const ptrdiff_t (*)[2])caps, 2, RX_SUBST_GAPS, NULL, 0, &cur);
    CHECK("el.size", rc == 0 && cur.w == 10 && cur.fits == 0, "rc %d w %zu", rc, cur.w);
    /* tight capacity: never past cap (ASan: exact malloc) */
    for (size_t cap = 0; cap <= 10; cap++) {
        unsigned char *o = malloc(cap ? cap : 1);
        cur = (rx_subst_cur){ 0, 0, 1 };
        rc = s1_render(&b, &ctx, (const ptrdiff_t (*)[2])caps, 2, RX_SUBST_GAPS, o, cap, &cur);
        rx_subst_put(&cur, o, cap, ctx.subject + cur.prev, ctx.len - cur.prev);
        char id[32]; snprintf(id, sizeof id, "el.cap%zu", cap);
        CHECK(id, rc == 0 && cur.w == 10 && cur.fits == (cap >= 10), "rc %d w %zu fits %d", rc, cur.w, cur.fits);
        free(o);
    }
    /* §4¶7: "the element writes cur->prev and cur->w; it writes no other caller state" -- fits? */
    cur = (rx_subst_cur){ 0, 0, 1 };
    rc = s1_render(&b, &ctx, (const ptrdiff_t (*)[2])caps, 1, RX_SUBST_GAPS, out, 2, &cur);
    CHECK("el.writes.fits", cur.fits == 1, "the element cleared cur->fits (now %d): §4¶7 says it writes only prev and w", cur.fits);

    /* BADSPAN (§4¶5) */
    ptrdiff_t bs[2][3][2] = { { { 3, 2 }, { -1, -1 }, { -1, -1 } } };
    cur = (rx_subst_cur){ 0, 0, 1 };
    rc = s1_render(&b, &ctx, (const ptrdiff_t (*)[2])bs, 1, RX_SUBST_GAPS, out, 64, &cur);
    CHECK("el.badspan.endlt", rc == PCREC_SUBST_BADSPAN, "rc %d", rc);
    cur = (rx_subst_cur){ 0, 0, 1 };
    rc = s1_render(&b, &ctx, (const ptrdiff_t (*)[2])bs, 1, 0, out, 64, &cur);
    CHECK("el.badspan.endlt.nogaps", rc == PCREC_SUBST_BADSPAN, "rc %d", rc);
    ptrdiff_t ov[2][3][2] = { { { 2, 5 }, { -1, -1 }, { -1, -1 } }, { { 4, 6 }, { -1, -1 }, { -1, -1 } } };
    cur = (rx_subst_cur){ 0, 0, 1 };
    rc = s1_render(&b, &ctx, (const ptrdiff_t (*)[2])ov, 2, RX_SUBST_GAPS, out, 64, &cur);
    CHECK("el.badspan.overlap", rc == PCREC_SUBST_BADSPAN, "rc %d", rc);
    cur = (rx_subst_cur){ 0, 0, 1 };
    rc = s1_render(&b, &ctx, (const ptrdiff_t (*)[2])ov, 2, 0, out, 64, &cur);
    CHECK("el.overlap.nogaps.ok", rc == 0 && cur.w == 4, "rc %d w %zu (§4¶5: without GAPS only the first test)", rc, cur.w);
    /* a backwards jump without gaps, then GAPS on the next call: prev was set by the no-gap call */
    ptrdiff_t ps[1][3][2] = { { { -1, -1 }, { -1, -1 }, { -1, -1 } } };
    cur = (rx_subst_cur){ 0, 0, 1 };
    rc = s1_render(&b, &ctx, (const ptrdiff_t (*)[2])ps, 1, 0, out, 64, &cur);
    CHECK("el.unset.match.span", rc == PCREC_SUBST_BADSPAN || rc == 0, "rc %d", rc);
    printf("INFO el.unset.match.span rc=%d (a whole-match span {-1,-1}: §4¶5 does not say)\n", rc);
    /* a group span that ends before it starts (§4¶5 speaks of the match span only) */
    ptrdiff_t gs[1][3][2] = { { { 2, 4 }, { 3, 2 }, { -1, -1 } } };
    cur = (rx_subst_cur){ 0, 0, 1 };
    rc = s1_render(&b, &ctx, (const ptrdiff_t (*)[2])gs, 1, RX_SUBST_GAPS, out, 64, &cur);
    printf("INFO el.group.backwards rc=%d (group span [3,2): §4¶5 silent)\n", rc);
    CHECK("el.group.backwards.norender", rc < 0 || cur.w <= 4, "rc %d w %zu", rc, cur.w);
    /* a group set past the match end (lookahead capture) renders */
    ptrdiff_t la[1][3][2] = { { { 2, 3 }, { 3, 6 }, { -1, -1 } } };
    cur = (rx_subst_cur){ 0, 0, 1 };
    rc = s1_render(&b, &ctx, (const ptrdiff_t (*)[2])la, 1, RX_SUBST_GAPS, out, 64, &cur);
    CHECK("el.group.past.end", rc == 0 && cur.w == 7 && !memcmp(out, "xx[byy]", 7), "rc %d w %zu", rc, cur.w);
    /* unset under --unset=error (§4¶6) */
    rx_subst_binding be; bind(&be, &ra_info, &se1_subst_info);
    ptrdiff_t un[1][3][2] = { { { 2, 3 }, { 2, 3 }, { -1, -1 } } };
    cur = (rx_subst_cur){ 0, 0, 1 };
    rc = se1_render(&be, &ctx, (const ptrdiff_t (*)[2])un, 1, RX_SUBST_GAPS, out, 64, &cur);
    CHECK("el.unset.error", rc == PCREC_SUBST_UNSET, "rc %d", rc);
    ptrdiff_t un2[1][3][2] = { { { 2, 3 }, { 2, 3 }, { 3, -1 } } };   /* half-set pair */
    cur = (rx_subst_cur){ 0, 0, 1 };
    rc = se1_render(&be, &ctx, (const ptrdiff_t (*)[2])un2, 1, RX_SUBST_GAPS, out, 64, &cur);
    CHECK("el.unset.halfpair", rc == PCREC_SUBST_UNSET, "rc %d", rc);

    /* saturation (§4¶2) */
    cur = (rx_subst_cur){ 0, SIZE_MAX - 3, 0 };
    rc = s1_render(&b, &ctx, (const ptrdiff_t (*)[2])caps, 1, RX_SUBST_GAPS, NULL, 0, &cur);
    CHECK("el.saturate", rc == 0 && cur.w == SIZE_MAX && cur.fits == 0, "rc %d w %zu", rc, cur.w);
    rc = s1_render(&b, &ctx, (const ptrdiff_t (*)[2])caps[1], 1, RX_SUBST_GAPS, NULL, 0, &cur);
    CHECK("el.saturate.sticky", rc == 0 && cur.w == SIZE_MAX, "w %zu", cur.w);
    cur = (rx_subst_cur){ 0, SIZE_MAX - 6, 0 };
    rc = s1_render(&b, &ctx, (const ptrdiff_t (*)[2])caps, 1, RX_SUBST_GAPS, NULL, 0, &cur);   /* +5 */
    CHECK("el.nosat.at.max-1", rc == 0 && cur.w == SIZE_MAX - 1, "w %zu", cur.w);
    cur = (rx_subst_cur){ 0, SIZE_MAX - 5, 0 };
    rc = s1_render(&b, &ctx, (const ptrdiff_t (*)[2])caps, 1, RX_SUBST_GAPS, NULL, 0, &cur);   /* +5 = SIZE_MAX */
    CHECK("el.sat.at.max", rc == 0 && cur.w == SIZE_MAX && cur.fits == 0, "w %zu", cur.w);
    /* rx_subst_put directly */
    cur = (rx_subst_cur){ 0, SIZE_MAX - 1, 0 };
    rx_subst_put(&cur, NULL, 0, (const unsigned char *)"", 0);
    CHECK("put.zero.at.max-1", cur.w == SIZE_MAX - 1, "w %zu", cur.w);
    rx_subst_put(&cur, NULL, 0, (const unsigned char *)"x", 1);
    CHECK("put.one.at.max-1", cur.w == SIZE_MAX, "w %zu", cur.w);
    cur = (rx_subst_cur){ 0, 0, 1 };
    rx_subst_put(&cur, out, 64, (const unsigned char *)s, SIZE_MAX);
    CHECK("put.huge.len", cur.w == SIZE_MAX && cur.fits == 0, "w %zu", cur.w);
    cur = (rx_subst_cur){ 0, 0, 1 };
    rx_subst_put(&cur, out, 4, (const unsigned char *)"abcd", 4);
    rx_subst_put(&cur, out, 4, (const unsigned char *)"", 0);
    CHECK("put.exact.then.empty", cur.fits == 1 && cur.w == 4, "fits %d", cur.fits);
    rx_subst_put(&cur, out, 4, (const unsigned char *)"e", 1);
    rx_subst_put(&cur, out, 4, (const unsigned char *)"", 0);
    CHECK("put.over.sticky", cur.fits == 0 && cur.w == 5, "fits %d w %zu", cur.fits, cur.w);
    /* after a miss, a later small piece that would fit must still not be written (bytes go while EVERYTHING so far fits) */
    unsigned char o8[8]; memset(o8, 0, 8);
    cur = (rx_subst_cur){ 0, 0, 1 };
    rx_subst_put(&cur, o8, 8, (const unsigned char *)"abcdefghij", 10);
    rx_subst_put(&cur, o8, 8, (const unsigned char *)"Z", 1);
    CHECK("put.no.write.after.miss", o8[0] == 0, "wrote after the output stopped fitting");

    /* the named-run resolution inside the element: duplicate names, first that participated */
    rx_subst_binding bd; bind(&bd, &rd_info, &sdn_subst_info);
    rx_ctx cd = mkctx("ab", 2, (size_t)rd_info.ncaps);
    ptrdiff_t dcaps[1][3][2] = { { { 1, 2 }, { -1, -1 }, { 1, 2 } } };
    cur = (rx_subst_cur){ 0, 0, 1 };
    rc = sdn_render(&bd, &cd, (const ptrdiff_t (*)[2])dcaps, 1, 0, out, 64, &cur);
    CHECK("el.dup.second", rc == 0 && cur.w == 3 && !memcmp(out, "<b>", 3), "rc %d w %zu", rc, cur.w);
    ptrdiff_t dcaps2[1][3][2] = { { { 0, 2 }, { 0, 1 }, { 1, 2 } } };
    cur = (rx_subst_cur){ 0, 0, 1 };
    rc = sdn_render(&bd, &cd, (const ptrdiff_t (*)[2])dcaps2, 1, 0, out, 64, &cur);
    CHECK("el.dup.first.wins", rc == 0 && cur.w == 3 && !memcmp(out, "<a>", 3), "rc %d w %zu", rc, cur.w);
    ptrdiff_t dcaps3[1][3][2] = { { { 0, 0 }, { 0, 0 }, { 0, 1 } } };   /* set-to-empty participates */
    cur = (rx_subst_cur){ 0, 0, 1 };
    rc = sdn_render(&bd, &cd, (const ptrdiff_t (*)[2])dcaps3, 1, 0, out, 64, &cur);
    CHECK("el.dup.empty.participates", rc == 0 && cur.w == 2, "rc %d w %zu", rc, cur.w);
    DONE();
}
