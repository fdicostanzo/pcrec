/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2's presence family,
 *   lane k382a, R-38 K38-2a; moved to the seam event's statement form at
 *   R-38 K38-2, lane k382).
 *
 * memfn/tests/g2/g2_pres_gen.c — G2'S PRESENCE FAMILY, THE GENERATOR (the only
 * file of the family that calls the kit; docs/design/memfn/span_runs_sheet.md
 * rev 1.3 §2.1-§2.4 (C2), §3.2-§3.5 (W-L1, W-K1..W-K4b), and §5's K38-2 row,
 * PLAN (c) FAM-2 and (d) ORC-3). It GENERATES pre-check sites in the SEAM
 * EVENT's statement form (MF_SITE_ABI 27): set-member spans, and the run ONE
 * presence span in SET form (nalt 1, one span at start 0, each position its
 * byte set, core all, verify NO, wfloor SUBJECT, nterm 0, LAST), its `omin`
 * of EITHER SIGN (the origin the attempt start, §3.1) and, on an ASSIGN site,
 * a SIGNED K (`head_max`, §3.2; <= 0 included). It states them as a host does
 * (the presence spans, the start search's proof, the consumer kind), asks the
 * kit (mf_ask: the links and THE RUN's ONE DECISION, mf_class.run), LAYS THE
 * PARTS OUT as a host does (the head member, then ONE run part the kit
 * DERIVES, a FUNC part stating only `fn_ref`, where the run's link is tested,
 * then the rest members), defines the site and renders its two uses: the
 * ENTRY (lo the activation's origin) and, on an ASSIGN site, the RE-ENTRY.
 * Per route, by the PRES row that decided the run's link:
 *   P0  every span REQUIRED (the VM attempt loop's consumer kind);
 *   P3  every span OPTIONAL (the pick: the reply's extent may be partial);
 *   P9  OPTIONAL under `--memfn=no-fd-pres-pick`;
 *   P2  OPTIONAL, the proof standing for the leading check: nothing is
 *       verified, so the host lays out no run part (C2's third clause), and a
 *       layout WITH the derived part is refused (the control).
 * Rates: none, skewed, uniform (every byte one rate: `--analysis=uniform`'s
 * regime, all ties), tie-heavy over the site's own bytes, or FIXED (a
 * witness's, stated below).
 *
 * FAM-2: the run's scan and verified extent are read OFF THE REPLY
 * (mf_class.run, from mf_ask and again from mf_defined, which must agree),
 * never from the run's length or a window constant; the reply's stated
 * invariants (§2.2: scan < n where has_scan; ver_lo + ver_len <= n; all zero
 * where the link is untested) are held here.
 * W-K3 (the twin, §3.5): on every site whose landmark admission bit at K 0 is
 * 1 (m > h), the bit at every K in -32..-1 equals it: the STATED rule
 * max(K, 0) (§3.2), never presence.c's arithmetic.
 *
 * Writes OUT/g2p_sites.c: TARGET's family guard, the headers the renderings'
 * mf_includes name, the recorder's wrappers of the libc reads (G2P_REC), the
 * target's region around every definition, a direct call of each rendered
 * run part (`g2p_part_<id>_0`, the classifier's), then `#define <fn>(...)`
 * routing every later call of the part through the recorder (g2p_rec), then
 * the ENTRY and RE-ENTRY wrappers; and the site table (g2_pres.h): the run
 * AS GENERATED, its stated omin and K, the part AS LAID OUT (run frame), and
 * the kit's reply, never anything read from the kit's text.
 * THE LEVER WITNESSES (plant C): a run of distinct exact bytes under the
 * uniform rates, every position a tie; the driver reads the scan offset the
 * TEXT uses and holds it to the stated rule (the incumbent: the rightmost;
 * under `run-tie-left`: the leftmost).
 * THE §3.5 WITNESS SITES (the driver runs them): W-L1 (`foobar`, omin -3; a
 * second instance whose FIXED rates put the scan at position 0, below the
 * origin), W-K1 (`foobar`, omin -3) and W-K2 (`abab`, omin -2), each an
 * ASSIGN site on P0, K its fixed placement (= omin).
 *
 *   g2_pres_gen SEED NSITES OUTDIR TARGET LEVER   (LEVER 0 or 1: every art of
 *                                                  the pass under run-tie-left)
 */
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "memfn.h"
#include "g2_pres.h"

/* ---- text ------------------------------------------------------------------- */

typedef struct { char *p; size_t len, cap; } buf;

static void bput(buf *b, const char *s, size_t n)
{
    if (b->len + n + 1 > b->cap) {
        b->cap = (b->len + n + 1) * 2;
        b->p = realloc(b->p, b->cap);
        if (!b->p) { perror("realloc"); exit(2); }
    }
    memcpy(b->p + b->len, s, n);
    b->len += n;
    b->p[b->len] = 0;
}

static void bputs(buf *b, const char *s) { bput(b, s, strlen(s)); }

static void bvprintf(buf *b, const char *fmt, va_list ap)
{
    char tmp[8192];
    int k = vsnprintf(tmp, sizeof tmp, fmt, ap);
    if (k < 0 || (size_t)k >= sizeof tmp) { fprintf(stderr, "g2p: line too long\n"); exit(2); }
    bput(b, tmp, (size_t)k);
}

static void bprintf(buf *b, const char *fmt, ...) __attribute__((format(printf, 2, 3)));
static void bprintf(buf *b, const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    bvprintf(b, fmt, ap);
    va_end(ap);
}

static void sk_puts(void *u, const char *s) { bputs(u, s); }
static void sk_vprintf(void *u, const char *fmt, va_list ap) { bvprintf(u, fmt, ap); }
static int  sk_cmt_open(void *u, int tier) { (void)u; (void)tier; return 0; }
static void sk_cmt_close(void *u) { (void)u; }
static void sk_cstr(void *u, const uint8_t *bytes, size_t len)
{
    for (size_t i = 0; i < len; i++) bprintf(u, "\\%03o", bytes[i]);
}
static void sk_open(void *u, int level) { (void)u; (void)level; }
static void sk_close(void *u) { (void)u; }

static mf_sink mk_sink(buf *b)
{
    mf_sink s;
    memset(&s, 0, sizeof s);
    s.u = b;
    s.puts = sk_puts;
    s.vprintf = sk_vprintf;
    s.cmt_open = sk_cmt_open;
    s.cmt_close = sk_cmt_close;
    s.cstr = sk_cstr;
    s.simd_open = sk_open;
    s.simd_close = sk_close;
    return s;
}

static void *ar_alloc(void *u, size_t n) { (void)u; return calloc(1, n ? n : 1); }
static mf_arena g_arena = { NULL, ar_alloc };

/* ---- the family's own random stream ---------------------------------------- */

static unsigned long long g_rng;
static unsigned rnd(unsigned n)
{
    g_rng = g_rng * 6364136223846793005ull + 1442695040888963407ull;
    return n ? (unsigned)((g_rng >> 33) % n) : 0;
}

static void set_add(uint8_t set[32], unsigned b) { set[b >> 3] |= (uint8_t)(1u << (b & 7)); }

/* THE WIDE STREAM's own random stream (R-38 Part D, part_d.md §5.1 D0
   [r1pd F18]): every draw of the wide sites, after today's sites, so the
   main stream's sites, and the site file they write, stay byte-identical */
static unsigned long long g_rng2;
static unsigned rnd2(unsigned n)
{
    g_rng2 = g_rng2 * 6364136223846793005ull + 1442695040888963407ull;
    return n ? (unsigned)((g_rng2 >> 33) % n) : 0;
}

static unsigned set_count(const uint8_t set[32])
{
    unsigned k = 0;
    for (unsigned i = 0; i < 32; i++) k += (unsigned)__builtin_popcount(set[i]);
    return k;
}
static int set_has(const uint8_t set[32], unsigned b) { return set[b >> 3] >> (b & 7) & 1; }
static int set_first(const uint8_t set[32])
{
    for (unsigned b = 0; b < 256; b++) if (set_has(set, b)) return (int)b;
    return -1;
}
/* G2's OWN reading of "findable" (part_d.md §2.4 item 1, written from the
   design's words, never the kit's accessor): one member, or two members
   differing in one bit (a cube) */
static int findable(const uint8_t set[32])
{
    unsigned k = set_count(set);
    if (k == 1) return 1;
    if (k != 2) return 0;
    int a = set_first(set), b = -1;
    for (unsigned x = (unsigned)a + 1; x < 256 && b < 0; x++) if (set_has(set, x)) b = (int)x;
    return __builtin_popcount((unsigned)(a ^ b)) == 1;
}

/* ---- a generated site -------------------------------------------------------- */

enum { RATE_NONE, RATE_SKEW, RATE_UNIFORM, RATE_TIES, RATE_N, RATE_FIXED = RATE_N };

typedef struct {
    int      id, want, witness, wk;
    int      wide;                      /* a WIDE stream site (sets authoritative) */
    unsigned L;
    uint8_t  run[G2P_MAXRUN], mask[G2P_MAXRUN];
    uint8_t  set[G2P_MAXRUN][32];       /* each position's set (every site) */
    unsigned nm;
    uint8_t  members[4];
    int      rates, assign;
    int32_t  omin;                      /* the run span's omin, as stated  */
    int      kdraw;                     /* K - omin on an ASSIGN site      */
    uint32_t rate[256];
    char     names[G2P_MAXPART][40];
} gsite;

/* the run: bytes from a small alphabet (ties and repeats), mostly exact,
   a fifth of the positions a one-bit cube (a run position is one member or
   a pair); a quarter of the runs CASELESS (every letter its case pair,
   `(?i)`'s run): the only runs whose scan is a pair, the SIMD rows' shape
   (vrun.c rides over fn-pair) */
static void gen_run(gsite *g)
{
    if (rnd(4) == 0) {
        static const unsigned lens[] = { 2, 3, 4, 5, 6, 8, 9, 12, 16, 20, 32 };
        g->L = lens[rnd(sizeof lens / sizeof lens[0])];
        unsigned na = 2 + rnd(5), alpha[6];
        for (unsigned i = 0; i < na; i++) alpha[i] = 'a' + rnd(26);
        for (unsigned j = 0; j < g->L; j++) {
            unsigned b = rnd(8) ? alpha[rnd(na)] : '0' + rnd(10);
            g->mask[j] = b >= 'a' ? 0xDF : 0xFF;
            g->run[j] = (uint8_t)(b & g->mask[j]);
        }
        return;
    }
    static const unsigned lens[] = { 2, 3, 3, 4, 4, 5, 5, 6, 7, 8, 8, 9, 10, 11, 12, 13,
                                     14, 16, 18, 20, 24, 28, 32 };
    g->L = lens[rnd(sizeof lens / sizeof lens[0])];
    unsigned na = 2 + rnd(5), alpha[6];
    for (unsigned i = 0; i < na; i++) alpha[i] = rnd(4) ? 'a' + rnd(26) : rnd(256);
    for (unsigned j = 0; j < g->L; j++) {
        unsigned b = alpha[rnd(na)], m = 0xFF, k = rnd(20);
        if (k < 3) m = 0xDF;                            /* a letter's case bit */
        else if (k == 3) m = 0xFF & ~(1u << rnd(8));
        g->mask[j] = (uint8_t)m;
        g->run[j] = (uint8_t)(b & m);
    }
}

/* the run span's omin (§3.1): 0 (today's) on half the sites; else negative,
   half of those inside W-K4a's range -8..-32, the rest -1..-40 */
static int32_t gen_omin(void)
{
    if (rnd(2)) return 0;
    return rnd(2) ? -(int32_t)(8 + rnd(25)) : -(int32_t)(1 + rnd(40));
}

/* THE WIDE STREAM (R-38 Part D, part_d.md §5.2): a position's set from a
   stratified member-count distribution and shape, on rnd2 alone. `cls`:
   0 one byte; 1 a cube (a letter's case pair or a one-bit pair); 2 two
   members not a cube; 3 3-8 scattered; 4 one range of 9-32; 5 a union of
   ranges, 33-128 members; 6 exactly 128 (the low or the high half); 7 \d;
   8 hex; 9 [a-z]; 10 \w; 11 \s; 12 a UTF-8 lead set; 13 continuation */
enum { PC_ONE, PC_CUBE, PC_TWO, PC_SCAT, PC_RANGE, PC_UNION, PC_128, PC_D, PC_HEX, PC_AZ, PC_W,
       PC_S, PC_LEAD, PC_CONT, PC_N };
static void set_range(uint8_t s[32], unsigned lo, unsigned hi) { for (unsigned b = lo; b <= hi; b++) set_add(s, b); }
static void wide_pos(uint8_t s[32], int cls)
{
    memset(s, 0, 32);
    unsigned b = rnd2(256);
    switch (cls) {
    case PC_ONE:   set_add(s, b); break;
    case PC_CUBE:
        if (rnd2(2)) { b = 'a' + rnd2(26); set_add(s, b); set_add(s, b & 0xDF); }
        else { set_add(s, b); set_add(s, b ^ (1u << rnd2(8))); }
        break;
    case PC_TWO:   set_add(s, b); set_add(s, b ^ (3u << rnd2(7))); break;   /* two bits differ */
    case PC_SCAT:  for (unsigned n = 3 + rnd2(6); set_count(s) < n;) set_add(s, rnd2(256)); break;
    case PC_RANGE: { unsigned n = 9 + rnd2(24), lo = rnd2(256 - n); set_range(s, lo, lo + n - 1); } break;
    case PC_UNION: {
        unsigned want = 33 + rnd2(96);
        while (set_count(s) < want) {
            unsigned n = 4 + rnd2(28), lo = rnd2(256 - n);
            set_range(s, lo, lo + n - 1);
        }
        while (set_count(s) > 128) {                    /* at most 128 (info >= 1 bit) */
            unsigned x = (unsigned)set_first(s);
            s[x >> 3] &= (uint8_t)~(1u << (x & 7));
        }
        break;
    }
    case PC_128:   if (rnd2(2)) set_range(s, 0x00, 0x7F); else set_range(s, 0x80, 0xFF); break;
    case PC_D:     set_range(s, '0', '9'); break;
    case PC_HEX:   set_range(s, '0', '9'); set_range(s, 'a', 'f'); set_range(s, 'A', 'F'); break;
    case PC_AZ:    set_range(s, 'a', 'z'); break;
    case PC_W:     set_range(s, '0', '9'); set_range(s, 'a', 'z'); set_range(s, 'A', 'Z'); set_add(s, '_'); break;
    case PC_S:     set_range(s, 9, 13); set_add(s, ' '); break;
    case PC_LEAD:  set_range(s, 0xC2, 0xDF); break;
    default:       set_range(s, 0x80, 0xBF); break;
    }
}
static int wide_cls(void)        /* a WIDE class: three or more members */
{
    return PC_SCAT + (int)rnd2(PC_N - PC_SCAT);
}
static int find_cls(void)        /* a FINDABLE class */
{
    return rnd2(3) ? PC_ONE : PC_CUBE;
}
static void gen_wide(gsite *g)
{
    g->wide = 1;
    unsigned L = 0;
    int cls[G2P_MAXRUN];
    switch (rnd2(8)) {
    case 0:                                         /* NO findable position */
        L = 2 + rnd2(11);
        for (unsigned j = 0; j < L; j++) cls[j] = wide_cls();
        if (rnd2(4) == 0) { cls[0] = PC_128; cls[1] = PC_128; }   /* maybe "no background" */
        break;
    case 1: {                                       /* ab\dcd: a wide position between two stretches */
        unsigned a = 1 + rnd2(4), b = 1 + rnd2(4);
        for (unsigned j = 0; j < a; j++) cls[L++] = find_cls();
        cls[L++] = wide_cls();
        for (unsigned j = 0; j < b; j++) cls[L++] = find_cls();
        break;
    }
    case 2: {                                       /* \d[aA]\d: a lone findable between wide ones */
        unsigned n = 1 + rnd2(3);
        for (unsigned j = 0; j < n; j++) cls[L++] = wide_cls();
        cls[L++] = find_cls();
        for (unsigned j = 0; j < n; j++) cls[L++] = wide_cls();
        break;
    }
    case 3:                                         /* a wide position at either end */
        L = 3 + rnd2(10);
        for (unsigned j = 0; j < L; j++) cls[j] = find_cls();
        if (rnd2(2)) cls[0] = wide_cls();
        if (rnd2(2) || cls[0] < PC_SCAT) cls[L - 1] = wide_cls();
        break;
    case 4: {                                       /* a joint superset: 2-4 literal branches' union */
        L = 2 + rnd2(7);
        unsigned nb = 2 + rnd2(3);
        for (unsigned j = 0; j < L; j++) {
            memset(g->set[j], 0, 32);
            for (unsigned k = 0; k < nb; k++) set_add(g->set[j], 'a' + rnd2(26));
            cls[j] = -1;
        }
        break;
    }
    default:                                        /* stratified per position */
        L = 2 + rnd2(G2P_MAXRUN - 1);
        for (unsigned j = 0; j < L; j++) {
            unsigned k = rnd2(10);
            cls[j] = k < 3 ? PC_ONE : k < 5 ? PC_CUBE : k < 6 ? PC_TWO : wide_cls();
        }
        break;
    }
    g->L = L;
    for (unsigned j = 0; j < L; j++) {
        if (cls[j] >= 0) wide_pos(g->set[j], cls[j]);
        g->run[j] = (uint8_t)set_first(g->set[j]);   /* unread on a wide site: the sets are */
        g->mask[j] = 0xFF;
    }
}

/* every position's set from today's run/mask form (the main stream) */
static void sets_of_run(gsite *g)
{
    memset(g->set, 0, sizeof g->set);
    for (unsigned j = 0; j < g->L; j++)
        for (unsigned b = 0; b < 256; b++)
            if ((b & g->mask[j]) == g->run[j]) set_add(g->set[j], b);
}

/* 1 iff no position of `g` is findable (G2's own computation, [r1pd F21]) */
static int no_findable(const gsite *g)
{
    for (unsigned j = 0; j < g->L; j++) if (findable(g->set[j])) return 0;
    return 1;
}
static int any_wide(const gsite *g)
{
    for (unsigned j = 0; j < g->L; j++) if (!findable(g->set[j])) return 1;
    return 0;
}

/* the lever witness: distinct exact bytes, uniform rates: every position a tie */
static void gen_witness(gsite *g)
{
    g->L = 4 + rnd(5);
    unsigned b0 = 'A' + rnd(10);
    for (unsigned j = 0; j < g->L; j++) {
        g->run[j] = (uint8_t)(b0 + 3 * j);
        g->mask[j] = 0xFF;
    }
}

/* a §3.5 witness site: the run `text`, exact, its omin and K the fixed
   placement (K = omin: the occurrence's position 0 lies exactly -omin bytes
   before the attempt start, `(?<=foo)bar`'s shape) */
static void gen_wk(gsite *g, int wk)
{
    const char *text = wk == G2P_W_K2 ? "abab" : "foobar";
    g->wk = wk;
    g->L = (unsigned)strlen(text);
    for (unsigned j = 0; j < g->L; j++) { g->run[j] = (uint8_t)text[j]; g->mask[j] = 0xFF; }
    g->omin = wk == G2P_W_K2 ? -2 : -3;
    g->kdraw = 0;
    g->want = G2P_P0;
    g->assign = 1;
    g->nm = 0;
    g->rates = RATE_NONE;
    if (wk == G2P_W_L1B || wk == G2P_W_K1B) {
        /* W-K1b (review 2026-11-11 r1 k382 F16): W-K1 with the SAME rates,
           so its scan offset k = 0 < N - origin (3 - 1): a wrapped floor
           `lo - N` then does not land on the clamped floor's candidate
           (W-K1's k = 5 >= N - origin reaches the same candidate either way,
           modulo 2^64, so it reds only through layout L's faults).
           W-L1b: the scan on position 0 ('f', the rarest), whose byte lies BELOW the
           origin 3 (span_runs_sheet.md §3.5 W-L1's second case); every run
           byte rarer than the rest of the alphabet, so the full start set's
           mass m exceeds the run's hit mass h (W-K3's reaching rates) */
        g->rates = RATE_FIXED;
        for (unsigned b = 0; b < 256; b++) g->rate[b] = 3800;
        g->rate['f'] = 5;
        g->rate['o'] = 2000;
        g->rate['b'] = 1500;
        g->rate['a'] = 1700;
        g->rate['r'] = 1600;
    }
}

/* The rates of a WIDE stream site ([r2pd P18], scoped by [r3pd FIX-3]): a
   position of THREE or more members rates each member (RATE_SKEW from
   rnd2(200000 / |S|), RATE_TIES 50000 / |S|), so its summed mass is in a
   one-member position's range; a position of one or two members keeps
   today's one draw on its first member; all on rnd2 */
static void gen_rates_wide(gsite *g)
{
    for (unsigned b = 0; b < 256; b++) g->rate[b] = 0;
    int skew = g->rates == RATE_SKEW;
    switch (g->rates) {
    case RATE_SKEW:
    case RATE_TIES:
        for (unsigned b = 0; b < 256; b++) g->rate[b] = skew ? rnd2(2000) : 100 + rnd2(50);
        for (unsigned j = 0; j < g->L; j++) {
            unsigned c = set_count(g->set[j]);
            if (c >= 3) {
                for (unsigned b = 0; b < 256; b++)
                    if (set_has(g->set[j], b)) g->rate[b] = skew ? rnd2(200000 / c) : 50000 / c;
            } else g->rate[set_first(g->set[j])] = skew ? rnd2(200000) : 50000;
        }
        for (unsigned i = 0; i < g->nm; i++) g->rate[g->members[i]] = skew ? rnd2(200000) : 50000;
        break;
    case RATE_UNIFORM:
        for (unsigned b = 0; b < 256; b++) g->rate[b] = 3906;
        break;
    default: break;
    }
}

static void gen_rates(gsite *g)
{
    if (g->rates == RATE_FIXED) return;
    if (g->wide) { gen_rates_wide(g); return; }
    for (unsigned b = 0; b < 256; b++) g->rate[b] = 0;
    switch (g->rates) {
    case RATE_SKEW:
        for (unsigned b = 0; b < 256; b++) g->rate[b] = rnd(2000);
        for (unsigned j = 0; j < g->L; j++) g->rate[g->run[j]] = rnd(200000);
        for (unsigned i = 0; i < g->nm; i++) g->rate[g->members[i]] = rnd(200000);
        break;
    case RATE_UNIFORM:
        for (unsigned b = 0; b < 256; b++) g->rate[b] = 3906;
        break;
    case RATE_TIES:
        for (unsigned b = 0; b < 256; b++) g->rate[b] = 100 + rnd(50);
        for (unsigned j = 0; j < g->L; j++) g->rate[g->run[j]] = 50000;
        for (unsigned i = 0; i < g->nm; i++) g->rate[g->members[i]] = 50000;
        break;
    default: break;
    }
}

static const char *fn_name_hook(void *u, uint32_t fn_ref)
{
    gsite *g = u;
    return fn_ref >= 1 && fn_ref <= G2P_MAXPART ? g->names[fn_ref - 1] : "g2p_badref";
}

static int in_run_set(const gsite *g, unsigned j, unsigned b)
{
    return set_has(g->set[j], b);
}

/* the presence spans a host states (emit_dfa.c req_pres_spans' shape): the
   members in descending byte order, one one-byte span each (the last one in
   pattern order states the member count, the others UNKNOWN), omin 0; the
   whole run LAST, in SET FORM (span_runs_sheet.md §2.1): one window
   statement, no entry fact, one span at start 0 of its L positions, each its
   byte set, table_ref 0, core STATED over all, verify NO, wfloor SUBJECT,
   nterm 0, and the generated omin (either sign) */
static mf_pred g_ps[5];
static mf_walt g_ra;
static mf_wspan g_rw;
static unsigned state_spans(const gsite *g, mf_need need)
{
    unsigned k = 0;
    memset(g_ps, 0, sizeof g_ps);
    uint8_t order[4];
    memcpy(order, g->members, g->nm);
    for (unsigned a = 0; a < g->nm; a++)        /* descending byte order */
        for (unsigned b = a + 1; b < g->nm; b++)
            if (order[b] > order[a]) { uint8_t t = order[a]; order[a] = order[b]; order[b] = t; }
    for (unsigned i = 0; i < g->nm; i++, k++) {
        mf_term *t = &g_ps[k].term[0];
        t->kind = MF_T_SET;
        t->need = need;
        set_add(t->set, order[i]);
        t->ppm_hi = MF_PPM_FULL;
        g_ps[k].nterm = 1;
        g_ps[k].member_order = order[i] == g->members[g->nm - 1] ? (uint16_t)g->nm
                                                                  : (uint16_t)MF_ORDER_UNKNOWN;
    }
    memset(&g_rw, 0, sizeof g_rw);
    g_rw.start = 0;
    g_rw.len = (uint8_t)g->L;
    g_rw.verify = MF_VERIFY_NO;
    g_rw.core = MF_CORE_STATED;
    g_rw.core_lo = 0;
    g_rw.core_len = (uint8_t)g->L;
    for (unsigned j = 0; j < g->L; j++)
        for (unsigned b = 0; b < 256; b++)
            if (in_run_set(g, j, b)) set_add(g_rw.set[j], b);
    g_ra = (mf_walt){ MF_ENTRY_NONE, 1, &g_rw };
    g_ps[k].nterm = 0;
    g_ps[k].nalt = 1;
    g_ps[k].alts = &g_ra;
    g_ps[k].wfloor = MF_WFLOOR_SUBJECT;
    g_ps[k].omin = g->omin;
    k++;
    for (unsigned i = 0; i < k; i++) {
        g_ps[i].need = need;
        g_ps[i].plan_hint = MF_NO_PRED;
        g_ps[i].span_class = MF_SPAN_PRESENCE;
    }
    return k;
}

static void site_base(mf_site *s)
{
    memset(s, 0, sizeof *s);
    s->abi = MF_SITE_ABI;
    s->ret_pred = MF_NO_PRED;
    s->span_hi = MF_SPAN_UNBOUNDED;
    s->cand_ppm_hi = MF_PPM_FULL;
    s->pred.plan_hint = MF_NO_PRED;
    s->policy = 0;
}

static const mf_target *g_target;
static int g_lever;
static int g_deny;                      /* the deny pass: every site under no-run-verify-wide */
static int g_oml = 1;                   /* the sites' on_miss_leaves (argv[6]) */
static int g_g2site;                    /* env G2P_G2SITE: print D3's join line */
static const char *g_tag;
static uint32_t g_inc;
static int g_fails;
static long g_generic;              /* sites mf_define rendered by the generic row */
static long g_ctl_nopart, g_ctl_two;  /* F14's two layout controls, refused as ruled */
static long g_route_sites[G2P_NROUTE], g_p2_untested, g_p2_refused, g_layout_ok, g_simd16, g_simd32;
static long g_neg_omin, g_wk4_omin, g_k_nonpos, g_k_signed, g_partial, g_room, g_wk3_sites,
            g_wk3_cases, g_wk3_zero;
static mf_finder_listing g_rows;
/* R-38 Part D's populations (part_d.md §5.1.1 D0-D2 floors; K35) */
static long g_wide_sites, g_wide_ver, g_nofind, g_nobg, g_f24, g_f24_3, g_scan_findable,
            g_declines, g_dec_member, g_dec_assign, g_dec_twin, g_dec_untested, g_dec_refused,
            g_dec_rendered, g_dec_noprecheck, g_scanless_req, g_dom_noscan, g_deny_sites, g_deny_one,
            g_r41, g_r41_flip;

static void fail(int id, const char *what, const char *why)
{
    g_fails++;
    fprintf(stderr, "FAIL g2p %s site %d: %s%s%s\n", g_tag, id, what, why ? ": " : "", why ? why : "");
}

static mf_art *art_of(const char *prefix, const mf_analysis *an)
{
    mf_art *art = mf_art_begin(&g_arena, prefix, 0, NULL, an);
    if (!art || mf_art_target(art, g_target)) return NULL;
    if (g_lever && mf_lever(art, "run-tie-left")) return NULL;
    return art;
}

static int route_of(const mf_class *c, unsigned run)
{
    unsigned r = c->pres_row[run];
    const char *id = r >= 1 && r <= g_rows.n ? g_rows.rows[r - 1].id : "";
    return !strcmp(id, "P0") ? G2P_P0 : !strcmp(id, "P2") ? G2P_P2 : !strcmp(id, "P3") ? G2P_P3
         : !strcmp(id, "P9") ? G2P_P9 : !strcmp(id, "PD") ? G2P_PD : -1;
}

typedef struct {
    int      rendered, route, assign, has_scan, scan, fnok, tested;
    int32_t  omin;                      /* the run span's stated omin */
    int64_t  head_max;                  /* K as stated               */
    unsigned ver_lo, ver_len;
    char     forms[48];
    unsigned nmem;                      /* the verified member parts' bytes */
    uint8_t  mem[8];
} gout;

/* The reply's stated invariants (span_runs_sheet.md §2.2; memfn.h
 * mf_run_reply): NULL iff `r` keeps them for a run of `n` positions whose
 * link is `tested`. */
static const char *reply_bad(const mf_run_reply *r, unsigned n, int tested)
{
    if (!tested)
        return r->has_scan || r->scan || r->ver_lo || r->ver_len
             ? "the run's link is untested and its reply is not all zero" : NULL;
    if (r->has_scan && r->scan >= n) return "scan >= n where has_scan";
    if ((unsigned)r->ver_lo + r->ver_len > n) return "ver_lo + ver_len > n";
    if (!r->ver_len && r->ver_lo) return "ver_len 0 with ver_lo not 0";
    return NULL;
}

/* W-K3 (§3.5, the twin): the landmark port's admission bit, at every K in
 * -32..-1, equals its bit at K 0, where that bit is 1 (otherwise every bit
 * is 0 and the plant cannot show). The expectation is the STATED rule: the
 * kit admits by max(K, 0) (§3.2), so a K <= 0 is K 0. The start set is every
 * byte (m the mass of the whole alphabet). */
static void twin_check(gsite *g, const mf_art *art, const mf_site *s, int dec, int head)
{
    static uint8_t all[32];
    memset(all, 0xFF, sizeof all);
    mf_site t = *s;
    t.handoff = MF_H_ASSIGN;
    t.npred = 0;
    t.preds = NULL;
    t.ret_pred = MF_NO_PRED;
    mf_pres_picks pk;
    t.head_max = 0;
    if (mf_pres_ports(art, &t, &t.pres_proof, all, &pk)) {
        fail(g->id, "W-K3", "mf_pres_ports refused the ASSIGN site at K 0");
        return;
    }
    g_wk3_sites++;
    if (pk.landmark < 0) { fail(g->id, "W-K3", "no landmark bit on an ASSIGN site"); return; }
    /* R-41 (MF_SITE_ABI 29): a STATED unbounded K (MF_HEAD_MAX_UNBOUNDED)
       declines the landmark on every ASSIGN site, whatever the bit at K 0
       (an h == 0 member's admission included); r41_flip counts the sites
       whose K 0 bit was 1, the ones the decline moves */
    {
        mf_site u = t;
        mf_pres_picks pu;
        u.head_max = MF_HEAD_MAX_UNBOUNDED;
        if (mf_pres_ports(art, &u, &u.pres_proof, all, &pu)) {
            fail(g->id, "R-41", "mf_pres_ports refused a stated unbounded K");
            return;
        }
        if (pu.landmark != 0) {
            fail(g->id, "R-41", "a stated unbounded K (MF_HEAD_MAX_UNBOUNDED) did not decline the landmark");
            return;
        }
        g_r41++;
        g_r41_flip += pk.landmark == 1;
    }
    /* F1 (part_d.md §2.4 item 5): on a DECLINED run the landmark is the head
       member, so the bit at K 0 is G2's own byte rule: the member's mass h
       (its rate capped at 1e6; under no rates the uniform floor(1e6 / 256))
       against the start set's m (every byte: 1e6), admitted iff h == 0 or
       m > h; the run branch over the empty extent would read h = 1e6 (0) */
    if (dec && head >= 0) {
        unsigned b = (unsigned)set_first(g_ps[head].term[0].set);
        unsigned long long h = g->rates == RATE_NONE ? 1000000u / 256u
                             : g->rate[b] > 1000000u ? 1000000u : g->rate[b];
        unsigned long long m = 0;
        if (g->rates == RATE_NONE) m = 1000000u;
        else { for (unsigned x = 0; x < 256; x++) m += g->rate[x]; if (m > 1000000u) m = 1000000u; }
        int want = h == 0 || m > h;
        if (pk.landmark != want) {
            char why[160];
            snprintf(why, sizeof why, "a declined run's landmark bit at K 0 is %d, the head member's "
                     "byte rule (h %llu, m %llu) says %d", pk.landmark, h, m, want);
            fail(g->id, "F1 (the twin on a declined run)", why);
            return;
        }
        g_dec_twin += want;
    }
    if ((g->wk == G2P_W_L1B || g->wk == G2P_W_K1B) && pk.landmark != 1)
        fail(g->id, "W-K3", "the witness's stated rates (m > h) do not reach: the bit at K 0 is 0");
    if (pk.landmark != 1) { g_wk3_zero++; return; }
    if (g->wk) printf("G2PWK3 %s site %d reached: bit 1 at K 0, checked at K -1..-32\n", g_tag, g->id);
    for (int k = -1; k >= -32; k--) {
        t.head_max = k;
        if (mf_pres_ports(art, &t, &t.pres_proof, all, &pk)) {
            fail(g->id, "W-K3", "mf_pres_ports refused a negative K");
            return;
        }
        g_wk3_cases++;
        if (pk.landmark != 1) {
            char why[160];
            snprintf(why, sizeof why, "the admission bit at K %d is %d, at K 0 it is 1 (the stated "
                     "rule max(K, 0) makes them equal)", k, pk.landmark);
            fail(g->id, "W-K3", why);
            return;
        }
    }
}

/* Generates, states, asks, lays out, defines and renders site `g` into `fs`
 * (file scope) and fills `o`. */
static void one_site(gsite *g, buf *fs, gout *o)
{
    memset(o, 0, sizeof *o);
    mf_akind kd;
    memset(&kd, 0, sizeof kd);
    kd.tag = "byte-rate";
    kd.version = 1;
    kd.present = MF_KIND_PRESENT;
    kd.digest = 1;
    kd.payload = g->rate;
    mf_analysis an = { MF_ANALYSIS_LIST_V, 1, &kd };
    const mf_analysis *anp = g->rates == RATE_NONE ? NULL : &an;
    char pfx[32];
    snprintf(pfx, sizeof pfx, "g2p%d", g->id);
    snprintf(g->names[0], sizeof g->names[0], "g2p%d_r1", g->id);
    mf_art *art = art_of(pfx, anp);
    if (!art) { fail(g->id, "the art", "refused its target or lever"); return; }

    mf_need need = g->want == G2P_P0 ? MF_REQUIRED : MF_OPTIONAL;
    mf_site s;
    site_base(&s);
    s.body = MF_BODY_ONESHOT;
    s.form = MF_FORM_STMT;
    s.op = MF_OP_ALL_PRESENT;
    s.handoff = MF_H_ON_MISS;
    s.empty = MF_EMPTY_MISS;
    s.use = MF_USE_ENTRY;
    static const uint8_t kinds[] = { MF_SK_DFA_SCAN, MF_SK_DFA_ATTEMPT, MF_SK_HYB_PF };
    s.site_kind = g->want == G2P_P0 ? MF_SK_VM_ATTEMPT : kinds[rnd(3)];
    s.on_miss_leaves = (uint8_t)g_oml;
    s.opts = g->want == G2P_P9 ? (g_deny ? "no-fd-pres-pick,no-run-verify-wide" : "no-fd-pres-pick")
           : g_deny ? "no-run-verify-wide" : NULL;
    int nofind = no_findable(g);
    s.npspan = (uint16_t)state_spans(g, need);
    s.pspans = g_ps;
    s.pres_proof = (mf_pres_proof){ -1, 0, 0, 1 };
    unsigned run = s.npspan - 1u;
    o->omin = s.pspans[run].omin;

    mf_hooks h;
    memset(&h, 0, sizeof h);
    h.fn_name = fn_name_hook;
    h.u = g;
    h.start = "search_from";
    mf_class c;

    /* P2: the proof stands for the leading check: the run's scan byte where
       its position is exact (the scan off the REPLY, asked with no proof:
       the OPTIONAL route tests the run), else the set's pick */
    if (g->want == G2P_P2) {
        mf_pres_picks pk;
        if (mf_pres_ports(art, &s, NULL, NULL, &pk)) { fail(g->id, "mf_pres_ports", "refused"); return; }
        if (mf_ask(art, &s, &h, &c)) { fail(g->id, "mf_ask (P2's lead)", "refused"); return; }
        int sc = c.pres[run].verify && c.run.has_scan ? c.run.scan : -1;
        int lead = -1;
        if (sc >= 0 && set_count(g->set[sc]) == 1) lead = set_first(g->set[sc]);
        else if (pk.set_pick >= 0)
            for (unsigned b = 0; b < 256; b++)
                if (g_ps[pk.set_pick].term[0].set[b >> 3] >> (b & 7) & 1) lead = (int)b;
        /* [r3pd FIX-4]: pcrec's real proof states `run` 0 on a run the kit
           cannot scan (run_verified is never set there): G2 states it so on
           its no-findable-position sites; every other site keeps run 1 */
        if (lead >= 0) s.pres_proof = (mf_pres_proof){ (int16_t)lead, 0, (uint8_t)!nofind, 1 };
    }

    if (mf_ask(art, &s, &h, &c)) { fail(g->id, "mf_ask (the presence links)", "refused"); return; }
    o->route = route_of(&c, run);
    if (o->route < 0) { fail(g->id, "the run's link", "no P0/P2/P3/P9 row decided it"); return; }
    g_route_sites[o->route]++;
    int tested = c.pres[run].verify;
    const char *rb = reply_bad(&c.run, g->L, tested);
    if (rb) { fail(g->id, "the run's reply (mf_ask)", rb); return; }
    /* memfn.h mf_link: on the run span `member` is 0 and UNREAD (the stretch
       is the reply's), whatever row decided it (review 2026-11-11 r1 k382
       F13: P3's row template once crossed as 1) */
    if (c.pres[run].member) {
        fail(g->id, "the run's link (mf_ask)", "`member` is not 0 on the run span");
        return;
    }

    /* R-38 Part D, THE REPLY LEVEL (part_d.md §5.1 D1's check, [r1pd F14,
       F21], [r2pd P22]), each against G2's OWN sets: the scan is never a
       wide position; a decline exactly where G2 computes one (an OPTIONAL
       route, no findable position, not dominated by P2); a REQUIRED run with
       no findable position verified whole, scan-less; a dominated no-scan
       site's every span proven (F3); a declined run's member at the HEAD
       (F2); the twin's landmark on a declined run the head's byte (F1) */
    int head = -1;
    for (unsigned i = 0; i < run; i++)
        if (c.pres[i].verify && c.pres[i].order == 0) head = (int)i;
    int dec = o->route == G2P_PD;
    if (g->wide) g_wide_sites++;
    g_nofind += nofind;
    if (c.run.has_scan && c.run.scan < g->L && !findable(g->set[c.run.scan])) {
        fail(g->id, "the run's reply", "its scan is a WIDE position (the scan is findable only)");
        return;
    }
    if (c.run.has_scan && any_wide(g)) g_scan_findable++;
    int dec_want = need == MF_OPTIONAL && nofind && o->route != G2P_P2;
    if (dec != dec_want) {
        fail(g->id, "the decline", dec ? "PD declined a run G2 finds a findable position in (or "
                                         "on a REQUIRED route)"
                                       : "a run with no findable position on an OPTIONAL, "
                                         "undominated route was not declined");
        return;
    }
    if (dec) {
        g_declines++;
        if (g->nm) {
            if (head < 0) { fail(g->id, "F2", "a declined run with a member has no HEAD"); return; }
            g_dec_member++;
        }
        if (g->assign) g_dec_assign++;
    }
    if (need == MF_REQUIRED && nofind) {
        if (!tested || c.run.has_scan || c.run.ver_lo || c.run.ver_len != g->L) {
            fail(g->id, "the scan-less REQUIRED run", "not verified whole without a scan (K66)");
            return;
        }
        g_scanless_req++;
    }
    if (o->route == G2P_P2 && nofind) {
        for (unsigned i = 0; i < s.npspan; i++)
            if (!c.pres[i].proven_by) {
                fail(g->id, "F3", "a dominated site with no findable run position leaves a span unproven");
                return;
            }
        g_dom_noscan++;
    }
    if (g_deny && tested) {
        for (unsigned j = c.run.ver_lo; j < (unsigned)c.run.ver_lo + c.run.ver_len; j++)
            if (c.run.has_scan && !findable(g->set[j])) {
                fail(g->id, "the deny (run-verify-wide)", "the verified extent holds a wide position");
                return;
            }
        g_deny_one += c.run.has_scan && c.run.ver_len == 1;
    }
    if (tested)
        for (unsigned j = c.run.ver_lo; j < (unsigned)c.run.ver_lo + c.run.ver_len; j++)
            if (!findable(g->set[j])) { g_wide_ver++; break; }

    /* W-K3, the twin, on every site (the port reads the reply's extent) */
    twin_check(g, art, &s, dec, head);

    /* THE LAYOUT (compose.c's statement rule as a host follows it, emit_dfa.c
       req_site_define): the head, ONE derived run part where the run's link
       is tested (a FUNC part stating only `fn_ref`), the rest ascending */
    static mf_pred preds[1 + 1 + 4];
    memset(preds, 0, sizeof preds);
    unsigned np = 0;
    if (head >= 0) {                    /* the head as read above (the kit's links) */
        int b = -1;
        for (unsigned x = 0; x < 256; x++)
            if (g_ps[head].term[0].set[x >> 3] >> (x & 7) & 1) b = (int)x;
        /* the head's need reads whether the run is TESTED ([r2pd P1, P6]): a
           declined run's layout is a run-less one, its head REQUIRED */
        mf_need gn = tested ? (mf_need)g_ps[head].need : MF_REQUIRED;
        o->mem[o->nmem++] = (uint8_t)b;
        preds[np].nterm = 1;
        preds[np].need = gn;
        preds[np].term[0].kind = MF_T_SET;
        preds[np].term[0].need = gn;
        set_add(preds[np].term[0].set, (unsigned)b);
        preds[np].term[0].ppm_hi = MF_PPM_FULL;
        np++;
    }
    int keepi = -1;
    if (tested) {
        preds[np].fn_ref = 1;           /* the derived run part: nothing else */
        if (g->assign) keepi = (int)np;
        np++;
    }
    for (unsigned x = 0; x < 256; x++)
        for (unsigned i = 0; i + 1 < s.npspan; i++) {
            if (!c.pres[i].verify || c.pres[i].order != 2 ||
                !(g_ps[i].term[0].set[x >> 3] >> (x & 7) & 1))
                continue;
            if (o->nmem == sizeof o->mem) {     /* an unlisted member: the driver's rule unsound */
                fail(g->id, "the member table", "more verified members than g2p_site.mem holds");
                return;
            }
            o->mem[o->nmem++] = (uint8_t)x;
            preds[np].nterm = 1;
            preds[np].need = MF_REQUIRED;
            preds[np].term[0].kind = MF_T_SET;
            preds[np].term[0].need = MF_REQUIRED;
            set_add(preds[np].term[0].set, x);
            preds[np].term[0].ppm_hi = MF_PPM_FULL;
            np++;
        }

    o->tested = tested;
    if (!tested) {
        /* C2's third clause: the run's link is untested, so no run part; the
           control lays the derived part out anyway and the kit must refuse it.
           Each untested route counts its own pair ([r3pd FIX-7]): P2's, and
           the DECLINE's ([r2pd P6]), whose site is then laid out WITHOUT a
           run part (members only, the head by the kit's links), rendered and
           checked; a declined site with no verified member has no pre-check */
        if (o->route == G2P_P2) g_p2_untested++;
        if (dec) g_dec_untested++;
        mf_art *ac = art_of(pfx, anp);
        mf_pred cp[1];
        memset(cp, 0, sizeof cp);
        cp[0].fn_ref = 1;
        mf_site sc = s;
        sc.npred = 1;
        sc.preds = cp;
        buf t = { 0 };
        mf_sink sk = mk_sink(&t);
        uint32_t hd;
        if (ac && mf_define(ac, &sc, &h, &sk, &hd)) {
            if (o->route == G2P_P2) g_p2_refused++;
            if (dec) g_dec_refused++;
        } else fail(g->id, "C2 (no run part where the link is untested)",
                    "a run part laid out on an untested link was not refused");
        free(t.p);
        if (!dec) return;
        if (!np) { g_dec_noprecheck++; return; }
    }

    /* THE STATEMENT RULE's other two refusals (review 2026-11-11 r1 k382
       F14), each a control on a site whose run link IS tested, each refused
       by ITS rule (the error names it, so another refusal is no pass):
       (ii) the layout drops the derived run part (compose.c
       pres_layout_check); (iii) the layout carries a SECOND derived part
       (window.c wf_parts_check) */
    if (tested) {
        static mf_pred cp[1 + 2 + 4];
        const char *want[2] = { "its run part (the FUNC part the kit derives) is not where",
                                "a second derived run part" };
        for (int v = 0; v < 2; v++) {
            unsigned n2 = 0;
            for (unsigned i = 0; i < np; i++) {
                if (preds[i].fn_ref && v == 0) continue;
                cp[n2++] = preds[i];
                if (preds[i].fn_ref) cp[n2++] = preds[i];   /* (iii): twice */
            }
            mf_art *ac = art_of(pfx, anp);
            mf_site sc = s;
            sc.npred = (uint16_t)n2;
            sc.preds = cp;
            sc.handoff = MF_H_ON_MISS;
            sc.ret_pred = MF_NO_PRED;
            buf t = { 0 };
            mf_sink sk = mk_sink(&t);
            uint32_t hd;
            const char *err = ac && mf_define(ac, &sc, &h, &sk, &hd) ? mf_art_error(ac) : NULL;
            if (err && strstr(err, want[v])) { if (v) g_ctl_two++; else g_ctl_nopart++; }
            else fail(g->id, v ? "F14 (iii): a second derived run part" : "F14 (ii): no run part on a tested link",
                      err ? err : "not refused");
            free(t.p);
        }
    }

    s.npred = (uint16_t)np;
    s.preds = preds;
    s.handoff = keepi >= 0 ? MF_H_ASSIGN : MF_H_ON_MISS;
    s.ret_pred = keepi >= 0 ? (uint8_t)keepi : MF_NO_PRED;
    /* K (§3.2): the largest offset of the landmark's position 0 from the
       attempt start, signed, never below omin (the smallest) */
    s.head_max = keepi >= 0 ? (int64_t)g->omin + g->kdraw : 0;
    o->assign = keepi >= 0;
    o->head_max = s.head_max;

    buf def = { 0 }, ent = { 0 }, ree = { 0 }, hl = { 0 };
    mf_sink sd = mk_sink(&def), se = mk_sink(&ent), sr = mk_sink(&ree), sh = mk_sink(&hl);
    uint32_t handle;
    if (mf_define(art, &s, &h, &sd, &handle)) {
        fail(g->id, "mf_define", mf_art_error(art));
        return;
    }
    /* R-38 Part D D3's JOIN (part_d.md §5.1 D3 [r3pd RDY-4]): under
       G2P_G2SITE (the run against the trace kit) each site's define is
       closed by `G2SITE id=N` on stderr, the stream the kit's MFTRACE
       records share, so every `run_part_terms` record between two G2SITE
       lines is site N's (the kit's art= is its own trace id) */
    if (g_g2site) fprintf(stderr, "G2SITE id=%d\n", g->id);
    g_layout_ok++;
    g_dec_rendered += dec;
    g_deny_sites += g_deny;
    /* FAM-2: the reply the define kept (mf_defined), held equal to the ask's;
       every reader below reads it */
    mf_result dr;
    if (mf_defined(art, handle, &dr)) { fail(g->id, "mf_defined", mf_art_error(art)); return; }
    if (memcmp(&dr.cls.run, &c.run, sizeof c.run)) {
        fail(g->id, "the run's reply", "mf_defined's mf_class.run differs from mf_ask's");
        return;
    }
    snprintf(o->forms, sizeof o->forms, "%s", dr.form_id);
    /* THE GENERIC PASS (on_miss_leaves 0; review 2026-11-11 r1 k382 F1): no
       pre-check row admits the site, so the generic row renders it, its run
       part inline (no function); every site of the pass must be generic's,
       and none of another pass may be */
    int gen = !strcmp(dr.form_id, "generic");
    g_generic += gen;
    if (gen != !g_oml) {
        fail(g->id, "the define's row", g_oml ? "the generic row rendered an on_miss_leaves 1 site"
                                              : "an on_miss_leaves 0 site not rendered by the generic row");
        return;
    }
    o->has_scan = dr.cls.run.has_scan;
    o->scan = dr.cls.run.scan;
    o->ver_lo = dr.cls.run.ver_lo;
    o->ver_len = dr.cls.run.ver_len;
    mf_hooks u;
    memset(&u, 0, sizeof u);
    u.s = "subject"; u.n = "subject_length"; u.lo = "search_from"; u.indent = "    ";
    u.on_miss = "return 0;";
    u.fn_name = fn_name_hook; u.u = g;
    if (o->assign) { u.result = "handoff_position"; u.result_decl = "size_t "; u.miss = MF_MISS_N; }
    mf_result res;
    if (mf_use(art, handle, &u, &se, &res)) { fail(g->id, "mf_use (entry)", mf_art_error(art)); return; }
    if (o->assign) {
        mf_hooks r = u;
        r.lo = "posvar"; r.result = "landmark_position"; r.result_decl = NULL;
        if (mf_use(art, handle, &r, &sr, &res)) { fail(g->id, "mf_use (re-entry)", mf_art_error(art)); return; }
    }
    if (mf_flush_helpers(art, &sh)) { fail(g->id, "mf_flush_helpers", mf_art_error(art)); return; }
    g_inc |= mf_includes(art);
    if (mf_art_end(art, NULL)) { fail(g->id, "mf_art_end", mf_art_error(art)); return; }

    /* the census (K35): the populations K38-2 adds */
    if (o->omin < 0) g_neg_omin++;
    if (o->omin <= -8 && o->omin >= -32) g_wk4_omin++;
    if (o->assign && o->omin < 0) g_k_signed++;
    if (o->assign && o->head_max <= 0 && o->omin < 0) g_k_nonpos++;
    if (o->ver_len < g->L) g_partial++;
    /* C2's decision plant (the reply says ver_len + 1) can show only where
       the extent ends before the run does: its reach */
    if (o->ver_lo + o->ver_len < g->L) g_room++;

    /* the file scope: the kit's definitions and helpers; the rendered part's
       direct call; then every later call through the recorder */
    /* the SIMD levels' population (a census of the kit's own text, never a
       verdict): a run part with a w16 or a w32 arm */
    g_simd16 += def.p && strstr(def.p, "__w16(const") != NULL;
    g_simd32 += def.p && strstr(def.p, "__w32(const") != NULL;
    bprintf(fs, "/* ---- site %d (%s) ---- */\n", g->id, g_tag);
    bputs(fs, def.p ? def.p : "");
    bputs(fs, hl.p ? hl.p : "");
    char call[64];
    snprintf(call, sizeof call, "%s(", g->names[0]);
    o->fnok = def.p && strstr(def.p, call) != NULL;
    if (!o->fnok && g_oml && tested) fail(g->id, "the derived run part", "the define rendered no function of its name");
    if (o->fnok && !tested) fail(g->id, "the declined site", "the define rendered a run part");
    else if (o->fnok) {
        bprintf(fs, "size_t g2p_part_%d_0(const unsigned char *s, size_t n, size_t lo)\n"
                    "{ return %s(s, n, lo); }\n", g->id, g->names[0]);
        bprintf(fs, "#define %s(s_, n_, lo_) g2p_rec(%d, 0, %s, (s_), (n_), (lo_))\n",
                g->names[0], g->id, g->names[0]);
    }
    bprintf(fs, "int g2p_entry_%d(const unsigned char *subject, size_t subject_length, "
                "size_t search_from, size_t *out)\n{\n%s    *out = %s;\n    return 1;\n}\n",
            g->id, ent.p ? ent.p : "", o->assign ? "handoff_position" : "search_from");
    if (o->assign)
        bprintf(fs, "int g2p_reentry_%d(const unsigned char *subject, size_t subject_length, "
                    "size_t posvar, size_t *out)\n{\n    size_t landmark_position;\n%s"
                    "    *out = landmark_position;\n    return 1;\n}\n",
                g->id, ree.p ? ree.p : "");
    free(def.p); free(ent.p); free(ree.p); free(hl.p);
    o->rendered = 1;
}

int main(int argc, char **argv)
{
    if (argc < 6 || argc > 9) {
        fprintf(stderr, "usage: g2_pres_gen SEED NSITES OUTDIR TARGET LEVER [ON_MISS_LEAVES "
                        "[NWIDE [DENY]]]\n");
        return 2;
    }
    g_rng = strtoull(argv[1], NULL, 10) * 2654435761ull + 0x7072657365ull;
    g_rng2 = strtoull(argv[1], NULL, 10) * 40503ull + 0x77696465ull;
    int nwide = argc > 7 ? atoi(argv[7]) : 0;  /* the WIDE stream's sites (R-38 Part D), LAST */
    g_deny = argc > 8 && atoi(argv[8]);
    int nsites = atoi(argv[2]);
    char err[200];
    g_target = mf_target_parse(argv[4], strlen(argv[4]), err, sizeof err);
    if (!g_target) { fprintf(stderr, "g2p: target %s: %s\n", argv[4], err); return 2; }
    g_lever = atoi(argv[5]);
    if (argc >= 7) g_oml = atoi(argv[6]);
    g_g2site = getenv("G2P_G2SITE") != NULL;
    char tag[64];
    snprintf(tag, sizeof tag, "%s.%s%s%s", argv[4], g_lever ? "lever" : "default", g_oml ? "" : ".oml0",
             g_deny ? ".deny" : "");
    g_tag = tag;
    mf_finder_rows(&g_rows);

    int nw = 24;                        /* the lever witnesses, first */
    int nwk = G2P_W_N - 1;              /* the §3.5 witness sites, LAST */
    int total = nw + nsites + nwk + nwide;
    gsite *gs = calloc((size_t)total, sizeof *gs);
    gout *os = calloc((size_t)total, sizeof *os);
    buf fs = { 0 };
    for (int i = 0; i < total; i++) {
        gsite *g = &gs[i];
        g->id = i;
        g->witness = i < nw;
        if (g->witness) {
            gen_witness(g);
            g->want = i % 2 ? G2P_P3 : G2P_P0;
            g->rates = RATE_UNIFORM;
            g->assign = 0;
        } else if (i >= nw + nsites + nwk) {
            /* THE WIDE STREAM (rnd2 only): its own layouts, members, routes, rates */
            gen_wide(g);
            g->nm = rnd2(4) ? rnd2(4) : 0;
            for (unsigned m = 0; m < g->nm; m++) {
                const uint8_t *ps = g->set[rnd2(g->L)];
                unsigned c = set_count(ps), k = rnd2(c);
                int b = -1;
                for (unsigned x = 0; x < 256 && b < 0; x++) if (set_has(ps, x) && !k--) b = (int)x;
                g->members[m] = (uint8_t)(rnd2(3) ? (unsigned)b : rnd2(256));
            }
            for (unsigned a = 0; a < g->nm; a++)        /* distinct members */
                for (unsigned b = a + 1; b < g->nm; b++)
                    if (g->members[b] == g->members[a]) g->members[b] = (uint8_t)(g->members[b] + 1 + b);
            static const int wwants[] = { G2P_P0, G2P_P3, G2P_P3, G2P_P9, G2P_P2 };
            g->want = wwants[i % 5];
            g->rates = (int)rnd2(RATE_N);
            g->assign = rnd2(3) != 0;
            g->omin = rnd2(2) ? 0 : -(int32_t)(1 + rnd2(40));
            g->kdraw = (int)rnd2(40);
        } else if (i >= nw + nsites) {
            gen_wk(g, 1 + (i - nw - nsites));
        } else {
            gen_run(g);
            g->nm = rnd(4) ? rnd(4) : 0;
            for (unsigned m = 0; m < g->nm; m++)
                g->members[m] = (uint8_t)(rnd(3) ? g->run[rnd(g->L)] | (rnd(2) ? 0x20 : 0) : rnd(256));
            for (unsigned a = 0; a < g->nm; a++)        /* distinct members */
                for (unsigned b = a + 1; b < g->nm; b++)
                    if (g->members[b] == g->members[a]) g->members[b] = (uint8_t)(g->members[b] + 1 + b);
            static const int wants[] = { G2P_P0, G2P_P3, G2P_P3, G2P_P9, G2P_P2 };
            g->want = wants[i % 5];
            g->rates = (int)rnd(RATE_N);
            g->assign = rnd(3) != 0;
            g->omin = gen_omin();
            g->kdraw = (int)rnd(40);
        }
        if (!g->wide) sets_of_run(g);
        gen_rates(g);
        if (g->wide) {
            /* the background (§5.2): a byte in no position's set, else "no
               background"; F24's population: on a RATED art, a wide position
               LIGHTER than every findable one (p1's reach), and its stratum of
               three or more members ([r3pd FIX-2]) */
            uint8_t u[32] = { 0 };
            for (unsigned j = 0; j < g->L; j++) for (unsigned x = 0; x < 32; x++) u[x] |= g->set[j][x];
            g_nobg += set_count(u) == 256;
            if (g->rates != RATE_NONE) {
                unsigned long long fmin = ~0ull, wmin = ~0ull;
                unsigned wc = 0;
                for (unsigned j = 0; j < g->L; j++) {
                    unsigned long long ms = 0;
                    for (unsigned b = 0; b < 256; b++) if (set_has(g->set[j], b)) ms += g->rate[b];
                    if (findable(g->set[j])) { if (ms < fmin) fmin = ms; }
                    else if (ms < wmin) { wmin = ms; wc = set_count(g->set[j]); }
                }
                if (fmin != ~0ull && wmin < fmin) { g_f24++; g_f24_3 += wc >= 3; }
            }
        }
        one_site(g, &fs, &os[i]);
        if (g->wk && !os[i].rendered) fail(g->id, "a §3.5 witness site", "not rendered");
        if (g->wk && os[i].route != G2P_P0) fail(g->id, "a §3.5 witness site", "its route is not P0");
    }

    char path[4096];
    snprintf(path, sizeof path, "%s/g2p_sites.c", argv[3]);
    FILE *c = fopen(path, "w");
    if (!c) { perror(path); return 2; }
    fputs("/* generated by memfn/tests/g2/g2_pres_gen.c: do not edit */\n"
          "#include <stddef.h>\n#include <stdint.h>\n#include <string.h>\n"
          "#include \"g2_pres.h\"\n\n", c);
    if (g_target->family) fputs(mf_family_c_of(g_target->family)->guard, c);
    for (uint32_t bit = 1; bit; bit <<= 1) {
        if (!(g_inc & bit)) continue;
        const char *line = mf_include_c(bit);
        if (!line) { fprintf(stderr, "g2p: include bit 0x%x has no spelling\n", (unsigned)bit); g_fails++; }
        else fputs(line, c);
    }
    /* the recorder's libc reads (g2_pres_run.c): every read the kit's text
       makes through memchr, memcmp or memcpy is recorded byte by byte */
    fputs("#ifdef G2P_REC\n"
          "void *g2p_memchr(const void *p, int c, size_t n);\n"
          "int g2p_memcmp(const void *a, const void *b, size_t n);\n"
          "void *g2p_memcpy(void *d, const void *s, size_t n);\n"
          "#define memchr g2p_memchr\n#define memcmp g2p_memcmp\n#define memcpy g2p_memcpy\n"
          "#endif\n", c);
    fputs(mf_target_c_of(g_target)->region_open, c);
    fputs("/* G2P KIT TEXT BEGIN */\n", c);
    fputs(fs.p ? fs.p : "", c);
    fputs("/* G2P KIT TEXT END */\n", c);
    fputs(mf_target_c_of(g_target)->region_close, c);
    for (int i = 0; i < total; i++) {
        if (!os[i].rendered) continue;
        if (os[i].fnok) fprintf(c, "size_t g2p_part_%d_0(const unsigned char *, size_t, size_t);\n", i);
        fprintf(c, "int g2p_entry_%d(const unsigned char *, size_t, size_t, size_t *);\n", i);
        if (os[i].assign)
            fprintf(c, "int g2p_reentry_%d(const unsigned char *, size_t, size_t, size_t *);\n", i);
    }
    for (int i = 0; i < total; i++) {      /* the WIDE stream's sets (none on today's) */
        if (!os[i].rendered || !gs[i].wide) continue;
        fprintf(c, "static const uint8_t g2p_sets_%d[%u][32] = {", i, gs[i].L);
        for (unsigned j = 0; j < gs[i].L; j++) {
            fputs(j ? ", {" : "{", c);
            for (unsigned x = 0; x < 32; x++) fprintf(c, "%s%u", x ? "," : "", gs[i].set[j][x]);
            fputc('}', c);
        }
        fputs("};\n", c);
    }
    fprintf(c, "const g2p_site g2p_sites[] = {\n");
    int n = 0;
    for (int i = 0; i < total; i++) {
        const gout *o = &os[i];
        const gsite *g = &gs[i];
        if (!o->rendered) continue;
        n++;
        fprintf(c, "    { %d, \"%s\", %d, %d, %d, %d, %d, %u, %d, %lld, {", i, tag, o->route, o->assign,
                g->witness, g_lever, g->wk, g->L, (int)o->omin, (long long)o->head_max);
        for (unsigned j = 0; j < g->L; j++) fprintf(c, "%s%u", j ? "," : "", g->run[j]);
        fputs("}, {", c);
        for (unsigned j = 0; j < g->L; j++) fprintf(c, "%s%u", j ? "," : "", g->mask[j]);
        fprintf(c, "}, %d, %d, %u, %u, %d, {{ 0, %u, ", o->has_scan, o->scan, o->ver_lo, o->ver_len,
                o->tested, g->L);
        if (o->fnok) fprintf(c, "g2p_part_%d_0", i);
        else fputs("NULL", c);
        fprintf(c, ", %d, %u, %u }}, g2p_entry_%d, ", o->scan, o->ver_lo, o->ver_len, i);
        if (o->assign) fprintf(c, "g2p_reentry_%d", i);
        else fputs("NULL", c);
        fprintf(c, ", \"%s\", %u, {", o->forms, o->nmem);
        for (unsigned j = 0; j < o->nmem; j++) fprintf(c, "%s%u", j ? "," : "", o->mem[j]);
        fputs("} },\n", c);
    }
    fprintf(c, "};\nconst int g2p_nsites = %d;\n", n);
    int nw2 = 0;                        /* the WIDE stream's table (g2_pres.h), only if any */
    for (int i = 0; i < total; i++) nw2 += os[i].rendered && gs[i].wide;
    if (nw2) {
        fputs("const g2p_wide g2p_wides[] = {\n", c);
        for (int i = 0; i < total; i++)
            if (os[i].rendered && gs[i].wide) fprintf(c, "    { %d, g2p_sets_%d },\n", i, i);
        fprintf(c, "};\nconst int g2p_nwides = %d;\n", nw2);
    }
    fclose(c);

    /* the generator's census (the runner's floors read it) */
    printf("G2PGEN %s sites=%d rendered=%d layout_ok=%ld P0=%ld P2=%ld P3=%ld P9=%ld "
           "p2_untested=%ld p2_refused=%ld simd16=%ld simd32=%ld neg_omin=%ld wk4_omin=%ld "
           "k_signed=%ld k_nonpos=%ld partial=%ld room=%ld wk3_sites=%ld wk3_zero=%ld wk3_cases=%ld "
           "generic=%ld ctl_nopart=%ld ctl_two=%ld\n",
           tag, total, n, g_layout_ok, g_route_sites[G2P_P0], g_route_sites[G2P_P2],
           g_route_sites[G2P_P3], g_route_sites[G2P_P9], g_p2_untested, g_p2_refused, g_simd16,
           g_simd32, g_neg_omin, g_wk4_omin, g_k_signed, g_k_nonpos, g_partial, g_room, g_wk3_sites,
           g_wk3_zero, g_wk3_cases, g_generic, g_ctl_nopart, g_ctl_two);
    /* R-38 Part D's census (part_d.md §5.1.1; the runner's floors read it) */
    printf("G2PWIDE %s wide_sites=%ld wide_ver=%ld nofind=%ld nobg=%ld f24=%ld f24_3=%ld "
           "scan_findable=%ld PD=%ld declines=%ld dec_member=%ld dec_assign=%ld dec_twin=%ld "
           "dec_untested=%ld dec_refused=%ld dec_rendered=%ld dec_noprecheck=%ld scanless_req=%ld "
           "dom_noscan=%ld deny_sites=%ld deny_one=%ld r41=%ld r41_flip=%ld\n", tag, g_wide_sites, g_wide_ver, g_nofind,
           g_nobg, g_f24, g_f24_3, g_scan_findable, g_route_sites[G2P_PD], g_declines, g_dec_member,
           g_dec_assign, g_dec_twin, g_dec_untested, g_dec_refused, g_dec_rendered, g_dec_noprecheck,
           g_scanless_req, g_dom_noscan, g_deny_sites, g_deny_one, g_r41, g_r41_flip);
    printf("g2_pres_gen failures: %d\n", g_fails);
    return g_fails ? 1 : 0;
}
