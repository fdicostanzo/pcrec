/* replace-all over -futf-check and -fstartpos-guard=align artifacts: refusals
 * leave *len untouched (§10¶9).  substb2: was the glue. */
#include "t.h"

#define UNTOUCHED ((size_t)0x5a5a5a5a)

int main(void)
{
    unsigned char out[64];
    size_t L = UNTOUCHED, K;
    int rc = sub_all(&rck_info, &s2_subst_info, NULL, 0, (const unsigned char *)"a\xff" "b", 3, out, 64, &L);
    CHECK("utfcheck.refused", rc == PCREC_ERR_UTF && L == UNTOUCHED, "rc %d L %zu", rc, L);
    rc = sub_all(&rck_info, &s2_subst_info, NULL, 0, (const unsigned char *)"a\xc3\xa9", 3, out, 64, &L);
    CHECK("utfcheck.valid", rc == 2 && L == 7 && !memcmp(out, "<a><\xc3\xa9>", 7), "rc %d L %zu", rc, L);
    /* the recipe with limit 0 runs no search, so no check; limit 1 reaches it */
    char res[64];
    rc = rlim(&rck_info, &s2_subst_info, NULL, 0, "a\xff" "b", 3, 0, 64, res, &L, &K);
    printf("INFO utfcheck.limit0 rc=%d L=%zu (limit 0 runs no search, so no check)\n", rc, L);
    rc = rlim(&rck_info, &s2_subst_info, NULL, 0, "a\xff" "b", 3, 1, 64, res, &L, &K);
    CHECK("utfcheck.limit1", rc == PCREC_ERR_UTF, "rc %d", rc);
    L = UNTOUCHED;
    rc = sub_all(&rck_info, &s2_subst_info, NULL, 0, (const unsigned char *)"abc\xc3", 4, out, 64, &L);
    CHECK("utfcheck.truncated.tail", rc == PCREC_ERR_UTF && L == UNTOUCHED, "rc %d", rc);
    rc = rlim(&rck_info, &s2_subst_info, NULL, 0, "abc\xc3", 4, 1, 64, res, &L, &K);
    CHECK("utfcheck.truncated.tail.limit1", rc == PCREC_ERR_UTF, "rc %d (the check covers [start-LB, n) at the first call)", rc);
    /* align: a mid-character start moves forward; the gap before the first match is the subject from 0 */
    rx_iter it = RX_ITER_INIT((const unsigned char *)"\xc3\xa9x", 3);
    rx_iter_at(&it, 1);
    rc = sub_all_it(&ral_info, &s2_subst_info, NULL, 0, &it, out, 64, &L);
    CHECK("align.midchar", rc == 1 && L == 5 && !memcmp(out, "\xc3\xa9<x>", 5), "rc %d L %zu", rc, L);
    DONE();
}
