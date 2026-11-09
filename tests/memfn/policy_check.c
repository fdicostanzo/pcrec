/* tests/memfn/policy_check.c -- [XARCH-DEV] unit U2 fix (request R-37): the
 * kit's define-time refusal of a policy bit outside its named set
 * (unconditional since review 2026-11-08 r5 X-5 deleted the staging switch).
 *
 * Built by tests/memfn/run_finder.sh against the library its other parts
 * link, and driven through the public header only: the one check that can
 * tell the refusal from its absence (S3000). Each case defines a FIND site,
 * differing from the control only in its policy word, on an art whose target
 * is stated:
 *
 *   control   the named bits (MF_P_INLOOP | MF_P_SIZE_LEANING; bit 0 is retired)
 *             define cleanly, so a refusal below is the policy word's alone;
 *   plant     an unnamed bit (1u << 7) is refused, and mf_art_error carries
 *             the unnamed bits in hex ("0x80"), not merely a refusal.
 *
 * Prints `checks passed: N` / `checks failed: M`; exit 1 on any failure. */
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "memfn.h"

static int passed, failed;

static void verdict(const char *name, const char *why)
{
    if (*why) { printf("FAIL: %s: %s\n", name, why); failed++; }
    else { printf("ok   %s\n", name); passed++; }
}

static void *a_alloc(void *u, size_t n)
{
    (void)u;
    void *p = calloc(1, n ? n : 1);
    if (!p) { perror("calloc"); exit(2); }
    return p;
}

/* A sink that discards: the text is not under test, only the define's verdict. */
static void k_puts(void *u, const char *s) { (void)u; (void)s; }
static void k_vprintf(void *u, const char *f, va_list ap) { (void)u; (void)f; (void)ap; }
static int  k_cmt_open(void *u, int tier) { (void)u; (void)tier; return 1; }
static void k_cmt_close(void *u) { (void)u; }
static void k_stamp(void *u, const char *n, const char *v) { (void)u; (void)n; (void)v; }
static void k_cstr(void *u, const uint8_t *b, size_t n) { (void)u; (void)b; (void)n; }
static void k_legend(void *u, uint8_t b) { (void)u; (void)b; }

static const char *h_fn_name(void *u, uint32_t ref) { (void)u; (void)ref; return "rx_f"; }

/* Define one FIND site with policy word `policy`; the art's error text is
 * copied to err (empty when the define succeeded). Returns mf_define's rc. */
static int define_with(uint32_t policy, char *err, size_t n)
{
    mf_arena a = { NULL, a_alloc };
    mf_art *art = mf_art_begin(&a, "rx", 0, NULL, NULL);
    mf_site s;
    memset(&s, 0, sizeof s);
    s.abi = MF_SITE_ABI;
    s.form = MF_FORM_FUNC;
    s.op = MF_OP_FIND;
    s.handoff = MF_H_RETURN;
    s.use = MF_USE_POSITION;
    s.ret_pred = MF_NO_PRED;
    s.span_hi = MF_SPAN_UNBOUNDED;
    s.cand_ppm_hi = MF_PPM_FULL;
    s.empty = MF_EMPTY_MISS;
    s.policy = policy;
    s.body = MF_BODY_ONESHOT;
    s.pred.need = MF_REQUIRED;
    s.pred.fn_ref = 1;
    s.pred.nterm = 1;               /* one required byte: a site the kit defines */
    s.pred.plan_hint = 1;
    s.pred.span_class = MF_SPAN_BOUNDED;
    s.pred.term[0].kind = MF_T_SET;
    s.pred.term[0].set['q' >> 3] = (uint8_t)(1u << ('q' & 7));
    s.pred.term[0].ppm_hi = MF_PPM_FULL;
    s.pred.term[0].need = MF_REQUIRED;
    err[0] = 0;
    if (!art || mf_art_target(art, mf_portable_target())) {
        snprintf(err, n, "setup: %s", art ? mf_art_error(art) : "mf_art_begin failed");
        return -2;
    }
    mf_hooks hd = { .fn_name = h_fn_name };
    mf_sink sk = { .puts = k_puts, .vprintf = k_vprintf, .cmt_open = k_cmt_open,
                   .cmt_close = k_cmt_close, .stamp = k_stamp, .cstr = k_cstr,
                   .legend_byte = k_legend };
    uint32_t handle = 0;
    int rc = mf_define(art, &s, &hd, &sk, &handle);
    snprintf(err, n, "%s", rc ? mf_art_error(art) : "");
    return rc;
}

int main(void)
{
    char err[512];
    int rc;

    rc = define_with(MF_P_INLOOP | MF_P_SIZE_LEANING, err, sizeof err);
    verdict("P1 the named policy bits are defined (the site itself is sound)",
            rc == 0 ? "" : err);

    rc = define_with(MF_P_INLOOP | (1u << 7), err, sizeof err);
    verdict("P2 an unnamed policy bit (1u<<7) is refused at define",
            rc == -1 ? "" : "mf_define did not refuse it");
    verdict("P3 the refusal carries the unnamed bits in hex",
            strstr(err, "policy bits 0x80 ") ? "" : "no \"policy bits 0x80\" in the error");

    rc = define_with(1u << 8, err, sizeof err);
    verdict("P4 bit 8 alone is refused too, hex 0x100",
            rc == -1 && strstr(err, "policy bits 0x100 ") ? "" : "not refused with hex 0x100");

    printf("checks passed: %d\n", passed);
    printf("checks failed: %d\n", failed);
    return failed ? 1 : 0;
}
