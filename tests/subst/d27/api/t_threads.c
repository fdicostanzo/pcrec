/* §3¶6, §7¶3: one binding, many threads, each with its own iterator and out. */
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ra.h"
#include "s1.h"

static rx_subst_binding B;
static char SUBJ[20000];
static unsigned char REF[40000];
static size_t REFLEN;

static void *worker(void *arg)
{
    long bad = 0;
    unsigned char *o = malloc(40000);
    for (int rep = 0; rep < 50; rep++) {
        rx_iter it = RX_ITER_INIT((const unsigned char *)SUBJ, sizeof SUBJ);
        size_t L, K;
        int rc = pcrec_subst(&B, &it, SIZE_MAX, o, 40000, &L, &K);
        if (rc || L != REFLEN || memcmp(o, REF, L)) bad++;
    }
    free(o);
    (void)arg;
    return (void *)bad;
}

int main(void)
{
    rx_subst_run runs[1];
    int bad;
    for (size_t i = 0; i < sizeof SUBJ; i++) SUBJ[i] = "abaxa"[i % 5];
    if (pcrec_subst_bind(&B, &ra_info, &s1_subst_info, runs, 1, NULL, 0, &bad)) { puts("FAIL bind"); return 1; }
    rx_iter it = RX_ITER_INIT((const unsigned char *)SUBJ, sizeof SUBJ);
    size_t K;
    if (pcrec_subst(&B, &it, SIZE_MAX, REF, sizeof REF, &REFLEN, &K)) { puts("FAIL ref"); return 1; }
    pthread_t t[8];
    for (int i = 0; i < 8; i++) pthread_create(&t[i], NULL, worker, NULL);
    long total = 0;
    for (int i = 0; i < 8; i++) { void *r; pthread_join(t[i], &r); total += (long)r; }
    printf("%s threads.shared.binding: %ld bad runs of 400\n", total ? "FAIL" : "PASS", total);
    return 0;
}
