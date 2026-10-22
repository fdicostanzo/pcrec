/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2's window family, lane
 *   wsc1, D172 S2 commit 1).
 *
 * memfn/tests/g2/g2_win.h — G2'S WINDOW FAMILY: its OWN description of a
 * window site (docs/design/memfn/window_site.md rev 3.2 §1), shared by the
 * generator (g2_win_gen.c, the only file that calls the kit), the reference
 * (g2_win_ref.c) and the driver (g2_win_run.c). It does not include memfn.h:
 * the reference and the driver read G2's facts, never the kit's types.
 */
#ifndef G2_WIN_H
#define G2_WIN_H

#include <stddef.h>
#include <stdint.h>

#define G2W_MAXPOS  32      /* positions per span (memfn.h MF_WSPAN_POS)        */
#define G2W_MAXSPAN 32      /* spans per alternative (MF_WMAX_SPAN)             */
#define G2W_LO      (-8)    /* the least offset (memfn.h -MF_MAX_BACK)          */
#define G2W_REACH   64      /* offsets lie below it (MF_WREACH)                 */
#define G2W_NOFF    (G2W_REACH - G2W_LO)
#define G2W_PROOF_LO (-8)   /* memfn.h MF_PROOF_LO                             */
#define G2W_NPROOF  41      /* MF_MAX_FWD - MF_PROOF_LO: the proof's offsets   */

enum { G2W_YES = 1, G2W_NO = 2 };                       /* verify            */
enum { G2W_E_NONE = 1, G2W_E_PARKED = 2, G2W_E_RESEED = 3 };  /* entry         */
enum { G2W_F_UNSTATED = 0, G2W_F_SUBJECT = 1, G2W_F_EXPR = 2 };  /* floor      */

typedef struct {
    int             start;
    int             len;
    int             verify;
    int             core_lo, core_len;
    const uint8_t (*set)[32];       /* set[j], j < len                       */
    const uint32_t *table;          /* table[j]: G2's offer id, 0: none      */
} g2w_span;

typedef struct {
    int             entry;
    int             nspan;
    const g2w_span *span;
} g2w_alt;

/* What the kit answered (mf_wreply), copied field by field by the generator:
 * the driver holds it to the reference's own decision. */
typedef struct {
    int      alt, reseed, has_stop, stop;
    uint8_t  stop_set[32];
    int      nplan;
    int      plan[G2W_NOFF];
    int      plan_term[G2W_NOFF];
    int      pinned, run_stated, run_member, run_lo, run_len;
    char     path[16];
} g2w_reply;

/* The frames G2 renders a site in (the driver's wrapper per site). */
enum {
    G2W_FR_FUNC,        /* FUNC / RETURN                                       */
    G2W_FR_ASSIGN,      /* STMT / ASSIGN, `result` the wrapper's own variable  */
    G2W_FR_ASSIGN_LO,   /* STMT / ASSIGN in place: `result` IS `lo`, miss n    */
    G2W_FR_ONMISS,      /* STMT / ON_MISS                                      */
};
enum { G2W_EMPTY_MISS, G2W_EMPTY_NOP, G2W_EMPTY_EXCLUDED, G2W_EMPTY_AT_N };

typedef struct {
    const char *name;
    int         nalt;
    g2w_alt     alt[2];
    int         wfloor;
    int         floor_is_lo;    /* the `floor` hook's text IS lo's: F == lo   */
    int         frame, empty;
    int         miss_n;         /* the miss: 0 (size_t)-1, 1 n, 2 n - 1        */
    int         onm;            /* on_miss: 0 none, 1 braced, 2 a leaving goto */
    int         rate_kind;      /* 0: no byte-rate (NONE), 1 skewed, 2 ties   */
    const uint32_t *rate;       /* the analysis object's byte-rate, or NULL   */
    g2w_reply   reply;
    const uint8_t (*proven)[32];/* the define's class, proven[d - PROOF_LO]   */
    const char *form_id;        /* mf_result.form_id (opaque: counted only)   */
    const char *row;            /* mf_result.row                              */
} g2w_site;

/* One wrapper per site: the rendered text called on (s, n, lo, fl).
 * *wrote: the site wrote its result (ASSIGN frames); *missed: its on_miss
 * ran. The return value is the result (FUNC, ASSIGN), `lo` after the site
 * (ASSIGN_LO) or 0 (ON_MISS). */
typedef size_t (*g2w_fn)(const unsigned char *s, size_t n, size_t lo, size_t fl,
                         int *wrote, int *missed);

/* ---- the reference (g2_win_ref.c): written from window_site.md rev 3.2,
 * never from the kit's source ----------------------------------------------- */

/* The decision the design describes (§2.1 Table A, MARGIN, TIE; §2.3 Table C;
 * §3.2 prefix_k), over the facts and the rate (NULL: NONE). */
typedef struct {
    int     alt, reseed, has_stop, stop;
    uint8_t stop_set[32];
    int     nplan;
    int     plan[G2W_NOFF];         /* ascending                              */
    int     plan_term[G2W_NOFF];    /* equal = one compare                    */
    int     pinned, run_stated, run_member, run_lo, run_len;
    /* the tested positions (plan and stop) as the text must test them */
    int     ntest;
    int     toff[G2W_NOFF + 1];
    uint8_t tset[G2W_NOFF + 1][32];
    int     tcore[G2W_NOFF + 1];
    int     hy_set, hy;             /* the empty range                        */
    /* which tie rows decided something (the floors count them) */
    int     tie_mass, tie_model, margin_tie;
    const char *arow;               /* "empty" "parked" "reseed" "mass" "floor" */
} g2w_dec;

void g2w_decide(const g2w_site *x, const uint32_t *rate, g2w_dec *out);
/* The defect the reference plants (--ref-defect K, its W1 witness), 0: none */
extern int g2w_ref_defect;

/* The answer semantics (§1.2, §1.3): 1 iff span `sp` holds at candidate c of
 * subject s[0..n) under floor F (the core rule; a position inside [0, F) is
 * pcrec's edge: not covered, so it fails). `ronly`: unused here. */
int g2w_span_holds(const g2w_span *sp, const unsigned char *s, long n, long F, long c);
/* 1 iff the TESTED positions hold at c (the plan semantics). */
int g2w_tested_hold(const g2w_dec *d, const unsigned char *s, long n, long F, long c);

#endif /* G2_WIN_H */
