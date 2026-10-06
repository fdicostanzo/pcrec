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
 * The two E1 facts (the kind mask, nullability) are the exception to "on
 * first ask": `pcrec_facts_seal_e1` FORCES them on the structural tree, and
 * `pcrec_facts_seal_e2` re-derives them on the lowered one as the invariance
 * cross-check (design §2-§3). After the seal their accessors are memo reads.
 *
 * The necessary SET and WHOLE RUN are core facts from ONE walk
 * (`src/facts/req.c`); asking either derives both, each under its own deny.
 * The WINDOW and the BYTE are derived facts, speed choices over them
 * (`src/facts/req.c`, through the rate readers in `src/core/findings.c`),
 * reading their core facts through `pf_ask`, which is
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
    case PF_KINDS:        pf->kinds = 0; break;
    case PF_NULLABLE:     pf->nullable = false; break;
    case PF_START_ANCHOR: pf->start_anchor = PCREC_SANCH_NONE; break;
    case PF_START_SET:
        memset(pf->start_set.bits, 0xFF, sizeof pf->start_set.bits);
        pf->start_set.nullable = true;
        break;
    case PF_END_WINDOW:   pf->end_window = -1; break;
    case PF_REQ_SET:
        memset(pf->req_set.bits, 0, sizeof pf->req_set.bits);
        pf->req_set.rightmost = -1;
        break;
    case PF_REQ_WHOLE_RUN:
        memset(pf->req_run.whole, 0, sizeof pf->req_run.whole);
        memset(pf->req_run.whole_mask, 0, sizeof pf->req_run.whole_mask);
        pf->req_run.whole_len = 0;
        pf->req_run.whole_maxoff = 0;
        break;
    case PF_REQ_RUN:
        memset(pf->req_run.bytes, 0, sizeof pf->req_run.bytes);
        memset(pf->req_run.mask, 0, sizeof pf->req_run.mask);
        pf->req_run.len = 0;
        pf->req_run.idx = 0;
        pf->req_run.at = 0;
        pf->req_run.maxoff = 0;
        break;
    case PF_REQ_RUN_MAXOFF: pf->req_run.maxoff = 0; break;
    case PF_REQ_BYTE:     pf->req_byte = -1; break;
    case PF_KSET_WALK:    memset(&pf->kset_walk, 0, sizeof pf->kset_walk); break;
    case PF_RUN_PIN:      pf->run_pin = (RunPin){ false, 0, 0, 0, 0 }; break;
    case PF_NFACTS:       break;
    }
}

/* True where `f` is an E3 fact and this route sealed E2 but never E3: the
 * one epoch gap that is a route's DECLINE rather than an asker's error. */
static bool pf_route_unsealed(const PatFacts *pf, PfFactId f)
{
    return pf_epoch[f] == PF_E3_MACHINE && pf->epoch == PF_E2_LOWERED;
}

/* Steps 1-3. Returns true when the caller must DERIVE `f` (step 4): it is
 * sealed, uncached and not denied. An E3 fact on a route that never sealed
 * E3 is answered here, `absent`, and never derived. `pass` is true on a public accessor. A
 * denied fact is cached with its empty value and the LOWEST denying bit, so
 * `-fno-req-byte -fno-req-run` names the byte flag on the whole run, the
 * order `--list-axes` prints a two-bit deny in. */
static bool pf_enter(Ctx *cx, PfFactId f, bool pass)
{
    PatFacts *pf = &cx->job->pf;
    uint64_t d;
    if (pass) pf->used |= pf_bit(f);
    if (pf_route_unsealed(pf, f)) {
        /* E3 IS PER BRANCH (design §3, r1 A3): not an internal error but the
         * route's decline. A forward NFA that exists here was never wrapped
         * (`ENG_ATTEMPT`); none at all means no DFA scan was built. The
         * reason is the machine's state, stored with the empty value. */
        pf->have |= pf_bit(f);
        pf_store_empty(pf, f);
        pf->why[f] = (PfWhy){ PF_ST_ABSENT,
                              cx->job->nfa.n > 0 ? PF_WHY_ATTEMPT_UNWRAPPED
                                                 : PF_WHY_NO_FORWARD_NFA, 0 };
        return false;
    }
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
 * the walk runs once per attempt whichever of the two is asked first.
 *
 * THE RUN'S ADMISSION FLOOR IS IN BITS ([OPT-LITSCAN] S4 C3): a run ships
 * only where its information, `Σ popcount(K)`, reaches
 * `PCREC_MIN_REQ_RUN_BITS` (16). On an exact run that is "two bytes or more"
 * exactly, today's floor, and a shorter run is `[OPT-REQBYTE]`'s `L = 1`
 * case, carried by the set; three caseless letters (21) pass and two (14) do
 * not. A run that passes has at least two positions, so every reader's
 * `len >= 2` still means "a run shipped".
 *
 * `-fno-req-run-fold` IS READ HERE AND HANDED IN as the walk's position
 * bound (1, the single byte), so the walk reads no option and the deny
 * narrows the fact for every consumer at once (D126 Q3). */
static void pf_derive_req_walk(Ctx *cx)
{
    PatFacts *pf = &cx->job->pf;
    RbSet set;
    RbRun run;
    int bits = 0;
    pcrec_req_walk(cx, pf->root,
                   (cx->opt->flags & PCREC_NO_REQ_RUN_FOLD)
                       ? 1 : PCREC_MAX_REQ_RUN_POS_SET,
                   &set, &run);
    for (int i = 0; i < run.n; i++) bits += __builtin_popcount(run.mask[i]);
    if (pf_enter(cx, PF_REQ_SET, false)) {
        memcpy(pf->req_set.bits, set.bits, sizeof set.bits);
        pf->req_set.rightmost = set.pick;
        pf_done(pf, PF_REQ_SET);
    }
    if (pf_enter(cx, PF_REQ_WHOLE_RUN, false)) {
        memset(pf->req_run.whole, 0, sizeof pf->req_run.whole);
        memset(pf->req_run.whole_mask, 0, sizeof pf->req_run.whole_mask);
        pf->req_run.whole_len = 0;
        pf->req_run.whole_maxoff = 0;
        if (bits >= PCREC_MIN_REQ_RUN_BITS) {
            memcpy(pf->req_run.whole, run.bytes, (size_t)run.n);
            memcpy(pf->req_run.whole_mask, run.mask, (size_t)run.n);
            pf->req_run.whole_len = run.n;
            /* [K82] the walk's bound on where this run begins. */
            pf->req_run.whole_maxoff = run.off;
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
    case PF_KINDS:
        pf->kinds = pcrec_pattern_kinds(pf->root);
        break;
    case PF_NULLABLE:
        pf->nullable = pcrec_pattern_nullable(pf->root);
        break;
    case PF_START_ANCHOR:
        pf->start_anchor = pcrec_start_anchor(pf->root);
        break;
    case PF_START_SET:
        pcrec_start_set(cx, pf->root, &pf->start_set);
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
    case PF_REQ_RUN_MAXOFF:
        /* [K82] computed with the window it bounds (`pcrec_req_window`);
         * this row publishes it, declined where no static bound exists. */
        pf_ask(cx, PF_REQ_RUN, false);
        if (pf->req_run.len >= 2 && pf->req_run.maxoff >= PCREC_W_UNBOUNDED)
            why = PF_WHY_UNBOUNDED;
        break;
    case PF_REQ_BYTE:
        pf_ask(cx, PF_REQ_SET, false);
        pf_ask(cx, PF_REQ_RUN, false);
        pf->req_byte = pcrec_req_pick(cx, &pf->req_set, &pf->req_run, &why);
        break;
    case PF_KSET_WALK:
        /* The machine E3 sealed: `Job.nfa`, wrapped, never rebuilt after. */
        pcrec_kset_walk(cx, &cx->job->nfa, &pf->kset_walk);
        break;
    case PF_RUN_PIN:
        pf_ask(cx, PF_KSET_WALK, false);
        pf_ask(cx, PF_REQ_RUN, false);
        pcrec_run_pin(&pf->kset_walk, &pf->req_run, pcrec_find_byte_rate(cx),
                      &pf->run_pin);
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

/* E1 is FORCED, not lazy (design §2): both facts are derived here, on the
 * structural tree, so their answer is a function of the seal and never of
 * which pass asked first. `pf_ask`'s `pass` is false: the seal is not a
 * consumer, and `used` stays the passes' record. */
void pcrec_facts_seal_e1(Ctx *cx, const struct Ast *root)
{
    cx->job->pf.root = root;
    cx->job->pf.epoch = PF_E1_STRUCT;
    pf_ask(cx, PF_KINDS, false);
    pf_ask(cx, PF_NULLABLE, false);
}

/* THE E1 INVARIANCE CROSS-CHECK (design §3): the same two derivations over
 * the LOWERED tree must reproduce what E1 sealed on the structural one. The
 * proof is that every pass between the seals rewrites node flags or class
 * contents only; this is that proof checked on every compile, in the shape of
 * `src/ir/nfa.c`'s `cstart_check_omission` — a diagnosed internal error at
 * the point a disagreement would start to matter, never an `abort()`. */
static void pf_check_e1(Ctx *cx, const struct Ast *root)
{
    const PatFacts *pf = &cx->job->pf;
    unsigned kinds = pcrec_pattern_kinds(root);
    bool nullable = pcrec_pattern_nullable(root);
    if (kinds != pf->kinds)
        pcrec_ctx_fail(cx, 0, "internal error: [PATFACTS] the kind mask sealed "
                       "at E1 (0x%x) disagrees with the lowered tree's (0x%x)",
                       pf->kinds, kinds);
    if (nullable != pf->nullable)
        pcrec_ctx_fail(cx, 0, "internal error: [PATFACTS] nullability sealed "
                       "at E1 (%s) disagrees with the lowered tree's (%s)",
                       pf->nullable ? "yes" : "no", nullable ? "yes" : "no");
}

void pcrec_facts_seal_e2(Ctx *cx, const struct Ast *root)
{
    if (cx->job->pf.epoch != PF_E1_STRUCT)
        pcrec_ctx_fail(cx, 0, "internal error: [PATFACTS] E2 sealed on an "
                       "attempt that never sealed E1");
    pf_check_e1(cx, root);
    cx->job->pf.root = root;
    cx->job->pf.epoch = PF_E2_LOWERED;
}

void pcrec_facts_seal_e3(Ctx *cx)
{
    if (cx->job->pf.epoch != PF_E2_LOWERED)
        pcrec_ctx_fail(cx, 0, "internal error: [PATFACTS] E3 sealed on an "
                       "attempt that never sealed E2");
    cx->job->pf.epoch = PF_E3_MACHINE;
}

unsigned pcrec_fact_kinds(Ctx *cx)
{
    pf_ask(cx, PF_KINDS, true);
    return cx->job->pf.kinds;
}

bool pcrec_fact_nullable(Ctx *cx)
{
    pf_ask(cx, PF_NULLABLE, true);
    return cx->job->pf.nullable;
}

int pcrec_fact_start_anchor(Ctx *cx)
{
    pf_ask(cx, PF_START_ANCHOR, true);
    return cx->job->pf.start_anchor;
}

const StartSet *pcrec_fact_start_set(Ctx *cx)
{
    pf_ask(cx, PF_START_SET, true);
    return &cx->job->pf.start_set;
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

long long pcrec_fact_req_run_maxoff(Ctx *cx)
{
    pf_ask(cx, PF_REQ_RUN_MAXOFF, true);
    return cx->job->pf.req_run.len >= 2 ? cx->job->pf.req_run.maxoff : -1;
}

int pcrec_fact_req_byte(Ctx *cx)
{
    pf_ask(cx, PF_REQ_BYTE, true);
    return cx->job->pf.req_byte;
}

const KsetWalk *pcrec_fact_kset_walk(Ctx *cx)
{
    pf_ask(cx, PF_KSET_WALK, true);
    return &cx->job->pf.kset_walk;
}

const RunPin *pcrec_fact_run_pin(Ctx *cx)
{
    pf_ask(cx, PF_RUN_PIN, true);
    return &cx->job->pf.run_pin;
}

void pcrec_facts_force_all(Ctx *cx)
{
    PatFacts *pf = &cx->job->pf;
    pf->forcing = true;
    for (; pf->force_next < PF_NFACTS; pf->force_next++) {
        PfFactId f = (PfFactId)pf->force_next;
        /* Never past a seal this route did not write: forcing it would walk
         * a machine the compile never built, or one whose meaning is not the
         * fact's (design §3, §11.4). An E3 fact on a route that sealed E2 is
         * still ASKED — `pf_enter` answers it `absent` with the route's
         * decline without deriving — so its row names the reason. */
        if ((int)pf->epoch < (int)pf_epoch[f] && !pf_route_unsealed(pf, f))
            continue;
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

/* `n` bytes as lowercase hex, then `@idx` when `idx >= 0`, then — only where
 * some position of `mask` is not `0xFF` — `/` and the mask as hex: the
 * `REQ_RUN` spelling (hex because a run is arbitrary bytes inside a
 * `#define`'s string body — one spelling for all 256 values), arena text.
 * An exact run's text is unchanged by the mask ([OPT-LITSCAN] S4 C3), so
 * `"53454c454354@4/dfdfdfdfdfdf"` is a masked run and `"2e746172@0"` an
 * exact one. */
static const char *pf_hex(Ctx *cx, const unsigned char *b,
                          const unsigned char *mask, int n, int idx)
{
    StrBuf sb = { 0 };
    const char *t;
    bool masked = false;
    sb.cx = cx;
    for (int k = 0; k < n; k++) pcrec_sb_printf(&sb, "%02x", b[k]);
    if (idx >= 0) pcrec_sb_printf(&sb, "@%d", idx);
    for (int k = 0; k < n; k++) if (mask[k] != 0xFF) masked = true;
    if (masked) {
        pcrec_sb_putc(&sb, '/');
        for (int k = 0; k < n; k++) pcrec_sb_printf(&sb, "%02x", mask[k]);
    }
    t = pcrec_sb_fragf(&cx->arena, "%s", sb.p ? sb.p : "");
    pcrec_sb_free(&sb);
    return t;
}

/* The `kinds` value's member names, indexed by `PF_KIND_*` bit position. */
static const char *const pf_kind_name[] = {
    "bref", "linked_call", "var", "atomic", "lookaround", "live_capture",
    "collapsible_rep"
};
_Static_assert(PF_KIND_COLLAPSIBLE_REP ==
                   1u << (sizeof pf_kind_name / sizeof pf_kind_name[0] - 1),
               "one kind name per PF_KIND_* bit, the last bit last");

/* Fact `f`'s ONE renderer. Every fact with no answer to give renders
 * `"none"` — the stamps' own member for "declined", because 0 is a legal
 * byte and a legal window and no number is free to mean it. The switch has
 * no `default:`, so a `facts.def` row with no renderer does not compile. */
const char *pcrec_fact_render(Ctx *cx, PfFactId f)
{
    const PatFacts *pf = &cx->job->pf;
    switch (f) {
    case PF_KINDS: {
        StrBuf sb = { 0 };
        const char *t;
        sb.cx = cx;
        for (unsigned b = 0; b < sizeof pf_kind_name / sizeof pf_kind_name[0]; b++)
            if (pf->kinds & (1u << b))
                pcrec_sb_printf(&sb, "%s%s", sb.len ? "," : "", pf_kind_name[b]);
        t = sb.len ? pcrec_sb_fragf(&cx->arena, "%s", sb.p) : "none";
        pcrec_sb_free(&sb);
        return t;
    }
    case PF_NULLABLE:
        return pf->nullable ? "yes" : "no";
    case PF_START_ANCHOR:
        return pcrec_start_anchor_name(pf->start_anchor);
    case PF_START_SET: {
        /* `nullable` where the erased language can match empty (no byte is
         * necessary); otherwise the member count, `:`, and the 32 bytes in
         * lowercase hex, byte 0 first, bit `b & 7` of byte `b >> 3`. */
        StrBuf sb = { 0 };
        const char *t;
        int n = 0;
        if (pf->start_set.nullable) return "nullable";
        sb.cx = cx;
        for (int b = 0; b < 256; b++) n += (pf->start_set.bits[b >> 3] >> (b & 7)) & 1;
        pcrec_sb_printf(&sb, "%d:", n);
        for (int i = 0; i < 32; i++) pcrec_sb_printf(&sb, "%02x", pf->start_set.bits[i]);
        t = pcrec_sb_fragf(&cx->arena, "%s", sb.p);
        pcrec_sb_free(&sb);
        return t;
    }
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
        return pf_hex(cx, pf->req_run.whole, pf->req_run.whole_mask,
                      pf->req_run.whole_len, -1);
    case PF_REQ_RUN:
        if (pf->req_run.len < 2) return "none";
        return pf_hex(cx, pf->req_run.bytes, pf->req_run.mask, pf->req_run.len,
                      pf->req_run.idx);
    case PF_REQ_RUN_MAXOFF:
        /* [K82] the window's maximum byte offset from the attempt start. */
        if (pf->req_run.len < 2) return "none";
        if (pf->req_run.maxoff >= PCREC_W_UNBOUNDED) return "unbounded";
        return pcrec_sb_fragf(&cx->arena, "%lld", pf->req_run.maxoff);
    case PF_REQ_BYTE:
        if (pf->req_byte < 0) return "none";
        return pcrec_sb_fragf(&cx->arena, "%d", pf->req_byte);
    case PF_KSET_WALK: {
        /* One item per offset, offset order: a singleton as its byte in
         * decimal, a wider set as `[N]`, its member count. */
        StrBuf sb = { 0 };
        const char *t;
        sb.cx = cx;
        for (int j = 0; j < pf->kset_walk.nwalk; j++) {
            const PrefixK *k = &pf->kset_walk.k[j];
            if (k->count == 1) pcrec_sb_printf(&sb, "%s%d", j ? "," : "", k->byte);
            else pcrec_sb_printf(&sb, "%s[%d]", j ? "," : "", k->count);
        }
        t = sb.len ? pcrec_sb_fragf(&cx->arena, "%s", sb.p) : "none";
        pcrec_sb_free(&sb);
        return t;
    }
    case PF_RUN_PIN:
        /* `o` for a pin on the whole window (every exact run: the text
         * before [OPT-LITSCAN] S4 C3); `o:at+len` for a pin on an exact
         * stretch inside a masked window. */
        if (!pf->run_pin.pinned) return "none";
        if (pf->run_pin.at == 0 && pf->run_pin.len == pf->req_run.len)
            return pcrec_sb_fragf(&cx->arena, "%d", pf->run_pin.o);
        return pcrec_sb_fragf(&cx->arena, "%d:%d+%d", pf->run_pin.o,
                              pf->run_pin.at, pf->run_pin.len);
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
