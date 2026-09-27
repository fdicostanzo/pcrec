/* src/facts/facts.c — THE PATTERN-FACTS RECORD: the memo, the epoch guard,
 * the deny, and each accessor's call into its owner's derivation
 * ([PATFACTS], D120/D126; docs/design/patfacts/design.md §2, §7).
 *
 * EVERY ACCESSOR IS THE SAME FOUR STEPS (design §2), and `pf_enter` is them
 * minus the derivation, so no accessor can skip one:
 *   1. EPOCH GUARD — asked before its seal is an internal-error refusal. That
 *      turns step 1's implicit "only after `pcrec_lower_enc`" contract into a
 *      checked one.
 *   2. MEMO — a cached fact is a bit test.
 *   3. DENY — a fact deny stores the fact's EMPTY VALUE without deriving, and
 *      records which flag did it. A denied build is indistinguishable from a
 *      pattern with nothing to find, for every consumer at once: that is
 *      `src/opt/possessify.c`'s no-trace rule, which `compile_driver` applied
 *      inline before this file existed, now in one place (design §7.1).
 *   4. DERIVE — the owner's derivation, once.
 *
 * `used` is set by the PUBLIC accessors only: a pass asking. A derived fact's
 * own derivation reads its core facts through `pf_*` helpers that do not set
 * it, so `--emit-facts`' `used` column says which facts a PASS consumed
 * (design §11.4), not which ones fed another fact.
 *
 * The necessary SET and WHOLE RUN are core facts from ONE walk
 * (`src/facts/req.c`); asking either derives both, each under its own deny.
 * The WINDOW and the BYTE are derived facts, speed choices over them
 * (`src/opt/reqbyte.c`), reading their core facts through `pf_ask`, which is
 * the one path along the DEPENDS-ON edges `facts.def` declares. */

#include <string.h>

#include "core/internal.h"
#include "enc/enc.h"
#include "facts/facts_derive.h"

/* The table's deny, epoch and name columns, indexed by `PfFactId`. */
static const uint64_t pf_deny[PF_NFACTS] = {
#define PF_FACT(ID, name, epoch, kind, deny, owner, depends) \
    [PF_##ID] = (uint64_t)(deny),
#include "facts/facts.def"
};
static const unsigned char pf_epoch[PF_NFACTS] = {
#define PF_FACT(ID, name, epoch, kind, deny, owner, depends) [PF_##ID] = (epoch),
#include "facts/facts.def"
};
static const char *const pf_name[PF_NFACTS] = {
#define PF_FACT(ID, name, epoch, kind, deny, owner, depends) [PF_##ID] = name,
#include "facts/facts.def"
};

static uint32_t pf_bit(PfFactId f) { return (uint32_t)1 << f; }

/* Stores fact `f`'s EMPTY VALUE — the answer for a pattern with nothing to
 * find, which every consumer already handles because real patterns produce
 * it. The switch has no `default:` so a new row is a compile error here. */
static void pf_store_empty(PatFacts *pf, PfFactId f)
{
    switch (f) {
    case PF_START_ANCHOR: pf->start_anchor = PCREC_SANCH_NONE; break;
    case PF_END_WINDOW:   pf->end_window = -1; break;
    case PF_REQ_SET:
        memset(pf->req_set.bits, 0, sizeof pf->req_set.bits);
        pf->req_set.rightmost = -1;
        break;
    case PF_REQ_WHOLE_RUN:
        memset(pf->req_run.whole, 0, sizeof pf->req_run.whole);
        pf->req_run.whole_len = 0;
        break;
    case PF_REQ_RUN:
        memset(pf->req_run.bytes, 0, sizeof pf->req_run.bytes);
        pf->req_run.len = 0;
        pf->req_run.idx = 0;
        pf->req_run.at = 0;
        break;
    case PF_REQ_BYTE:     pf->req_byte = -1; break;
    case PF_NFACTS:       break;
    }
}

/* Steps 1-3. Returns true when the caller must DERIVE `f` (step 4): it is
 * sealed, uncached and not denied. `pass` is true on a public accessor. A
 * denied fact is cached with its empty value and the LOWEST denying bit, so
 * `-fno-req-byte -fno-req-run` names the byte flag on the whole run, the
 * order `--list-axes` prints a two-bit deny in. */
static bool pf_enter(Ctx *cx, PfFactId f, bool pass)
{
    PatFacts *pf = &cx->job->pf;
    uint64_t d;
    if (pass) pf->used |= pf_bit(f);
    if ((int)pf->epoch < (int)pf_epoch[f])
        pcrec_ctx_fail(cx, 0, "internal error: pattern fact '%s' asked before "
                       "its epoch (E%d) was sealed", pf_name[f], pf_epoch[f]);
    if (pf->have & pf_bit(f)) return false;
    d = cx->opt->flags & pf_deny[f];
    if (d) {
        pf->have |= pf_bit(f);
        pf_store_empty(pf, f);
        pf->why[f] = (PfWhy){ PF_ST_DENIED, PF_WHY_DENY, d & (~d + 1) };
        return false;
    }
    return true;
}

/* Marks `f` derived: cached, with a plain `why`. */
static void pf_done(PatFacts *pf, PfFactId f)
{
    pf->have |= pf_bit(f);
    pf->why[f] = (PfWhy){ PF_ST_DERIVED, PF_WHY_NONE, 0 };
}

/* Marks `f` derived with the reason its derivation REPORTED — a structural
 * decline (status `declined`) or the rate rule a pick answered by (status
 * `derived`). The reason is stored when the value is, never reconstructed
 * from the value afterwards (design §11.3 item 3). */
static void pf_done_why(PatFacts *pf, PfFactId f, PfWhyCode code)
{
    bool decl = code == PF_WHY_ENC_MULTIBYTE || code == PF_WHY_NOT_END_ANCHORED ||
                code == PF_WHY_GSTART || code == PF_WHY_UNBOUNDED;
    pf->have |= pf_bit(f);
    pf->why[f] = (PfWhy){ decl ? PF_ST_DECLINED : PF_ST_DERIVED,
                          (unsigned char)code, 0 };
}

static void pf_ask(Ctx *cx, PfFactId f, bool pass);

/* The two CORE necessary-byte facts from their one walk. Each is stored only
 * if it is still unasked and not denied (`pf_enter` caches a denied one), so
 * the walk runs once per attempt whichever of the two is asked first. A run
 * shorter than two bytes is not a run fact: that is `[OPT-REQBYTE]`'s `L = 1`
 * case, carried by the set. */
static void pf_derive_req_walk(Ctx *cx)
{
    PatFacts *pf = &cx->job->pf;
    RbSet set;
    RbRun run;
    pcrec_req_walk(pf->root, &set, &run);
    if (pf_enter(cx, PF_REQ_SET, false)) {
        memcpy(pf->req_set.bits, set.bits, sizeof set.bits);
        pf->req_set.rightmost = set.pick;
        pf_done(pf, PF_REQ_SET);
    }
    if (pf_enter(cx, PF_REQ_WHOLE_RUN, false)) {
        memset(pf->req_run.whole, 0, sizeof pf->req_run.whole);
        pf->req_run.whole_len = 0;
        if (run.n >= 2) {
            memcpy(pf->req_run.whole, run.bytes, (size_t)run.n);
            pf->req_run.whole_len = run.n;
        }
        pf_done(pf, PF_REQ_WHOLE_RUN);
    }
}

/* Step 4: fact `f`'s derivation, reading other facts only through `pf_ask`
 * along the DEPENDS-ON edges `facts.def` declares. No `default:`, so a new
 * row is a compile error here. */
static void pf_derive(Ctx *cx, PfFactId f)
{
    PatFacts *pf = &cx->job->pf;
    PfWhyCode why = PF_WHY_NONE;
    switch (f) {
    case PF_START_ANCHOR:
        pf->start_anchor = pcrec_start_anchor(pf->root);
        break;
    case PF_END_WINDOW:
        /* The descriptor is resolved HERE, once, and handed in: the
         * derivation's one encoding input is declared, never looked up
         * (design §4.2.2 carve-out (d)). */
        pf->end_window = pcrec_end_window(pcrec_enc_by_id(cx->opt->encoding),
                                          pf->root, &why);
        break;
    case PF_REQ_SET:
    case PF_REQ_WHOLE_RUN:
        pf_derive_req_walk(cx);
        return;
    case PF_REQ_RUN:
        pf_ask(cx, PF_REQ_WHOLE_RUN, false);
        pcrec_req_window(cx, &pf->req_run, &why);
        break;
    case PF_REQ_BYTE:
        pf_ask(cx, PF_REQ_SET, false);
        pf_ask(cx, PF_REQ_RUN, false);
        pf->req_byte = pcrec_req_pick(cx, &pf->req_set, &pf->req_run, &why);
        break;
    case PF_NFACTS:
        return;
    }
    pf_done_why(pf, f, why);
}

/* The four steps: `pf_enter`'s three, then the derivation. */
static void pf_ask(Ctx *cx, PfFactId f, bool pass)
{
    if (pf_enter(cx, f, pass)) pf_derive(cx, f);
}

void pcrec_facts_seal_e2(Ctx *cx, const struct Ast *root)
{
    cx->job->pf.root = root;
    cx->job->pf.epoch = PF_E2_LOWERED;
}

int pcrec_fact_start_anchor(Ctx *cx)
{
    pf_ask(cx, PF_START_ANCHOR, true);
    return cx->job->pf.start_anchor;
}

long long pcrec_fact_end_window(Ctx *cx)
{
    pf_ask(cx, PF_END_WINDOW, true);
    return cx->job->pf.end_window;
}

const ReqSet *pcrec_fact_req_set(Ctx *cx)
{
    pf_ask(cx, PF_REQ_SET, true);
    return &cx->job->pf.req_set;
}

const ReqRun *pcrec_fact_req_whole_run(Ctx *cx)
{
    pf_ask(cx, PF_REQ_WHOLE_RUN, true);
    return &cx->job->pf.req_run;
}

const ReqRun *pcrec_fact_req_run(Ctx *cx)
{
    pf_ask(cx, PF_REQ_RUN, true);
    return &cx->job->pf.req_run;
}

int pcrec_fact_req_byte(Ctx *cx)
{
    pf_ask(cx, PF_REQ_BYTE, true);
    return cx->job->pf.req_byte;
}

void pcrec_facts_force_all(Ctx *cx)
{
    PatFacts *pf = &cx->job->pf;
    pf->forcing = true;
    for (; pf->force_next < PF_NFACTS; pf->force_next++) {
        PfFactId f = (PfFactId)pf->force_next;
        /* Never past a seal this route did not write: an unsealed epoch is
         * a DECLINE of the route, not a failure, and forcing it would build a
         * machine the compile never built (design §3, §11.4). Every fact is
         * E2 today and every successful compile seals E2, so no row takes
         * this arm yet; E1/E3 facts arrive with steps 3.2/3.4. */
        if ((int)pf->epoch < (int)pf_epoch[f]) continue;
        pf_ask(cx, f, false);
    }
    pf->forcing = false;
}

void pcrec_facts_force_failed(Ctx *cx)
{
    PatFacts *pf = &cx->job->pf;
    if (pf->force_next < PF_NFACTS) {
        PfFactId f = (PfFactId)pf->force_next;
        pf->have |= pf_bit(f);
        pf->why[f] = (PfWhy){ PF_ST_ABSENT, PF_WHY_FORCE_FAILED, 0 };
        pf->force_next++;
    }
}

/* `n` bytes as lowercase hex, then `@idx` when `idx >= 0`: the `REQ_RUN`
 * spelling (hex because a run is arbitrary bytes inside a `#define`'s string
 * body — one spelling for all 256 values), arena text. */
static const char *pf_hex(Ctx *cx, const unsigned char *b, int n, int idx)
{
    StrBuf sb = { 0 };
    const char *t;
    sb.cx = cx;
    for (int k = 0; k < n; k++) pcrec_sb_printf(&sb, "%02x", b[k]);
    if (idx >= 0) pcrec_sb_printf(&sb, "@%d", idx);
    t = pcrec_sb_fragf(&cx->arena, "%s", sb.p ? sb.p : "");
    pcrec_sb_free(&sb);
    return t;
}

/* Fact `f`'s ONE renderer. Every fact with no answer to give renders
 * `"none"` — the stamps' own member for "declined", because 0 is a legal
 * byte and a legal window and no number is free to mean it. The switch has
 * no `default:`, so a `facts.def` row with no renderer does not compile. */
const char *pcrec_fact_render(Ctx *cx, PfFactId f)
{
    const PatFacts *pf = &cx->job->pf;
    switch (f) {
    case PF_START_ANCHOR:
        return pcrec_start_anchor_name(pf->start_anchor);
    case PF_END_WINDOW:
        if (pf->end_window < 0) return "none";
        return pcrec_sb_fragf(&cx->arena, "%lld", pf->end_window);
    case PF_REQ_SET: {
        StrBuf sb = { 0 };
        const char *t;
        int n = 0;
        sb.cx = cx;
        for (int b = 0; b < 256; b++)
            if ((pf->req_set.bits[b >> 3] >> (b & 7)) & 1)
                pcrec_sb_printf(&sb, "%s%d", n++ ? "," : "", b);
        t = n ? pcrec_sb_fragf(&cx->arena, "%s", sb.p) : "none";
        pcrec_sb_free(&sb);
        return t;
    }
    case PF_REQ_WHOLE_RUN:
        if (pf->req_run.whole_len < 2) return "none";
        return pf_hex(cx, pf->req_run.whole, pf->req_run.whole_len, -1);
    case PF_REQ_RUN:
        if (pf->req_run.len < 2) return "none";
        return pf_hex(cx, pf->req_run.bytes, pf->req_run.len, pf->req_run.idx);
    case PF_REQ_BYTE:
        if (pf->req_byte < 0) return "none";
        return pcrec_sb_fragf(&cx->arena, "%d", pf->req_byte);
    case PF_NFACTS:
        break;
    }
    return "";
}

const char *pcrec_fact_stamp(Ctx *cx, PfFactId f)
{
    pf_ask(cx, f, true);
    return pcrec_fact_render(cx, f);
}
