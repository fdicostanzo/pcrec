/* tests/memfn/run_decide_check.c -- R-38 K38-1 (lane k381;
 * docs/design/memfn/span_runs_sheet.md rev 1.2 §5's K38-1 row): THE RUN
 * DECISION's READERS, each read where it lands, on fixed witnesses.
 *
 *   rundecchk          one `ok   <reader> <witness>` or `FAIL: ...` line per
 *                      check, then `checks passed: N` / `checks failed: M`;
 *                      exit 1 on any failure.
 *
 * Run by tests/memfn/run_finder.sh (`make test-memfn-finder`). White-box (the
 * kit's internal header, as mass_check.c): wf_prepare is the kit's.
 *
 * WHY IT EXISTS. memfn/src/presence.c `kit_run_decide` is the ONE decision of
 * a pre-check run's scan position and verified stretch; every reader asks it.
 * A plant in it (the tie rule, the window's tie) must move EVERY reader
 * together, and pcrec's own observers (emit_dfa.c `req_run_member`'s
 * agreement check, compose.c `pres_layout_check`) stop the compile at the
 * FIRST reader that disagrees, so they cannot count the rest. This check
 * reads each reader at its own output and counts them one line each:
 *   scan    the class's run reply's scan (`mf_class.run`, K38-2; was
 *           mf_pres_ports `run_scan`), on P3's route
 *   window  its verified extent (`ver_lo`, `ver_len`; was `run_window`)
 *   twin    the twin admission's mass term, read as the landmark bit
 *           (mf_pres_ports `landmark` on an ASSIGN site)
 *   member  the window family's member of a pre-check run part (mf_wdecide
 *           on a verify-YES run: `run_member`)
 *   stretch the same part's stretch (mf_wreply `run_lo`, `run_len`: the whole
 *           run, the stretch the decision's WHOLE ask answers)
 *   rank    translate's RQ-2 ranking (wf_prepare's legacy predicate:
 *           `rank_pos[]`)
 * P0/P9's whole-run keep asks no one (the route's constant, review
 * 2026-11-10 r1 k381 K1); the RUN CALLERS census holds the reader set.
 *
 * THE CONTROL. Every expected value is a LITERAL written from the stated rule
 * (span_runs_sheet.md §2.3; presence.c's header: the scan the least position
 * mass, ties to the HIGHER position; the window the least window mass among
 * the MF_PRES_WINDOW-position windows holding the scan, ties to the LEFTMOST;
 * the twin's h the rounded-up product of the window's capped masses, the bit
 * (1e6 - K h) m > 1e6 h with m 1e6 where no start set is handed), derived in
 * its comment from the rate table below, never computed by a kit function.
 *
 * THE WITNESSES.
 *   W1  S1095's: the four positions `abcd` under NONE (no rates: every
 *       position ties). scan 3, member 3, rank 3,2,1,0. Window and twin are
 *       tie-blind on four positions (one window).
 *   W2  the twin's (sheet §5: a tied stretch over more than 8 positions):
 *       `qzeeeeeeeeeq` (12) under RATES. q (100) ties at 0 and 11.
 *   W3  the window's tie: `eeeeeeqeeeeeee` (14) under RATES, the scan q at 6
 *       and every window holding it of equal mass (seven e and one q).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../../memfn/src/kit.h"

static int passed, failed;

static void expect(const char *name, long got, long want)
{
    if (got == want) {
        printf("ok   %s\n", name);
        passed++;
    } else {
        printf("FAIL: %s: got %ld, want %ld\n", name, got, want);
        failed++;
    }
}

/* RATES: q 100, z 300000, e 900000, every other byte 3000 (ppm). */
static uint32_t rates[256];
static mf_akind kinds[1];
static mf_analysis an;

static const mf_analysis *an_rated(void)
{
    for (unsigned b = 0; b < 256; b++) rates[b] = 3000;
    rates['q'] = 100;
    rates['z'] = 300000;
    rates['e'] = 900000;
    memset(kinds, 0, sizeof kinds);
    kinds[0].tag = "byte-rate";
    kinds[0].version = 1;
    kinds[0].present = MF_KIND_PRESENT;
    kinds[0].digest = 1;
    kinds[0].payload = rates;
    an.list_v = MF_ANALYSIS_LIST_V;
    an.nkinds = 1;
    an.kinds = kinds;
    return &an;
}

static void *a_alloc(void *u, size_t n) { (void)u; return calloc(1, n); }
static mf_arena arena = { NULL, a_alloc };

static mf_art *art_of(const mf_analysis *a)
{
    mf_art *art = mf_art_begin(&arena, "rd", 0, NULL, a);
    if (!art || mf_art_target(art, mf_portable_target())) {
        printf("FAIL: the art does not begin\n");
        exit(1);
    }
    return art;
}

static mf_site base_site(void)
{
    mf_site s;
    memset(&s, 0, sizeof s);
    s.abi = MF_SITE_ABI;
    s.ret_pred = MF_NO_PRED;
    s.span_hi = MF_SPAN_UNBOUNDED;
    s.cand_ppm_hi = MF_PPM_FULL;
    s.empty = MF_EMPTY_MISS;
    s.pred.need = MF_REQUIRED;
    s.body = MF_BODY_ONESHOT;
    return s;
}

/* The PRES ports on the run `run` stated as the site's one presence span in
 * SET FORM (R-38 K38-2: one window alternative, one span uncut, verify NO,
 * no term; the floor SUBJECT), OPTIONAL on a DFA-scan site (the route whose
 * deciding row is P3, so the run decision's WINDOW mode answers), an ASSIGN
 * site where `k` > INT64_MIN, its head_max k (signed). `rr` gets the run's
 * reply as the class carries it (`mf_class.run`, fd_pres_run: the routed
 * PRES rows' own ask). */
static mf_wspan pwsp;
static mf_walt pwalt;

static mf_pres_picks ports_rr(const mf_analysis *a, const char *run, long long k,
                              mf_run_reply *rr)
{
    static mf_pred span;
    unsigned n = (unsigned)strlen(run);
    memset(&span, 0, sizeof span);
    memset(&pwsp, 0, sizeof pwsp);
    pwsp.len = (uint8_t)n;
    pwsp.verify = MF_VERIFY_NO;
    pwsp.core = MF_CORE_STATED;
    pwsp.core_len = (uint8_t)n;
    for (unsigned j = 0; j < n; j++)
        pwsp.set[j][(unsigned char)run[j] >> 3] |= (uint8_t)(1u << ((unsigned char)run[j] & 7));
    pwalt = (mf_walt){ MF_ENTRY_NONE, 1, &pwsp };
    span.need = MF_OPTIONAL;
    span.plan_hint = MF_NO_PRED;
    span.span_class = MF_SPAN_PRESENCE;
    span.nalt = 1;
    span.alts = &pwalt;
    span.wfloor = MF_WFLOOR_SUBJECT;
    mf_site s = base_site();
    s.op = MF_OP_ALL_PRESENT;
    s.site_kind = MF_SK_DFA_SCAN;
    s.npspan = 1;
    s.pspans = &span;
    s.pres_proof.stated = 1;
    s.pres_proof.byte = -1;
    if (k > INT64_MIN) {
        s.handoff = MF_H_ASSIGN;
        s.head_max = (int64_t)k;
    }
    mf_pres_picks pk;
    const char *why = NULL;
    mf_art *art = art_of(a);
    memset(&pk, 0, sizeof pk);
    if (mf_pres_ports(art, &s, NULL, NULL, &pk) || fd_pres_run(art, &s, rr, &why)) {
        printf("FAIL: the ports refuse the run %s (%s; %s)\n", run, why ? why : "-",
               mf_art_error(art) ? mf_art_error(art) : "-");
        failed++;
    }
    return pk;
}

/* A FIND site stating `run` as one verify-YES span (a pre-check run part's
 * statement: the run must hold whole). */
static mf_wspan wsp;
static mf_walt walt;

static mf_site run_find_site(const char *run)
{
    unsigned n = (unsigned)strlen(run);
    memset(&wsp, 0, sizeof wsp);
    wsp.start = 0;
    wsp.len = (uint8_t)n;
    wsp.verify = MF_VERIFY_YES;
    wsp.core = MF_CORE_STATED;
    wsp.core_lo = 0;
    wsp.core_len = (uint8_t)n;
    for (unsigned j = 0; j < n; j++)
        wsp.set[j][(unsigned char)run[j] >> 3] |= (uint8_t)(1u << ((unsigned char)run[j] & 7));
    walt = (mf_walt){ MF_ENTRY_NONE, 1, &wsp };
    mf_site s = base_site();
    s.pred.need = 0;
    s.op = MF_OP_FIND;
    s.form = MF_FORM_FUNC;
    s.handoff = MF_H_RETURN;
    s.use = MF_USE_POSITION;
    s.site_kind = MF_SK_DFA_SCAN;
    s.pred.fn_ref = 1;
    s.nalt = 1;
    s.alts = &walt;
    return s;
}

static int wreply(const mf_analysis *a, const char *run, mf_wreply *r)
{
    mf_site s = run_find_site(run);
    mf_art *art = art_of(a);
    if (mf_wdecide(art, &s, NULL, MF_WCALL_NONE, r) || !r->run_stated) {
        printf("FAIL: mf_wdecide names no run member for %s (%s)\n", run, mf_art_error(art));
        failed++;
        return -1;
    }
    return 0;
}

static long member(const mf_analysis *a, const char *run)
{
    mf_wreply r;
    return wreply(a, run, &r) ? -1 : r.run_member;
}

/* The verify-YES member's STRETCH, `[run_lo, run_lo + run_len)` as one
   number lo * 1000 + len. */
static long member_stretch(const mf_analysis *a, const char *run)
{
    mf_wreply r;
    return wreply(a, run, &r) ? -1 : (long)r.run_lo * 1000 + r.run_len;
}

static const char *h_fn_name(void *u, uint32_t ref) { (void)u; (void)ref; return "rd_fn"; }

/* translate's ranking of `run`, as one string of positions ("3210"). */
static void rank(const mf_analysis *a, const char *run, char out[64])
{
    mf_site s = run_find_site(run);
    mf_art *art = art_of(a);
    mf_hooks hd = { .fn_name = h_fn_name, .miss = MF_MISS_N };
    const mf_site *leg = NULL;
    const struct wf_plan *plan = NULL;
    const char *path = NULL, *why = NULL;
    out[0] = 0;
    if (wf_prepare(art, &s, &hd, MF_PH_DEFINE, 1, &leg, &plan, &path, &why) || !leg ||
        mf_art_error(art)) {
        printf("FAIL: wf_prepare renders no legacy predicate for %s (%s; %s)\n", run,
               why ? why : "-", mf_art_error(art) ? mf_art_error(art) : "-");
        failed++;
        return;
    }
    char *o = out;
    for (unsigned k = 0; k < leg->pred.rank_n && k < 20; k++)
        o += sprintf(o, "%s%u", k ? "," : "", (unsigned)leg->pred.rank_pos[k]);
}

static void expect_str(const char *name, const char *got, const char *want)
{
    if (!strcmp(got, want)) {
        printf("ok   %s\n", name);
        passed++;
    } else {
        printf("FAIL: %s: got '%s', want '%s'\n", name, got, want);
        failed++;
    }
}

int main(void)
{
    const mf_analysis *rated = an_rated();
    char r[64];

    /* ---- W1: S1095's `abcd` under NONE: every position ties, the higher
       takes it (scan 3), and the order walks down (3,2,1,0) ------------- */
    mf_run_reply rr;
    mf_pres_picks pk = ports_rr(NULL, "abcd", INT64_MIN, &rr);
    (void)pk;
    expect("scan W1 (abcd, NONE: the tie to the higher position)", rr.scan, 3);
    expect("window W1 (four positions: one window, start 0, the whole run)",
           rr.ver_lo * 1000 + rr.ver_len, 4);
    expect("member W1 (verify YES: the run decision's scan)", member(NULL, "abcd"), 3);
    expect("stretch W1 (verify YES: the whole run, [0,4))", member_stretch(NULL, "abcd"), 4);
    rank(NULL, "abcd", r);
    expect_str("rank W1 (higher positions first)", r, "3,2,1,0");

    /* ---- W2: `qzeeeeeeeeeq` (12) under RATES. q (100) is the least, at 0
       and 11: the scan 11. Windows holding 11 start at 4..min(11, 12-8) =
       4 only: [4,12), seven e and q. The twin's h over it: 1e6 x 0.9^7 =
       478,297 (rounded up at each step: 900000, 810000, 729000, 656100,
       590490, 531441, 478297), then x 100 / 1e6 = 47.83, up to 48. K 30000:
       K h = 1,440,000 >= 1e6, so the bit is 0. (The leftmost scan, 0, would
       take [0,8): q z e e e e e e, h 100 -> 30 -> 27 -> 25 -> 23 -> 21 -> 19
       -> 18; 18 x 30001 < 1e6, bit 1: the plant moves the bit.) The rank
       walks q at 11 then 0, z at 1, then the e positions from the
       highest. ---------------------------------------------------------- */
    pk = ports_rr(rated, "qzeeeeeeeeeq", 30000, &rr);
    expect("scan W2 (q at 0 and 11 tie: the higher)", rr.scan, 11);
    expect("window W2 (the one window holding 11: [4,12))", rr.ver_lo * 1000 + rr.ver_len, 4008);
    expect("twin W2 (h 48 over [4,12), K 30000: not admitted)", pk.landmark, 0);
    /* W-K3's literal at the reader: K negative admits as K 0 (max(K, 0)):
       h 48, K 0, m 1e6: (1e6 - 0) 1e6 > 1e6 x 48, the bit 1, at K -5 too */
    pk = ports_rr(rated, "qzeeeeeeeeeq", 0, &rr);
    expect("twin W2 at K 0 (admitted)", pk.landmark, 1);
    pk = ports_rr(rated, "qzeeeeeeeeeq", -5, &rr);
    expect("twin W2 at K -5 (max(K, 0): as K 0)", pk.landmark, 1);
    expect("member W2 (verify YES)", member(rated, "qzeeeeeeeeeq"), 11);
    expect("stretch W2 (verify YES: the whole run, [0,12))",
           member_stretch(rated, "qzeeeeeeeeeq"), 12);
    rank(rated, "qzeeeeeeeeeq", r);
    expect_str("rank W2 (q 11, q 0, z 1, then e from the highest)", r,
               "11,0,1,10,9,8,7,6,5,4,3,2");

    /* ---- W3: `eeeeeeqeeeeeee` (14) under RATES: the scan q at 6; windows
       holding it start at max(0, 6-7) = 0 .. min(6, 14-8) = 6, every one
       seven e and q, equal mass: the LEFTMOST, 0. ------------------------ */
    pk = ports_rr(rated, "eeeeeeqeeeeeee", INT64_MIN, &rr);
    expect("scan W3 (the one q)", rr.scan, 6);
    expect("window W3 (seven equal windows: the leftmost, [0,8))", rr.ver_lo * 1000 + rr.ver_len, 8);

    printf("checks passed: %d\n", passed);
    printf("checks failed: %d\n", failed);
    return failed ? 1 : 0;
}
