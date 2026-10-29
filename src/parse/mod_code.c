/* mod_code.c — modules `code-<lang>` ([INLINE-C] stage 2): embedded code in
 * a pattern, ``(?C`c: ...`)``, `code-c` in v1.
 *
 * Design: docs/design/inline_c.md §1.1 (one node, ownership as rows), §2
 * (the spellings, the tag grammar, the end rules, the errors), §3 (the
 * generated function this node becomes, src/gen/emit_dfa.c) and §5 (the
 * trust gate). Contract: docs/spec/match_api.md §11.9.
 *
 * WHAT A CODE SEGMENT IS, in one sentence: an ordinary callout site (the
 * same A_CALLOUT node, the same call site, the same return table, firing
 * class and `once` rule as module `callouts`' sites) whose callee pcrec
 * writes itself, from the segment's text, as a file-local function of the
 * artifact; the site calls it through a file-local `rx_callout_ref`, the ONE
 * call form every binding row uses (Frank 2026-10-27).
 *
 * THE SPELLING reaches the port through one registry row per language,
 * GENERATED from src/parse/codelang.def (src/parse/registry.c): the tagged
 * `(?C` string (PCRE2's own spelling, a string callout to PCRE2), `lang
 * attrs ":"` then the code, with PCRE2's end rule exactly (the string ends
 * at the first lone closing delimiter, a doubled one is one byte, §2.3), so
 * the same bytes mean the same pattern to both programs. The `(?{ ... })`
 * spelling, whose end needs a lexer, is row [SCANNER-DOGFOOD]'s (ruling R1,
 * 2026-10-27). The text is OPAQUE beyond finding its end: pcrec never
 * parses, checks or rewrites the user's code (Q7: no `$1` substitution,
 * generated names only).
 *
 * THE GATE IS THE ROWS' RF_INVOKER_ONLY column (§5.1): the port runs only
 * when the invoker granted the language (`--allow-code`,
 * `pcrec_options.allow_code`); a `features` text cannot. The port itself
 * refuses the one trust row it can see at parse time, REACHED code (§5.4
 * row 3): a segment inside a definition the composer read from another file
 * is refused before pins (stage 3). */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"
#include "enc/enc.h"   /* pcrec_utf8_decode: the segment is UTF-8 to gcc */

/* THE LANGUAGE ROWS, projected from src/parse/codelang.def in its order. */
static const PcrecCodeLang code_langs[] = {
#define PCREC_CODE_LANG(id, tag, feat, mod) { (tag), (feat), (mod) },
#include "parse/codelang.def"
#undef PCREC_CODE_LANG
};

const PcrecCodeLang *pcrec_code_langs(size_t *n)
{
    *n = sizeof code_langs / sizeof code_langs[0];
    return code_langs;
}

/* THE DESCRIBE GRANT (inline_c.md §5.9's second class; review
 * 2026-10-27-r1-ic2 F8): a describe entry parses code to describe the
 * pattern and writes no C, so it opens EVERY registered language whatever
 * the caller's grant says (unset, "" or a list alike: one fact, one
 * answer). Two spellings of that one rule, side by side here and nowhere
 * else: this tag list, which the string-grant entries (`--emit-ir`,
 * `--emit-facts`) put in their options, and the module mask below, which the
 * mask entries (`--count-groups`, the registry's `built` probe) OR in. */
const char *pcrec_code_describe_grant(void)
{
    static const char all[] = ""
#define PCREC_CODE_LANG(id, tag, feat, mod) "," tag
#include "parse/codelang.def"
#undef PCREC_CODE_LANG
        ;
    return all[0] ? all + 1 : all;
}

/* Every registered language's module bit: THE DESCRIBE GRANT above, as the
 * mask the mask entries open. */
unsigned pcrec_code_describe_mask(void)
{
    unsigned m = 0;
    for (size_t i = 0; i < sizeof code_langs / sizeof code_langs[0]; i++)
        m |= code_langs[i].feature;
    return m;
}

/* THE `code-header` OPERAND (inline_c.md §3.3), one reader for the `.rxt`
 * head line and `--code-header`: `lang` a registered language and `hdr` an
 * `#include` operand, `"name"` or `<name>`, of printable ASCII with no
 * closing delimiter, backslash or newline inside (pcrec emits it AS WRITTEN
 * and never opens it, so the one thing it checks is that the line it writes
 * is one well-formed `#include`). NULL when well formed, else the reason. */
const char *pcrec_code_header_check(const char *lang, const char *hdr)
{
    if (!pcrec_code_lang_by_tag(lang, strlen(lang)))
        return "unknown code language";
    const size_t n = strlen(hdr);
    const char close = n && hdr[0] == '"' ? '"' : n && hdr[0] == '<' ? '>' : 0;
    if (!close || n < 3 || hdr[n - 1] != close)
        return "a header is \"name\" or <name>";
    for (size_t i = 1; i + 1 < n; i++)
        if (hdr[i] == close || hdr[i] == '\\' || hdr[i] < 0x20 || hdr[i] > 0x7e)
            return "a header name is printable ASCII with no backslash or "
                   "closing delimiter";
    return NULL;
}

/* The language whose module owns `feature`, or NULL. */
/* The language row whose tag is the `len` bytes at `tag`, or NULL: the ONE
 * lookup by tag (the `code-header` check, the grant resolver, the compile's
 * header gate; review 2026-10-27-r1-ic2 F32). */
const PcrecCodeLang *pcrec_code_lang_by_tag(const char *tag, size_t len)
{
    for (size_t i = 0; i < sizeof code_langs / sizeof code_langs[0]; i++)
        if (strlen(code_langs[i].tag) == len &&
            !memcmp(code_langs[i].tag, tag, len))
            return &code_langs[i];
    return NULL;
}

const PcrecCodeLang *pcrec_code_lang_by_feature(unsigned feature)
{
    for (size_t i = 0; i < sizeof code_langs / sizeof code_langs[0]; i++)
        if (code_langs[i].feature == feature) return &code_langs[i];
    return NULL;
}

/* THE REFUSED CHARACTERS (§2.4, [r1 T4]; the CVE-2021-42574 shape, review
 * 2026-10-27-r1-ic2 F1/F2/F35): every character that makes the code a
 * reviewer reads differ from the code gcc compiles, ONE first-match table.
 * A row is a UCD property (the vendored data's own set, through the table
 * `make gen-tables` generates, src/parse/uprops_tables.inc) or a code-point
 * range, with what the diagnostic calls it. The segment is C source, which
 * gcc reads as UTF-8 whatever the pattern's encoding, so the scan decodes
 * UTF-8; a byte that starts no well-formed character is not a character to
 * a renderer or to gcc's identifier reader and is left as it is. A carriage
 * return is refused unless a line feed follows it (gcc ends a line at a lone
 * CR; a terminal overwrites the line), which is a rule on two bytes and so
 * sits beside the table. */
#define PROP(n)     { (n), 0, 0 }
#define RANGE(a, b) { NULL, (a), (b) }
static const struct { PcrecSetTerm t; const char *what; } code_refused[] = {
    { PROP("BIDICONTROL"),               "a bidirectional control (Bidi_Control)" },
    { PROP("DEFAULTIGNORABLECODEPOINT"), "an invisible character (Default_Ignorable_Code_Point)" },
    { RANGE(0x85, 0x85),                 "a Unicode line end gcc does not end a line at" },
    { RANGE(0x2028, 0x2029),             "a Unicode line end gcc does not end a line at" },
    { RANGE(0x00, 0x08),                 "a control character" },
    { RANGE(0x0B, 0x0C),                 "a vertical tab or form feed (a line break to a terminal, not to gcc)" },
    { RANGE(0x0E, 0x1F),                 "a control character" },
    { RANGE(0x7F, 0x7F),                 "a control character" },
};
#undef PROP
#undef RANGE

/* Is `cp` in the sorted interval list iv[0..n)? */
static bool code_span_has(const PcrecCpRange *iv, int n, unsigned cp)
{
    int lo = 0, hi = n;
    while (lo < hi) {
        const int mid = lo + (hi - lo) / 2;
        if (cp < iv[mid].lo) hi = mid;
        else if (cp > iv[mid].hi) lo = mid + 1;
        else return true;
    }
    return false;
}

/* What the table calls `cp`, or NULL when a segment may carry it. */
static const char *code_refused_what(Ctx *cx, size_t at, unsigned cp)
{
    for (size_t k = 0; k < sizeof code_refused / sizeof code_refused[0]; k++) {
        const PcrecSetTerm *t = &code_refused[k].t;
        if (!t->prop) {
            if (cp >= t->lo && cp <= t->hi) return code_refused[k].what;
            continue;
        }
        int n = 0;
        const PcrecCpRange *iv = pcrec_uprops_span(t->prop, &n);
        if (!iv)
            pcrec_ctx_fail(cx, at, "internal error: the code refusal table "
                           "names property '%s', which unicode-props does "
                           "not ship", t->prop);
        if (code_span_has(iv, n, cp)) return code_refused[k].what;
    }
    return NULL;
}

/* The first refused character of the decoded segment `s` (n bytes): what
 * it is (the table above, or a lone carriage return), its code point in
 * `*cp` and its byte offset in `*off`; NULL when there is none. */
static const char *code_find_refused(Ctx *cx, size_t at, const char *s,
                                     size_t n, unsigned *cp, size_t *off)
{
    const unsigned char *u = (const unsigned char *)s;
    for (size_t i = 0; i < n;) {
        unsigned c = u[i];
        int len = 1;
        if (u[i] >= 0x80 &&
            pcrec_utf8_decode(u, n, i, &c, &len) != PCREC_UTF8_OK) {
            i++;
            continue;
        }
        const char *what = code_refused_what(cx, at, c);
        if (!what && c == '\r' && !(i + 1 < n && u[i + 1] == '\n'))
            what = "a carriage return with no line feed after it (a line end "
                   "to gcc, an overwritten line to a terminal)";
        if (what) {
            *cp = c;
            *off = i;
            return what;
        }
        i += (size_t)len;
    }
    return NULL;
}

/* Reads the code TAG at `s` (n bytes) for language `L`: applies its
 * attribute list to `a` and returns the offset of the code's first byte (one
 * past the `:`), or 0 when `s` opens with no tag of `L`'s. A refused
 * attribute list returns SIZE_MAX with the reason in `*why`. */
static size_t code_tag(Ctx *cx, Ast *a, const PcrecCodeLang *L,
                       const char *s, size_t n, const char **why)
{
    const size_t colon = pcrec_code_tag_extent_scan(s, n, L->tag);
    if (!colon) return 0;
    const size_t tl = strlen(L->tag);
    if (colon > tl) {
        *why = pcrec_callout_attrs(cx, a, s + tl + 1, colon - tl - 1, ',');
        if (*why) return SIZE_MAX;
    }
    return colon + 1;
}

ExtResult pcrec_codeport(Ctx *cx, const RegRow *rw, ExtWant want, size_t at,
                         size_t from)
{
    const char *p = cx->pat;
    const PcrecCodeLang *L = pcrec_code_lang_by_feature(rw->feature);
    if (!L)
        REFUSE(at, "internal error: a code row whose module is in no "
               "language row");

    Ast *a = pcrec_ast_node(cx, A_CALLOUT);
    a->not_repeatable = true;
    a->u.callout.at = at;
    a->u.callout.bind = CO_CODE;
    a->u.callout.lang = L->tag;

    const char *why = NULL;
    /* ``(?C`c,attrs: code`)``: the recogniser that elected this row ran the
     * same two scans on the same text. */
    PcrecCoScan sc;
    if (from >= cx->patlen ||
        !pcrec_callout_extent_scan(p + from, cx->patlen - from, &sc) ||
        !sc.string)
        REFUSE(at, "internal error: the tagged-code row was elected for a "
               "text that is not a (?C string");
    const char *raw = p + from + sc.str;
    const size_t c0 = code_tag(cx, a, L, raw, sc.rawlen, &why);
    if (c0 == SIZE_MAX) REFUSE(at, "%s", why);
    if (c0 == 0)
        REFUSE(at, "internal error: the tagged-code row was elected for a "
               "string with no '%s:' tag", L->tag);
    const char *code = raw + c0;
    const size_t codelen = sc.rawlen - c0;
    /* Decode: a doubled closing delimiter is one literal byte (PCRE2's
     * rule, §2.3); the decoded text is what gcc compiles. */
    char *text = pcrec_arena_alloc(&cx->arena, codelen + 1);
    bool exact;
    const size_t textlen = pcrec_callout_string_decode(code, codelen, sc.close,
                                                       text, &exact);

    unsigned cp;
    size_t off;
    const char *what = code_find_refused(cx, at, text, textlen, &cp, &off);
    if (what)
        REFUSE(at, "the code segment at offset %zu contains U+%04X, %s, at "
               "byte %zu of the segment; such characters make the code a "
               "reviewer reads differ from what the compiler compiles", at,
               cp, what, off);

    /* §5.4 row 3: REACHED code (a definition read from another file through
     * a `lib` line) is refused until pins exist (stage 3). */
    if (cx->code_def && cx->defs && cx->defs->file &&
        cx->code_def->file != cx->defs->file->path)
        REFUSE(at, "embedded code at %s:%zu is not allowed: code from "
               "included files needs pinned include lines (not in this "
               "build)", cx->code_def->file, cx->code_def->line);

    a->u.callout.text = text;
    a->u.callout.textlen = textlen;
    a->u.callout.code_at = (size_t)(code - p);
    a->u.callout.code_exact = exact;
    a->u.callout.seg = ++cx->ncodesegs;
    pcrec_ast_stamp(a, rw, at);
    cx->ncallouts++;

    ExtResult res = { .what = EXT_NODE, .at = at, .msg = "",
                      .answered_at = want };
    res.node = a;
    res.end = from + sc.end;
    return res;
}
