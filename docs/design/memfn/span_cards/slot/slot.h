/* span_cards/slot/slot.h — the slot driver's arm table (span_cards.md §3.2-§3.3). One launch executable is
 * drv.c + gen.c + tab.c (written by link.py) + one PAD object and one ARM object per arm and twin. Every arm
 * object defines `<sym>_time` (the timed loop: its address is the arm's placement) and `<sym>_gate` (the same
 * loop counting, summing and hashing what it finds). THE ANSWER GATE (drv gate, before any clock) runs BOTH over
 * every subject of every (arm, length) pool: `_gate`'s count, sum and FNV and `_time`'s count against gen.c's
 * (review r9 G1: the thing timed is the thing gated). */
#ifndef SLOT_H
#define SLOT_H
#include <stddef.h>
#include <stdint.h>

enum { K_FIND, K_CMP, K_NULL, K_ART };          /* a find form, a compare, the null base, a whole artifact */
enum { LD_MISS, LD_PERIODIC, LD_RANDOM };

typedef uint64_t (*time_fn)(const unsigned char *s, size_t n, const uint32_t *c, size_t nc);
typedef uint64_t (*gate_fn)(const unsigned char *s, size_t n, const uint32_t *c, size_t nc,
                            uint64_t *sum, uint64_t *h);

typedef struct {
    const char *name;               /* the row key, KEY#b, base.<name>                                  */
    int         kind;
    time_fn     time;
    gate_fn     gate;
    int         nlen;               /* 1..3; link.py writes the plan's lengths                          */
    uint32_t    len[3];
    /* the subject (gen.c): find: hits from `hit` (split one: hit[0]; alt: alternating hit[0], hit[1]) on
       the shared miss text; cmp/null: E candidates every 64 bytes; art: the file `subj` */
    int         landing, split;
    uint32_t    gap;
    unsigned char hit[16];
    unsigned char member[32];       /* cmp: the set test's members (bitmap), or empty for a run         */
    int         L;
    unsigned char run[32], mask[32];
    int         pass;               /* cmp/null: 0 (p0) or 50 (p50)                                    */
    const char *subj;               /* art: the subject file (raw bytes)                               */
    const char *expect;             /* art: the file holding `count sum fnv` (python re's answer)      */
} arm;

extern const arm slot_arms[];
extern const int slot_narms;
/* the union of every find form's members (bitmap), from the forms' own facts (link.py): the miss text avoids
   them, so every find arm reads the same bytes and differs only by its planted hits */
extern const unsigned char slot_find_members[32];

/* gen.c: subject `idx` of the pool for arm `a` at length `len`, into buf (len bytes) and, for cmp/null,
   the candidate array; the expectation (count, sum, FNV-1a-64 of the found positions or passing indices).
   `sentinel` (the gate's second subject, never timed): the same subject with a hit at its LAST byte (find) or
   its LAST candidate passing (cmp), so a timed loop that stops short of the end misses even on a miss-only or
   p0 subject (r9 G1's "halve the timed loop"). */
void gen_subject(const arm *a, uint32_t len, uint32_t idx, unsigned char *buf, uint32_t *cand, size_t *nc,
                 uint64_t *count, uint64_t *sum, uint64_t *h, int sentinel);
uint64_t fnv_pos(uint64_t h, uint64_t pos);
#define FNV0 1469598103934665603ull
#ifndef POOL_BYTES                 /* the pinned 16 MiB pool (§2.3): plan.py's, passed by link.py           */
#error "POOL_BYTES is plan.py's: link.py passes -DPOOL_BYTES"
#endif
#ifndef CAND_STRIDE                /* a candidate every CAND_STRIDE bytes: plan.py's, passed by link.py      */
#error "CAND_STRIDE is plan.py's: link.py passes -DCAND_STRIDE"
#endif
#endif
