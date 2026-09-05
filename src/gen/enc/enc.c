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

#include "gen/enc/enc.h"

/* [M5.0 stage 2] The `utf8` row stopped being the PENDING one this table
 * carried from [M5-SEAM] through stage 1 (a name with `entries == NULL`,
 * refused by `pcrec_enc_ready`) and became a real backend — enc_utf8.c, the
 * third-encoding recipe's first execution: one new file in this directory,
 * one extern in enc.h, this one row. */
static const PcrecEnc *const enc_table[] = {
    &pcrec_enc_backend_byte,
    &pcrec_enc_backend_utf8
};

const PcrecEnc *pcrec_enc_by_id(int id)
{
    for (size_t i = 0; i < sizeof enc_table / sizeof *enc_table; i++)
        if (enc_table[i]->id == id) return enc_table[i];
    return NULL;
}

const PcrecEnc *pcrec_enc_by_name(const char *name)
{
    if (!name) return NULL;
    for (size_t i = 0; i < sizeof enc_table / sizeof *enc_table; i++)
        if (!strcmp(enc_table[i]->name, name)) return enc_table[i];
    return NULL;
}

void pcrec_enc_names(char *buf, size_t cap)
{
    /* Rendered from the table above rather than written out, so a new row
     * cannot leave a diagnostic listing a stale menu. */
    size_t k = 0;
    if (!cap) return;
    for (size_t i = 0; i < sizeof enc_table / sizeof *enc_table; i++) {
        const char *n = enc_table[i]->name;
        size_t ln = strlen(n);
        if (k && k + 2 < cap) { buf[k++] = ','; buf[k++] = ' '; }
        if (k + ln + 1 < cap) { memcpy(buf + k, n, ln); k += ln; }
    }
    buf[k] = 0;
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
    for (const PcrecEncEntry *t = e->entries; t->decls; t++)
        if (mask & t->id) pcrec_enc_emit_text(sb, t->decls, prefix);
}

void pcrec_enc_emit_defs(StrBuf *sb, const PcrecEnc *e, unsigned mask,
                         const char *prefix)
{
    if (!e || !e->entries) return;
    for (const PcrecEncEntry *t = e->entries; t->decls; t++)
        if (mask & t->id) pcrec_enc_emit_text(sb, t->defs, prefix);
}

bool pcrec_enc_entry_engine_callable(const PcrecEnc *e, unsigned id)
{
    if (!e || !e->entries) return false;
    for (const PcrecEncEntry *t = e->entries; t->decls; t++)
        if (t->id == id) return t->engine_callable;
    return false;
}

void pcrec_enc_emit_text(StrBuf *sb, const char *text, const char *prefix)
{
    for (const char *q = text; *q; q++) {
        if (*q == '$') sb_puts(sb, prefix);
        else           sb_putc(sb, *q);
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
