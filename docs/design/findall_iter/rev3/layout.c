/* docs/design/findall_iter/rev3/layout.c -- findall_iter.md revision 3, §1.1's measured sentence.
 * sizeof(rx_iter) at revision 2's layout, at revision 3's I1 layout (no owner, the batch
 * setter's fields, no st) and at I2 (+ st with S = 64); and the BOUND fast path's code.
 * Build into the worktree's build/, never /tmp:
 *   gcc -O2 -Wall -Wextra -o build/layout layout.c && build/layout
 *   gcc -O2 -fPIC -S -o - layout.c | sed -n '/^fast:/,/ret/p'
 * rx_var is a stand-in with the shipped field count; only its pointer is stored. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
typedef struct { const char *name; const unsigned char *p; size_t len; } rx_var;
/* rev 2 as written */
typedef struct { uint32_t hdr; int32_t rc; uint32_t flags; int32_t rc_next;
  const unsigned char *s; size_t n; size_t lo; const void *owner;
  const rx_var *vars; size_t nvars; const void *bufs; size_t bhead, bcount;
  union { unsigned char b[64]; uint64_t a; } st; } rev2;
/* rev 3 at I1: no owner, batch setter fields, no st (S deferred to I2) */
typedef struct rx_iter { uint32_t hdr; int32_t rc; uint32_t flags; int32_t rc_next;
  const unsigned char *s; size_t n; size_t lo;
  const rx_var *vars; size_t nvars; const void *bufs;
  ptrdiff_t (*batch)[2]; size_t nbatch; size_t bhead, bcount; } rx_iter;
/* rev 3 at I2: + st, S = 64 */
typedef struct { rx_iter fixed; union { unsigned char b[64]; uint64_t a; } st; } rev3_i2;
#define PCREC_ITER_BOUND 0x49540202u
#define PCREC_ITER_FRESH 0x49540201u
#define PCREC_ITER_ENDED 0x49540203u
#define PCREC_ITER_OPT_BATCH 0x80u
static inline rx_iter rx_iter_init(const unsigned char *s, size_t n)
{ rx_iter it; it.hdr = PCREC_ITER_FRESH; it.s = s; it.n = n; return it; }
static inline void rx_iter_batch(rx_iter *it, ptrdiff_t (*b)[2], size_t npairs)
{ if ((it->hdr & ~0xF0u) == PCREC_ITER_FRESH) { it->batch = b; it->nbatch = npairs; it->hdr |= PCREC_ITER_OPT_BATCH; }
  else if (it->hdr != PCREC_ITER_ENDED) it->hdr = 0; }
int enter(rx_iter *);
int fast(rx_iter *it) { if (__builtin_expect(it->hdr != PCREC_ITER_BOUND, 0)) return enter(it); return (int)it->lo; }
int use(const unsigned char *s, size_t n) { ptrdiff_t b[64][2]; rx_iter it = rx_iter_init(s, n); rx_iter_batch(&it, b, 64); return fast(&it); }
int main(void){ printf("rev2 %zu rev3-I1 %zu rev3-I2 %zu\n", sizeof(rev2), sizeof(rx_iter), sizeof(rev3_i2)); return 0; }
int enter(rx_iter *it){ return (int)it->n; }
