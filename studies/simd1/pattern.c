#include "pattern.h"

#include <string.h>

/* Sets member b at position pos; when ci is set and b is ASCII alpha, also
 * sets its case twin (b ^ 0x20). */
static void set_member(pattern_t *out, int pos, unsigned char b, int ci)
{
    out->bits[pos][b >> 3] |= (unsigned char)(1u << (b & 7));
    if (ci && ((b >= 'A' && b <= 'Z') || (b >= 'a' && b <= 'z'))) {
        unsigned char t = (unsigned char)(b ^ 0x20);
        out->bits[pos][t >> 3] |= (unsigned char)(1u << (t & 7));
    }
}

/* Parses a "[...]" group: *sp points at the '['. Fills position pos with the
 * listed members and advances *sp past the ']'. Returns 0, or -1 on a '['
 * member, an empty group, or a missing ']'. Callers check the k bound before
 * calling, so pos is always in range. */
static int parse_group(const char **sp, pattern_t *out, int pos, int ci)
{
    const char *s = *sp + 1; /* past '[' */
    int had_member = 0;

    while (*s && *s != ']') {
        if (*s == '[')
            return -1; /* '[' cannot be a member */
        set_member(out, pos, (unsigned char)*s, ci);
        had_member = 1;
        s++;
    }
    if (*s != ']')
        return -1; /* unterminated group */
    if (!had_member)
        return -1; /* empty group */

    *sp = s + 1;
    return 0;
}

int pat_compile(const char *spec, int ci, pattern_t *out)
{
    if (!spec || !out)
        return -1;

    memset(out, 0, sizeof *out);

    int k = 0;
    const char *s = spec;

    while (*s) {
        if (k >= PAT_MAX_K)
            return -1;
        if (*s == '[') {
            if (parse_group(&s, out, k, ci) != 0)
                return -1;
            k++;
        } else {
            set_member(out, k, (unsigned char)*s, ci);
            k++;
            s++;
        }
    }

    if (k == 0 || k > PAT_MAX_K)
        return -1;

    out->k = k;
    return 0;
}

int pat_count(const pattern_t *p, int pos)
{
    int c = 0;
    for (int i = 0; i < 32; i++)
        c += __builtin_popcount(p->bits[pos][i]);
    return c;
}

/* Members are returned in ascending byte-value order: idx 0 is the smallest
 * member byte, idx 1 the next smallest, and so on. */
int pat_nth(const pattern_t *p, int pos, int idx)
{
    if (idx < 0)
        return -1;
    for (int b = 0; b < 256; b++) {
        if (pat_member(p, pos, (unsigned char)b)) {
            if (idx == 0)
                return b;
            idx--;
        }
    }
    return -1;
}

int pat_is_exact(const pattern_t *p)
{
    for (int i = 0; i < p->k; i++)
        if (pat_count(p, i) != 1)
            return 0;
    return 1;
}

const char *pat_scan(const pattern_t *p, const char *hay, size_t n)
{
    int k = p->k;

    if ((size_t)k > n)
        return NULL;

    for (size_t i = 0; i + (size_t)k <= n; i++) {
        int j = 0;
        for (; j < k; j++) {
            if (!pat_member(p, j, (unsigned char)hay[i + j]))
                break;
        }
        if (j == k)
            return hay + i;
    }
    return NULL;
}

/* ---- alternation ------------------------------------------------------ */

/* Parses "{N}": *sp points at the '{'. Stores N and advances *sp past the '}'.
 * Returns 0, or -1 on missing digits, a missing '}', or N outside 1..PAT_MAX_K.
 * A '{' that does not parse as a quantifier is an error, never a literal. */
static int parse_repeat(const char **sp, int *nrep)
{
    const char *s = *sp + 1; /* past '{' */
    int ndig = 0;
    long n = 0;

    while (*s >= '0' && *s <= '9') {
        if (n <= PAT_MAX_K) /* stop accumulating once out of range: no overflow */
            n = n * 10 + (*s - '0');
        ndig++;
        s++;
    }
    if (ndig == 0 || *s != '}')
        return -1;
    if (n < 1 || n > PAT_MAX_K)
        return -1;

    *sp = s + 1;
    *nrep = (int)n;
    return 0;
}

int alt_compile(const char *spec, int ci, alt_t *out)
{
    if (!spec || !out)
        return -1;

    memset(out, 0, sizeof *out);

    int nbr = 0;
    const char *s = spec;

    for (;;) {
        if (nbr >= PAT_MAX_BR)
            return -1; /* too many branches */

        pattern_t *p = &out->br[nbr];
        int k = 0; /* k > 0 also means "this branch has a position to modify" */

        while (*s && *s != '|') {
            if (*s == '{') {
                int nrep;

                if (k == 0)
                    return -1; /* quantifier with nothing to repeat */
                if (parse_repeat(&s, &nrep) != 0)
                    return -1;
                /* The position appears nrep times in total, so append nrep - 1
                 * more copies of its bitmap. */
                for (int r = 1; r < nrep; r++) {
                    if (k >= PAT_MAX_K)
                        return -1;
                    memcpy(p->bits[k], p->bits[k - 1], sizeof p->bits[k]);
                    k++;
                }
            } else if (*s == '+') {
                if (k == 0)
                    return -1; /* nothing to repeat */
                /* No-op, and exact rather than approximate: matchers report
                 * only the leftmost START of a match, and X+ can start at i
                 * exactly when X matches at i -- the extra repetitions only
                 * extend the match to the right, which never changes the set
                 * of start positions. So one occurrence is the right compile. */
                s++;
            } else if (*s == '[') {
                if (k >= PAT_MAX_K)
                    return -1;
                if (parse_group(&s, p, k, ci) != 0)
                    return -1;
                k++;
            } else {
                /* Any other byte, ']' included, is a singleton position. */
                if (k >= PAT_MAX_K)
                    return -1;
                set_member(p, k, (unsigned char)*s, ci);
                k++;
                s++;
            }
        }

        if (k < 1 || k > PAT_MAX_K)
            return -1; /* empty branch (or overrun) */
        p->k = k;
        nbr++;

        if (*s == '\0')
            break;
        s++; /* past '|' */
    }

    out->nbr = nbr;
    return 0;
}

const char *alt_scan(const alt_t *a, const char *hay, size_t n)
{
    int mink = alt_min_k(a);

    if (mink <= 0)
        return NULL;

    /* No branch can match past the point where the shortest one still fits. */
    for (size_t i = 0; i + (size_t)mink <= n; i++) {
        for (int b = 0; b < a->nbr; b++) {
            const pattern_t *p = &a->br[b];

            if (i + (size_t)p->k > n)
                continue; /* this branch runs off the end here */
            int j = 0;
            for (; j < p->k; j++) {
                if (!pat_member(p, j, (unsigned char)hay[i + j]))
                    break;
            }
            if (j == p->k)
                return hay + i;
        }
    }
    return NULL;
}

int alt_min_k(const alt_t *a)
{
    if (a->nbr <= 0)
        return 0;

    int m = a->br[0].k;
    for (int b = 1; b < a->nbr; b++)
        if (a->br[b].k < m)
            m = a->br[b].k;
    return m;
}

int alt_max_k(const alt_t *a)
{
    if (a->nbr <= 0)
        return 0;

    int m = a->br[0].k;
    for (int b = 1; b < a->nbr; b++)
        if (a->br[b].k > m)
            m = a->br[b].k;
    return m;
}
