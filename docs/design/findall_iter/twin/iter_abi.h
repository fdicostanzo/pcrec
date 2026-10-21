/* docs/design/findall_iter/twin/iter_abi.h — [FINDALL-NEXT] HAND TWIN, REVISION 3
 * (lane parity, 2026-10-21; revision 1 was lane iterdes's).
 *
 * The shared-ABI-block addition findall_iter.md §1.1 proposes AT I1, transcribed from
 * the design's own text: the header word (tag | layout 3 | state | option bits), no
 * `owner` (D165 add. 3), no `st` (S lands at I2, IC2), the setters on a FRESH iterator
 * (rx_iter_at / rx_iter_vars / rx_iter_batch), binding at init (D165 add. 2 Q3).
 * The twin includes it after the artifact's own .h (which supplies rx_var). In the real
 * build these lines sit INSIDE the artifact's PCREC_RX_ABI_H block. NOT emitted by
 * pcrec; a design probe.
 */
#ifndef FINDALL_ITER_TWIN_ABI_H
#define FINDALL_ITER_TWIN_ABI_H
#include <stddef.h>
#include <stdint.h>

#ifndef PCREC_ERR_ITER
#define PCREC_ERR_ITER (-10)  /* [FINDALL-NEXT] below PCREC_ERR_FLOOR: NOT a give-up -- the iterator was refused */
#endif

#define PCREC_ITER_LAYOUT      3u   /* bumps with any change to rx_iter's layout */
#define PCREC_ITER_TAG       (0x49540000u | (PCREC_ITER_LAYOUT << 8))
#define PCREC_ITER_FRESH     (PCREC_ITER_TAG | 0x01u)
#define PCREC_ITER_BOUND     (PCREC_ITER_TAG | 0x02u)
#define PCREC_ITER_ENDED     (PCREC_ITER_TAG | 0x03u)
#define PCREC_ITER_OPT_AT    0x10u  /* option bits, set by the setters on a FRESH iterator */
#define PCREC_ITER_OPT_VARS  0x20u
#define PCREC_ITER_OPT_IN    0x40u
#define PCREC_ITER_OPT_BATCH 0x80u
#define PCREC_ITER_STATE_MASK 0x0Fu

#define RX_ITER_F_RETRY   0x1u   /* an EMPTY match was reported at lo: retry there, NOTEMPTY_ATSTART */
#define RX_ITER_F_CHECKED 0x2u   /* the once-per-iterator checks ran */

typedef struct rx_iter {
    uint32_t hdr;      /* STABLE PREFIX: tag | layout | state | option bits */
    int32_t  rc;       /* STABLE PREFIX: 1 live, 0 done, < 0 the code that ended it */
    uint32_t flags;    /* RX_ITER_F_RETRY, RX_ITER_F_CHECKED */
    int32_t  rc_next;  /* the code a batch fill met, delivered after the batch drains (§2.3) */
    const unsigned char *s;   /* bound at init */
    size_t   n;
    size_t   lo;       /* the next search position; never decreases */
    const rx_var *vars;       /* rx_iter_vars; NULL/0 after bind if not set */
    size_t   nvars;
    const void *bufs;         /* <prefix>_iter_buffers; NULL after bind if not set */
    ptrdiff_t (*batch)[2];    /* rx_iter_batch; NULL after bind if not set */
    size_t   nbatch;          /* as set: capacity in PAIRS; after bind: K, in matches */
    size_t   bhead, bcount;   /* the batch cursor: entries [bhead, bcount) are undelivered */
} rx_iter;                    /* I2 appends: union { unsigned char b[S]; uint64_t align_; } st; */

static inline rx_iter rx_iter_init(const unsigned char *s, size_t n)
{ rx_iter it; it.hdr = PCREC_ITER_FRESH; it.s = s; it.n = n; return it; }
#define RX_ITER_INIT(s_, n_) rx_iter_init((s_), (n_))

/* Setters: legal only on a FRESH iterator. On an ENDED one they do nothing, so the sticky rc
   survives. On anything else they poison the header, so the next call refuses with
   PCREC_ERR_ITER rather than rebinding silently. */
#define PCREC_ITER_SET_(it_, stores_, bit_) \
    do { if (((it_)->hdr & ~0xF0u) == PCREC_ITER_FRESH) { stores_; (it_)->hdr |= (bit_); } \
         else if ((it_)->hdr != PCREC_ITER_ENDED) (it_)->hdr = 0; } while (0)
static inline void rx_iter_at(rx_iter *it, size_t pos)
{ PCREC_ITER_SET_(it, it->lo = pos, PCREC_ITER_OPT_AT); }
static inline void rx_iter_vars(rx_iter *it, const rx_var *v, size_t nv)
{ PCREC_ITER_SET_(it, (it->vars = v, it->nvars = nv), PCREC_ITER_OPT_VARS); }
static inline void rx_iter_batch(rx_iter *it, ptrdiff_t (*b)[2], size_t npairs)
{ PCREC_ITER_SET_(it, (it->batch = b, it->nbatch = npairs), PCREC_ITER_OPT_BATCH); }

#endif
