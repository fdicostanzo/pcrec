/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text; no third-party source
 *   (memfn/PROVENANCE.md).
 *
 * memfn/src/presence.c — THE FIVE-PICK PORTS (R17-b' B3a, lane b3a; KW-8;
 * docs/design/memfn/r17b_prime.md rev 3 §1.4, §3.1 row B3a, §4.1).
 *
 * WHAT IT IS. The kit's ports of the host's five priced presence picks, over
 * the presence spans a site STATES (mf_site.pspans, PR-5: every member of the
 * necessary set its own one-byte span, the whole run one span) and the
 * compile's analysis object (the frequency kind `byte-rate`, read at ANY
 * provenance, D162 ruling 2: these are the total default reproducing today):
 *   P3  the set's pick (the rarest member; a tie to the member LAST in
 *       pattern order, then to the larger byte); the run's scan and its
 *       verified extent are THE RUN DECISION's (kit_run_decide, below),
 *       answered on the class (mf_class.run) since R-38 K38-2, no port;
 *   P4  set-leads (the set's pick STRICTLY rarer than the run's scan member);
 *   P2  G1 (the start search's proof stands for the leading check: identity,
 *       the run verified, or a no-commoner stop byte);
 *   and the FIFTH, the landmark admission, which is not a kit row (framing
 *   (a) leaves the origin pcrec's, D167 Q-R17P-11) and is computed here as
 *   the shadow's evidence only.
 * Each is VERBATIM: the same arithmetic over the same facts, so the host's
 * trace build can hold every answer equal to its own pick on every site
 * (r17b_prime.md §8.1 B3a). The NONE answers (no table in the frequency
 * kind) are each question kind's own, as the host spells them (findings
 * design §6.1): MASS is cardinality (the uniform rate's mass), PICK ties go
 * where a uniform cost sends them, COMPARE answers "no".
 *
 * WHAT IT DOES SINCE B3b: THE PRES ROWS READ IT. `kit_pres_picks` is the
 * ports' arithmetic; the routed PRES slot (finder.c `fd_pres`: P2, P3, P4)
 * reads it over the site's own statement (its spans and `pres_proof`), so
 * the links mf_ask and mf_defined answer, and the parts the host lays out
 * from them, are these picks. mf_pres_ports stays the pure query of B3a:
 * the host's trace build compares each answer with its own pick (the KW-8
 * census, re-run at B3b on the kit-sourced proof).
 */
#include <string.h>

#include "kit.h"

/* ---- the frequency kind ---------------------------------------------------- */

/* The byte-rate table the compile's analysis object carries (ppm per byte,
 * uint32_t[256]), or NULL where it carries none (no object, the kind absent,
 * or present with no payload). */
const uint32_t *kit_byte_rate(const mf_art *art)
{
    const mf_analysis *an = art->an;
    for (uint16_t i = 0; an && an->kinds && i < an->nkinds; i++)
        if (an->kinds[i].tag && !strcmp(an->kinds[i].tag, "byte-rate"))
            return an->kinds[i].present == MF_KIND_PRESENT
                 ? (const uint32_t *)an->kinds[i].payload : NULL;
    return NULL;
}

/* THE MASS of a position multiset: the summed byte rates of every member
 * byte of every listed position, a byte repeated across positions counted at
 * each (a run window's `zzzzzzz~J` sums z seven times; a union set would
 * count it once and move the window). `cap` KIT_MASS_CAP caps the sum at 1e6
 * (pcrec_find_set_mass's arithmetic), KIT_MASS_SUM leaves it (PICK's
 * position mass, pcrec_find_pick / run_rank). The sets are positions, never
 * cubes (D187): normal form is a CHECKED fact at the input boundary
 * (kit_presence_check refuses a presence run byte outside its mask), so a
 * run's set and the cube pcrec meant are the same bytes.
 *
 * THE NONE ROW (span_pick.md rev 5.2 [rev5.1 R2], D186 add. 2): with no rates
 * handed, the mass is the uniform rate's over the multiset's member count k,
 * floor(k x 1e6 / 256), taken ONCE over the whole count (16 bytes: 62,500,
 * not 16 x 3,906 = 62,496); so the rules rank by member count and their own
 * tie rows break an equal count. Its density readers (HORS_MIN, MARGIN) are
 * the named exception (span_pick.md §The tables), and so is P2's dominance
 * compare (kit_pres_picks): it reads the raw rate table, so under NONE it
 * answers "not dominated" where this row's equal counts would answer yes. */
uint32_t kit_mass(const uint32_t *rate, const uint8_t *set, unsigned n, kit_mass_cap cap)
{
    unsigned long long m = 0, k = 0;
    for (unsigned i = 0; i < n; i++, set += 32)
        for (unsigned b = 0; b < 256; b++)
            if (set[b >> 3] >> (b & 7) & 1) { k++; if (rate) m += rate[b]; }
    uint32_t t = rate ? (uint32_t)m : (uint32_t)(k * 1000000u / 256u);
    return cap == KIT_MASS_CAP && t > 1000000u ? 1000000u : t;
}

void kit_run_set(const mf_term *t, unsigned j, uint8_t set[32])
{
    unsigned mask = t->mask ? t->mask[j] : 0xFFu;
    memset(set, 0, 32);
    for (unsigned b = 0; b < 256; b++)
        if ((b & mask) == t->run[j]) set[b >> 3] |= (uint8_t)(1u << (b & 7));
}

/* ---- the spans ---------------------------------------------------------------- */

static int set_first_member(const uint8_t set[32])
{
    for (unsigned b = 0; b < 256; b++)
        if (set[b >> 3] >> (b & 7) & 1) return (int)b;
    return -1;
}

static int one_byte(const mf_term *t)
{
    return set_first_member(t->set);
}

/* A member span's key under the TIE table's presence-member row. */
static int32_t member_key(const mf_pred *p)
{
    return kit_tie_member_key(p->member_order, one_byte(&p->term[0]));
}

/* The run member's reader of a RUN term (`src`): position j as its set. */
const uint8_t *kit_run_at(const void *src, unsigned j, uint8_t buf[32])
{
    kit_run_set(src, j, buf);
    return buf;
}

const uint8_t *kit_wspan_at(const void *src, unsigned j, uint8_t buf[32])
{
    (void)buf;
    return ((const mf_wspan *)src)->set[j];
}

/* THE RUN RECOGNIZER (kit.h): the run is the LAST presence span, stating
 * `nalt` 1 and `nterm` 0 (kit_presence_check refuses one anywhere else). */
int kit_pres_run(const mf_site *s)
{
    if (!s->npspan || !s->pspans) return -1;
    const mf_pred *p = &s->pspans[s->npspan - 1];
    return p->nalt == 1 && p->nterm == 0 ? (int)s->npspan - 1 : -1;
}

const mf_wspan *kit_pres_run_span(const mf_site *s, int run)
{
    return &s->pspans[run].alts[0].spans[0];
}

const char *kit_run_floor(mf_art *art, const char *lo, const mf_site *s, const char *who)
{
    int run = kit_pres_run(s);
    int32_t omin = run >= 0 ? s->pspans[run].omin : 0;
    if (omin >= 0) return lo;
    unsigned long long back = (unsigned long long)-(long long)omin;
    kb f;
    kb_init(&f, art->a);
    kb_printf(&f, "(%s >= %llu ? %s - %llu : 0)", lo, back, lo, back);
    if (f.oom) { kit_fail(art, "%s: out of memory", who); return NULL; }
    return f.p;
}

/* ---- THE RUN DECISION (R-38 K38-1, K38-2; span_runs_sheet.md rev 1.3 §2.3, §5)
 *
 * ONE function decides a run's scan position and the stretch its check
 * verifies; every reader asks it: the routed PRES slot's run reply
 * (finder.c fd_pres, mf_class.run, the mode its row's route names, U3), and
 * through the reply P4, P2 and the twin's mass (here); the window family's
 * member of a run (window.c run_member, either verify fact); translate's
 * RQ-2 ranking (window.c, asked once per ranked position with the previous
 * answer handed back as `after`) and Table A's in-run stop (window.c
 * a_mass_choose, K38-2a). The scan is the run member (kit_run_member, ties
 * per `o.tie`); the stretch is the MODE's, a declared first-match table
 * (`run_modes[]`, below; memory pcrec-decisions-as-first-match-tables),
 * each row's rule the incumbent's, reproduced.
 * `after` non-NULL: the next position the order ranks after it (the stretch
 * is then the whole run's); no candidate left, `has_scan` 0. */

/* P3's window: the least window mass among the MF_PRES_WINDOW-position
 * windows holding the scan, ties per T_WINDOW (the leftmost). */
static void stretch_window(const uint32_t *rate, kit_pos_at *at, const void *src, unsigned n,
                           kit_run_reply *r)
{
    int lo_s = r->scan - (MF_PRES_WINDOW - 1), hi_s = r->scan;
    if (lo_s < 0) lo_s = 0;
    if (hi_s > (int)n - MF_PRES_WINDOW) hi_s = (int)n - MF_PRES_WINDOW;
    kit_pick bw = KIT_PICK_NONE;
    for (int w = lo_s; w <= hi_s; w++) {
        uint8_t win[MF_PRES_WINDOW][32];
        for (unsigned j = 0; j < MF_PRES_WINDOW; j++) {
            const uint8_t *q = at(src, (unsigned)w + j, win[j]);
            if (q != win[j]) memcpy(win[j], q, 32);
        }
        uint32_t wm = kit_mass(rate, win[0], MF_PRES_WINDOW, KIT_MASS_SUM);
        if (kit_pick_takes(&bw, wm, T_WINDOW, w)) bw = (kit_pick){ w, w, wm };
    }
    r->ver_lo = (uint8_t)bw.pos;
    r->ver_len = MF_PRES_WINDOW;
}

static int one_member(const uint8_t set[32])
{
    unsigned m = 0;
    for (unsigned i = 0; i < 32; i++) m += (unsigned)__builtin_popcount(set[i]);
    return m == 1;
}

/* The maximal stretch of exact (one-member) positions around the scan
 * (the window site's verify-NO run, today's run-pinned compare). */
static void stretch_exact(const uint32_t *rate, kit_pos_at *at, const void *src, unsigned n,
                          kit_run_reply *r)
{
    (void)rate;
    uint8_t buf[32];
    unsigned lo = r->scan, hi = (unsigned)r->scan + 1;
    while (lo > 0 && one_member(at(src, lo - 1, buf))) lo--;
    while (hi < n && one_member(at(src, hi, buf))) hi++;
    r->ver_lo = (uint8_t)lo;
    r->ver_len = (uint8_t)(hi - lo);
}

/* THE MODE TABLE, first match on (mode, the run's length): each row's
 * candidates (`cand`, kit.h kit_cand: EXACT one-member positions only;
 * FINDABLE the positions the kit's finds read, one member or a cube, part_d
 * §2.4 item 1, the identity on every run stated before R-38 Part D) and
 * stretch (NULL: the whole run). */
static const struct {
    kit_run_stretch st;
    unsigned        longer_than;    /* the row applies to runs longer than this */
    kit_cand        cand;
    void          (*stretch)(const uint32_t *, kit_pos_at *, const void *, unsigned,
                             kit_run_reply *);
} run_modes[] = {
    { KIT_RUN_WINDOW,       MF_PRES_WINDOW, KIT_CAND_FINDABLE, stretch_window },
    { KIT_RUN_WINDOW,       0,              KIT_CAND_FINDABLE, NULL },   /* fits one window: whole */
    { KIT_RUN_WHOLE,        0,              KIT_CAND_FINDABLE, NULL },
    { KIT_RUN_EXACT_AROUND, 0,              KIT_CAND_EXACT,    stretch_exact },
};

/* THE DENY's CLIP (`run-verify-wide`, part_d.md §5.1 D2): the stretch cut
 * to the maximal FINDABLE stretch holding the scan (positions with a (T, K)
 * spelling, kit_pos_spelled), the identity where every position is one. */
static void clip_findable(kit_pos_at *at, const void *src, unsigned n, kit_run_reply *r)
{
    uint8_t buf[32];
    unsigned lo = r->scan, hi = (unsigned)r->scan + 1;
    while (lo > 0 && kit_pos_spelled(at(src, lo - 1, buf))) lo--;
    while (hi < n && kit_pos_spelled(at(src, hi, buf))) hi++;
    unsigned vlo = r->ver_lo > lo ? r->ver_lo : lo;
    unsigned vhi = (unsigned)r->ver_lo + r->ver_len < hi ? (unsigned)r->ver_lo + r->ver_len : hi;
    r->ver_lo = (uint8_t)vlo;
    r->ver_len = (uint8_t)(vhi - vlo);
}

kit_run_reply kit_run_decide(const uint32_t *rate, kit_run_opts o, kit_pos_at *at,
                             const void *src, unsigned n, const kit_run_reply *after)
{
    unsigned m = 0;
    while (m + 1 < sizeof run_modes / sizeof run_modes[0] &&
           !(run_modes[m].st == o.st && n > run_modes[m].longer_than))
        m++;
    kit_member prev = { -1, 0 };
    if (after) {
        uint8_t buf[32];
        prev = (kit_member){ after->scan, kit_mass(rate, at(src, after->scan, buf), 1, KIT_MASS_SUM) };
    }
    kit_member sc = kit_run_member(rate, at, src, n, run_modes[m].cand, after ? &prev : NULL, o.tie);
    kit_run_reply r = KIT_RUN_NONE;
    if (sc.pos < 0) return r;
    r.has_scan = 1;
    r.scan = (uint8_t)sc.pos;
    r.ver_len = (uint8_t)n;
    if (!after && run_modes[m].stretch) run_modes[m].stretch(rate, at, src, n, &r);
    if (!after && o.clip) clip_findable(at, src, n, &r);
    return r;
}

/* THE DECISION's OPTIONS on an art: the stretch its reader renders, and the
 * tie its ties read, the TIE table's stretch row (the higher position) or,
 * under the test-only lever `run-tie-left` (mf_lever, K38-2a; C4's reaching
 * regime, span_runs_sheet.md §2.4), T_RUN_LEFT (the lower position). The
 * lever moves every reader of the decision on the art together (scan,
 * stretch, the twin's mass, the ranking, the in-run stop) and nothing else. */
kit_run_opts kit_run_opts_of(const mf_art *art, const mf_site *s, kit_run_stretch st)
{
    int left = art && (art->levers & KIT_LEVER_RUN_LEFT);
    int clip = s && kit_opt_denied(s->opts, "run-verify-wide");
    return (kit_run_opts){ st, left ? T_RUN_LEFT : T_MASS_STRETCH, clip };
}

/* ---- the ports ---------------------------------------------------------------- */

int mf_pres_ports(const mf_art *art, const mf_site *s, const mf_pres_proof *proof,
                  const uint8_t *start_set, mf_pres_picks *out)
{
    const char *why;
    mf_run_reply ext;
    out->set_pick = -1;
    out->set_leads = out->dominated = out->landmark = -1;
    if (s->abi != MF_SITE_ABI || s->op != MF_OP_ALL_PRESENT || kit_presence_check(s) ||
        fd_pres_run(art, s, &ext, &why))
        return -1;
    kit_pres_picks(art, s, proof, start_set, &ext, out, NULL);
    return 0;
}

void kit_pres_picks(const mf_art *art, const mf_site *s, const mf_pres_proof *proof,
                    const uint8_t *start_set, const mf_run_reply *ext, mf_pres_picks *out,
                    int *run_noscan)
{
    out->set_pick = -1;
    out->set_leads = out->dominated = out->landmark = -1;
    if (run_noscan) *run_noscan = 0;
    if (!s->npspan) return;
    const uint32_t *rate = kit_byte_rate(art);
    int run = kit_pres_run(s);
    const mf_wspan *rs = run >= 0 ? kit_pres_run_span(s, run) : NULL;
    kit_pick bs = KIT_PICK_NONE;

    /* P3: the set's pick */
    for (unsigned i = 0; i < s->npspan; i++) {
        const mf_pred *p = &s->pspans[i];
        if ((int)i == run) continue;
        uint32_t m = kit_mass(rate, p->term[0].set, 1, KIT_MASS_SUM);
        if (kit_pick_takes(&bs, m, T_PRES_MEMBER, member_key(p)))
            bs = (kit_pick){ (int)i, member_key(p), m };
    }
    int best = bs.pos;
    out->set_pick = (int16_t)best;
    int q = best >= 0 ? one_byte(&s->pspans[best].term[0]) : -1;

    /* the run's scan, the run decision's (the scan is every mode's member:
       the stretch alone reads the route). `rsc`: a run WITH a scan; a run
       with no position the kit finds (part_d.md §2.4 items 2, 4) is read as
       absent by P4 and P2, and its fact is handed back (`run_noscan`) */
    kit_run_reply rr = KIT_RUN_NONE;
    uint32_t scan_mass = 0;
    if (rs) {
        rr = kit_run_decide(rate, kit_run_opts_of(art, s, KIT_RUN_WHOLE), kit_wspan_at, rs,
                            rs->len, NULL);
        if (rr.has_scan) scan_mass = kit_mass(rate, rs->set[rr.scan], 1, KIT_MASS_SUM);
        else if (run_noscan) *run_noscan = 1;
    }
    int rsc = rs && rr.has_scan;

    /* P4: set-leads, the set's pick against the run's scan member */
    if (rsc && q >= 0)
        out->set_leads = kit_mass(rate, s->pspans[best].term[0].set, 1, KIT_MASS_SUM) < scan_mass;

    /* P2 (G1): the proof against the leading check (an exact scan position's
       byte, else the set's pick); a run with no scan is RUN-LESS here (the
       set's pick leads, the proof's `run` not required: part_d.md §2.4
       item 2 [r2pd P3]) */
    {
        int lead = rsc && one_member(rs->set[rr.scan]) ? set_first_member(rs->set[rr.scan]) : q;
        int dom;
        if (!proof || proof->byte < 0) dom = 0;
        else if (rsc && !proof->run) dom = 0;
        else if (proof->byte == lead) dom = 1;
        else if (rsc) dom = 0;
        else if (!proof->stop) dom = 0;
        else dom = rate && lead >= 0 && rate[proof->byte] <= rate[lead];
        out->dominated = (int8_t)dom;
    }

    /* the FIFTH: the landmark admission, where the site ASSIGNs its landmark,
       at max(K, 0) (a landmark at or before the attempt start costs no step
       back; span_runs_sheet.md §3.2); a run's hit mass over the reply's
       VERIFIED EXTENT (`ext`, the define's own decision). Where the run is
       not tested (a declined run: `ext` verifies nothing) the landmark is
       the head member, so the mass is the set pick's (part_d.md §2.4 item
       5 [r1pd F1]); a scan-less tested run keeps the run branch (its part
       ships). THE UNBOUNDED K (R-41): a stated MF_HEAD_MAX_UNBOUNDED declines,
       whatever the mass, a never-hit landmark (h 0) included */
    if (s->handoff == MF_H_ASSIGN && ext) {
        unsigned long long h = 1000000u, m = 1000000u;
        unsigned long long k = s->head_max > 0 ? (unsigned long long)s->head_max : 0;
        if (!rs || !ext->ver_len) { /* the set's pick alone (none picked: the empty set, 0) */
            h = q >= 0 ? kit_mass(rate, s->pspans[best].term[0].set, 1, KIT_MASS_CAP) : 0;
        } else {
            for (unsigned j = ext->ver_lo; j < (unsigned)ext->ver_lo + ext->ver_len; j++)
                h = (h * kit_mass(rate, rs->set[j], 1, KIT_MASS_CAP) + 999999u) / 1000000u;
        }
        if (start_set) m = kit_mass(rate, start_set, 1, KIT_MASS_CAP);
        if (s->head_max == MF_HEAD_MAX_UNBOUNDED) out->landmark = 0;
        else if (h == 0) out->landmark = 1;
        else if (k * h >= 1000000u) out->landmark = 0;
        else out->landmark = (int8_t)((1000000u - k * h) * m > 1000000u * h);
    }
}
