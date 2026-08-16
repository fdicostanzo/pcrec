#include "matcher.h"

/* Hand-written references. */
extern const char *find_hello_scalar(const char *hay, size_t n);
extern const char *find_hello_avx2_bcast(const char *hay, size_t n);
extern const char *find_hello_avx2_fl(const char *hay, size_t n);

/* Template instantiations from cand_gen.c. The pattern/ci pair on each row
 * below must describe exactly the member sets compiled into the function;
 * the harness oracle compares against pat_scan() of that pair. */
extern const char *find_gen_do(const char *hay, size_t n);
extern const char *find_gen_wolf(const char *hay, size_t n);
extern const char *find_gen_backfire(const char *hay, size_t n);
extern const char *find_gen_k16(const char *hay, size_t n);
extern const char *find_gen_k32(const char *hay, size_t n);
extern const char *find_gen_h3ll0w9(const char *hay, size_t n);
extern const char *find_ci_hello_or(const char *hay, size_t n);
extern const char *find_ci_backfire(const char *hay, size_t n);
extern const char *find_ci_h3ll0w9(const char *hay, size_t n);
extern const char *find_ci_hello_fold(const char *hay, size_t n);
extern const char *find_ci_backfire_fold(const char *hay, size_t n);
extern const char *find_ci_h3ll0w9_fold(const char *hay, size_t n);
extern const char *find_cls_abcdgh(const char *hay, size_t n);
extern const char *find_cls_digits(const char *hay, size_t n);

/* Range and arbitrary-set idioms from cand_range.c / cand_shufti.c. */
extern const char *find_rng_digits(const char *hay, size_t n);
extern const char *find_shufti_scatter(const char *hay, size_t n);

/* Alternation: per-branch masks OR-ed over shared loads, from cand_alt.c. */
extern const char *find_alt_names(const char *hay, size_t n);
extern const char *find_alt_mixed(const char *hay, size_t n);
extern const char *find_alt_plus(const char *hay, size_t n);

/* Prefiltered alternation: union-class filter then full evaluation, from
 * cand_alt_pf.c. */
extern const char *find_alt_names_pf1(const char *hay, size_t n);
extern const char *find_alt_names_pf3(const char *hay, size_t n);
extern const char *find_alt_mixed_pf(const char *hay, size_t n);

/* 128-bit SSE ports of the AVX2 candidates above, from cand_sse.c; each row
 * here pairs with the 256-bit row of the same algorithm for the width A/B. */
extern const char *find_sse_hello(const char *hay, size_t n);
extern const char *find_sse_wolf(const char *hay, size_t n);
extern const char *find_sse_backfire(const char *hay, size_t n);
extern const char *find_sse_k16(const char *hay, size_t n);
extern const char *find_sse_ci_hello(const char *hay, size_t n);
extern const char *find_sse_rng_digits(const char *hay, size_t n);
extern const char *find_sse_shufti(const char *hay, size_t n);
extern const char *find_sse_alt_pf3(const char *hay, size_t n);

/* Established-optimization studies: rare-position selection (cand_rare.c),
 * blockwise shift-and (cand_shiftand.c), Teddy vs union prefilter at eight
 * branches (cand_teddy.c). */
extern const char *find_enzyme_chain(const char *hay, size_t n);
extern const char *find_enzyme_fl(const char *hay, size_t n);
extern const char *find_enzyme_rare2(const char *hay, size_t n);
extern const char *find_backfire_shiftand(const char *hay, size_t n);
extern const char *find_k16_shiftand(const char *hay, size_t n);
extern const char *find_alt8_union(const char *hay, size_t n);
extern const char *find_alt8_teddy(const char *hay, size_t n);

/* Software-prefetch distance study (cand_prefetch.c): enzyme_rare2 + one
 * prefetcht0 per block at +512/+1024/+4096. */
extern const char *find_enzyme_pf512(const char *hay, size_t n);
extern const char *find_enzyme_pf1024(const char *hay, size_t n);
extern const char *find_enzyme_pf4096(const char *hay, size_t n);

const matcher MATCHERS[] = {
    /* name              pattern                             ci  fn                      avx2 */
    { "scalar",          "hello",                            0, find_hello_scalar,        0 },
    { "avx2_bcast",      "hello",                            0, find_hello_avx2_bcast,    1 },
    { "avx2_firstlast",  "hello",                            0, find_hello_avx2_fl,       1 },

    /* generated, exact: the needle-length axis */
    { "gen_do",          "do",                               0, find_gen_do,              1 },
    { "gen_wolf",        "wolf",                             0, find_gen_wolf,            1 },
    { "gen_backfire",    "backfire",                         0, find_gen_backfire,        1 },
    { "gen_k16",         "incomprehensible",                 0, find_gen_k16,             1 },
    { "gen_k32",         "thequickbrownfoxjumpsoverthelazy", 0, find_gen_k32,             1 },
    { "gen_h3ll0w9",     "h3ll0_w9",                         0, find_gen_h3ll0w9,         1 },

    /* generated, case-insensitive by OR-ing the case twins */
    { "ci_hello_or",     "hello",                            1, find_ci_hello_or,         1 },
    { "ci_backfire",     "backfire",                         1, find_ci_backfire,         1 },
    { "ci_h3ll0w9",      "h3ll0_w9",                         1, find_ci_h3ll0w9,          1 },

    /* generated, case-insensitive by folding the haystack block */
    { "ci_hello_fold",   "hello",                            1, find_ci_hello_fold,       1 },
    { "ci_backfire_fold","backfire",                         1, find_ci_backfire_fold,    1 },
    { "ci_h3ll0w9_fold", "h3ll0_w9",                         1, find_ci_h3ll0w9_fold,     1 },

    /* generated, multi-member character classes */
    { "cls_abcdgh",      "[ab][cd]gh",                       0, find_cls_abcdgh,          1 },
    { "cls_digits",      "[0369][0369]zz",                   0, find_cls_digits,          1 },

    /* contiguous range via saturating subtract; scattered set via pshufb */
    { "rng_digits",      "[0123456789][0123456789]px",       0, find_rng_digits,          1 },
    { "shufti_scatter",  "[aeiou0369_]zq",                   0, find_shufti_scatter,      1 },

    /* alternation: OR of per-branch masks over one set of shared loads */
    { "alt_names",       "fred|bob|janet|frederick",         0, find_alt_names,           1 },
    { "alt_mixed",       "bob|[0123456789]{5}|ted",          0, find_alt_mixed,           1 },
    { "alt_plus",        "bob|[0123456789]+|ted",            0, find_alt_plus,            1 },

    /* prefilter variants: derived union-class filter, then full evaluation */
    { "alt_names_pf1",   "fred|bob|janet|frederick",         0, find_alt_names_pf1,       1 },
    { "alt_names_pf3",   "fred|bob|janet|frederick",         0, find_alt_names_pf3,       1 },
    { "alt_mixed_pf",    "bob|[0123456789]{5}|ted",          0, find_alt_mixed_pf,        1 },

    /* 128-bit SSE (SSSE3-max) ports for the width A/B -- needs_avx2=0; SSSE3
     * assumed present on all test hardware */
    { "sse_hello",       "hello",                            0, find_sse_hello,           0 },
    { "sse_wolf",        "wolf",                             0, find_sse_wolf,            0 },
    { "sse_backfire",    "backfire",                         0, find_sse_backfire,        0 },
    { "sse_k16",         "incomprehensible",                 0, find_sse_k16,             0 },
    { "sse_ci_hello",    "hello",                            1, find_sse_ci_hello,        0 },
    { "sse_rng_digits",  "[0123456789][0123456789]px",       0, find_sse_rng_digits,      0 },
    { "sse_shufti",      "[aeiou0369_]zq",                   0, find_sse_shufti,          0 },
    { "sse_alt_pf3",     "fred|bob|janet|frederick",         0, find_sse_alt_pf3,         0 },

    /* established-optimization studies */
    { "enzyme_chain",    "enzyme",                           0, find_enzyme_chain,        1 },
    { "enzyme_fl",       "enzyme",                           0, find_enzyme_fl,           1 },
    { "enzyme_rare2",    "enzyme",                           0, find_enzyme_rare2,        1 },
    { "backfire_sa",     "backfire",                         0, find_backfire_shiftand,   1 },
    { "k16_sa",          "incomprehensible",                 0, find_k16_shiftand,        1 },
    { "alt8_union",  "fred|bob|janet|frederick|alice|megan|carol|dave", 0, find_alt8_union, 1 },
    { "alt8_teddy",  "fred|bob|janet|frederick|alice|megan|carol|dave", 0, find_alt8_teddy, 1 },

    /* software-prefetch distance study */
    { "enzyme_pf512",    "enzyme",                           0, find_enzyme_pf512,        1 },
    { "enzyme_pf1024",   "enzyme",                           0, find_enzyme_pf1024,       1 },
    { "enzyme_pf4096",   "enzyme",                           0, find_enzyme_pf4096,       1 },
};
const int N_MATCHERS = sizeof MATCHERS / sizeof MATCHERS[0];
