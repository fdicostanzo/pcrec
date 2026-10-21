/* docs/design/findall_iter/twin/drv.c — [FINDALL-NEXT] HAND TWIN answer driver, REVISION 3
 * (lane parity, 2026-10-21; revision 1 was lane iterdes's).
 *
 * Answers only (NO timing). Built against one twin artifact (mktwin.py) with
 * -DPFX=<prefix> -DPFXU=<PREFIX> -DHDR="<prefix>.h", plus -DTWIN_FILL for a twin
 * made with --fill. Reads subjects, one per stdin line, in the .rxt subject-escape
 * vocabulary (\t \n \r \\ \xNN), and prints for each, TAB-separated KEY=VALUE:
 *
 *   L=<spans>   match_api.md §3.1.3's loop over <p>_search + <p>_next_pos
 *   I=<spans>   the iterator, <p>_next with a caps buffer, no batch region (K = 1)
 *   rc=<rc>     its final rc; " STICKY-FAIL" if a call after the end matched, and
 *               " ENDSET-FAIL" if a setter on the ENDED iterator changed anything
 *   Z=<count>   <p>_next with caps == NULL (the count)
 *   X=ok|bad    the state machine (§1.1, §1.2): a setter on a BOUND iterator poisons
 *               it and the next call refuses with PCREC_ERR_ITER; a zeroed header
 *               refuses too; a setter on a FRESH one before the first call is legal
 *   A=<spans>   the iterator started by rx_iter_at(&it, 1)        (I1's start setter)
 *   La=<spans>  the §3.1.3 loop started at p = 1                  (A's comparator)
 *   off cell:  N=<spans>   <p>_next_n with k = 3 (crossing its own batch boundaries)
 *   fill cell: B=<spans>   <p>_next with a 64-entry batch region (rx_iter_batch), and
 *              BK=ok|bad   the same sequence, final rc included, at K = 2, K = 3 and a
 *                          one-entry region (K = 1 by the rule), all against I
 *
 * A give-up or refusal ending a span list prints " GU<code>". The runner (run_twin.sh)
 * compares I against L (plain twins) or against libpcre2's global loop (retry twins),
 * I against N or B always, and A against La on plain twins.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CAT2(a, b) a##b
#define CAT(a, b) CAT2(a, b)
#define F(x) CAT(PFX, x)
#include HDR
#include "iter_abi.h"

int F(_next)(rx_iter *it, ptrdiff_t (*caps)[2]);
#ifndef TWIN_FILL
size_t F(_next_n)(rx_iter *it, ptrdiff_t (*out)[2], size_t k);
#endif

static size_t unesc(const char *in, size_t len, unsigned char *out)
{
    size_t o = 0;
    for (size_t i = 0; i < len; i++) {
        if (in[i] == '\\' && i + 1 < len) {
            char c = in[i + 1];
            if (c == 't') { out[o++] = '\t'; i++; continue; }
            if (c == 'n') { out[o++] = '\n'; i++; continue; }
            if (c == 'r') { out[o++] = '\r'; i++; continue; }
            if (c == '\\') { out[o++] = '\\'; i++; continue; }
            if (c == 'x' && i + 3 < len) {
                char h[3] = { in[i + 2], in[i + 3], 0 };
                out[o++] = (unsigned char)strtoul(h, NULL, 16);
                i += 3;
                continue;
            }
        }
        out[o++] = (unsigned char)in[i];
    }
    return o;
}

#define NCAPS CAT(PFXU, _NCAPS)
#define SPANS_MAX 4096

/* one span list as text, into buf; returns its length */
static size_t put_span(char *buf, size_t at, size_t k, ptrdiff_t a, ptrdiff_t b)
{
    return at + (size_t)sprintf(buf + at, "%s(%td,%td)", k ? " " : "", a, b);
}

static void loop_from(const unsigned char *s, size_t n, size_t p, char *buf)
{
    ptrdiff_t caps[NCAPS][2];
    size_t at = 0, k = 0;
    buf[0] = 0;
    while (p <= n && k < SPANS_MAX) {
        int r = F(_search)(s, n, p, caps);
        if (r != 1) { if (r < 0) at += (size_t)sprintf(buf + at, " GU%d", r); break; }
        at = put_span(buf, at, k++, caps[0][0], caps[0][1]);
        p = (caps[0][1] > caps[0][0]) ? F(_next_pos)(s, n, (size_t)caps[0][1] - 1)
                                     : F(_next_pos)(s, n, (size_t)caps[0][0]);
    }
}

/* drain an iterator into buf, final code appended as for the loop */
static int iter_drain(rx_iter *it, char *buf)
{
    ptrdiff_t caps[NCAPS][2];
    size_t at = 0, k = 0;
    buf[0] = 0;
    while (k < SPANS_MAX && F(_next)(it, caps))
        at = put_span(buf, at, k++, caps[0][0], caps[0][1]);
    if (it->rc < 0) sprintf(buf + at, " GU%d", it->rc);
    return it->rc;
}

int main(void)
{
    static char line[1 << 20];
    static unsigned char s[1 << 19];
    static char bL[1 << 16], bI[1 << 16], bA[1 << 16], bLa[1 << 16], bX[1 << 16];
    static ptrdiff_t caps[NCAPS][2];
    while (fgets(line, sizeof line, stdin)) {
        size_t len = strlen(line);
        if (len && line[len - 1] == '\n') line[--len] = 0;
        size_t n = unesc(line, len, s);
        int k;

        loop_from(s, n, 0, bL);
        printf("L=%s", bL);

        rx_iter it = RX_ITER_INIT(s, n);
        int rc = iter_drain(&it, bI);
        printf("\tI=%s\trc=%d", bI, rc);
        if (F(_next)(&it, caps)) printf(" STICKY-FAIL");        /* a call after the end stays at the end */
        rx_iter_at(&it, 0);                                      /* a setter on ENDED is a no-op (IT8) */
        if (it.hdr != PCREC_ITER_ENDED || it.rc != rc || F(_next)(&it, caps)) printf(" ENDSET-FAIL");

        rx_iter iz = RX_ITER_INIT(s, n);
        for (k = 0; F(_next)(&iz, NULL); k++) ;
        printf("\tZ=%d", k);

        /* the state machine */
        int xok = 1;
        {
            rx_iter ix = RX_ITER_INIT(s, n);
            rx_iter_at(&ix, 0);                                  /* legal on FRESH: same answers */
            iter_drain(&ix, bX);
            if (strcmp(bX, bI) != 0) xok = 0;
            rx_iter ip = RX_ITER_INIT(s, n);
            if (F(_next)(&ip, caps) && ip.hdr == PCREC_ITER_BOUND) {
                rx_iter_at(&ip, 0);                              /* on BOUND: poison */
                if (F(_next)(&ip, caps) || ip.rc != PCREC_ERR_ITER || ip.hdr != PCREC_ITER_ENDED) xok = 0;
            }
            rx_iter ig; memset(&ig, 0, sizeof ig);              /* a zeroed (never-initialized) header */
            if (F(_next)(&ig, caps) || ig.rc != PCREC_ERR_ITER) xok = 0;
        }
        printf("\tX=%s", xok ? "ok" : "bad");

        rx_iter ia = RX_ITER_INIT(s, n);
        rx_iter_at(&ia, 1);
        iter_drain(&ia, bA);
        loop_from(s, n, 1, bLa);
        printf("\tA=%s\tLa=%s", bA, bLa);

#ifndef TWIN_FILL
        static ptrdiff_t out[3][2];
        rx_iter in = RX_ITER_INIT(s, n);
        printf("\tN=");
        size_t got, tot = 0;
        while ((got = F(_next_n)(&in, out, 3)) > 0) {
            for (size_t i = 0; i < got; i++, tot++)
                printf("%s(%td,%td)", tot ? " " : "", out[i][0], out[i][1]);
            if (got < 3) break;
        }
        if (in.rc < 0) printf(" GU%d", in.rc);
#else
        /* every region is heap-allocated at its exact size, so an over-fill past K entries
           is an ASan error under TWIN_ASAN=1 (a static array would absorb it silently) */
        static char bB[1 << 16];
        ptrdiff_t (*bb)[2] = malloc(sizeof(*bb) * 64 * NCAPS);
        rx_iter ib = RX_ITER_INIT(s, n);
        rx_iter_batch(&ib, bb, 64 * NCAPS);
        int brc = iter_drain(&ib, bB);
        free(bb);
        printf("\tB=%s", bB);
        int bk = (brc == rc);
        static const size_t ks[3] = { 2, 3, 1 };
        for (int j = 0; j < 3; j++) {
            ptrdiff_t (*bk_region)[2] = malloc(sizeof(*bk_region) * ks[j] * NCAPS);
            rx_iter ik = RX_ITER_INIT(s, n);
            rx_iter_batch(&ik, bk_region, ks[j] * NCAPS);
            int krc = iter_drain(&ik, bX);
            free(bk_region);
            if (krc != rc || strcmp(bX, bI) != 0) bk = 0;
        }
        printf("\tBK=%s", bk ? "ok" : "bad");
#endif
        printf("\n");
    }
    return 0;
}
