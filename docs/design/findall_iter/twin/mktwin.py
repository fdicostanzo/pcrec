#!/usr/bin/env python3
# docs/design/findall_iter/twin/mktwin.py — lane iterdes, [FINDALL-NEXT] HAND TWIN.
#
# Mechanical transform of a pcrec-emitted artifact (.c, split form with its .h)
# into the iterator shape findall_iter.md §2 proposes, so the design's codegen and
# answer claims can be checked on REAL artifacts before any emitter change:
#
#   1. the exported `<p>_search` definition is renamed `<p>__find` and made
#      `static inline __attribute__((always_inline))` (the one search body);
#   2. a thin exported `<p>_search` is re-added AFTER it (same noclone attribute
#      the emitter puts on the DFA entry, K24), calling the body;
#   3. `<p>__adv`, a static inline copy of the artifact's own `<p>_next_pos` body
#      (the encoding residual; byte or utf8 read off the artifact);
#   4. `<p>__step` (one find-all step: the RETRY arm, the search from lo, the
#      K75/empty advance), `<p>_next` and `<p>_next_n` sharing it;
#   5. with --retry, the VM artifact's accept label gains the NOTEMPTY_ATSTART
#      guard and `<p>__retry` runs the anchored caps entry with it armed (the
#      twin carries the flag in ctx->user, which no twin pattern uses; the design
#      carries it in the run state, §3.3).
#
# The transform asserts every anchor it rewrites is found exactly once; a miss is
# a hard error, never a silent no-op.
#
# usage: python3 -I mktwin.py PREFIX IN.c OUT.c [--retry] [--shared]
import re
import sys

pfx, src, dst = sys.argv[1], sys.argv[2], sys.argv[3]
retry = "--retry" in sys.argv[4:]
shared = "--shared" in sys.argv[4:]   # the size alternative: ONE noinline body for every entry
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

# 5. the NOTEMPTY_ATSTART guard at the VM accept label
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

tail = f"""
/* ---- the iterator twin (findall_iter.md §2); body linkage: {'static noinline (static label table)' if static_labels else ('static noinline (--shared)' if shared else 'always_inline')} ---- */
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
/* One find-all step: 1 (a match in c), 0 (done) or a code. */
static inline __attribute__((always_inline)) int {pfx}__step(rx_iter *it, const unsigned char *s, size_t n,
                                                            ptrdiff_t (*c)[2])
{{
    size_t lo = it->lo;
"""
if retry:
    tail += f"""    if (it->flags & RX_ITER_F_RETRY) {{       /* an empty match was reported at lo */
        it->flags &= ~RX_ITER_F_RETRY;
        int r = {pfx}__retry(s, n, lo, c);
        if (r < 0) return r;
        if (r == 1) goto matched;
        lo = {pfx}__adv(s, n, lo);
    }}
"""
tail += f"""    if (lo > n) return 0;
    {{
        int r = {pfx}__find(s, n, lo, c);
        if (r != 1) return r;
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

/* The per-call prologue: bind on the first call, refuse a foreign or misbound one. */
static inline __attribute__((always_inline)) int {pfx}__enter(rx_iter *it, const unsigned char *s, size_t n)
{{
    if (__builtin_expect(it->hdr == PCREC_ITER_BOUND, 1)) {{
        if (__builtin_expect((((uintptr_t)it->s ^ (uintptr_t)s) | (it->n ^ n)
                              | ((uintptr_t)it->owner ^ (uintptr_t)&{pfx}_info)) != 0, 0)) {{
            it->rc = PCREC_ERR_ITER;
            return 0;
        }}
        return it->rc == 1;
    }}
    if (it->hdr == PCREC_ITER_FRESH) it->lo = 0;
    else if (it->hdr != PCREC_ITER_FRESH_AT) {{ it->rc = PCREC_ERR_ITER; return 0; }}
    it->hdr = PCREC_ITER_BOUND; it->rc = 1; it->flags = 0;
    it->s = s; it->n = n; it->owner = &{pfx}_info; it->vars = NULL; it->nvars = 0;
    return 1;
}}

#if __has_attribute(noclone)
__attribute__((noclone))
#endif
int {pfx}_next(rx_iter *it, const unsigned char *s, size_t n, ptrdiff_t (*caps)[2])
{{
    if (!{pfx}__enter(it, s, n)) return 0;
    ptrdiff_t local[{P}_NCAPS][2];
    int r = {pfx}__step(it, s, n, caps ? caps : local);
    if (r == 1) return 1;
    it->rc = r;
    return 0;
}}

#if __has_attribute(noclone)
__attribute__((noclone))
#endif
size_t {pfx}_next_n(rx_iter *it, const unsigned char *s, size_t n, ptrdiff_t (*out)[2], size_t k)
{{
    if (!{pfx}__enter(it, s, n)) return 0;
    ptrdiff_t c[{P}_NCAPS][2];
    size_t got = 0;
    while (got < k) {{
        int r = {pfx}__step(it, s, n, c);
        if (r != 1) {{ it->rc = r; break; }}
        out[got][0] = c[0][0];
        out[got][1] = c[0][1];
        got++;
    }}
    return got;
}}
"""
open(dst, "w", encoding="utf-8", errors="surrogateescape").write(text + tail)
