/* src/dump/cpu_targets_dump.c — [XARCH-DEV] unit P1 `pcrec --list-cpu-targets`
 * (docs/spec/cli.md §2.16, docs/spec/table_contract.md).
 *
 * Lists every token `-fmemfn-simd=LIST` accepts. pcrec owns none of it: each
 * cell is the kit's own text, read through `mf_families`, `mf_targets` and
 * `mf_host_family`, so a token the kit adds is listed without an edit here
 * and a hand-copied token list would be the defect. */
#include <string.h>

#include "core/internal.h"
#include "pcrec.h"
#include "../../memfn/include/memfn.h"

char *pcrec_cpu_targets_tsv(void)
{
    StrBuf sb = {0};
    size_t nf = 0, nt = 0;
    const mf_family *fam = mf_families(&nf);
    const mf_target *tgt = mf_targets(&nt);
    const mf_family *host = mf_host_family();

    pcrec_sb_puts(&sb,
        "# pcrec CPU targets (docs/spec/cli.md §2.16): every token the list of\n"
        "# -fmemfn-simd=LIST accepts, all text the search-code kit's own.\n"
        "# kind: \"family\" (in a list it means that family's default list) |\n"
        "#   \"target\" (one CPU target; a list holds one target for now).\n"
        "# family: a target's family, empty for the portable target and for a\n"
        "#   family row.\n"
        "# host: \"host\" on the family -fmemfn-simd alone selects (the one this\n"
        "#   build was compiled for), else empty.\n"
        "# defaults: a family's default list; features: a target's features.\n"
        "#kind\tname\tfamily\thost\tdefaults\tfeatures\tdoc\n");
    for (size_t i = 0; i < nf; i++) {
        const char *cells[] = { "family", fam[i].name, "",
                                &fam[i] == host ? "host" : "",
                                fam[i].defaults, "", fam[i].doc };
        pcrec_sb_row(&sb, cells, sizeof cells / sizeof *cells);
    }
    for (size_t i = 0; i < nt; i++) {
        const char *cells[] = { "target", tgt[i].name,
                                tgt[i].family ? tgt[i].family->name : "", "",
                                "", tgt[i].features, tgt[i].doc };
        pcrec_sb_row(&sb, cells, sizeof cells / sizeof *cells);
    }
    return pcrec_sb_take(&sb);
}
