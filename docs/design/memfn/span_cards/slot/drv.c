/* span_cards/slot/drv.c — THE SLOT DRIVER (span_cards.md §3.2-§3.4 step 1). Linked per launch with gen.c,
 * the launch's tab.c and its arm and pad objects (link.py).
 *   drv gate              THE ANSWER GATE, no clock: every arm, length and pool subject; the count, the
 *                         position sum and FNV-1a-64 against gen.c's; one line per arm, exit 3 on any miss
 *   drv addr              each arm's timed function address (the placement, also read by nm)
 *   drv round R NFILE     one ROUND of the launch: every (arm, length) point in the order rotated by R,
 *                         each timing N calls over its 16 MiB pool (N doubled until a loop takes >= 50 ms,
 *                         D144 add. 1, at the launch's first round and kept in NFILE for its later rounds);
 *                         prints `pt ARM LEN N T_NS PERCALL_E6 ACC` per point
 * One call is one find-all (find), one pass over the candidate array (cmp, null) or one artifact find-all
 * (art) over one pool subject; the pool cycles. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "slot.h"

typedef struct { unsigned char **s; uint32_t **c; size_t nc; uint32_t np, len; } pool;

static void pool_make(const arm *a, uint32_t len, pool *p, int gate, int *bad)
{
    p->len = len;
    p->np = a->kind == K_ART ? 1 : POOL_BYTES / len;
    p->s = calloc(p->np, sizeof *p->s);
    p->c = calloc(p->np, sizeof *p->c);
    if (!p->s || !p->c) exit(2);
    for (uint32_t i = 0; i < p->np; i++) {
        p->s[i] = malloc(len + 64);
        p->c[i] = malloc(sizeof(uint32_t) * (len / CAND_STRIDE + 1));
        if (!p->s[i] || !p->c[i]) exit(2);
        memset(p->s[i] + len, 0, 64);
        uint64_t ec, es, eh;
        gen_subject(a, len, i, p->s[i], p->c[i], &p->nc, &ec, &es, &eh);
        if (gate) {
            uint64_t sum = 0, h = FNV0;
            uint64_t cnt = a->gate(p->s[i], len, p->c[i], p->nc, &sum, &h);
            if (cnt != ec || sum != es || h != eh) {
                if (*bad < 5)
                    printf("GATE MISS %s len %u subject %u: found %llu sum %llu fnv %016llx, planted %llu sum %llu fnv %016llx\n",
                           a->name, len, i, (unsigned long long)cnt, (unsigned long long)sum, (unsigned long long)h,
                           (unsigned long long)ec, (unsigned long long)es, (unsigned long long)eh);
                (*bad)++;
            }
        }
    }
}

static void pool_free(pool *p)
{
    for (uint32_t i = 0; i < p->np; i++) { free(p->s[i]); free(p->c[i]); }
    free(p->s);
    free(p->c);
}

static uint64_t now_ns(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (uint64_t)t.tv_sec * 1000000000ull + (uint64_t)t.tv_nsec;
}

static uint64_t run_n(const arm *a, const pool *p, uint64_t n, uint64_t *acc)
{
    uint64_t t0 = now_ns();
    for (uint64_t k = 0; k < n; k++) {
        uint32_t i = (uint32_t)(k % p->np);
        *acc += a->time(p->s[i], p->len, p->c[i], p->nc);
    }
    return now_ns() - t0;
}

int main(int argc, char **argv)
{
    if (argc >= 2 && !strcmp(argv[1], "addr")) {
        for (int i = 0; i < slot_narms; i++) printf("%s\t%p\n", slot_arms[i].name, (void *)slot_arms[i].time);
        return 0;
    }
    if (argc >= 2 && !strcmp(argv[1], "gate")) {
        int bad = 0, total = 0;
        for (int i = 0; i < slot_narms; i++) {
            const arm *a = &slot_arms[i];
            int b0 = bad;
            for (int k = 0; k < a->nlen; k++) {
                pool p;
                pool_make(a, a->len[k], &p, 1, &bad);
                pool_free(&p);
                total++;
            }
            printf("gate\t%s\t%s\n", a->name, bad == b0 ? "ok" : "MISS");
        }
        printf("== s2 GATE %s: %d arms, %d (arm, length) pools, %d misses\n", bad ? "FAILED" : "ok", slot_narms,
               total, bad);
        return bad ? 3 : 0;
    }
    if (argc == 4 && !strcmp(argv[1], "round")) {
        int r = atoi(argv[2]);
        int np = 0;
        for (int i = 0; i < slot_narms; i++) np += slot_arms[i].nlen;
        uint64_t *nn = calloc((size_t)np, sizeof *nn);
        FILE *f = fopen(argv[3], "r");
        int have = 0;
        if (f) { for (int i = 0; i < np && fscanf(f, "%llu", (unsigned long long *)&nn[i]) == 1; i++) have++; fclose(f); }
        int calibrate = have != np;
        uint64_t acc = 0;
        for (int q = 0; q < np; q++) {
            int pt = (q + r - 1) % np, ai = 0, k = pt;
            while (k >= slot_arms[ai].nlen) { k -= slot_arms[ai].nlen; ai++; }
            const arm *a = &slot_arms[ai];
            pool p;
            int bad = 0;
            pool_make(a, a->len[k], &p, 0, &bad);
            if (calibrate) {
                uint64_t n = 1;
                while (run_n(a, &p, n, &acc) < 50000000ull) n *= 2;
                nn[pt] = n;
            }
            uint64_t t = run_n(a, &p, nn[pt], &acc);
            unsigned long long pc = (t * 1000000ull + nn[pt] / 2) / nn[pt];
            printf("pt\t%s\t%u\t%llu\t%llu\t%llu\t%llu\n", a->name, a->len[k], (unsigned long long)nn[pt],
                   (unsigned long long)t, pc, (unsigned long long)acc);
            pool_free(&p);
        }
        if (calibrate) {
            f = fopen(argv[3], "w");
            if (!f) return 2;
            for (int i = 0; i < np; i++) fprintf(f, "%llu\n", (unsigned long long)nn[i]);
            fclose(f);
        }
        return 0;
    }
    fprintf(stderr, "usage: drv gate | addr | round R NFILE\n");
    return 2;
}
