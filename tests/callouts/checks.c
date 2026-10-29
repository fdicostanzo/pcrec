/* tests/callouts/checks.c — the callout checks a `.rxt` cell cannot express
 * ([INLINE-C] stage 1b; docs/spec/match_api.md §11). Built and run by
 * run_callouts_tests.sh, which compiles each artifact named below under its
 * prefix and links this file with stubs.c.
 *
 * Each check prints `PASS: ...` or `FAIL: ...`; the exit status is the
 * failure count. `checks trap NAME` runs ONE case that must trap (the runner
 * expects death by a signal) and returns 0 only if it did not. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "va.h"
#include "vb.h"
#include "vk.h"
#include "vn.h"
#include "vc.h"
#include "ve.h"
#include "gs.h"
#include "gf.h"
#include "sc.h"
#include "dt.h"
#include "in1.h"
#include "ou.h"
#include "tf.h"
#include "tu.h"
#include "tp.h"

static int fails;
#define CHECK(cond, ...)                                                      \
    do {                                                                      \
        if (cond) { printf("PASS: "); printf(__VA_ARGS__); putchar('\n'); }   \
        else { printf("FAIL: "); printf(__VA_ARGS__); putchar('\n'); fails++; } \
    } while (0)

/* ---- recording bindings: `see` and `see1` keep every fire's view -------- */
#define SEE_MAX 64
typedef struct { size_t pos, ncap; ptrdiff_t c[4][2]; } Seen;
static Seen seen[SEE_MAX];
static int nseen;

static ptrdiff_t see_fn(const rx_ctx *c)
{
    if (nseen < SEE_MAX) {
        Seen *s = &seen[nseen++];
        s->pos = c->pos;
        s->ncap = c->ncap;
        for (size_t g = 0; g < 4; g++)
            s->c[g][0] = s->c[g][1] = -9;
        for (size_t g = 0; g < c->ncap && g < 4; g++) {
            s->c[g][0] = c->caps[g][0];
            s->c[g][1] = c->caps[g][1];
        }
    }
    return 0;
}
const rx_callout_ref rx_callout_see = { see_fn, NULL };
const rx_callout_ref rx_callout_see1 = { see_fn, NULL };

static const Seen *seen_at(size_t pos)
{
    for (int i = 0; i < nseen; i++)
        if (seen[i].pos == pos) return &seen[i];
    return NULL;
}

/* ---- give-up, counting, artifact-as-callee and trap bindings ------------ */
static ptrdiff_t steps_fn(const rx_ctx *c) { (void)c; return PCREC_ERR_STEPS; }
static ptrdiff_t frames_fn(const rx_ctx *c) { (void)c; return PCREC_ERR_FRAMES; }
const rx_callout_ref rx_callout_steps = { steps_fn, NULL };
const rx_callout_ref rx_callout_frames = { frames_fn, NULL };

static int tier_escalations;
void gf_tier_escalated(void) { tier_escalations++; }

static int count_n;
static ptrdiff_t count_fn(const rx_ctx *c) { (void)c; count_n++; return 0; }
const rx_callout_ref rx_callout_count = { count_fn, NULL };

const rx_callout_ref rx_callout_octet = { in1_match, NULL };

static ptrdiff_t far_fn(const rx_ctx *c) { return (ptrdiff_t)(c->len - c->pos) + 5; }
static ptrdiff_t one_fn(const rx_ctx *c) { (void)c; return 1; }
const rx_callout_ref rx_callout_far = { far_fn, NULL };
const rx_callout_ref rx_callout_one = { one_fn, NULL };

#define U(s) (const unsigned char *)(s), strlen(s)

int main(int argc, char **argv)
{
    ptrdiff_t caps[4][2];
    int r;

    if (argc == 3 && !strcmp(argv[1], "trap")) {
        if (!strcmp(argv[2], "overlong"))
            r = tf_search(U("ab"), 0, caps);
        else if (!strcmp(argv[2], "midchar"))
            r = tu_search(U("\xc3\xa9"), 0, caps);
        else if (!strcmp(argv[2], "pred1"))
            r = tp_search(U("ab"), 0, caps);
        else
            return 2;
        printf("no trap: %s returned %d\n", argv[2], r);
        return 1;
    }

    /* A2: the view shows every group; a group's last closed value. */
    nseen = 0;
    r = va_search(U("aa"), 0, caps);
    const Seen *s = seen_at(1);
    CHECK(r == 1 && caps[0][0] == 0 && caps[0][1] == 2,
          "A2 (?:(?C\"see\")(a))+ on aa matches [0,2)");
    CHECK(s && s->ncap == 2 && s->c[1][0] == 0 && s->c[1][1] == 1,
          "A2 the second fire sees group 1 = [0,1) from the first iteration");
    s = seen_at(0);
    CHECK(s && s->c[0][0] == 0 && s->c[1][0] == -1,
          "A2 the first fire sees RX_START 0 and group 1 unset");

    nseen = 0;
    r = vb_search(U("ab"), 0, caps);
    s = seen_at(1);
    CHECK(r == 1 && s && s->ncap == 3 && s->c[1][0] == 0 && s->c[1][1] == 1 &&
          s->c[2][0] == -1,
          "A2 (?:(?C\"see\")(a)|(b))+ on ab: the second fire sees g1 [0,1), g2 unset, ncap 3");

    /* A4: \K moves the reported start, never the callee's RX_START. */
    nseen = 0;
    r = vk_search(U("abc"), 0, caps);
    s = seen_at(2);
    CHECK(r == 1 && caps[0][0] == 1 && caps[0][1] == 3,
          "A4 a\\Kb(?C\"see\")c on abc reports [1,3)");
    CHECK(s && s->c[0][0] == 0, "A4 the callee's RX_START is the attempt start 0");

    /* A5: --no-captures keeps every group the site reads. */
    r = vn_search(U("ab"), 0, caps);
    CHECK(r == 1 && caps[0][0] == 0 && caps[0][1] == 2 && VN_NCAPS == 1,
          "A5 (a)b(?C\"g1set\") under --no-captures matches ab (NCAPS 1)");
    nseen = 0;
    r = vc_search(U("ab"), 0, caps);
    s = seen_at(2);
    CHECK(r == 1 && s && s->ncap == 2 && s->c[1][0] == 0 && s->c[1][1] == 1,
          "A5 under --no-captures the site still sees ncap 2 and group 1 [0,1)");

    /* An enclosing group: the second iteration's site sees the first. */
    nseen = 0;
    r = ve_search(U("abab"), 0, caps);
    s = seen_at(3);
    CHECK(r == 1 && caps[0][1] == 4 && s && s->c[1][0] == 0 && s->c[1][1] == 2,
          "(a(?C\"see1\")b)+ on abab: the second fire sees group 1 [0,2)");

    /* Give-ups propagate (D8). */
    r = gs_search(U("aab"), 0, caps);
    CHECK(r == PCREC_ERR_STEPS, "a binding's PCREC_ERR_STEPS propagates (got %d)", r);
    tier_escalations = 0;
    r = gf_search(U("aab"), 0, caps);
    CHECK(r == PCREC_ERR_FRAMES && tier_escalations == 0,
          "a binding's PCREC_ERR_FRAMES propagates without escalating the tier "
          "(got %d, %d escalations)", r, tier_escalations);

    /* Each fire is charged one step (match_api.md §4¶1). */
    r = sc_search(U("aaaaaaaaaaaaaaaaaaaa"), 0, caps);
    CHECK(r == PCREC_ERR_STEPS,
          "an always-vetoing site under --step-budget=5 gives up STEPS (got %d)", r);

    /* DT-4.1: a counter is told fires happen, never how many. */
    count_n = 0;
    r = dt_search(U("12y"), 0, caps);
    CHECK(r == 1 && caps[0][0] == 0 && caps[0][1] == 3 && count_n >= 1,
          "DT-4.1 (\\d+)(?C\"count\")x|(\\d+)y on 12y matches [0,3), count >= 1");

    /* §6: an artifact bound as a consuming callout. */
    r = ou_search(U("x12y"), 0, caps);
    CHECK(r == 1 && caps[0][0] == 0 && caps[0][1] == 4,
          "x(?C\"octet,consume\")y with octet = in1_match matches x12y");
    r = ou_search(U("x1y"), 0, caps);
    CHECK(r == 0, "x(?C\"octet,consume\")y does not match x1y");

    printf("checks: %d failed\n", fails);
    return fails;
}
