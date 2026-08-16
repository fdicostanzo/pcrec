#ifndef PATTERN_H
#define PATTERN_H

#include <stddef.h>

/* A pattern is k positions, each with a set of allowed bytes stored as a
 * 256-bit bitmap. Exact needles are all-singleton; case-insensitive adds the
 * ASCII case twin of every alpha member; [ab] groups list members explicitly.
 * This is the harness's universal oracle representation. */

#define PAT_MAX_K 32

typedef struct {
    int k;
    unsigned char bits[PAT_MAX_K][32]; /* bit b of position j: bits[j][b>>3] >> (b&7) */
} pattern_t;

/* Compile a spec string: plain bytes are singleton positions; "[...]" lists
 * the members of one position (no ranges, no escapes; '[' ']' cannot be
 * members). ci != 0 adds the ASCII case twin of every alphabetic member.
 * Returns 0 on success, -1 on syntax error, empty pattern, empty group,
 * or k > PAT_MAX_K. */
int pat_compile(const char *spec, int ci, pattern_t *out);

static inline int pat_member(const pattern_t *p, int pos, unsigned char b)
{
    return (p->bits[pos][b >> 3] >> (b & 7)) & 1;
}

int pat_count(const pattern_t *p, int pos);        /* number of members */
int pat_nth(const pattern_t *p, int pos, int idx); /* idx'th member (0-based, ascending), -1 if out of range */
int pat_is_exact(const pattern_t *p);              /* 1 if every position is a singleton */

/* Naive reference scan: pointer to the first i where hay[i+j] is a member of
 * position j for all j, else NULL. Never reads at or past hay+n. */
const char *pat_scan(const pattern_t *p, const char *hay, size_t n);

/* ---- alternation ------------------------------------------------------ */

#define PAT_MAX_BR 8

/* Top-level alternation of fixed-length branches: spec syntax adds
 *   '|'   separating branches (no grouping, no nesting)
 *   {N}   the preceding position repeated so it appears N times total
 *         (N decimal, 1..PAT_MAX_K)
 *   '+'   on the preceding position: one-or-more. Because matchers report
 *         only the leftmost START position, X+ matches at i exactly when
 *         X{1} does, so '+' compiles to a single occurrence -- exact, not
 *         an approximation, under start-only semantics.
 * A match at i means at least one branch matches at i. */
typedef struct {
    int nbr;
    pattern_t br[PAT_MAX_BR];
} alt_t;

/* Returns 0 on success; -1 on syntax error, empty branch, too many branches,
 * or any branch exceeding PAT_MAX_K positions. ci applies to every branch. */
int alt_compile(const char *spec, int ci, alt_t *out);

/* First i where any branch matches; NULL if none. Never reads >= hay+n. */
const char *alt_scan(const alt_t *a, const char *hay, size_t n);

int alt_min_k(const alt_t *a);
int alt_max_k(const alt_t *a);

#endif
