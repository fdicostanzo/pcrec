/* ucd_dump.c — the Unicode property tables, as text, THROUGH THE INTERFACE
 * ([DATA-PLAN] A1).
 *
 * The Python tools that need the table's contents (`uprops_names.py`, the
 * `clsets.py` population readers) used to regex-parse the generated `.inc`,
 * which made each of them a second reader of the storage format.  They read
 * this program's output instead, so the one module that knows the format
 * (`src/parse/ucd_tables.c`) is the only thing that does.
 *
 *     ucd_dump            the whole table
 *     ucd_dump --version  just the pinned Unicode version
 *
 * Output, one record per line, tab separated:
 *     #version  <string>
 *     #ns       <LABEL>  <number>          (the interface's PCREC_UCD_NS_*)
 *     <name>  <ns mask>  <set>  <caseless set>
 * where a set is `lo-hi` hex pairs joined by commas, `-` when empty.  Rows
 * come in the interface's row order, which is not a contract. */
#include <stdio.h>
#include <string.h>

#include "parse/ucd_tables.h"

static void put_set(const PcrecCpRange *iv, int n)
{
    if (n == 0) { fputs("-", stdout); return; }
    for (int i = 0; i < n; i++)
        printf("%s%X-%X", i ? "," : "", iv[i].lo, iv[i].hi);
}

int main(int argc, char **argv)
{
    if (argc > 1 && strcmp(argv[1], "--version") == 0) {
        puts(pcrec_ucd_unicode_version());
        return 0;
    }
    Arena a = { 0 };
    printf("#version\t%s\n", pcrec_ucd_unicode_version());
    printf("#ns\tBARE\t%u\n#ns\tSC\t%u\n#ns\tSCX\t%u\n#ns\tBC\t%u\n"
           "#ns\tBLK\t%u\n#ns\tAGE\t%u\n",
           PCREC_UCD_NS_BARE, PCREC_UCD_NS_SC, PCREC_UCD_NS_SCX,
           PCREC_UCD_NS_BC, PCREC_UCD_NS_BLK, PCREC_UCD_NS_AGE);
    for (size_t i = 0; i < pcrec_ucd_row_count(); i++) {
        unsigned ns;
        const char *name = pcrec_ucd_row_name(i, &ns);
        int n, nc;
        const PcrecCpRange *iv = pcrec_ucd_row_set(&a, i, false, &n);
        const PcrecCpRange *ci = pcrec_ucd_row_set(&a, i, true, &nc);
        printf("%s\t%u\t", name, ns);
        put_set(iv, n);
        fputc('\t', stdout);
        put_set(ci, nc);
        fputc('\n', stdout);
    }
    pcrec_arena_free(&a);
    return 0;
}
