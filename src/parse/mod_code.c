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

/* Every registered language's tag, comma-separated ("c"): the grant the
 * DESCRIBE modes take (`--emit-ir`, `--emit-facts`, `--count-groups`;
 * inline_c.md §5.9's second class), which parse code to describe the
 * pattern and write no C. */
const char *pcrec_code_all_langs(void)
{
    static const char all[] = ""
#define PCREC_CODE_LANG(id, tag, feat, mod) "," tag
#include "parse/codelang.def"
#undef PCREC_CODE_LANG
        ;
    return all[0] ? all + 1 : all;
}

/* Every registered language's module bit: the grant a DESCRIBE entry
 * (inline_c.md §5.9's second class: `--count-groups`, the registry's
 * `built` probe) opens, since it parses code and writes no C. */
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
    size_t nl, k = 0;
    const PcrecCodeLang *L = pcrec_code_langs(&nl);
    while (k < nl && strcmp(L[k].tag, lang)) k++;
    if (k == nl) return "unknown code language";
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
const PcrecCodeLang *pcrec_code_lang_by_feature(unsigned feature)
{
    for (size_t i = 0; i < sizeof code_langs / sizeof code_langs[0]; i++)
        if (code_langs[i].feature == feature) return &code_langs[i];
    return NULL;
}

/* THE BIDI AND INVISIBLE-FORMAT REFUSAL (§2.4, [r1 T4]; the CVE-2021-42574
 * shape): the code points a reviewer cannot see but gcc compiles. Each row
 * is a UTF-8 lead pair and the range of the third byte, so the check is a
 * table read over the segment's bytes, whatever the pattern's encoding (the
 * segment is C source, which gcc reads as UTF-8). */
static const struct {
    unsigned char b0, b1, lo, hi;   /* third byte in [lo, hi] */
    unsigned      cp_lo;            /* the code point of `lo` */
} code_invisible[] = {
    { 0xE2, 0x80, 0x8B, 0x8F, 0x200B },   /* U+200B..U+200F ZWSP, ZWNJ, ZWJ, LRM, RLM */
    { 0xE2, 0x80, 0xAA, 0xAE, 0x202A },   /* U+202A..U+202E LRE, RLE, PDF, LRO, RLO */
    { 0xE2, 0x81, 0xA0, 0xA4, 0x2060 },   /* U+2060..U+2064 WJ and invisible operators */
    { 0xE2, 0x81, 0xA6, 0xA9, 0x2066 },   /* U+2066..U+2069 LRI, RLI, FSI, PDI */
    { 0xEF, 0xBB, 0xBF, 0xBF, 0xFEFF },   /* U+FEFF ZWNBSP (BOM) */
};

/* The first invisible or bidi control in `s` (n bytes): its code point in
 * `*cp` and its byte offset in `*off`; false when there is none. */
static bool code_find_invisible(const char *s, size_t n, unsigned *cp,
                                size_t *off)
{
    const unsigned char *u = (const unsigned char *)s;
    for (size_t i = 0; i + 2 < n; i++)
        for (size_t k = 0; k < sizeof code_invisible / sizeof code_invisible[0]; k++)
            if (u[i] == code_invisible[k].b0 && u[i + 1] == code_invisible[k].b1 &&
                u[i + 2] >= code_invisible[k].lo && u[i + 2] <= code_invisible[k].hi) {
                *cp = code_invisible[k].cp_lo + (unsigned)(u[i + 2] - code_invisible[k].lo);
                *off = i;
                return true;
            }
    return false;
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
    size_t textlen = 0;
    bool exact = true;
    for (size_t i = 0; i < codelen; i++) {
        text[textlen++] = code[i];
        if (code[i] == sc.close) { i++; exact = false; }
    }
    text[textlen] = 0;

    unsigned cp;
    size_t off;
    if (code_find_invisible(text, textlen, &cp, &off))
        REFUSE(at, "the code segment at offset %zu contains U+%04X, an "
               "invisible or bidirectional control character, at byte %zu "
               "of the segment; such characters make the code a reviewer "
               "reads differ from what the compiler compiles", at, cp, off);

    /* A C0 control byte other than C's whitespace has no place in source
     * text, and \x01 is the emitter's own placeholder lead (K79), which a
     * segment must never carry into the artifact. */
    for (size_t i = 0; i < textlen; i++) {
        const unsigned char b = (unsigned char)text[i];
        if ((b < 0x20 && b != '\t' && b != '\n' && b != '\v' && b != '\f' &&
             b != '\r') || b == 0x7f)
            REFUSE(at, "the code segment at offset %zu contains the control "
                   "byte 0x%02X at byte %zu of the segment", at, b, i);
    }

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
