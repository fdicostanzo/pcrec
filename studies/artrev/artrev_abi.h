/* artrev_abi.h -- the flat art_* surface shim.c exports; included by the drivers. */
#ifndef ARTREV_ABI_H
#define ARTREV_ABI_H
#include <stddef.h>
int       art_ncaps(void);
int       art_have_in(void);
int       art_search(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
int       art_search_in(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
ptrdiff_t art_match(const unsigned char *, size_t, size_t);
ptrdiff_t art_match_in(const unsigned char *, size_t, size_t);
ptrdiff_t art_match_caps(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
ptrdiff_t art_match_caps_in(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
size_t    art_next_pos(const unsigned char *, size_t, size_t);
size_t    art_valid_upto(const unsigned char *, size_t, size_t);
#endif
