/* §4: the element called directly, with hand-made caps and an output record
 * of pieces.  substb2: was the R3 byte-cursor element; the bytes are the
 * flattened pieces. */
#include "t.h"

#define P1 S1_PIECES   /* [$1]: gap, "[", $1, "]" */

/* a context for subject s through the real setup, so the check has run (§7¶4) */
static rx_ctx mkctx(const struct rx_info *rx, const struct pcrec_subst_info *t, const pcrec_subst_map *map,
                    const char *s, size_t n, unsigned flags, rx_var *vres)
{
    rx_ctx c;
    rx_iter it = RX_ITER_INIT((const unsigned char *)s, n);
    int bad, rc = pcrec_subst_ctx_init(&c, &it, rx, t, map, vres, flags, &bad);
    if (rc < 0) { printf("FAIL mkctx rc %d\n", rc); exit(1); }
    return c;
}

/* flat bytes of o's pieces, then the tail from o->prev (a replacement's last step) */
static size_t bytes(const pcrec_subst_out *o, const rx_ctx *c, int tail, unsigned char *out, size_t cap)
{
    size_t w = flat(o, out, cap);
    if (tail && c->len > o->prev) { memcpy(out + w, c->subject + o->prev, c->len - o->prev); w += c->len - o->prev; }
    return w;
}

int main(void)
{
    rx_var vres[4];
    const char *s = "xxabyyab";
    rx_ctx ctx = mkctx(&ra_info, &s1_subst_info, NULL, s, 8, 0, vres);
    ptrdiff_t caps[4][3][2] = {
        { { 2, 4 }, { 2, 3 }, { 3, 4 } },
        { { 6, 8 }, { 6, 7 }, { 7, 8 } },
    };
    unsigned char out[64];
    pcrec_subst_piece pc[64];
    pcrec_subst_out o;
    int rc;
#define RESET() do { memset(pc, 0xEE, sizeof pc); o = (pcrec_subst_out){ .pc = pc, .cap = 64 }; } while (0)

    CHECK("el.npieces", P1 == 4 && s1_subst_info.npieces == 4, "npieces %d", s1_subst_info.npieces);
    /* k = 0 checks the call and renders nothing (§4¶2) */
    RESET();
    rc = s1_render(&ctx, NULL, (ptrdiff_t (*)[2])caps, 0, PCREC_SUBST_GAPS, &o);
    CHECK("el.k0", rc == 0 && o.n == 0 && o.sn == 0 && o.prev == 0 && *(unsigned char *)&pc[0] == 0xEE, "rc %d n %zu", rc, o.n);
    rc = s1_render(&ctx, NULL, NULL, 0, PCREC_SUBST_GAPS, &o);
    CHECK("el.k0.capsNULL", rc == 0, "rc %d", rc);
    rc = s1_render(&ctx, NULL, NULL, 0, 0x4, &o);
    CHECK("el.k0.badflag", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    /* flags (§4¶25, §4¶26): any other bit is MISMATCH, nothing written */
    for (unsigned f = 4; f; f <<= 1) {
        RESET();
        rc = s1_render(&ctx, NULL, (ptrdiff_t (*)[2])caps, 1, f | PCREC_SUBST_GAPS, &o);
        if (rc != PCREC_SUBST_MISMATCH || o.n) { CHECK("el.flags.each", 0, "flag %#x rc %d", f, rc); break; }
        if (f == 0x80000000u) CHECK("el.flags.each", 1, "%s", "");
    }
    /* the output record's fields (§4¶3): the element sets n, prev; sn stays 0 without a case region */
    RESET();
    rc = s1_render(&ctx, NULL, (ptrdiff_t (*)[2])caps, 2, PCREC_SUBST_GAPS, &o);
    size_t w = bytes(&o, &ctx, 1, out, 64);
    CHECK("el.k2.gaps", rc == 0 && o.n == 2 * P1 && o.prev == 8 && o.sn == 0 && w == 10 && !memcmp(out, "xx[a]yy[a]", 10),
          "rc %d n %zu prev %zu w %zu out %.*s", rc, o.n, o.prev, w, (int)w, out);
    CHECK("el.k2.unwritten", *(unsigned char *)&pc[2 * P1] == 0xEE && o.need == 0 && o.sneed == 0,
          "pieces past k*P untouched (§4¶5)");
    RESET();
    rc = s1_render(&ctx, NULL, (ptrdiff_t (*)[2])caps, 2, 0, &o);
    w = bytes(&o, &ctx, 0, out, 64);
    CHECK("el.k2.nogaps", rc == 0 && o.n == 2 * (P1 - 1) && w == 6 && !memcmp(out, "[a][a]", 6), "rc %d n %zu w %zu", rc, o.n, w);
    /* split across calls == one call (§4¶4: n carries between calls) */
    RESET();
    rc = s1_render(&ctx, NULL, (ptrdiff_t (*)[2])caps, 1, PCREC_SUBST_GAPS, &o);
    rc |= s1_render(&ctx, NULL, (ptrdiff_t (*)[2])caps[1], 1, PCREC_SUBST_GAPS, &o);
    w = bytes(&o, &ctx, 1, out, 64);
    CHECK("el.split", rc == 0 && o.n == 2 * P1 && w == 10 && !memcmp(out, "xx[a]yy[a]", 10), "rc %d w %zu", rc, w);
    /* §4¶9: every piece is written, empty ones included, and p is never NULL */
    int nn = 1;
    for (size_t i = 0; i < o.n; i++) if (!pc[i].p) nn = 0;
    CHECK("el.p.never.null", nn, "a piece with p == NULL");
    ptrdiff_t unx[1][3][2] = { { { 2, 3 }, { -1, -1 }, { -1, -1 } } };   /* group 1 unset */
    RESET();
    rc = s1_render(&ctx, NULL, (ptrdiff_t (*)[2])unx, 1, PCREC_SUBST_GAPS, &o);
    CHECK("el.unset.empty.piece", rc == 0 && o.n == P1 && pc[2].len == 0 && pc[2].p != NULL && pc[0].len == 2,
          "rc %d n %zu len %zu", rc, o.n, pc[2].len);
    /* pieces point into the subject, and into the artifact's constant data for literals (§4¶22 table) */
    RESET();
    s1_render(&ctx, NULL, (ptrdiff_t (*)[2])caps, 1, PCREC_SUBST_GAPS, &o);
    CHECK("el.piece.sources", pc[0].p == ctx.subject && pc[2].p == ctx.subject + 2 && pc[2].len == 1,
          "gap and group point into the subject");

    /* NOSPACE in pieces: cap - n < k*P, need = n + k*P, n unchanged (§4¶14) */
    for (size_t cap = 0; cap <= 2 * P1 + 1; cap++) {
        pcrec_subst_piece *pp = malloc((cap ? cap : 1) * sizeof *pp);
        pcrec_subst_out oo = { .pc = pp, .cap = cap };
        rc = s1_render(&ctx, NULL, (ptrdiff_t (*)[2])caps, 2, PCREC_SUBST_GAPS, &oo);
        char id[32]; snprintf(id, sizeof id, "el.cap%zu", cap);
        CHECK(id, cap < 2 * P1 ? (rc == PCREC_SUBST_NOSPACE && oo.need == 2 * P1 && oo.n == 0 && oo.prev == 0)
                               : (rc == 0 && oo.n == 2 * P1), "rc %d need %zu n %zu", rc, oo.need, oo.n);
        free(pp);
    }
    /* NOSPACE after earlier pieces: need = n + k*P, n and prev unchanged */
    RESET();
    o.cap = 2 * P1 - 1;
    rc = s1_render(&ctx, NULL, (ptrdiff_t (*)[2])caps, 1, PCREC_SUBST_GAPS, &o);
    rc = s1_render(&ctx, NULL, (ptrdiff_t (*)[2])caps[1], 1, PCREC_SUBST_GAPS, &o);
    CHECK("el.nospace.after.n", rc == PCREC_SUBST_NOSPACE && o.need == 2 * P1 && o.n == P1 && o.prev == 4,
          "rc %d need %zu n %zu prev %zu", rc, o.need, o.n, o.prev);
    /* overflow of the product and of the sum: NOSPACE with SIZE_MAX (§4¶14) */
    RESET();
    rc = s1_render(&ctx, NULL, (ptrdiff_t (*)[2])caps, SIZE_MAX / 2, PCREC_SUBST_GAPS, &o);
    CHECK("el.need.overflow.product", rc == PCREC_SUBST_NOSPACE && o.need == SIZE_MAX && o.n == 0, "rc %d need %zu", rc, o.need);
    {   /* cap and n at the top: the pieces are never touched, the sum n + k*P does not fit */
        pcrec_subst_out oo = { .pc = pc, .cap = SIZE_MAX, .n = SIZE_MAX - 1 };
        rc = s1_render(&ctx, NULL, (ptrdiff_t (*)[2])caps, 1, PCREC_SUBST_GAPS, &oo);
        CHECK("el.need.overflow.sum", rc == PCREC_SUBST_NOSPACE && oo.need == SIZE_MAX && oo.n == SIZE_MAX - 1,
              "rc %d need %zu", rc, oo.need);
    }

    /* BADSPAN (§4¶16-19) */
    ptrdiff_t bs[2][3][2] = { { { 3, 2 }, { -1, -1 }, { -1, -1 } } };
    RESET();
    rc = s1_render(&ctx, NULL, (ptrdiff_t (*)[2])bs, 1, PCREC_SUBST_GAPS, &o);
    CHECK("el.badspan.endlt", rc == PCREC_SUBST_BADSPAN && o.n == 0 && o.prev == 0, "rc %d", rc);
    RESET();
    rc = s1_render(&ctx, NULL, (ptrdiff_t (*)[2])bs, 1, 0, &o);
    CHECK("el.badspan.endlt.nogaps", rc == PCREC_SUBST_BADSPAN, "rc %d", rc);
    ptrdiff_t ov[2][3][2] = { { { 2, 5 }, { -1, -1 }, { -1, -1 } }, { { 4, 6 }, { -1, -1 }, { -1, -1 } } };
    RESET();
    rc = s1_render(&ctx, NULL, (ptrdiff_t (*)[2])ov, 2, PCREC_SUBST_GAPS, &o);
    CHECK("el.badspan.overlap", rc == PCREC_SUBST_BADSPAN, "rc %d", rc);
    /* §4¶21: the matches before the failing one are committed, nothing of it */
    CHECK("el.commit.prefix", o.n == P1 && o.prev == 5, "n %zu prev %zu (match 0 committed)", o.n, o.prev);
    RESET();
    rc = s1_render(&ctx, NULL, (ptrdiff_t (*)[2])ov, 2, 0, &o);
    CHECK("el.overlap.nogaps.ok", rc == 0 && flat(&o, out, 64) == 4, "rc %d (§4¶20: without GAPS only the first test)", rc);
    ptrdiff_t ps[1][3][2] = { { { -1, -1 }, { -1, -1 }, { -1, -1 } } };
    RESET();
    rc = s1_render(&ctx, NULL, (ptrdiff_t (*)[2])ps, 1, 0, &o);
    CHECK("el.unset.match.span", rc == PCREC_SUBST_BADSPAN, "rc %d (§4¶17: a whole-match span {-1,-1})", rc);
    ptrdiff_t past[1][3][2] = { { { 2, 9 }, { -1, -1 }, { -1, -1 } } };
    RESET();
    rc = s1_render(&ctx, NULL, (ptrdiff_t (*)[2])past, 1, 0, &o);
    CHECK("el.badspan.past.len", rc == PCREC_SUBST_BADSPAN, "rc %d (§4¶17: ends past ctx->len)", rc);
    /* a referenced group's set span that ends before it starts (§4¶19) */
    ptrdiff_t gs[1][3][2] = { { { 2, 4 }, { 3, 2 }, { -1, -1 } } };
    RESET();
    rc = s1_render(&ctx, NULL, (ptrdiff_t (*)[2])gs, 1, PCREC_SUBST_GAPS, &o);
    CHECK("el.group.backwards", rc == PCREC_SUBST_BADSPAN, "rc %d", rc);
    /* a group set past the match end (lookahead capture) renders */
    ptrdiff_t la[1][3][2] = { { { 2, 3 }, { 3, 6 }, { -1, -1 } } };
    RESET();
    rc = s1_render(&ctx, NULL, (ptrdiff_t (*)[2])la, 1, PCREC_SUBST_GAPS, &o);
    w = bytes(&o, &ctx, 0, out, 64);
    CHECK("el.group.past.end", rc == 0 && w == 7 && !memcmp(out, "xx[byy]", 7), "rc %d w %zu", rc, w);

    /* unset under PCREC_SUBST_STRICT (§4¶23): the first match with one; the default is an empty piece */
    ptrdiff_t un[1][3][2] = { { { 2, 3 }, { 2, 3 }, { -1, -1 } } };
    rx_ctx cs = mkctx(&ra_info, &se1_subst_info, NULL, s, 8, PCREC_SUBST_STRICT, vres);
    RESET();
    rc = se1_render(&cs, NULL, (ptrdiff_t (*)[2])un, 1, PCREC_SUBST_GAPS | PCREC_SUBST_STRICT, &o);
    CHECK("el.unset.strict", rc == PCREC_SUBST_UNSET && o.n == 0, "rc %d", rc);
    RESET();
    rc = se1_render(&cs, NULL, (ptrdiff_t (*)[2])un, 1, PCREC_SUBST_GAPS, &o);
    w = bytes(&o, &cs, 0, out, 64);
    CHECK("el.unset.default.blank", rc == 0 && w == 6 && !memcmp(out, "xx[a|]", 6), "rc %d w %zu", rc, w);
    ptrdiff_t un2[1][3][2] = { { { 2, 3 }, { 2, 3 }, { 3, -1 } } };   /* half-set pair */
    RESET();
    rc = se1_render(&cs, NULL, (ptrdiff_t (*)[2])un2, 1, PCREC_SUBST_GAPS | PCREC_SUBST_STRICT, &o);
    CHECK("el.unset.halfpair", rc == PCREC_SUBST_UNSET, "rc %d", rc);
    /* the first match that has one: matches before it are committed (§4¶21) */
    ptrdiff_t un3[2][3][2] = { { { 2, 3 }, { 2, 3 }, { 3, 4 } }, { { 5, 6 }, { 5, 6 }, { -1, -1 } } };
    RESET();
    rc = se1_render(&cs, NULL, (ptrdiff_t (*)[2])un3, 2, PCREC_SUBST_GAPS | PCREC_SUBST_STRICT, &o);
    CHECK("el.unset.commit.prefix", rc == PCREC_SUBST_UNSET && o.n == se1_subst_info.npieces && o.prev == 3,
          "rc %d n %zu prev %zu", rc, o.n, o.prev);

    /* the run walk: duplicate names, first that participated; a map and the element (§3¶5) */
    pcrec_subst_map md;
    int bad;
    rc = mkmap(&md, &sdn_subst_info, &rd_info, &bad);
    rx_ctx cd = mkctx(&rd_info, &sdn_subst_info, &md, "ab", 2, 0, vres);
    ptrdiff_t dcaps[1][3][2] = { { { 1, 2 }, { -1, -1 }, { 1, 2 } } };
    RESET();
    rc = sdn_render(&cd, &md, (ptrdiff_t (*)[2])dcaps, 1, 0, &o);
    w = bytes(&o, &cd, 0, out, 64);
    CHECK("el.dup.second", rc == 0 && w == 3 && !memcmp(out, "<b>", 3), "rc %d w %zu", rc, w);
    ptrdiff_t dcaps2[1][3][2] = { { { 0, 2 }, { 0, 1 }, { 1, 2 } } };
    RESET();
    rc = sdn_render(&cd, &md, (ptrdiff_t (*)[2])dcaps2, 1, 0, &o);
    w = bytes(&o, &cd, 0, out, 64);
    CHECK("el.dup.first.wins", rc == 0 && w == 3 && !memcmp(out, "<a>", 3), "rc %d w %zu", rc, w);
    ptrdiff_t dcaps3[1][3][2] = { { { 0, 0 }, { 0, 0 }, { 0, 1 } } };   /* set-to-empty participates */
    RESET();
    rc = sdn_render(&cd, &md, (ptrdiff_t (*)[2])dcaps3, 1, 0, &o);
    w = bytes(&o, &cd, 0, out, 64);
    CHECK("el.dup.empty.participates", rc == 0 && w == 2, "rc %d w %zu", rc, w);
    ptrdiff_t dcaps4[1][3][2] = { { { 0, 0 }, { -1, -1 }, { -1, -1 } } };   /* none participated: unset */
    RESET();
    rc = sdn_render(&cd, &md, (ptrdiff_t (*)[2])dcaps4, 1, PCREC_SUBST_STRICT, &o);
    CHECK("el.dup.none.strict", rc == PCREC_SUBST_UNSET, "rc %d", rc);

    /* PCREC_SUBST_NOGROUP is always unset and never an error, STRICT included (§3¶6) */
    static const int ng[] = { PCREC_SUBST_NOGROUP };
    pcrec_subst_map mng = { ng, 1, NULL, 0 };
    rx_ctx cn = mkctx(&ra_info, &s1_subst_info, &mng, s, 8, PCREC_SUBST_STRICT, vres);
    RESET();
    rc = s1_render(&cn, &mng, (ptrdiff_t (*)[2])caps, 1, PCREC_SUBST_GAPS | PCREC_SUBST_STRICT, &o);
    w = bytes(&o, &cn, 0, out, 64);
    CHECK("el.nogroup.strict", rc == 0 && w == 4 && !memcmp(out, "xx[]", 4), "rc %d w %zu", rc, w);
    /* a map the check never saw: a slot outside [0, ncap) met by the run walk is MISMATCH (§4¶11) */
    int slotv[1] = { 1 };
    pcrec_subst_map mv = { slotv, 1, NULL, 0 };
    rx_ctx cv = mkctx(&ra_info, &s1_subst_info, &mv, s, 8, 0, vres);
    slotv[0] = 9;
    RESET();
    rc = s1_render(&cv, &mv, (ptrdiff_t (*)[2])caps, 1, PCREC_SUBST_GAPS, &o);
    CHECK("el.map.slot.changed", rc == PCREC_SUBST_MISMATCH && o.n == 0, "rc %d", rc);
    pcrec_subst_map mshort = { slotv, 0, NULL, 0 };   /* arrays shorter than the reference list */
    RESET();
    rc = s1_render(&cv, &mshort, (ptrdiff_t (*)[2])caps, 1, PCREC_SUBST_GAPS, &o);
    CHECK("el.map.short", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    /* the map reorders and reuses slots (§3¶5): $1 reads slot 2 */
    int slot2[1] = { 2 };
    pcrec_subst_map m2 = { slot2, 1, NULL, 0 };
    rx_ctx c2 = mkctx(&ra_info, &s1_subst_info, &m2, s, 8, 0, vres);
    RESET();
    rc = s1_render(&c2, &m2, (ptrdiff_t (*)[2])caps, 1, PCREC_SUBST_GAPS, &o);
    w = bytes(&o, &c2, 0, out, 64);
    CHECK("el.map.reads.other.slot", rc == 0 && w == 5 && !memcmp(out, "xx[b]", 5), "rc %d w %zu", rc, w);
    /* ${!name} without a variable array on the context (§4¶11) */
    rx_ctx cvar = ctx; cvar.vars = NULL; cvar.nvars = 0;
    RESET();
    rc = sv_render(&cvar, NULL, (ptrdiff_t (*)[2])caps, 1, PCREC_SUBST_GAPS, &o);
    CHECK("el.vars.missing", rc == PCREC_SUBST_MISMATCH, "rc %d", rc);
    DONE();
}
