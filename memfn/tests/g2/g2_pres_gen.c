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

/* ---- a generated site -------------------------------------------------------- */

enum { RATE_NONE, RATE_SKEW, RATE_UNIFORM, RATE_TIES, RATE_N, RATE_FIXED = RATE_N };

typedef struct {
    int      id, want, witness, wk;
    unsigned L;
    uint8_t  run[G2P_MAXRUN], mask[G2P_MAXRUN];
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

static void gen_rates(gsite *g)
{
    if (g->rates == RATE_FIXED) return;
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
    return (b & g->mask[j]) == g->run[j];
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
static int g_oml = 1;                   /* the sites' on_miss_leaves (argv[6]) */
static const char *g_tag;
static uint32_t g_inc;
static int g_fails;
static long g_generic;              /* sites mf_define rendered by the generic row */
static long g_ctl_nopart, g_ctl_two;  /* F14's two layout controls, refused as ruled */
static long g_route_sites[G2P_NROUTE], g_p2_untested, g_p2_refused, g_layout_ok, g_simd16, g_simd32;
static long g_neg_omin, g_wk4_omin, g_k_nonpos, g_k_signed, g_partial, g_room, g_wk3_sites,
            g_wk3_cases, g_wk3_zero;
static mf_finder_listing g_rows;

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
         : !strcmp(id, "P9") ? G2P_P9 : -1;
}

typedef struct {
    int      rendered, route, assign, has_scan, scan, fnok;
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
static void twin_check(gsite *g, const mf_art *art, const mf_site *s)
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
    s.opts = g->want == G2P_P9 ? "no-fd-pres-pick" : NULL;
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
        if (sc >= 0 && g->mask[sc] == 0xFF) lead = g->run[sc];
        else if (pk.set_pick >= 0)
            for (unsigned b = 0; b < 256; b++)
                if (g_ps[pk.set_pick].term[0].set[b >> 3] >> (b & 7) & 1) lead = (int)b;
        if (lead >= 0) s.pres_proof = (mf_pres_proof){ (int16_t)lead, 0, 1, 1 };
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

    /* W-K3, the twin, on every site (the port reads the reply's extent) */
    twin_check(g, art, &s);

    /* THE LAYOUT (compose.c's statement rule as a host follows it, emit_dfa.c
       req_site_define): the head, ONE derived run part where the run's link
       is tested (a FUNC part stating only `fn_ref`), the rest ascending */
    static mf_pred preds[1 + 1 + 4];
    memset(preds, 0, sizeof preds);
    unsigned np = 0;
    int head = -1;
    for (unsigned i = 0; i + 1 < s.npspan; i++)
        if (c.pres[i].verify && c.pres[i].order == 0) head = (int)i;
    if (head >= 0) {
        int b = -1;
        for (unsigned x = 0; x < 256; x++)
            if (g_ps[head].term[0].set[x >> 3] >> (x & 7) & 1) b = (int)x;
        mf_need gn = (mf_need)g_ps[head].need;
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

    if (!tested) {
        /* C2's third clause: the run's link is untested, so no run part; the
           control lays the derived part out anyway and the kit must refuse it */
        if (o->route == G2P_P2) g_p2_untested++;
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
        if (ac && mf_define(ac, &sc, &h, &sk, &hd)) g_p2_refused++;
        else fail(g->id, "C2 (no run part where the link is untested)",
                  "a run part laid out on an untested link was not refused");
        free(t.p);
        return;
    }

    /* THE STATEMENT RULE's other two refusals (review 2026-11-11 r1 k382
       F14), each a control on a site whose run link IS tested, each refused
       by ITS rule (the error names it, so another refusal is no pass):
       (ii) the layout drops the derived run part (compose.c
       pres_layout_check); (iii) the layout carries a SECOND derived part
       (window.c wf_parts_check) */
    {
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
    g_layout_ok++;
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
    if (!o->fnok && g_oml) fail(g->id, "the derived run part", "the define rendered no function of its name");
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
    if (argc != 6 && argc != 7) {
        fprintf(stderr, "usage: g2_pres_gen SEED NSITES OUTDIR TARGET LEVER [ON_MISS_LEAVES]\n");
        return 2;
    }
    g_rng = strtoull(argv[1], NULL, 10) * 2654435761ull + 0x7072657365ull;
    int nsites = atoi(argv[2]);
    char err[200];
    g_target = mf_target_parse(argv[4], strlen(argv[4]), err, sizeof err);
    if (!g_target) { fprintf(stderr, "g2p: target %s: %s\n", argv[4], err); return 2; }
    g_lever = atoi(argv[5]);
    if (argc == 7) g_oml = atoi(argv[6]);
    char tag[64];
    snprintf(tag, sizeof tag, "%s.%s%s", argv[4], g_lever ? "lever" : "default", g_oml ? "" : ".oml0");
    g_tag = tag;
    mf_finder_rows(&g_rows);

    int nw = 24;                        /* the lever witnesses, first */
    int nwk = G2P_W_N - 1;              /* the §3.5 witness sites, LAST */
    int total = nw + nsites + nwk;
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
        gen_rates(g);
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
        fprintf(c, "}, %d, %d, %u, %u, 1, {{ 0, %u, ", o->has_scan, o->scan, o->ver_lo, o->ver_len,
                g->L);
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
    printf("g2_pres_gen failures: %d\n", g_fails);
    return g_fails ? 1 : 0;
}
