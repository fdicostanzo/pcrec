/* subst lane phase A probe: the independent-element glue loop over today's
 * find-all iterator, oracle'd against libpcre2 10.46 pcre2_substitute
 * (GLOBAL | UNSET_EMPTY | OVERFLOW_LENGTH).  The *_render functions are
 * hand-written stand-ins for what a phase-B template compiler would emit;
 * the glue and the bind are the generic (prefix-independent) half.
 * Build and run: run.sh PCREC OUTDIR (beside this file). */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <string.h>
#include "ast.h"
#include "alt.h"
#include "ab.h"
#include "ymd.h"
#include "mdy.h"
#include "ea.h"
#include "xy.h"
#include "kr.h"
#include "lb.h"

/* ---- the subst element's shared half (would live in a subst header) ---- */
typedef struct rx_subst_ref { const char *name; int number; } rx_subst_ref;
typedef ptrdiff_t rx_substfn(const int *slot, const rx_ctx *ctx,
                             unsigned char *out, size_t cap);
struct rx_subst_info {
    const char *template_text;
    int nrefs;
    const rx_subst_ref *refs;
    rx_substfn *render;
};
#define PCREC_SUBST_NOSPACE (-1)   /* probe only: the code value is a phase-B question */

/* Bind once: resolve every reference against the rx's shape.  0 = bound,
 * -1 = the rx does not deliver a referenced group (the AOT promise: this is
 * the ONLY place an unknown reference can surface, before any substitution). */
static int rx_subst_bind(const struct rx_info *rx, const struct rx_subst_info *sub, int *slot)
{
    for (int i = 0; i < sub->nrefs; i++) {
        const rx_subst_ref *r = &sub->refs[i];
        slot[i] = -1;
        if (!r->name) {
            if (r->number <= rx->ngroups && r->number < rx->ncaps) slot[i] = r->number;
            if (r->number == 0) slot[i] = 0;
        } else {
            for (int g = 0; g < rx->nnames; g++)       /* bsearch in phase B; dup runs too */
                if (strcmp(rx->groups[g].name, r->name) == 0) { slot[i] = rx->groups[g].slot; break; }
        }
        if (slot[i] < 0) return -1;
    }
    return 0;
}

/* The glue: gaps copied by the glue, replacement rendered by the element,
 * one pass, required capacity always reported (D38 Q4/Q11 semantics). */
static ptrdiff_t rx_subst_all(const struct rx_info *rx, rx_iter *it,
                              const struct rx_subst_info *sub, const int *slot,
                              unsigned char *out, size_t cap, size_t *outlen)
{
    const unsigned char *s = it->s;
    size_t n = it->n, w = 0, prev = 0;
    ptrdiff_t count = 0;
    int fits = out != NULL;
    rx_ctx ctx = { s, n, 0, (size_t)rx->ncaps, NULL, NULL, NULL, 0 };
    RX_FOREACH(rx, it, m) {
        size_t st = (size_t)m[0][0], gap = st - prev;
        if (fits && w + gap > cap) fits = 0;
        if (fits) memcpy(out + w, s + prev, gap);
        w += gap;
        ctx.pos = st; ctx.caps = (const ptrdiff_t (*)[2])m;
        ptrdiff_t r = sub->render(slot, &ctx, fits ? out + w : NULL, fits ? cap - w : 0);
        if (r < 0) return r;                 /* a renderer failed: phase-B code */
        if (fits && w + (size_t)r > cap) fits = 0;
        w += (size_t)r;
        prev = (size_t)m[0][1];
        count++;
    }
    if (it->rc < 0) return it->rc;           /* the iterator's give-up / refusal */
    if (fits && w + (n - prev) > cap) fits = 0;
    if (fits) memcpy(out + w, s + prev, n - prev);
    w += n - prev;
    *outlen = w;
    return (out && !fits) ? PCREC_SUBST_NOSPACE : count;
}

/* ---- "emitted" renders: one per template, straight-line ---- */
#define SPAN(k) (ctx->caps[slot[k]][0] < 0 ? 0 : (size_t)(ctx->caps[slot[k]][1] - ctx->caps[slot[k]][0]))
#define COPY(k) do { size_t l_ = SPAN(k); if (l_) memcpy(o, ctx->subject + ctx->caps[slot[k]][0], l_); o += l_; } while (0)
#define LIT(str) do { memcpy(o, str, sizeof str - 1); o += sizeof str - 1; } while (0)

/* "[$0]" */
static const rx_subst_ref br0_refs[] = { { NULL, 0 } };
static ptrdiff_t br0_render(const int *slot, const rx_ctx *ctx, unsigned char *out, size_t cap)
{
    size_t need = 2 + SPAN(0);
    if (out && need <= cap) { unsigned char *o = out; LIT("["); COPY(0); LIT("]"); }
    return (ptrdiff_t)need;
}
static const struct rx_subst_info br0 = { "[$0]", 1, br0_refs, br0_render };

/* "[$1|$2]" */
static const rx_subst_ref two_refs[] = { { NULL, 1 }, { NULL, 2 } };
static ptrdiff_t two_render(const int *slot, const rx_ctx *ctx, unsigned char *out, size_t cap)
{
    size_t need = 3 + SPAN(0) + SPAN(1);
    if (out && need <= cap) { unsigned char *o = out; LIT("["); COPY(0); LIT("|"); COPY(1); LIT("]"); }
    return (ptrdiff_t)need;
}
static const struct rx_subst_info two = { "[$1|$2]", 2, two_refs, two_render };

/* "<$1>" */
static const rx_subst_ref one_refs[] = { { NULL, 1 } };
static ptrdiff_t one_render(const int *slot, const rx_ctx *ctx, unsigned char *out, size_t cap)
{
    size_t need = 2 + SPAN(0);
    if (out && need <= cap) { unsigned char *o = out; LIT("<"); COPY(0); LIT(">"); }
    return (ptrdiff_t)need;
}
static const struct rx_subst_info one = { "<$1>", 1, one_refs, one_render };

/* "${y}.${m}" — names, resolved per rx at bind (the M:N case) */
static const rx_subst_ref ym_refs[] = { { "y", 0 }, { "m", 0 } };
static ptrdiff_t ym_render(const int *slot, const rx_ctx *ctx, unsigned char *out, size_t cap)
{
    size_t need = 1 + SPAN(0) + SPAN(1);
    if (out && need <= cap) { unsigned char *o = out; COPY(0); LIT("."); COPY(1); }
    return (ptrdiff_t)need;
}
static const struct rx_subst_info ym = { "${y}.${m}", 2, ym_refs, ym_render };

/* ---- oracle ---- */
static int oracle(const char *pat, const char *subj, const char *tmpl, char *buf, size_t *len)
{
    int ec; PCRE2_SIZE eo;
    pcre2_code *c = pcre2_compile((PCRE2_SPTR)pat, PCRE2_ZERO_TERMINATED, 0, &ec, &eo, NULL);
    if (!c) return -999;
    pcre2_match_data *md = pcre2_match_data_create_from_pattern(c, NULL);
    PCRE2_SIZE ol = *len;
    int rc = pcre2_substitute(c, (PCRE2_SPTR)subj, strlen(subj), 0,
                              PCRE2_SUBSTITUTE_GLOBAL | PCRE2_SUBSTITUTE_UNSET_EMPTY |
                              PCRE2_SUBSTITUTE_OVERFLOW_LENGTH,
                              md, NULL, (PCRE2_SPTR)tmpl, PCRE2_ZERO_TERMINATED,
                              (PCRE2_UCHAR *)buf, &ol);
    *len = ol;
    pcre2_match_data_free(md); pcre2_code_free(c);
    return rc;
}

static int fails;
static void cell(const char *label, const struct rx_info *rx, const char *pat,
                 const struct rx_subst_info *sub, const char *subj)
{
    int slot[8];
    char ob[512]; size_t ol = sizeof ob;
    int orc = oracle(pat, subj, sub->template_text, ob, &ol);
    if (rx_subst_bind(rx, sub, slot) != 0) {
        printf("%-6s %-18s %-10s BIND-REFUSED (oracle rc=%d)\n", label, pat, sub->template_text, orc);
        return;
    }
    unsigned char pb[512]; size_t pl = 0;
    rx_iter it = RX_ITER_INIT((const unsigned char *)subj, strlen(subj));
    /* sizing pass first on a COPY of the fresh iterator, then the real pass */
    rx_iter it2 = it; size_t need = 0;
    ptrdiff_t sz = rx_subst_all(rx, &it2, sub, slot, NULL, 0, &need);
    ptrdiff_t prc = rx_subst_all(rx, &it, sub, slot, pb, sizeof pb, &pl);
    int ok = prc == orc && pl == ol && memcmp(pb, ob, pl) == 0 && need == pl && sz == prc;
    if (!ok) fails++;
    printf("%-6s %-18s %-10s %-10s pcrec=%td:\"%.*s\" pcre2=%d:\"%.*s\" size=%zu %s\n",
           label, pat, sub->template_text, subj, prc, (int)pl, pb, orc, (int)ol, ob, need,
           ok ? "OK" : "DIFF");
}

int main(void)
{
    /* subst_template_design.md §6.1's measured cells, now through the iterator */
    cell("6.1a", &ast_info, "a*", &br0, "bab");
    cell("6.1b", &ast_info, "a*", &br0, "aab");
    /* the §3.1.3¶9 lossy class: the retry is the iterator's, not the glue's */
    cell("retry", &ea_info, "|a", &br0, "aaa");
    cell("retry", &xy_info, "x*|y", &br0, "xyy");
    cell("K", &kr_info, "ab\\K", &br0, "ababab");
    /* unset-but-existing groups (D38 Q3 default empty) */
    cell("unset", &alt_info, "(a)|(b)", &two, "xaby");
    cell("grp", &ab_info, "(a+)b", &one, "xaabzaab");
    /* a group BEFORE the reported start (lookbehind capture) */
    cell("lbcap", &lb_info, "(?<=(a))b", &one, "abab");
    /* 1:N — one rx, two substs */
    cell("1:N", &alt_info, "(a)|(b)", &br0, "xaby");
    /* M:N — one NAMED subst over two rx with different group orders */
    cell("M:N", &ymd_info, "(?<y>\\d+)-(?<m>\\d+)", &ym, "on 2026-10 and 2027-11.");
    cell("M:N", &mdy_info, "(?<m>\\d+)/(?<y>\\d+)", &ym, "on 10/2026 and 11/2027.");
    /* shape refusal: $1|$2 against a no-group rx */
    cell("shape", &ast_info, "a*", &two, "aa");
    /* undersized buffer: NOSPACE with the required capacity reported */
    {
        int slot[1]; unsigned char small[5]; size_t l = 0;
        rx_subst_bind(&ast_info, &br0, slot);
        rx_iter it = RX_ITER_INIT((const unsigned char *)"bab", 3);
        ptrdiff_t r = rx_subst_all(&ast_info, &it, &br0, slot, small, sizeof small, &l);
        printf("nospace cap=5 rc=%td required=%zu %s\n", r, l, (r == PCREC_SUBST_NOSPACE && l == 11) ? "OK" : "DIFF");
        if (!(r == PCREC_SUBST_NOSPACE && l == 11)) fails++;
    }
    printf("fails=%d\n", fails);
    return fails != 0;
}
