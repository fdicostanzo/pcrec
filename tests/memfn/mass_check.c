/* tests/memfn/mass_check.c -- span_pick units 1b and 1c (lanes sp1b, sp1c): the
 * GOLDEN VALUES of the kit's one mass primitive, `kit_mass`, its one
 * run-position-to-set conversion `kit_run_set` and the run member
 * `kit_run_member` (memfn/src/presence.c, window.c; span_pick.md rev 5.2
 * §Staging, units 1b and 1c), and the NORMAL FORM refusal at the kit's input
 * boundary they rely on (kit_presence_check, D187).
 *
 *   masschk            one `ok   <case>` or `FAIL: <case>: got G, want W` line
 *                      per check, then `checks passed: N` / `checks failed: M`;
 *                      exit 1 on any failure.
 *
 * Run by tests/memfn/run_finder.sh (`make test-memfn-finder`), which floors the
 * passed count. White-box (it includes the kit's internal header, as
 * proven_check.c does): these entries are internal to the kit.
 *
 * What it holds:
 *   NONE  the declared NONE row (no rates): floor(k x 1e6 / 256) over the
 *         multiset's member count k, taken ONCE (k = 1, 3, 6, 16, 256; 16
 *         one-byte positions are 62,500, not 16 x 3,906 = 62,496);
 *   MULTI a byte repeated across positions is counted at each (`zzzzzzz~J`'s
 *         window), under NONE and under rates: a set-shaped primitive (the
 *         union of the positions) reads less;
 *   CAP   capped (KIT_MASS_CAP, 1e6) vs uncapped (KIT_MASS_SUM), under rates
 *         and under NONE past 256 members; and the cap taken once over the
 *         TOTAL of two or more rated positions;
 *   RUN   kit_run_set: a run position's set is {x : (x & mask) == run}, a
 *         byte outside its mask the EMPTY set (the vocabulary's formula, never
 *         the cube run | f);
 *   MEMBER kit_run_member: the least mass, ties to the HIGHER position
 *         (T_MASS_STRETCH), `exact` keeping one-member positions only, and
 *         `after` walking the whole order (translate's ranking);
 *   NORMAL kit_presence_check refuses a presence RUN byte outside its mask and
 *         accepts the same span in normal form (its control: the refusal is
 *         not firing on every run).
 *
 * THE CONTROL. Every expected value is a LITERAL derived by hand in its
 * comment from the rate tables' formulas below (rate1[b] = 1000 + b, rate2[b]
 * = 5000, rate3[b] = 1 for b < 2, else 1000 + b), never computed here and never through another kit function. */
#include <stdio.h>
#include <string.h>

#include "../../memfn/src/kit.h"

static int passed, failed;
static uint32_t rate1[256], rate2[256], rate3[256];

static void expect(const char *name, uint32_t got, uint32_t want)
{
    if (got == want) {
        printf("ok   %s\n", name);
        passed++;
    } else {
        printf("FAIL: %s: got %u, want %u\n", name, got, want);
        failed++;
    }
}

/* A set position over `members` (its bitset is the input, not the oracle). */
static void set_of(uint8_t set[32], const char *members)
{
    memset(set, 0, 32);
    for (; *members; members++)
        set[(unsigned char)*members >> 3] |= (uint8_t)(1u << ((unsigned char)*members & 7));
}

/* A set position over the bytes lo..hi. */
static void range_of(uint8_t set[32], unsigned lo, unsigned hi)
{
    memset(set, 0, 32);
    for (unsigned b = lo; b <= hi; b++) set[b >> 3] |= (uint8_t)(1u << (b & 7));
}

/* A one-byte position. */
static void byte_of(uint8_t set[32], unsigned b)
{
    range_of(set, b, b);
}

/* The run member's reader of consecutive sets (as window.c's). */
static const uint8_t *sets_at(const void *src, unsigned j, uint8_t buf[32])
{
    (void)buf;
    return (const uint8_t *)src + 32u * j;
}

int main(void)
{
    for (unsigned b = 0; b < 256; b++) {
        rate1[b] = 1000u + b;
        rate2[b] = 5000u;
        rate3[b] = b < 2 ? 1u : 1000u + b;
    }
    uint8_t abc[32], all[32];
    set_of(abc, "abc");
    memset(all, 0xFF, 32);
    uint8_t p[16][32];

    /* ---- NONE: floor(k x 1e6 / 256) ------------------------------------- */
    byte_of(p[0], 'A');                                 /* k = 1: 1e6/256 = 3906.25 */
    expect("NONE k=1 (one byte)", kit_mass(NULL, p[0], 1, KIT_MASS_SUM), 3906);
    memcpy(p[0], abc, 32);                              /* k = 3: 3e6/256 = 11718.75 */
    expect("NONE k=3 (a set of 3)", kit_mass(NULL, p[0], 1, KIT_MASS_SUM), 11718);
    range_of(p[0], 0x40, 0x41);                         /* 2 */
    range_of(p[1], 0x10, 0x13);                         /* 4 */
    expect("NONE k=6 (two sets, 2 + 4)", kit_mass(NULL, p[0], 2, KIT_MASS_SUM), 23437); /* 23437.5 */
    range_of(p[0], 0x30, 0x3F);                         /* 16 */
    expect("NONE k=16 (one set of 16)", kit_mass(NULL, p[0], 1, KIT_MASS_SUM), 62500);
    for (unsigned i = 0; i < 16; i++) byte_of(p[i], 0x30 + i);
    expect("NONE k=16 (16 one-byte positions: once, not 16 x 3906)",
           kit_mass(NULL, p[0], 16, KIT_MASS_SUM), 62500);
    memcpy(p[0], all, 32);                              /* k = 256: 1e6 exactly */
    expect("NONE k=256 (the full set)", kit_mass(NULL, p[0], 1, KIT_MASS_SUM), 1000000);
    expect("NONE k=256 (the full set, capped)", kit_mass(NULL, p[0], 1, KIT_MASS_CAP), 1000000);

    /* ---- MULTI: a repeated byte counted per position -------------------- */
    for (unsigned i = 0; i < 7; i++) byte_of(p[i], 'z');
    byte_of(p[7], '~');
    byte_of(p[8], 'J');
    /* rates: 7 x (1000 + 122) + (1000 + 126) + (1000 + 74) = 7854 + 2200;
       the union {z, ~, J} would read 1122 + 1126 + 1074 = 3322 */
    expect("MULTI zzzzzzz~J under rates", kit_mass(rate1, p[0], 9, KIT_MASS_SUM), 10054);
    /* NONE: k = 9, 9e6/256 = 35156.25; the union's k = 3 would read 11718 */
    expect("MULTI zzzzzzz~J under NONE", kit_mass(NULL, p[0], 9, KIT_MASS_SUM), 35156);
    byte_of(p[0], 'a');
    memcpy(p[1], abc, 32);                              /* 'a' again inside the set */
    /* 1097 + (1097 + 1098 + 1099) */
    expect("MULTI a byte and a set holding it", kit_mass(rate1, p[0], 2, KIT_MASS_SUM), 4391);

    /* ---- the rates on each position size ---------------------------------- */
    byte_of(p[0], 'z');                                 /* 1000 + 122 */
    expect("rates one byte", kit_mass(rate1, p[0], 1, KIT_MASS_SUM), 1122);
    range_of(p[0], 0x40, 0x41);                         /* 1064 + 1065 */
    expect("rates a set of 2", kit_mass(rate1, p[0], 1, KIT_MASS_SUM), 2129);
    memcpy(p[1], abc, 32);                              /* + 1097 + 1098 + 1099 */
    expect("rates a set of 2 and a set of 3", kit_mass(rate1, p[0], 2, KIT_MASS_SUM), 5423);

    /* ---- CAP: capped vs uncapped ---------------------------------------- */
    memcpy(p[0], all, 32);                              /* 256 x 5000 = 1,280,000 */
    expect("CAP uncapped full set", kit_mass(rate2, p[0], 1, KIT_MASS_SUM), 1280000);
    expect("CAP capped full set", kit_mass(rate2, p[0], 1, KIT_MASS_CAP), 1000000);
    memcpy(p[0], abc, 32);                              /* 3 x 5000, under the cap */
    expect("CAP under the cap, capped", kit_mass(rate2, p[0], 1, KIT_MASS_CAP), 15000);
    memcpy(p[0], all, 32);
    memcpy(p[1], all, 32);                              /* NONE k = 512: 2,000,000 */
    expect("CAP NONE k=512 uncapped", kit_mass(NULL, p[0], 2, KIT_MASS_SUM), 2000000);
    expect("CAP NONE k=512 capped", kit_mass(NULL, p[0], 2, KIT_MASS_CAP), 1000000);

    /* The cap is taken ONCE over the total, never per position (a plant that
     * capped each position's rated sum and summed the capped values reads
     * 2,000,000 / 1,280,000 below). */
    /* p[0], p[1] the full set: 2 x 1,280,000 = 2,560,000 */
    expect("CAP rated two full sets uncapped", kit_mass(rate2, p[0], 2, KIT_MASS_SUM), 2560000);
    expect("CAP rated two full sets capped", kit_mass(rate2, p[0], 2, KIT_MASS_CAP), 1000000);
    range_of(p[0], 0x00, 0x7F);                         /* 128 x 5000 = 640,000 */
    range_of(p[1], 0x80, 0xFF);                         /* 640,000 */
    expect("CAP rated two half sets uncapped (each under 1e6)",
           kit_mass(rate2, p[0], 2, KIT_MASS_SUM), 1280000);
    expect("CAP rated two half sets capped (each under 1e6)",
           kit_mass(rate2, p[0], 2, KIT_MASS_CAP), 1000000);
    memcpy(p[1], abc, 32);                              /* 640,000 + 15,000, still under */
    expect("CAP rated half set and a set, under the cap",
           kit_mass(rate2, p[0], 2, KIT_MASS_CAP), 655000);

    /* ---- RUN: kit_run_set, {x : (x & mask) == run} ------------------------ */
    {
        static const uint8_t run[] = { 'A', 0x10, 'z', 'a' };
        static const uint8_t mask[] = { 0xDF, 0xFC, 0xFF, 0xDF };
        mf_term t;
        memset(&t, 0, sizeof t);
        t.kind = MF_T_RUN;
        t.run = run;
        t.mask = mask;
        t.run_len = 4;
        kit_run_set(&t, 0, p[0]);                       /* 'A','a': 1065 + 1097 */
        expect("RUN a case-folded position", kit_mass(rate1, p[0], 1, KIT_MASS_SUM), 2162);
        kit_run_set(&t, 1, p[0]);                       /* 0x10..0x13: 4 x 1000 + 70 */
        expect("RUN a two-bit-free position", kit_mass(rate1, p[0], 1, KIT_MASS_SUM), 4070);
        kit_run_set(&t, 2, p[0]);                       /* 'z' alone: 1122 */
        expect("RUN an exact position", kit_mass(rate1, p[0], 1, KIT_MASS_SUM), 1122);
        /* 'a' (0x61) has bit 0x20 outside mask 0xDF: no byte x has
           (x & 0xDF) == 0x61, so the set is EMPTY (the cube 'a' | f would
           read 'a' alone: 1097, and NONE 3906) */
        kit_run_set(&t, 3, p[0]);
        expect("RUN a byte outside its mask is the empty set",
               kit_mass(rate1, p[0], 1, KIT_MASS_SUM), 0);
        expect("RUN a byte outside its mask under NONE", kit_mass(NULL, p[0], 1, KIT_MASS_SUM), 0);
        t.mask = NULL;                                  /* NULL mask: exact, 'a' alone */
        kit_run_set(&t, 3, p[0]);
        expect("RUN a NULL mask is exact", kit_mass(rate1, p[0], 1, KIT_MASS_SUM), 1097);
    }

    /* ---- MEMBER: kit_run_member ------------------------------------------- */
    {
        uint8_t r[5][32];
        byte_of(r[0], 'c');                             /* 1099 */
        byte_of(r[1], 'a');                             /* 1097 */
        byte_of(r[2], 'b');                             /* 1098 */
        byte_of(r[3], 'a');                             /* 1097, ties position 1 */
        range_of(r[4], 0x00, 0x00);                     /* 1000: the least, one member */
        kit_member m = kit_run_member(rate1, sets_at, r, 4, 0, NULL);
        /* positions 1 and 3 tie at 1097: the HIGHER (3) takes the tie */
        expect("MEMBER the least mass, a tie to the higher position", (uint32_t)m.pos, 3);
        expect("MEMBER its mass", m.mass, 1097);
        m = kit_run_member(NULL, sets_at, r, 4, 0, NULL);
        /* NONE: every position 3906, so the highest position (3) */
        expect("MEMBER under NONE: the highest position", (uint32_t)m.pos, 3);
        range_of(r[4], 0x00, 0x01);                     /* 2001, but two members */
        range_of(r[3], 0x61, 0x62);                     /* 'a','b': 2195, two members */
        m = kit_run_member(rate3, sets_at, r, 5, 0, NULL);
        /* rate3: 0 1099, 1 1097, 2 1098, 3 2195, 4 {0x00,0x01} = 2: 4 */
        expect("MEMBER rate3 all positions: the two-member least", (uint32_t)m.pos, 4);
        m = kit_run_member(rate3, sets_at, r, 5, 1, NULL);
        /* exact: positions 3 and 4 are not candidates; 1 (1097) is least */
        expect("MEMBER exact keeps one-member positions only", (uint32_t)m.pos, 1);
        m = kit_run_member(rate1, sets_at, r, 5, 0, NULL);
        /* all: 0 1099, 1 1097, 2 1098, 3 2195, 4 2001 -> 1 */
        expect("MEMBER all positions", (uint32_t)m.pos, 1);
        /* the whole order from `after`: 1 (1097), 2 (1098), 0 (1099),
           4 (2001), 3 (2195), then none */
        static const int order[] = { 1, 2, 0, 4, 3, -1 };
        kit_member a = { -1, 0 };
        int ok = 1;
        for (unsigned k = 0; k < 6; k++) {
            a = kit_run_member(rate1, sets_at, r, 5, 0, k ? &a : NULL);
            if (a.pos != order[k]) ok = 0;
            if (a.pos < 0) break;
        }
        expect("MEMBER `after` walks the whole order, then none", (uint32_t)ok, 1);
        for (unsigned j = 0; j < 4; j++) byte_of(r[j], 'q');      /* four equal masses */
        static const int ties[] = { 3, 2, 1, 0 };
        ok = 1;
        a = (kit_member){ -1, 0 };
        for (unsigned k = 0; k < 4; k++) {
            a = kit_run_member(rate1, sets_at, r, 4, 0, k ? &a : NULL);
            if (a.pos != ties[k]) ok = 0;
        }
        expect("MEMBER `after` on equal masses: higher positions first", (uint32_t)ok, 1);
    }

    /* ---- NORMAL: the presence run's normal form, refused at the boundary --- */
    {
        static const uint8_t folded[] = { 'A', 'B', 'C' }, mask[] = { 0xDF, 0xDF, 0xDF };
        static const uint8_t lower[] = { 'a', 'B', 'C' };      /* 'a' & ~0xDF: outside */
        mf_pred span;
        memset(&span, 0, sizeof span);
        span.nterm = 1;
        span.need = MF_REQUIRED;
        span.plan_hint = MF_NO_PRED;
        span.span_class = MF_SPAN_PRESENCE;
        span.term[0].kind = MF_T_RUN;
        span.term[0].need = MF_REQUIRED;
        span.term[0].run = folded;
        span.term[0].mask = mask;
        span.term[0].run_len = 3;
        mf_site s;
        memset(&s, 0, sizeof s);
        s.abi = MF_SITE_ABI;
        s.op = MF_OP_ALL_PRESENT;
        s.npspan = 1;
        s.pspans = &span;
        s.pres_proof.stated = 1;
        s.pres_proof.byte = -1;
        const char *why = kit_presence_check(&s);
        if (why) printf("note: the normal span is refused: %s\n", why);
        expect("NORMAL a normal presence run is accepted (the control)", why == NULL, 1);
        span.term[0].run = lower;
        why = kit_presence_check(&s);
        expect("NORMAL a presence run byte outside its mask is refused",
               why != NULL && strstr(why, "outside its mask") != NULL, 1);
        span.term[0].mask = NULL;                       /* exact: 'a' is normal */
        why = kit_presence_check(&s);
        expect("NORMAL an exact presence run is accepted", why == NULL, 1);
    }

    printf("checks passed: %d\n", passed);
    printf("checks failed: %d\n", failed);
    return failed ? 1 : 0;
}
