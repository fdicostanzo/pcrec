/* parse_mods.h — the SCOPED INLINE-OPTION STATE, and the reason it lives in a
 * header no pass outside src/parse/ includes ([M6.2] wave A; D62;
 * docs/design/assertions_design.md §8.2 and §8.6).
 *
 * THE INVARIANT this file enforces:
 *
 *     Scoped modifier state is resolved AT PARSE TIME, onto the node.
 *     No post-parse pass reads it.
 *
 * That was a discipline rule until [M6.2] wave A, and exactly one pass broke
 * it. `src/opt/possessify.c` captured `cx->mods.multiline` once, after the
 * parse had finished, and exempted `$` from its follow-set widening on the
 * strength of it. `(?m)` is SCOPED in PCRE2, so the end-of-parse value is not
 * the value at the `$`: `(?m:a{0,4}$)` and `(?m)a{0,4}$(?-m)` both read
 * multiline=FALSE there while their `$` is genuinely multiline, and both would
 * have possessified a quantifier whose retreat is the only way to the match —
 * two measured lost-match cells (assertions_design.md §8.1.1), shipping the
 * day the `m` letter is accepted. The cure resolves the fact onto the node
 * (`Ast.multiline`); THIS FILE is what stops the next analysis re-deriving it
 * from a separate source it has to keep in sync, which is this project's
 * recorded check-design failure mode.
 *
 * `Ctx.mods` is declared as a pointer to an INCOMPLETE `ParseMods` in
 * src/core/internal.h. Code that includes this header can dereference it;
 * code that cannot see this definition gets a compile error rather than a
 * plausible wrong answer. src/parse/ is the whole legitimate consumer set —
 * measured: after the possessify cure, `mods.` appears in no other directory
 * (assertions_design.md §8.4's grep, re-run in this lane).
 *
 * DO NOT include this from src/opt/, src/ir/, src/gen/, src/core/ or cli/.
 * If a pass there needs to know something a modifier decided, the answer is a
 * FIELD ON THE NODE set by the parser, in the shape `Ast.greedy` (from `(?U)`)
 * and `Ast.multiline` (from `(?m)`) already have. */
#ifndef PCREC_PARSE_MODS_H
#define PCREC_PARSE_MODS_H

#include "core/internal.h"

struct ParseMods {
    bool    caseless;   /* i — the OS-1/D23 fold, applied at class
                         * construction time (char_node/from_bits) */
    bool    dotall;     /* s — `.` keeps 0x0A instead of clearing it */
    /* m — `^`/`$` match at every newline rather than only at the subject
     * ends. NO WRITER TODAY: pcrec refuses `(?m)` and has no `-m`, so this is
     * false for every compile that reaches a producer, and module
     * `assertions`' wave C is the writer that makes it live.
     *
     * ITS ONE CONSUMER IS THE PARSER, and that is now structural rather than
     * a convention (see this file's header): `p_atom`'s `^`/`$` cases copy it
     * onto the node as `Ast.multiline`, at the position of the assertion
     * itself, and every downstream analysis reads the node. D47.5's live-gate
     * requirement is satisfied by that read, not by this field — the gate is
     * live, and it is now also SCOPE-CORRECT, which D47.5's own wording did
     * not ask for and which its recorded test obligation would have missed
     * (it names the leading-`(?m)` shape, the one the pre-cure code got
     * right). */
    bool    multiline;
    bool    ungreedy;   /* U — quantifier greed default inverted; a
                         * trailing `?` then RE-inverts. NOT reset by ^ */
    bool    nocap;      /* n — plain `(` stops counting as a capture */
    /* [M6.5.2] J — DUPLICATE GROUP NAMES ARE LEGAL (PCRE2_DUPNAMES).
     *
     * MEASURED, backrefs_design.md §8.1 over seventeen cells: the duplicate
     * check is made AT EACH DECLARATION, against the SCOPED `(?J)` state in
     * force AT THAT DECLARATION. Not at the pattern's start, not globally, and
     * not once per compile. `(?<a>x)(?J)(?<a>y)` is legal because the SECOND
     * declaration is under `(?J)`; `(?J:(?<a>x))(?<a>y)` is not, because the
     * second is not; `(?<a>x)(?<a>y)(?J)` is an error, which kills the reading
     * that `(?J)` anywhere legalises everything.
     *
     * So it is `caseless`'s and `multiline`'s shape exactly — a scoped parser
     * bool saved and restored at group boundaries — and its ONE consumer is
     * `mod_named_groups.c`'s duplicate check, which reads it at the
     * declaration site. Nothing downstream reads it, which this header makes a
     * compile error rather than a convention.
     *
     * THERE IS NO `PCREC_DUPNAMES` OPTION BIT (ASK-2, ruled): inline `(?J)`
     * only. `(?i)` has both spellings for a historical reason `(?J)` does not
     * share, and `pcrec_options.flags` stays as D44.8 froze it. A libpcre2
     * cell that separates the two is measured and recorded: an inline `(?-J)`
     * BEATS the API bit, so the letter — not an option word — is the
     * authoritative state even in PCRE2. */
    bool    dupnames;
    uint8_t xlevel;     /* 0 off / 1 `x` / 2 `xx` — consumed by the
                         * MOD-0.5d lexer; the state exists so one run
                         * parser owns every letter */
};

#endif /* PCREC_PARSE_MODS_H */
