/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2, lane memfng2).
 *
 * memfn/tests/g2/g2.h — G2's OWN description of a generated site, shared
 * by the generator (g2_gen.c, which also renders the site through the kit)
 * and the driver (g2_driver.c + g2_ref.c, which never sees the kit).
 *
 * This header is the test's vocabulary, written from the contract
 * (integration.md §14.3-§14.7), not from the kit: it does not include
 * memfn.h, and its enum values are G2's own. The generator maps them onto
 * the kit's enums in one place (g2_gen.c: to_mf_*), so a renumbering of the
 * kit's enums cannot silently re-label a reference case.
 */
#ifndef G2_H
#define G2_H

#include <stddef.h>
#include <stdint.h>

enum { G2_FORM_EXPR, G2_FORM_STMT, G2_FORM_FUNC };
enum { G2_OP_FIND, G2_OP_SKIP, G2_OP_VERIFY, G2_OP_ALL };
enum { G2_H_RETURN, G2_H_ASSIGN, G2_H_ON_MISS, G2_H_ADVANCE, G2_H_ON_CAND,
       G2_H_BOOL };
enum { G2_EMPTY_MISS, G2_EMPTY_NOP, G2_EMPTY_EXCLUDED };
enum { G2_REQ, G2_OPT };
enum { G2_T_SET, G2_T_RUN };
enum { G2_USE_POSITION, G2_USE_DISCARD };

#define G2_MAXT   8           /* terms per predicate (the header's MF_MAX_TERM) */
#define G2_MAXOPT 6           /* OPTIONAL items per site: 2^6 candidate subsets */
#define G2_LOGMAX 160         /* ON_CAND visits recorded per call               */
#define G2_SENT   ((size_t)0x5e7f00d5e7f00dULL)  /* "never written" sentinel   */
#define G2_UNBOUNDED UINT64_MAX

typedef struct {
    uint8_t        kind;      /* G2_T_*                                        */
    uint8_t        need;      /* G2_REQ / G2_OPT                               */
    int32_t        off;       /* from cand; may be negative                    */
    uint8_t        set[32];   /* SET: bit (b & 7) of byte b >> 3              */
    uint32_t       len;       /* RUN: bytes                                    */
    const uint8_t *run;       /* RUN                                           */
    const uint8_t *mask;      /* RUN: NULL = exact                             */
} g2_term;

typedef struct {
    uint8_t  nterm;
    uint8_t  need;            /* a whole predicate may be OPTIONAL (ALL only)  */
    g2_term  t[G2_MAXT];
} g2_pred;

struct g2_out {               /* what one call of a rendered site produced     */
    size_t        res;
    int           missed;     /* on_miss ran                                   */
    unsigned long cnt;        /* ADVANCE: the count, when the site has one     */
    uint32_t      nlog;       /* ON_CAND: the candidates visited, in order     */
    size_t        log[G2_LOGMAX];
    uint32_t      acc_mod;    /* ON_CAND: accept iff (cand + salt) % acc_mod == 0 */
    uint32_t      salt;       /*   (acc_mod 0: never accept)                   */
};

typedef int (*g2_fn)(const unsigned char *s, size_t n, size_t lo, size_t fl,
                     struct g2_out *o);

typedef struct {
    uint32_t        id;
    uint8_t         form, op, handoff, reverse, empty, end_back, use;
    uint8_t         gbc;          /* guard_by_caller (EXPR VERIFY)             */
    uint8_t         ret_pred;     /* 0xFF = none                               */
    uint16_t        npred;        /* FIND/SKIP/VERIFY: 1                       */
    const g2_pred  *preds;
    uint8_t         has_count;    /* ADVANCE                                   */
    unsigned long   count_start;
    uint64_t        span_lo, span_hi;  /* TRUE facts: the driver honours them */
    uint32_t        reach;        /* ON_CAND: on_cand_reach                    */
    uint8_t         tok;          /* ON_CAND: 0 `if (acc) A`, 1 A, 2 R         */
    uint32_t        acc_mod;
    uint8_t         miss_mode;    /* which `miss` expression (g2_missv); 4 = the MF_MISS_N token */
    uint8_t         hook_style;   /* 0 plain, 1 counted (purity), 2 ternary    */
    uint8_t         mutated;      /* W2 witness: the text was mutated          */
    uint8_t         via;          /* 0 mf_emit, 1 mf_define+mf_use, 2 +mf_call */
    const char     *label;        /* "FIND/EXPR/RETURN" etc.                   */
    g2_fn           fn;           /* the rendered site, wrapped                */
    g2_fn           fn2;          /* via 2: the mf_call copy, else NULL        */
    uint8_t         floor_null;   /* hooks.floor NULL: the driver passes fl 0  */
} g2_site;

/* The miss value each miss_mode names; the generator renders the same
 * expression text (g2_gen.c: miss_text). Never a value in [lo, n - eb). */
static inline size_t g2_missv(int mode, size_t n)
{
    switch (mode) {
    case 0:  return n;
    case 1:  return (size_t)-1;
    case 2:  return n + 5;
    case 4:  return n;         /* MF_MISS_N: the site's own n, stated by token */
    default: return n - 1;     /* mode 3: only with end_back 1 */
    }
}

/* --- helpers the rendered wrappers call (pcrec's side of the hooks) ------ */

/* hook-evaluation counter (style 1): a function call, so two evaluations
 * in one expression are indeterminately sequenced, never unsequenced */
extern unsigned long g2_evc;
static inline int g2_tick(void) { g2_evc++; return 1; }
#define G2_EV(x) (g2_tick() ? (x) : (x))

/* on_cand's body: read exactly reach bytes at cand (so a guard page sees an
 * unestablished cand + reach <= n), record the visit, decide. */
static inline void g2_touch(const unsigned char *s, size_t cand, uint32_t reach,
                            struct g2_out *o)
{
    volatile unsigned char sink = 0;
    for (uint32_t j = 0; j < reach; j++) sink ^= s[cand + j];
    (void)sink;
    if (o->nlog < G2_LOGMAX) o->log[o->nlog] = cand;
    o->nlog++;
}
static inline int g2_acc(struct g2_out *o, size_t cand)
{
    return o->acc_mod && (cand + o->salt) % o->acc_mod == 0;
}

#endif /* G2_H */
