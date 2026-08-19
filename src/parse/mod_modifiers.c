/* mod_modifiers.c — module `modifiers` (MOD-0.5): the `(?` doorway's OPTION
 * RUN grammar.
 *
 * MOD-0.5b, slice 1 — THE GRAMMAR MOVE, byte-identity only. This TU carries
 * pcrec_registry_option_run_ok out of registry.c, together with the whole
 * measured grammar comment below it (the probes-and-code-together rule:
 * R8/C2-9 found the `(*LIMIT_*=digits` rule's measured description in
 * registry.c and its implementation in ext.c had DRIFTED — ext.c accepted
 * `=99999999999` that the description forbade — which is exactly the failure
 * mode of separating a construct's measurements from its code. So the whole
 * block, probes and grammar together, moves as one unit). No semantics
 * change here: RF_OPTION_RUN retires and the twelve GROUP_OPT rows carry a
 * `recognise` pointer instead (see pcrec_registry_option_run_recognise
 * below), but what a pattern compiles to is unchanged — measured over the
 * base/classes corpora, the reject table, and the twelve option-setting
 * shapes swept both valid and malformed, against the pre-move tree.
 *
 * WHERE THIS FUNCTION USED TO LIVE. Until this slice it sat in registry.c
 * under a comment reading "THIS FUNCTION'S HOME IS PROVISIONAL AND WILL
 * MOVE" — a body PARSER living in a file whose own header describes itself
 * as `static const` data plus a lookup, unlike how the other two multi-byte
 * doorways are split (`(*`'s NAME tables and `[[:...:]]`'s NAME table both
 * keep their tables in registry.c and their SCANNING in ext.c/scans.c).
 * Frank's call, 2026-08-10, still stands as the target this slice moves
 * TOWARD, not the design it delivers: a module should expose SEVERAL PORTS
 * — a semantic one and a syntax one — and the doorway should identify the
 * construct from key+tail and then call the row's SYNTAX handler for the
 * details. This slice gets the syntax handler into its own module file and
 * off the flag ext.c used to test; the semantic ports (Ctx modifier state,
 * per-letter production) are MOD-0.5c and are not built yet.
 *
 * It is written in its own file rather than inlined into ext.c for one
 * reason worth keeping wherever it ultimately lands: the grammar below and
 * the measurements that establish it must not be separated. Whichever file
 * holds the port, the probes and the code go together. */

#include <stdio.h>

#include "core/internal.h"
#include "parse/parse_mods.h"

/* Splitting the catch-all into eleven option-letter rows fixed the BYTE and
 * left the same over-promise one level down: `(?iZ)`, `(?-Z)` and `(?i-Z)` are
 * PCRE2 error 111 and pcrec still answered "requires module 'modifiers'",
 * because the row is chosen by the first byte and nothing read the rest. That
 * is Q2's own defect at a smaller scale — the shape the wake brief warns about
 * as "fixing the narrowest instance and calling it the class".
 *
 * So this doorway reads its whole run, exactly as `(*` reads its whole name.
 *
 * THE GRAMMAR IS MEASURED, and the sub-option rule is why it had to be. Swept
 * against libpcre2 10.46 over single bytes, both terminators, the `^` and `-`
 * prefixes, and every two-byte run:
 *
 *     letters   J U a i m n r s x          and NOTHING else
 *     a<sub>    aD aP aS aT aW             one ASCII-restrict letter after `a`
 *     (?aPP)    error 111                  ...and only one; `P` is not a letter
 *     (?aDPS)   error 111                  same
 *     repeats   (?xx) (?xxx) (?imsxJU)     OK — a letter may repeat
 *     hyphen    (?i-m) (?i-) (?-) (?aP-i)  OK
 *     caret     (?^) (?^i) (?^aP)          OK — and only at the very start
 *     terminator  ')' or ':'
 *
 * Every one of those lines is a probe that was run, not a sentence from
 * pcre2syntax. The `a` sub-options in particular are invisible to any rule
 * derived from single letters, and a "set of option letters" implementation —
 * the obvious one — accepts `(?aPP)` and rejects `(?aP)`, getting BOTH
 * directions wrong.
 *
 * THE QUESTION IS RECOGNITION, NOT VALIDITY, and getting that backwards is the
 * mistake this function was written with. PCRE2 has two answers for a bad run
 * and only one of them means "no construct here":
 *
 *     (?i-m-s) (?--i) (?-i-) (?i--m) (?^-i)   error 194 "invalid hyphen in
 *                                             option setting" — PCRE2 HAS
 *                                             recognised an option setting
 *     (?i-mZ) (?a-P) (?^^i) (?i^m)            error 111 — no construct at all
 *
 * So hyphens may appear anywhere and repeat: a misplaced one is a MALFORMED
 * option setting, which module 'modifiers' is exactly what would diagnose. The
 * doorway names the module; the module validates the body. Writing the stricter
 * "at most one hyphen, never after ^" rule here made pcrec answer "unrecognized
 * character" for five shapes PCRE2 calls option settings — an UNDER-promise,
 * the mirror of the over-promise Q2 removes, and the generated differential in
 * pcre2_check.c refused it within a minute of being pointed at it. */

static bool opt_letter(int c)
{
    return c == 'J' || c == 'U' || c == 'a' || c == 'i' || c == 'm' ||
           c == 'n' || c == 'r' || c == 's' || c == 'x';
}

/* The ASCII-restrict sub-options, valid ONLY directly after `a`. */
static bool opt_a_sub(int c)
{
    return c == 'D' || c == 'P' || c == 'S' || c == 'T' || c == 'W';
}

bool pcrec_registry_option_run_ok(const char *at, size_t avail)
{
    size_t i = 0;
    bool caret = false, hyphen = false;

    if (!at) return false;

    /* `^` only at the very start: `(?^^i)` and `(?i^m)` are error 111. */
    if (i < avail && at[i] == '^') { caret = true; i++; }

    for (;;) {
        /* Running off the END of the pattern is not an illegal byte: `(?i` is
         * PCRE2 error 114, "missing closing parenthesis", which is a RECOGNISED
         * option setting that was truncated. Returning false here made pcrec
         * answer "unrecognized character" for every truncated option run, and
         * registry_check's own 255-byte sweep — whose template is `(?%c`, with
         * no terminator at all — failed on all eleven option bytes at once. */
        if (i >= avail) return true;
        if (at[i] == ')' || at[i] == ':') return true;   /* a terminator ends it */

        if (at[i] == '-') {
            /* PCRE2 STOPS AT THE FIRST ERROR, and that ordering is part of the
             * rule rather than an implementation detail to be normalised away.
             * A hyphen that is invalid HERE — a second one, or one after `^` —
             * raises error 194 and PCRE2 never looks at what follows. So
             * `(?--D)` is a recognised (malformed) option setting even though
             * `D` would have been error 111 on its own, and a rule that scanned
             * the whole run before deciding got that backwards for 24 shapes. */
            if (caret || hyphen) return true;
            hyphen = true;
            i++;
            continue;
        }
        if (!opt_letter((unsigned char)at[i])) return false;
        bool is_a = at[i] == 'a';
        i++;
        /* `a` may take exactly one ASCII-restrict sub-option, and those letters
         * are not option letters anywhere else: `(?aP)` compiles, `(?a-P)` and
         * `(?aPP)` are error 111. */
        if (is_a && i < avail && opt_a_sub((unsigned char)at[i])) i++;
    }
}

/* ---- MOD-0.5b: the recogniser that retires RF_OPTION_RUN -----------------
 *
 * The twelve GROUP_OPT rows now carry this in their `recognise` field so
 * ext.c can key off the FIELD instead of a flag: "does this row's construct
 * need the doorway's whole-run check" becomes a pointer-identity question
 * (`r->recognise == pcrec_registry_option_run_recognise`) rather than a bit.
 *
 * IT DOES NOT RUN THE CHECK ITSELF, and that is a deliberate, measured
 * choice, not a shortcut. The obvious design — wrap pcrec_registry_option_
 * run_ok in the standard `(at, avail, tail)` signature and let MOD-0.2's
 * arbitration run it directly, the way recognise_N_name_brace (registry.c)
 * decides its own row — does not fit here, for a reason specific to this
 * construct: option_run_ok's grammar starts AT THE SELECTOR BYTE (`(?i-m`'s
 * run is "i-m", the letter included), one byte before what `at` conventionally
 * means everywhere else in this table (text AFTER the selector, what a `tail`
 * is compared against). Reconstructing that earlier byte as `at - 1` is safe
 * from ext.c's own arbitrate call, where `at` is always cx->pat plus a real
 * offset with a real selector byte sitting before it — but the SAME
 * recogniser is also called, through the SAME field, by
 * tests/registry/registry_check.c's arbitration sweeps
 * (check_arbitration_liveness's bucket floors and its no-ambiguity sweep),
 * against hand-built probe buffers that carry no such byte. `at - 1` there
 * reads outside the probe array — undefined behaviour introduced by a row's
 * OWN recogniser, exercised by the very checks meant to keep arbitration
 * honest. So this function stays a pure MARKER, answering exactly what the
 * old tail-less default already answered ("no tail: answers always", D32 §2)
 * — zero change to any arbitration or liveness count — and ext.c keeps doing
 * the real check itself, with the real Ctx, exactly as it did under the flag. */
bool pcrec_registry_option_run_recognise(const char *at, size_t avail,
                                         const char *tail)
{
    (void)at; (void)avail; (void)tail;
    return true;
}

/* ---- the SEMANTIC port (MOD-0.5c) ---------------------------------------
 *
 * The twelve GROUP_OPT rows' atom port. Called by the `(?` doorway ONLY at a
 * post-gate WANT_RESULT, and only after pcrec_registry_option_run_ok accepted
 * the run — which deliberately INCLUDES the recognised-malformed shapes
 * (PCRE2 error 194: a second hyphen, or a hyphen after `^`): the doorway
 * names the construct, this port diagnoses its body (D28's SYN_MALFORMED
 * half). `from` is the SELECTOR byte — the run includes it.
 *
 * PER-LETTER SEMANTICS, every line measured (probe_mod05.c, probe_mod05b.c,
 * probe_mod05c.c — the MOD-0.5a design gate plus this slice's corners):
 *
 *   i s U n     scoped parse state (cx->mods); the masks COLLECT over the
 *               whole run and UNSET WINS regardless of order — `(?i-i)k` and
 *               `(?-ii)k` are BOTH case-sensitive (measured).
 *   x / xx      a LEVEL, assigned per run, adjacency-sensitive: on each set-
 *               side `x` the level becomes 2 if the previous byte was also
 *               `x`, else 1 — `(?xsx)` and `(?xaDx)` are level 1 (measured),
 *               `(?xx)`/`(?xxx)`/`(?^xx)` level 2, and a later bare `(?x)`
 *               DOWNGRADES an earlier `(?xx)` (measured: `(?xx)(?x)[a b]`
 *               has the space member again; the `(?xx)(?s)` control keeps
 *               deletion). `-x` clears BOTH levels (`(?xx-x)` measured).
 *               The state is written here; its CONSUMER is the MOD-0.5d
 *               lexer, which lands in the same merge.
 *   ^           reset to the HARDWIRED defaults — caseless/dotall/nocap/
 *               xlevel false/0 — and ungreedy SURVIVES: U and J both live
 *               through `(?^)` (probe_mod05b; "unset imnsx" is the measured
 *               rule). The reset is to-constant, not to-`opt` — a `(?^)`
 *               under `-i` turns caseless OFF (the PARSE-1 landmine, now
 *               load-bearing).
 *   r, a+sub    MEASURED NO-OPS at options=0 in the C locale: `(?ri)` vs
 *               `(?i)` is 0 diff cells over 256x256, and all four a-sub
 *               pairs are census-identical (probe_mod05.c). They become
 *               real under UTF/UCP — MOD-0.6/M5 own that day; the letters
 *               are consumed here so the run parses, and nothing is set.
 *   m           REAL as of [M6.2] wave C — module `assertions`. Sets the
 *               scoped multiline state; `p_atom`'s `^`/`$` rows resolve it
 *               onto the node at the assertion itself (D62), which is what
 *               makes `(?m:...)` and `(?m)...(?-m)` right by construction
 *               rather than by a downstream pass re-deriving scope. Refused
 *               by its own name while the module is DISABLED. `-m` is
 *               accepted with no gate: it asks for the semantics pcrec's
 *               anchors have without the module.
 *   J           AN HONEST PER-LETTER REFUSAL (the MOD-0.3a per-name
 *               precedent): J is observable only through named groups.
 *               A tier-2 attribution, recorded in the plan. `-J` is an
 *               accepted no-op — duplicate names cannot occur without
 *               named groups, so unsetting it is true today.
 *
 * TERMINATORS: `)` applies the delta to the ENCLOSING scope — the caller's
 * splice deliberately bypasses p_group_body's save/restore, so the mutation
 * survives to the enclosing group's `)` (the measured 17/17 scoping).
 * `:` is set-parse-restore: the body parses under the new state through
 * pcrec_parse_body (the callback PARSE-1 built), and both the state and the
 * cursor are restored before returning (check06: the doorway never moves
 * cx->pos; the result carries `end` past the construct's `)`). */

static ExtResult modport_refuse(ExtWant want, size_t at, const char *msg)
{
    ExtResult res = { .what = EXT_REFUSAL, .at = at, .msg = "",
                      .answered_at = want };
    snprintf(res.msg, sizeof res.msg, "%s", msg);
    return res;
}

ExtResult pcrec_modport_optrun(Ctx *cx, const RegRow *rw, ExtWant want,
                               size_t at, size_t from)
{
    (void)rw;
    const char *p = cx->pat;
    size_t n = cx->patlen;
    size_t i = from;
    bool caret = false, hyphen = false;
    bool set_i = false, set_s = false, set_U = false, set_n = false;
    bool set_m = false;
    bool un_i = false, un_s = false, un_U = false, un_n = false, un_x = false;
    bool un_m = false;
    int xlvl = -1;              /* -1 = the run does not touch the level */

    if (i < n && p[i] == '^') { caret = true; i++; }
    for (;;) {
        if (i >= n)
            /* `(?i` — PCRE2 error 114's shape: a RECOGNISED option setting,
             * truncated. The run check already called this a construct;
             * the honest post-gate answer is the truncation itself. */
            return modport_refuse(want, at,
                                  "missing closing ) for inline option setting");
        int c = (unsigned char)p[i];
        if (c == ')' || c == ':') break;
        if (c == '-') {
            if (caret || hyphen)
                /* PCRE2 stops at the FIRST error (error 194) — the ordering
                 * is part of the measured rule, mod-grammar block above. */
                return modport_refuse(want, i,
                                      "invalid hyphen in option setting");
            hyphen = true;
            i++;
            continue;
        }
        switch (c) {
        case 'i': if (hyphen) un_i = true; else set_i = true; break;
        case 's': if (hyphen) un_s = true; else set_s = true; break;
        case 'U': if (hyphen) un_U = true; else set_U = true; break;
        case 'n': if (hyphen) un_n = true; else set_n = true; break;
        case 'x':
            if (hyphen) un_x = true;
            else xlvl = (i > from && p[i - 1] == 'x') ? 2 : 1;
            break;
        case 'm':
            /* [M6.2 wave C] ACCEPTED. Through wave B this letter carried its
             * own per-letter refusal in TWO forms (module-off and
             * module-on-but-unbuilt), because `(?m)`'s refusal is produced
             * HERE rather than by the `(?` doorway's GROUP_OPT row — a
             * letter's module is not the dispatching row's. That machinery is
             * retired with the letter, not made conditional: module
             * `assertions` implements multiline `^`/`$` in this wave, so the
             * honest answer to `(?m)` is to set the bit.
             *
             * The bit's ONE consumer is the parser itself — `p_atom`'s `^`
             * and `$` rows copy the state IN FORCE AT THE ASSERTION onto
             * `Ast.multiline` (D62; src/parse/parse.c). Nothing downstream
             * reads this struct, which src/parse/parse_mods.h makes a compile
             * error rather than a convention. That is why `(?m:...)` and
             * `(?m)...(?-m)` are right by construction here: the set/restore
             * below is the same machinery `(?i)` has always used, and the
             * resolution happens at each `^`/`$` while it is in force.
             *
             * `\A`/`\Z`/`\z` are UNAFFECTED and that is not an oversight:
             * src/parse/mod_assertions.c pins their nodes' flag false, which
             * is PCRE2's own rule — `\Z` under `(?m)` is still the subject's
             * end, not a line's.
             *
             * THE MODULE GATE STAYS (§9.2): with `assertions` disabled the
             * letter is refused by the same "requires module" sentence the
             * rest of the class uses. `-m` needs no gate — it asks for the
             * semantics pcrec's anchors have with no module at all. */
            if (!hyphen) {
                if (!pcrec_feature_enabled(FEAT_ASSERTIONS))
                    return modport_refuse(want, i,
                        "inline option 'm' (multiline) requires module "
                        "'assertions'");
                set_m = true;
            } else {
                un_m = true;
            }
            break;
        case 'J':
            /* [M6.3] WORDING, THIRD AND FINAL PASS (manager ruling,
             * 2026-08-18, citing docs/pcre2_options.md's RATIFIED D38 row
             * — PCRE2_DUPNAMES is `RIDES(M4/captures)`, a PLANNED-LATER
             * disposition — and docs/pcre2_compliance.md's own `(?J)` row,
             * REJECTED/planned, not OUT-OF-SCOPE). Two earlier wordings
             * were both wrong, for opposite reasons, and both are worth
             * knowing before touching this line again:
             *   1. "requires module 'named-groups'" — true while that
             *      module did not exist, but a LIE the moment it shipped
             *      WITHOUT dupnames support, since "requires X" reads as
             *      "enabling X fixes this" and enabling it does not.
             *   2. K14's ROADMAP_NEVER shape ("is outside pcrec's scope
             *      and no module will implement it") — WRONG in the other
             *      direction: (?J) is real PCRE2, D38 already rules it
             *      PLANNED-LATER capture-group machinery, and K14's bar is
             *      "architecturally out of scope per the survey", which a
             *      planned construct does not meet.
             * The correct shape names the OWNING module (named-groups —
             * duplicate NAMES are named-group semantics, the identical
             * dispatch logic 'm' already uses for 'assertions') without
             * the false "requires" framing: pcrec KNOWS what would
             * implement this and says so truthfully, indefinitely,
             * whether or not named-groups itself is enabled (this
             * refusal is unconditional either way — see
             * mod_named_groups.c's duplicate-name check, which never
             * consults this letter). Mirrors the `-e utf8` refusal's
             * precedent (a name pcrec knows, refused truthfully, no
             * "requires" claim). */
            if (!hyphen)
                return modport_refuse(want, i,
                    "inline option 'J' (dupnames): module 'named-groups' "
                    "does not implement duplicate group names (see "
                    "docs/pcre2_compliance.md)");
            break;                        /* -J: true today, accepted */
        case 'r':
            break;                        /* measured no-op at options=0 */
        case 'a':
            /* One optional ASCII-restrict sub-letter (the measured grammar);
             * the pair is a no-op at options=0 (census-identical). */
            if (i + 1 < n && (p[i + 1] == 'D' || p[i + 1] == 'P' ||
                              p[i + 1] == 'S' || p[i + 1] == 'T' ||
                              p[i + 1] == 'W'))
                i++;
            break;
        default:
            /* Unreachable: option_run_ok admitted the run. A wall, not a
             * decline — declining here would re-read the construct. */
            return modport_refuse(want, i,
                "internal error: option-run port saw a byte the grammar rejects");
        }
        i++;
    }

    /* The applied state: reset first (caret), then set, then unset — unset
     * WINS on a letter named on both sides (measured, (?i-i)/(?-ii)). */
    ParseMods ns = *cx->mods;
    if (caret) {
        bool keep_ungreedy = ns.ungreedy;
        ns = (ParseMods){0};
        ns.ungreedy = keep_ungreedy;
    }
    if (set_i) ns.caseless = true;
    if (set_s) ns.dotall = true;
    if (set_U) ns.ungreedy = true;
    if (set_n) ns.nocap = true;
    if (set_m) ns.multiline = true;
    if (xlvl >= 0) ns.xlevel = (uint8_t)xlvl;
    if (un_i) ns.caseless = false;
    if (un_s) ns.dotall = false;
    if (un_U) ns.ungreedy = false;
    if (un_n) ns.nocap = false;
    if (un_m) ns.multiline = false;
    if (un_x) ns.xlevel = 0;

    if (p[i] == ')') {
        /* Bare run: mutate the enclosing scope and produce the construct's
         * node — A_EMPTY, because an option setting matches nothing.
         *
         * AND IT IS NOT A REPEATABLE ITEM (R20/SPEC-1, a tier-1 miscompile
         * the D27 blinded writer found). A_EMPTY alone does not say that —
         * `()*` and `(a|)*` are ordinary quantifiable empties — so without
         * the flag `a(?i)*` compiled, the `*` bound to this node, and the
         * emitted matcher matched a/aa/aaa where libpcre2 gives err 109 at
         * the quantifier. The registry had been right the whole time: these
         * rows' `quantifiable` column reads `form`, and the producer
         * contradicted it. The boundary is BARE-vs-SCOPING, measured with no
         * exceptions: `a(?i:b)*` is correct and stays quantifiable (the `:`
         * branch below never sets this), while every accepted bare spelling
         * — `(?i)`, `(?i-m)`, `(?^)`, `(?xx)`, `(?U)` — is err 109. */
        *cx->mods = ns;
        ExtResult res = { .what = EXT_NODE, .at = at, .msg = "",
                          .answered_at = want };
        res.node = pcrec_ast_node(cx, A_EMPTY);
        res.node->not_repeatable = true;
        res.end = i + 1;
        return res;
    }

    /* `:` — a group body under the new state: set, parse, restore (the
     * semantic D29 said cannot be written without the callback). */
    {
        ParseMods saved_mods = *cx->mods;
        size_t   saved_pos  = cx->pos;
        AltInfo  info;
        *cx->mods = ns;
        cx->pos = i + 1;
        Ast *body = pcrec_parse_body(cx, &info);
        if (cx->pos >= n || p[cx->pos] != ')') {
            *cx->mods = saved_mods;
            cx->pos = saved_pos;
            return modport_refuse(want, at, "missing closing ) for group");
        }
        size_t end = cx->pos + 1;
        *cx->mods = saved_mods;
        cx->pos = saved_pos;
        if (body->k == A_BOL || body->k == A_EOL || body->k == A_END) {
            /* the S-M1 anchor wrap, mirrored from p_group_body: `(?i:^)*`
             * stays quantifiable exactly as `(^)*` is */
            Ast *cat = pcrec_ast_node(cx, A_CAT);
            cat->l = body;
            cat->r = pcrec_ast_node(cx, A_EMPTY);
            body = cat;
        }
        ExtResult res = { .what = EXT_NODE, .at = at, .msg = "",
                          .answered_at = want };
        res.node = body;
        res.end = end;
        return res;
    }
}
