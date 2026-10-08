/* The ENCODING REGISTRY ([M5-SEAM], D58) — the one table the encoding
 * namespace is defined by, plus the prefix substitution every backend's text
 * goes through. See enc.h for the seam's contract and the third-encoding
 * recipe.
 *
 * The table carries a row for every member of the namespace, INCLUDING one
 * with no backend yet (`decls == NULL`). That is deliberate: a name pcrec
 * knows but cannot compile must be refused by NAME rather than fall out of a
 * lookup as "unknown", and the refusal in src/core/compile.c reads the row's
 * own `name` string rather than a literal of its own. [SR-10]'s motivating
 * instance was exactly this pair of hand-written strings (compile.c's
 * diagnostic and cli/main.c's name mapping) drifting apart. */
#include <string.h>

#include "enc/enc.h"

/* [M5.0 stage 2] The `utf8` row stopped being the PENDING one this table
 * carried from [M5-SEAM] through stage 1 (a name with `entries == NULL`,
 * refused by `pcrec_enc_ready`) and became a real backend — enc_utf8.c, the
 * third-encoding recipe's first execution: one new file in this directory,
 * one extern in enc.h, this one row. */
static const PcrecEnc *const enc_table[] = {
    &pcrec_enc_backend_byte,
    &pcrec_enc_backend_utf8
};

/* The encoding row whose id matches `id`, or NULL. */
const PcrecEnc *pcrec_enc_by_id(int id)
{
    for (size_t i = 0; i < sizeof enc_table / sizeof *enc_table; i++)
        if (enc_table[i]->id == id) return enc_table[i];
    return NULL;
}

/* The encoding row named `name` (exact match), or NULL. */
const PcrecEnc *pcrec_enc_by_name(const char *name)
{
    if (!name) return NULL;
    for (size_t i = 0; i < sizeof enc_table / sizeof *enc_table; i++)
        if (!strcmp(enc_table[i]->name, name)) return enc_table[i];
    return NULL;
}

/* Renders the comma-separated encoding-name menu into buf/cap (an ordered
 * PREFIX, never a gap or a dangling separator -- see the comment above for the
 * two ways this loop used to lie and are now gone), rendered from enc_table so
 * a new row can never leave a diagnostic listing a stale menu. */
void pcrec_enc_names(char *buf, size_t cap)
{
    /* Rendered from the table above rather than written out, so a new row
     * cannot leave a diagnostic listing a stale menu.
     *
     * [REVW.1] wave 1, L10-2: ONE OVER-LONG POLICY, AN ORDERED PREFIX, THE
     * SAME ONE `render_modules` (src/parse/enabled.c) STATES — read that
     * function's comment for the measurement and for why neither of the two
     * bounded joins in this tree reaches the kit's `pcrec_sb_join`. This loop had
     * TWO ways to lie rather than one: a name that did not fit was skipped
     * while LATER ones were still appended, and the separator was written
     * under a DIFFERENT bound from the name, so a cap between the two glued
     * `byte` and `utf8` into one word. Both are unreachable today (the menu
     * is 10 bytes and both callers pass 128), and both are gone. */
    size_t k = 0;
    if (!cap) return;
    for (size_t i = 0; i < sizeof enc_table / sizeof *enc_table; i++) {
        const char *n = enc_table[i]->name;
        size_t ln = strlen(n) + (k ? 2 : 0);
        if (k + ln + 1 > cap) break;        /* an ordered PREFIX, never a gap */
        if (k) { buf[k++] = ','; buf[k++] = ' '; }
        memcpy(buf + k, n, strlen(n));
        k += strlen(n);
    }
    buf[k] = 0;
}

/* Closes `mask` over every present entry's `requires` until nothing new is
 * added: the set of entries an artifact must carry, given the ones its
 * engine calls. */
unsigned pcrec_enc_mask_close(const PcrecEnc *e, unsigned mask)
{
    if (!e || !e->entries) return mask;
    for (;;) {
        unsigned m = mask;
        for (const PcrecEncEntry *t = e->entries; t->decls; t++)
            if (m & t->id) m |= t->requires;
        if (m == mask) return mask;
        mask = m;
    }
}

/* [M6.5.2] THE TWO EMITTERS, one loop each over the backend's entries.
 *
 * A backend with no table emits nothing, which is what keeps the `-e utf8`
 * refusal path from ever reaching here; `emit_residual_*` in
 * src/gen/emit_dfa.c checks `pcrec_enc_ready` first anyway, because a NULL
 * text pointer reaching this far would otherwise emit a TRUNCATED artifact
 * instead of failing. */
void pcrec_enc_emit_decls(StrBuf *sb, const PcrecEnc *e, unsigned mask,
                          const char *prefix)
{
    if (!e || !e->entries) return;
    mask = pcrec_enc_mask_close(e, mask);
    for (const PcrecEncEntry *t = e->entries; t->decls; t++)
        if (mask & t->id) {
            /* [EMIT-VERB] the entry's doc half, through the render gate. */
            if (t->decls_doc) {
                pcrec_sb_cmt_open(sb, PCREC_CMT_NONESSENTIAL);
                pcrec_enc_emit_text(sb, t->decls_doc, prefix);
                pcrec_sb_cmt_close(sb);
            }
            pcrec_enc_emit_text(sb, t->decls, prefix);
        }
}

/* [K94] The fold table the UCP caseless span compare's body searches: one
 * `{byte, representative}` row per Latin-1 byte whose fold class has a lesser
 * member, sorted by byte. GENERATED FROM fold.c's own links at emit time, so
 * the match-time fold and the --ucp class fold are one definition. The brace
 * is on its own line for the DD12a(i) brace-matching excision, as utf8's
 * table's is. */
static void enc_emit_latin1_fold_table(StrBuf *sb, const char *prefix)
{
    int col = 0;
    pcrec_sb_cmt_open(sb, PCREC_CMT_NONESSENTIAL);
    pcrec_sb_puts(sb, "/* THE LATIN-1 FOLD MAP, sorted by byte: {from, to}, where `to` is\n"
                      " * the least member of from's fold class within Latin-1; only\n"
                      " * the non-identity entries are here. */\n");
    pcrec_sb_cmt_close(sb);
    pcrec_sb_printf(sb, "static const unsigned char %s_span_ci_fold_pairs[][2] =\n{\n",
                    prefix);
    for (unsigned c = 0; c < 256; c++) {
        unsigned r = pcrec_fold_latin1_rep(c);
        if (r == c) continue;
        pcrec_sb_printf(sb, "%s{0x%02X,0x%02X},", col ? " " : "    ", c, r);
        if (++col == 6) { pcrec_sb_putc(sb, '\n'); col = 0; }
    }
    pcrec_sb_puts(sb, col ? "\n};\n\n" : "};\n\n");
}

/* Emits every entry's `defs` text (and, gated through the comment layer, its
 * defs_doc) whose id is set in the CLOSED `mask` and whose `inline_def` is
 * `inline_half` -- pcrec_enc_emit_decls' own sibling loop over the
 * DEFINITIONS half. A backend with no table emits nothing. */
static void enc_emit_defs(StrBuf *sb, const PcrecEnc *e, unsigned mask,
                          const char *prefix, bool inline_half)
{
    if (!e || !e->entries) return;
    mask = pcrec_enc_mask_close(e, mask);
    for (const PcrecEncEntry *t = e->entries; t->decls; t++)
        if ((mask & t->id) && t->inline_def == inline_half) {
            if (t->id == PCREC_ENCE_SPAN_CASELESS_UCP)
                enc_emit_latin1_fold_table(sb, prefix);
            if (t->defs_doc) {
                pcrec_sb_cmt_open(sb, PCREC_CMT_NONESSENTIAL);
                pcrec_enc_emit_text(sb, t->defs_doc, prefix);
                pcrec_sb_cmt_close(sb);
            }
            pcrec_enc_emit_text(sb, t->defs, prefix);
        }
}

/* The out-of-line entries' definitions (the artifact's epilogue). */
void pcrec_enc_emit_defs(StrBuf *sb, const PcrecEnc *e, unsigned mask,
                         const char *prefix)
{
    enc_emit_defs(sb, e, mask, prefix, false);
}

/* The `static inline` entries' definitions, placed by the caller ahead of
 * every engine body that calls them. */
void pcrec_enc_emit_inline_defs(StrBuf *sb, const PcrecEnc *e, unsigned mask,
                                const char *prefix)
{
    enc_emit_defs(sb, e, mask, prefix, true);
}

/* True iff entry `id` in `e`'s table is marked engine_callable; false for an
 * unknown id or a backend with no table. */
bool pcrec_enc_entry_engine_callable(const PcrecEnc *e, unsigned id)
{
    if (!e || !e->entries) return false;
    for (const PcrecEncEntry *t = e->entries; t->decls; t++)
        if (t->id == id) return t->engine_callable;
    return false;
}

/* True iff entry `id` is present in `e`'s table at all, whatever its other
 * columns say. False for a backend with no table. */
bool pcrec_enc_has_entry(const PcrecEnc *e, unsigned id)
{
    if (!e || !e->entries) return false;
    for (const PcrecEncEntry *t = e->entries; t->decls; t++)
        if (t->id == id) return true;
    return false;
}

/* [ART-POSS-ARMS] The fold relation `e`'s caseless span compare folds by for
 * a construct with `ucp` in force: the Latin-1 relation when the table
 * carries the UCP entry (its definitions are generated from it), the
 * encoding's own otherwise — the entry choice `vm_caseless_entry` makes,
 * asked for the relation instead of the entry. */
const PcrecFold *pcrec_enc_span_fold(const PcrecEnc *e, bool ucp)
{
    return ucp && pcrec_enc_has_entry(e, PCREC_ENCE_SPAN_CASELESS_UCP)
        ? &pcrec_fold_latin1 : e->fold;
}

/* Emits `text` verbatim, substituting `prefix` for every `$` -- the ONE
 * templating rule every backend's decls/defs/advance text shares. */
void pcrec_enc_emit_text(StrBuf *sb, const char *text, const char *prefix)
{
    for (const char *q = text; *q; q++) {
        if (*q == '$') pcrec_sb_puts(sb, prefix);
        else           pcrec_sb_putc(sb, *q);
    }
}

/* [K49] Append `s` at `*len`, tracking overflow rather than truncating into a
 * plausible-looking half statement. */
static void adv_put(char *buf, size_t cap, size_t *len, const char *s)
{
    size_t k = strlen(s);
    if (*len + k < cap) memcpy(buf + *len, s, k);
    *len += k;
}

/* Renders the encoding's own `advance` template into buf/cap, substituting the
 * three @P/@S/@N tokens for posvar/subjvar/lenvar and `indent` at the start of
 * every line, tracking overflow (adv_put) rather than truncating; a bare `@`
 * not followed by one of those three is a defect in the backend's own text,
 * answered as an internal-error false rather than passed through. Returns
 * false on cap==0, no `advance` template, an unknown token, or overflow. */
bool pcrec_enc_advance(const PcrecEnc *e, char *buf, size_t cap,
                       const char *indent, const char *posvar,
                       const char *subjvar, const char *lenvar)
{
    size_t len = 0;
    bool at_line_start = true;

    if (cap == 0) return false;
    if (!e || !e->advance) return false;

    for (const char *q = e->advance; *q; q++) {
        if (at_line_start) { adv_put(buf, cap, &len, indent); at_line_start = false; }
        if (*q == '@') {
            /* The three tokens enc.h documents. An `@` before anything else —
             * including at the very end of the text — is a defect in a
             * backend's own text, not a character to pass through: emitted C
             * has no use for a bare `@`, so answering false turns a typo into
             * an internal error at the call site rather than into an artifact
             * that does not compile. */
            switch (q[1]) {
                case 'P': adv_put(buf, cap, &len, posvar);  q++; continue;
                case 'S': adv_put(buf, cap, &len, subjvar); q++; continue;
                case 'N': adv_put(buf, cap, &len, lenvar);  q++; continue;
                default:  return false;
            }
        }
        if (len + 1 < cap) buf[len] = *q;
        len++;
        if (*q == '\n') at_line_start = true;
    }
    if (len >= cap) return false;
    buf[len] = '\0';
    return true;
}

/* [K50] The start guard. Shares `adv_put`'s overflow discipline and the same
 * three tokens; it does NOT share the indentation rule, because the text is
 * one expression spliced into an `if` rather than a statement list.
 *
 * TWO FALSE OUTCOMES, KEPT APART. "This backend has no restriction" is the
 * common, correct answer (`byte`) and the caller emits nothing; "the text did
 * not fit" is an internal error the caller must raise. Returning false for
 * both and letting the caller guess is how the second one would ship as the
 * first — so `*truncated` carries the difference, and it is written on every
 * path rather than only on the failing one. */
bool pcrec_enc_start_guard(const PcrecEnc *e, char *buf, size_t cap,
                           const char *posvar, const char *subjvar,
                           const char *lenvar, bool *truncated)
{
    size_t len = 0;

    *truncated = false;
    if (cap == 0) { *truncated = true; return false; }
    buf[0] = '\0';
    if (!e || !e->start_guard) return false;

    for (const char *q = e->start_guard; *q; q++) {
        if (*q == '@') {
            switch (q[1]) {
                case 'P': adv_put(buf, cap, &len, posvar);  q++; continue;
                case 'S': adv_put(buf, cap, &len, subjvar); q++; continue;
                case 'N': adv_put(buf, cap, &len, lenvar);  q++; continue;
                default:  *truncated = true; return false;
            }
        }
        if (len + 1 < cap) buf[len] = *q;
        len++;
    }
    if (len >= cap) { *truncated = true; return false; }
    buf[len] = '\0';
    return true;
}

/* [K50] The partition precondition enc.h's `start_cls` comment states. A
 * backend with no restriction passes trivially — there is no set to check. */
bool pcrec_enc_start_cls_ok(const PcrecEnc *e)
{
    if (!e || !e->start_cls) return true;
    for (int c = 0; c < 256; c++) {
        if (cls_has(e->start_cls, (unsigned)c)) continue;
        if (cls_has(pcrec_cls_word_esc, (unsigned)c)) return false;
        if (cls_has(pcrec_cls_newline,  (unsigned)c)) return false;
    }
    return true;
}

/* The one compile-time UTF-8 encoder (enc.h). It lives here, not in
 * enc_utf8.c, because that file is artifact TEXT and this is compiler code. */
int pcrec_utf8_encode(unsigned cp, unsigned char b[4])
{
    if (cp <= 0x7F)   { b[0] = (unsigned char)cp; return 1; }
    if (cp <= 0x7FF)  { b[0] = (unsigned char)(0xC0 | (cp >> 6));
                        b[1] = (unsigned char)(0x80 | (cp & 0x3F)); return 2; }
    if (cp <= 0xFFFF) { b[0] = (unsigned char)(0xE0 | (cp >> 12));
                        b[1] = (unsigned char)(0x80 | ((cp >> 6) & 0x3F));
                        b[2] = (unsigned char)(0x80 | (cp & 0x3F)); return 3; }
    b[0] = (unsigned char)(0xF0 | (cp >> 18));
    b[1] = (unsigned char)(0x80 | ((cp >> 12) & 0x3F));
    b[2] = (unsigned char)(0x80 | ((cp >> 6) & 0x3F));
    b[3] = (unsigned char)(0x80 | (cp & 0x3F));
    return 4;
}

/* Byte image of a byte-expressible context set (see enc.h). */
bool pcrec_enc_set_bytes(const PcrecEnc *e, const PcrecCpRange *iv, int n,
                         uint8_t out[32])
{
    memset(out, 0, 32);
    for (int i = 0; i < n; i++) {
        if (iv[i].hi > e->onebyte_max) return false;
        for (unsigned c = iv[i].lo; c <= iv[i].hi; c++)
            out[c >> 3] |= (uint8_t)(1u << (c & 7));
    }
    return true;
}
