/* [COMPOUND] THE COMPOUND TOOL'S PARTS (docs/design/compound.md §A.1, §A.5;
 * build step B1). Driver tier: it calls the pipeline driver, as compile.c's
 * own entries do.
 *
 * A PART is the unchanged pipeline run on a derived input and rendered as
 * `<prefix>__<role>` inside a compound's one artifact. What makes it a part
 * is two things the driver is handed and no `pcrec_options` field carries
 * (`PcrecEmitIn`): an entry request that exports nothing and keeps what the
 * controller reads (`need`, through [EMIT-ENTRIES]' closure), and PART MODE
 * (the role, which renders the prefix and drops the shared blocks, and the
 * bound, which the start table's BOUND slot reads).
 *
 * NO SILENT DEFAULT (memory `pcrec-no-silent-defaults`, compound.md §A.1).
 * Every `CompPart` field is stated: the two enums' zero values are UNSTATED
 * and refused, a NULL derivation is unstated (`pcrec_derive_none` is the
 * explicit none), and a part that forces a flag both on and off is
 * refused. A part's options are the parent's with `flags_set` OR-ed in and
 * `flags_clear` masked out; `tune`, `analysis`, `features`, `encoding` and
 * every cap are the parent's by that one written rule. B4's compound_rows[]
 * runs `pcrec_comp_part_check` over every part of every row at table build;
 * until then its callers are the unit drive and `pcrec_compile_part`.
 * A part's derivation runs as the driver's tree-hook (B2); its report goes
 * to the caller's `report` (NULL: none wanted). */
#include "core/internal.h"

#include <stdio.h>
#include <string.h>

const PcrecDerive pcrec_derive_none = { "none", NULL };

/* The pipeline's engine request for each stated part engine. */
static const int part_engine[] = {
    [PCREC_PE_AUTO] = PCREC_ENGINE_AUTO,
    [PCREC_PE_DFA] = PCREC_ENGINE_DFA,
    [PCREC_PE_VM] = PCREC_ENGINE_VM,
};

/* The [EMIT-ENTRIES] kept roots a part's `need` names. */
static unsigned part_kept(unsigned need)
{
    unsigned m = 0;
    if (need & PCREC_PART_NEED_SEARCH)     m |= PCREC_ENTRY_BIT(PCREC_ENTRY_SEARCH);
    if (need & PCREC_PART_NEED_MATCH_CAPS) m |= PCREC_ENTRY_BIT(PCREC_ENTRY_MATCH_CAPS);
    if (need & PCREC_PART_NEED_NEXT_POS)   m |= PCREC_ENTRY_BIT(PCREC_ENTRY_NEXT_POS);
    if (need & PCREC_PART_NEED_VALID_UPTO) m |= PCREC_ENTRY_BIT(PCREC_ENTRY_VALID_UPTO);
    return m;
}

const char *pcrec_comp_part_check(const CompPart *part)
{
    if (!part) return "no part";
    const char *r = part->role;
    size_t n = r ? strlen(r) : 0;
    if (n < 1 || n > PCREC_PART_ROLE_MAX) return "role: 1 to 3 characters";
    for (size_t i = 0; i < n; i++)
        if (!((r[i] >= 'a' && r[i] <= 'z') || (r[i] >= '0' && r[i] <= '9')))
            return "role: [a-z0-9] only";
    if (!part->derive) return "derive: unstated (pcrec_derive_none is the explicit none)";
    if (part->derive != &pcrec_derive_none && !part->derive->fn)
        return "derive: a derivation with no function";
    if (part->flags_set & part->flags_clear) return "flags: one flag both set and cleared";
    if (part->engine == PCREC_PE_UNSTATED) return "engine: unstated";
    if (part->bound == PCREC_PB_UNSTATED) return "bound: unstated";
    if (!(part->need & PCREC_PART_NEED_SEARCH)) return "need: no search entry";
    if (part->need & ~PCREC_PART_NEED_ALL) return "need: an unknown bit";
    if (part->groups.kind == CG_UNSTATED) return "groups: unstated";
    return NULL;
}

int pcrec_compile_part(const char *pattern, const pcrec_options *parent,
                       const CompPart *part, PcrecDeriveReport *report,
                       pcrec_output *out, pcrec_error *err)
{
    const char *why = pcrec_comp_part_check(part);
    if (why) {
        if (out) memset(out, 0, sizeof *out);
        if (err) {
            snprintf(err->msg, sizeof err->msg, "internal error: compound part: %s", why);
            err->pos = 0;
            err->input = PCREC_ERR_INPUT_PATTERN;
        }
        return -1;
    }
    pcrec_options o;
    pcrec_default_options(&o);
    if (parent) o = *parent;
    o.flags = pcrec_flags_without(o.flags | part->flags_set, part->flags_clear);
    o.engine = part_engine[part->engine];
    o.header_name = NULL;
    const PcrecEntryReq req = { 0, part_kept(part->need) };
    const PcrecEmitIn in = { &req, part->role, part->bound, part->derive->fn,
                             report };
    return pcrec_compile_driver(pattern, &o, out, err, NULL, NULL, NULL, NULL,
                                NULL, &in);
}
