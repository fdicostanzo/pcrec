/* tests/memfn/proven_check.c -- [MEMFN] R-25 (lane memfn-r25): the form
 * class's proven sets honour what the row TESTS. `proven0` (and
 * `proven_prev`) may name only bytes the committed text tests at every
 * candidate: an offset-0 term a row may skip (OPTIONAL and untested) proves
 * nothing, whatever pcrec states it needs.
 *
 *   provenchk          one `ok   <case>` or `FAIL: <case>: <why>` line per
 *                      check, then `checks passed: N` / `checks failed: M`;
 *                      exit 1 on any failure.
 *
 * Run by tests/memfn/run_finder.sh (`make test-memfn-finder`), which floors
 * the passed count. A WHITE-BOX check: it includes the kit's internal
 * header (the one file outside memfn/src that does; arch_blind_check.py
 * exempts tests/memfn) because no shipped row skips an OPTIONAL term today,
 * so the skip path is reachable only through a row the test declares
 * itself. Its TEST-ONLY ROWS (`skip_row`, ARM_TESTS_REQUIRED; `every_row`,
 * ARM_TESTS_EVERY; `unstated_row`) go through `kit_class`, the very
 * function mf_define and mf_ask call, so the path exercised is the shipped
 * one with only the row's declaration varied. Families:
 *
 *   A  the skip path: an OPTIONAL offset-0 term under skip_row reads
 *      proven0 all ones; the same site under every_row reads the term's set
 *      (with a REQUIRED term beside it, a RUN term, and a whole OPTIONAL
 *      predicate); proven_prev likewise on a context stop.
 *   B  the refusal: a FIND row stating ARM_TESTS_UNSTATED is refused (and
 *      proves nothing); a non-FIND site is not asked for it.
 *   C  the shipped FIND rows (generic, ofsskip, the five PF rows) each state
 *      a value, and an OPTIONAL offset-0 term under each reads its set (they
 *      test every term); ofsskip once more through the public mf_ask, the
 *      real selection.
 *
 * THE CONTROL. Expected sets are written here as MEMBER STRINGS and held to
 * the kit's bitset byte by byte by `strchr` membership (`expect`), never by
 * building a bitset the way the site's terms are built (`set_of`) and never
 * through anything of the kit's; "ALL" is all 256 bytes. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../../memfn/src/kit.h"

static int passed, failed;

/* The test-only rows: a declaration and nothing else (kit_class reads only
 * `tests`, `libc` and `includes`). */
static const arm skip_row = { .id = "test-skip", .tests = ARM_TESTS_REQUIRED };
static const arm every_row = { .id = "test-every", .tests = ARM_TESTS_EVERY };
static const arm unstated_row = { .id = "test-unstated", .tests = ARM_TESTS_UNSTATED };

/* A bitset of the bytes in `members` (the site's input, not the oracle). */
static void set_of(uint8_t set[32], const char *members, size_t n)
{
    memset(set, 0, 32);
    for (size_t i = 0; i < n; i++)
        set[(unsigned char)members[i] >> 3] |= (uint8_t)(1u << ((unsigned char)members[i] & 7));
}

/* A FIND site, its terms to be filled by the caller. */
static mf_site find_site(void)
{
    mf_site s;
    memset(&s, 0, sizeof s);
    s.abi = MF_SITE_ABI;
    s.form = MF_FORM_FUNC;
    s.op = MF_OP_FIND;
    s.handoff = MF_H_RETURN;
    s.use = MF_USE_POSITION;
    s.ret_pred = MF_NO_PRED;
    s.span_hi = MF_SPAN_UNBOUNDED;
    s.cand_ppm_hi = MF_PPM_FULL;
    s.empty = MF_EMPTY_MISS;
    s.consumer = MF_C_ENGINE;
    s.policy = MF_P_PORTABLE_ONLY;
    s.body = MF_BODY_ONESHOT;
    s.pred.need = MF_REQUIRED;
    s.pred.fn_ref = 1;
    return s;
}

static void t_set(mf_term *t, int off, const char *members, mf_need need)
{
    memset(t, 0, sizeof *t);
    t->kind = MF_T_SET;
    t->offset = off;
    set_of(t->set, members, strlen(members));
    t->table_ref = strlen(members) > 1 ? 1 : 0;
    t->ppm_hi = MF_PPM_FULL;
    t->need = need;
}

static void t_run(mf_term *t, int off, const char *run, const uint8_t *mask, mf_need need)
{
    memset(t, 0, sizeof *t);
    t->kind = MF_T_RUN;
    t->offset = off;
    t->run = (const uint8_t *)run;
    t->mask = mask;
    t->run_len = (uint32_t)strlen(run);
    t->ppm_hi = MF_PPM_FULL;
    t->need = need;
}

/* "" if `bits` holds exactly the bytes of `members` ("ALL": every byte),
 * else the first byte it gets wrong, as text. */
static const char *expect(const uint8_t bits[32], const char *members)
{
    static char why[64];   /* test code, one process */
    int all = strcmp(members, "ALL") == 0;
    for (int x = 0; x < 256; x++) {
        int want = all || (x != 0 && strchr(members, x) != NULL);
        int got = (bits[x >> 3] >> (x & 7)) & 1;
        if (want != got) {
            snprintf(why, sizeof why, "byte 0x%02x %s", x, got ? "proven, not expected"
                                                            : "expected, not proven");
            return why;
        }
    }
    return "";
}

static void verdict(const char *name, const char *why)
{
    if (why && *why) { printf("FAIL: %s: %s\n", name, why); failed++; }
    else { printf("ok   %s\n", name); passed++; }
}

/* One class reading: row `a` on site `s`, proven0 (or proven_prev when
 * `prev`) held to `members`. */
static void check(const char *name, const arm *a, const mf_site *s, int prev,
                  const char *members)
{
    mf_class c;
    const char *r = kit_class(a, s, &c);
    if (r) { verdict(name, r); return; }
    verdict(name, expect(prev ? c.proven_prev : c.proven0, members));
}

/* ---- A: the skip path ---------------------------------------------------- */

static void family_a(void)
{
    static const uint8_t ci[] = { 0xDF, 0xFF };
    mf_site s = find_site();

    /* an OPTIONAL offset-0 SET beside a REQUIRED byte at offset 1 */
    s.pred.nterm = 2;
    t_set(&s.pred.term[0], 0, "ab", MF_OPTIONAL);
    t_set(&s.pred.term[1], 1, "z", MF_REQUIRED);
    s.pred.plan_hint = 1;
    check("A1 optional-0 skipped: proven0 all ones", &skip_row, &s, 0, "ALL");
    check("A2 optional-0 tested: proven0 the term's set", &every_row, &s, 0, "ab");

    /* a REQUIRED and an OPTIONAL term, both at offset 0 */
    t_set(&s.pred.term[0], 0, "abc", MF_REQUIRED);
    t_set(&s.pred.term[1], 0, "ax", MF_OPTIONAL);
    s.pred.plan_hint = 0;
    check("A3 required+optional-0, optional skipped: the required set", &skip_row, &s, 0, "abc");
    check("A4 required+optional-0, both tested: the intersection", &every_row, &s, 0, "a");

    /* RUN terms: a caseless REQUIRED run and an OPTIONAL run, disjoint first bytes */
    t_run(&s.pred.term[0], 0, "Ab", ci, MF_REQUIRED);
    t_run(&s.pred.term[1], 0, "q", NULL, MF_OPTIONAL);
    check("A5 run terms, optional skipped: the required run's first cube", &skip_row, &s, 0, "Aa");
    check("A6 run terms, both tested: empty", &every_row, &s, 0, "");

    /* a REQUIRED term of a whole OPTIONAL predicate (set-leads' lead) */
    s.pred.nterm = 1;
    t_set(&s.pred.term[0], 0, "a", MF_REQUIRED);
    s.pred.need = MF_OPTIONAL;
    check("A7 optional predicate skipped: proven0 all ones", &skip_row, &s, 0, "ALL");
    check("A8 optional predicate tested: the term's set", &every_row, &s, 0, "a");
    s.pred.need = MF_REQUIRED;
    check("A9 required term, required predicate: tested by skip_row too", &skip_row, &s, 0, "a");

    /* proven_prev: a context stop, one SET term one byte below the candidate */
    t_set(&s.pred.term[0], -1, "\n", MF_OPTIONAL);
    check("A10 optional context stop skipped: proven_prev all ones", &skip_row, &s, 1, "ALL");
    check("A11 optional context stop tested: proven_prev the set", &every_row, &s, 1, "\n");
    s.pred.term[0].need = MF_REQUIRED;
    check("A12 required context stop: proven_prev the set", &skip_row, &s, 1, "\n");
    check("A13 context stop: proven0 all ones (no offset-0 term)", &skip_row, &s, 0, "ALL");
}

/* ---- B: the refusal ------------------------------------------------------ */

static void family_b(void)
{
    mf_site s = find_site();
    s.pred.nterm = 1;
    t_set(&s.pred.term[0], 0, "ab", MF_REQUIRED);
    mf_class c;
    const char *r = kit_class(&unstated_row, &s, &c);
    verdict("B1 FIND under an UNSTATED row: refused", r ? "" : "kit_class gave it a reading");
    verdict("B2 the refused class proves nothing", expect(c.proven0, "ALL"));
    s.op = MF_OP_VERIFY;
    r = kit_class(&unstated_row, &s, &c);
    verdict("B3 a non-FIND site under an UNSTATED row: not refused", r ? r : "");
}

/* ---- C: the shipped FIND rows -------------------------------------------- */

static const char *h_fn_name(void *u, uint32_t ref)
{
    (void)u; (void)ref;
    return "rx_ofsskip";
}

static const char *h_table_name(void *u, uint32_t ref)
{
    (void)u; (void)ref;
    return "rx_ofs_k0";
}

static void *a_alloc(void *u, size_t n)
{
    (void)u;
    void *p = calloc(1, n ? n : 1);
    if (!p) { perror("calloc"); exit(2); }
    return p;
}

static void family_c(void)
{
    static const struct { const char *name; const arm *a; } rows[] = {
        { "generic", &generic_arm },
        { "ofsskip", &ofsskip_arm },
        { "pf_memchr", &pf_memchr_arm },
        { "pf_memchr_bounded", &pf_memchr_bounded_arm },
        { "pf_walk", &pf_walk_arm },
        { "pf_walk_bounded", &pf_walk_bounded_arm },
        { "pf_memchr_back", &pf_memchr_back_arm },
    };
    mf_site s = find_site();
    s.pred.nterm = 2;
    t_set(&s.pred.term[0], 0, "0123456789", MF_OPTIONAL);
    t_set(&s.pred.term[1], 3, "q", MF_REQUIRED);
    s.pred.plan_hint = 1;
    for (size_t i = 0; i < sizeof rows / sizeof rows[0]; i++) {
        char name[96];
        snprintf(name, sizeof name, "C1 %s states its tested terms", rows[i].name);
        verdict(name, rows[i].a->tests == ARM_TESTS_UNSTATED ? "ARM_TESTS_UNSTATED" : "");
        snprintf(name, sizeof name, "C2 %s: an OPTIONAL offset-0 term reads its set", rows[i].name);
        check(name, rows[i].a, &s, 0, "0123456789");
    }

    /* the real selection: mf_ask over an offset-skip site (ofsskip's row) */
    s.pred.window_stated = 1;       /* a forward FIND states its window (R17-a) */
    s.pred.move_back = 0;
    mf_arena a = { NULL, a_alloc };
    mf_art *art = mf_art_begin(&a, "rx", MF_P_PORTABLE_ONLY, 0, NULL, NULL);
    mf_hooks hd = { .fn_name = h_fn_name, .table_name = h_table_name, .miss = MF_MISS_N };
    mf_class c;
    if (!art || mf_ask(art, &s, &hd, &c))
        verdict("C3 mf_ask, offset-skip site: proven0 the OPTIONAL term's set",
                art ? "mf_ask refused the site" : "mf_art_begin failed");
    else
        verdict("C3 mf_ask, offset-skip site: proven0 the OPTIONAL term's set",
                expect(c.proven0, "0123456789"));
}

int main(void)
{
    family_a();
    family_b();
    family_c();
    printf("checks passed: %d\n", passed);
    printf("checks failed: %d\n", failed);
    return failed ? 1 : 0;
}
