/* tests/callouts/behaviors.h — the callout BEHAVIOURS the callouts tests
 * bind ([INLINE-C] stage 1b; docs/spec/match_api.md §11).
 *
 * A behaviour is a PURE function of what a callee is shown (the subject, the
 * position, the capture view): match_api.md §11.6's defined answer exists
 * only for such a callee, so every test binding is one. The table below is
 * the ONE definition both sides read: `stubs.c` binds each row as an
 * `rx_matchfn` for pcrec's artifacts, and `co_oracle.c` calls the same row
 * from a libpcre2 callout. Sharing it is not the control sharing a source
 * with what it controls: the behaviour is the test's INPUT (the user's
 * code), and the two matchers under comparison share nothing else.
 *
 * Return values are pcrec's (match_api.md §11.4): 0 passes, -1 fails the
 * path, k > 0 consumes k bytes (a `consume` row only). A `consume` row has
 * no libpcre2 callout form, so it carries `pcre2_equiv`, the pattern text
 * that matches what it consumes, and the oracle splices that in its place.
 *
 * NUMBERED callouts: `rx_callout_<n>` binds check row `n % CO_NCHECK`, so a
 * test that wants a behaviour on a numbered site picks the number. */
#ifndef TESTS_CALLOUTS_BEHAVIORS_H
#define TESTS_CALLOUTS_BEHAVIORS_H

#include <stddef.h>

/* The view, as both sides hand it over. */
typedef struct {
    const unsigned char *s;
    size_t len, pos, ncap;
    const ptrdiff_t (*caps)[2];
} CoView;

typedef ptrdiff_t (*co_beh)(const CoView *v);

static inline int co_g_set(const CoView *v, size_t g)
{
    return g < v->ncap && v->caps[g][0] >= 0;
}

static inline ptrdiff_t co_pass(const CoView *v)  { (void)v; return 0; }
static inline ptrdiff_t co_veto(const CoView *v)  { (void)v; return -1; }
/* `odd` vetoes an odd position, `even` an even one */
static inline ptrdiff_t co_odd(const CoView *v)   { return (v->pos & 1) ? -1 : 0; }
static inline ptrdiff_t co_even(const CoView *v)  { return (v->pos & 1) ? 0 : -1; }
/* vetoes the attempt that began at offset 0 */
static inline ptrdiff_t co_vetostart(const CoView *v) { return v->caps[0][0] == 0 ? -1 : 0; }
/* passes only once group 1 has closed */
static inline ptrdiff_t co_g1set(const CoView *v) { return co_g_set(v, 1) ? 0 : -1; }
/* vetoes a closed group 1 of odd length */
static inline ptrdiff_t co_g1even(const CoView *v)
{
    if (!co_g_set(v, 1)) return 0;
    return ((v->caps[1][1] - v->caps[1][0]) & 1) ? -1 : 0;
}
/* passes only right after an `a` */
static inline ptrdiff_t co_aftera(const CoView *v)
{
    return v->pos > 0 && v->s[v->pos - 1] == 'a' ? 0 : -1;
}
/* passes only at the subject's end */
static inline ptrdiff_t co_atend(const CoView *v) { return v->pos == v->len ? 0 : -1; }
/* vetoes when the next byte is `b` */
static inline ptrdiff_t co_notb(const CoView *v)
{
    return v->pos < v->len && v->s[v->pos] == 'b' ? -1 : 0;
}
/* vetoes when the attempt has consumed exactly one byte */
static inline ptrdiff_t co_notone(const CoView *v)
{
    return (ptrdiff_t)v->pos - v->caps[0][0] == 1 ? -1 : 0;
}

/* D1/P7/P10: passes while group 1, read as a decimal, is at most 255 */
static inline ptrdiff_t co_le255(const CoView *v)
{
    if (!co_g_set(v, 1)) return -1;
    long n = 0;
    for (ptrdiff_t k = v->caps[1][0]; k < v->caps[1][1]; k++) {
        if (v->s[k] < '0' || v->s[k] > '9') return -1;
        if ((n = n * 10 + (v->s[k] - '0')) > 255) return -1;
    }
    return 0;
}
/* D2: passes only when group 1 is the text `ab` */
static inline ptrdiff_t co_g1ab(const CoView *v)
{
    return co_g_set(v, 1) && v->caps[1][1] - v->caps[1][0] == 2 &&
           v->s[v->caps[1][0]] == 'a' && v->s[v->caps[1][0] + 1] == 'b' ? 0 : -1;
}

/* consumers */
static inline ptrdiff_t co_two(const CoView *v) { return v->pos + 2 <= v->len ? 2 : -1; }
static inline ptrdiff_t co_digits(const CoView *v)
{
    size_t k = v->pos;
    while (k < v->len && v->s[k] >= '0' && v->s[k] <= '9') k++;
    return (ptrdiff_t)(k - v->pos);
}
static inline ptrdiff_t co_onea(const CoView *v)
{
    return v->pos < v->len && v->s[v->pos] == 'a' ? 1 : -1;
}

typedef struct {
    const char *name;
    co_beh fn;
    const char *pcre2_equiv;   /* consumers: the spliced equivalent; NULL: a check */
} CoBehRow;

/* Checks first: a numbered callout `n` binds row `n % CO_NCHECK`. */
#define CO_NCHECK 13
static const CoBehRow co_rows[] = {
    { "pass",      co_pass,      NULL },
    { "veto",      co_veto,      NULL },
    { "odd",       co_odd,       NULL },
    { "even",      co_even,      NULL },
    { "vetostart", co_vetostart, NULL },
    { "g1set",     co_g1set,     NULL },
    { "g1even",    co_g1even,    NULL },
    { "aftera",    co_aftera,    NULL },
    { "atend",     co_atend,     NULL },
    { "notb",      co_notb,      NULL },
    { "notone",    co_notone,    NULL },
    { "le255",     co_le255,     NULL },
    { "g1ab",      co_g1ab,      NULL },
    { "two",       co_two,       "(?s:..)" },
    { "digits",    co_digits,    "(?>[0-9]*)" },
    { "onea",      co_onea,      "a" },
};
#define CO_NROWS (sizeof co_rows / sizeof co_rows[0])

#endif
