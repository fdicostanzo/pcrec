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
 * (pcrec_find_set_mass's arithmetic), KIT_MASS_SUM leaves it (PICK's cube
 * mass, pcrec_find_pick / run_rank).
 *
 * THE NONE ROW (span_pick.md rev 5.2 [rev5.1 R2], D186 add. 2): with no rates
 * handed, the mass is the uniform rate's over the multiset's member count k,
 * floor(k x 1e6 / 256), taken ONCE over the whole count (16 bytes: 62,500,
 * not 16 x 3,906 = 62,496); so the rules rank by member count and their own
 * tie rows break an equal count. Its density readers (HORS_MIN, MARGIN) are
 * the named exception (span_pick.md §The tables), and so is P2's dominance
 * compare (kit_pres_picks): it reads the raw rate table, so under NONE it
 * answers "not dominated" where this row's equal counts would answer yes. */
uint32_t kit_mass(const uint32_t *rate, const kit_pos *pos, unsigned n, kit_mass_cap cap)
{
    unsigned long long m = 0, k = 0;
    for (unsigned i = 0; i < n; i++) {
        if (pos[i].set) {
            for (unsigned b = 0; b < 256; b++)
                if (pos[i].set[b >> 3] >> (b & 7) & 1) { k++; if (rate) m += rate[b]; }
            continue;
        }
        unsigned f = ~pos[i].mask & 0xFFu;
        for (unsigned b = f;; b = (b - 1) & f) {
            k++;
            if (rate) m += rate[pos[i].t | b];
            if (!b) break;
        }
    }
    uint32_t t = rate ? (uint32_t)m : (uint32_t)(k * 1000000u / 256u);
    return cap == KIT_MASS_CAP && t > 1000000u ? 1000000u : t;
}

/* ---- the spans ---------------------------------------------------------------- */

static int one_byte(const mf_term *t)
{
    for (unsigned b = 0; b < 256; b++)
        if (t->set[b >> 3] >> (b & 7) & 1) return (int)b;
    return -1;
}

/* A member span's key under the TIE table's presence-member row. */
static int32_t member_key(const mf_pred *p)
{
    return kit_tie_member_key(p->member_order, one_byte(&p->term[0]));
}

/* Run position `j` of `t` as a mass position: its cube (the byte under its
 * mask). */
static kit_pos run_pos(const mf_term *t, unsigned j)
{
    return (kit_pos){ .t = t->run[j], .mask = t->mask ? t->mask[j] : 0xFFu };
}

/* ---- the ports ---------------------------------------------------------------- */

int mf_pres_ports(const mf_art *art, const mf_site *s, const mf_pres_proof *proof,
                  const uint8_t *start_set, mf_pres_picks *out)
{
    out->set_pick = out->run_scan = out->run_window = -1;
    out->set_leads = out->dominated = out->landmark = -1;
    if (s->abi != MF_SITE_ABI || s->op != MF_OP_ALL_PRESENT || kit_presence_check(s))
        return -1;
    kit_pres_picks(art, s, proof, start_set, out);
    return 0;
}

void kit_pres_picks(const mf_art *art, const mf_site *s, const mf_pres_proof *proof,
                    const uint8_t *start_set, mf_pres_picks *out)
{
    out->set_pick = out->run_scan = out->run_window = -1;
    out->set_leads = out->dominated = out->landmark = -1;
    if (!s->npspan) return;
    const uint32_t *rate = kit_byte_rate(art);
    const mf_pred *run = NULL;
    int best = -1;
    uint32_t lo = 0;

    /* P3: the set's pick */
    for (unsigned i = 0; i < s->npspan; i++) {
        const mf_pred *p = &s->pspans[i];
        if (p->term[0].kind == MF_T_RUN) { run = p; continue; }
        kit_pos b = { .t = (uint8_t)one_byte(&p->term[0]), .mask = 0xFFu };
        uint32_t m = kit_mass(rate, &b, 1, KIT_MASS_SUM);
        if (best < 0 || m < lo ||
            (m == lo && kit_tie_takes(T_PRES_MEMBER, member_key(p), member_key(&s->pspans[best])))) {
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
            kit_pos c1 = run_pos(t, i);
            uint32_t c = kit_mass(rate, &c1, 1, KIT_MASS_SUM);
            if (scan < 0 || c < sm) { scan = (int)i; sm = c; }
        }
        if (n > MF_PRES_WINDOW) {
            int lo_s = scan - (MF_PRES_WINDOW - 1), hi_s = scan;
            if (lo_s < 0) lo_s = 0;
            if (hi_s > (int)n - MF_PRES_WINDOW) hi_s = (int)n - MF_PRES_WINDOW;
            uint32_t wl = 0;
            at = lo_s;
            for (int w = lo_s; w <= hi_s; w++) {
                kit_pos win[MF_PRES_WINDOW];
                for (unsigned j = 0; j < MF_PRES_WINDOW; j++) win[j] = run_pos(t, (unsigned)w + j);
                uint32_t wm = kit_mass(rate, win, MF_PRES_WINDOW, KIT_MASS_SUM);
                if (w == lo_s || wm < wl || (wm == wl && kit_tie_takes(T_WINDOW, w, at))) {
                    wl = wm;
                    at = w;
                }
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
        if (q >= 0) {
            kit_pos qp = { .t = (uint8_t)q, .mask = 0xFFu }, sp = run_pos(t, (unsigned)scan);
            out->set_leads = kit_mass(rate, &qp, 1, KIT_MASS_SUM) <
                             kit_mass(rate, &sp, 1, KIT_MASS_SUM);
        }
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
        const kit_pos sp = { .set = set };
        if (!run) {
            memset(set, 0, sizeof set);
            if (q >= 0) set[q >> 3] = (uint8_t)(1u << (q & 7));
            h = kit_mass(rate, &sp, 1, KIT_MASS_CAP);
        } else {
            const mf_term *t = &run->term[0];
            unsigned len = t->run_len - (unsigned)at < MF_PRES_WINDOW
                         ? t->run_len - (unsigned)at : MF_PRES_WINDOW;
            for (unsigned j = (unsigned)at; j < (unsigned)at + len; j++) {
                unsigned mask = t->mask ? t->mask[j] : 0xFFu;
                memset(set, 0, sizeof set);
                for (unsigned b = 0; b < 256; b++)
                    if ((b & mask) == t->run[j]) set[b >> 3] |= (uint8_t)(1u << (b & 7));
                h = (h * kit_mass(rate, &sp, 1, KIT_MASS_CAP) + 999999u) / 1000000u;
            }
        }
        if (start_set) m = kit_mass(rate, &(const kit_pos){ .set = start_set }, 1, KIT_MASS_CAP);
        if (h == 0) out->landmark = 1;
        else if (k * h >= 1000000u) out->landmark = 0;
        else out->landmark = (int8_t)((1000000u - k * h) * m > 1000000u * h);
    }
}
