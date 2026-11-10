/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text (G2's presence family,
 *   lane k382a, R-38 K38-2a).
 *
 * memfn/tests/g2/g2_pres_gen.c — G2'S PRESENCE FAMILY, THE GENERATOR (the only
 * file of the family that calls the kit; docs/design/memfn/span_runs_sheet.md
 * rev 1.3 §5's K38-2a row, §2.4 C2, §3.3, §3.5). It GENERATES pre-check sites
 * in TODAY's statement form (MF_SITE_ABI 26: set-member spans and the whole
 * run one span, `omin` 0, K >= 0), states them as a host does (the presence
 * spans, the start search's proof, the consumer kind), asks the kit's
 * presence links (mf_ask), LAYS THE PARTS OUT from the links as a host does
 * (the head member, the run's window and, where the link keeps it whole, the
 * whole run, each a FUNC part with its own window statement, then the rest
 * members), defines the site and renders its two uses: the ENTRY (lo the
 * activation's origin) and, on an ASSIGN site, the RE-ENTRY (lo another
 * position). Per route, by the PRES row that decided the run's link:
 *   P0  every span REQUIRED (the VM attempt loop's consumer kind);
 *   P3  every span OPTIONAL (the pick: the run's window verified);
 *   P9  OPTIONAL under `--memfn=no-fd-pres-pick` (the run verified whole);
 *   P2  OPTIONAL, the proof standing for the leading check: nothing is
 *       verified, so the host lays out no run part (C2's third clause), and a
 *       layout WITH one is refused (the control).
 * Rates: none, skewed, uniform (every byte one rate: `--analysis=uniform`'s
 * regime, all ties) or tie-heavy over the site's own bytes.
 *
 * Writes OUT/g2p_sites.c: TARGET's family guard, the headers the renderings'
 * mf_includes name, the recorder's wrappers of the libc reads (G2P_REC), the
 * target's region around every definition, a direct call of each rendered
 * run part (`g2p_part_<id>_<k>`, the classifier's), then `#define <fn>(...)`
 * routing every later call of the part through the recorder (g2p_rec), then
 * the ENTRY and RE-ENTRY wrappers; and the site table (g2_pres.h): the run
 * AS GENERATED, the parts AS LAID OUT, and the kit's public replies
 * (mf_pres_ports' scan and window, mf_wdecide's member and stretch for each
 * part's statement), never anything read from the kit's text.
 * THE LEVER WITNESSES (plant C): a run of distinct exact bytes under the
 * uniform rates, every position a tie; the driver reads the scan offset the
 * TEXT uses and holds it to the stated rule (the incumbent: the rightmost;
 * under `run-tie-left`: the leftmost).
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

enum { RATE_NONE, RATE_SKEW, RATE_UNIFORM, RATE_TIES, RATE_N };

typedef struct {
    int      id, want, witness;
    unsigned L;
    uint8_t  run[G2P_MAXRUN], mask[G2P_MAXRUN];
    unsigned nm;
    uint8_t  members[4];
    int      rates, assign;
    uint32_t rate[256];
    char     names[G2P_MAXPART][40];
} gsite;

/* the run: bytes from a small alphabet (ties and repeats), mostly exact,
   a fifth of the positions a one-bit cube (a run position is one member or
   a pair, the R shape mf_wdecide states: a two-bit cube is not R); a
   quarter of the runs CASELESS (every letter its case pair, `(?i)`'s run):
   the only runs whose scan is a pair, the SIMD rows' shape (vrun.c rides
   over fn-pair) */
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

static void gen_rates(gsite *g)
{
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

/* the presence spans a host states (emit_dfa.c req_pres_spans' shape): the
   members in descending byte order, one one-byte span each (the last one in
   pattern order states the member count, the others UNKNOWN), the whole run
   last; every span `need`, omin 0 */
static mf_pred g_ps[5];
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
        g_ps[k].member_order = order[i] == g->members[g->nm - 1] ? (uint16_t)g->nm
                                                                  : (uint16_t)MF_ORDER_UNKNOWN;
    }
    int exact = 1;
    for (unsigned j = 0; j < g->L; j++) exact &= g->mask[j] == 0xFF;
    mf_term *t = &g_ps[k].term[0];
    t->kind = MF_T_RUN;
    t->need = need;
    t->run = g->run;
    t->mask = exact ? NULL : g->mask;
    t->run_len = g->L;
    t->ppm_hi = MF_PPM_FULL;
    k++;
    for (unsigned i = 0; i < k; i++) {
        g_ps[i].nterm = 1;
        g_ps[i].need = need;
        g_ps[i].plan_hint = MF_NO_PRED;
        g_ps[i].span_class = MF_SPAN_PRESENCE;
    }
    return k;
}

/* a run part's window statement: one alternative, no entry fact, one span of
   positions [at, at + len) of the run (each its byte's cube), core all,
   verify YES (emit_dfa.c req_part_window's) */
typedef struct { mf_walt alt; mf_wspan sp; } gwin;
static void state_window(const gsite *g, unsigned at, unsigned len, gwin *w)
{
    memset(w, 0, sizeof *w);
    w->sp.start = 0;
    w->sp.len = (uint8_t)len;
    w->sp.verify = MF_VERIFY_YES;
    w->sp.core = MF_CORE_STATED;
    w->sp.core_lo = 0;
    w->sp.core_len = (uint8_t)len;
    for (unsigned j = 0; j < len; j++)
        for (unsigned b = 0; b < 256; b++)
            if ((b & g->mask[at + j]) == g->run[at + j]) set_add(w->sp.set[j], b);
    w->alt.entry = MF_ENTRY_NONE;
    w->alt.nspan = 1;
    w->alt.spans = &w->sp;
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
static const char *g_tag;
static uint32_t g_inc;
static int g_fails;
static long g_route_sites[G2P_NROUTE], g_p2_untested, g_p2_refused, g_layout_ok, g_simd16, g_simd32;
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
    int      rendered, route, assign, scan, member[G2P_MAXPART];
    unsigned ver_lo, ver_len, nparts, at[G2P_MAXPART], len[G2P_MAXPART], plo[G2P_MAXPART],
             plen[G2P_MAXPART], fnref[G2P_MAXPART], fnok[G2P_MAXPART];
    char     forms[48];
} gout;

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
    snprintf(g->names[1], sizeof g->names[1], "g2p%d_r2", g->id);
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
    s.on_miss_leaves = 1;
    s.opts = g->want == G2P_P9 ? "no-fd-pres-pick" : NULL;
    s.npspan = (uint16_t)state_spans(g, need);
    s.pspans = g_ps;
    s.pres_proof = (mf_pres_proof){ -1, 0, 0, 1 };
    unsigned run = s.npspan - 1u;

    /* P2: the proof stands for the leading check (its byte, the run proven) */
    mf_pres_picks pk;
    if (mf_pres_ports(art, &s, NULL, NULL, &pk)) { fail(g->id, "mf_pres_ports", "refused"); return; }
    if (g->want == G2P_P2) {
        int lead = g->mask[pk.run_scan] == 0xFF ? g->run[pk.run_scan]
                 : pk.set_pick >= 0 ? g->members[0] : -1;
        if (g->mask[pk.run_scan] != 0xFF && pk.set_pick >= 0) {
            for (unsigned b = 0; b < 256; b++)
                if (g_ps[pk.set_pick].term[0].set[b >> 3] >> (b & 7) & 1) lead = (int)b;
        }
        if (lead >= 0) s.pres_proof = (mf_pres_proof){ (int16_t)lead, 0, 1, 1 };
    }
    if (mf_pres_ports(art, &s, &s.pres_proof, NULL, &pk)) { fail(g->id, "mf_pres_ports", "refused"); return; }

    mf_hooks h;
    memset(&h, 0, sizeof h);
    h.fn_name = fn_name_hook;
    h.u = g;
    h.start = "search_from";
    mf_class c;
    if (mf_ask(art, &s, &h, &c)) { fail(g->id, "mf_ask (the presence links)", "refused"); return; }
    o->route = route_of(&c, run);
    if (o->route < 0) { fail(g->id, "the run's link", "no P0/P2/P3/P9 row decided it"); return; }
    g_route_sites[o->route]++;
    o->scan = pk.run_scan;

    /* THE LAYOUT (compose.c's rule as a host follows it, emit_dfa.c
       req_site_define): the head, the run's window, the whole run where the
       link keeps it whole and it is longer, the rest ascending */
    static mf_pred preds[3 + 4];
    static gwin wins[G2P_MAXPART];
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
        preds[np].nterm = 1;
        preds[np].need = gn;
        preds[np].term[0].kind = MF_T_SET;
        preds[np].term[0].need = gn;
        set_add(preds[np].term[0].set, (unsigned)b);
        preds[np].term[0].ppm_hi = MF_PPM_FULL;
        np++;
    }
    int keepi = -1;
    if (c.pres[run].verify) {
        unsigned at = c.pres[run].member ? c.pres[run].member - 1u : (unsigned)pk.run_window;
        unsigned len = g->L - at < MF_PRES_WINDOW ? g->L - at : MF_PRES_WINDOW;
        o->ver_lo = c.pres[run].member ? at : 0;
        o->ver_len = c.pres[run].member ? len : g->L;
        o->at[0] = at; o->len[0] = len; o->nparts = 1;
        if (c.pres[run].member == 0 && g->L > len) {
            o->at[1] = 0; o->len[1] = g->L; o->nparts = 2;
        }
        for (unsigned k = 0; k < o->nparts; k++) {
            state_window(g, o->at[k], o->len[k], &wins[k]);
            preds[np].fn_ref = k + 1;
            preds[np].nalt = 1;
            preds[np].alts = &wins[k].alt;
            preds[np].wfloor = MF_WFLOOR_SUBJECT;
            o->fnref[k] = k + 1;
            if (g->assign && (keepi < 0 || rnd(2))) keepi = (int)np;
            np++;
        }
    }
    for (unsigned x = 0; x < 256; x++)
        for (unsigned i = 0; i + 1 < s.npspan; i++) {
            if (!c.pres[i].verify || c.pres[i].order != 2 ||
                !(g_ps[i].term[0].set[x >> 3] >> (x & 7) & 1))
                continue;
            preds[np].nterm = 1;
            preds[np].need = MF_REQUIRED;
            preds[np].term[0].kind = MF_T_SET;
            preds[np].term[0].need = MF_REQUIRED;
            set_add(preds[np].term[0].set, x);
            preds[np].term[0].ppm_hi = MF_PPM_FULL;
            np++;
        }

    if (!c.pres[run].verify) {
        /* C2's third clause: the run's link is untested, so no run part; the
           control lays one out anyway (the window, as P3 would) and the kit
           must refuse it */
        if (o->route == G2P_P2) g_p2_untested++;
        mf_art *ac = art_of(pfx, anp);
        mf_pred cp[1];
        memset(cp, 0, sizeof cp);
        unsigned len = g->L < MF_PRES_WINDOW ? g->L : MF_PRES_WINDOW;
        state_window(g, 0, len, &wins[0]);
        cp[0].fn_ref = 1;
        cp[0].nalt = 1;
        cp[0].alts = &wins[0].alt;
        cp[0].wfloor = MF_WFLOOR_SUBJECT;
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

    s.npred = (uint16_t)np;
    s.preds = preds;
    s.handoff = keepi >= 0 ? MF_H_ASSIGN : MF_H_ON_MISS;
    s.ret_pred = keepi >= 0 ? (uint8_t)keepi : MF_NO_PRED;
    s.head_max = keepi >= 0 ? rnd(40) : 0;
    o->assign = keepi >= 0;

    /* each part's own reply: the window family's member and stretch for its
       statement, on the same art */
    for (unsigned k = 0; k < o->nparts; k++) {
        mf_site ws;
        site_base(&ws);
        ws.nalt = 1;
        ws.alts = &wins[k].alt;
        ws.wfloor = MF_WFLOOR_SUBJECT;
        mf_wreply w;
        if (mf_wdecide(art, &ws, &w) || !w.run_stated) {
            fail(g->id, "mf_wdecide on a run part's statement", "no member");
            return;
        }
        o->member[k] = w.run_member;
        o->plo[k] = (unsigned)w.run_lo;
        o->plen[k] = w.run_len;
    }

    buf def = { 0 }, ent = { 0 }, ree = { 0 }, hl = { 0 };
    mf_sink sd = mk_sink(&def), se = mk_sink(&ent), sr = mk_sink(&ree), sh = mk_sink(&hl);
    uint32_t handle;
    if (mf_define(art, &s, &h, &sd, &handle)) {
        fail(g->id, "mf_define", mf_art_error(art));
        return;
    }
    g_layout_ok++;
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
    mf_result dr;
    if (!mf_defined(art, handle, &dr)) snprintf(o->forms, sizeof o->forms, "%s", dr.form_id);
    g_inc |= mf_includes(art);
    if (mf_art_end(art, NULL)) { fail(g->id, "mf_art_end", mf_art_error(art)); return; }

    /* the file scope: the kit's definitions and helpers; each rendered part's
       direct call; then every later call through the recorder */
    /* the SIMD levels' population (a census of the kit's own text, never a
       verdict): a run part with a w16 or a w32 arm */
    g_simd16 += def.p && strstr(def.p, "__w16(const") != NULL;
    g_simd32 += def.p && strstr(def.p, "__w32(const") != NULL;
    bprintf(fs, "/* ---- site %d (%s) ---- */\n", g->id, g_tag);
    bputs(fs, def.p ? def.p : "");
    bputs(fs, hl.p ? hl.p : "");
    for (unsigned k = 0; k < o->nparts; k++) {
        char call[64];
        snprintf(call, sizeof call, "%s(", g->names[k]);
        o->fnok[k] = def.p && strstr(def.p, call) != NULL;
        if (o->fnok[k])
            bprintf(fs, "size_t g2p_part_%d_%u(const unsigned char *s, size_t n, size_t lo)\n"
                        "{ return %s(s, n, lo); }\n", g->id, k, g->names[k]);
    }
    for (unsigned k = 0; k < o->nparts; k++)
        if (o->fnok[k])
            bprintf(fs, "#define %s(s_, n_, lo_) g2p_rec(%d, %u, %s, (s_), (n_), (lo_))\n",
                    g->names[k], g->id, k, g->names[k]);
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
    if (argc != 6) {
        fprintf(stderr, "usage: g2_pres_gen SEED NSITES OUTDIR TARGET LEVER\n");
        return 2;
    }
    g_rng = strtoull(argv[1], NULL, 10) * 2654435761ull + 0x7072657365ull;
    int nsites = atoi(argv[2]);
    char err[200];
    g_target = mf_target_parse(argv[4], strlen(argv[4]), err, sizeof err);
    if (!g_target) { fprintf(stderr, "g2p: target %s: %s\n", argv[4], err); return 2; }
    g_lever = atoi(argv[5]);
    char tag[64];
    snprintf(tag, sizeof tag, "%s.%s", argv[4], g_lever ? "lever" : "default");
    g_tag = tag;
    mf_finder_rows(&g_rows);

    int nw = 24;                        /* the lever witnesses, first */
    int total = nw + nsites;
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
        }
        gen_rates(g);
        one_site(g, &fs, &os[i]);
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
        for (unsigned k = 0; k < os[i].nparts; k++)
            if (os[i].fnok[k])
                fprintf(c, "size_t g2p_part_%d_%u(const unsigned char *, size_t, size_t);\n", i, k);
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
        fprintf(c, "    { %d, \"%s\", %d, %d, %d, %d, %u, {", i, tag, o->route, o->assign,
                g->witness, g_lever, g->L);
        for (unsigned j = 0; j < g->L; j++) fprintf(c, "%s%u", j ? "," : "", g->run[j]);
        fputs("}, {", c);
        for (unsigned j = 0; j < g->L; j++) fprintf(c, "%s%u", j ? "," : "", g->mask[j]);
        fprintf(c, "}, %d, %u, %u, %u, {", o->scan, o->ver_lo, o->ver_len, o->nparts);
        for (unsigned k = 0; k < o->nparts; k++) {
            fprintf(c, "%s{ %u, %u, ", k ? ", " : "", o->at[k], o->len[k]);
            if (o->fnok[k]) fprintf(c, "g2p_part_%d_%u", i, k);
            else fputs("NULL", c);
            fprintf(c, ", %d, %u, %u }", o->member[k], o->plo[k], o->plen[k]);
        }
        fprintf(c, "}, g2p_entry_%d, ", i);
        if (o->assign) fprintf(c, "g2p_reentry_%d", i);
        else fputs("NULL", c);
        fprintf(c, ", \"%s\" },\n", o->forms);
    }
    fprintf(c, "};\nconst int g2p_nsites = %d;\n", n);
    fclose(c);

    /* the generator's census (the runner's floors read it) */
    printf("G2PGEN %s sites=%d rendered=%d layout_ok=%ld P0=%ld P2=%ld P3=%ld P9=%ld "
           "p2_untested=%ld p2_refused=%ld simd16=%ld simd32=%ld\n", tag, total, n, g_layout_ok,
           g_route_sites[G2P_P0], g_route_sites[G2P_P2], g_route_sites[G2P_P3], g_route_sites[G2P_P9],
           g_p2_untested, g_p2_refused, g_simd16, g_simd32);
    printf("g2_pres_gen failures: %d\n", g_fails);
    return g_fails ? 1 : 0;
}
