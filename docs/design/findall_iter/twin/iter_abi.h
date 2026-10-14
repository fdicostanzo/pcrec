/* docs/design/findall_iter/twin/iter_abi.h — lane iterdes, [FINDALL-NEXT] HAND TWIN.
 *
 * The shared-ABI-block addition findall_iter.md §1 proposes, as a standalone
 * header the twin includes after the artifact's own .h. In the real build these
 * lines sit INSIDE the artifact's PCREC_RX_ABI_H block (match_api.md §1¶5),
 * byte-identical under every prefix. NOT emitted by pcrec; a design probe.
 */
#ifndef FINDALL_ITER_TWIN_ABI_H
#define FINDALL_ITER_TWIN_ABI_H
#include <stddef.h>
#include <stdint.h>

#ifndef PCREC_ERR_ITER
#define PCREC_ERR_ITER (-10)  /* below PCREC_ERR_FLOOR: NOT a give-up -- the iterator was refused */
#endif

/* S and A: DERIVED from the storage-row table (findall_iter.md §1.3); the twin
 * carries the proposed value. */
#define PCREC_ITER_STATE_SIZE  56
#define PCREC_ITER_STATE_ALIGN 8

/* The header word: a tag ('I','T') in the high half and the rx_iter LAYOUT
 * version in the low byte; FRESH/FRESH_AT/BOUND are three states of one word.
 * A struct of another layout carries another word and is refused. */
#define PCREC_ITER_LAYOUT   1u
#define PCREC_ITER_FRESH    (0x49540000u | (PCREC_ITER_LAYOUT << 8) | 0x01u)
#define PCREC_ITER_FRESH_AT (0x49540000u | (PCREC_ITER_LAYOUT << 8) | 0x02u)
#define PCREC_ITER_BOUND    (0x49540000u | (PCREC_ITER_LAYOUT << 8) | 0x03u)

#define RX_ITER_F_RETRY   0x1u   /* an EMPTY match was reported at lo: retry there, NOTEMPTY_ATSTART */
#define RX_ITER_F_CHECKED 0x2u   /* the once-per-iterator entry checks ran (guard, -futf-check, vars) */

typedef struct rx_iter {
    uint32_t hdr;      /* STABLE PREFIX: PCREC_ITER_FRESH / _FRESH_AT / _BOUND */
    int32_t  rc;       /* STABLE PREFIX: 1 live, 0 done, < 0 the code that ended it; valid after the first call */
    uint32_t flags;    /* RX_ITER_F_* */
    uint32_t reserved_;
    size_t   lo;       /* the next search position; never decreases */
    const unsigned char *s;     /* bound at the first call */
    size_t   n;
    const void *owner;          /* &<prefix>_info of the artifact that bound it */
    const void *vars;           /* (rx_var *) bound by rx_iter_vars(); NULL = none */
    size_t   nvars;
    union { unsigned char b[PCREC_ITER_STATE_SIZE]; uint64_t align_; } st;   /* the storage rows */
} rx_iter;

/* `rx_iter it = RX_ITER_INIT;` writes ONE word (measured: twin/init_spellings.out). */
static inline rx_iter rx_iter_fresh(void) { rx_iter it; it.hdr = PCREC_ITER_FRESH; return it; }
static inline rx_iter rx_iter_fresh_at(size_t pos) { rx_iter it; it.hdr = PCREC_ITER_FRESH_AT; it.lo = pos; return it; }
#define RX_ITER_INIT        rx_iter_fresh()
#define RX_ITER_INIT_AT(p_) rx_iter_fresh_at(p_)

#endif
