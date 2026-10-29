/* tests/callouts/stubs.c — the callout BINDINGS every callouts driver links
 * ([INLINE-C] stage 1b; docs/spec/match_api.md §11.2).
 *
 * Linked through this directory's `harness.manifest` by
 * tests/harness/run.sh, and by run_callouts_tests.sh's own drivers. It is
 * compiled with `-include` of an artifact header, which supplies the shared
 * ABI block (`rx_ctx`, `rx_callout_ref`): no copy of the ABI lives here.
 *
 * Every binding is a row of behaviors.h: `rx_callout_<name>` for each named
 * row, and `rx_callout_<n>` (n = 0..255) binding check row `n % CO_NCHECK`.
 *
 * THE FIRE LOG. Each fire appends (binding id, attempt start) to `co_log`,
 * which a driver resets before a call and reads after it: the firing-class
 * bound (match_api.md §11.8) is checked against it, never a fire COUNT
 * (§11.6 leaves those unspecified). A binding's id is its number for a
 * numbered one and 256 + its row for a named one. */
#include "behaviors.h"

#define CO_LOG_MAX 65536
int co_log_n;
int co_log_id[CO_LOG_MAX];
ptrdiff_t co_log_start[CO_LOG_MAX];

static ptrdiff_t co_fire(int id, int row, const rx_ctx *c)
{
    if (co_log_n < CO_LOG_MAX) {
        co_log_id[co_log_n] = id;
        co_log_start[co_log_n] = c->caps ? c->caps[0][0] : -1;
        co_log_n++;
    }
    const CoView v = { c->subject, c->len, c->pos, c->ncap, c->caps };
    return co_rows[row].fn(&v);
}

#define CO_NAMED(NAME, ROW)                                                   \
    static ptrdiff_t co_named_##NAME(const rx_ctx *c)                         \
    { return co_fire(256 + (ROW), (ROW), c); }                                \
    const rx_callout_ref rx_callout_##NAME = { co_named_##NAME, NULL };

CO_NAMED(pass, 0)
CO_NAMED(veto, 1)
CO_NAMED(odd, 2)
CO_NAMED(even, 3)
CO_NAMED(vetostart, 4)
CO_NAMED(g1set, 5)
CO_NAMED(g1even, 6)
CO_NAMED(aftera, 7)
CO_NAMED(atend, 8)
CO_NAMED(notb, 9)
CO_NAMED(notone, 10)
CO_NAMED(le255, 11)
CO_NAMED(g1ab, 12)
CO_NAMED(two, 13)
CO_NAMED(digits, 14)
CO_NAMED(onea, 15)

#define CO_NUM(N)                                                             \
    static ptrdiff_t co_num_##N(const rx_ctx *c)                              \
    { return co_fire((N), (N) % CO_NCHECK, c); }                              \
    const rx_callout_ref rx_callout_##N = { co_num_##N, NULL };
#define CO_NUM10(D) CO_NUM(D##0) CO_NUM(D##1) CO_NUM(D##2) CO_NUM(D##3)     \
    CO_NUM(D##4) CO_NUM(D##5) CO_NUM(D##6) CO_NUM(D##7) CO_NUM(D##8) CO_NUM(D##9)

CO_NUM(0) CO_NUM(1) CO_NUM(2) CO_NUM(3) CO_NUM(4)
CO_NUM(5) CO_NUM(6) CO_NUM(7) CO_NUM(8) CO_NUM(9)
CO_NUM10(1) CO_NUM10(2) CO_NUM10(3) CO_NUM10(4) CO_NUM10(5)
CO_NUM10(6) CO_NUM10(7) CO_NUM10(8) CO_NUM10(9)
CO_NUM10(10) CO_NUM10(11) CO_NUM10(12) CO_NUM10(13) CO_NUM10(14)
CO_NUM10(15) CO_NUM10(16) CO_NUM10(17) CO_NUM10(18) CO_NUM10(19)
CO_NUM10(20) CO_NUM10(21) CO_NUM10(22) CO_NUM10(23) CO_NUM10(24)
CO_NUM(250) CO_NUM(251) CO_NUM(252) CO_NUM(253) CO_NUM(254) CO_NUM(255)
