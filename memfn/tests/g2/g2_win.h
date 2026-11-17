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

/* The twins of the kit's bounds. They only SIZE arrays: every span G2 draws
 * has a literal or drawn length of its own. R-45 (r45_reply rev 6 §3
 * "Answers, controlled by G2"; review r35 F12): G2W_REACH 256, CHOSEN, twice
 * the span r45_reply names (128, twice the largest finite grid head, 64, so
 * that head has positions on both sides). G2W_MAXPOS, the positions per
 * span G2 states, is DERIVED in the generator (the only file that includes
 * memfn.h, and the only one that reads it): min(128, MF_WSPAN_POS), 32 in a
 * tree before the [COVER-CAP] stage 2 raise and r45_reply's 128 after it,
 * with no edit (ruling R1 of lane formsfixb); G2 reaches past 64 with
 * stretches of several spans either way (a loop crosses span boundaries).
 * The generator holds each twin to the kit's own bound with a
 * _Static_assert. */
#define G2W_MAXSPAN 32      /* spans per alternative (MF_WMAX_SPAN)             */
#define G2W_LO      (-8)    /* the least offset (memfn.h -MF_MAX_BACK)          */
#define G2W_REACH   256     /* offsets lie below it (MF_WREACH)                 */
#define G2W_NOFF    (G2W_REACH - G2W_LO)
#define G2W_PROOF_LO (-8)   /* memfn.h MF_PROOF_LO                             */

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
    /* the frame part (plan_frame.md 3.0b), the framed EMIT ask's */
    int      framed;
    char     frame_row[12];
    char     method[8];
    int      search, stream, fused;
    int      plan_test[G2W_NOFF];
    int      stop_test;
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
    int         nproof;         /* the define's class: proof_n rows           */
    const uint8_t (*proven)[32];/* its rows, proven[d - PROOF_LO], d < nproof */
    const char *form_id;        /* mf_result.form_id (opaque: counted only)   */
    const char *row;            /* mf_result.row                              */
    int         pair;           /* the text keeps two memchr streams (PAIR):
                                   the driver's long subjects                 */
    int         run_left;       /* the art carries the lever run-tie-left    */
    /* R-45's span forms (review r35 F17): the head the site was rendered at
       (the lever span-head=N; -1: the shipped default, which G2 does not
       name), and the ONE-CLASS STRETCH the generator stated, [st_lo, st_end)
       with a second class from st_mid (st_mid == st_end: one class; st_end
       0: none). The driver breaks the entries at its edges and at the head
       deterministically (run_breaks). */
    int         head, st_lo, st_mid, st_end;
} g2w_site;



/* One wrapper per site: the rendered text called on (s, n, lo, fl).
 * *wrote: the site wrote its result (ASSIGN frames); *missed: its on_miss
 * ran. The return value is the result (FUNC, ASSIGN), `lo` after the site
 * (ASSIGN_LO) or 0 (ON_MISS). */
typedef size_t (*g2w_fn)(const unsigned char *s, size_t n, size_t lo, size_t fl,
                         int *wrote, int *missed);

/* THE LONG ROWS (R-45 r45_reply rev 6 §3 "Long cases"; review r35 F12):
 * one alternative, one verify-YES all-core stretch of k positions (500, and
 * the longest one alternative can state, G2W_MAXSPAN spans of G2W_MAXPOS:
 * 1024 until MF_WSPAN_POS's raise, then 4095) at offsets 0..k-1, set `a`
 * below `mid` and `b` from it (mid == k: one class), stated in spans of
 * G2W_MAXPOS; frame STMT/ASSIGN, empty MISS, floor SUBJECT. Their answer is
 * G2's own byte loop (g2_win_run.c run_long_rows), not the reference's
 * decision, whose arrays G2W_REACH sizes. `state`: the pass's head, or the
 * deny (I) or the force (L); `head` -1 where the pass names none. */
enum { G2W_LS_HEAD, G2W_LS_DENY, G2W_LS_FORCE };
typedef struct {
    const char *name;
    int         k, mid, head, state, kind_report, stop;
    uint8_t     a[32], b[32];
    g2w_fn      fn;
} g2w_long_site;

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
    /* the in-run stop's branches (span_runs_sheet.md §5 K38-2 PLAN (e)): a
       candidate outside the run decision's own competed with R's stop at a
       mass no greater (and won), and the meet moved R's stop */
    int     inrun_set, inrun_set_won, inrun_meet;
    int     inrun_filt;             /* the in-run filter DECIDES the stop: the scan without it picks another */
    /* R-38 Part D's moved populations (part_d.md §5.1.1 [r3pd FIX-9]), of
       the CHOSEN alternative: R (by role) beside a spelled verify-YES span
       of two or more positions, R the member; R holding a wide position
       (three or more members) with its member an exact position */
    int     r_yes, r_wide;
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
