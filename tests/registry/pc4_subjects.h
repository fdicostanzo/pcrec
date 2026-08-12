/* pc4_subjects.h — THE ONE HOME of PC-4's subject set (MOD-0.3e).
 *
 * Included by BOTH sides of the differential — pc4_driver.c (runs the
 * pcrec-compiled matchers) and pc4_check.c (runs libpcre2 in-process) — so
 * the two sides cannot drift apart on what was probed. A differential's
 * INPUTS must share exactly one source; it is the VERDICTS that must come
 * from independent ones.
 *
 * 256 single-byte subjects (every byte value — the census axis: any
 * one-byte membership disagreement in a produced set is caught here) plus
 * curated multi-byte subjects for span/leftmost behaviour: empty, ASCII
 * runs mixing the produced categories, newline placement (\N and \v care),
 * high bytes (\h's 0xA0, \v's 0x85), embedded NUL, and case pairs (the -i
 * axis — PC-4 is the first external oracle -i has ever met).
 *
 * `sizeof(s) - 1` carries embedded NULs correctly, so no entry needs an
 * explicit length. */

#ifndef PC4_SUBJECTS_H
#define PC4_SUBJECTS_H

#include <stddef.h>

typedef struct { const unsigned char *s; size_t len; } Pc4Subject;

#define PC4_ENTRY(str) { (const unsigned char *)(str), sizeof(str) - 1 },
#define PC4_MULTI(X) \
    X("") \
    X("ab12CD") \
    X("  \t x") \
    X("no digits here") \
    X("007") \
    X("line1\nline2") \
    X("\r\n\x0b\x0c") \
    X("\xa0 \t") \
    X("\x85\n") \
    X("_under_score_9") \
    X("DEADbeef09") \
    X("aA1!zZ") \
    X("\x00" "mid\x00") \
    X("\xff\xfe\x80") \
    X("xy-z")

static const Pc4Subject pc4_multi[] = { PC4_MULTI(PC4_ENTRY) };
#define PC4_NMULTI  (sizeof pc4_multi / sizeof pc4_multi[0])
#define PC4_NSINGLE 256
#define PC4_NSUBJ   (PC4_NSINGLE + PC4_NMULTI)

/* subject i: 0..255 = the single byte i; 256.. = pc4_multi[i - 256] */
static inline const unsigned char *pc4_subject(int i, unsigned char *onebyte,
                                               size_t *len)
{
    if (i < PC4_NSINGLE) {
        *onebyte = (unsigned char)i;
        *len = 1;
        return onebyte;
    }
    *len = pc4_multi[i - PC4_NSINGLE].len;
    return pc4_multi[i - PC4_NSINGLE].s;
}

#endif
