/* memfn twins T-C: CONSTANT-DESCRIPTOR SPECIALIZATION.
 *
 * Question ([MEMFN] R1d): if the library is ONE header-only always_inline
 * kernel that reads a set DESCRIPTOR (shape kind + constants + tables), and
 * the emitter writes that descriptor as a `static const` struct, does gcc
 * (16) / clang at -O2 compile the call to the same code, at the same speed,
 * as the hand-specialized kernel (shapes.h)? If yes, injected text can be
 * "one kernel + one descriptor" instead of per-pattern kernel text.
 *
 * Per set, five functions computing the same find-first (all noinline, so
 * each is one symbol to disassemble):
 *   hand_X      shapes.h's hand kernel (constants in the code)
 *   desc_X      mf_find(s, n, &D_X), D_X a `static const struct mf_set`
 *   mut_X       the same with a writable EXTERNAL `struct mf_set` (the
 *               control: what another TU may write cannot be folded; a
 *               writable `static` one that nothing writes, clang folds anyway)
 *   hoist_X     mf_find_rt: the library form, descriptor at run time, the
 *               shape switch HOISTED once per call to a per-shape loop
 *   rt          ONE function for every set: descriptor at run time, the
 *               switch inside the classifier (left to the compiler)
 * `tc_asm.sh` diffs hand_X against desc_X (and mut_X) after normalizing
 * addresses and symbol names; this binary times them (--check: each against
 * the hand kernel over n 0..300, alignments, every byte value, ASan).
 */
#include "shapes.h"

enum mf_kind { MF_EQ2, MF_RANGE, MF_ACUBE, MF_CUBE, MF_NIB1, MF_NIB2 };
struct mf_set {
    int kind;
    uint8_t a, b;       /* EQ2: the bytes; RANGE: lo, span; ACUBE: care, val; CUBE: lo, care */
    uint8_t t1[16], t2[16]; /* NIB1: T; NIB2: lo, hi */
};

#if VHAVE_TBL
#define MF_TBL_CASES(v, d)                                                    \
    case MF_NIB1: return veq(vtbl(vtab((d)->t1), vand((v), vdup(0x0F))), (v)); \
    case MF_NIB2:                                                             \
        return vnz(vand(vtbl(vtab((d)->t1), vand((v), vdup(0x0F))), vtbl(vtab((d)->t2), vshr4(v))));
#else
#define MF_TBL_CASES(v, d)
#endif

INL vu8 mf_cls(vu8 v, const struct mf_set *d)
{
    switch (d->kind) {
    case MF_EQ2: return vor(veq(v, vdup(d->a)), veq(v, vdup(d->b)));
    case MF_RANGE: return vle(vsub(v, vdup(d->a)), vdup(d->b));
    case MF_ACUBE: return veq(vand(v, vdup(d->a)), vdup(d->b));
    case MF_CUBE: return veq(vand(vsub(v, vdup(d->a)), vdup(d->b)), vdup(0));
    MF_TBL_CASES(v, d)
    default: __builtin_unreachable();
    }
}
INL int mf_pred(uint8_t c, const struct mf_set *d)
{
    switch (d->kind) {
    case MF_EQ2: return c == d->a || c == d->b;
    case MF_RANGE: return (uint8_t)(c - d->a) <= d->b;
    case MF_ACUBE: return (c & d->a) == d->b;
    case MF_CUBE: return (((c - d->a) & d->b) & 0xFF) == 0;
    case MF_NIB1: return d->t1[c & 15] == c;
    case MF_NIB2: return (d->t1[c & 15] & d->t2[c >> 4]) != 0;
    default: __builtin_unreachable();
    }
}

/* the library kernel: one body, the descriptor read through d */
INL size_t mf_find(const uint8_t *s, size_t n, const struct mf_set *d)
{
#define CLS(v) mf_cls((v), d)
#define PRED(c) mf_pred((c), d)
    FIND_BODY(CLS, PRED)
#undef CLS
#undef PRED
}
/* the library's run-time entry with the switch hoisted: one loop per kind */
#define MF_KIND(K) INL size_t mf_find_##K(const uint8_t *s, size_t n, const struct mf_set *d) \
    { struct mf_set e = *d; e.kind = K; return mf_find(s, n, &e); }
MF_KIND(MF_EQ2) MF_KIND(MF_RANGE) MF_KIND(MF_ACUBE) MF_KIND(MF_CUBE)
#if VHAVE_TBL
MF_KIND(MF_NIB1) MF_KIND(MF_NIB2)
#endif
OOL size_t mf_find_rt(const uint8_t *s, size_t n, const struct mf_set *d)
{
    switch (d->kind) {
    case MF_EQ2: return mf_find_MF_EQ2(s, n, d);
    case MF_RANGE: return mf_find_MF_RANGE(s, n, d);
    case MF_ACUBE: return mf_find_MF_ACUBE(s, n, d);
    case MF_CUBE: return mf_find_MF_CUBE(s, n, d);
#if VHAVE_TBL
    case MF_NIB1: return mf_find_MF_NIB1(s, n, d);
    case MF_NIB2: return mf_find_MF_NIB2(s, n, d);
#endif
    default: return n;
    }
}
OOL size_t rt(const uint8_t *s, size_t n, const struct mf_set *d) { return mf_find(s, n, d); }

/* the hand NIB2 for \w (tables from ta_set.c's builder) */
#if VHAVE_TBL
static const uint8_t W_LO[16] = { 0x0d, 0x0f, 0x0f, 0x0f, 0x0f, 0x0f, 0x0f, 0x0f,
                                  0x0f, 0x0f, 0x0e, 0x02, 0x02, 0x02, 0x02, 0x06 };
static const uint8_t W_HI[16] = { 0x00, 0x00, 0x00, 0x01, 0x02, 0x04, 0x02, 0x08,
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
INL size_t k_w_nib2h(const uint8_t *s, size_t n)
{
    const vu8 LO = vtab(W_LO), HI = vtab(W_HI), F = vdup(0x0F);
#define CLS(v) vnz(vand(vtbl(LO, vand((v), F)), vtbl(HI, vshr4(v))))
#define PRED(c) (W_LO[(c) & 15] & W_HI[(c) >> 4])
    FIND_BODY(CLS, PRED)
#undef CLS
#undef PRED
}
#endif

/* X(name, hand kernel, descriptor initializer...) */
#define DESC_SETS_BASE(X)                                                     \
    X(q2, k_q2_shape, { MF_EQ2, '"', '\'', {0}, {0} })                        \
    X(d, k_d_shape, { MF_RANGE, '0', 9, {0}, {0} })                           \
    X(ss, k_ss_shape, { MF_ACUBE, 0xDF, 'S', {0}, {0} })                      \
    X(ab, k_ab_shape, { MF_CUBE, 'A', 0xDE, {0}, {0} })
#if VHAVE_TBL
#define DESC_SETS(X) DESC_SETS_BASE(X)                                        \
    X(sp, k_sp_shape, { MF_NIB1, 0, 0, { ' ', 0x00, 0x03, 0x02, 0x05, 0x04, 0x07, 0x06, \
                        0x09, '\t', '\n', '\v', '\f', '\r', 0x0F, 0x0E }, {0} }) \
    X(w, k_w_nib2h, { MF_NIB2, 0, 0, { 0x0d, 0x0f, 0x0f, 0x0f, 0x0f, 0x0f, 0x0f, 0x0f, \
                       0x0f, 0x0f, 0x0e, 0x02, 0x02, 0x02, 0x02, 0x06 },     \
                       { 0x00, 0x00, 0x00, 0x01, 0x02, 0x04, 0x02, 0x08 } })
#else
#define DESC_SETS(X) DESC_SETS_BASE(X)
#endif

#define GEN(N, H, ...)                                                       \
    static const struct mf_set D_##N = __VA_ARGS__;                                  \
    struct mf_set M_##N = __VA_ARGS__; /* external: another TU may write it */                                        \
    OOL size_t hand_##N(const uint8_t *s, size_t n) { return H(s, n); }       \
    OOL size_t desc_##N(const uint8_t *s, size_t n) { return mf_find(s, n, &D_##N); } \
    OOL size_t mut_##N(const uint8_t *s, size_t n) { return mf_find(s, n, &M_##N); } \
    OOL size_t hoist_##N(const uint8_t *s, size_t n) { return mf_find_rt(s, n, &D_##N); } \
    OOL size_t rt_##N(const uint8_t *s, size_t n) { return rt(s, n, &D_##N); }
DESC_SETS(GEN)

typedef size_t (*kfn)(const uint8_t *, size_t);
struct row { const char *name; kfn f[5]; const struct mf_set *d; };
static const char *const fname[5] = { "hand", "desc", "mut", "hoist", "rt" };
#define ROW(N, H, ...) { #N, { hand_##N, desc_##N, mut_##N, hoist_##N, rt_##N }, &D_##N },
static const struct row rows[] = { DESC_SETS(ROW) };
#define NR (int)(sizeof rows / sizeof rows[0])

static long g_bad, g_cases;
static int check(void)
{
    for (int r = 0; r < NR; r++)
        for (size_t n = 0; n <= 300; n++)
            for (size_t al = 0; al < 32; al += (n > 80 ? 5 : 1)) {
                uint8_t *blk = malloc(al + n + 1), *s = blk + al;
                for (int b = 0; b < 256; b++) {
                    for (size_t i = 0; i < n; i++) s[i] = (uint8_t)rng();
                    if (n) s[(size_t)b % n] = (uint8_t)b;
                    size_t want = rows[r].f[0](s, n);
                    /* the hand kernel against a byte loop over mf_pred */
                    size_t bl = n;
                    for (size_t i = 0; i < n; i++)
                        if (mf_pred(s[i], rows[r].d)) { bl = i; break; }
                    g_cases++;
                    if (want != bl && g_bad++ < 20)
                        printf("BAD %s hand n=%zu al=%zu b=%d got=%zu want=%zu\n", rows[r].name, n, al, b, want, bl);
                    for (int v = 1; v < 5; v++) {
                        size_t got = rows[r].f[v](s, n);
                        g_cases++;
                        if (got != want && g_bad++ < 20)
                            printf("BAD %s %s n=%zu al=%zu b=%d got=%zu want=%zu\n", rows[r].name,
                                   fname[v], n, al, b, got, want);
                    }
                }
                free(blk);
            }
    printf("check (" VISA "): %d sets x 5 forms, %ld cases, %ld bad\n", NR, g_cases, g_bad);
    return g_bad != 0;
}

struct tctx { kfn f; const uint8_t *s; size_t n; };
OOL static double t_once(const void *ctx, long reps)
{
    const struct tctx *c = ctx;
    size_t acc = 0;
    double t0 = now_ns();
    for (long r = 0; r < reps; r++) {
        const uint8_t *s = c->s;
        __asm__ volatile("" : "+r"(s));
        acc += c->f(s, c->n);
    }
    __asm__ volatile("" : : "r"(acc));
    return now_ns() - t0;
}

int main(int argc, char **argv)
{
    for (int a = 1; a < argc; a++) {
        if (!strcmp(argv[a], "--check")) return check();
        if (!strcmp(argv[a], "--quick")) g_min_loop_ns = 5e6;
    }
    static const size_t spans[] = { 16, 64, 256, 1024, 4096, 65536 };
    uint8_t *buf = aligned_alloc(64, 65536);
    printf("# memfn twins T-C (constant descriptor vs hand kernel), vec=%s VW=%d\n", VISA, VW);
    printf("# ns per call (noinline, miss: the whole span read), min of %d loops >= %.0f ms\n",
           REPEATS, g_min_loop_ns / 1e6);
    printf("%-4s %-6s", "set", "form");
    for (size_t j = 0; j < sizeof spans / sizeof spans[0]; j++) printf(" %10zu", spans[j]);
    printf("\n");
    for (int r = 0; r < NR; r++) {
        for (size_t i = 0; i < 65536; i++) { /* a non-member background */
            uint8_t c = (uint8_t)(0x21 + (i * 7) % 94);
            while (mf_pred(c, rows[r].d)) c = (uint8_t)(c + 1 > 0x7E ? 0x21 : c + 1);
            buf[i] = c;
        }
        for (int v = 0; v < 5; v++) {
            printf("%-4s %-6s", rows[r].name, fname[v]);
            for (size_t j = 0; j < sizeof spans / sizeof spans[0]; j++) {
                struct tctx c = { rows[r].f[v], buf, spans[j] };
                double lo, hi;
                tmeasure(t_once, &c, &lo, &hi);
                printf(" %10.2f", lo);
                fflush(stdout);
            }
            printf("\n");
        }
    }
    return 0;
}
