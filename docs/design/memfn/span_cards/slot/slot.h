/* span_cards/slot/slot.h — the slot driver's arm table (span_cards.md §3.2-§3.3). One launch executable is
 * drv.c + gen.c + tab.c (written by link.py) + one PAD object and one ARM object per arm and twin. Every arm
 * object defines `<sym>_time` (the timed loop: its address is the arm's placement) and `<sym>_gate` (the same
 * loop counting, summing and hashing what it finds, run before any clock). */
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
    int         nlen;
    uint32_t    len[3];
    /* the subject (gen.c): find: hits from `hit` (split one: hit[0]; alt: alternating hit[0], hit[1]) on
       the shared miss text; cmp/null: E candidates every 64 bytes; art: the file `subj` */
    int         landing, split;
    uint32_t    gap;
    int         nhit;
    unsigned char hit[16];
    unsigned char member[32];       /* cmp: the set test's members (bitmap), or empty for a run         */
    int         L;
    unsigned char run[32], mask[32];
    int         pass;               /* cmp/null: 0 (p0) or 50 (p50)                                    */
    long long   events;             /* -1: `-`                                                         */
    const char *subj;               /* art: the subject file (raw bytes)                               */
    const char *expect;             /* art: the file holding `count sum fnv` (python re's answer)      */
} arm;

extern const arm slot_arms[];
extern const int slot_narms;

/* gen.c: subject `idx` of the pool for arm `a` at length `len`, into buf (len bytes) and, for cmp/null,
   the candidate array; the expectation (count, sum, FNV-1a-64 of the found positions or passing indices). */
void gen_subject(const arm *a, uint32_t len, uint32_t idx, unsigned char *buf, uint32_t *cand, size_t *nc,
                 uint64_t *count, uint64_t *sum, uint64_t *h);
uint64_t fnv_pos(uint64_t h, uint64_t pos);
#define FNV0 1469598103934665603ull
#define POOL_BYTES (16u << 20)      /* the pinned 16 MiB pool (§2.3)                                      */
#define CAND_STRIDE 64u             /* a candidate every 64 bytes: E = len / 64 (UNMEASURED DEFAULT, D149) */
#endif
