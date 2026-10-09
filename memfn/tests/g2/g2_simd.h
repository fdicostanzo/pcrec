/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2's SIMD family, lane
 *   r13, R-13).
 *
 * memfn/tests/g2/g2_simd.h — the site table G2's SIMD family's generated TU
 * exports to its driver (g2_simd_gen.c writes it, g2_simd_driver.c reads it).
 * Everything here is what G2 GENERATED, never what the kit computed: the
 * driver's reference reads only these bytes.
 */
#ifndef G2_SIMD_H
#define G2_SIMD_H
#include <stddef.h>

typedef size_t (*g2v_fn)(const unsigned char *s, size_t n, size_t lo);

typedef struct {
    unsigned id, cls, L, off;
    g2v_fn fn;
    unsigned char run[40], mask[40];
    unsigned two;       /* a second term: the byte 'z' right after the run */
} g2v_site;

extern const g2v_site g2v_sites[];
extern const unsigned g2v_nsites;
/* per-path execution counters, [4 * level + path] (w16 0-3, w32 4-7): the
 * runner's text instrumentation of the rendered file, never the kit's */
extern unsigned long g2v_path[8];
#endif
