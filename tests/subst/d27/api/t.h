/* substd27 API drivers: shared check macros.  Every CHECK is one case. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "ra.h"
#include "rb.h"
#include "rn.h"
#include "rd.h"
#include "rk.h"
#include "rs.h"
#include "rx1.h"
#include "ru.h"
#include "ru2.h"
#include "rnc.h"
#include "rv.h"
#include "rz.h"
#include "rg.h"
#include "rgg.h"
#include "rlb.h"
#include "rck.h"
#include "ral.h"
#include "s1.h"
#include "s2.h"
#include "sn.h"
#include "snm.h"
#include "sv.h"
#include "sve.h"
#include "se1.h"
#include "s0.h"
#include "sall.h"
#include "snul.h"
#include "snone.h"
#include "sdn.h"

static int npass, nfail;
#define CHECK(id, cond, ...) do { if (cond) { npass++; printf("PASS %s\n", id); } \
    else { nfail++; printf("FAIL %s: ", id); printf(__VA_ARGS__); printf("\n"); } fflush(stdout); } while (0)
#define DONE() do { printf("TOTAL pass=%d fail=%d\n", npass, nfail); return 0; } while (0)

static rx_subst_run RUNS[64];

static int bind(rx_subst_binding *b, const struct rx_info *rx, const struct rx_subst_info *s)
{
    int bad;
    return pcrec_subst_bind(b, rx, s, RUNS, 64, NULL, 0, &bad);
}

/* the glue over a fresh iterator of s[0,n) into a malloc of exactly cap bytes */
static int glue(const rx_subst_binding *b, const char *s, size_t n, size_t limit, size_t cap,
                char *res, size_t *len, size_t *k)
{
    unsigned char *subj = malloc(n ? n : 1), *out = malloc(cap ? cap : 1);
    memcpy(subj, s, n);
    rx_iter it = RX_ITER_INIT(subj, n);
    int rc = pcrec_subst(b, &it, limit, out, cap, len, k);
    if (res) { size_t m = rc == 0 ? *len : 0; memcpy(res, out, m); res[m] = 0; }
    free(subj); free(out);
    return rc;
}
