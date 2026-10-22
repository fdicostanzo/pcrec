/* §7¶5: one map and one record, many threads, each with its own iterator,
 * context, pieces and output.  substb2: was one binding (R3); now the shared
 * const objects are the record and a by-name map. */
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ra.h"
#include "s1.h"
#define PCREC_SUPPORT_IMPLEMENTATION
#include "support.h"

static rx_subst_map M;
static int SLOT[8];
static rx_subst_run RUN[1];
static char SUBJ[20000];
static unsigned char REF[40000];
static size_t REFLEN;

static int one(unsigned char *o, size_t cap, size_t *len)
{
    rx_iter it = RX_ITER_INIT((const unsigned char *)SUBJ, sizeof SUBJ);
    rx_var vres[1];
    rx_subst_piece pc[64 * S1_PIECES];
    rx_subst_out po = { .pc = pc, .cap = 64 * S1_PIECES };
    rx_ctx ctx;
    int bad, rc = rx_subst_ctx_init(&ctx, &it, &ra_info, &s1_subst_info, &M, vres, 0, &bad);
    if (rc < 0) return rc;
    return rx_subst_replace_all(ra_info.next_n, &it, &s1_subst_info, &ctx, &M, 0, &po, o, cap, len);
}

static void *worker(void *arg)
{
    long bad = 0;
    unsigned char *o = malloc(40000);
    for (int rep = 0; rep < 50; rep++) {
        size_t L;
        int rc = one(o, 40000, &L);
        if (rc < 0 || L != REFLEN || memcmp(o, REF, L)) bad++;
    }
    free(o);
    (void)arg;
    return (void *)bad;
}

int main(void)
{
    int bad;
    size_t na;
    for (size_t i = 0; i < sizeof SUBJ; i++) SUBJ[i] = "abaxa"[i % 5];
    if (pcrec_subst_map_names(&s1_subst_info, &ra_info, 0, SLOT, 8, RUN, 1, &M, &bad, &na)) { puts("FAIL map"); return 1; }
    if (one(REF, sizeof REF, &REFLEN) < 0) { puts("FAIL ref"); return 1; }
    pthread_t t[8];
    for (int i = 0; i < 8; i++) pthread_create(&t[i], NULL, worker, NULL);
    long total = 0;
    for (int i = 0; i < 8; i++) { void *r; pthread_join(t[i], &r); total += (long)r; }
    printf("%s threads.shared.map: %ld bad runs of 400\n", total ? "FAIL" : "PASS", total);
    return 0;
}
