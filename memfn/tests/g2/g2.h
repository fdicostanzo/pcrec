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
enum { G2_EMPTY_MISS, G2_EMPTY_NOP, G2_EMPTY_EXCLUDED,
       G2_EMPTY_AT_N };    /* MF_SITE_ABI 6 (Q-R7-2): lo <= n and a non-NULL subject
                              are PROVEN; the outcome on an empty scan is MISS's */
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
    uint8_t         miss_mode;    /* which `miss` expression (g2_missv): 0 "n", 1 (size_t)-1,
                                     2 n + 5, 3 n - 1, 4 the MF_MISS_N token,
                                     5 NULL (unstated), 6 the `n` hook's text */
    uint8_t         hook_style;   /* 0 plain, 1 counted (purity), 2 ternary    */
    uint8_t         mutated;      /* W2 witness: the text was mutated          */
    uint8_t         via;          /* 0 mf_emit, 1 mf_define+mf_use, 2 +mf_call */
    const char     *label;        /* "FIND/EXPR/RETURN" etc.                   */
    g2_fn           fn;           /* the rendered site, wrapped                */
    g2_fn           fn2;          /* via 2: the mf_call copy, else NULL        */
    uint8_t         floor_null;   /* hooks.floor NULL or "0": the driver passes fl 0 */
    /* lane g2u (folding lane g2x) */
    uint8_t         fam;          /* G2_FAM_*: the shape family                */
    uint8_t         leaves;       /* mf_site.on_miss_leaves (Q-G2-18)          */
    uint8_t         pend;         /* G2_PEND_*: 0, or the PENDING-ENFORCE class */
    uint8_t         vfield;       /* G2_V_*: the field a semantic variant varies */
    uint8_t         vclass;       /*   and the class this variant takes        */
    uint8_t         fid;          /* the kit's reported form id, as the generator
                                     numbered it (FORMID lines); counted only  */
    uint8_t         noread;       /* the on_miss text leaves and reads no result
                                     (§15.5's composite ASSIGN: the result may
                                     be unwritten on another predicate's miss) */
    /* lane g2pf: the PF site shape (G2_FAM_PF, integration.md 15.7 [R4g]) */
    uint8_t         pfcell;       /* 1..4: the cell the site is of (a variant keeps it) */
    uint8_t         pfedge;       /* G2_PFE_*: the edge a variant is (0 = the base cell) */
    uint8_t         inplace;      /* the result lvalue IS lo (the same text): the
                                     in-place advance; the wrapper reports lo      */
    uint8_t         noonmiss;     /* the on_miss hook is NULL: the miss is the
                                     written value alone                         */
    uint8_t         lo_over;      /* the driver may pass lo > n (empty, Q-G2-1)    */
    uint8_t         tabbad;       /* the table disagrees with the set: a caller
                                     defect, the answer is UNDEFINED; only a
                                     fault is checked                            */
    /* lane g2m4 (MF_SITE_ABI 6) */
    uint8_t         floor_lo;     /* hooks.floor is the SAME text as hooks.lo: the
                                     floor is lo itself, so the driver passes fl == lo */
    uint8_t         loopx;        /* on_miss is exactly `break;` (Q-R7-3 LOOP_EXIT):
                                     the wrapper runs the site inside a loop the
                                     DRIVER owns, and a break must leave THAT loop */
} g2_site;

/* The shape FAMILIES (lane g2x, folded by lane g2u). G2_FAM_BASE is the
 * original generated space; the others are the site shapes integration.md
 * §15 says pcrec SENDS the kit, generated densely so that the kit's
 * specialised arms, not only its generic row, answer G2 (K35). G2_FAM_SEM is
 * the semantic differential (one field varied over its classes on otherwise
 * identical sites, item 7 of the g2u brief). */
enum {
    G2_FAM_BASE,      /* the original space (term cells, combo grid, width, fill) */
    G2_FAM_OFS,       /* §15.1/§15.2: FUNC/FIND/RETURN, SET+RUN conjunctions     */
    G2_FAM_OFSRUN,    /* §15.1: FUNC/FIND/RETURN over one RUN term, the run grid  */
    G2_FAM_STMT,      /* §15.3/§15.5 lines: the same predicates as STMT sites     */
    G2_FAM_ONEBYTE,   /* §15.3: STMT/FIND/ON_MISS, one SET term at offset 0       */
    G2_FAM_GATE,      /* §15.5: the K82 gate, ONE composite ALL_PRESENT site      */
    G2_FAM_SETREST,   /* §15.4: STMT/ALL_PRESENT/ON_MISS, singleton SETs, EXCLUDED */
    G2_FAM_VMRUN,     /* §15.6, §R4.8.1 item 4: EXPR/VERIFY/BOOL, guard_by_caller */
    G2_FAM_PF,        /* §15.7 [R4g]: STMT/FIND/ASSIGN, one REQUIRED SET at offset 0 */
    G2_FAM_MLINE,     /* §15.7 [R-7]: STMT/FIND/ASSIGN, one REQUIRED one-byte SET at -1,
                         empty AT_N, floor == lo, a leaving on_miss (goto/return/break;) */
    G2_FAM_SEM,       /* the semantic differential's variant groups              */
    G2_NFAM
};
static inline const char *g2_fam_name(int f)
{
    static const char *const names[G2_NFAM] = {
        "base", "ofs", "ofsrun", "stmt", "onebyte", "gate", "setrest", "vmrun", "pf", "mline", "sem",
    };
    return f >= 0 && f < G2_NFAM ? names[f] : "?";
}

/* ENFORCED CLASSES (formerly "PENDING-ENFORCE"; the G2_PEND_* identifiers and
 * the batch header's "pending N" keep the old name): a case whose correct
 * outcome is the kit's row-contract ENFORCEMENT (memfn.h "THE ROW CONTRACTS"),
 * now in force. Its outcome is counted per class, and is a HARD check by
 * default: render + compile + answer as the reference, or a loud refusal
 * naming the field. G2_STRICT_HOOKS=0 is the legacy diagnostic (bucket only). */
enum {
    G2_PEND_NONE,
    G2_PEND_HOOK,     /* F1: non-identifier s/n/lo/floor text on a §15 shape     */
    G2_PEND_MISS,     /* `miss` NULL (UNSTATED, memfn.h) where the handoff writes
                         a miss value (RETURN/ASSIGN): only a refusal naming
                         `miss` serves it                                       */
    G2_PEND_NAME,     /* a refusal of a missing hook whose text does not name it
                         (generator only: no site carries it)                   */
    G2_PEND_FNREF,    /* a FUNC site stating no fn_ref (0 = none) (a refusal
                         naming `fn_ref`, R1; on a RETURN site whose `miss` is
                         also unstated, `miss` serves too)                      */
    G2_PEND_LOOPX,    /* lane g2m4: on_miss is exactly `break;` (Q-R7-3 LOOP_EXIT): the generic
                         row serves none, so the site is RENDERED by a non-generic row (then
                         run inside a driver-owned loop the break must leave) or REFUSED
                         naming `on_miss`                                          */
    G2_PEND_EDGE,     /* lane g2pf: a PF variant that states a field the base cell
                         leaves unstated or in another class: it RENDERS and
                         answers as the reference, or is REFUSED naming that
                         field (the row contracts R1/R2)                        */
    G2_NPEND
};
static inline const char *g2_pend_name(int c)
{
    static const char *const names[G2_NPEND] = { "none", "hook-nonident", "miss-unstated", "refusal-unnamed", "fn_ref-unstated", "loop-exit", "pf-edge" };
    return c >= 0 && c < G2_NPEND ? names[c] : "?";
}

/* lane g2pf: the PF edges (g2_site.pfedge), each a counted population */
enum { G2_PFE_NONE, G2_PFE_MISS, G2_PFE_RESULT, G2_PFE_FLOOR, G2_PFE_NOTE, G2_PFE_DECL,
       G2_PFE_ONMISS, G2_PFE_TABBAD, G2_NPFE };
static inline const char *g2_pfe_name(int e)
{
    static const char *const names[G2_NPFE] = { "none", "miss-not-range-end", "result-not-lo",
        "stated-floor", "stated-note", "stated-result_decl", "stated-on_miss", "table-disagrees" };
    return e >= 0 && e < G2_NPFE ? names[e] : "?";
}

/* The SEMANTIC differential's fields (G2_FAM_SEM): a variant group is one
 * seed site cloned once per value class of ONE field, every other field
 * identical; every variant is answer-checked against the reference. */
enum {
    G2_V_SEED, G2_V_MISS, G2_V_STYLE, G2_V_FLOOR, G2_V_LEAVES, G2_V_DECL, G2_V_USE,
    G2_V_TABREF, G2_V_FNREF, G2_V_PLAN, G2_V_NEED, G2_V_EMPTY, G2_V_POLICY,
    G2_V_CONSUMER, G2_V_CMT, G2_V_VIA, G2_V_SITEFN, G2_NV
};
static inline const char *g2_v_name(int v)
{
    static const char *const names[G2_NV] = {
        "seed", "miss", "hook-style", "floor", "on_miss_leaves", "result_decl", "use",
        "table_ref", "fn_ref", "plan_hint", "term-need", "empty", "policy",
        "consumer", "comment-gate", "via", "site-fn_ref",
    };
    return v >= 0 && v < G2_NV ? names[v] : "?";
}

/* The miss value each miss_mode names; the generator renders the same
 * expression text (g2_gen.c: miss_text). Never a value in [lo, n - eb). */
static inline size_t g2_missv(int mode, size_t n)
{
    switch (mode) {
    case 0:  return n;
    case 1:  return (size_t)-1;
    case 2:  return n + 5;
    case 3:  return n - 1;     /* only with end_back 1 */
    case 4:  return n;         /* MF_MISS_N: the site's own n, stated by token */
    case 5:  return n;         /* `miss` NULL, UNSTATED: PENDING-ENFORCE only (a
                                  rendering is read as §15.1's `miss` = `n`, and
                                  counted in the bucket, never as a pass)    */
    default: return n;         /* 6: exactly the `n` hook's own text         */
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
