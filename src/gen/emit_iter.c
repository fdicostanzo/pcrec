/* [FINDALL-NEXT] I1 THE FIND-ALL ITERATOR'S EMITTER (docs/design/findall_iter.md
 * revision 3, as cut by the I1 ruling: no batch ABI, no `next_n`).
 *
 * `<prefix>_next(rx_iter *, caps)` is the `iterate` row of `entry_rows[]`
 * (src/gen/entries.c): bind once (`<p>__enter`, the iterator's own state
 * machine plus the once-per-iterator checks), then one STEP per call
 * (`<p>__step`): the NOTEMPTY_ATSTART retry where the artifact can report an
 * empty span, the search body at `lo`, and PCRE2's global-iteration advance.
 * This file writes the shared block's `rx_iter` and its setters, the header's
 * two lines, and the iterator's static steps; the engine emitter writes the
 * search body (`<p>__find`, a DFA body split off `<p>_search`, or the VM's
 * search loop split off `<p>_search_run`) and the retry (`<p>__retry`), and
 * says which shape the STEP has (`PcrecIterText`).
 *
 * EVERYTHING HERE IS SCAFFOLD (findall_iter.md §6.4): fixed text, the same on
 * every artifact of a shape, emitted inside the scaffold bracket
 * (`pcrec_sb_scaffold_open`) so no length decision reads it. The retry
 * machine's tables are NOT here: they are a machine, emitted by the DFA
 * emitter, and count like one. */
#include "core/internal.h"

/* The retry rows' predicates. `none`: nothing is retried -- no
 * `<prefix>_next`, a compound part (which never iterates), or no empty span
 * is ever reported. */
static bool retry_none_applies(Ctx *cx)
{
    return !pcrec_entry_requested(cx, PCREC_ENTRY_NEXT) || pcrec_is_part(cx) ||
           !pcrec_fact_reports_empty(cx);
}
/* `notempty-machine`: a DFA artifact. */
static bool retry_machine_applies(Ctx *cx)
{
    return cx->job->fit.chosen == ENGM_DFA;
}
/* `guarded-matcher`: a VM artifact. */
static bool retry_matcher_applies(Ctx *cx)
{
    return cx->job->fit.chosen == ENGM_VM;
}

/* THE RETRY TABLE (internal.h), first match. `retry`: the anchored scan of
 * a machine whose start never accepts, so it cannot give up. `retry-budgeted`:
 * one anchored attempt of the VM program with its accept guarded, metered
 * like any search, so a give-up can end the iteration there. */
static const PcrecIterRetryRow iter_retry_rows[] = {
    { "none",             "none",           retry_none_applies,    0 },
    { "notempty-machine", "retry",          retry_machine_applies, PCREC_ITER_NEEDS_NEDFA },
    { "guarded-matcher",  "retry-budgeted", retry_matcher_applies, PCREC_ITER_NEEDS_GUARDED },
};

const PcrecIterRetryRow *pcrec_iter_retry_of(Ctx *cx)
{
    /* `none` reads the request, which the driver can ask before emission;
     * `next` is a root no row calls, so the closure emits it exactly then */
    if (cx->job->entry_shaped &&
        pcrec_entry_emitted(cx, PCREC_ENTRY_NEXT) != pcrec_entry_requested(cx, PCREC_ENTRY_NEXT))
        pcrec_ctx_fail(cx, 0, "internal error: `next` is emitted where the entry "
                       "request does not name it, or the reverse");
    for (size_t i = 0; i < sizeof iter_retry_rows / sizeof *iter_retry_rows; i++)
        if (iter_retry_rows[i].applies(cx)) return &iter_retry_rows[i];
    pcrec_ctx_fail(cx, 0, "internal error: an artifact that reports an empty "
                   "span has no find-all retry row (src/gen/emit_iter.c)");
    return NULL;
}

/* The shared block's iterator text: `PCREC_ERR_ITER` sits with the other
 * codes (emit_dfa.c); this is the type, its states and its setters. */
void pcrec_emit_iter_abi_types(StrBuf *sb)
{
    pcrec_sb_scaffold_open(sb);
    pcrec_sb_puts(sb,
        "/* [FINDALL-NEXT] THE FIND-ALL ITERATOR: one caller-owned struct per\n"
        " * find-all over one subject, bound at init:\n"
        " *\n"
        " *   rx_iter it = RX_ITER_INIT(s, n);\n"
        " *   while (<prefix>_next(&it, caps)) use(caps);\n"
        " *   if (it.rc < 0) ... the give-up or refusal that ended it\n"
        " *\n"
        " * <prefix>_next returns 1 per match (caps as <prefix>_search writes\n"
        " * them) and 0 at the end; rc is then 0 (done) or the code. The\n"
        " * iteration is PCRE2's global iteration (an empty match is retried at\n"
        " * its position under NOTEMPTY_ATSTART). A caller writes the struct\n"
        " * only through RX_ITER_INIT and the setters, and only while it is\n"
        " * FRESH (before the first call); a setter on an ENDED iterator does\n"
        " * nothing, on any other it makes the next call refuse with\n"
        " * PCREC_ERR_ITER. While it is live the subject, the variables and the\n"
        " * buffers bound into it must not change, and handing it to another\n"
        " * artifact's <prefix>_next is undefined. lo is defined only once the\n"
        " * iterator has ended with rc < 0: the start of the search that ended\n"
        " * it. The struct is position-independent and may be copied. */\n"
        "#define PCREC_ITER_LAYOUT      3u   /* bumps with any change to rx_iter's layout */\n"
        "#define PCREC_ITER_TAG       (0x49540000u | (PCREC_ITER_LAYOUT << 8))\n"
        "#define PCREC_ITER_FRESH     (PCREC_ITER_TAG | 0x01u)\n"
        "#define PCREC_ITER_BOUND     (PCREC_ITER_TAG | 0x02u)\n"
        "#define PCREC_ITER_ENDED     (PCREC_ITER_TAG | 0x03u)\n"
        "#define PCREC_ITER_OPT_AT    0x10u  /* option bits: the setters, on a FRESH iterator */\n"
        "#define PCREC_ITER_OPT_VARS  0x20u\n"
        "#define PCREC_ITER_OPT_IN    0x40u\n"
        "#define PCREC_ITER_OPT_MASK  0xF0u\n"
        "#define PCREC_ITER_F_RETRY   0x1u   /* flags: an empty match is to be retried at lo */\n"
        "\n"
        "typedef struct rx_iter {\n"
        "    uint32_t hdr;              /* tag | layout | state | option bits */\n"
        "    int32_t  rc;               /* 1 live, 0 done, < 0 the code that ended it */\n"
        "    uint32_t flags;            /* PCREC_ITER_F_* */\n"
        "    const unsigned char *s;    /* bound at init */\n"
        "    size_t   n;\n"
        "    size_t   lo;               /* the next search position; never decreases */\n"
        "    const rx_var *vars;        /* rx_iter_vars; NULL after bind if not set */\n"
        "    size_t   nvars;\n"
        "    const void *bufs;          /* <prefix>_iter_buffers; NULL after bind if not set */\n"
        "} rx_iter;\n"
        "\n"
        "static inline rx_iter rx_iter_init(const unsigned char *s, size_t n)\n"
        "{ rx_iter it = { PCREC_ITER_FRESH, 1, 0, s, n, 0, (const rx_var *)0, 0, (const void *)0 }; return it; }\n"
        "#define RX_ITER_INIT(s_, n_) rx_iter_init((s_), (n_))\n"
        "\n"
        "#define PCREC_ITER_SET_(it_, stores_, bit_) \\\n"
        "    do { if (((it_)->hdr & ~PCREC_ITER_OPT_MASK) == PCREC_ITER_FRESH) { stores_; (it_)->hdr |= (bit_); } \\\n"
        "         else if ((it_)->hdr != PCREC_ITER_ENDED) (it_)->hdr = 0; } while (0)\n"
        "/* Start at pos rather than 0 (checked once, at the first call, as\n"
        " * <prefix>_search checks its start position). */\n"
        "static inline void rx_iter_at(rx_iter *it, size_t pos)\n"
        "{ PCREC_ITER_SET_(it, it->lo = pos, PCREC_ITER_OPT_AT); }\n"
        "/* The caller's variables, by name, for every search of this find-all. */\n"
        "static inline void rx_iter_vars(rx_iter *it, const rx_var *v, size_t nv)\n"
        "{ PCREC_ITER_SET_(it, (it->vars = v, it->nvars = nv), PCREC_ITER_OPT_VARS); }\n"
        "\n");
    pcrec_sb_scaffold_close(sb);
}

/* The header's two lines for `<prefix>`: the typed buffers setter, beside the
 * `<prefix>_buffers` type it names, and the entry's declaration. */
void pcrec_emit_iter_buffers_setter(StrBuf *sb, const char *prefix)
{
    pcrec_sb_scaffold_open(sb);
    /* Outside the shared block, so its prose is NON-ESSENTIAL (D112 item 2). */
    pcrec_sb_cmt_open(sb, PCREC_CMT_NONESSENTIAL);
    pcrec_sb_printf(sb,
        "/* [FINDALL-NEXT] Bind this storage for every search of a FRESH iterator\n"
        " * (the iterator's own storage otherwise), as %s_search_in binds it. */\n",
        prefix);
    pcrec_sb_cmt_close(sb);
    pcrec_sb_printf(sb,
        "static inline void %s_iter_buffers(rx_iter *it, const %s_buffers *b)\n"
        "{ PCREC_ITER_SET_(it, it->bufs = b, PCREC_ITER_OPT_IN); }\n",
        prefix, prefix);
    pcrec_sb_scaffold_close(sb);
}

/* The two controllers' declarations; the caller writes the first line's
 * storage, `storage` is the second's (the NEXT entry's, for both). */
void pcrec_emit_next_decl(StrBuf *sb, const char *prefix, const char *storage)
{
    pcrec_sb_scaffold_open(sb);
    pcrec_sb_printf(sb, "int %s_next(rx_iter *it, ptrdiff_t (*capture_spans)[2]);\n", prefix);
    pcrec_sb_printf(sb, "%ssize_t %s_next_n(rx_iter *it, ptrdiff_t (*capture_spans)[2], size_t k);\n",
                    storage, prefix);
    pcrec_sb_scaffold_close(sb);
}

/* `<p>__bind_checks`: the caller-position prologue `<p>_search` runs on every
 * call (the startpos guard or alignment, then the `-futf-check` precheck), run
 * ONCE per iterator on its first position: every later `lo` is a character
 * boundary and the checked range only shrinks (findall_iter.md §3.5, §3.6).
 * The one prologue emitter both entries use writes it, so the codes and their
 * order are `_search`'s (IT12). Returns whether it wrote anything: an artifact
 * whose prologue is empty has no bind check. */
static bool emit_bind_checks(Ctx *cx, StrBuf *c, const char *p)
{
    /* the position is the caller's `lo` itself, so an alignment the guard
     * makes is stored before the subject check can refuse: `lo` is then the
     * position `<prefix>_valid_upto` was asked from (§3.8¶9) */
    StrBuf g = { .cx = cx };
    pcrec_sb_comments(&g, !c->cmt_drop);
    pcrec_emit_startpos_guard(cx, &g, "    ", "(*pos)", "subject",
                              "subject_length", false);
    bool any = g.len > 0 || g.cmt_dropped > 0;
    if (any) {
        pcrec_sb_printf(c,
            "static int %s__bind_checks(const unsigned char *subject, size_t subject_length,\n"
            "                          size_t *pos)\n"
            "{\n", p);
        pcrec_sb_puts(c, g.p ? g.p : "");
        pcrec_sb_puts(c,
            "    return 0;\n"
            "}\n\n");
    }
    pcrec_sb_free(&g);
    return any;
}

/* `<p>__enter`, the slow path (findall_iter.md §1.2): an ENDED iterator
 * returns 0 with no work; a FRESH one is BOUND -- the once-per-iterator
 * checks run and the bare BOUND word is stored, after which nothing reads an
 * option bit; any other header refuses with PCREC_ERR_ITER and ends. Every
 * field a setter did not write already holds its neutral value, because
 * `rx_iter_init` writes them all (IT1; lane iteropt: the bind used to store
 * them a second time), so with no checks a bind is one store and gcc inlines
 * it into both controllers. */
static void emit_enter(StrBuf *c, const char *p, bool checks)
{
    pcrec_sb_printf(c,
        "static inline int %s__enter(rx_iter *it)\n"
        "{\n"
        "    uint32_t h = it->hdr;\n"
        "    if (h == PCREC_ITER_ENDED) return 0;\n"
        "    if ((h & ~PCREC_ITER_OPT_MASK) != PCREC_ITER_FRESH) {\n"
        "        it->rc = PCREC_ERR_ITER;\n"
        "        it->hdr = PCREC_ITER_ENDED;\n"
        "        return 0;\n"
        "    }\n", p);
    if (checks)
        pcrec_sb_printf(c,
            "    {\n"
            "        int r = %s__bind_checks(it->s, it->n, &it->lo);\n"
            "        if (r) { it->rc = r; it->hdr = PCREC_ITER_ENDED; return 0; }\n"
            "    }\n", p);
    pcrec_sb_puts(c,
        "    it->hdr = PCREC_ITER_BOUND;\n"
        "    return 1;\n"
        "}\n\n");
}

/* The STEP's cursor parameters, `<p>__step`'s and its own-storage wrappers'
 * (lane iteropt2): the subject, the next search position `*lop` and, where
 * the retry is emitted, `*flp` (the iterator's `lo` and `flags`), plus the
 * caller's variables on a variable-bearing artifact. The controllers hold
 * `lo` and `flags` in locals, loaded from `rx_iter` once per call and stored
 * back once, so nothing the search body calls makes gcc reload them through
 * `it`. */
static const char *cursor_params(Ctx *cx, const PcrecIterText *t)
{
    return pcrec_sb_fragf(&cx->arena, "const unsigned char *s, size_t n, size_t *lop%s%s",
                          t->retry ? ", uint32_t *flp" : "",
                          t->vars ? ", const rx_var *vars, size_t nvars" : "");
}

/* The same cursor as arguments, forwarded by name from a function that has
 * the cursor parameters. */
static const char *cursor_args(Ctx *cx, const PcrecIterText *t)
{
    return pcrec_sb_fragf(&cx->arena, "s, n, lop%s%s", t->retry ? ", flp" : "",
                          t->vars ? ", vars, nvars" : "");
}

/* `<p>__step`, one STEP (findall_iter.md §2.1, §3.1-§3.3): past the end
 * (`lo > n`, where an empty match at `n` leaves it) done, with no search: the
 * search body has no caller-position guard, and a `\G` artifact's would
 * report an empty match at `lo` there. Where RETRY is set
 * the retry R at `lo` and, on its no match, the search one character on;
 * else the search at `lo`. Returns 1 (a match in `c`, `NCAPS` pairs, and the
 * cursor advanced), 0 (done) or a code; `*at` is the start of the search
 * that answered. It COMMITS the cursor only on 1, so a step a tier gave up
 * on runs again from the same state. The advance after a non-empty match is
 * the aligned end (K75); after an empty one it is the retry at its position,
 * or the end at `n`; on an artifact whose reported span is never empty it is
 * today's loop's `next_pos(start)`, unreachable but exact. */
static void emit_step(Ctx *cx, StrBuf *c, const char *p, const char *body,
                      const PcrecIterText *t)
{
    const char *runp = t->vm ? ", " : "";
    const char *runt = t->vm ? pcrec_sb_fragf(&cx->arena, "%s_run_state *run", p) : "";
    const char *runa = t->vm ? ", run" : "";
    const char *va = t->vars ? ", vars, nvars" : "";
    pcrec_sb_printf(c,
        "static inline __attribute__((always_inline)) int %s__step(%s,\n"
        "                                                       ptrdiff_t (*c)[2]%s%s, size_t *at)\n"
        "{\n"
        "    size_t lo = *lop;\n"
        "    int r;\n"
        "    if (lo > n) { *at = lo; return 0; }   /* an empty match at n ended it */\n",
        p, cursor_params(cx, t), runp, runt);
    if (t->retry)
        pcrec_sb_printf(c,
            "    if (*flp & PCREC_ITER_F_RETRY) {   /* an empty match was reported at lo */\n"
            "        ptrdiff_t len;\n"
            "        *at = lo;\n"
            "        len = %s__retry(s, n, lo, c%s%s);\n"
            "        if (len >= 0) goto %s_matched;\n"
            "        if (len < -1) return (int)len;\n"
            "        lo = %s__next_pos(s, n, lo);\n"
            "    }\n", p, runa, va, p, p);
    pcrec_sb_printf(c,
        "    *at = lo;\n"
        "    r = %s(s, n, lo, c%s%s);\n"
        "    if (r != 1) return r;\n", body, runa, va);
    if (t->retry)
        pcrec_sb_printf(c,
            "%s_matched:\n"
            "    if (c[0][1] > c[0][0]) {\n"
            "        *lop = %s__next_pos(s, n, (size_t)c[0][1] - 1);   /* K75: the aligned end */\n"
            "        *flp = 0;\n"
            "    } else if ((size_t)c[0][0] < n) {\n"
            "        *lop = (size_t)c[0][0];                          /* PCRE2: retry at the empty match */\n"
            "        *flp = PCREC_ITER_F_RETRY;\n"
            "    } else {\n"
            "        *lop = n + 1;                                    /* an empty match at n ends it */\n"
            "        *flp = 0;\n"
            "    }\n"
            "    return 1;\n"
            "}\n\n", p, p);
    else
        pcrec_sb_printf(c,
            "    *lop = c[0][1] > c[0][0] ? %s__next_pos(s, n, (size_t)c[0][1] - 1)   /* K75 */\n"
            "                             : %s__next_pos(s, n, (size_t)c[0][0]);\n"
            "    return 1;\n"
            "}\n\n", p, p);
}

/* The VM's own-storage STEP, `<p>__step_own`: the binding `<p>_search` makes
 * when no buffers are bound into the iterator -- the stamped default, the fast
 * tier escalating to the deep one on a FRAMES give-up ([OPT-1]: the deep re-run
 * is the same step from the same cursor, its answer the default's), or the
 * frameless forward's empty storage. */
static void emit_step_own(Ctx *cx, StrBuf *c, const char *p, const char *up,
                          const PcrecIterText *t)
{
    const char *cp = cursor_params(cx, t);
    const char *ca = cursor_args(cx, t);
    switch (t->own) {
    case PCREC_FWD_OWN_TIERED:
        pcrec_sb_printf(c,
            "static %sint %s__step_deep(%s,\n"
            "                           ptrdiff_t (*c)[2], size_t *at)\n"
            "{\n"
            "    %s_run_state run;\n"
            "    %s_run_buffers storage;   /* this artifact's stamped default */\n"
            "    %s_run_state_bind(&run, storage.frames, %s_RESUME_FRAMES,\n"
            "                            storage.trail,  %s_TRAIL_FRAMES);\n"
            "    return %s__step(%s, c, &run, at);\n"
            "}\n\n"
            "static inline __attribute__((always_inline)) int %s__step_own(%s,\n"
            "                                                           ptrdiff_t (*c)[2], size_t *at)\n"
            "{\n"
            "    %s_run_state run;\n"
            "    %s_fast_buffers fast;   /* [OPT-1] the page-budgeted fast tier */\n"
            "    int r;\n"
            "    %s_run_state_bind(&run, fast.frames, %s_FAST_FRAMES,\n"
            "                            fast.trail,  %s_FAST_TRAIL);\n"
            "    r = %s__step(%s, c, &run, at);\n"
            "    if (r != %s) return r;\n"
            "    %s_TIER_NOTE();\n"
            "    return %s__step_deep(%s, c, at);\n"
            "}\n\n",
            pcrec_attr_text(PCREC_ATTR_NOINLINE), p, cp, p, p, p, up, up, p, ca,
            p, cp, p, p, p, up, up, p, ca, t->frames_code, up, p, ca);
        return;
    case PCREC_FWD_EMPTY:
        pcrec_sb_printf(c,
            "static inline __attribute__((always_inline)) int %s__step_own(%s,\n"
            "                                                           ptrdiff_t (*c)[2], size_t *at)\n"
            "{\n"
            "    %s_run_state run;   /* frameless: no storage to bind */\n"
            "    %s_run_state_bind(&run, (void *)0, 0, (void *)0, 0);\n"
            "    return %s__step(%s, c, &run, at);\n"
            "}\n\n", p, cp, p, p, p, ca);
        return;
    case PCREC_FWD_OWN:
    case PCREC_FWD_INERT:
    case PCREC_FWD_CALLER:
        break;
    }
    pcrec_sb_printf(c,
        "static inline __attribute__((always_inline)) int %s__step_own(%s,\n"
        "                                                           ptrdiff_t (*c)[2], size_t *at)\n"
        "{\n"
        "    %s_run_state run;\n"
        "    %s_run_buffers storage;   /* this artifact's stamped default */\n"
        "    %s_run_state_bind(&run, storage.frames, %s_RESUME_FRAMES,\n"
        "                            storage.trail,  %s_TRAIL_FRAMES);\n"
        "    return %s__step(%s, c, &run, at);\n"
        "}\n\n", p, cp, p, p, p, up, up, p, ca);
}

/* `<p>__one`, ONE search of a BOUND iterator from the caller's cursor
 * (findall_iter_i2.md §2.3; lane iteropt2): one STEP (the caller's storage
 * or the artifact's own on the VM), and on the end path the cursor's `lo`
 * set to the search that ended it and the iterator ENDED with `rc`. `c` is
 * never NULL. The controllers own the cursor: `<p>__one_call` (`_next`'s
 * body) loads and stores it around one call, `_next_n` around its loop. */
static void emit_one(Ctx *cx, StrBuf *c, const char *p, const PcrecIterText *t)
{
    const char *sa = pcrec_sb_fragf(&cx->arena, "s, n, lop%s%s", t->retry ? ", flp" : "",
                                    t->vars ? ", it->vars, it->nvars" : "");
    pcrec_sb_printf(c,
        "static inline __attribute__((always_inline)) int %s__one(rx_iter *it, const unsigned char *s,\n"
        "                                                      size_t n, size_t *lop%s,\n"
        "                                                      ptrdiff_t (*c)[2])\n"
        "{\n"
        "    size_t at;\n"
        "    int r;\n", p, t->retry ? ", uint32_t *flp" : "");
    if (t->vm)
        pcrec_sb_printf(c,
            "    if (it->bufs) {                                    /* the caller's storage */\n"
            "        const %s_buffers *b = (const %s_buffers *)it->bufs;\n"
            "        %s_run_state run;\n"
            "        %s_run_state_bind(&run, b->frames, b->nframes, b->trail, b->ntrail);\n"
            "        r = %s__step(%s, c, &run, &at);\n"
            "    } else\n"
            "        r = %s__step_own(%s, c, &at);\n", p, p, p, p, p, sa, p, sa);
    else
        pcrec_sb_printf(c, "    r = %s__step(%s, c, &at);\n", p, sa);
    pcrec_sb_puts(c,
        "    if (r == 1) return 1;\n"
        "    *lop = at;                                         /* the search that ended it */\n"
        "    it->rc = r;\n"
        "    it->hdr = PCREC_ITER_ENDED;                        /* sticky */\n"
        "    return 0;\n"
        "}\n\n");
}

/* `<p>__one_call`, one `<prefix>_next` call: bind a non-BOUND header, then
 * one `<p>__one` whose cursor is the iterator's own `lo` and `flags`. One
 * search loads and stores them once anyway; a local copy would only add a
 * store on the end path, where `lo` has not moved (measured, lane iteropt2). */
static void emit_one_call(StrBuf *c, const char *p, const PcrecIterText *t)
{
    pcrec_sb_printf(c,
        "static inline __attribute__((always_inline)) int %s__one_call(rx_iter *it,\n"
        "                                                           ptrdiff_t (*capture_spans)[2])\n"
        "{\n"
        "    if (__builtin_expect(it->hdr != PCREC_ITER_BOUND, 0))\n"
        "        if (!%s__enter(it)) return 0;                  /* bind; or refuse; or ENDED */\n"
        "    return %s__one(it, it->s, it->n, &it->lo%s, capture_spans);\n"
        "}\n\n", p, p, p, t->retry ? ", &it->flags" : "");
}

/* The two exported controllers, both with the NEXT entry's linkage (no
 * entry of their own: `.next_n` is NULL exactly where `.next` is):
 * `<prefix>_next`, one `<p>__one_call`; `<prefix>_next_n`, up to `k`
 * searches into consecutive NCAPS-pair entries, stopping at the first that
 * ends the iterator, with the cursor in locals across the whole loop (lane
 * iteropt2: `it->lo` was loaded and stored around every search). `k == 0`
 * runs nothing, in every state, so it returns before the bind. A NULL
 * `capture_spans` goes to `<p>__one_local`, the one function that owns the
 * NCAPS-pair stack buffer STEP then writes: with that array out of the
 * controllers, gcc's -fstack-protector-strong (Ubuntu's default) puts no
 * canary on them, which it did on every call (measured, 6-7 instructions
 * per call). It CALLS `<prefix>_next` with that buffer rather than holding
 * a third copy of the step (and of the search body inlined into it). */
static void emit_controllers(Ctx *cx, StrBuf *c, const char *p, const char *up,
                             const PcrecIterText *t)
{
    const char *st = pcrec_entry_storage(cx, PCREC_ENTRY_NEXT);
    pcrec_sb_printf(c,
        "static %sint %s__one_local(rx_iter *it)\n"
        "{\n"
        "    ptrdiff_t local[%s_NCAPS][2];   /* STEP writes NCAPS pairs whatever caps is */\n"
        "    local[0][0] = local[0][1] = 0;   /* -Wmaybe-uninitialized: gcc cannot see the search write them */\n"
        "    return %s_next(it, local);\n"
        "}\n\n", pcrec_attr_text(PCREC_ATTR_NOINLINE), p, up, p);
    pcrec_sb_puts(c, pcrec_attr_text(PCREC_ATTR_NOCLONE));
    pcrec_sb_printf(c,
        "%sint %s_next(rx_iter *it, ptrdiff_t (*capture_spans)[2])\n"
        "{\n"
        "    if (__builtin_expect(!capture_spans, 0)) return %s__one_local(it);\n"
        "    return %s__one_call(it, capture_spans);\n"
        "}\n\n", st, p, p, p);
    pcrec_sb_puts(c, pcrec_attr_text(PCREC_ATTR_NOCLONE));
    pcrec_sb_printf(c,
        "%ssize_t %s_next_n(rx_iter *it, ptrdiff_t (*capture_spans)[2], size_t k)\n"
        "{\n"
        "    const unsigned char *s;\n"
        "    size_t n, lo, i = 0;\n"
        "%s"
        "    if (__builtin_expect(!capture_spans, 0)) {\n"
        "        while (i < k && %s__one_local(it)) ++i;\n"
        "        return i;\n"
        "    }\n"
        "    if (k == 0) return 0;                              /* nothing, in every state */\n"
        "    if (__builtin_expect(it->hdr != PCREC_ITER_BOUND, 0))\n"
        "        if (!%s__enter(it)) return 0;                  /* bind; or refuse; or ENDED */\n"
        "    s = it->s;\n"
        "    n = it->n;\n"
        "    lo = it->lo;\n"
        "%s"
        "    while (i < k && %s__one(it, s, n, &lo%s, capture_spans + i * %s_NCAPS))\n"
        "        ++i;\n"
        "    it->lo = lo;\n"
        "%s"
        "    return i;\n"
        "}\n\n", st, p, t->retry ? "    uint32_t flags;\n" : "", p, p,
        t->retry ? "    flags = it->flags;\n" : "", p, t->retry ? ", &flags" : "", up,
        t->retry ? "    it->flags = flags;\n" : "");
}

void pcrec_emit_iterate(Ctx *cx, StrBuf *c, const GenNames *g,
                        const PcrecIterText *t)
{
    const char *p = cx->opt->prefix;
    pcrec_sb_scaffold_open(c);
    pcrec_sb_cmt_open(c, PCREC_CMT_NONESSENTIAL);
    pcrec_sb_puts(c,
        "/* [FINDALL-NEXT] THE FIND-ALL ITERATOR (pcrec docs/spec/match_api.md\n"
        " * S3.8): bind once, then one search per call, advancing as PCRE2's\n"
        " * global iteration does. */\n");
    pcrec_sb_cmt_close(c);
    /* the search the step runs: the body without the prologue the bind ran,
     * or the search itself where it has none (entries.c's `pr_next_*`) */
    const char *body = pcrec_entry_emitted(cx, PCREC_ENTRY_FIND)
        ? pcrec_sb_fragf(&cx->arena, "%s__find", p)
        : t->vm ? pcrec_sb_fragf(&cx->arena, "%s_run", g->searchfn) : g->searchfn;
    bool checks = emit_bind_checks(cx, c, p);
    emit_enter(c, p, checks);
    emit_step(cx, c, p, body, t);
    if (t->vm) emit_step_own(cx, c, p, g->upper, t);
    emit_one(cx, c, p, t);
    emit_one_call(c, p, t);
    emit_controllers(cx, c, p, g->upper, t);
    pcrec_sb_scaffold_close(c);
}
