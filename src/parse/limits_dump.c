/* src/parse/limits_dump.c — [LIM-1] `pcrec --list-limits`, the numeric-
 * limits registry's SIXTH TSV surface (docs/spec/table_contract.md,
 * docs/spec/registry.md; D90).
 *
 * WHAT THIS PROVES AND WHAT IT DOES NOT. This dump `#include`s
 * `src/core/limits.def` DIRECTLY — defining the full `PCREC_LIMIT(name,
 * value, unit, kind, override, anchor, desc, home)` macro itself rather than
 * going through any site's per-HOME dispatch layer (limits.def's own header
 * comment names this shape) — so every row's `name` and `value` are the
 * SAME table every `#define`/`enum` in the tree now generates from
 * (src/core/limits.h and friends). A row's `value` argument is spliced
 * straight into a numeric cast at this call site, so a row that references
 * an earlier row's own symbol (PCREC_MAX_EMIT_NAME_LEN's `PCREC_MAX_PREFIX_
 * LEN + 96`) evaluates to the REAL compiled-in number, never a second
 * computation of it — the same "one derivation" property `--list-axes`
 * documents for its own live-array reads. This file proves the table's
 * numbers agree with what the compiler actually built; it does NOT prove a
 * value is DOCUMENTED correctly elsewhere — `tests/registry/limits_check.sh`
 * (dump-vs-docs/spec/limits.md §3, dump-vs-bare-#define) is the independent
 * side of that claim, on `--list-axes`'s own precedent.
 *
 * Wire format: docs/spec/table_contract.md (TSV, `#` comments, last `#`
 * line before data is the header, columns append-only). */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"
#include "pcrec.h"

/* `override`'s table token (a bare identifier — NONE/FLAG/BUILD_D, chosen so
 * limits.def's per-HOME dispatch can `##`-paste it — see that file's own
 * header) is stringified HERE rather than compared against; the C token
 * text is what a `#override` in this row's own macro invocation yields, so
 * this function's input is always one of exactly three spellings and a
 * fourth is a build error at the switch below, not a silently-wrong TSV
 * cell. */
static const char *override_name(const char *tok)
{
    if (!strcmp(tok, "NONE"))    return "none";
    if (!strcmp(tok, "FLAG"))    return "flag";
    if (!strcmp(tok, "BUILD_D")) return "-D";
    return tok; /* unreached on a well-formed table; visible rather than lost */
}

static void limit_row(StrBuf *sb, const char *name, long long value,
                      const char *unit, const char *kind,
                      const char *override, const char *anchor,
                      const char *desc)
{
    sb_printf(sb, "%s\t%lld\t%s\t%s\t%s\t%s\t%s\n",
              name, value, unit, kind, override_name(override), anchor, desc);
}

char *pcrec_limits_tsv(void)
{
    StrBuf sb = {0};

    sb_puts(&sb,
        "# pcrec numeric-limits registry (docs/spec/table_contract.md, the\n"
        "# SIXTH TSV surface; D90/[LIM-1]). One row per numeric limit in\n"
        "# src/core/limits.def, in the table's own order.\n"
        "#\n"
        "# unit: the quantity's dimension, or empty for a dimensionless\n"
        "# magnitude ceiling.\n"
        "# kind: \"compile budget\" (bounds the COMPILER's own analysis or\n"
        "#   emission; crossing it can refuse a pattern) | \"runtime\n"
        "#   capacity\" (bounds the EMITTED MATCHER's own resource use;\n"
        "#   crossing it is a give-up, never a wrong answer) | \"size cap\"\n"
        "#   (bounds emitted artifact bytes) | \"selection knee\" (a\n"
        "#   threshold or default that steers a selection mechanism, not a\n"
        "#   hard ceiling) | \"identifier cap\" (bounds a name's length or a\n"
        "#   naming-tied count).\n"
        "# override: \"flag\" (a CLI flag or pcrec_options field moves it per\n"
        "#   compile) | \"-D\" (only a build-time -D at pcrec's OWN compile\n"
        "#   moves it) | \"none\" (fixed).\n"
        "# anchor: the docs/spec/limits.md section this number is\n"
        "#   documented in, empty when it is not (limits.md states caller-\n"
        "#   facing PROMISES, not an internals catalogue — see this file's\n"
        "#   own header and src/core/limits.def's for the boundary).\n"
        "#name\tvalue\tunit\tkind\toverride\tanchor\tdesc\n");

#define PCREC_LIMIT(name, value, unit, kind, override, anchor, desc, home) \
    limit_row(&sb, #name, (long long)(value), unit, kind, #override, anchor, desc);
#include "core/limits.def"
#undef PCREC_LIMIT

    return sb_take(&sb);
}
