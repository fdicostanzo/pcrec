/* memfn twins: the HAND-SPECIALIZED set kernels (constants written into the
 * code), one per shape, shared by T-A (ta_set.c, against the generic
 * kernels) and T-C (tc_desc.c, against the same algorithms reached through
 * a compile-time-constant descriptor). Per set X: X_DECL (the constant
 * vectors), X_CLS(v) (the compare vector), X_PRED(c) (one byte), and from
 * them k_X_shape (vec.h FIND_BODY: find-first) and k_X_iter (ITER_BODY: a
 * find-all that keeps the block mask across hits, T-A's restart control).
 * See ta_set.c's header for the shapes. */
#ifndef MEMFN_TWINS_SHAPES_H
#define MEMFN_TWINS_SHAPES_H
#include "vec.h"

#define q2_DECL const vu8 A = vdup('"'), B = vdup('\'')
#define q2_CLS(v) vor(veq((v), A), veq((v), B))
#define q2_PRED(c) ((c) == '"' || (c) == '\'')

#define h3_DECL const vu8 A = vdup('\t'), B = vdup(' '), C = vdup(0xA0)
#define h3_CLS(v) vor(vor(veq((v), A), veq((v), B)), veq((v), C))
#define h3_PRED(c) ((c) == '\t' || (c) == ' ' || (c) == 0xA0)

#define d_DECL const vu8 LO = vdup('0'), SP = vdup(9)
#define d_CLS(v) vle(vsub((v), LO), SP)
#define d_PRED(c) ((uint8_t)((c) - '0') <= 9)

#define ss_DECL const vu8 CARE = vdup(0xDF), VAL = vdup('S')
#define ss_CLS(v) veq(vand((v), CARE), VAL)
#define ss_PRED(c) (((c) & 0xDF) == 'S')

/* {A,B,a,b} is a cube over x = c - 'A' (members x = 0, 1, 0x20, 0x21: free
 * bits 0x21), cls_tree_study.md §4.3's cube_of form. Not an absolute cube:
 * 'A' ^ 'B' = 0x03, so the offset is load-bearing (the check caught the
 * absolute spelling). */
#define ab_DECL const vu8 LO = vdup('A'), CARE = vdup(0xDE), Z = vdup(0)
#define ab_CLS(v) veq(vand(vsub((v), LO), CARE), Z)
#define ab_PRED(c) ((((c) - 'A') & 0xDE) == 0)

#if VHAVE_TBL
/* nib1: T[l] = the member whose low nibble is l, else a byte whose low
 * nibble is not l (so it never equals the subject byte) */
static const uint8_t sp_T[16] = { ' ', 0x00, 0x03, 0x02, 0x05, 0x04, 0x07, 0x06,
                                  0x09, '\t', '\n', '\v', '\f', '\r', 0x0F, 0x0E };
#define sp_DECL const vu8 TV = vtab(sp_T), F = vdup(0x0F)
#define sp_CLS(v) veq(vtbl(TV, vand((v), F)), (v))
#define sp_PRED(c) (sp_T[(c) & 15] == (c))

static const uint8_t dm_T[16] = { '0', '1', '2', '3', '4', '5', '6', '7',
                                  '8', '9', 0x0B, 0x0A, 0x0D, '-', 0x0F, 0x0E };
#define dm_DECL const vu8 TV = vtab(dm_T), F = vdup(0x0F)
#define dm_CLS(v) veq(vtbl(TV, vand((v), F)), (v))
#define dm_PRED(c) (dm_T[(c) & 15] == (c))
#endif

#define w_DECL const vu8 B20 = vdup(0x20), LA = vdup('a'), S25 = vdup(25), D0 = vdup('0'), \
                         S9 = vdup(9), US = vdup('_')
#define w_CLS(v) vor(vor(vle(vsub(vor((v), B20), LA), S25), vle(vsub((v), D0), S9)), veq((v), US))
#define w_PRED(c) ((uint8_t)(((c) | 0x20) - 'a') <= 25 || (uint8_t)((c) - '0') <= 9 || (c) == '_')

#define DEFSHAPE(X)                                                           \
    INL size_t k_##X##_shape(const uint8_t *s, size_t n)                      \
    {                                                                         \
        X##_DECL;                                                             \
        FIND_BODY(X##_CLS, X##_PRED)                                          \
    }                                                                         \
    INL long k_##X##_iter(const uint8_t *s, size_t n, size_t *pos, long cap)  \
    {                                                                         \
        X##_DECL;                                                             \
        ITER_BODY(X##_CLS, X##_PRED)                                          \
    }
DEFSHAPE(q2) DEFSHAPE(h3) DEFSHAPE(d) DEFSHAPE(ss) DEFSHAPE(ab) DEFSHAPE(w)
#if VHAVE_TBL
DEFSHAPE(sp) DEFSHAPE(dm)
#endif

#endif
