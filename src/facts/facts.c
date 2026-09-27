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
 * The necessary set, whole run, window and byte come off ONE derivation call
 * today, `pcrec_req_byte` — one walk and one pick, which is how
 * `compile_driver` computed them. `pf_derive_req` fills all four at once,
 * each under its own deny; the walk/pick split (core in `req.c`, derived in
 * `reqbyte.c`) is a later relocation. */

#include <string.h>

#include "core/internal.h"
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
    case PF_REQ_SET:      memset(&pf->req_set, 0, sizeof pf->req_set); break;
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
        pf->why[f] = (PfWhy){ PF_DENIED, PF_WHY_DENY, d & (~d + 1) };
        return false;
    }
    return true;
}

/* Marks `f` derived: cached, with a plain `why`. */
static void pf_done(PatFacts *pf, PfFactId f)
{
    pf->have |= pf_bit(f);
    pf->why[f] = (PfWhy){ PF_DERIVED, PF_WHY_NONE, 0 };
}

/* The four necessary-byte facts from their one derivation call. Each is
 * stored only if it is still unasked and not denied (`pf_enter` has cached a
 * denied one already), so the answers are exactly `compile_driver`'s were:
 * `run_ok` is `-fno-req-run`'s complement, and under `-fno-req-byte` every
 * one of the four is denied before this is reached. */
static void pf_derive_req(Ctx *cx)
{
    PatFacts *pf = &cx->job->pf;
    ReqRun run;
    ReqSet set;
    int byte = pcrec_req_byte(cx, pf->root, !(cx->opt->flags & PCREC_NO_REQ_RUN),
                              &run, &set);
    if (pf_enter(cx, PF_REQ_SET, false)) {
        pf->req_set = set;
        pf_done(pf, PF_REQ_SET);
    }
    if (pf_enter(cx, PF_REQ_WHOLE_RUN, false)) {
        memcpy(pf->req_run.whole, run.whole, sizeof run.whole);
        pf->req_run.whole_len = run.whole_len;
        pf_done(pf, PF_REQ_WHOLE_RUN);
    }
    if (pf_enter(cx, PF_REQ_RUN, false)) {
        memcpy(pf->req_run.bytes, run.bytes, sizeof run.bytes);
        pf->req_run.len = run.len;
        pf->req_run.idx = run.idx;
        pf->req_run.at = run.at;
        pf_done(pf, PF_REQ_RUN);
    }
    if (pf_enter(cx, PF_REQ_BYTE, false)) {
        pf->req_byte = byte;
        pf_done(pf, PF_REQ_BYTE);
    }
}

void pcrec_facts_seal_e2(Ctx *cx, const struct Ast *root)
{
    cx->job->pf.root = root;
    cx->job->pf.epoch = PF_E2_LOWERED;
}

int pcrec_fact_start_anchor(Ctx *cx)
{
    PatFacts *pf = &cx->job->pf;
    if (pf_enter(cx, PF_START_ANCHOR, true)) {
        pf->start_anchor = pcrec_start_anchor(pf->root);
        pf_done(pf, PF_START_ANCHOR);
    }
    return pf->start_anchor;
}

long long pcrec_fact_end_window(Ctx *cx)
{
    PatFacts *pf = &cx->job->pf;
    if (pf_enter(cx, PF_END_WINDOW, true)) {
        pf->end_window = pcrec_end_window(cx, pf->root);
        pf_done(pf, PF_END_WINDOW);
    }
    return pf->end_window;
}

const ReqSet *pcrec_fact_req_set(Ctx *cx)
{
    if (pf_enter(cx, PF_REQ_SET, true)) pf_derive_req(cx);
    return &cx->job->pf.req_set;
}

const ReqRun *pcrec_fact_req_whole_run(Ctx *cx)
{
    if (pf_enter(cx, PF_REQ_WHOLE_RUN, true)) pf_derive_req(cx);
    return &cx->job->pf.req_run;
}

const ReqRun *pcrec_fact_req_run(Ctx *cx)
{
    if (pf_enter(cx, PF_REQ_RUN, true)) pf_derive_req(cx);
    return &cx->job->pf.req_run;
}

int pcrec_fact_req_byte(Ctx *cx)
{
    if (pf_enter(cx, PF_REQ_BYTE, true)) pf_derive_req(cx);
    return cx->job->pf.req_byte;
}
