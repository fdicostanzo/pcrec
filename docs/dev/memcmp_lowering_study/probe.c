#include <string.h>
#include <stdint.h>
#include <stddef.h>

int cmp_memcmp_1(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 1u <= n_ && !memcmp(s + pos, "\x61", 1);
}


int cmp_memcmp_2(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 2u <= n_ && !memcmp(s + pos, "\x61\x62", 2);
}


int cmp_memcmp_3(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 3u <= n_ && !memcmp(s + pos, "\x61\x62\x63", 3);
}


int cmp_memcmp_4(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 4u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64", 4);
}


int cmp_memcmp_5(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 5u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64\x65", 5);
}


int cmp_memcmp_6(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 6u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64\x65\x66", 6);
}


int cmp_memcmp_7(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 7u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64\x65\x66\x67", 7);
}


int cmp_memcmp_8(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 8u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64\x65\x66\x67\x68", 8);
}


int cmp_memcmp_9(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 9u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64\x65\x66\x67\x68\x69", 9);
}


int cmp_memcmp_10(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 10u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a", 10);
}


int cmp_memcmp_11(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 11u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b", 11);
}


int cmp_memcmp_12(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 12u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c", 12);
}


int cmp_memcmp_13(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 13u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d", 13);
}


int cmp_memcmp_14(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 14u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e", 14);
}


int cmp_memcmp_15(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 15u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f", 15);
}


int cmp_memcmp_16(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 16u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\x70", 16);
}


int cmp_memcmp_17(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 17u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\x70\x71", 17);
}


int cmp_memcmp_20(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 20u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\x70\x71\x72\x73\x74", 20);
}


int cmp_memcmp_24(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 24u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\x70\x71\x72\x73\x74\x75\x76\x77\x78", 24);
}


int cmp_memcmp_31(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 31u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x41\x42\x43\x44\x45", 31);
}


int cmp_memcmp_32(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 32u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x41\x42\x43\x44\x45\x46", 32);
}


int cmp_memcmp_33(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 33u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x41\x42\x43\x44\x45\x46\x47", 33);
}


int cmp_memcmp_40(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 40u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e", 40);
}


int cmp_memcmp_48(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 48u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f\x50\x51\x52\x53\x54\x55\x56", 48);
}


int cmp_memcmp_64(const unsigned char *s, size_t pos, size_t n_) {
    return pos + 64u <= n_ && !memcmp(s + pos, "\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x61\x62", 64);
}


int cmp_mask_1(const unsigned char *s, size_t pos, size_t n_) {
    uint32_t w;
    if (pos + 4u > n_) return 0;
    memcpy(&w, s + pos, 4);
    return (w & (uint32_t)0xffULL) == (uint32_t)97ULL;
}


int cmp_mask_2(const unsigned char *s, size_t pos, size_t n_) {
    uint32_t w;
    if (pos + 4u > n_) return 0;
    memcpy(&w, s + pos, 4);
    return (w & (uint32_t)0xffffULL) == (uint32_t)25185ULL;
}


int cmp_mask_3(const unsigned char *s, size_t pos, size_t n_) {
    uint32_t w;
    if (pos + 4u > n_) return 0;
    memcpy(&w, s + pos, 4);
    return (w & (uint32_t)0xffffffULL) == (uint32_t)6513249ULL;
}


int cmp_mask_4(const unsigned char *s, size_t pos, size_t n_) {
    uint32_t w;
    if (pos + 4u > n_) return 0;
    memcpy(&w, s + pos, 4);
    return (w & (uint32_t)0xffffffffULL) == (uint32_t)1684234849ULL;
}


int cmp_mask_5(const unsigned char *s, size_t pos, size_t n_) {
    uint64_t w;
    if (pos + 8u > n_) return 0;
    memcpy(&w, s + pos, 8);
    return (w & (uint64_t)0xffffffffffULL) == (uint64_t)435475931745ULL;
}


int cmp_mask_6(const unsigned char *s, size_t pos, size_t n_) {
    uint64_t w;
    if (pos + 8u > n_) return 0;
    memcpy(&w, s + pos, 8);
    return (w & (uint64_t)0xffffffffffffULL) == (uint64_t)112585661964897ULL;
}


int cmp_mask_7(const unsigned char *s, size_t pos, size_t n_) {
    uint64_t w;
    if (pos + 8u > n_) return 0;
    memcpy(&w, s + pos, 8);
    return (w & (uint64_t)0xffffffffffffffULL) == (uint64_t)29104508263162465ULL;
}


int cmp_mask_8(const unsigned char *s, size_t pos, size_t n_) {
    uint64_t w;
    if (pos + 8u > n_) return 0;
    memcpy(&w, s + pos, 8);
    return (w & (uint64_t)0xffffffffffffffffULL) == (uint64_t)7523094288207667809ULL;
}

/* cmp_mask_9: no single-load mask form (n=9 > width=8) */

/* cmp_mask_10: no single-load mask form (n=10 > width=8) */

/* cmp_mask_11: no single-load mask form (n=11 > width=8) */

/* cmp_mask_12: no single-load mask form (n=12 > width=8) */

/* cmp_mask_13: no single-load mask form (n=13 > width=8) */

/* cmp_mask_14: no single-load mask form (n=14 > width=8) */

/* cmp_mask_15: no single-load mask form (n=15 > width=8) */

/* cmp_mask_16: no single-load mask form (n=16 > width=8) */

/* cmp_mask_17: no single-load mask form (n=17 > width=8) */

/* cmp_mask_20: no single-load mask form (n=20 > width=8) */

/* cmp_mask_24: no single-load mask form (n=24 > width=8) */

/* cmp_mask_31: no single-load mask form (n=31 > width=8) */

/* cmp_mask_32: no single-load mask form (n=32 > width=8) */

/* cmp_mask_33: no single-load mask form (n=33 > width=8) */

/* cmp_mask_40: no single-load mask form (n=40 > width=8) */

/* cmp_mask_48: no single-load mask form (n=48 > width=8) */

/* cmp_mask_64: no single-load mask form (n=64 > width=8) */


int cmp_overlap_5(const unsigned char *s, size_t pos, size_t n_) {
    uint32_t a, b;
    if (pos + 5u > n_) return 0;
    memcpy(&a, s + pos, 4);
    memcpy(&b, s + pos + 1, 4);
    return a == (uint32_t)1684234849ULL && b == (uint32_t)1701077858ULL;
}


int cmp_overlap_6(const unsigned char *s, size_t pos, size_t n_) {
    uint32_t a, b;
    if (pos + 6u > n_) return 0;
    memcpy(&a, s + pos, 4);
    memcpy(&b, s + pos + 2, 4);
    return a == (uint32_t)1684234849ULL && b == (uint32_t)1717920867ULL;
}


int cmp_overlap_7(const unsigned char *s, size_t pos, size_t n_) {
    uint32_t a, b;
    if (pos + 7u > n_) return 0;
    memcpy(&a, s + pos, 4);
    memcpy(&b, s + pos + 3, 4);
    return a == (uint32_t)1684234849ULL && b == (uint32_t)1734763876ULL;
}

