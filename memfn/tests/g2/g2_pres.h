/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2's presence family,
 *   lane k382a, R-38 K38-2a; moved to the seam event's statement form at
 *   R-38 K38-2, lane k382).
 *
 * memfn/tests/g2/g2_pres.h — G2'S PRESENCE FAMILY, the site table the
 * generator (g2_pres_gen.c) writes and the driver (g2_pres_run.c) reads. It
 * does not include memfn.h: every field is a FACT as G2 generated or laid it
 * out, or a reply the kit gave through its public ports (the run's ONE
 * decision, mf_class.run, as mf_ask and mf_defined answer it), copied as
 * numbers.
 */
#ifndef G2_PRES_H
#define G2_PRES_H

#include <stddef.h>
#include <stdint.h>

#define G2P_MAXRUN  32          /* the longest generated run (MF_WSPAN_POS)   */
#define G2P_MAXPART 1           /* the run parts a site lays out: ONE, the part
                                   the kit derives from the run span (MF_SITE_ABI
                                   27; no host-cut window, no second part)   */

/* The routes (the PRES row that decided the run's link, read off
 * mf_class.pres_row through mf_finder_rows); G2P_PD the decline (R-38 Part
 * D, part_d.md §2.4 item 2: a run with no findable position, untested on an
 * OPTIONAL route), appended so today's route numbers stay. */
enum { G2P_P0, G2P_P2, G2P_P3, G2P_P9, G2P_PD, G2P_NROUTE };

/* The fixed witnesses of span_runs_sheet.md §3.5 the DRIVER runs (W-K3, the
 * twin, is the generator's: it is a port answer, not text). */
enum { G2P_W_NONE, G2P_W_L1A, G2P_W_L1B, G2P_W_K1, G2P_W_K2, G2P_W_K1B, G2P_W_N };

typedef size_t (*g2p_part_fn)(const unsigned char *s, size_t n, size_t lo);
typedef int (*g2p_use_fn)(const unsigned char *s, size_t n, size_t lo, size_t *out);

/* THE RUN PART, in the RUN frame (review 2026-11-10 r2 k382a ORC-3): the
 * derived part's candidate is the run occurrence's position 0, so the part
 * spans the whole run, positions [at, at + len) = [0, run_len). `fn` is a
 * direct call of the kit's function; `member`, `ver_lo`, `ver_len` are the
 * site's REPLY (mf_class.run: its scan and verified extent, run positions;
 * FAM-2: read off the reply, never derived by G2). */
typedef struct {
    unsigned    at, len;
    g2p_part_fn fn;
    int         member;         /* the reply's scan position                  */
    unsigned    ver_lo, ver_len;/* the reply's verified extent                */
} g2p_part;

typedef struct {
    int         id;
    const char *tag;            /* "<target>.<lever>": the record's site prefix */
    int         route;          /* G2P_P*                                      */
    int         assign;         /* the site ASSIGNs its landmark (re-entry use) */
    int         witness;        /* 1: a lever witness site (all-tie, distinct) */
    int         lever;          /* rendered on an art under run-tie-left       */
    int         wk;             /* G2P_W_*: a §3.5 witness site                */
    unsigned    run_len;
    int32_t     omin;           /* the run span's STATED omin (may be < 0)     */
    int64_t     head_max;       /* K as stated (signed; 0 on an ON_MISS site)  */
    uint8_t     run[G2P_MAXRUN], mask[G2P_MAXRUN];
    int         has_scan, scan; /* the site's reply: mf_class.run              */
    unsigned    ver_lo, ver_len;/* the site's reply: its verified extent       */
    unsigned    nparts;
    g2p_part    parts[G2P_MAXPART];
    g2p_use_fn  entry, reentry; /* reentry NULL on an ON_MISS site             */
    const char *forms;          /* mf_defined's form id                        */
    unsigned    nmem;           /* the verified MEMBER parts' bytes (the head  */
    uint8_t     mem[8];         /* and the rest), as laid out: each must occur */
                                /* in [lo, n) for the site to answer present   */
} g2p_site;

/* R-38 Part D (part_d.md §5.1 D0 [r1pd F16, F18]): THE WIDE STREAM's sites
 * state each run position as a SET (run_len sets of 32 bytes; their `run`
 * and `mask` unread), listed in a table of their own that the generator
 * writes only where it renders a wide site. WEAK, so a site file of today's
 * stream alone (which must stay byte-identical, a hashed check) declares
 * neither and links: &g2p_nwides is then NULL, and position j of every site
 * is {b : (b & mask[j]) == run[j]} as before. */
typedef struct {
    int             id;
    const uint8_t (*sets)[32];
} g2p_wide;
extern const g2p_wide g2p_wides[] __attribute__((weak));
extern const int g2p_nwides __attribute__((weak));

extern const g2p_site g2p_sites[];
extern const int g2p_nsites;

/* The recorder (g2_pres_run.c): every run-part call of the kit's text goes
 * through it (the generator's `#define <fn>(...)` after each definition). */
size_t g2p_rec(int site, int part, g2p_part_fn fn, const unsigned char *s, size_t n,
               size_t lo);

#endif
