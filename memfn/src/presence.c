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
 *       run member: the rarest position by its set's mass; a tie to the
 *       rightmost) and the window start (the least window mass among the
 *       MF_PRES_WINDOW-position windows holding the scan position; a tie to
 *       the leftmost), both THE RUN DECISION's (kit_run_decide, below);
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

/* The run member's reader of a RUN term (`src`): position j as its set. */
const uint8_t *kit_run_at(const void *src, unsigned j, uint8_t buf[32])
{
    kit_run_set(src, j, buf);
    return buf;
}

/* ---- THE RUN DECISION (R-38 K38-1; span_runs_sheet.md rev 1.2 §2.3, §5) ------
 *
 * ONE function decides a pre-check run's scan position and the stretch its
 * check verifies; every reader asks it: P3's run scan and window (here,
 * kit_pres_picks, and through it the twin's mass, P4 and P2), the window
 * family's member of a
 * pre-check run part (window.c run_member, verify YES) and translate's RQ-2
 * ranking (window.c, asked once per ranked position with the previous answer
 * handed back as `after`). Its rule is the incumbent's, reproduced: the scan
 * is the run member (kit_run_member over every position, ties per the TIE
 * table's stretch row, the higher position); the stretch is the whole run
 * (KIT_RUN_WHOLE) or P3's window (KIT_RUN_WINDOW: the least window mass among
 * the MF_PRES_WINDOW-position windows holding the scan, ties per T_WINDOW,
 * the leftmost; the whole run where it is no longer than one window).
 * `after` non-NULL: the next position the order ranks after it (the stretch
 * is then the whole run's); no candidate left, `has_scan` 0. The kit's
 * verify-NO prefilter member (window.c run_member, exact positions) is a
 * different site's decision and asks kit_run_member itself
 * (span_runs_sheet.md §2.5); tests/memfn/decider_census.py's RUN CALLERS
 * section holds both call sets. */
kit_run_reply kit_run_decide(const uint32_t *rate, kit_run_stretch st, kit_pos_at *at,
                             const void *src, unsigned n, const kit_run_reply *after)
{
    kit_member prev = after ? (kit_member){ after->scan, after->mass } : (kit_member){ -1, 0 };
    kit_member sc = kit_run_member(rate, at, src, n, 0, after ? &prev : NULL, T_MASS_STRETCH);
    kit_run_reply r = { sc.pos >= 0, sc.pos, sc.mass, 0, n };
    if (!r.has_scan || after || st == KIT_RUN_WHOLE || n <= MF_PRES_WINDOW) return r;
    /* P3's window: the windows holding the scan, each start's mass */
    int lo_s = sc.pos - (MF_PRES_WINDOW - 1), hi_s = sc.pos;
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
    r.ver_lo = (unsigned)bw.pos;
    r.ver_len = MF_PRES_WINDOW;
    return r;
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
    kit_pick bs = KIT_PICK_NONE;

    /* P3: the set's pick */
    for (unsigned i = 0; i < s->npspan; i++) {
        const mf_pred *p = &s->pspans[i];
        if (p->term[0].kind == MF_T_RUN) { run = p; continue; }
        uint32_t m = kit_mass(rate, p->term[0].set, 1, KIT_MASS_SUM);
        if (kit_pick_takes(&bs, m, T_PRES_MEMBER, member_key(p)))
            bs = (kit_pick){ (int)i, member_key(p), m };
    }
    int best = bs.pos;
    out->set_pick = (int16_t)best;
    int q = best >= 0 ? one_byte(&s->pspans[best].term[0]) : -1;

    /* P3: the run's scan position and window, the run decision's */
    kit_run_reply rr = KIT_RUN_NONE;
    if (run) {
        rr = kit_run_decide(rate, KIT_RUN_WINDOW, kit_run_at, &run->term[0], run->term[0].run_len,
                            NULL);
        out->run_scan = (int16_t)rr.scan;
        out->run_window = (int16_t)rr.ver_lo;
    }

    /* P4: set-leads, the set's pick against the run's scan member */
    unsigned scan_mask = 0xFFu;
    if (run) {
        const mf_term *t = &run->term[0];
        scan_mask = t->mask ? t->mask[rr.scan] : 0xFFu;
        if (q >= 0)
            out->set_leads = kit_mass(rate, s->pspans[best].term[0].set, 1, KIT_MASS_SUM) < rr.mass;
    }

    /* P2 (G1): the proof against the leading check */
    {
        int lead = run && scan_mask == 0xFFu ? run->term[0].run[rr.scan] : q;
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
        if (!run) {             /* the set's pick alone (none picked: the empty set, 0) */
            h = q >= 0 ? kit_mass(rate, s->pspans[best].term[0].set, 1, KIT_MASS_CAP) : 0;
        } else {                /* the run decision's stretch (P3's window) */
            const mf_term *t = &run->term[0];
            for (unsigned j = rr.ver_lo; j < rr.ver_lo + rr.ver_len; j++) {
                uint8_t set[32];
                kit_run_set(t, j, set);
                h = (h * kit_mass(rate, set, 1, KIT_MASS_CAP) + 999999u) / 1000000u;
            }
        }
        if (start_set) m = kit_mass(rate, start_set, 1, KIT_MASS_CAP);
        if (h == 0) out->landmark = 1;
        else if (k * h >= 1000000u) out->landmark = 0;
        else out->landmark = (int8_t)((1000000u - k * h) * m > 1000000u * h);
    }
}
