/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2's presence family,
 *   lane k382a, R-38 K38-2a).
 *
 * memfn/tests/g2/g2_pres.h — G2'S PRESENCE FAMILY, the site table the
 * generator (g2_pres_gen.c) writes and the driver (g2_pres_run.c) reads. It
 * does not include memfn.h: every field is a FACT as G2 generated or laid it
 * out, or a reply the kit gave through its public ports (mf_pres_ports,
 * mf_wdecide, mf_class's links), copied as numbers.
 */
#ifndef G2_PRES_H
#define G2_PRES_H

#include <stddef.h>
#include <stdint.h>

#define G2P_MAXRUN  32          /* the longest generated run (MF_WSPAN_POS)   */
#define G2P_MAXPART 2           /* the run parts a site may lay out: the
                                   window and the whole run                  */

/* The routes (the PRES row that decided the run's link, read off
 * mf_class.pres_row through mf_finder_rows). */
enum { G2P_P0, G2P_P2, G2P_P3, G2P_P9, G2P_NROUTE };

typedef size_t (*g2p_part_fn)(const unsigned char *s, size_t n, size_t lo);
typedef int (*g2p_use_fn)(const unsigned char *s, size_t n, size_t lo, size_t *out);

/* One RUN PART the generator laid out: positions [at, at + len) of the
 * site's whole run, the part's own statement. `fn` is a direct call of the
 * kit's function (NULL where the kit implied the part and defined none,
 * R-30); the reply is the window family's for the part's statement
 * (mf_wdecide on the same art: run_member and [run_lo, run_lo + run_len),
 * part positions). */
typedef struct {
    unsigned    at, len;
    g2p_part_fn fn;
    int         member;         /* the reply's scan position (part frame)     */
    unsigned    ver_lo, ver_len;/* the reply's verified stretch (part frame)  */
} g2p_part;

typedef struct {
    int         id;
    const char *tag;            /* "<target>.<lever>": the record's site prefix */
    int         route;          /* G2P_P*                                      */
    int         assign;         /* the site ASSIGNs its landmark (re-entry use) */
    int         witness;        /* 1: a lever witness site (all-tie, distinct) */
    int         lever;          /* rendered on an art under run-tie-left       */
    unsigned    run_len;
    int32_t     omin;           /* the run span's STATED omin (the statement's) */
    uint8_t     run[G2P_MAXRUN], mask[G2P_MAXRUN];
    int         scan;           /* the site's reply: mf_pres_ports' run_scan   */
    unsigned    ver_lo, ver_len;/* the site's reply: P3's window, or the whole */
    unsigned    nparts;
    g2p_part    parts[G2P_MAXPART];
    g2p_use_fn  entry, reentry; /* reentry NULL on an ON_MISS site             */
    const char *forms;          /* mf_defined's form id                        */
} g2p_site;

extern const g2p_site g2p_sites[];
extern const int g2p_nsites;

/* The recorder (g2_pres_run.c): every run-part call of the kit's text goes
 * through it (the generator's `#define <fn>(...)` after each definition). */
size_t g2p_rec(int site, int part, g2p_part_fn fn, const unsigned char *s, size_t n,
               size_t lo);

#endif
