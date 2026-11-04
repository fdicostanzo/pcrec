/* tests/memfn/mass_check.c -- span_pick unit 1b (lane sp1b): the GOLDEN VALUES
 * of the kit's one mass primitive, `kit_mass` (memfn/src/presence.c; span_pick.md
 * rev 5.2 §Staging, unit 1b's witness).
 *
 *   masschk            one `ok   <case>` or `FAIL: <case>: got G, want W` line
 *                      per check, then `checks passed: N` / `checks failed: M`;
 *                      exit 1 on any failure.
 *
 * Run by tests/memfn/run_finder.sh (`make test-memfn-finder`), which floors the
 * passed count. White-box (it includes the kit's internal header, as
 * proven_check.c does): kit_mass is internal to the kit.
 *
 * What it holds:
 *   NONE  the declared NONE row (no rates): floor(k x 1e6 / 256) over the
 *         multiset's member count k, taken ONCE (k = 1, 3, 6, 16, 256; 16
 *         one-byte positions are 62,500, not 16 x 3,906 = 62,496);
 *   MULTI a byte repeated across positions is counted at each (`zzzzzzz~J`'s
 *         window), under NONE and under rates: a set-shaped primitive (the
 *         union of the positions) reads less;
 *   CAP   capped (KIT_MASS_CAP, 1e6) vs uncapped (KIT_MASS_SUM), under rates
 *         and under NONE past 256 members; a cube and a set position; and the cap
 *         taken once over the TOTAL of two or more rated positions.
 *
 * THE CONTROL. Every expected value is a LITERAL derived by hand in its
 * comment from the rate tables' formulas below (rate1[b] = 1000 + b, rate2[b]
 * = 5000), never computed here and never through another kit function. */
#include <stdio.h>
#include <string.h>

#include "../../memfn/src/kit.h"

static int passed, failed;
static uint32_t rate1[256], rate2[256];

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

/* A one-byte position. */
static kit_pos byte_pos(unsigned b)
{
    return (kit_pos){ .t = (uint8_t)b, .mask = 0xFFu };
}

/* A set position over `members` (its bitset is the input, not the oracle). */
static void set_of(uint8_t set[32], const char *members)
{
    memset(set, 0, 32);
    for (; *members; members++)
        set[(unsigned char)*members >> 3] |= (uint8_t)(1u << ((unsigned char)*members & 7));
}

int main(void)
{
    for (unsigned b = 0; b < 256; b++) {
        rate1[b] = 1000u + b;
        rate2[b] = 5000u;
    }
    uint8_t abc[32], all[32];
    set_of(abc, "abc");
    memset(all, 0xFF, 32);
    kit_pos p[16];

    /* ---- NONE: floor(k x 1e6 / 256) ------------------------------------- */
    p[0] = byte_pos('A');                               /* k = 1: 1e6/256 = 3906.25 */
    expect("NONE k=1 (one byte)", kit_mass(NULL, p, 1, KIT_MASS_SUM), 3906);
    p[0] = (kit_pos){ .set = abc };                     /* k = 3: 3e6/256 = 11718.75 */
    expect("NONE k=3 (a set of 3)", kit_mass(NULL, p, 1, KIT_MASS_SUM), 11718);
    p[0] = (kit_pos){ .t = 0x40, .mask = 0xFE };        /* 0x40,0x41: 2 */
    p[1] = (kit_pos){ .t = 0x10, .mask = 0xFC };        /* 0x10..0x13: 4 */
    expect("NONE k=6 (two cubes, 2 + 4)", kit_mass(NULL, p, 2, KIT_MASS_SUM), 23437); /* 23437.5 */
    p[0] = (kit_pos){ .t = 0x30, .mask = 0xF0 };        /* 0x30..0x3F: 16 */
    expect("NONE k=16 (one cube of 16)", kit_mass(NULL, p, 1, KIT_MASS_SUM), 62500);
    for (unsigned i = 0; i < 16; i++) p[i] = byte_pos(0x30 + i);
    expect("NONE k=16 (16 one-byte positions: once, not 16 x 3906)",
           kit_mass(NULL, p, 16, KIT_MASS_SUM), 62500);
    p[0] = (kit_pos){ .set = all };                     /* k = 256: 1e6 exactly */
    expect("NONE k=256 (the full set)", kit_mass(NULL, p, 1, KIT_MASS_SUM), 1000000);
    p[0] = (kit_pos){ .t = 0x00, .mask = 0x00 };        /* the full cube: 256 */
    expect("NONE k=256 (the full cube)", kit_mass(NULL, p, 1, KIT_MASS_CAP), 1000000);

    /* ---- MULTI: a repeated byte counted per position -------------------- */
    for (unsigned i = 0; i < 7; i++) p[i] = byte_pos('z');
    p[7] = byte_pos('~');
    p[8] = byte_pos('J');
    /* rates: 7 x (1000 + 122) + (1000 + 126) + (1000 + 74) = 7854 + 2200;
       the union {z, ~, J} would read 1122 + 1126 + 1074 = 3322 */
    expect("MULTI zzzzzzz~J under rates", kit_mass(rate1, p, 9, KIT_MASS_SUM), 10054);
    /* NONE: k = 9, 9e6/256 = 35156.25; the union's k = 3 would read 11718 */
    expect("MULTI zzzzzzz~J under NONE", kit_mass(NULL, p, 9, KIT_MASS_SUM), 35156);
    p[0] = byte_pos('a');
    p[1] = (kit_pos){ .set = abc };                     /* 'a' again inside the set */
    /* 1097 + (1097 + 1098 + 1099) */
    expect("MULTI a byte and a set holding it", kit_mass(rate1, p, 2, KIT_MASS_SUM), 4391);

    /* ---- the rates on each position shape -------------------------------- */
    p[0] = byte_pos('z');                               /* 1000 + 122 */
    expect("rates one byte", kit_mass(rate1, p, 1, KIT_MASS_SUM), 1122);
    p[0] = (kit_pos){ .t = 0x40, .mask = 0xFE };        /* 1064 + 1065 */
    expect("rates a cube of 2", kit_mass(rate1, p, 1, KIT_MASS_SUM), 2129);
    p[1] = (kit_pos){ .set = abc };                     /* + 1097 + 1098 + 1099 */
    expect("rates a cube and a set", kit_mass(rate1, p, 2, KIT_MASS_SUM), 5423);

    /* ---- CAP: capped vs uncapped ---------------------------------------- */
    p[0] = (kit_pos){ .set = all };                     /* 256 x 5000 = 1,280,000 */
    expect("CAP uncapped full set", kit_mass(rate2, p, 1, KIT_MASS_SUM), 1280000);
    expect("CAP capped full set", kit_mass(rate2, p, 1, KIT_MASS_CAP), 1000000);
    p[0] = (kit_pos){ .t = 0x00, .mask = 0x00 };        /* the same bytes as a cube */
    expect("CAP uncapped full cube", kit_mass(rate2, p, 1, KIT_MASS_SUM), 1280000);
    expect("CAP capped full cube", kit_mass(rate2, p, 1, KIT_MASS_CAP), 1000000);
    p[0] = (kit_pos){ .set = abc };                     /* 3 x 5000, under the cap */
    expect("CAP under the cap, capped", kit_mass(rate2, p, 1, KIT_MASS_CAP), 15000);
    p[0] = (kit_pos){ .set = all };
    p[1] = (kit_pos){ .set = all };                     /* NONE k = 512: 2,000,000 */
    expect("CAP NONE k=512 uncapped", kit_mass(NULL, p, 2, KIT_MASS_SUM), 2000000);
    expect("CAP NONE k=512 capped", kit_mass(NULL, p, 2, KIT_MASS_CAP), 1000000);

    /* The cap is taken ONCE over the total, never per position (a plant that
     * capped each position's rated sum and summed the capped values reads
     * 2,000,000 / 1,280,000 below). */
    p[0] = (kit_pos){ .set = all };
    p[1] = (kit_pos){ .set = all };                     /* 2 x 1,280,000 = 2,560,000 */
    expect("CAP rated two full sets uncapped", kit_mass(rate2, p, 2, KIT_MASS_SUM), 2560000);
    expect("CAP rated two full sets capped", kit_mass(rate2, p, 2, KIT_MASS_CAP), 1000000);
    p[0] = (kit_pos){ .t = 0x00, .mask = 0x80 };        /* 0x00..0x7F: 128 x 5000 = 640,000 */
    p[1] = (kit_pos){ .t = 0x80, .mask = 0x80 };        /* 0x80..0xFF: 640,000 */
    expect("CAP rated two half cubes uncapped (each under 1e6)",
           kit_mass(rate2, p, 2, KIT_MASS_SUM), 1280000);
    expect("CAP rated two half cubes capped (each under 1e6)",
           kit_mass(rate2, p, 2, KIT_MASS_CAP), 1000000);
    p[1] = (kit_pos){ .set = abc };                     /* 640,000 + 15,000, still under */
    expect("CAP rated half cube and a set, under the cap",
           kit_mass(rate2, p, 2, KIT_MASS_CAP), 655000);

    printf("checks passed: %d\n", passed);
    printf("checks failed: %d\n", failed);
    return failed ? 1 : 0;
}
