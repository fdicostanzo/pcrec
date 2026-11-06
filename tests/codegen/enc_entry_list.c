/* tests/codegen/enc_entry_list.c — [VLOOKBEHIND] (vlookbehind.md §5.6) THE
 * SEAM'S ENTRY TABLE, AS THE ENCODING CHECKS READ IT.
 *
 * DD12a(i) and K49 (run_encoding_checks.sh) used to carry hand lists of the
 * seam's entry NAMES and RETURN TYPES, and the file records three drifts of
 * those lists ([VAR]'s `int`, the `span_ci_` rename, [CLS-TREE]'s `decode`).
 * This reader prints the seam's own answer instead, linked against
 * build/libpcrec.a (the tests/utf8/startbnd_backend_check.c precedent): one
 * line per (backend, entry row),
 *
 *   backend <TAB> id <TAB> inline|outline <TAB> stands-for <TAB> boundary
 *           <TAB> sym sym ...
 *
 * `id` and `stands-for` are hex entry bits (`pcrec_enc_entry_stands_for`:
 * a SUBSTITUTE row, today byte's SPAN_CASELESS_UCP, stands for the entry it
 * replaces, so the two count as one key). `boundary` is 1 for a member of
 * PCREC_ENC_BOUNDARY_ENTRIES (K49's agreement set). The symbols are every
 * file-scope name the row's emission DEFINES (`pcrec_enc_entry_symbols`,
 * which sits beside the code that emits them), without the prefix.
 *
 * Backends are enumerated by id until the registry answers NULL, so a third
 * encoding is listed without an edit here. */
#include <stdio.h>

#include "core/internal.h"
#include "enc/enc.h"

static void put_sym(const char *sym, void *u)
{
    (void)u;
    printf(" %s", sym);
}

int main(void)
{
    int nrows = 0;
    for (int id = 0; ; id++) {
        const PcrecEnc *e = pcrec_enc_by_id(id);
        if (!e) break;
        if (!e->entries) continue;
        for (const PcrecEncEntry *t = e->entries; t->decls; t++) {
            printf("%s\t0x%x\t%s\t0x%x\t%d\t", e->name, t->id,
                   t->inline_def ? "inline" : "outline",
                   pcrec_enc_entry_stands_for(t->id),
                   (t->id & PCREC_ENC_BOUNDARY_ENTRIES) ? 1 : 0);
            pcrec_enc_entry_symbols(e, t->id, put_sym, NULL);
            printf("\n");
            nrows++;
        }
    }
    return nrows > 0 ? 0 : 1;
}
