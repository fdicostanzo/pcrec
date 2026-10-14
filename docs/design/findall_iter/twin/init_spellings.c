/* docs/design/findall_iter/twin/init_spellings.c — lane iterdes, [FINDALL-NEXT].
 * CODEGEN probe (no timing): how many stores does each spelling of iterator
 * initialization cost at the caller, for an rx_iter whose state buffer is S
 * bytes? D165 item 5: "init writes one validity word, never a memset of S".
 * Build: gcc -O2 -S -Wall -Wextra -Werror init_spellings.c; read the stores
 * into the iterator before each call to use(). */
#include <stddef.h>
#include <stdint.h>
#define PCREC_ITER_STATE_SIZE 56
#define PCREC_ITER_FRESH 0x49540000u
typedef struct rx_iter {
    uint32_t hdr; int32_t rc; uint32_t flags; uint32_t pad_;
    size_t lo; const unsigned char *s; size_t n; const void *owner;
    const void *vars; size_t nvars;
    union { unsigned char b[PCREC_ITER_STATE_SIZE]; uint64_t a_; } st;
} rx_iter;
extern void use(rx_iter *);

/* I1: the aggregate initializer (C zero-fills every omitted member) */
#define RX_ITER_INIT_AGG { .hdr = PCREC_ITER_FRESH }   /* designated: an unnamed `{ X }` trips -Wmissing-field-initializers under -Wextra */
void i1(void) { rx_iter it = RX_ITER_INIT_AGG; use(&it); }

/* I2: a statement that writes the header word only */
#define RX_ITER_START(itp) ((itp)->hdr = PCREC_ITER_FRESH)
void i2(void) { rx_iter it; RX_ITER_START(&it); use(&it); }

/* I3: an initializer EXPRESSION from a static inline that sets hdr only */
static inline rx_iter rx_iter_fresh(void) { rx_iter it; it.hdr = PCREC_ITER_FRESH; return it; }
void i3(void) { rx_iter it = rx_iter_fresh(); use(&it); }

/* I4: re-initialization of an EXISTING iterator by assignment from I3's expression */
void i4(rx_iter *it) { *it = rx_iter_fresh(); use(it); }
/* I5: start at a caller position (two words: hdr + lo) */
#define PCREC_ITER_FRESH_AT 0x49540001u
static inline rx_iter rx_iter_fresh_at(size_t pos) { rx_iter it; it.hdr = PCREC_ITER_FRESH_AT; it.lo = pos; return it; }
void i5(size_t p) { rx_iter it = rx_iter_fresh_at(p); use(&it); }
