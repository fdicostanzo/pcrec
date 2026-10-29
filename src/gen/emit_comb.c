/* [COMPOUND] E0c THE COMBINATOR EMITTERS (docs/design/compound_entries.md
 * §4.1 "each combinator has ONE emitter", §5.1 E0c).
 *
 * Every exported matcher entry is written HERE, by the emitter of its
 * `entry_rows[]` row's combinator (src/gen/entries.c): `pcrec_emit_entry`
 * reads the row's column through `pcrec_entry_comb` and calls
 *
 *   forward             `comb_forward`: call a sibling for the same answer,
 *                       binding storage or not -- the DFA's three inert `_in`
 *                       entries, the VM's three `_in` entries and its three
 *                       un-suffixed entries on every entry rung;
 *   finish-at           `comb_finish_at`: axis G's dispatch, `_match` and
 *                       `_match_caps` by their FINISH form (search-and-filter,
 *                       the anchored machine's own body, nomatch), and the
 *                       compound's one-attempt form;
 *   locate-then-finish  `comb_locate_finish`: the DFA search body
 *                       (`pcrec_emit_dfa_engine`), as `<p>_search` and as the
 *                       VM hybrid's embedded search;
 *   first-nonzero       `pcrec_emit_compound_search` (src/gen/emit_compound.c).
 *
 * The engine emitters say only what each combinator is built from
 * (`PcrecEntryText`, one member per combinator) and in which order the
 * entries go into the file; they write no entry text themselves. The row
 * picks the member read, and a row whose member the engine did not supply
 * is an internal error, so the table and the emitters cannot disagree in
 * silence.
 *
 * A RE-SPELLING, BYTE-IDENTICAL (E0c, zero movers, no abi event): every text
 * below is the old emitter's, moved here verbatim (src/gen/emit_dfa.c's
 * `emit_in_entry_defs` and axis G's writers, src/gen/emit_vm.c's
 * `vm_emit_default_entry` and three `_in` writers); the three `_in` texts per
 * engine are one format over `fwd_sigs[]`, the per-entry differences as
 * data. The VM's `_run` bodies (internal `finish-at`/`locate-then-finish`
 * rows) are still written by src/gen/emit_vm.c. */
#include "core/internal.h"

/* ---- forward ------------------------------------------------------------ */

/* The three forwarding families' per-entry differences: what each
 * un-suffixed entry returns, takes and threads to its sibling or `_run`. The
 * `_in` sibling takes the same arguments plus the descriptor, spelled on its
 * own continuation layout (`in_params`, then `in_sep` before the
 * descriptor). Only `<p>_search` takes the caller's variables as arguments
 * (`vars`); the anchored entries read them from `rx_ctx`. */
typedef struct {
    PcrecEntry entry, in;
    const char *ret;
    const char *params;      /* the un-suffixed entry's parameters */
    const char *in_params;   /* the `_in` entry's, before the descriptor */
    const char *in_sep;      /* between them and the descriptor */
    const char *args;        /* the sibling call's arguments */
    const char *tail;        /* the own storage local's comment */
    bool vars;
} FwdSig;

static const FwdSig fwd_sigs[] = {
    { PCREC_ENTRY_SEARCH, PCREC_ENTRY_SEARCH_IN, "int",
      "const unsigned char *subject, size_t subject_length, size_t search_from,\n"
      "       ptrdiff_t (*capture_spans)[2]",
      "const unsigned char *subject, size_t subject_length, size_t search_from,\n"
      "          ptrdiff_t (*capture_spans)[2]", ", ",
      "subject, subject_length, search_from, capture_spans",
      "   /* this artifact's stamped default */", true },
    { PCREC_ENTRY_MATCH, PCREC_ENTRY_MATCH_IN, "ptrdiff_t",
      "const rx_ctx *ctx", "const rx_ctx *ctx", ", ", "ctx", "", false },
    { PCREC_ENTRY_MATCH_CAPS, PCREC_ENTRY_MATCH_CAPS_IN, "ptrdiff_t",
      "const rx_ctx *ctx, ptrdiff_t (*capture_spans_out)[2]",
      "const rx_ctx *ctx, ptrdiff_t (*capture_spans_out)[2]", ",\n                ",
      "ctx, capture_spans_out", "", false },
};

/* The un-suffixed entry's name among the artifact's names. */
static const char *fwd_name(const GenNames *g, PcrecEntry e)
{
    return e == PCREC_ENTRY_SEARCH ? g->searchfn
         : e == PCREC_ENTRY_MATCH  ? g->matchfn : g->matchcapsfn;
}

/* The CALLER binding's one text at `indent`: the run state `run` bound to
 * the regions of the descriptor `d`, frames-then-trail (the order sabotage
 * row S180 swaps). `fwd_in` and the find-all iterator's caller-storage step
 * write it. */
void pcrec_emit_caller_bind(StrBuf *c, const char *indent, const char *p, const char *d)
{
    pcrec_sb_printf(c,
        "%s%s_run_state_bind(&run, %s->frames, %s->nframes,\n"
        "%s                        %s->trail,  %s->ntrail);\n", indent, p, d, d, indent, d, d);
}

/* Writes an `_in` entry, `forward`'s two bindings that take the caller's
 * descriptor: INERT (the DFA: the descriptor is unused, spec §10.4) and
 * CALLER (the VM: a NULL descriptor IS the un-suffixed call, spec §10.3,
 * else bind the caller's two regions and run `_run`). One text per binding
 * for all three entries; `run_state_bind` names the caller's capacities
 * frames-then-trail, the order sabotage row S180 swaps. */
static void fwd_in(Ctx *cx, StrBuf *c, const GenNames *g, const FwdSig *s,
                   PcrecFwdBind bind)
{
    const char *p = cx->opt->prefix;
    const char *name = fwd_name(g, s->entry);
    const char *vp = s->vars ? pcrec_vars_param_text(cx) : "";
    const char *va = s->vars ? pcrec_vars_arg_text(cx) : "";
    pcrec_sb_printf(c, "%s%s %s_in(%s%s%sconst %s_buffers *buffers)\n{\n",
                    pcrec_entry_storage(cx, s->in), s->ret, name, s->in_params,
                    vp, s->in_sep, p);
    if (bind == PCREC_FWD_INERT) {
        pcrec_sb_printf(c,
            "    (void)buffers;\n"
            "    return %s(%s%s);\n"
            "}\n",
            name, s->args, va);
        return;
    }
    pcrec_sb_printf(c,
        "    %s_run_state run;\n"
        "    if (!buffers) return %s(%s%s);\n", p, name, s->args, va);
    pcrec_emit_caller_bind(c, "    ", p, "buffers");
    pcrec_sb_printf(c,
        "    return %s_run(%s, &run%s);\n"
        "}\n\n", name, s->args, va);
}

/* Writes one of the VM's three un-suffixed entries (`<prefix>_search`/`_match`/`_match_caps`), the forward that binds the storage itself: `forward`'s OWN bindings.
 *
 * [COMPOUND] E0c moved this from src/gen/emit_vm.c (`vm_emit_default_entry`)
 * verbatim; `p`/`up` are the prefix and its uppercase (`Vm.p`/`Vm.up`).
 *
 * [OPT-1] THE THREE UN-SUFFIXED ENTRIES, from ONE emitter
 * (docs/design/two_tier_entry.md §2).
 *
 * WHY THIS IS A FUNCTION AND NOT THREE MORE FORMAT STRINGS. `<prefix>_search`,
 * `<prefix>_match` and `<prefix>_match_caps` differ in exactly four things --
 * return type, parameter list, the arguments they thread through to their
 * `_run`, and how the FRAMES give-up is spelled at their layer -- and are
 * otherwise the same six lines. They were already three near-copies before
 * [OPT-1]; adding the tier to each in place would have made them three
 * near-copies of TWELVE lines, with the escalation test pasted three times.
 * That is the parallel-mechanism shape Frank's standing direction rules out,
 * and it is the shape sabotage row S-FB2 exists for: a per-entry typo in one
 * of three copies is what nobody's eye catches.
 *
 * The `_in` entries are NOT emitted here (`fwd_in`). They take no storage
 * decision -- that is the whole of what distinguishes them -- so they have
 * nothing this function decides, and [DD-14.FB]'s delegation direction keeps
 * them thin.
 *
 * THE TWO SHAPES:
 *
 *   tiered == false   exactly what shipped before [OPT-1]: one entry owning a
 *                     `<prefix>_run_buffers` at the stamped default. Emitted
 *                     byte for byte, so a single-tier artifact's entries do
 *                     not move (§3.1's three degenerate cases and
 *                     `-fno-tiered-entry` all land here).
 *   tiered == true    a `noinline` `<name>_deep` static owning that same
 *                     storage, plus an entry that runs on the page-budgeted
 *                     `<prefix>_fast_buffers` and calls it on a FRAMES give-up
 *                     and on nothing else.
 *
 * `frames_code` is the give-up's spelling AT THIS ENTRY'S LAYER, and the two
 * spellings are not interchangeable prose: `<prefix>_search` sits above the
 * search loop, which has already collapsed the private sentinel to the public
 * `PCREC_ERR_FRAMES`, while the two anchored entries sit directly on
 * `<prefix>_match_anchored` and still see `<PREFIX>_R_FRAMES` (§4.4's three
 * layers). Numerically equal today; the layer seam is the reason each is
 * spelled where it belongs. */
static void fwd_own(StrBuf *c, const char *p, const char *up, bool tiered, bool fwd,
                    const char *storage, const char *in_storage,
                    const char *ret, const char *name, const char *callee,
                    const char *params, const char *storage_tail,
                    const char *runargs, const char *deepargs,
                    const char *frames_code, const char *fwdargs,
                    bool callouts, bool fast_no_compact)
{
    if (fwd) {
        /* [CC-DIFF] STEP 2, the FORWARD rungs (`vm_entry_shape` SHARED and
         * FORWARD), and this is Frank's own question answered in the emitter:
         * "why can't rx_match call rx_match_in with the stack buffer?"
         *
         * On an artifact that provably never WRITES the working storage there
         * is no stack buffer to pass, so this entry has nothing to decide.
         * The `_in` sibling already accepts a descriptor and binds whatever it
         * names, so the un-suffixed entry becomes a pure forward through a
         * static empty one — and every property that made STEP 1(a)'s
         * attribute worth having survives: NO LOCAL AT ALL here, so no
         * `<prefix>_run_buffers`, no `<prefix>_run_state`, no array whose
         * presence trips `-fstack-protector-strong`, and no address escaping
         * into a callee. gcc emits a `jmp`.
         *
         * WHAT IT RE-PAYS is one call per entry, against a matcher body the
         * size term has already found large. What it BUYS is the copy count:
         * six inlined bodies become three (FORWARD) or one (SHARED).
         *
         * THE DESCRIPTOR IS STATIC AND `const`, so it is one shared read-only
         * object rather than a per-call store, and it is EMPTY rather than
         * NULL for one reason: `<prefix>_*_in` reads a NULL descriptor as
         * "use the un-suffixed sibling's own storage" and would call straight
         * back here. `{ NULL, 0, NULL, 0 }` takes the binding path instead,
         * which is correct precisely because `emitted_set` and `has_push` are
         * both false — nothing in this artifact reads or writes either
         * region, so a capacity of zero is never consulted. */
        /* The `_in` sibling is DEFINED below this entry, so the forward needs
         * its prototype. It is composed from THIS entry's own `params` plus
         * the descriptor parameter, which is exactly what the definition's
         * own format string spells — one derivation, two spellings, so a
         * parameter list that changed at the definition and not here would be
         * a conflicting declaration rather than a silent mismatch. */
        pcrec_sb_printf(c,
            "%s%s %s_in(%s, const %s_buffers *buffers);\n"
            "%s%s %s(%s)\n"
            "{\n"
            "    return %s_in(%s, &%s_no_buffers);\n"
            "}\n\n",
            in_storage, ret, name, params, p,
            storage, ret, name, params, name, fwdargs, p);
    } else if (tiered) {
        pcrec_sb_cmt_open(c, PCREC_CMT_NONESSENTIAL);
        pcrec_sb_puts(c,
            "/* [OPT-1] THE DEEP TIER: the stamped default storage, on a frame\n"
            " * only a FRAMES give-up reaches. `noinline` is load-bearing --\n"
            " * inlined, these arrays would be back on the entry's own frame and\n"
            " * gcc would probe every one of their pages on every call, which is\n"
            " * the whole of what this shape exists to avoid. */\n");
        pcrec_sb_cmt_close(c);
        pcrec_sb_printf(c,
            "static %s%s %s_deep(%s)\n"
            "{\n"
            "    %s_run_state run;\n"
            "    %s_run_buffers storage;   /* this artifact's stamped default */\n"
            "    %s_run_state_bind(&run, storage.frames, %s_RESUME_FRAMES,\n"
            "                            storage.trail,  %s_TRAIL_FRAMES);\n"
            "    return %s(%s);\n"
            "}\n\n",
            pcrec_attr_text(PCREC_ATTR_NOINLINE), ret, name, params, p, p, p,
            up, up, callee, runargs);
        pcrec_sb_printf(c,
            "%s%s %s(%s)\n"
            "{\n"
            "    %s_run_state run;\n"
            "    %s_fast_buffers fast;   /* [OPT-1] the page-budgeted fast tier */\n"
            "    %s result;\n"
            "    %s_run_state_bind(&run, fast.frames, %s_FAST_FRAMES,\n"
            "                            fast.trail,  %s_FAST_TRAIL);\n",
            storage, ret, name, params, p, p, ret, p, up, up);
        /* [K134] THE FAST TIER NEVER COMPACTS ITS TRAIL. Its FRAMES give-up
         * escalates to a deep tier that re-runs the match from scratch, so a
         * compaction here could only spend work before the same escalation
         * (review 2026-10-29-r2 F5: +15-20% instructions on short calls). */
        if (fast_no_compact)
            pcrec_sb_puts(c, "    run.trail_gc_floor = (size_t)-1;   /* a FRAMES here escalates */\n");
        pcrec_sb_printf(c, "    result = %s(%s);\n", callee, runargs);
        pcrec_sb_cmt_open(c, PCREC_CMT_NONESSENTIAL);
        pcrec_sb_puts(c,
            "    /* ESCALATE ON A FRAMES GIVE-UP AND ON NOTHING ELSE. That code\n"
            "     * means \"a capacity ran out\" and nothing more, so the deep\n"
            "     * tier re-runs the SAME match from scratch at the stamped\n"
            "     * default: same capacities, budgets refilled, one\n"
            "     * deterministic VM. Its answer is therefore the answer this\n"
            "     * entry gave before the tier existed -- match, no-match or any\n"
            "     * give-up, FRAMES included. Every other outcome is already\n"
            "     * that answer and returns here. */\n");
        pcrec_sb_cmt_close(c);
        /* [INLINE-C] 1b (inline_c.md §1.6 D8) a FRAMES that a callout's
         * callee returned is the callee's own capacity, already escalated by
         * its own entry: the replay cannot help, so it propagates here. */
        pcrec_sb_printf(c,
            "    if (result != %s%s) return result;\n"
            "    %s_TIER_NOTE();\n"
            "    return %s_deep(%s);\n"
            "}\n\n",
            frames_code, callouts ? " || run.callee_gave_up" : "", up, name,
            deepargs);
    } else {
        pcrec_sb_printf(c,
            "%s%s %s(%s)\n"
            "{\n"
            "    %s_run_state run;\n"
            "    %s_run_buffers storage;%s\n"
            "    %s_run_state_bind(&run, storage.frames, %s_RESUME_FRAMES,\n"
            "                            storage.trail,  %s_TRAIL_FRAMES);\n"
            "    return %s(%s);\n"
            "}\n\n",
            storage, ret, name, params, p, p, storage_tail, p, up,
            up, callee, runargs);
    }
}

/* [FINDALL-NEXT] `forward`'s OWN and OWN_TIERED bindings for a function that
 * is not one of the six entries: the find-all iterator's own-storage step
 * (src/gen/emit_iter.c). The same text as the entries', so the tier
 * escalation is spelled once. */
void pcrec_emit_own_binding(Ctx *cx, StrBuf *c, const GenNames *g, bool tiered,
                            const char *storage, const char *ret, const char *name,
                            const char *callee, const char *params,
                            const char *runargs, const char *deepargs,
                            const char *frames_code, bool fast_no_compact)
{
    fwd_own(c, cx->opt->prefix, g->upper, tiered, false, storage, "", ret, name,
            callee, params, "", runargs, deepargs, frames_code, "",
            cx->ncallouts > 0, fast_no_compact);
}

/* `forward`'s ONE emitter: entry `e` (one of the six) under binding `f`.
 * The `_in` entries take the caller's descriptor (INERT, CALLER); the
 * un-suffixed ones bind their own storage on the VM's entry rung (OWN,
 * OWN_TIERED, EMPTY). A binding on the wrong half is the engine's bug. */
static void comb_forward(Ctx *cx, StrBuf *c, const GenNames *g, PcrecEntry e,
                         const PcrecFwd *f)
{
    for (size_t i = 0; i < sizeof fwd_sigs / sizeof *fwd_sigs; i++) {
        const FwdSig *s = &fwd_sigs[i];
        const bool in = f->bind == PCREC_FWD_INERT || f->bind == PCREC_FWD_CALLER;
        if (e != (in ? s->in : s->entry)) continue;
        if (in) {
            fwd_in(cx, c, g, s, f->bind);
            return;
        }
        const char *va = s->vars ? pcrec_vars_arg_text(cx) : "";
        const char *args = pcrec_sb_fragf(&cx->arena, "%s%s", s->args, va);
        fwd_own(c, cx->opt->prefix, g->upper, f->bind == PCREC_FWD_OWN_TIERED,
                f->bind == PCREC_FWD_EMPTY, pcrec_entry_storage(cx, s->entry),
                pcrec_entry_storage(cx, s->in), s->ret, fwd_name(g, s->entry),
                pcrec_sb_fragf(&cx->arena, "%s_run", fwd_name(g, s->entry)),
                pcrec_sb_fragf(&cx->arena, "%s%s", s->params,
                               s->vars ? pcrec_vars_param_text(cx) : ""),
                s->tail, pcrec_sb_fragf(&cx->arena, "%s, &run%s", s->args, va),
                args, f->frames_code, args, cx->ncallouts > 0, f->fast_no_compact);
        return;
    }
    pcrec_ctx_fail(cx, 0, "internal error: forward binding %d asked of entry %s",
                   (int)f->bind, pcrec_entry_name(e));
}

/* ---- finish-at ------------------------------------------------------------ */

/* Writes the `<prefix>_match` entry: an anchored match-here test built by reusing `<prefix>_search`'s own leftmost-first priority.
 *
 * [M4.4] (match_api_m4.md §3): the match-here entry, exported UNCONDITIONALLY
 * on every generated matcher (F1/F2) and RETROFITTED onto the existing DFA
 * search — nothing at [M4.4] requires a second, genuinely-anchored
 * automaton. `<prefix>_search`'s own leftmost-first priority already makes
 * this exact: a match beginning at ctx->pos exists iff the search's
 * highest-priority thread (which always tries "match starting here" before
 * "skip a byte and try later", by construction of the unanchored wrap) finds
 * one, so checking the reported start against ctx->pos is not an
 * approximation of anchored matching, it IS anchored matching, reusing the
 * existing forward+reverse walk rather than a new one.
 *
 * [K28 fix, 2026-08-19, repair slice] `caps` IS INITIALIZED, and the
 * initializer is not defensive padding — it is the only shape that compiles.
 * When the pattern's DFA is a single dead state, `<prefix>_search` always
 * returns 0, gcc -O1 inlines it here, and then reports this array as
 * maybe-uninitialized even though `found != 1` short-circuits the read. The
 * warning is bogus (the read is unreachable) but the artifact is source
 * SOMEONE ELSE compiles, and the harness's own GENCFLAGS are
 * `-O1 -Wall -Wextra -Werror`, so it is a build failure rather than a
 * blemish. Two things measured before choosing this:
 *   - it fires at -O1 ONLY: -O0, -O2, -O3 and -Os are all clean, measured,
 *     all five. Why only -O1 was not established and is not asserted here;
 *     what matters is that -O1 is exactly tests/harness/run.sh's default
 *     GENCFLAGS, so "compile it at a different level" is not a fix.
 *   - SPLITTING the `||` into two `if`s does NOT silence it. The dominance
 *     gcc cannot see is not the short-circuit; restructuring the test is not
 *     available and the initializer is the smallest thing that works.
 * The same three lines are owed by `emit_match_caps_def` below and
 * `pcrec_emit_main` (src/gen/emit_dfa.c), which have the identical shape and warn for the
 * identical reason -- the `-Werror` build merely stopped at the first one.
 * Full history, the six corpus spellings it cost, and the repro:
 * docs/dev/known_issues.md K28. */
static void emit_match_def(StrBuf *c, const char *storage, const char *matchfn,
                           const char *searchfn, const char *upper)
{
    pcrec_sb_cmt_open(c, PCREC_CMT_NONESSENTIAL);
    pcrec_sb_puts(c,
        "/* D49: the give-up codes PROPAGATE rather than collapsing to -1.\n"
        " * Unreachable on this engine -- a DFA artifact has no counter to\n"
        " * exhaust -- but written uniformly on purpose: the contract of\n"
        " * rx_matchfn is one contract, and a wrapper that discards codes it\n"
        " * merely happens never to see is the shape that goes wrong when a\n"
        " * later engine shares this emitter. */\n");
    pcrec_sb_cmt_close(c);
    pcrec_sb_printf(c,
        "%sptrdiff_t %s(const rx_ctx *ctx)\n"
        "{\n", storage, matchfn);
    pcrec_sb_cmt_open(c, PCREC_CMT_NONESSENTIAL);
    pcrec_sb_puts(c,
        "    /* Initialized: gcc -O1 false maybe-uninitialized (pcrec K28). */\n");
    pcrec_sb_cmt_close(c);
    pcrec_sb_printf(c,
        "    ptrdiff_t capture_spans[%s_NCAPS][2] = {{0}};\n"
        "    int found = %s(ctx->subject, ctx->len, ctx->pos, capture_spans);\n"
        "    if (found < 0) return (ptrdiff_t)found;\n"
        "    if (found != 1 || (size_t)capture_spans[0][0] != ctx->pos) return -1;\n"
        "    return capture_spans[0][1] - capture_spans[0][0];\n"
        "}\n",
        upper, searchfn);
}

/* Writes the `<prefix>_match_caps` entry: `<prefix>_match`'s capture-delivering sibling.
 *
 * [M4.4] (match_api_m4.md §3.1, D41.4): the anchored capture-DELIVERING
 * sibling of <prefix>_match — same anchoring test, plus a capture_spans_out
 * parameter that gets every RX_NCAPS pair on success and is left UNTOUCHED
 * on failure (A-8's "untouched wins" rule, shared with <prefix>_search). At
 * [M4.4] RX_NCAPS is always 1, so capture_spans_out[0] is the only slot ever
 * written; the loop is written against the macro rather than hardcoded so
 * nothing here needs revisiting when [M4.5] grows it. */
static void emit_match_caps_def(StrBuf *c, const char *storage, const char *fn,
                                const char *searchfn, const char *upper)
{
    pcrec_sb_printf(c,
        "%sptrdiff_t %s(const rx_ctx *ctx, ptrdiff_t (*capture_spans_out)[2])\n"
        "{\n", storage, fn);
    pcrec_sb_cmt_open(c, PCREC_CMT_NONESSENTIAL);
    pcrec_sb_puts(c,
        "    /* Initialized: gcc -O1 false maybe-uninitialized (pcrec K28). */\n");
    pcrec_sb_cmt_close(c);
    pcrec_sb_printf(c,
        "    ptrdiff_t capture_spans[%s_NCAPS][2] = {{0}};\n"
        "    int found = %s(ctx->subject, ctx->len, ctx->pos, capture_spans);\n"
        "    if (found < 0) return (ptrdiff_t)found;\n"
        "    if (found != 1 || (size_t)capture_spans[0][0] != ctx->pos) return -1;\n"
        "    if (capture_spans_out) {\n"
        "        for (int k = 0; k < %s_NCAPS; k++) {\n"
        "            capture_spans_out[k][0] = capture_spans[k][0];\n"
        "            capture_spans_out[k][1] = capture_spans[k][1];\n"
        "        }\n"
        "    }\n"
        "    return capture_spans[0][1] - capture_spans[0][0];\n"
        "}\n",
        upper, searchfn, upper);
}

/* [OPT-REVEND] L2 THE MATCH-HERE ENTRY OF A BODY THAT MATCHES NOTHING
 * (FINISH `nomatch` on the meet `caller ⊓ empty`, locate_finish.md LR-G8):
 * `-1` at once, after K50's startpos guard (which the search-and-filter form
 * reached through `<prefix>_search`, so the refusal is unchanged). Its
 * `_match_caps` is the anchored form's delegate, which never writes. */
static void emit_nomatch_match_def(Ctx *cx, StrBuf *c, const char *matchfn)
{
    pcrec_sb_printf(c,
        "%sptrdiff_t %s(const rx_ctx *ctx)\n"
        "{\n"
        "    const unsigned char *subject = ctx->subject;\n"
        "    size_t subject_length = ctx->len;\n"
        "    size_t search_from = ctx->pos;\n",
        pcrec_entry_storage(cx, PCREC_ENTRY_MATCH), matchfn);
    pcrec_emit_startpos_guard(cx, c, "    ", "search_from", "subject",
                              "subject_length", true);
    pcrec_sb_puts(c, "    (void)subject; (void)subject_length; (void)search_from;\n"
               "    return -1;\n"
               "}\n");
}

/* The capture-delivering sibling. It delegates to `<prefix>_match` rather than
 * re-emitting the scan — one machine, one loop, one place a change lands.
 *
 * IT WRITES THE DEAD GROUPS ITSELF, and that is not optional. On the
 * search-and-filter form those come from `emit_dead_group_fill`, which
 * fills slots 1..NCAPS-1 with PCREC_UNSET on `<prefix>_search`'s success
 * paths (wave G's dead-capture elision: a DFA artifact can promise groups it
 * can never write,
 * because PCRE2 counts them and reports them unset). This form never calls
 * `<prefix>_search`, so the fill has to happen here or those slots would come
 * back as whatever the caller's array held. `RX_NCAPS` is 1 on almost every
 * DFA artifact and the loop then emits nothing at run time.
 *
 * `caps_out[0] == [ctx->pos, ctx->pos + length)` is spec S3.3's own sentence,
 * true here BY CONSTRUCTION rather than by a filter that proved it. On every
 * negative return `caps_out` is UNTOUCHED (A-8's rule) -- every write is
 * below the early return. */
static void emit_anchored_match_caps_def(StrBuf *c, const char *storage,
                                         const char *fn, const char *matchfn,
                                         const char *upper)
{
    pcrec_sb_printf(c,
        "%sptrdiff_t %s(const rx_ctx *ctx, ptrdiff_t (*capture_spans_out)[2])\n"
        "{\n"
        "    ptrdiff_t rx_len = %s(ctx);\n"
        "    if (rx_len < 0) return rx_len;\n"
        "    if (capture_spans_out) {\n"
        "        capture_spans_out[0][0] = (ptrdiff_t)ctx->pos;\n"
        "        capture_spans_out[0][1] = (ptrdiff_t)ctx->pos + rx_len;\n"
        "        for (int rx_g = 1; rx_g < %s_NCAPS; rx_g++) {\n",
        storage, fn, matchfn, upper);
    pcrec_sb_cmt_open(c, PCREC_CMT_NONESSENTIAL);
    pcrec_sb_puts(c,
        "            /* every group this artifact promises is reached only\n"
        "               through a subroutine call or sits under a {0}, so no\n"
        "               match can set it (PCRE2 reports the same) */\n");
    pcrec_sb_cmt_close(c);
    pcrec_sb_puts(c,
        "            capture_spans_out[rx_g][0] = PCREC_UNSET;\n"
        "            capture_spans_out[rx_g][1] = PCREC_UNSET;\n"
        "        }\n"
        "    }\n"
        "    return rx_len;\n"
        "}\n");
}

/* `finish-at`'s ONE emitter, axis G's dispatch: `_match` or `_match_caps` by
 * the FINISH form. Search-and-filter wraps `<p>_search` twice; the
 * anchored-machine and nomatch forms give `_match` its own body and
 * `_match_caps` the delegate that calls it; the compound's form is its first
 * part's one attempt. `_match` is followed by a blank line on every DFA
 * form, as it always was. */
static void comb_finish_at(Ctx *cx, StrBuf *c, const GenNames *g, PcrecEntry e,
                           const PcrecFinish *f)
{
    if (e != PCREC_ENTRY_MATCH && e != PCREC_ENTRY_MATCH_CAPS)
        pcrec_ctx_fail(cx, 0, "internal error: finish-at asked of entry %s",
                       pcrec_entry_name(e));
    const bool caps = e == PCREC_ENTRY_MATCH_CAPS;
    switch (f->form) {
    case PCREC_FIN_FILTER:
        if (caps) {
            emit_match_caps_def(c, pcrec_entry_storage(cx, e), g->matchcapsfn,
                                g->searchfn, g->upper);
            return;
        }
        emit_match_def(c, pcrec_entry_storage(cx, e), g->matchfn, g->searchfn,
                       g->upper);
        break;
    case PCREC_FIN_VERIFY:
    case PCREC_FIN_NOMATCH:
        if (caps) {
            emit_anchored_match_caps_def(c, pcrec_entry_storage(cx, e),
                                         g->matchcapsfn, g->matchfn, g->upper);
            return;
        }
        if (f->form == PCREC_FIN_VERIFY) pcrec_emit_dfa_anchored_match(cx, c, g);
        else                             emit_nomatch_match_def(cx, c, g->matchfn);
        break;
    case PCREC_FIN_PART:
        pcrec_emit_compound_match(cx, c, f->shell, e,
                                  caps ? g->matchcapsfn : g->matchfn, g->upper);
        return;
    }
    pcrec_sb_puts(c, "\n");
}

/* ---- the dispatch --------------------------------------------------------- */

static const char *const comb_names[] = {
    "locate-then-finish", "finish-at", "forward", "first-nonzero",
    "iterate", "leaf", "data", "driver",
};

/* [FINDALL-NEXT] the search body's name, `<p>__find` (entries.c's FIND). */
static const char *find_name(Ctx *cx)
{
    return pcrec_sb_fragf(&cx->arena, "%s__find", cx->opt->prefix);
}

bool pcrec_emit_entry(Ctx *cx, const GenNames *g, PcrecEntry e,
                      const PcrecEntryText *t)
{
    if (!pcrec_entry_emitted(cx, e)) return false;
    StrBuf *c = &cx->job->csb;
    const PcrecEntryComb k = pcrec_entry_comb(cx, e);
    switch (k) {
    case PCREC_COMB_FORWARD:
        if (!t->fwd) break;
        comb_forward(cx, c, g, e, t->fwd);
        return true;
    case PCREC_COMB_FINISH_AT:
        if (!t->fin) break;
        comb_finish_at(cx, c, g, e, t->fin);
        return true;
    case PCREC_COMB_LOCATE_FINISH:
        if (!t->body) break;
        /* `locate-then-finish`'s ONE emitter: the DFA search body under the
         * entry's name and linkage. [FINDALL-NEXT] Where the iterator runs
         * the body too (the FIND row is live), the search entry's body is
         * `<p>__find`, and `<p>_search` is its prologue over that body. */
        if (e == PCREC_ENTRY_SEARCH && pcrec_entry_emitted(cx, PCREC_ENTRY_FIND)) {
            pcrec_emit_dfa_engine(cx, find_name(cx), PCREC_ENTRY_FIND);
            pcrec_emit_search_wrapper(cx, c, g->searchfn);
            return true;
        }
        pcrec_emit_dfa_engine(cx, t->body, e);
        return true;
    case PCREC_COMB_FIRST_NONZERO:
        if (!t->shell || e != PCREC_ENTRY_SEARCH) break;
        if (!pcrec_entry_emitted(cx, PCREC_ENTRY_FIND)) {
            pcrec_emit_compound_search(cx, c, t->shell, g->searchfn, PCREC_ENTRY_SEARCH,
                                       g->upper);
            return true;
        }
        pcrec_emit_compound_search(cx, c, t->shell, find_name(cx), PCREC_ENTRY_FIND,
                                   g->upper);
        pcrec_emit_search_wrapper(cx, c, g->searchfn);
        return true;
    case PCREC_COMB_ITERATE:
        if (!t->iter) break;
        pcrec_emit_iterate(cx, c, g, t->iter);
        return true;
    case PCREC_COMB_LEAF:
    case PCREC_COMB_DATA:
    case PCREC_COMB_DRIVER:
        break;
    }
    pcrec_ctx_fail(cx, 0, "internal error: entry %s's row is `%s`, and its "
                   "engine supplied no text that combinator writes",
                   pcrec_entry_name(e), comb_names[k]);
    return false;
}
