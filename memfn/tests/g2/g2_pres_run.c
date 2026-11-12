/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2's presence family,
 *   lane k382a, R-38 K38-2a).
 *
 * memfn/tests/g2/g2_pres_run.c — G2'S PRESENCE FAMILY, THE DRIVER, over the
 * text g2_pres_gen.c rendered (OUT/g2p_sites.c, linked in; g2_pres.h's
 * table). It never links the kit: its expectations are the run AS GENERATED
 * (the positions' sets), its stated omin and K, and the kit's reply AS
 * NUMBERS (mf_class.run: FAM-2, span_runs_sheet.md §5 K38-2 PLAN (c)); what
 * it measures is the RENDERED TEXT, by behaviour and by the reads it makes.
 * Since R-38 K38-2 a site lays out ONE run part, the one the kit derives; its
 * candidate is the run occurrence's position 0, so the part is measured in
 * the RUN frame (positions [0, run_len)), and the reply's extent may be
 * partial (P3's).
 *
 *   THE TEXT CLASSIFIER (span_runs_sheet.md §2.4 C2), per run part, from its
 *   text alone (a direct call of the part, g2p_part_<id>_<k>):
 *     COVER   every member of every position's set, placed at the position
 *             in an occurrence above `lo`, is found (so the find's byte set
 *             CONTAINS the scan's set: a superset, or an ANDed second
 *             position, still finds every occurrence);
 *     EXTENT  the positions the text COMPARES are exactly the reply's
 *             verified extent [ver_lo, ver_lo + ver_len): an occurrence
 *             broken at a position inside it is not yielded, one broken
 *             outside it still is (so a reply that claims a position the
 *             text does not compare, C2's decision plant, reds here); and
 *             each compare is EXACT:
 *             every member of a verified position with one bit flipped to
 *             a byte outside the position's set (a NEAR-MISS) breaks the
 *             occurrence (review 2026-11-10 r2 k382a FAM-3: the filler
 *             differs from a member in the bits it happens to, so a
 *             compare one bit looser still rejected it);
 *     SCAN    the text's find reads the reply's scan position first (the
 *             first subject read on a subject with no candidate, short
 *             enough for the scalar body: a SIMD arm may load an ANDed
 *             second position first, so it is held to COVER; part frame,
 *             then site frame);
 *     SOUND   a yielded candidate lies at or above `lo`, its verified extent
 *             inside the subject, and holds every compared position
 *             (subjects carry near-miss occurrences too, FAM-3).
 *   (C2's third clause, no run part where the link is untested, is the
 *   generator's: its P2 control.)
 *   THE LEVER WITNESSES (plant C): the text's scan on an all-tie run of
 *   distinct bytes is the STATED rule's position (incumbent rightmost; under
 *   run-tie-left leftmost); `G2PW` lines let the runner show it moved.
 *   THE ORACLE SEAM (G2P_REC builds): every call of a run part through the
 *   site's ENTRY or RE-ENTRY use (g2p_rec) writes one record in exactly the
 *   format of docs/dev/lanes/k382a_oracle_iface.md, taken at the CALLER
 *   boundary (review 2026-11-10 r2 k382a ORC-1): subject, length and origin
 *   are the host's, as uses() handed them to the use (the attempt start, the
 *   stated omin off the site table), never the arguments the kit's text
 *   passed its part, and the result is in the host's frame; so a use that
 *   moves its part's floor or subject is checked against the attempt, not
 *   against itself. `reads` are the subject offsets the part read in
 *   [-PAD, n + PAD) of the host's subject (a read further out is not
 *   recorded: layouts U and L fault on it), from the compiler's own
 *   instrumentation of the kit's text (-fsanitize=kernel-address with every
 *   access an outlined call: the __asan_* callbacks below) and the libc
 *   reads (memchr, memcmp, memcpy, routed here by g2p_sites.c's G2P_REC
 *   block).
 *   ORC-3 (§5 K38-2 PLAN (d)): the records are in the RUN frame (the part's
 *   `at` is 0: the candidate is run position 0, so the floor asked is run
 *   position 0's), carry the site's REPLY (its ver_lo/ver_len), and the
 *   stated omin of either sign; the runner floors the hits whose verified
 *   extent is PARTIAL (`partial_hits`), the records with a negative omin and
 *   the hits BELOW the attempt start.
 *   THE §3.5 WITNESSES (W-L1 a/b, W-K1, W-K2): fixed sites and subjects, the
 *   expected candidate GENERATED from the stated rule (§3.3: floor = max(0,
 *   origin + omin), the least whole-run occurrence at or after it, the
 *   extent whole) and held equal to the sheet's literal; each states its
 *   reach (the floor below the origin; W-L1b's scan byte below it).
 *   THE LAYOUTS (§3.5 W-K4): U, a guard page at s + n; L, the subject at a
 *   page start with a guard page below (W-K4a's: every site, the negative
 *   omin ones with the origin below -omin half the time, counted); and, in
 *   the ASan build (G2P_ASAN), A, the subject at offset 1..W-1 from a
 *   W-aligned heap block (W 16 and 32), the block's bytes below the subject
 *   poisoned (W-K4b's). A fault is a failure.
 *
 *   g2p_run [--records FILE] [--seed N]
 */
#define _GNU_SOURCE
#include <setjmp.h>
#include <stdarg.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#include "g2_pres.h"

#ifdef G2P_ASAN
#include <sanitizer/asan_interface.h>
#endif

static long g_pass, g_fail;
static unsigned long long g_rng = 0x67327072ull, g_rng2 = 0x6e6d6973ull;
static unsigned rnd(unsigned n)
{
    g_rng = g_rng * 6364136223846793005ull + 1442695040888963407ull;
    return n ? (unsigned)((g_rng >> 33) % n) : 0;
}
/* the near-misses' own stream (FAM-3), so the probes before them draw what
   they drew without it */
static unsigned rnd2(unsigned n)
{
    g_rng2 = g_rng2 * 6364136223846793005ull + 1442695040888963407ull;
    return n ? (unsigned)((g_rng2 >> 33) % n) : 0;
}

static void failf(const g2p_site *x, const char *what, const char *fmt, ...)
    __attribute__((format(printf, 3, 4)));
static void failf(const g2p_site *x, const char *what, const char *fmt, ...)
{
    va_list ap;
    if (++g_fail > 60) return;
    printf("FAIL %s site %d (%s): %s: ", x->tag, x->id, x->forms, what);
    va_start(ap, fmt);
    vprintf(fmt, ap);
    va_end(ap);
    putchar('\n');
}
#define CHECK(x, cond, what, ...) \
    do { if (cond) g_pass++; else failf((x), (what), __VA_ARGS__); } while (0)

/* ---- the run as generated ---------------------------------------------------- */

static int in_set(const g2p_site *x, unsigned j, unsigned b)
{
    return (b & x->mask[j]) == x->run[j];
}
static unsigned members(const g2p_site *x, unsigned j, unsigned m[2])
{
    unsigned k = 0;
    m[k++] = x->run[j];
    if (x->mask[j] != 0xFF) m[k++] = x->run[j] | (~x->mask[j] & 0xFF);
    return k;
}
/* a byte in no position's set (the filler) */
static unsigned filler(const g2p_site *x)
{
    for (unsigned b = 1; b < 256; b++) {
        int any = 0;
        for (unsigned j = 0; j < x->run_len && !any; j++) any = in_set(x, j, b);
        if (!any) return b;
    }
    return 0;
}

/* ---- the reads (instrumentation) -------------------------------------------- */

#define PAD 64
static int g_active;                     /* inside a measured part call */
static const unsigned char *g_sb;        /* the subject              */
static size_t g_sn;
static int g_first;                      /* the first subject read's offset */
static long g_nreads;
static unsigned g_gen, g_stamp[512 + 2 * PAD];

static void rd(const void *p, size_t size)
{
    if (!g_active) return;
    const unsigned char *a = p;
    for (size_t i = 0; i < size; i++) {
        long o = (long)(a + i - g_sb);
        if (o < -PAD || o >= (long)g_sn + PAD) continue;    /* not the subject's */
        if (g_first == INT32_MIN) g_first = (int)o;
        if (g_stamp[o + PAD] != g_gen) { g_stamp[o + PAD] = g_gen; g_nreads++; }
    }
}
static void rd_begin(const unsigned char *s, size_t n)
{
    g_sb = s; g_sn = n; g_first = INT32_MIN; g_nreads = 0;
    if (++g_gen == 0) { memset(g_stamp, 0, sizeof g_stamp); g_gen = 1; }
    g_active = 1;
}

#ifdef G2P_REC
/* the compiler's outlined access checks (-fsanitize=kernel-address,
   asan-instrumentation-with-call-threshold=0): the kit text's every load */
static long g_vec;                       /* vector loads (>= 16 bytes) of the subject */
static void rdv(const void *p, size_t n)
{
    if (g_active && n >= 16 && (const unsigned char *)p >= g_sb - PAD &&
        (const unsigned char *)p < g_sb + g_sn + PAD)
        g_vec++;
    rd(p, n);
}
#define LD(N) void __asan_load##N##_noabort(void *p) { rdv(p, N); } \
              void __asan_store##N##_noabort(void *p) { (void)p; }
LD(1) LD(2) LD(4) LD(8) LD(16)
void __asan_loadN_noabort(void *p, size_t n) { rdv(p, n); }
void __asan_storeN_noabort(void *p, size_t n) { (void)p; (void)n; }
void __asan_handle_no_return(void) {}
void *g2p_memchr(const void *p, int c, size_t n)
{
    const unsigned char *q = memchr(p, c, n);
    rd(p, q ? (size_t)(q - (const unsigned char *)p) + 1 : n);
    return (void *)q;
}
int g2p_memcmp(const void *a, const void *b, size_t n) { rd(a, n); rd(b, n); return memcmp(a, b, n); }
void *g2p_memcpy(void *d, const void *s, size_t n) { rd(s, n); return memcpy(d, s, n); }
#endif

/* ---- the oracle seam: the records ------------------------------------------- */

static FILE *g_rec;
static const char *g_call;               /* "entry" / "reentry" while a use runs */
static const g2p_site *g_site_of[1 << 12];
static long g_reach[G2P_NROUTE][2], g_records;
static long g_partial_hits, g_neg_records, g_below_hits;   /* ORC-3's populations */
/* THE CALLER BOUNDARY (ORC-1): the host's subject, length and attempt start,
   set by uses() before it calls the use */
static const unsigned char *g_hs;
static size_t g_hn, g_hlo;

size_t g2p_rec(int site, int part, g2p_part_fn fn, const unsigned char *s, size_t n, size_t lo)
{
    if (g_active || !g_call) return fn(s, n, lo);
    const g2p_site *x = g_site_of[site];
    rd_begin(g_hs, g_hn);                /* reads in the host's frame */
    size_t r = fn(s, n, lo);
    g_active = 0;
    g_reach[x->route][g_call[0] == 'r']++;
    if (!g_rec) return r;
    const g2p_part *pt = &x->parts[part];
    fprintf(g_rec, "%s.%d.p%d\t%s\t", x->tag, x->id, part, g_call);
    for (size_t i = 0; i < g_hn; i++) fprintf(g_rec, "%02x", g_hs[i]);
    fprintf(g_rec, "\t%zu\t%d\t", g_hlo, (int)x->omin);
    for (unsigned j = 0; j < pt->len; j++) {
        unsigned jj = pt->at + j;
        if (j) fputc(',', g_rec);
        for (int d = 63; d >= 0; d--) {             /* digit 63 - d holds bytes 4d..4d+3 */
            unsigned v = 0;
            for (unsigned k = 0; k < 4; k++) v |= (unsigned)in_set(x, jj, 4u * (unsigned)d + k) << k;
            fputc("0123456789abcdef"[v], g_rec);
        }
    }
    fprintf(g_rec, "\t%u\t%u\t", pt->ver_lo, pt->ver_len);
    /* the part's hit is an offset from ITS `s`: the record's is the host's */
    if (r < n) {
        ptrdiff_t c = (s + r) - g_hs;
        fprintf(g_rec, "%td\t", c);
        if (pt->ver_len < x->run_len) g_partial_hits++;
        if (c < (ptrdiff_t)g_hlo) g_below_hits++;
    } else fputs("MISS\t", g_rec);
    if (x->omin < 0) g_neg_records++;
    int first = 1;
    for (long o = -PAD; o < (long)g_hn + PAD; o++)
        if (g_stamp[o + PAD] == g_gen) { fprintf(g_rec, "%s%ld", first ? "" : ",", o); first = 0; }
    fputc('\n', g_rec);
    g_records++;
    return r;
}

/* ---- the layouts --------------------------------------------------------------- */

static long g_page;
static unsigned char *g_map;             /* three pages: guard, data, guard */
static sigjmp_buf g_jb;
static volatile int g_faulted;
static void on_fault(int sig) { (void)sig; g_faulted = 1; siglongjmp(g_jb, 1); }

enum { LAY_U, LAY_L, LAY_N };
static const char *lay_name[] = { "U (guard at s + n)", "L (subject at a page start, guard below)" };

/* the subject placed for layout `lay`, copied from `src` */
static unsigned char *place(int lay, const unsigned char *src, size_t n)
{
    unsigned char *data = g_map + g_page;
    unsigned char *s = lay == LAY_U ? data + g_page - n : data;
    memcpy(s, src, n);
    return s;
}

/* ---- the checks ------------------------------------------------------------------ */

static long g_cover, g_extent, g_scan, g_sound, g_witness, g_lay_calls[LAY_N], g_wk4_low, g_generic;
static long g_nearmiss, g_nm_sound, g_nm_uses;   /* FAM-3's probes, counted */
static long g_scan_route[G2P_NROUTE];

/* one direct call of part `pt` at `lo` on `src` (layout U), measured */
static size_t measure(const g2p_part *pt, const unsigned char *src, size_t n, size_t lo, int *first)
{
    unsigned char *s = place(LAY_U, src, n);
    rd_begin(s, n);
    size_t r = pt->fn(s, n, lo);
    g_active = 0;
    if (first) *first = g_first;
    return r;
}

/* 1 iff `buf` holds part `pt`'s verified extent with its position 0 at `c`
 * (inside the subject of `n`) */
static int holds_extent(const g2p_site *x, const g2p_part *pt, const unsigned char *buf, size_t n,
                        size_t c)
{
    if (c + pt->ver_lo + pt->ver_len > n) return 0;
    for (unsigned j = pt->ver_lo; j < pt->ver_lo + pt->ver_len; j++)
        if (!in_set(x, pt->at + j, buf[c + j])) return 0;
    return 1;
}

/* The part's first candidate at or after `gap` from `lo`: a PARTIAL extent
 * may legally yield an earlier candidate (an occurrence's own stretch shifted
 * onto repeated positions holds the extent), so each candidate below `gap`
 * must hold the extent and the part is asked again past it. *bad 1: a
 * candidate below `gap` that does not hold the extent (SOUND's matter). */
static size_t first_from(const g2p_site *x, const g2p_part *pt, const unsigned char *buf, size_t n,
                         size_t lo, size_t gap, int *bad)
{
    size_t r;
    *bad = 0;
    while ((r = measure(pt, buf, n, lo, NULL)) < gap) {
        if (!holds_extent(x, pt, buf, n, r)) {
            *bad = 1;
            failf(x, "SOUND", "part at %u len %u: lo %zu n %zu yielded %zu, which does not hold "
                  "the verified extent [%u, %u)", pt->at, pt->len, lo, n, r, pt->ver_lo,
                  pt->ver_lo + pt->ver_len);
            return r;
        }
        lo = r + 1;
    }
    return r;
}

/* an occurrence of part `pt` at `c` in `buf`, each position a random member */
static void occ_r(const g2p_site *x, const g2p_part *pt, unsigned char *buf, size_t c,
                  unsigned (*r)(unsigned))
{
    for (unsigned j = 0; j < pt->len; j++) {
        unsigned m[2], k = members(x, pt->at + j, m);
        buf[c + j] = (unsigned char)m[r(k)];
    }
}
static void occ(const g2p_site *x, const g2p_part *pt, unsigned char *buf, size_t c)
{
    occ_r(x, pt, buf, c, rnd);
}

/* A NEAR-MISS occurrence of part `pt` at `c` (FAM-3, rnd2's stream): an
 * occurrence with one position of [vlo, vlo + vlen) a member with one bit
 * flipped to a byte outside that position's set; 0 where the drawn
 * position's every flip stays in its set (no near-miss there) */
static int near_occ(const g2p_site *x, const g2p_part *pt, unsigned vlo, unsigned vlen,
                    unsigned char *buf, size_t c)
{
    if (!vlen) return 0;
    occ_r(x, pt, buf, c, rnd2);
    unsigned j = vlo + rnd2(vlen), m[2], k = members(x, pt->at + j, m), b = m[rnd2(k)];
    for (unsigned t = 0, bit = rnd2(8); t < 8; t++, bit = (bit + 1) & 7)
        if (!in_set(x, pt->at + j, b ^ (1u << bit))) {
            buf[c + j] = (unsigned char)(b ^ (1u << bit));
            return 1;
        }
    return 0;
}

/* The classifier over one part; returns its measured extent [*lo, *hi) and
 * scan in part frame. */
static void classify(const g2p_site *x, const g2p_part *pt, int *ext_lo, int *ext_hi, int *scan)
{
    unsigned char buf[256];
    unsigned F = filler(x), len = pt->len;
    *ext_lo = -1; *ext_hi = -1;
    /* COVER: every member of every position, the occurrence strictly above lo */
    for (unsigned j = 0; j < len; j++) {
        unsigned m[2], k = members(x, pt->at + j, m);
        for (unsigned i = 0; i < k; i++)
            for (int v = 0; v < 3; v++) {     /* ending at n; short; long (a SIMD arm's) */
                size_t gap = 1 + rnd(v == 2 ? 70 : 12), lo = rnd((unsigned)gap);
                size_t n = gap + len + (v == 0 ? 0 : v == 1 ? rnd(9) : rnd(40));
                memset(buf, (int)F, n);
                occ(x, pt, buf, gap);
                buf[gap + j] = (unsigned char)m[i];
                int bad;
                size_t r = first_from(x, pt, buf, n, lo, gap, &bad);
                g_cover++;
                CHECK(x, r == gap, "COVER", "part at %u len %u: member 0x%02x at position %u "
                      "(occurrence at %zu, lo %zu, n %zu) yielded %zu", pt->at, len, m[i], j, gap, lo, n, r);
            }
    }
    /* EXTENT: an occurrence broken at j is yielded iff j is not compared */
    for (unsigned jv = 0; jv < 2 * len; jv++) {      /* each position short, then long */
        unsigned j = jv % len;
        size_t gap = 1 + rnd(jv < len ? 12 : 70), n = gap + len + rnd(jv < len ? 9 : 40),
               lo = rnd((unsigned)gap);
        memset(buf, (int)F, n);
        occ(x, pt, buf, gap);
        buf[gap + j] = (unsigned char)F;
        int bad;
        size_t r = first_from(x, pt, buf, n, lo, gap, &bad);
        int compared = r != gap;
        if (compared) { if (*ext_lo < 0) *ext_lo = (int)j; *ext_hi = (int)j + 1; }
        int want = (int)j >= (int)pt->ver_lo && j < pt->ver_lo + pt->ver_len;
        g_extent++;
        CHECK(x, compared == want, "EXTENT", "part at %u len %u: position %u %s compared, the "
              "reply's stretch is [%u, %u)", pt->at, len, j, compared ? "IS" : "is NOT",
              pt->ver_lo, pt->ver_lo + pt->ver_len);
    }
    /* EXTENT, EXACT (FAM-3): each member of each verified position, each bit
       flipped where that leaves the position's set (a flip of a masked bit is
       still a member), placed in an otherwise whole occurrence: not yielded */
    for (unsigned j = pt->ver_lo; j < pt->ver_lo + pt->ver_len; j++) {
        unsigned m[2], k = members(x, pt->at + j, m);
        for (unsigned i = 0; i < k; i++)
            for (unsigned bit = 0; bit < 8; bit++) {
                unsigned nm = m[i] ^ (1u << bit);
                if (in_set(x, pt->at + j, nm)) continue;
                size_t gap = 1 + rnd2(12), n = gap + len + rnd2(9), lo = rnd2((unsigned)gap);
                memset(buf, (int)F, n);
                occ_r(x, pt, buf, gap, rnd2);
                buf[gap + j] = (unsigned char)nm;
                int bad;
                size_t r = first_from(x, pt, buf, n, lo, gap, &bad);
                g_nearmiss++;
                CHECK(x, r != gap, "EXTENT", "part at %u len %u: a near-miss 0x%02x (member 0x%02x, "
                      "bit %u) at verified position %u is yielded as an occurrence (lo %zu, n %zu)",
                      pt->at, len, nm, m[i], bit, j, lo, n);
            }
    }
    /* SCAN: the text's first read on a subject with no candidate, short
       enough (len + 2) that the selector takes the scalar body: a SIMD arm's
       find may load an ANDed second position first (C2 allows the AND; its
       order is the compiler's), so the arms are held to COVER alone */
    size_t n = len + 2;
    memset(buf, (int)F, n);
    measure(pt, buf, n, 0, scan);
#ifdef G2P_REC
    g_scan++;
    CHECK(x, *scan == pt->member, "SCAN", "part at %u len %u: the text's find reads position "
          "%d first, the reply's scan is %d", pt->at, len, *scan, pt->member);
#endif
    /* SOUND: random subjects over the run's own bytes and the filler */
    for (int t = 0; t < 24; t++) {
        n = rnd(len + (t & 1 ? 120 : 30));
        for (size_t i = 0; i < n; i++) {
            unsigned j = rnd(len), m[2], k = members(x, pt->at + j, m);
            buf[i] = rnd(5) ? (unsigned char)m[rnd(k)] : (unsigned char)F;
        }
        if (n > len && rnd(2)) occ(x, pt, buf, rnd((unsigned)(n - len + 1)));
        size_t lo = rnd((unsigned)n + 1);
        if (n >= len && rnd2(2) &&                       /* FAM-3: a near-miss occurrence */
            near_occ(x, pt, pt->ver_lo, pt->ver_len, buf, rnd2((unsigned)(n - len + 1))))
            g_nm_sound++;
        size_t r = measure(pt, buf, n, lo, NULL);
        int ok = r >= n || (r >= lo && r + pt->ver_lo + pt->ver_len <= n);
        for (unsigned j = (unsigned)pt->ver_lo; ok && r < n && j < pt->ver_lo + pt->ver_len; j++)
            ok = in_set(x, pt->at + j, buf[r + j]);
        g_sound++;
        CHECK(x, ok, "SOUND", "part at %u len %u: lo %zu n %zu yielded %zu", pt->at, len, lo, n, r);
    }
}

/* classify, a fault in a direct part call (layout U) a failure: -1 */
static int classify_guarded(const g2p_site *x, const g2p_part *pt, int *lo, int *hi, int *sc)
{
    if (sigsetjmp(g_jb, 1)) {
        g_active = 0;
        failf(x, "LAYOUT", "a direct call of the part at %u faulted (layout U)", pt->at);
        return -1;
    }
    classify(x, pt, lo, hi, sc);
    return 0;
}

/* one call of use `f`, a fault caught (g_faulted 1; a recorded call's
 * g_active reset, ORC-4); its return, 0 on a fault. Its own frame, so no
 * caller's variable lives across the sigsetjmp. */
static __attribute__((noinline)) int call_use(g2p_use_fn f, const unsigned char *s, size_t n,
                                              size_t lo, size_t *out)
{
    g_faulted = 0;
    if (!sigsetjmp(g_jb, 1)) return f(s, n, lo, out);
    g_active = 0;
    return 0;
}

static long least_occ(const g2p_site *x, const unsigned char *s, size_t n, size_t origin);

/* THE USES' PRESENCE RULE (review 2026-11-11 r1 k382 F1; span_runs_sheet.md
 * §3.3 items 1-3, the SOUND direction): where the whole run occurs at a
 * least c >= max(0, origin + omin) and every verified member occurs in
 * [origin, n), the use must answer present, and an ASSIGN use's landmark
 * lies in [max(0, origin + omin), c] (the run part's least candidate holds
 * the extent, which the whole occurrence at c does). It reads the stated
 * run, omin and members only, so it holds every row alike: the pre-check
 * row's calls and the GENERIC row's inline loops (which the classifier,
 * reading function calls, cannot see). `below`: the occurrence lies below
 * the origin, the population a floor at `lo` misses. */
static long g_pres_checks, g_pres_below;
static void pres_check(const g2p_site *x, const unsigned char *s, size_t n, size_t origin,
                       int hit, size_t out, int assign, const char *call, const char *lay)
{
    long want = least_occ(x, s, n, origin);
    if (want < 0) return;
    for (unsigned k = 0; k < x->nmem; k++)
        if (origin >= n || !memchr(s + origin, x->mem[k], n - origin)) return;
    long floor = (long)origin + x->omin < 0 ? 0 : (long)origin + x->omin;
    g_pres_checks++;
    g_pres_below += want < (long)origin;
    CHECK(x, hit, "PRESENCE", "%s: the %s from %zu (n %zu) misses, the whole run occurs at %ld "
          "and every member is present", lay, call, origin, n, want);
    if (hit && assign)
        CHECK(x, (long)out >= floor && (long)out <= want, "PRESENCE", "%s: the %s from %zu (n %zu) "
              "yields %zu, outside [%ld, %ld] (the floor, the least whole occurrence)", lay, call,
              origin, n, out, floor, want);
}

/* the entry and re-entry uses over generated subjects, in layout `lay` */
static void uses(const g2p_site *x, int lay)
{
    unsigned char buf[256];
    unsigned F = filler(x);
    g2p_part whole = { 0, x->run_len, NULL, 0, 0, x->run_len };
    for (int t = 0; t < 16; t++) {
        size_t n = rnd(x->run_len + 48);
        for (size_t i = 0; i < n; i++) {
            unsigned j = rnd(x->run_len), m[2], k = members(x, j, m);
            buf[i] = rnd(3) ? (unsigned char)m[rnd(k)] : rnd(4) ? (unsigned char)F : (unsigned char)rnd(256);
        }
        for (int o = 0; o < 2 && n > x->run_len; o++)
            if (rnd(3)) occ(x, &whole, buf, rnd((unsigned)(n - x->run_len + 1)));
        size_t lo = rnd((unsigned)n + 1), out;
        if (x->omin < 0 && rnd(2)) {            /* the origin below -omin: the floor clamps to 0 */
            size_t back = (size_t)-(long long)x->omin;
            lo = rnd((unsigned)(n < back ? n : back) + 1);
        }
        if (lay == LAY_L && x->omin <= -8 && x->omin >= -32 && lo < (size_t)-(long long)x->omin)
            g_wk4_low++;
        if (n >= x->run_len && rnd2(2) &&                /* FAM-3: a near-miss occurrence */
            near_occ(x, &whole, 0, x->run_len, buf, rnd2((unsigned)(n - x->run_len + 1))))
            g_nm_uses++;
        unsigned char *s = place(lay, buf, n);
        g_hs = s; g_hn = n; g_hlo = lo;                  /* the caller boundary (ORC-1) */
        g_call = lay == LAY_U ? "entry" : NULL;
        int hit = call_use(x->entry, s, n, lo, &out);
        g_lay_calls[lay]++;
        CHECK(x, !g_faulted, "LAYOUT", "%s: the entry faulted (n %zu, lo %zu)", lay_name[lay], n, lo);
        if (!g_faulted) pres_check(x, s, n, lo, hit, out, x->assign, "entry", lay_name[lay]);
        if (x->reentry) {
            size_t pv = rnd((unsigned)n + 1);
            g_hlo = pv;
            g_call = lay == LAY_U ? "reentry" : NULL;
            hit = call_use(x->reentry, s, n, pv, &out);
            g_lay_calls[lay]++;
            CHECK(x, !g_faulted, "LAYOUT", "%s: the re-entry faulted (n %zu, lo %zu)", lay_name[lay], n, pv);
            if (!g_faulted) pres_check(x, s, n, pv, hit, out, 1, "re-entry", lay_name[lay]);
        }
        g_call = NULL;
    }
}

#ifdef G2P_ASAN
/* layout A (W-K4b): the subject at offset `off` from a W-aligned heap block
 * of exactly off + n bytes, the block's whole granules below the subject
 * poisoned (ASan's 8-byte granule: the off % 8 bytes just below s stay
 * addressable, a stated limit), every part and use called */
static long g_lay_a;
static void lay_a(const g2p_site *x)
{
    static const unsigned ws[] = { 16, 32 };
    unsigned char buf[256];
    unsigned F = filler(x);
    for (unsigned wi = 0; wi < 2; wi++)
        for (unsigned off = 1; off < ws[wi]; off++) {
            size_t n = x->run_len + rnd(24);
            for (size_t i = 0; i < n; i++) buf[i] = rnd(3) ? x->run[rnd(x->run_len)] : (unsigned char)F;
            void *blk;
            if (posix_memalign(&blk, ws[wi], off + n + (n == 0))) { perror("posix_memalign"); exit(2); }
            unsigned char *s = (unsigned char *)blk + off;
            memcpy(s, buf, n);
            size_t pz = off & ~7u;
            if (pz) ASAN_POISON_MEMORY_REGION(blk, pz);
            size_t out;
            for (unsigned k = 0; k < x->nparts; k++)
                if (x->parts[k].fn) x->parts[k].fn(s, n, rnd((unsigned)n + 1));
            x->entry(s, n, rnd((unsigned)n + 1), &out);
            if (x->reentry) x->reentry(s, n, rnd((unsigned)n + 1), &out);
            if (pz) ASAN_UNPOISON_MEMORY_REGION(blk, pz);
            free(blk);
            g_lay_a++;
        }
}
#endif

/* ---- the §3.5 witnesses (W-L1 a/b, W-K1, W-K2) ---------------------------------- */

/* The stated rule (span_runs_sheet.md §3.3 items 1-3, the extent whole): the
 * least c >= max(0, origin + omin) at which the WHOLE run occurs inside the
 * subject, or -1. Computed in signed integers: no wrap. */
static long least_occ(const g2p_site *x, const unsigned char *s, size_t n, size_t origin)
{
    long floor = (long)origin + x->omin;
    if (floor < 0) floor = 0;
    for (long c = floor; c + (long)x->run_len <= (long)n; c++) {
        unsigned j = 0;
        while (j < x->run_len && in_set(x, j, s[c + j])) j++;
        if (j == x->run_len) return c;
    }
    return -1;
}

static long g_wk_ok[G2P_W_N], g_wk_reach[G2P_W_N];
static const struct {
    int wk;
    const char *name, *subject;
    size_t origin;
    int reentry;            /* 1: the call is the RE-ENTRY use */
    long want;              /* the sheet's literal (§3.5)      */
} wk_cases[] = {
    { G2P_W_L1A, "W-L1",  "foobar",   3, 0, 0 },
    { G2P_W_L1B, "W-L1b", "foobar",   3, 0, 0 },
    { G2P_W_K1,  "W-K1",  "foobar",   1, 0, 0 },
    { G2P_W_K2,  "W-K2",  "abababcc", 3, 1, 2 },
};

static void wk_run(const g2p_site *x)
{
    for (unsigned i = 0; i < sizeof wk_cases / sizeof wk_cases[0]; i++) {
        if (wk_cases[i].wk != x->wk) continue;
        const char *name = wk_cases[i].name;
        size_t n = strlen(wk_cases[i].subject), origin = wk_cases[i].origin, out = 0;
        const unsigned char *src = (const unsigned char *)wk_cases[i].subject;
        long want = least_occ(x, src, n, origin);
        CHECK(x, want == wk_cases[i].want, name, "the stated rule gives %ld, the sheet's literal "
              "is %ld (the witness itself is wrong)", want, wk_cases[i].want);
        /* reach: the floor lies below the origin (omin < 0, origin > 0), so a
           kit flooring at the origin misses the answer; W-L1b: the answer's
           scan byte lies below the origin too (has_scan, scan < origin - c) */
        long floor = (long)origin + x->omin < 0 ? 0 : (long)origin + x->omin;
        int reach = floor < (long)origin && want >= 0 && want < (long)origin;
        if (x->wk == G2P_W_L1B)
            reach = reach && x->has_scan && want + x->scan < (long)origin;
        CHECK(x, reach, name, "does not reach (floor %ld, origin %zu, answer %ld, scan %d)", floor,
              origin, want, x->has_scan ? x->scan : -1);
        g_wk_reach[x->wk] += reach;
        for (int lay = 0; lay < LAY_N; lay++) {
            unsigned char *s = place(lay, src, n);
            g_hs = s; g_hn = n; g_hlo = origin;
            g_call = lay == LAY_U ? (wk_cases[i].reentry ? "reentry" : "entry") : NULL;
            int hit = call_use(wk_cases[i].reentry ? x->reentry : x->entry, s, n, origin, &out);
            g_call = NULL;
            long got = hit ? (long)out : -1;
            CHECK(x, !g_faulted, name, "%s: faulted", lay_name[lay]);
            int ok = !g_faulted && got == want;
            CHECK(x, ok, name, "%s: the %s from %zu on \"%s\" yields %ld, the stated rule %ld", lay_name[lay],
                  wk_cases[i].reentry ? "re-entry" : "entry", origin, wk_cases[i].subject, got, want);
            if (ok && lay == LAY_U) g_wk_ok[x->wk]++;
        }
        printf("G2PWK %s %s site %d: want %ld reach %d\n", x->tag, name, x->id, want, reach);
    }
}

int main(int argc, char **argv)
{
    const char *recpath = NULL;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--records") && i + 1 < argc) recpath = argv[++i];
        else if (!strcmp(argv[i], "--seed") && i + 1 < argc) {
            unsigned long long sd = strtoull(argv[++i], NULL, 10);
            g_rng ^= sd; g_rng2 ^= sd;
        }
        else { fprintf(stderr, "usage: g2p_run [--records FILE] [--seed N]\n"); return 2; }
    }
    g_page = sysconf(_SC_PAGESIZE);
    g_map = mmap(NULL, 3 * (size_t)g_page, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (g_map == MAP_FAILED) { perror("mmap"); return 2; }
    if (mprotect(g_map, (size_t)g_page, PROT_NONE) ||
        mprotect(g_map + 2 * g_page, (size_t)g_page, PROT_NONE)) { perror("mprotect"); return 2; }
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_fault;
    sa.sa_flags = SA_NODEFER;
    sigaction(SIGSEGV, &sa, NULL);
    sigaction(SIGBUS, &sa, NULL);
    if (recpath) {
        g_rec = fopen(recpath, "w");
        if (!g_rec) { perror(recpath); return 2; }
        fputs("#site\tcall\tsubject\torigin\tomin\tsets\tver_lo\tver_len\tresult\treads\n", g_rec);
    }
    long nsite[G2P_NROUTE] = { 0 }, nparts = 0, nwit = 0;
    for (int i = 0; i < g2p_nsites; i++) {
        const g2p_site *x = &g2p_sites[i];
        if (x->id < 0 || x->id >= (int)(sizeof g_site_of / sizeof g_site_of[0])) {
            printf("FAIL site id %d out of range\n", x->id);
            return 2;
        }
        g_site_of[x->id] = x;
    }
    /* the §3.5 witnesses FIRST, so their lines print ahead of any other
       failure (failf prints the first 60) */
    for (int i = 0; i < g2p_nsites; i++)
        if (g2p_sites[i].wk) wk_run(&g2p_sites[i]);
    for (int i = 0; i < g2p_nsites; i++) {
        const g2p_site *x = &g2p_sites[i];
        nsite[x->route]++;
        /* the classifier over the site's ONE run part (run frame): its
           measured extent is the site's reply, and its scan the reply's */
        int slo = -1, shi = -1, sscan = INT32_MIN, have = 0;
        if (!strcmp(x->forms, "generic")) {
            /* THE GENERIC PASS: the run part is inline in the uses (no
               function to classify); the uses' PRESENCE rule is its check */
            g_generic++;
            for (int lay = 0; lay < LAY_N; lay++) uses(x, lay);
#ifdef G2P_ASAN
            lay_a(x);
#endif
            continue;
        }
        CHECK(x, x->nparts == 1 && x->parts[0].fn && x->parts[0].at == 0 &&
              x->parts[0].len == x->run_len, "LAYOUT", "the site does not lay out ONE derived run "
              "part in the run frame (%u parts)", x->nparts);
        CHECK(x, x->has_scan, "SCAN", "the reply of a tested run states no scan position");
        if (x->nparts == 1 && x->parts[0].fn) {
            const g2p_part *pt = &x->parts[0];
            nparts++;
            int lo, hi, sc;
            if (!classify_guarded(x, pt, &lo, &hi, &sc)) {
                slo = lo; shi = hi; sscan = sc; have = 1;
                if (lo < 0) slo = shi = (int)x->ver_lo;     /* nothing compared: an empty extent */
            }
        }
        CHECK(x, have && slo == (int)x->ver_lo && shi == (int)(x->ver_lo + x->ver_len), "EXTENT",
              "the part compares [%d, %d), the site's reply is [%u, %u)", slo, shi, x->ver_lo,
              x->ver_lo + x->ver_len);
#ifdef G2P_REC   /* the reads exist only in the recording build */
        if (have) {
            g_scan_route[x->route]++;
            CHECK(x, sscan == x->scan, "SCAN", "the text's find reads run position %d first, the "
                  "site's reply scans %d", sscan, x->scan);
        }
        if (x->witness) {
            /* the STATED rule, not the kit's reply: every position ties */
            int want = x->lever ? 0 : (int)x->run_len - 1;
            nwit++;
            g_witness++;
            CHECK(x, have && sscan == want, "LEVER", "a tie witness's text scans %d, the stated rule "
                  "(%s) is %d", sscan, x->lever ? "run-tie-left: leftmost" : "incumbent: rightmost", want);
            printf("G2PW %s %d scan=%d\n", x->tag, x->id, sscan);
        }
#else
        (void)sscan;
#endif
        for (int lay = 0; lay < LAY_N; lay++) uses(x, lay);
#ifdef G2P_ASAN
        lay_a(x);
#endif
    }
    if (g_rec) fclose(g_rec);
    printf("G2P sites P0=%ld P2=%ld P3=%ld P9=%ld parts=%ld witnesses=%ld\n", nsite[G2P_P0],
           nsite[G2P_P2], nsite[G2P_P3], nsite[G2P_P9], nparts, nwit);
    printf("G2P reach P0=%ld P3=%ld P9=%ld (entry+reentry; reentry P0=%ld P3=%ld P9=%ld)\n",
           g_reach[G2P_P0][0] + g_reach[G2P_P0][1], g_reach[G2P_P3][0] + g_reach[G2P_P3][1],
           g_reach[G2P_P9][0] + g_reach[G2P_P9][1], g_reach[G2P_P0][1], g_reach[G2P_P3][1],
           g_reach[G2P_P9][1]);
    printf("G2P checks cover=%ld extent=%ld scan=%ld sound=%ld scan_sites P0=%ld P3=%ld P9=%ld "
           "layout_U=%ld layout_L=%ld records=%ld nearmiss=%ld nm_sound=%ld nm_uses=%ld\n", g_cover,
           g_extent, g_scan, g_sound, g_scan_route[G2P_P0], g_scan_route[G2P_P3], g_scan_route[G2P_P9],
           g_lay_calls[LAY_U], g_lay_calls[LAY_L], g_records, g_nearmiss, g_nm_sound, g_nm_uses);
    printf("G2P k382 partial_hits=%ld neg_records=%ld below_hits=%ld wk4_low=%ld\n", g_partial_hits,
           g_neg_records, g_below_hits, g_wk4_low);
    printf("G2P presence checks=%ld below=%ld generic=%ld\n", g_pres_checks, g_pres_below, g_generic);
    printf("G2P wk L1=%ld/%ld L1b=%ld/%ld K1=%ld/%ld K2=%ld/%ld (green/reached)\n",
           g_wk_ok[G2P_W_L1A], g_wk_reach[G2P_W_L1A], g_wk_ok[G2P_W_L1B], g_wk_reach[G2P_W_L1B],
           g_wk_ok[G2P_W_K1], g_wk_reach[G2P_W_K1], g_wk_ok[G2P_W_K2], g_wk_reach[G2P_W_K2]);
#ifdef G2P_ASAN
    printf("G2P layout_A=%ld\n", g_lay_a);
#endif
#ifdef G2P_REC
    printf("G2P vec_reads=%ld\n", g_vec);
#endif
    printf("checks passed: %ld\nchecks failed: %ld\n", g_pass, g_fail);
    return g_fail ? 1 : 0;
}
