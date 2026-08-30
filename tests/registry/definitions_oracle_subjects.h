/* definitions_oracle_subjects.h — [DD-11.3]'s shared subject set.
 *
 * Included by BOTH sides of the differential — definitions_oracle_driver.c
 * (runs the two pcrec-compiled artifacts, prefixes `pa`/`pb`) and
 * definitions_oracle_check.c (runs libpcre2 in-process on Pattern A) — so
 * the two sides cannot drift on what was probed, PC-4's own
 * pc4_subjects.h precedent (tests/registry/CLAUDE.md) applied here.
 *
 * 256 single-byte subjects (every byte value) plus curated multis chosen
 * for THIS table's population: class-escape/POSIX-name boundary bytes are
 * already covered by the single-byte sweep; the multis add what a
 * byte-at-a-time sweep cannot — newline PLACEMENT for `^`/`$`/`\R`'s
 * `(?m)`/EOL forms, word-BOUNDARY context for `\b`/`\B`, and short runs for
 * the possessive-suffix/`(?n)` body set's quantified/alternated bodies. */

#ifndef DEFN_ORACLE_SUBJECTS_H
#define DEFN_ORACLE_SUBJECTS_H

#include <stddef.h>

typedef struct { const unsigned char *s; size_t len; } DefnSubject;

#define DEFN_ENTRY(str) { (const unsigned char *)(str), sizeof(str) - 1 },
#define DEFN_MULTI(X) \
    X("") \
    X("a") \
    X("aa") \
    X("aaa") \
    X("ab") \
    X("ba") \
    X("aab") \
    X("bab") \
    X("aabb") \
    X("123") \
    X("\n") \
    X("\r\n") \
    X("a\n") \
    X("\na") \
    X("a\nb") \
    X("a\n\n") \
    X("\n\na") \
    X("line1\nline2") \
    X("line1\nline2\n") \
    X("\x0b\x0c\x85") \
    X(" a ") \
    X("_a_") \
    X("a_b") \
    X("9a9") \
    X("word boundary here") \
    X("DEADbeef09") \
    X("aA1!zZ") \
    X("\x00mid\x00") \
    X("\xff\xfe\x80") \
    X("xy-z")

static const DefnSubject defn_multi[] = { DEFN_MULTI(DEFN_ENTRY) };
#define DEFN_NMULTI  (sizeof defn_multi / sizeof defn_multi[0])
#define DEFN_NSINGLE 256
#define DEFN_NSUBJ   (DEFN_NSINGLE + DEFN_NMULTI)

/* subject i: 0..255 = the single byte i; 256.. = defn_multi[i - 256] */
static inline const unsigned char *defn_subject(int i, unsigned char *onebyte,
                                                 size_t *len)
{
    if (i < DEFN_NSINGLE) {
        *onebyte = (unsigned char)i;
        *len = 1;
        return onebyte;
    }
    *len = defn_multi[i - DEFN_NSINGLE].len;
    return defn_multi[i - DEFN_NSINGLE].s;
}

#endif
