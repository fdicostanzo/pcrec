#!/usr/bin/env python3
# docs/design/findall_iter/twin/mktwin.py — [FINDALL-NEXT] HAND TWIN, REVISION 3
# (lane parity, 2026-10-21; revision 1 was lane iterdes's, recoverable from git).
#
# Mechanical transform of a pcrec-emitted artifact (.c, split form with its .h)
# into the iterator shape findall_iter.md revision 3 proposes (§1.1, §1.2, §2.1,
# §2.3), so the design's codegen, answer and timing claims can be checked on REAL
# artifacts before any emitter change:
#
#   1. the exported `<p>_search` definition is renamed `<p>__find` and made
#      `static inline __attribute__((always_inline))` (the one search body);
#   2. a thin exported `<p>_search` is re-added AFTER it (same noclone attribute
#      the emitter puts on the DFA entry, K24), calling the body;
#   3. `<p>__adv`, a static inline copy of the artifact's own `<p>_next_pos` body
#      (the encoding residual; byte or utf8 read off the artifact);
#   4. `<p>__step` (STEP: the RETRY arm, SEARCH at lo, the K75/empty advance),
#      `<p>__enter` (bind at the first call, §1.2: normalize every optional field,
#      K into nbatch, rc/rc_next/flags/cursor, store BOUND; ENDED returns 0; any
#      other header refuses with PCREC_ERR_ITER and moves to ENDED), `<p>__end`
#      (rc + ENDED, sticky), and the exported `int <p>_next(rx_iter *, caps)` whose
#      fast path is the one header compare (no owner, D165 add. 3);
#   5. the `iterate` row's `batch` cell (§2.3):
#        off (default): `_next` is STEP once with K forced to 1, no `__deliver`,
#                       no cursor test; `size_t <p>_next_n(it, out, k)` (spans
#                       only, the optional extra) is emitted beside it;
#        --fill:        `__deliver` + `__fill` (the IT2 test first, then up to K
#                       STEPs into the bound batch region), `_next` tests the
#                       cursor; no `_next_n` (it would have to drain the batch,
#                       which no design text specifies);
#   6. with --retry, the VM artifact's accept label gains the NOTEMPTY_ATSTART
#      guard and `<p>__retry` runs the anchored caps entry with it armed (the
#      twin carries the flag in ctx->user, which no twin pattern uses; the design
#      carries it in the run state, §3.3).
#
# Fidelity, stated: `__find` is the WHOLE `_search` body, prologue included, so the
# twin runs the artifact's per-call entry checks (startpos guard, -futf-check) on every
# STEP; the design moves them to bind (§3.5, §3.6). That costs the twin, never the
# loop, so a parity verdict reached on the twin is conservative on that term. The
# bind's once-per-iterator checks are therefore not separately spelled here.
#
# The transform asserts every anchor it rewrites is found exactly once; a miss is
# a hard error, never a silent no-op.
#
# usage: python3 -I mktwin.py PREFIX IN.c OUT.c [--retry] [--shared] [--fill]
import re
import sys

pfx, src, dst = sys.argv[1], sys.argv[2], sys.argv[3]
retry = "--retry" in sys.argv[4:]
shared = "--shared" in sys.argv[4:]   # the size alternative / I_shared: ONE noinline body
fill = "--fill" in sys.argv[4:]       # the `batch` cell = fill (default: off)
P = pfx.upper()
text = open(src, encoding="utf-8", errors="surrogateescape").read()


def once(pat, s, flags=0):
    m = list(re.finditer(pat, s, flags))
    if len(m) != 1:
        sys.exit(f"mktwin: anchor {pat!r} found {len(m)} times in {src}")
    return m[0]


# 1. the search definition (single- or multi-line signature), with the noclone
# block the DFA emitter puts above it when present
sig = once(r"(?:#if __has_attribute\(noclone\)\n__attribute__\(\(noclone\)\)\n#endif\n)?"
           r"int " + re.escape(pfx) + r"_search\((const unsigned char \*subject, size_t subject_length,"
           r"\s*size_t search_from,\s*ptrdiff_t \(\*capture_spans\)\[2\])\)\n\{", text)
params = sig.group(1)
# A body that keeps label addresses in a STATIC table (the DFA attempt route's
# direct-threaded dispatch, `static const void *const <p>_targets_N[]`) cannot be
# duplicated by inlining (gcc: "can never be copied because it saves address of
# local label in a static variable"), so it stays ONE static function both entries
# call; every other body is inlined into each entry (findall_iter.md §2.2).
body_end = text.find("\n}\n", sig.end())
static_labels = re.search(r"static const void \*const \w+\[\d+\] = \{ *&&", text[sig.end():body_end]) is not None
linkage = ("static __attribute__((noinline)) int " if (static_labels or shared)
           else "static inline __attribute__((always_inline)) int ")
text = (text[:sig.start()] + linkage + pfx + "__find(" + params + ")\n{" + text[sig.end():])

# 3. the residual, copied (its body is the artifact's own)
nxt = once(r"size_t " + re.escape(pfx) + r"_next_pos\(const unsigned char \*s, size_t n, size_t pos\)\n\{\n(.*?)\n\}\n",
           text, re.S)
adv_body = nxt.group(1)

# 6. the NOTEMPTY_ATSTART guard at the VM accept label
has_k = re.search(r"#define " + P + r"_SLOT_WHOLE_START\b", text) is not None
if retry:
    acc = once(r"\n" + re.escape(pfx) + r"_accept: __attribute__\(\(unused\)\);\n", text)
    rs = ("(slot_values[" + P + "_SLOT_WHOLE_START] != PCREC_UNSET ? (size_t)slot_values["
          + P + "_SLOT_WHOLE_START] : ctx->pos)") if has_k else "ctx->pos"
    guard = ("    if (__builtin_expect(ctx->user == (void *)&" + pfx + "__ne_tag, 0)) {   /* twin: NOTEMPTY_ATSTART */\n"
             "        size_t ne_rs_ = " + rs + ";\n"
             "        if (ne_rs_ == scan_position && ne_rs_ == ctx->pos) goto " + pfx + "_fail;\n"
             "    }\n")
    text = text[:acc.end()] + guard + text[acc.end():]
    # the tag must be declared before the first anchored body
    first = once(r"\n#include \"[^\"]+\.h\"\n", text)
    text = text[:first.end()] + "static const char " + pfx + "__ne_tag;\n" + text[first.end():]

inc = once(r"\n#include \"[^\"]+\.h\"\n", text)
text = text[:inc.end()] + '#include "iter_abi.h"\n' + text[inc.end():]

body_link = ('static noinline (static label table)' if static_labels
             else ('static noinline (--shared)' if shared else 'always_inline'))
tail = f"""
/* ---- the iterator twin, revision 3 (findall_iter.md §1.2, §2.1, §2.3); body linkage: {body_link}; batch cell: {'fill' if fill else 'off'} ---- */
#if __has_attribute(noclone)
__attribute__((noclone))
#endif
int {pfx}_search({params})
{{
    return {pfx}__find(subject, subject_length, search_from, capture_spans);
}}

static inline __attribute__((always_inline)) size_t {pfx}__adv(const unsigned char *s, size_t n, size_t pos)
{{
{adv_body}
}}
"""
if retry:
    tail += f"""
static inline __attribute__((always_inline)) int {pfx}__retry(const unsigned char *s, size_t n, size_t q,
                                                             ptrdiff_t (*c)[2])
{{
    rx_ctx ctx;
    ctx.subject = s; ctx.len = n; ctx.pos = q; ctx.ncap = 0; ctx.caps = NULL;
    ctx.user = (void *)&{pfx}__ne_tag; ctx.vars = NULL; ctx.nvars = 0;
    ptrdiff_t len = {pfx}_match_caps(&ctx, c);
    return len >= 0 ? 1 : (len == -1 ? 0 : (int)len);
}}
"""
tail += f"""
/* STEP: 1 (a match in c, NCAPS pairs), 0 (done) or a code. Reads s, n, lo, flags. */
static inline __attribute__((always_inline)) int {pfx}__step(rx_iter *it, ptrdiff_t (*c)[2])
{{
    const unsigned char *s = it->s;
    size_t n = it->n;
    size_t lo = it->lo;
"""
if retry:
    tail += f"""    if (it->flags & RX_ITER_F_RETRY) {{       /* an empty match was reported at lo */
        it->flags &= ~RX_ITER_F_RETRY;
        int r = {pfx}__retry(s, n, lo, c);
        if (r < 0) return r;
        if (r == 1) goto matched;
        lo = {pfx}__adv(s, n, lo);
        it->lo = lo;
    }}
"""
tail += f"""    if (lo > n) return 0;
    {{
        int r = {pfx}__find(s, n, lo, c);
        if (r != 1) return r;                              /* it->lo stays the failing search's start */
    }}
"""
if retry:
    tail += "matched:\n"
tail += f"""    if (c[0][1] > c[0][0])
        it->lo = {pfx}__adv(s, n, (size_t)c[0][1] - 1);     /* K75: the aligned end */
"""
if retry:
    tail += f"""    else if ((size_t)c[0][0] < n) {{
        it->lo = (size_t)c[0][0];                          /* PCRE2: retry at the empty match */
        it->flags |= RX_ITER_F_RETRY;
    }} else
        it->lo = n + 1;
"""
else:
    tail += f"""    else
        it->lo = {pfx}__adv(s, n, (size_t)c[0][0]);         /* EMPTY: one character past its start */
"""
tail += f"""    return 1;
}}

/* End the iterator: rc and the sticky ENDED header (§1.2). */
static inline __attribute__((always_inline)) int {pfx}__end(rx_iter *it, int r)
{{
    it->rc = r;
    it->hdr = PCREC_ITER_ENDED;
    return 0;
}}

/* The slow path (§1.2): bind a FRESH iterator, or return 0 on ENDED, or refuse. */
static int {pfx}__enter(rx_iter *it)
{{
    uint32_t h = it->hdr;
    if (h == PCREC_ITER_ENDED) return 0;
    if ((h & ~0xF0u) != PCREC_ITER_FRESH) {{ it->rc = PCREC_ERR_ITER; it->hdr = PCREC_ITER_ENDED; return 0; }}
    /* 1. normalize every optional field (IT1); then K into nbatch */
    if (!(h & PCREC_ITER_OPT_AT)) it->lo = 0;
    if (!(h & PCREC_ITER_OPT_VARS)) {{ it->vars = NULL; it->nvars = 0; }}
    if (!(h & PCREC_ITER_OPT_IN)) it->bufs = NULL;
    if (!(h & PCREC_ITER_OPT_BATCH)) it->batch = NULL;
"""
if fill:
    tail += f"""    it->nbatch = (it->batch != NULL && it->nbatch / {P}_NCAPS >= 2) ? it->nbatch / {P}_NCAPS : 1;
"""
else:
    tail += """    it->nbatch = 1;                                    /* batch cell off: K forced to 1 */
"""
tail += f"""    /* 2. the run state */
    it->rc = 1; it->rc_next = 1; it->flags = 0; it->bhead = 0; it->bcount = 0;
    /* 3. the once-per-iterator checks: in the twin, __find's own prologue (header comment) */
    /* 4. BOUND, the option bits cleared */
    it->hdr = PCREC_ITER_BOUND;
    return 1;
}}
"""
if fill:
    tail += f"""
static inline __attribute__((always_inline)) int {pfx}__deliver(rx_iter *it, ptrdiff_t (*caps)[2])
{{
    ptrdiff_t (*e)[2] = it->batch + it->bhead * {P}_NCAPS;
    if (caps)
        for (size_t i = 0; i < {P}_NCAPS; i++) {{ caps[i][0] = e[i][0]; caps[i][1] = e[i][1]; }}
    it->bhead++;
    return 1;
}}

static inline __attribute__((always_inline)) int {pfx}__fill(rx_iter *it, ptrdiff_t (*caps)[2])
{{
    if (it->rc_next != 1)                                  /* IT2: a code is pending, the batch is drained */
        return {pfx}__end(it, it->rc_next);
    size_t K = it->nbatch;
    if (K == 1) {{
        ptrdiff_t local[{P}_NCAPS][2];
        int r = {pfx}__step(it, caps ? caps : local);
        return r == 1 ? 1 : {pfx}__end(it, r);
    }}
    ptrdiff_t (*b)[2] = it->batch;
    size_t i = 0;
    while (i < K) {{
        int r = {pfx}__step(it, b + i * {P}_NCAPS);
        if (r == 1) {{ i++; continue; }}
        it->rc_next = r;                                   /* 0 (done) or a code */
        break;
    }}
    it->bhead = 0; it->bcount = i;
    if (i > 0) return {pfx}__deliver(it, caps);
    return {pfx}__end(it, it->rc_next);
}}

#if __has_attribute(noclone)
__attribute__((noclone))
#endif
int {pfx}_next(rx_iter *it, ptrdiff_t (*caps)[2])
{{
    if (__builtin_expect(it->hdr != PCREC_ITER_BOUND, 0))
        if (!{pfx}__enter(it)) return 0;                  /* bind; or refuse; or ENDED */
    if (it->bhead < it->bcount)                            /* deliver a buffered match */
        return {pfx}__deliver(it, caps);
    return {pfx}__fill(it, caps);                          /* STEP once (K = 1) or up to K */
}}
"""
else:
    tail += f"""
#if __has_attribute(noclone)
__attribute__((noclone))
#endif
int {pfx}_next(rx_iter *it, ptrdiff_t (*caps)[2])
{{
    if (__builtin_expect(it->hdr != PCREC_ITER_BOUND, 0))
        if (!{pfx}__enter(it)) return 0;                  /* bind; or refuse; or ENDED */
    ptrdiff_t local[{P}_NCAPS][2];                         /* IT10: STEP always writes NCAPS pairs */
    int r = {pfx}__step(it, caps ? caps : local);
    return r == 1 ? 1 : {pfx}__end(it, r);
}}

#if __has_attribute(noclone)
__attribute__((noclone))
#endif
size_t {pfx}_next_n(rx_iter *it, ptrdiff_t (*out)[2], size_t k)
{{
    if (__builtin_expect(it->hdr != PCREC_ITER_BOUND, 0))
        if (!{pfx}__enter(it)) return 0;
    ptrdiff_t c[{P}_NCAPS][2];
    size_t got = 0;
    while (got < k) {{
        int r = {pfx}__step(it, c);
        if (r != 1) {{ {pfx}__end(it, r); break; }}
        out[got][0] = c[0][0];
        out[got][1] = c[0][1];
        got++;
    }}
    return got;
}}
"""
open(dst, "w", encoding="utf-8", errors="surrogateescape").write(text + tail)
