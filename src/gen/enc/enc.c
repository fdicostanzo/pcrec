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

static const PcrecEnc enc_utf8_pending = {
    /* NOT a backend: the NAME exists so `--encoding=utf8` is a recognised
     * member refused for a stated reason, rather than an unknown value. The
     * backend (lowering instance + this row's residual text) is M5's. */
    PCREC_ENC_UTF8, "utf8", NULL
};

static const PcrecEnc *const enc_table[] = {
    &pcrec_enc_backend_byte,
    &enc_utf8_pending
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
