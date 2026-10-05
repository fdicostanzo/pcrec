/* memfn twins: the HAND-SPECIALIZED set kernels (constants written into the
 * code), one per shape, shared by T-A (ta_set.c, against the generic
 * kernels) and T-C (tc_desc.c, against the same algorithms reached through
 * a compile-time-constant descriptor). Each is vec.h's FIND_BODY with the
 * shape's classifier; see ta_set.c's header for the shapes. */
#ifndef MEMFN_TWINS_SHAPES_H
#define MEMFN_TWINS_SHAPES_H
#include "vec.h"

INL size_t k_q2_shape(const uint8_t *s, size_t n)
{
    const vu8 A = vdup('"'), B = vdup('\'');
#define CLS(v) vor(veq((v), A), veq((v), B))
#define PRED(c) ((c) == '"' || (c) == '\'')
    FIND_BODY(CLS, PRED)
#undef CLS
#undef PRED
}
INL size_t k_h3_shape(const uint8_t *s, size_t n)
{
    const vu8 A = vdup('\t'), B = vdup(' '), C = vdup(0xA0);
#define CLS(v) vor(vor(veq((v), A), veq((v), B)), veq((v), C))
#define PRED(c) ((c) == '\t' || (c) == ' ' || (c) == 0xA0)
    FIND_BODY(CLS, PRED)
#undef CLS
#undef PRED
}
INL size_t k_d_shape(const uint8_t *s, size_t n)
{
    const vu8 LO = vdup('0'), SP = vdup(9);
#define CLS(v) vle(vsub((v), LO), SP)
#define PRED(c) ((uint8_t)((c) - '0') <= 9)
    FIND_BODY(CLS, PRED)
#undef CLS
#undef PRED
}
INL size_t k_ss_shape(const uint8_t *s, size_t n)
{
    const vu8 CARE = vdup(0xDF), VAL = vdup('S');
#define CLS(v) veq(vand((v), CARE), VAL)
#define PRED(c) (((c) & 0xDF) == 'S')
    FIND_BODY(CLS, PRED)
#undef CLS
#undef PRED
}
/* {A,B,a,b} is a cube over x = c - 'A' (members x = 0, 1, 0x20, 0x21: free
 * bits 0x21), cls_tree_study.md §4.3's cube_of form. Not an absolute cube:
 * 'A' ^ 'B' = 0x03, so the offset is load-bearing (the check caught the
 * absolute spelling). */
INL size_t k_ab_shape(const uint8_t *s, size_t n)
{
    const vu8 LO = vdup('A'), CARE = vdup(0xDE), Z = vdup(0);
#define CLS(v) veq(vand(vsub((v), LO), CARE), Z)
#define PRED(c) ((((c) - 'A') & 0xDE) == 0)
    FIND_BODY(CLS, PRED)
#undef CLS
#undef PRED
}
#if VHAVE_TBL
/* nib1: T[l] = the member whose low nibble is l, else a byte whose low
 * nibble is not l (so it never equals the subject byte) */
INL size_t k_sp_shape(const uint8_t *s, size_t n)
{
    static const uint8_t T[16] = { ' ', 0x00, 0x03, 0x02, 0x05, 0x04, 0x07, 0x06,
                                   0x09, '\t', '\n', '\v', '\f', '\r', 0x0F, 0x0E };
    const vu8 TV = vtab(T), F = vdup(0x0F);
#define CLS(v) veq(vtbl(TV, vand((v), F)), (v))
#define PRED(c) (T[(c) & 15] == (c))
    FIND_BODY(CLS, PRED)
#undef CLS
#undef PRED
}
INL size_t k_dm_shape(const uint8_t *s, size_t n)
{
    static const uint8_t T[16] = { '0', '1', '2', '3', '4', '5', '6', '7',
                                   '8', '9', 0x0B, 0x0A, 0x0D, '-', 0x0F, 0x0E };
    const vu8 TV = vtab(T), F = vdup(0x0F);
#define CLS(v) veq(vtbl(TV, vand((v), F)), (v))
#define PRED(c) (T[(c) & 15] == (c))
    FIND_BODY(CLS, PRED)
#undef CLS
#undef PRED
}
#endif
INL size_t k_w_shape(const uint8_t *s, size_t n)
{
    const vu8 B20 = vdup(0x20), LA = vdup('a'), S25 = vdup(25), D0 = vdup('0'),
              S9 = vdup(9), US = vdup('_');
#define CLS(v) vor(vor(vle(vsub(vor((v), B20), LA), S25), vle(vsub((v), D0), S9)), veq((v), US))
#define PRED(c) ((uint8_t)(((c) | 0x20) - 'a') <= 25 || (uint8_t)((c) - '0') <= 9 || (c) == '_')
    FIND_BODY(CLS, PRED)
#undef CLS
#undef PRED
}

#endif
