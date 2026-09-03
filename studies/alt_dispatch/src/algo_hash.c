#include "algo_hash.h"
#include <stdlib.h>
#include <string.h>

#define MAXK 4

typedef struct {
    bool used;
    unsigned char key[MAXK];
    int *group;
    int gn, gcap;
} Slot;

struct HashIdx {
    int k;
    Slot *slots;
    int cap;         /* power of two */
    int nkeys;        /* distinct keys stored */
    const Branch **shorts; /* branches with len < k */
    int nshorts;
};

static uint32_t fnv1a(const unsigned char *key, int k)
{
    uint32_t h = 2166136261u;
    for (int i = 0; i < k; i++) { h ^= key[i]; h *= 16777619u; }
    return h;
}

static int next_pow2(int x)
{
    int p = 16;
    while (p < x) p <<= 1;
    return p;
}

static Slot *slot_find_or_insert(HashIdx *hi, const unsigned char *key, bool *is_new)
{
    uint32_t h = fnv1a(key, hi->k) & (uint32_t)(hi->cap - 1);
    for (int probe = 0; probe < hi->cap; probe++) {
        uint32_t i = (h + (uint32_t)probe) & (uint32_t)(hi->cap - 1);
        Slot *s = &hi->slots[i];
        if (!s->used) { s->used = true; memcpy(s->key, key, (size_t)hi->k); *is_new = true; return s; }
        if (memcmp(s->key, key, (size_t)hi->k) == 0) { *is_new = false; return s; }
    }
    /* unreachable at the load factor this study builds tables with */
    return NULL;
}

static void group_push(Slot *s, int idx)
{
    if (s->gn == s->gcap) {
        s->gcap = s->gcap ? s->gcap * 2 : 4;
        s->group = realloc(s->group, (size_t)s->gcap * sizeof(int));
    }
    s->group[s->gn++] = idx;
}

/* Enumerate every concrete k-byte realization of branch `b`'s first k
 * classes, depth-first, calling `emit(key, ctx)` for each -- up to 2^k for
 * this study's <=2-member classes. */
static void enumerate(const Branch *b, int k, int pos, unsigned char *key,
                      void (*emit)(const unsigned char *, int, void *), void *ctx)
{
    if (pos == k) { emit(key, b->index, ctx); return; }
    const ByteSet *cs = &b->seq[pos];
    for (int c = 0; c < 256; c++) {
        if (bs_test(cs, (unsigned char)c)) {
            key[pos] = (unsigned char)c;
            enumerate(b, k, pos + 1, key, emit, ctx);
        }
    }
}

typedef struct { HashIdx *hi; } EmitCtx;

static void emit_insert(const unsigned char *key, int branch_index, void *vctx)
{
    EmitCtx *ec = vctx;
    bool is_new;
    Slot *s = slot_find_or_insert(ec->hi, key, &is_new);
    if (is_new) ec->hi->nkeys++;
    group_push(s, branch_index);
}

HashIdx *hash_build(const BranchSet *bs, int k)
{
    if (k > MAXK) k = MAXK;
    HashIdx *hi = calloc(1, sizeof *hi);
    hi->k = k;

    int nlong = 0;
    for (int i = 0; i < bs->n; i++) if (bs->br[i].len >= k) nlong++;
    hi->cap = next_pow2(nlong * (1 << k) * 2 + 16);
    hi->slots = calloc((size_t)hi->cap, sizeof(Slot));

    hi->shorts = malloc((size_t)bs->n * sizeof(const Branch *));
    hi->nshorts = 0;

    EmitCtx ec = { hi };
    unsigned char key[MAXK];
    for (int i = 0; i < bs->n; i++) {
        const Branch *b = &bs->br[i];
        if (b->len < k) { hi->shorts[hi->nshorts++] = b; continue; }
        enumerate(b, k, 0, key, emit_insert, &ec);
    }
    return hi;
}

void hash_free(HashIdx *hi)
{
    if (!hi) return;
    for (int i = 0; i < hi->cap; i++) free(hi->slots[i].group);
    free(hi->slots);
    free((void *)hi->shorts);
    free(hi);
}

size_t hash_bytes(const HashIdx *hi)
{
    size_t s = sizeof(*hi) + (size_t)hi->cap * sizeof(Slot);
    for (int i = 0; i < hi->cap; i++) s += (size_t)hi->slots[i].gcap * sizeof(int);
    s += (size_t)hi->nshorts * sizeof(const Branch *);
    return s;
}

int hash_table_slots(const HashIdx *hi) { return hi->cap; }
int hash_distinct_keys(const HashIdx *hi) { return hi->nkeys; }

static bool branch_matches_full(const Branch *b, const unsigned char *subj,
                                size_t slen, size_t pos, long long *vb, int start_at)
{
    size_t avail = pos < slen ? slen - pos : 0;
    for (int k = start_at; k < b->len; k++) {
        if ((size_t)k >= avail) return false;
        (*vb)++;
        if (!bs_test(&b->seq[k], subj[pos + (size_t)k])) return false;
    }
    return true;
}

Answer hash_dispatch(const HashIdx *hi, const BranchSet *bs,
                     const unsigned char *subj, size_t slen, size_t pos,
                     Cost *cost)
{
    (void)bs;
    int best = -1, best_len = 0;

    /* per-byte path: branches shorter than k */
    for (int i = 0; i < hi->nshorts; i++) {
        cost->tries++;
        const Branch *b = hi->shorts[i];
        if (branch_matches_full(b, subj, slen, pos, &cost->verify_bytes, 0)) {
            best = b->index; best_len = b->len; break;
        }
    }

    size_t avail = pos < slen ? slen - pos : 0;
    if (avail >= (size_t)hi->k) {
        cost->tries++; /* the block hash probe itself */
        unsigned char key[MAXK];
        memcpy(key, subj + pos, (size_t)hi->k);
        uint32_t h = fnv1a(key, hi->k) & (uint32_t)(hi->cap - 1);
        const Slot *found = NULL;
        for (int probe = 0; probe < hi->cap; probe++) {
            uint32_t i = (h + (uint32_t)probe) & (uint32_t)(hi->cap - 1);
            const Slot *s = &hi->slots[i];
            cost->tries++; /* one probe step (linear-probing collision cost) */
            if (!s->used) break;             /* miss: this k-prefix is dead */
            if (memcmp(s->key, key, (size_t)hi->k) == 0) { found = s; break; }
        }
        if (found) {
            /* `group` is ascending by construction (branches enumerated in
             * index order), so the first success here IS this group's own
             * minimum index -- exactly the ascending-scan-stop-at-first
             * shape (a), (b) and the trie walk all share. */
            for (int g = 0; g < found->gn; g++) {
                cost->tries++;
                int j = found->group[g];
                const Branch *b = &bs->br[j];
                if (branch_matches_full(b, subj, slen, pos, &cost->verify_bytes, hi->k)) {
                    if (best < 0 || j < best) { best = j; best_len = b->len; }
                    break;
                }
            }
        }
    }

    Answer a = { false, -1, 0 };
    if (best >= 0) { a.hit = true; a.index = best; a.match_len = best_len; }
    return a;
}
