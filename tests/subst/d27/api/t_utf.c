/* the glue over -futf-check and -fstartpos-guard=align artifacts: refusals carry 0 and 0 */
#include "t.h"

int main(void)
{
    rx_subst_binding b, ba;
    bind(&b, &rck_info, &s2_subst_info);
    bind(&ba, &ral_info, &s2_subst_info);
    char out[64];
    size_t L, K;
    int rc = glue(&b, "a\xff" "b", 3, SIZE_MAX, 64, out, &L, &K);
    CHECK("utfcheck.refused", rc == PCREC_ERR_UTF && L == 0 && K == 0, "rc %d L %zu K %zu", rc, L, K);
    rc = glue(&b, "a\xc3\xa9", 3, SIZE_MAX, 64, out, &L, &K);
    CHECK("utfcheck.valid", rc == 0 && !strcmp(out, "<a><\xc3\xa9>"), "rc %d out %s", rc, out);
    rc = glue(&b, "a\xff" "b", 3, 0, 64, out, &L, &K);
    printf("INFO utfcheck.limit0 rc=%d L=%zu (limit 0 runs no search, so no check)\n", rc, L);
    rc = glue(&b, "a\xff" "b", 3, 1, 64, out, &L, &K);
    CHECK("utfcheck.limit1", rc == PCREC_ERR_UTF && L == 0 && K == 0, "rc %d L %zu", rc, L);
    rc = glue(&b, "abc\xc3", 4, SIZE_MAX, 64, out, &L, &K);
    CHECK("utfcheck.truncated.tail", rc == PCREC_ERR_UTF && L == 0, "rc %d", rc);
    rc = glue(&b, "abc\xc3", 4, 1, 64, out, &L, &K);
    CHECK("utfcheck.truncated.tail.limit1", rc == PCREC_ERR_UTF, "rc %d (the check covers [start-LB, n) at the first call)", rc);
    /* align: a mid-character start moves forward; the gap before the first match is the subject from 0 */
    rx_iter it = RX_ITER_INIT((const unsigned char *)"\xc3\xa9x", 3);
    rx_iter_at(&it, 1);
    unsigned char o[64];
    rc = pcrec_subst(&ba, &it, SIZE_MAX, o, 64, &L, &K);
    CHECK("align.midchar", rc == 0 && L == 5 && !memcmp(o, "\xc3\xa9<x>", 5) && K == 1, "rc %d L %zu", rc, L);
    DONE();
}
