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
 *       pattern order, then to the larger byte), the run's scan position (the
 *       rarest position by its cube's mass; a tie to the rightmost) and the
 *       window start (the least window mass among the MF_PRES_WINDOW-position
 *       windows holding the scan position; a tie to the leftmost);
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
 * WHAT IT DOES AT B3a: NOTHING RENDERS FROM IT. mf_pres_ports is a pure
 * query, like mf_ask; the host calls it in its trace build only. At B3b the
 * PRES rows (finder.c P2, P3, P4) read these ports and route.
 */
#include <string.h>

#include "kit.h"

/* ---- the frequency kind ---------------------------------------------------- */

/* The byte-rate table the compile's analysis object carries (ppm per byte,
 * uint32_t[256]), or NULL where it carries none (no object, the kind absent,
 * or present with no table: PRIOR_NONE). */
static const uint32_t *byte_rate(const mf_art *art)
{
    const mf_analysis *an = art->an;
    for (uint16_t i = 0; an && an->kinds && i < an->nkinds; i++)
        if (an->kinds[i].tag && !strcmp(an->kinds[i].tag, "byte-rate"))
            return an->kinds[i].present == MF_KIND_PRESENT
                 ? (const uint32_t *)an->kinds[i].payload : NULL;
    return NULL;
}

/* MASS's NONE answer for `k` bytes: the uniform rate's, floor(k * 1e6 / 256). */
static uint32_t uniform_mass(unsigned k)
{
    return (uint32_t)((unsigned long long)k * 1000000u / 256u);
}

/* The mass of the position (t, mask): every byte t | f for f a submask of
 * the free bits ~mask; a byte (mask 0xFF) is rate[t]. NONE: cardinality. */
static uint32_t cube_mass(const uint32_t *rate, unsigned t, unsigned mask)
{
    unsigned f = ~mask & 0xFFu;
    unsigned long long m = 0;
    if (!rate) return uniform_mass(1u << __builtin_popcount(f));
    for (unsigned b = f;; b = (b - 1) & f) {
        m += rate[t | b];
        if (!b) break;
    }
    return (uint32_t)m;
}

/* The mass of a byte SET (256-bit), capped at 1e6. NONE: cardinality. */
static uint32_t set_mass(const uint32_t *rate, const uint8_t set[32])
{
    unsigned long long t = 0;
    unsigned k = 0;
    for (unsigned b = 0; b < 256; b++)
        if (set[b >> 3] >> (b & 7) & 1) { k++; if (rate) t += rate[b]; }
    if (!rate) t = uniform_mass(k);
    return t > 1000000u ? 1000000u : (uint32_t)t;
}

/* The mass of the window [s, s + MF_PRES_WINDOW) of the run: the sum over
 * every member byte of every position's cube (MASS over the member list).
 * NONE: the member count's uniform mass. */
static uint32_t window_mass(const uint32_t *rate, const mf_term *t, unsigned s)
{
    unsigned long long m = 0;
    unsigned k = 0;
    for (unsigned j = s; j < s + MF_PRES_WINDOW; j++) {
        unsigned mask = t->mask ? t->mask[j] : 0xFFu, f = ~mask & 0xFFu;
        for (unsigned b = f;; b = (b - 1) & f) {
            k++;
            if (rate) m += rate[t->run[j] | b];
            if (!b) break;
        }
    }
    return rate ? (uint32_t)m : uniform_mass(k);
}

/* ---- the spans ---------------------------------------------------------------- */

static int one_byte(const mf_term *t)
{
    for (unsigned b = 0; b < 256; b++)
        if (t->set[b >> 3] >> (b & 7) & 1) return (int)b;
    return -1;
}

/* Does member span `a` take a mass tie over member span `b`? The one last in
 * pattern order first (a known position above an unknown one), then the
 * larger byte. */
static int tie_over(const mf_pred *a, const mf_pred *b)
{
    unsigned oa = a->member_order == MF_ORDER_UNKNOWN ? 0 : a->member_order;
    unsigned ob = b->member_order == MF_ORDER_UNKNOWN ? 0 : b->member_order;
    if (oa != ob) return oa > ob;
    return one_byte(&a->term[0]) > one_byte(&b->term[0]);
}

/* ---- the ports ---------------------------------------------------------------- */

int mf_pres_ports(const mf_art *art, const mf_site *s, const mf_pres_proof *proof,
                  const uint8_t *displaced, mf_pres_picks *out)
{
    out->set_pick = out->run_scan = out->run_window = -1;
    out->set_leads = out->dominated = out->landmark = -1;
    if (s->abi != MF_SITE_ABI || s->op != MF_OP_ALL_PRESENT || kit_presence_check(s))
        return -1;
    if (!s->npspan) return 0;
    const uint32_t *rate = byte_rate(art);
    const mf_pred *run = NULL;
    int best = -1;
    uint32_t lo = 0;

    /* P3: the set's pick */
    for (unsigned i = 0; i < s->npspan; i++) {
        const mf_pred *p = &s->pspans[i];
        if (p->term[0].kind == MF_T_RUN) { run = p; continue; }
        uint32_t m = cube_mass(rate, (unsigned)one_byte(&p->term[0]), 0xFFu);
        if (best < 0 || m < lo || (m == lo && tie_over(p, &s->pspans[best]))) {
            best = (int)i;
            lo = m;
        }
    }
    out->set_pick = (int16_t)best;
    int q = best >= 0 ? one_byte(&s->pspans[best].term[0]) : -1;

    /* P3: the run's scan position and window */
    int scan = -1, at = 0;
    if (run) {
        const mf_term *t = &run->term[0];
        unsigned n = t->run_len;
        uint32_t sm = 0;
        for (unsigned k = 0; k < n; k++) {          /* rightmost first: a tie stays */
            unsigned i = n - 1 - k;
            uint32_t c = cube_mass(rate, t->run[i], t->mask ? t->mask[i] : 0xFFu);
            if (scan < 0 || c < sm) { scan = (int)i; sm = c; }
        }
        if (n > MF_PRES_WINDOW) {
            int lo_s = scan - (MF_PRES_WINDOW - 1), hi_s = scan;
            if (lo_s < 0) lo_s = 0;
            if (hi_s > (int)n - MF_PRES_WINDOW) hi_s = (int)n - MF_PRES_WINDOW;
            uint32_t wl = 0;
            at = lo_s;
            for (int w = lo_s; w <= hi_s; w++) {
                uint32_t wm = window_mass(rate, t, (unsigned)w);
                if (w == lo_s || wm < wl) { wl = wm; at = w; }
            }
        }
        out->run_scan = (int16_t)scan;
        out->run_window = (int16_t)at;
    }

    /* P4: set-leads, the set's pick against the run's scan member */
    unsigned scan_mask = 0xFFu;
    if (run) {
        const mf_term *t = &run->term[0];
        scan_mask = t->mask ? t->mask[scan] : 0xFFu;
        if (q >= 0)
            out->set_leads = cube_mass(rate, (unsigned)q, 0xFFu) <
                             cube_mass(rate, t->run[scan], scan_mask);
    }

    /* P2 (G1): the proof against the leading check */
    {
        int lead = run && scan_mask == 0xFFu ? run->term[0].run[scan] : q;
        int dom;
        if (!proof || proof->byte < 0) dom = 0;
        else if (run && !proof->run) dom = 0;
        else if (proof->byte == lead) dom = 1;
        else if (run) dom = 0;
        else if (!proof->stop) dom = 0;
        else dom = rate && lead >= 0 && rate[proof->byte] <= rate[lead];
        out->dominated = (int8_t)dom;
    }

    /* the FIFTH: the landmark admission, where the site ASSIGNs its landmark */
    if (s->handoff == MF_H_ASSIGN) {
        unsigned long long h = 1000000u, m = 1000000u, k = s->head_max;
        uint8_t set[32];
        if (!run) {
            memset(set, 0, sizeof set);
            if (q >= 0) set[q >> 3] = (uint8_t)(1u << (q & 7));
            h = set_mass(rate, set);
        } else {
            const mf_term *t = &run->term[0];
            unsigned len = t->run_len - (unsigned)at < MF_PRES_WINDOW
                         ? t->run_len - (unsigned)at : MF_PRES_WINDOW;
            for (unsigned j = (unsigned)at; j < (unsigned)at + len; j++) {
                unsigned mask = t->mask ? t->mask[j] : 0xFFu;
                memset(set, 0, sizeof set);
                for (unsigned b = 0; b < 256; b++)
                    if ((b & mask) == t->run[j]) set[b >> 3] |= (uint8_t)(1u << (b & 7));
                h = (h * set_mass(rate, set) + 999999u) / 1000000u;
            }
        }
        if (displaced) m = set_mass(rate, displaced);
        if (h == 0) out->landmark = 1;
        else if (k * h >= 1000000u) out->landmark = 0;
        else out->landmark = (int8_t)((1000000u - k * h) * m > 1000000u * h);
    }
    return 0;
}
