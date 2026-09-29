/* src/parse/mod_ucp.c — module `ucp` (docs/design/ucp_design.md, D130).
 *
 * WHAT THE MODULE OWNS. The `(*UCP)` start-of-pattern verb, the `--ucp`
 * generation axis's parse-time meaning, and — through the definitions table's
 * `DEF_UCP_*` rows (registry.c) — what `\d \s \w` and the POSIX classes mean
 * under UCP. It also owns `(*UTF)`/`(*UTF8)`, which RESTATE `--encoding=utf8`
 * rather than switch to it (§1.2, D130 Q2): the encoding is a property of the
 * ARTIFACT's entry points, so a pattern may confirm it and may never change it.
 *
 * O-71: an encoding may IMPLY this module (`PcrecEnc.implied_features`), which
 * is how `-e utf8` makes `(*UCP)` and `(*UTF)` available without `--features`.
 * Enabled is not ON: UCP semantics apply only when `(*UCP)` or `--ucp` says so. */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"
#include "enc/enc.h"
#include "parse_mods.h"

/* Builds this module's refusal ExtResult carrying `msg` at `at`. */
static ExtResult ucp_refuse(ExtWant want, size_t at, const char *msg)
{
    ExtResult res = { .what = EXT_REFUSAL, .at = at, .msg = "",
                      .answered_at = want };
    snprintf(res.msg, sizeof res.msg, "%s", msg);
    return res;
}

/* An accepted start-of-pattern option: an A_EMPTY that matches nothing and is
 * not a repeatable item (`(*UTF)*` is PCRE2 error 109, the `(?i)*` shape), and
 * that extends the accepted option run so the NEXT option may follow it. */
static ExtResult ucp_option_node(Ctx *cx, ExtWant want, size_t at, size_t end)
{
    ExtResult res = { .what = EXT_NODE, .at = at, .msg = "",
                      .answered_at = want };
    res.node = pcrec_ast_node(cx, A_EMPTY);
    res.node->not_repeatable = true;
    res.end = end;
    cx->optrun_end = end;
    return res;
}

/* The `(*UTF)`/`(*UTF8)` port: accepted as a restatement when the compile's
 * encoding IS Unicode (its universe is Unicode's, `max_cp`), refused by the
 * row's own fixed sentence otherwise — asked of the encoding, never of its
 * identity (DD-12 (7)). `from` is one past the verb's `)`. */
ExtResult pcrec_ucpport_utf(Ctx *cx, const RegRow *rw, ExtWant want,
                            size_t at, size_t from)
{
    if (pcrec_enc_by_id(cx->opt->encoding)->max_cp < 0x10FFFFu)
        return ucp_refuse(want, at, rw->msg);
    return ucp_option_node(cx, want, at, from);
}

