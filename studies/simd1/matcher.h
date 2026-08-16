#ifndef MATCHER_H
#define MATCHER_H

#include <stddef.h>

/* A candidate matcher is compiled for one fixed, known pattern.
 * It receives only the haystack and its length, and returns a pointer to the
 * first position where every pattern position matches, or NULL if absent.
 * Ground truth is pat_scan() over the compiled (pattern, ci) from the
 * registry row; for exact literal patterns that equals
 * memmem(hay, n, needle, strlen(needle)).
 *
 * Hard requirements (the harness enforces these with guard pages):
 *  - never read hay[i] for i >= n, or before hay[0]
 *  - n == 0 and n < needle_len must return NULL without touching memory
 *  - haystack is NOT NUL-terminated; it may contain any byte values
 */
typedef const char *(*match_fn)(const char *hay, size_t n);

typedef struct {
    const char *name;    /* unique short name, used in reports and --matcher */
    const char *pattern; /* pattern spec (see pattern.h): literals + [ab] groups */
    int ci;              /* 1 = ASCII case-insensitive (alpha members get twins) */
    match_fn fn;
    int needs_avx2;      /* 1 if the fn uses AVX2 instructions */
} matcher;

extern const matcher MATCHERS[];
extern const int N_MATCHERS;

#endif
