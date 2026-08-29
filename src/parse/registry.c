/* The syntax construct registry (D24, step SR-1): every non-base PCRE
 * construct, described once, as static const data.
 *
 * WHY THIS FILE EXISTS. On 2026-08-09 two silent bugs were found by reading
 * PCRE2's syntax reference against the parser — `\v` decoded as vertical tab
 * when PCRE2 means vertical WHITESPACE, and POSIX collating elements accepted
 * when PCRE2 rejects them. Neither was a compiler defect; both were the
 * spec-to-code gap. `\v` in particular was a declarative table and an
 * imperative switch DISAGREEING TEN LINES APART, with nothing enforcing that
 * they agree, and the same knowledge then got copied into tests/reject/ and
 * docs/pcre2_compliance.md the same day. A construct with two homes will
 * drift; this file is the one home.
 *
 * THE FOUR DOORWAYS. Every non-base construct in PCRE2's entire surface enters
 * through exactly four places, each decided by one byte or a name:
 *
 *     after `\`              \d \v \p \K \g \Q \R \1
 *     after `(?`             (?= (?< (?> (?# (?C (?| (?( (?R (?& (?i
 *     after `(*`             (*SKIP) (*CR) (*script_run:
 *     after `[` in a class   [[:alpha:]] [[.a.]] [[=a=]]
 *
 * WHAT THE BASE TIER ACTUALLY COSTS, measured 2026-08-10 with an instrumented
 * build (R6), because the claim that stood here was wrong in both directions:
 *
 *     abc  a(b|c)+d  (?:ab)+           0 lookups
 *     [abc]                            1
 *     [a-z]+@[a-z]+\.[a-z]{2,4}        3
 *
 * `(?:` costs ZERO, not "one, once" — parse.c answers it before the registry is
 * reached, and its row exists so the table is complete for the dump. But the
 * CLASS-BRACKET doorway is a base-tier path: every non-negated `[` and every
 * `[` inside a class consults it, and a miss scans all rows because that kind
 * has no catch-all. So the cost is proportional to the number of character
 * classes, not zero. Frank's principle still holds — 3 lookups over 3 rows is
 * nothing against a 90 us compile floor — but it holds by SIZE, not BY
 * CONSTRUCTION, and SR-5 must assert the measured property rather than the
 * claimed one.
 *
 * WHAT IS NOT HERE, DELIBERATELY. Base syntax: literals, `.`, classes and
 * ranges, quantifiers, `|`, `(...)`, `^`, `$`, and the plain character escapes
 * \n \t \r \f \a \e \xHH. Those never consult this table. Two "requires
 * module" diagnostics also remain in parse.c because they are sub-cases of
 * BASE constructs rather than doorways, and inventing a doorway for them would
 * cost the base tier a lookup: `\x{...}` (reached only from the base `\x`
 * handler) and the possessive `+` suffix (a quantifier suffix, not an atom).
 * A third is a sub-case of a row rather than of the base tier: `\N{U+hhhh}` is
 * a distinct PCRE2 construct sharing the `N` selector byte with bare `\N`, and
 * whoever implements module 'classes' owns splitting it out. These three are
 * the registry's known outstanding second homes; SR-4 must special-case the
 * first two or silently drop their tests/reject/ coverage, since neither has a
 * row to iterate.
 *
 * WHAT THIS TABLE CANNOT DO, measured 2026-08-10 (R6). It identifies a DOORWAY
 * and names a MODULE. It cannot always identify the CONSTRUCT, because for two
 * constructs the deciding information is not at the doorway at all:
 *
 *   `(?(R)`  is a recursion condition or a NAMED-GROUP condition depending on
 *            whether the pattern declares a group called `R` — and that
 *            declaration may appear LATER in the pattern than the condition.
 *            Appending `(?<R>z)?` silently rebinds a condition 20 bytes to its
 *            left.
 *   `\ddd`   is an octal escape or a backreference depending on how many
 *            capture groups the parser has seen SO FAR. `(a)\12` is octal 012;
 *            with twelve groups it is a backreference to group 12. No amount of
 *            lookahead resolves it.
 *
 * Both are cleanly REJECTED today, naming the right module, so neither is a
 * live bug. What they bound is the future: whoever implements modules
 * 'conditionals' and 'backrefs' needs parser STATE the registry cannot supply —
 * a running capture count, and a whole-pattern group-name table. A row can say
 * "this doorway belongs to module X"; it cannot say which construct X should
 * build. Do not design a handler signature that assumes it can.
 *
 * FOUR AXES, KEPT APART. flavour (which construct a byte MEANS) / option (what
 * it DENOTES) / enablement (is it available) / engine (can it LOWER). Answering
 * all four with one mechanism is what produces an `if python-compat X else if
 * pcre2-dfa Y else Z` cascade. Kept apart, a flavour change REBINDS A ROW and
 * cannot reach inside another construct's handler.
 *
 * THE `engines` COLUMN IS DESIGN INTENT, NOT MEASUREMENT, and it is NOT a
 * statement about what a DFA can do in general. It records which PCREC engine
 * could lower each construct. Nothing consumes it, still, as of [M4.7a]
 * (SR-8): every VM_ONLY row below is gated by a module with no producer, so
 * building the lowering-time consultation ahead of that first producer would
 * be unpopulated machinery (D18/OS-0/D53's standing discipline). What DOES
 * exist since [M4.7a] is a TRIPWIRE, not a consumer:
 * tests/registry/registry_check.c's check_engine_capability_tripwire asserts
 * the fact that makes this column's silence safe — every RS_MODULE row whose
 * `engines` mask excludes ENGM_DFA has NO wired producer — so the day a
 * module wires the first one, that check fails loudly and names
 * src/opt/select_engine.c as the thing to build first. The conformance test
 * otherwise still asserts only that this column is well-formed.
 *
 * That distinction is load-bearing, because PCRE2's own DFA matcher disagrees
 * with several rows here. Measured against pcre2_dfa_match_8 in libpcre2 10.46:
 * it SUPPORTS lookaround, atomic groups and recursion — all marked VM_ONLY
 * below — and correctly enforces their semantics ((?>a+)a does not match "aaa"
 * while a+a does). It rejects \K, backreferences and conditionals (errors -42
 * and -40), agreeing with those rows.
 *
 * The rows are still right FOR PCREC, for a reason worth stating rather than
 * leaving a reader to infer: PCRE2's "DFA" is not a classical automaton. It is
 * a breadth-first simulation of compiled bytecode that can consult live capture
 * state and re-enter itself, which is exactly why recursion is possible in it.
 * pcrec's Dfa is a determinized transition table with no side channel for
 * capture state or re-entry, so those constructs genuinely cannot be
 * represented in THIS automaton even though they can be in PCRE2's. Treat every
 * value in this column as a claim to be re-checked when the VM lands.
 *
 * ADDING A ROW: fill it in here and nowhere else. `syntax` must be a pattern
 * that actually reaches this doorway — tests/registry/ uses it as the probe,
 * which is how a new row covers itself without a test edit. A NULL handler
 * (SR-2 introduces the field) and RS_MODULE status is a COMPLETE outcome: the
 * construct is named, cleanly rejected and queryable. It is not a stub. */

#include <string.h>

#include "core/internal.h"

/* ---- row shapes ---------------------------------------------------------
 * The macros below fix the fields that are CONSTANT for a shape and leave the
 * varying ones explicit, so a row reads as its own content rather than as
 * twelve positional fields. Three things this buys beyond brevity:
 *
 *   - `M_<module>` emits the feature bit and the diagnostic name AS A PAIR, so
 *     a row cannot carry FEAT_CLASSES while printing "assertions". That
 *     pairing was previously unchecked by anything.
 *   - a misspelled module is a COMPILE error (no such M_ macro), not a wrong
 *     string in a diagnostic nobody reads until a user hits it.
 *   - FLAV_PCRE2 lives here instead of being repeated 67 times. When SR-7 adds
 *     a second flavour, a row that genuinely VARIES by flavour must be written
 *     out longhand — so the exceptional row LOOKS exceptional in the source.
 *
 * A row with a shape of its own stays longhand. `(?:` is the only construct
 * here the base grammar implements, and it should not be able to hide inside a
 * macro that means "rejected". */

#define M_classes        FEAT_CLASSES,       "classes"
#define M_assertions     FEAT_ASSERTIONS,    "assertions"
#define M_backrefs       FEAT_BACKREFS,      "backrefs"
#define M_unicode_props  FEAT_UNICODE_PROPS, "unicode-props"
#define M_quoting        FEAT_QUOTING,       "quoting"
#define M_misc           FEAT_MISC,          "misc"
#define M_lookaround     FEAT_LOOKAROUND,    "lookaround"
#define M_named_groups   FEAT_NAMED_GROUPS,  "named-groups"
#define M_atomic_groups  FEAT_ATOMIC_GROUPS, "atomic-groups"
#define M_comments       FEAT_COMMENTS,      "comments"
#define M_callouts       FEAT_CALLOUTS,      "callouts"
#define M_branch_reset   FEAT_BRANCH_RESET,  "branch-reset"
#define M_conditionals   FEAT_CONDITIONALS,  "conditionals"
#define M_recursion      FEAT_RECURSION,     "recursion"
#define M_modifiers      FEAT_MODIFIERS,     "modifiers"
#define M_verbs          FEAT_VERBS,         "verbs"
#define M_extended_classes FEAT_EXTENDED_CLASSES, "extended-classes"
/* THERE IS NO COMPOUND MODULE MACRO ANY MORE. `M_lookaround_named`
 * ("lookaround/named-groups") lived here for `(?<`, one byte meaning two
 * constructs, and SR-9's `tail` retired it: `(?<=`, `(?<!` and `(?<*` are
 * lookaround rows and every other tail is a named group. A compound name is a
 * true sentence and an inexact answer, and D26 puts module attribution in
 * tier 2, where the standard is exact.
 *
 * Kept as a comment rather than deleted silently because the next person to
 * find one byte with two meanings will reach for this shape. Reach for `tail`
 * instead, and only fall back to a compound name if the deciding text is not a
 * literal prefix. */

#define ANY_ENGINE  (ENGM_DFA | ENGM_VM)
#define VM_ONLY     ENGM_VM

/* Every macro below spells its class_expect slot out. The six that can build
 * a CLASS-REACHABLE row (kind esc or class-bracket) take it as their trailing
 * `ce` parameter; the group/verb-only macros hardwire NULL, because `(` inside
 * a class is an ordinary member and a value there would be an invented fact.
 * The values themselves are measured, never authored — see internal.h. */
/* \x outside a class -> "\x requires module 'M'" */
#define ESC(sel, syn, mod, eng, note, q, ce) \
    {RK_ESC, (sel), NULL, (syn), M_##mod, FLAV_PCRE2, (eng), RS_MODULE, RD_MODULE, NULL, NULL, 0, (note), ROADMAP_PLANNED, (q), (ce), 0, NULL, NO_PORT, NO_PORT, NULL, NULL}
/* [DD-11.1] as ESC, but with a `definitions` array — `\c` and `\o{...}`'s
 * only customers today (both module `misc`, UNBUILT; the definitions
 * table can carry an unbuilt row's data ahead of a producer, `\R`'s own
 * precedent). */
#define ESC_D(sel, syn, mod, eng, note, q, ce, def) \
    {RK_ESC, (sel), NULL, (syn), M_##mod, FLAV_PCRE2, (eng), RS_MODULE, RD_MODULE, NULL, NULL, 0, (note), ROADMAP_PLANNED, (q), (ce), 0, NULL, NO_PORT, NO_PORT, NULL, (def)}
/* as ESC, but the row PRODUCES (MOD-0.3c): both ports carry the same
 * generated byte-set (see cls_bits.inc's provenance header), `neg` nonzero
 * for the complement forms (\D \S \W \H \V — only positive tables are
 * stored; the complement law is probe-asserted). Gated: with module
 * `classes` disabled these rows refuse exactly as ESC rows do. */
#define ESC_SET(sel, syn, mod, eng, note, q, ce, bits, neg) \
    {RK_ESC, (sel), NULL, (syn), M_##mod, FLAV_PCRE2, (eng), RS_MODULE, RD_MODULE, NULL, NULL, 0, (note), ROADMAP_PLANNED, (q), (ce), 0, NULL, {PORT_SET, false, (neg), (bits), NULL}, {PORT_SET, false, (neg), (bits), NULL}, NULL, NULL}
/* [DD-11.1] as ESC_SET, but with a `definitions` array (D85, Frank's
 * class-escape ruling, r43): the row's OWN byte set restated as a
 * core-syntax STRING (`--list-definitions`'s "one derivation, two readers"
 * — `--list-syntax` and this dump both trace to the SAME `bits`
 * generated table, just rendered two ways). Every class-escape row's
 * DEF_ALWAYS entry is what `--list-definitions` prints TODAY; DEF_UCP is
 * each family's chartered second row, unpopulated until `unicode-props`
 * ships an actual \w-shaped producer (`pcrec_def_tag_applies`'s own
 * comment — the tag answers `false` unconditionally until then, which
 * is sound: the row falls through to its DEF_ALWAYS entry). */
#define ESC_SET_D(sel, syn, mod, eng, note, q, ce, bits, neg, def) \
    {RK_ESC, (sel), NULL, (syn), M_##mod, FLAV_PCRE2, (eng), RS_MODULE, RD_MODULE, NULL, NULL, 0, (note), ROADMAP_PLANNED, (q), (ce), 0, NULL, {PORT_SET, false, (neg), (bits), NULL}, {PORT_SET, false, (neg), (bits), NULL}, NULL, (def)}
/* as ESC, but inside a class the byte is BASE syntax: one fixed literal,
 * carried as a BASE scalar class port (MOD-0.3d — the port replaced
 * RF_CLASS_BASE; ExtPort.base means the gate never touches it). */
/* [M6.5.2] `afn` is the ATOM-position producer. The two rows using this macro
 * are `\k` and `\g`, and both gained one with module `backrefs`; the
 * parameter exists rather than a second macro because the CLASS half — a base
 * literal fallback, ungated — is the fact the macro is named for and it does
 * not move. A row wanting no atom producer writes `NO_PORT` longhand rather
 * than passing NULL here, so this macro never has to mean two things. */
#define ESC_CLASS_SCALAR(sel, syn, mod, eng, note, q, ce, lit, afn) \
    {RK_ESC, (sel), NULL, (syn), M_##mod, FLAV_PCRE2, (eng), RS_MODULE, RD_MODULE, NULL, NULL, 0, (note), ROADMAP_PLANNED, (q), (ce), 0, NULL, {PORT_FN, false, 0, NULL, (afn)}, {PORT_SCALAR, true, (lit), NULL, NULL}, NULL, NULL}
/* \0..\9 -> "\N (backreference/octal) requires module 'backrefs'".
 * NOT named ESC_OCTAL: \1..\9 are never octal in PCRE2 — see the note above
 * the digit rows. The macro is named for the DIAGNOSTIC SHAPE it produces,
 * which is a different thing from the construct's semantics. */
/* as ESC, but PCRE2 forbids the construct INSIDE a class and always will, so
 * the in-class answer must promise no module (R9/SPEC-classes-F1). */
#define ESC_CLASS_INVALID(sel, syn, mod, eng, note, q, ce) \
    {RK_ESC, (sel), NULL, (syn), M_##mod, FLAV_PCRE2, (eng), RS_MODULE, RD_MODULE, NULL, NULL, RF_CLASS_INVALID, (note), ROADMAP_PLANNED, (q), (ce), 0, NULL, NO_PORT, NO_PORT, NULL, NULL}
/* [DD-11.1] as ESC_CLASS_INVALID, but with a `definitions` array — `\R`'s
 * only customer today (definitions_table.md §1: "the definitions table can
 * carry an unbuilt row's definition as data before any producer exists";
 * `\R` is module `misc`, currently UNBUILT). `\X`/`\C` stay plain
 * ESC_CLASS_INVALID rows: neither stands for another core-syntax construct
 * (§1's own exclusion list), so neither gets a `definitions` entry. */
#define ESC_CLASS_INVALID_D(sel, syn, mod, eng, note, q, ce, def) \
    {RK_ESC, (sel), NULL, (syn), M_##mod, FLAV_PCRE2, (eng), RS_MODULE, RD_MODULE, NULL, NULL, RF_CLASS_INVALID, (note), ROADMAP_PLANNED, (q), (ce), 0, NULL, NO_PORT, NO_PORT, NULL, (def)}
/* as ESC/GROUP, but the LEXICAL row kind (design §13.3): a tokenizer mode,
 * not an atom — no class port, no AST port when ports land. The macros force
 * QF_LEXICAL rather than take a `q`, because registry_check requires
 * RF_LEXICAL <=> QF_LEXICAL and a macro that could disagree with itself
 * would be the drift the pairing exists to catch. */
#define ESC_LEXICAL(sel, syn, mod, eng, note, ce) \
    {RK_ESC, (sel), NULL, (syn), M_##mod, FLAV_PCRE2, (eng), RS_MODULE, RD_MODULE, NULL, NULL, RF_LEXICAL, (note), ROADMAP_PLANNED, QF_LEXICAL, (ce), 0, NULL, NO_PORT, NO_PORT, NULL, NULL}
#define GROUP_LEXICAL(sel, syn, mod, eng, note) \
    {RK_GROUP, (sel), NULL, (syn), M_##mod, FLAV_PCRE2, (eng), RS_MODULE, RD_MODULE, NULL, NULL, RF_LEXICAL, (note), ROADMAP_PLANNED, QF_LEXICAL, NULL, 0, NULL, NO_PORT, NO_PORT, NULL, NULL}
#define ESC_DIGIT(sel, syn, eng, note, q, ce) \
    {RK_ESC, (sel), NULL, (syn), M_backrefs, FLAV_PCRE2, (eng), RS_MODULE, RD_MODULE_OCTAL, NULL, NULL, 0, (note), ROADMAP_PLANNED, (q), (ce), 0, NULL, {PORT_FN, false, 0, NULL, pcrec_brport_digit}, {PORT_FN, true, 0, NULL, pcrec_clsport_octal}, NULL, NULL}
/* [DD-11.1] as ESC_DIGIT, but with a `definitions` array — `\0`'s only
 * customer: unlike `\1`..`\9` (CONDITIONALLY octal, only when no such
 * capture group exists — a parse-state fact this table's closed DefTag
 * enum does not model), `\0` is UNCONDITIONALLY octal ("never a
 * backreference (there is no group 0)", this row's own `note`), which is
 * exactly the unconditional-replacement shape every other row in this
 * table has. */
#define ESC_DIGIT_D(sel, syn, eng, note, q, ce, def) \
    {RK_ESC, (sel), NULL, (syn), M_backrefs, FLAV_PCRE2, (eng), RS_MODULE, RD_MODULE_OCTAL, NULL, NULL, 0, (note), ROADMAP_PLANNED, (q), (ce), 0, NULL, {PORT_FN, false, 0, NULL, pcrec_brport_digit}, {PORT_FN, true, 0, NULL, pcrec_clsport_octal}, NULL, (def)}
/* as ESC_DIGIT, but the class answer is one fixed literal byte: \8 and \9
 * (8 and 9 are not octal digits, so no continuation is ever read — measured
 * at FIX-3, the [\81] cell). \0..\7 need the octal SCAN and get a PORT_FN
 * class port when it wires in (slice 3). */
#define ESC_DIGIT_LIT(sel, syn, eng, note, q, ce, lit) \
    {RK_ESC, (sel), NULL, (syn), M_backrefs, FLAV_PCRE2, (eng), RS_MODULE, RD_MODULE_OCTAL, NULL, NULL, 0, (note), ROADMAP_PLANNED, (q), (ce), 0, NULL, {PORT_FN, false, 0, NULL, pcrec_brport_digit}, {PORT_SCALAR, true, (lit), NULL, NULL}, NULL, NULL}
/* [DD-11.4b] a BASE-TIER literal escape with a `definitions` entry and
 * nothing else (docs/design/definitions_table.md's architectural note after
 * §1's table, [DD-11.4b] in §6's sequence, manager's ruling: one mechanism
 * rather than a second row-less table). `\a \e \f \n \r \t` decode directly
 * in `esc_char_value` (src/parse/parse.c) with NO doorway and NO row today
 * (D24's own base-tier boundary) — this row exists PURELY to give
 * `RegRow.definitions` a home and to answer `--list-syntax`/
 * `--list-definitions` truthfully; it is looked up by NEITHER
 * `pcrec_registry_arbitrate` at parse time (esc_char_value's switch always
 * answers first for these six bytes, exactly as it did before this row
 * existed) NOR any other consumer on the compile path — `no new doorway, no
 * new lookup on the base path` (the substep's own gate) holds by
 * construction, the same way the sole existing RS_BASE row (`(?:...)`,
 * group_rows below) never routes through the `(?` doorway's dispatch
 * either. `class_expect` is `esc_char_value`'s OWN decoded value — the
 * function is called from both `esc_atom` (atom position) and
 * `esc_class_value` (class position, parse.c), so the two positions are
 * identical by construction and the value is not a second measurement. */
#define ESC_BASE_D(sel, syn, note, ce, def) \
    {RK_ESC, (sel), NULL, (syn), 0, NULL, FLAV_PCRE2, ANY_ENGINE, RS_BASE, RD_NONE, NULL, NULL, 0, (note), ROADMAP_NONE, QF_YES, (ce), 0, NULL, NO_PORT, NO_PORT, NULL, (def)}
/* (?X -> "(?X...) requires module 'M'" */
#define GROUP(sel, syn, mod, eng, note, q) \
    {RK_GROUP, (sel), NULL, (syn), M_##mod, FLAV_PCRE2, (eng), RS_MODULE, RD_MODULE, NULL, NULL, 0, (note), ROADMAP_PLANNED, (q), NULL, 0, NULL, NO_PORT, NO_PORT, NULL, NULL}
/* as GROUP, but the construct is OUT-OF-SCOPE in docs/pcre2_compliance.md and
 * the diagnostic must not promise the module (K14, design Â§17.2). The module
 * and feature stay as CLASSIFICATION -- which doorway family owns the row --
 * they are simply never rendered as a promise. */
#define GROUP_NEVER(sel, syn, mod, eng, note, q) \
    {RK_GROUP, (sel), NULL, (syn), M_##mod, FLAV_PCRE2, (eng), RS_MODULE, RD_MODULE, NULL, NULL, 0, (note), ROADMAP_NEVER, (q), NULL, 0, NULL, NO_PORT, NO_PORT, NULL, NULL}
/* an inline option setting: the construct is the whole RUN, not this byte.
 * RF_OPTION_RUN retired at MOD-0.5b — the `recognise` field now carries the
 * same fact, as a MARKER (src/parse/mod_modifiers.c's own comment on
 * pcrec_registry_option_run_recognise says why it is a marker and not the
 * check itself, and internal.h's retired-RF_OPTION_RUN comment says where
 * the real check moved to: ext.c, gated on this pointer instead of the bit). */
#define GROUP_OPT(sel, syn, note, q) \
    {RK_GROUP, (sel), NULL, (syn), M_modifiers, FLAV_PCRE2, ANY_ENGINE, RS_MODULE, RD_MODULE, NULL, NULL, 0, (note), ROADMAP_PLANNED, (q), NULL, 0, pcrec_registry_option_run_recognise, {PORT_FN, false, 0, NULL, pcrec_modport_optrun}, NO_PORT, NULL, NULL}
/* as GROUP, but the row applies only when `tl` FOLLOWS the selector byte (SR-9).
 * One byte, several constructs: `(?P<` `(?P=` `(?P>` are a named group, a
 * backreference and a subroutine call, and answering all three with one module
 * was a tier-2 misattribution under D26. */
#define GROUP_T(sel, tl, syn, mod, eng, note, q) \
    {RK_GROUP, (sel), (tl), (syn), M_##mod, FLAV_PCRE2, (eng), RS_MODULE, RD_MODULE, NULL, NULL, 0, (note), ROADMAP_PLANNED, (q), NULL, 25, NULL, NO_PORT, NO_PORT, NULL, NULL}
/* [M6.6.2] as GROUP / GROUP_T, but with module `lookaround`'s ONE port wired
 * into the `aport` slot. Six rows, one port function, because the six
 * constructs differ only in the three `Ast.u.look` flags `pcrec_laport_group`
 * reads off this row's own `sel`/`tail` (design §8.1) — a second port would be
 * a second place the `(?<`-tail split is decided.
 *
 * A MACRO AND NOT SIX LONGHAND ROWS, and the distinction this file's header
 * draws is the one that licenses it: what must not hide inside a macro is a
 * row that MEANS REJECTED. These mean the opposite — every field below is
 * fixed for all six constructs (module, flavour, VM_ONLY, RS_MODULE,
 * ROADMAP_PLANNED, QF_YES, the port) and only the spelling and the note vary,
 * so six copies would be six chances to wire five of them. */
#define GROUP_LA(sel, syn, note) \
    {RK_GROUP, (sel), NULL, (syn), M_lookaround, FLAV_PCRE2, VM_ONLY, RS_MODULE, RD_MODULE, NULL, NULL, 0, (note), ROADMAP_PLANNED, QF_YES, NULL, 0, NULL, {PORT_FN, false, 0, NULL, pcrec_laport_group}, NO_PORT, NULL, NULL}
#define GROUP_LA_T(sel, tl, syn, note) \
    {RK_GROUP, (sel), (tl), (syn), M_lookaround, FLAV_PCRE2, VM_ONLY, RS_MODULE, RD_MODULE, NULL, NULL, 0, (note), ROADMAP_PLANNED, QF_YES, NULL, 25, NULL, {PORT_FN, false, 0, NULL, pcrec_laport_group}, NO_PORT, NULL, NULL}
/* [DD-14 wave B+C] as GROUP / GROUP_T, but with one of module `recursion`'s
 * THREE ports wired into `aport`. A macro per port rather than one taking the
 * function, because the three serve three FAMILIES and the family is what a
 * reader of this table needs to see at the row: `RC_NUM` is the absolute
 * numeric family and `(?R)` (design §2.4a's leading-zero rule lives inside the
 * port, which re-reads the whole digit run), `RC_REL` the relative one, and
 * `RC_NAME` the two by-name spellings.
 *
 * THE `quant` COLUMN IS LEFT EXACTLY AS IT WAS, including the nine `QF_NO`
 * values design §8.1 MEASURED WRONG (`^(a)(?1)*$` compiles on 10.46, as do all
 * twelve quantified spellings). Fixing it is wave F's row — it is a
 * documentation fact with no parser consumer (`quant` is read only by
 * `--list-syntax` and by tests/reject) — and moving it here would put a wave-F
 * deliverable inside a wave-B+C diff. */
#define GROUP_RC(sel, syn, note, q, port, fam) \
    {RK_GROUP, (sel), NULL, (syn), M_recursion, FLAV_PCRE2, VM_ONLY, RS_MODULE, RD_MODULE, NULL, NULL, 0, (note), ROADMAP_PLANNED, (q), NULL, 0, NULL, {PORT_FN, false, 0, NULL, (port)}, NO_PORT, (fam), NULL}
#define GROUP_RC_T(sel, tl, syn, note, q, port, fam) \
    {RK_GROUP, (sel), (tl), (syn), M_recursion, FLAV_PCRE2, VM_ONLY, RS_MODULE, RD_MODULE, NULL, NULL, 0, (note), ROADMAP_PLANNED, (q), NULL, 25, NULL, {PORT_FN, false, 0, NULL, (port)}, NO_PORT, (fam), NULL}
/* [DD-14 wave F] AN INDEX ROW FOR ONE OF MODULE `recursion`'s MISSING
 * SPELLINGS (RF_INDEX, internal.h; D71 item 3). Design §8.1 MEASURED four
 * families of spelling that PCRE2 accepts, that pcrec ALREADY COMPILES
 * CORRECTLY, and that no row in this table names — so `--list-syntax`,
 * `tests/reject/` and the compliance index were all silent about them while
 * the compiler handled them. This macro is how they get a line.
 *
 * IT NEVER DISPATCHES, and that is the whole point of the flag: `(?10)`
 * enters at the `(?1)` row's byte and `\g<0>` at the `\g<` row's, exactly as
 * they did before this wave. `pcrec_rcport_num` / `_rel` / `pcrec_brport_g`
 * re-read the whole digit run and were always the code that answered — the
 * SPELLINGS are what were missing from the inventory, never the behaviour,
 * which is why every one of these rows is `built` on the day it lands and why
 * this wave moves no artifact byte.
 *
 * `sel` IS THE REAL DISPATCHING BYTE rather than REG_SEL_ANY, unlike the
 * twelve `(*` alpha rows: those genuinely have no byte-keyed identity (their
 * doorway decides by name), while these do — `(?10)` really is elected by the
 * `1` bucket. Recording the true byte keeps the row HONEST about where its
 * spelling enters, and RF_INDEX is what keeps it from being elected there:
 * `pcrec_registry_arbitrate` skips the flag before any arm runs, which
 * `tests/registry/registry_check.c`'s dispatch sweep asserts over every
 * (kind x selector x text).
 *
 * `family` IS THE PRIMARY ROW'S OWN `syntax` and is REQUIRED (the flag's
 * contract): an index row exists to be a member of a family, and the family
 * is the line the index actually prints. */
#define INDEX_RC(kind, sel, syn, note, q, ce, fam) \
    {(kind), (sel), NULL, (syn), M_recursion, FLAV_PCRE2, VM_ONLY, RS_MODULE, RD_MODULE, NULL, NULL, RF_INDEX, (note), ROADMAP_PLANNED, (q), (ce), 0, NULL, NO_PORT, NO_PORT, (fam), NULL}
/* PCRE2 rejects it, and the byte that decides is the one AFTER the selector.
 * Takes `ce`: its one caller is an RK_ESC row, which is class-reachable.
 * Rank 25 = the tailed tier (MOD-0.2; see RegRow.rank) — its caller is the
 * SHORT half of the `\N` prefix pair, outranked by `\N{U+`'s 70 below. */
#define REJECTED_T(kind, sel, tl, syn, msg, note, q, ce) \
    {(kind), (sel), (tl), (syn), 0, NULL, FLAV_PCRE2, 0, RS_REJECTED, RD_FIXED, (msg), NULL, 0, (note), ROADMAP_NEVER, (q), (ce), 25, NULL, NO_PORT, NO_PORT, NULL, NULL}
/* a construct whose entire diagnostic is fixed text rather than a template.
 * Verb-kind callers only today, hence no `ce`; an esc/class-bracket caller
 * would need one (registry_check fails the NULL rather than letting it read
 * as a fact). */
#define FIXED(kind, sel, syn, mod, eng, msg, note, q) \
    {(kind), (sel), NULL, (syn), M_##mod, FLAV_PCRE2, (eng), RS_MODULE, RD_FIXED, (msg), NULL, 0, (note), ROADMAP_PLANNED, (q), NULL, 0, NULL, NO_PORT, NO_PORT, NULL, NULL}
/* PCRE2 rejects it too: no module to name, no feature to enable, no engine to
 * lower to. Agreement IS compliance. Group-kind callers only today — see FIXED. */
#define REJECTED(kind, sel, syn, msg, note, q) \
    {(kind), (sel), NULL, (syn), 0, NULL, FLAV_PCRE2, 0, RS_REJECTED, RD_FIXED, (msg), NULL, 0, (note), ROADMAP_NEVER, (q), NULL, 0, NULL, NO_PORT, NO_PORT, NULL, NULL}
/* as REJECTED, but a delimiter-pair construct: RF_CLASS_DELIM carries the two
 * recognition rules that SR-2 moved out of parse.c — see internal.h. Both
 * callers are class-bracket rows, so `ce` is required. */
#define REJECTED_DELIM(kind, sel, syn, msg, note, q, ce) \
    {(kind), (sel), NULL, (syn), 0, NULL, FLAV_PCRE2, 0, RS_REJECTED, RD_FIXED, (msg), \
     NULL, RF_CLASS_DELIM, (note), ROADMAP_NEVER, (q), (ce), 0, NULL, NO_PORT, NO_PORT, NULL, NULL}

/* ---- doorway 1: after '\' ----------------------------------------------
 * Only non-base escapes. \n \t \r \f \a \e \xHH decode in parse.c and never
 * arrive here. */
/* The `\N{` row's recogniser (MOD-0.3f, R16 engine critic): PCRE2 tries
 * the brace as a QUANTIFIER first — `\N{2,3}` is bare `\N` repeated, and
 * err 104/105 bodies prove the quantifier parser claimed the brace — and
 * only a non-quantifier-shaped body is the (unsupported) `\N{name}`
 * construct. So this recogniser answers for a `{` tail ONLY when the brace
 * is NOT quantifier-shaped; on `{2,3}` it declines, the bare `\N` fallback
 * wins the arbitration, and try_quant consumes the brace through the SAME
 * shape scan (one home, two callers — see pcrec_brace_quant_shape).
 * Measured boundary in tests/probes/probe_nbrace.c. */
static bool recognise_N_name_brace(const char *at, size_t avail,
                                   const char *tail)
{
    if (!pcrec_recognise_tail_default(at, avail, tail)) return false;
    return !pcrec_brace_quant_shape(at, avail);
}

/* [DD-11.1] the class-escape family's definitions (D85, Frank's ruling,
 * r43): each byte set restated as a core-syntax STRING, oracle-verified
 * against libpcre2 10.46 byte-for-byte this pass (definitions_table.md
 * revision 1's own probes) — `\d`==`[0-9]`, `\s`==`[\t\n\x0b\f\r ]`,
 * `\w`==`[A-Za-z0-9_]`, `\h`==`[\t \xa0]`, `\v`==`[\n\x0b\f\r\x85]`, each
 * confirmed a byte-for-byte set match, 0 disagreements. */
static const RegDef d_def[] = { {DEFK_STR, DEF_ALWAYS, "[0-9]", NULL, NULL}, {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL} };
static const RegDef D_def[] = { {DEFK_STR, DEF_ALWAYS, "[^0-9]", NULL, NULL}, {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL} };
static const RegDef s_def[] = { {DEFK_STR, DEF_ALWAYS, "[\\t\\n\\x0b\\f\\r ]", NULL, NULL}, {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL} };
static const RegDef S_def[] = { {DEFK_STR, DEF_ALWAYS, "[^\\t\\n\\x0b\\f\\r ]", NULL, NULL}, {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL} };
static const RegDef w_def[] = { {DEFK_STR, DEF_ALWAYS, "[A-Za-z0-9_]", NULL, NULL}, {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL} };
static const RegDef W_def[] = { {DEFK_STR, DEF_ALWAYS, "[^A-Za-z0-9_]", NULL, NULL}, {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL} };
static const RegDef h_def[] = { {DEFK_STR, DEF_ALWAYS, "[\\t \\xa0]", NULL, NULL}, {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL} };
static const RegDef H_def[] = { {DEFK_STR, DEF_ALWAYS, "[^\\t \\xa0]", NULL, NULL}, {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL} };
static const RegDef v_def[] = { {DEFK_STR, DEF_ALWAYS, "[\\n\\x0b\\f\\r\\x85]", NULL, NULL}, {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL} };
static const RegDef V_def[] = { {DEFK_STR, DEF_ALWAYS, "[^\\n\\x0b\\f\\r\\x85]", NULL, NULL}, {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL} };
static const RegDef bare_N_def[] = { {DEFK_STR, DEF_ALWAYS, "[^\\n]", NULL, NULL}, {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL} };

/* [DD-11.1] `\R`'s definition (definitions_table.md §1/§4): any Unicode
 * newline sequence, atomic so the CRLF branch cannot be torn by backtracking
 * — PCRE2's own definition, verified against libpcre2 10.46 (11/11 subjects
 * agree, incl. "\r\n", "\r\r", empty). `\R` is module `misc`, UNBUILT today;
 * the table carries the definition as data ahead of any producer. */
static const RegDef R_def[] = {
    {DEFK_STR, DEF_ALWAYS, "(?>\\r\\n|\\n|\\x0b|\\f|\\r|\\x85)", NULL, NULL},
    {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL},
};

/* [DD-11.1] `\b`/`\B`'s shared definition family (definitions_table.md §1/
 * §4): unconditional (DEF_ALWAYS-only — neither has an identity case, since
 * neither is in the reduced core set, §2), each referencing `\w` — itself
 * now a real row (§3 item 5's un-parked recursion guard is [DD-11.4], not a
 * blocker for populating these two). Verified against libpcre2 10.46 at
 * docs/design/lookaround_design.md:1792-1793 (0 disagreements). */
static const RegDef wordb_def[] = {
    {DEFK_STR, DEF_ALWAYS, "(?:(?<=\\w)(?!\\w)|(?<!\\w)(?=\\w))", NULL, NULL},
    {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL},
};
static const RegDef nwordb_def[] = {
    {DEFK_STR, DEF_ALWAYS, "(?:(?<=\\w)(?=\\w)|(?<!\\w)(?!\\w))", NULL, NULL},
    {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL},
};

/* [DD-11.4b] the 6 FIXED base-tier literal escapes' definitions — see
 * ESC_BASE_D's own comment (above the macro) for why these rows exist at
 * all. Each is DEF_ALWAYS-only (no identity case: none of these six is
 * itself the string it substitutes, `\x07` etc. is base/core `\x` syntax
 * a level further down, not a second table entry). */
static const RegDef a_def[] = { {DEFK_STR, DEF_ALWAYS, "\\x07", NULL, NULL}, {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL} };
static const RegDef e_def[] = { {DEFK_STR, DEF_ALWAYS, "\\x1b", NULL, NULL}, {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL} };
static const RegDef f_def[] = { {DEFK_STR, DEF_ALWAYS, "\\x0c", NULL, NULL}, {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL} };
static const RegDef n_def[] = { {DEFK_STR, DEF_ALWAYS, "\\x0a", NULL, NULL}, {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL} };
static const RegDef r_def[] = { {DEFK_STR, DEF_ALWAYS, "\\x0d", NULL, NULL}, {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL} };
static const RegDef t_def[] = { {DEFK_STR, DEF_ALWAYS, "\\x09", NULL, NULL}, {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL} };

/* [DD-11.1] the 5 DEFK_TEXTFN rows (manager ruling, 2026-08-29): each is
 * parameterized by TEXT AT THE OCCURRENCE, so no fixed `DEFK_STR` string
 * or AST-operand `DEFK_BUILDER` can carry its definition — see internal.h's
 * comment before `DefKind` for the full ruling. `str` here is a
 * human-readable TEMPLATE for `--list-definitions`, never spliced. `\c`
 * and `\o{}` are module `misc`, UNBUILT; `\N{U+` is module `unicode-props`,
 * UNBUILT; bare `\x` and `\0` are already real (base tier / module
 * `backrefs`). See src/parse/definitions.c's own header on this block for
 * why an unbuilt row's textfn is sound to write today (the `\R` precedent). */
static const RegDef cx_def[] = {
    {DEFK_TEXTFN, DEF_ALWAYS, "\\cX = byte (X xor 0x40)", NULL, pcrec_def_text_cx},
    {DEFK_END,    DEF_ALWAYS, NULL, NULL, NULL},
};
static const RegDef bare_x_def[] = {
    {DEFK_TEXTFN, DEF_ALWAYS, "\\xHH or \\x{HHHH} = byte HH..HHHH (hex)", NULL, pcrec_def_text_hex},
    {DEFK_END,    DEF_ALWAYS, NULL, NULL, NULL},
};
static const RegDef o_def[] = {
    {DEFK_TEXTFN, DEF_ALWAYS, "\\o{OOO} = byte OOO (octal)", NULL, pcrec_def_text_octal},
    {DEFK_END,    DEF_ALWAYS, NULL, NULL, NULL},
};
static const RegDef octal0_def[] = {
    {DEFK_TEXTFN, DEF_ALWAYS, "\\0OO = byte OOO (octal, never a backreference)", NULL, pcrec_def_text_octal},
    {DEFK_END,    DEF_ALWAYS, NULL, NULL, NULL},
};
static const RegDef unicode_def[] = {
    {DEFK_TEXTFN, DEF_ALWAYS, "\\N{U+HHHH} = code point HHHH -- byte today, a sequence under utf8 (encoding tag's 2nd row)", NULL, pcrec_def_text_unicode},
    {DEFK_END,    DEF_ALWAYS, NULL, NULL, NULL},
};

static const RegRow esc_rows[] = {
ESC_SET_D('d', "\\d", classes, ANY_ENGINE, "any decimal digit", QF_YES, "set 10", pcrec_cls_digit_esc, 0, d_def),
ESC_SET_D('D', "\\D", classes, ANY_ENGINE, "any character that is not a decimal digit", QF_YES, "set 246", pcrec_cls_digit_esc, 1, D_def),
ESC_SET_D('s', "\\s", classes, ANY_ENGINE, "any whitespace character", QF_YES, "set 6", pcrec_cls_space_esc, 0, s_def),
ESC_SET_D('S', "\\S", classes, ANY_ENGINE, "any character that is not whitespace", QF_YES, "set 250", pcrec_cls_space_esc, 1, S_def),
ESC_SET_D('w', "\\w", classes, ANY_ENGINE, "any word character (letter, digit or underscore)", QF_YES, "set 63", pcrec_cls_word_esc, 0, w_def),
ESC_SET_D('W', "\\W", classes, ANY_ENGINE, "any character that is not a word character", QF_YES, "set 193", pcrec_cls_word_esc, 1, W_def),
ESC_SET_D('h', "\\h", classes, ANY_ENGINE, "any horizontal whitespace character", QF_YES, "set 3", pcrec_cls_hspace, 0, h_def),
ESC_SET_D('H', "\\H", classes, ANY_ENGINE, "any character that is not horizontal whitespace", QF_YES, "set 253", pcrec_cls_hspace, 1, H_def),
/* THE ROW THIS WHOLE FILE EXISTS FOR. PCRE2's `\v` is vertical WHITESPACE —
 * 0x0a 0x0b 0x0c 0x0d 0x85 — not the vertical tab 0x0B. pcrec decoded it as
 * 0x0B until 2026-08-09; the corpus certified the bug because python `re`, the
 * base-tier oracle, reads `\v` as 0x0B too. It is also the only known
 * flavour-varying row, i.e. the single member of the set SR-7 is deferred for. */
ESC_SET_D('v', "\\v", classes, ANY_ENGINE, "any vertical whitespace character (NOT vertical tab; python re disagrees)", QF_YES, "set 5", pcrec_cls_vspace, 0, v_def),
ESC_SET_D('V', "\\V", classes, ANY_ENGINE, "any character that is not vertical whitespace", QF_YES, "set 251", pcrec_cls_vspace, 1, V_def),
/* `\N` IS THREE CONSTRUCTS, split by tail at SR-9. The bare escape is "any
 * character except newline"; `\N{U+hhhh}` is a Unicode code point; `\N{name}`
 * is a Perl construct PCRE2 states it does not support. Measured against
 * libpcre2 10.46:
 *
 *     \N            compiles
 *     \N{U+0041}    error 193  "\N{U+dddd} is supported only in Unicode (UTF) mode"
 *     \N{}  \N{name}  error 137  "PCRE2 does not support \F, \L, \l, \N{name}, \U, or \u"
 *
 * 193 is a CAPABILITY refusal, not a syntax one — our oracle compiles with
 * options = 0 and so can never be in UTF mode, exactly as `(*TURKISH_CASING)`'s
 * error 204 is bucketed with "PCRE2 recognised the construct" (Q1). So the
 * construct is real and `unicode-props` owns it. 137 is PCRE2 saying it will
 * never support the construct, which is what RS_REJECTED is for.
 *
 * The fact that `\N{U+hhhh}` is a distinct construct was ALREADY IN THIS FILE,
 * in the bare row's own `note`, correct and inert, because `note` is read by no
 * check (R8's finding, and R9's sharpest instance of it). SR-9 is what turned
 * it into a row that answers. */
/* \N produces at ATOM position only ([^\n], the newline table's
 * complement); its class port stays NONE — permanently invalid, err 171,
 * wording tier 3 (D33 §3). Longhand because it is the one row with a
 * producing aport and a class-invalid flag at once. */
{RK_ESC, 'N', NULL, "\\N", M_classes, FLAV_PCRE2, ANY_ENGINE, RS_MODULE, RD_MODULE, NULL, NULL, RF_CLASS_INVALID, "any character except newline (PCRE2 forbids it inside a class)", ROADMAP_PLANNED, QF_YES, "err 171", 0, NULL, {PORT_SET, false, 1, pcrec_cls_newline, NULL}, NO_PORT, NULL, bare_N_def},
/* THE SHORT TAIL IS WRITTEN FIRST ON PURPOSE. These two rows are the only
 * prefix-related tail pair in the table (`{` is a proper prefix of `{U+`), so
 * on `{U+...` text BOTH recognisers answer and rank is the only thing electing
 * the `{U+` row — the one place the ordering between two TAILED ranks is
 * observable (25 vs 70; everywhere else rank only beats the fallback's 0).
 * Keeping `{` first makes row ORDER disagree with the required outcome, so an
 * arbitration that quietly fell back to declaration order produces a wrong
 * answer here instead of a coincidentally right one. Under SR-9's
 * longest-tail-wins engine the same discipline made first-match-wins
 * observable (a sabotage with the rows in the other order produced ZERO
 * failures repository-wide — the measured reason for this ordering);
 * registry_check's arbitration-liveness floor now asserts this pair still
 * produces a triple-answer probe, so its disappearance fails loudly. */
{RK_ESC, 'N', "{", "\\N{name}", 0, NULL, FLAV_PCRE2, 0, RS_REJECTED, RD_FIXED,
 "PCRE2 does not support \\F, \\L, \\l, \\N{name}, \\U, or \\u", NULL, 0,
 "\\N{name} — PCRE2 states it does not support this Perl construct",
 ROADMAP_NEVER, QF_NO, "err 137", 25, recognise_N_name_brace, NO_PORT, NO_PORT, NULL, NULL},
/* K10 FIX (MOD-0.6 phase 2, 2026-08-12): RF_CLASS_INVALID removed. That flag
 * means "PCRE2 forbids this permanently in a class" (R9/SPEC-classes-F1), and
 * it was WRONG on this row — measured against libpcre2 10.46, [\N{U+41}] is
 * error 193 in EVERY class position (bare, leading, trailing, low endpoint,
 * negated: tests/probes/probe_uprops.c), which is recognition-then-mode-
 * refusal, not permanent rejection, exactly as this row's own `note` field
 * already said (R10/C1-7 — the row contradicted itself). Without the flag
 * this row falls through to the ordinary RS_MODULE in-class branch in ext.c,
 * so [\N{U+41}] now reads "\N in a class requires module 'unicode-props'"
 * instead of "\N is not valid inside a character class" — see
 * docs/dev/known_issues.md K10 and docs/design/design_notes_mod06.md §2 for the full
 * field-by-field account of what did and did not change on this row. */
{RK_ESC, 'N', "{U+", "\\N{U+0041}", M_unicode_props, FLAV_PCRE2, ANY_ENGINE,
 RS_MODULE, RD_MODULE, NULL, NULL, 0,
 "a Unicode code point by number — PCRE2 error 193 outside UTF mode, which is recognition, not rejection",
 ROADMAP_PLANNED, QF_NO, "err 193",
 /* rank 70: the LONGER half of the table's one prefix-related tail pair —
  * on `{U+...` text three recognisers answer (bare \N always, `{` as a
  * prefix, and this row) and rank is what elects this one (MOD-0.2). */
 70, NULL, NO_PORT, NO_PORT, NULL, unicode_def},

/* [M6.2] WAVE B: the word-boundary pair gains its ATOM PORT, and the two rows
 * are spelled longhand for the same one field wave A's three needed — `aport`
 * — with every other field byte-for-byte what ESC_CLASS_SCALAR and
 * ESC_CLASS_INVALID respectively built.
 *
 * THE ASYMMETRY BETWEEN THEM IS PCRE2'S AND IS NOT THIS MODULE'S TO TIDY.
 * `\b` keeps its CLASS port: inside a character class `\b` is not an
 * assertion at all, it is BASE syntax for backspace (0x08), which is why the
 * atom port lands beside a live `cport` rather than beside NO_PORT. `\B` has
 * no in-class meaning and keeps RF_CLASS_INVALID — `[\B]` is PCRE2 error 107
 * and always will be, because a class member is not an assertion (the
 * R9/SPEC-classes-F1 rule). The port being an ATOM port only is what keeps
 * both of those true by construction instead of by a second check. */
{RK_ESC, 'b', NULL, "\\b", M_assertions, FLAV_PCRE2, ANY_ENGINE, RS_MODULE,
 RD_MODULE, NULL, NULL, 0,
 "word boundary — but inside a class it is BASE syntax: backspace (0x08)",
 ROADMAP_PLANNED, QF_NO, "char 0x08", 0, NULL,
 {PORT_FN, false, 0, NULL, pcrec_asrtport_atom},
 {PORT_SCALAR, true, 0x08, NULL, NULL}, NULL, wordb_def},
{RK_ESC, 'B', NULL, "\\B", M_assertions, FLAV_PCRE2, ANY_ENGINE, RS_MODULE,
 RD_MODULE, NULL, NULL, RF_CLASS_INVALID, "not a word boundary",
 ROADMAP_PLANNED, QF_NO, "err 107", 0, NULL,
 {PORT_FN, false, 0, NULL, pcrec_asrtport_atom}, NO_PORT, NULL, nwordb_def},
/* [M6.2] WAVE A: the three rows module `assertions` PRODUCES. Longhand
 * rather than ESC_CLASS_INVALID for exactly one field — `aport` — and
 * every other field is byte-for-byte what the macro built, RF_CLASS_INVALID
 * included: `[\A]` is PCRE2 error 107 in every class position and stays so,
 * because a class member is not an assertion and no module will ever make it
 * one (the R9/SPEC-classes-F1 rule; the port is an ATOM port only, so the
 * class position keeps its permanent refusal by construction rather than by
 * a second check). See src/parse/mod_assertions.c for why two of the three
 * are exact aliases of shipped nodes and the third is not — AND for the two
 * things the alias must not be allowed to erase: multiline independence
 * (pinned false on the node, never copied from the scoped state) and the
 * `PCRE2_NOTBOL`/`PCRE2_NOTEOL` distinction between `\A`/`\Z` and `^`/`$`,
 * which is RULED API-PARAM (docs/pcre2_options.md rows 200-201, D38) and is
 * the known future consumer of a provenance field this wave deliberately
 * does not build. */
{RK_ESC, 'A', NULL, "\\A", M_assertions, FLAV_PCRE2, ANY_ENGINE, RS_MODULE,
 RD_MODULE, NULL, NULL, RF_CLASS_INVALID, "start of subject",
 ROADMAP_PLANNED, QF_NO, "err 107", 0, NULL,
 {PORT_FN, false, 0, NULL, pcrec_asrtport_atom}, NO_PORT, NULL, NULL},
{RK_ESC, 'Z', NULL, "\\Z", M_assertions, FLAV_PCRE2, ANY_ENGINE, RS_MODULE,
 RD_MODULE, NULL, NULL, RF_CLASS_INVALID,
 "end of subject, or before a final newline",
 ROADMAP_PLANNED, QF_NO, "err 107", 0, NULL,
 {PORT_FN, false, 0, NULL, pcrec_asrtport_atom}, NO_PORT, NULL, NULL},
{RK_ESC, 'z', NULL, "\\z", M_assertions, FLAV_PCRE2, ANY_ENGINE, RS_MODULE,
 RD_MODULE, NULL, NULL, RF_CLASS_INVALID, "end of subject",
 ROADMAP_PLANNED, QF_NO, "err 107", 0, NULL,
 {PORT_FN, false, 0, NULL, pcrec_asrtport_atom}, NO_PORT, NULL, NULL},
/* [M6.2] WAVE D: `\G` joins the three rows above, longhand for the same one
 * field and with the same RF_CLASS_INVALID (`[\G]` is PCRE2 error 107,
 * measured against libpcre2 10.46 by this wave). Its `syntax` and `desc`
 * strings are UNCHANGED from the ESC_CLASS_INVALID row it replaces — the
 * registry already stated PCRE2's semantics correctly, which is what
 * assertions_design.md §4 quotes. */
{RK_ESC, 'G', NULL, "\\G", M_assertions, FLAV_PCRE2, ANY_ENGINE, RS_MODULE,
 RD_MODULE, NULL, NULL, RF_CLASS_INVALID,
 "first matching position in the subject",
 ROADMAP_PLANNED, QF_NO, "err 107", 0, NULL,
 {PORT_FN, false, 0, NULL, pcrec_asrtport_atom}, NO_PORT, NULL, NULL},
/* [M6.2] WAVE E: `\K` gains its ATOM PORT, spelled longhand for the one field
 * the `\G` row above needed and for the same reason — every other field is
 * byte-for-byte what ESC_CLASS_INVALID built, `RF_CLASS_INVALID` included
 * (`[\K]` is PCRE2 error 107, measured against libpcre2 10.46 by this wave).
 *
 * `VM_ONLY` IS THE ONE FIELD THAT MAKES THIS ROW DIFFERENT FROM EVERY OTHER
 * `assertions` ROW, and it has said so since before there was a producer.
 * Until this wave it was inert: `tests/registry/registry_check.c`'s
 * capability tripwire asserts that every VM_ONLY-masked RS_MODULE row has NO
 * wired producer, precisely so that the day a module wires the first one, THAT
 * check fails and names `src/opt/select_engine.c` as the thing to build BEFORE
 * the producer lands rather than after. This wave is that day; the second
 * `forces_*` row is what discharges it. */
{RK_ESC, 'K', NULL, "\\K", M_assertions, FLAV_PCRE2, VM_ONLY, RS_MODULE,
 RD_MODULE, NULL, NULL, RF_CLASS_INVALID,
 "reset the reported start of the match",
 ROADMAP_PLANNED, QF_NO, "err 107", 0, NULL,
 {PORT_FN, false, 0, NULL, pcrec_asrtport_atom}, NO_PORT, NULL, NULL},

/* FIX-3 (K13): CLASS_BASE, because inside a class there is no such construct
 * at all — PCRE2's check_escape falls back to the LITERAL letter (`[\k<n>]`
 * matches k < n >), so the class position is base syntax exactly as `\b` is.
 * The ten digit rows carry the same flag: `[\0]`..`[\7]` are octal there and
 * `[\8]` `[\9]` are the literal digits. Measured: tests/probes/probe_fix3.c. */
/* [M6.5.2] BOTH ROWS GAIN AN ATOM PRODUCER, and `\g`'s doorway turns out to
 * carry TWO CONSTRUCTS where the table had one row.
 *
 * MEASURED discriminator (backrefs_design.md §2, `out/spellings.txt`): a
 * SUBROUTINE call re-runs the group's PATTERN, so `^(a|b)\g<1>$` matches "ab";
 * a BACKREFERENCE compares the captured TEXT, so `^(a|b)\1$`, `^(a|b)\g{1}$`
 * and `^(a|b)\g1$` all report NO MATCH on that subject. The split runs exactly
 * along the DELIMITER — braces and bare digits are backreferences, angle
 * brackets and single quotes are subroutine calls — so the two halves belong
 * to two different modules and this module may claim only one of them.
 *
 * Claiming both would be a MISCOMPILE of the kind D26 tier 1 forbids, so the
 * `<` and `'` tails get their own rows below, module `recursion`, born
 * UNBUILT. That is `registry.c`'s own `(?P=` / `(?P>` split exactly, and the
 * arbitration that makes it work is measured rather than assumed: two
 * `RK_ESC` rows in ONE `(kind, sel)` bucket, elected by tail and rank, is the
 * shipped `\N{` / `\N{U+` shape. The base `\g` row is rank 0, so the two
 * tailed rows outrank it and this module's port never sees `\g<` or `\g'`.
 *
 * [DD-14 wave D] AND THE TWO TAILED ROWS BELOW NOW SHARE THAT SAME PORT
 * FUNCTION, `pcrec_brport_g` — not a second one. Design §4.2 ruled it "NOT A
 * NEW PORT" precisely because arbitration, not the port, is what keeps a
 * `\g<1>` call from ever being read as a `\g{1}` reference: whichever row
 * wins the tail race is the row whose `at`/`from` reach the port, and
 * `pcrec_brport_g`'s own `<`/`'` arms (mod_backrefs.c) discriminate on the
 * SAME byte the registry just arbitrated on. `pcrec_call_node`/
 * `pcrec_call_by_name` (mod_recursion.c) are what keep the CALL's zero
 * family and name rule in that module rather than this one's port growing a
 * second copy of either. */
ESC_CLASS_SCALAR('k', "\\k<name>", backrefs, VM_ONLY, "backreference by name: \\k<n> \\k'n' \\k{n} — literal 'k' inside a class", QF_NO, "set 7", 'k', pcrec_brport_k),
ESC_CLASS_SCALAR('g', "\\g{-1}",   backrefs, VM_ONLY, "backreference by number or relative position: \\g1 \\g{-1} \\g{name} — literal 'g' inside a class", QF_NO, "err 108", 'g', pcrec_brport_g),
/* The subroutine half. `class_expect` is MEASURED for each row's own syntax
 * (`[\g<1>]` is the four bytes g < 1 >, `[\g'1']` the three g ' 1) because
 * inside a class `\g` is the literal letter and the rest of the spelling is
 * ordinary members — the same base fallback the row above carries, which is
 * why these two carry the identical BASE scalar class port rather than
 * NO_PORT. Without it, `[\g<]` would stop being the letter `g` the day these
 * rows landed: the class doorway arbitrates on the same tail. */
{RK_ESC, 'g', "<", "\\g<1>", M_recursion, FLAV_PCRE2, VM_ONLY, RS_MODULE,
 RD_MODULE, NULL, NULL, 0,
 "subroutine call into a group by number or name: \\g<1> \\g<name> — NOT a "
 "backreference (it re-runs the group's pattern)",
 ROADMAP_PLANNED, QF_YES, "set 4", 25, NULL,
 {PORT_FN, false, 0, NULL, pcrec_brport_g}, {PORT_SCALAR, true, 'g', NULL, NULL}, NULL, NULL},
{RK_ESC, 'g', "'", "\\g'1'", M_recursion, FLAV_PCRE2, VM_ONLY, RS_MODULE,
 RD_MODULE, NULL, NULL, 0,
 "subroutine call into a group, quoted spelling: \\g'1' \\g'name' — NOT a "
 "backreference",
 ROADMAP_PLANNED, QF_YES, "set 3", 25, NULL,
 {PORT_FN, false, 0, NULL, pcrec_brport_g}, {PORT_SCALAR, true, 'g', NULL, NULL}, NULL, NULL},
/* [DD-14 wave F] THE FOUR MISSING `\g` SPELLINGS, as INDEX rows (see
 * INDEX_RC above; these are longhand for the ESC kind's `class_expect`, which
 * that macro takes but the four values differ per row and are MEASURED, never
 * reasoned: `[\g<0>]` is the four bytes g < 0 > and `[\g<01>]` the five
 * g < 0 1 >, re-derived here against libpcre2 10.46 by the same census
 * tests/probes/probe_class_expect.c runs).
 *
 * `\g<0>` AND `\g'0'` ARE §2.4's TWO WHOLE-PATTERN SPELLINGS NOBODY LISTED,
 * and the leading-zero pair is §2.4a's rule reaching this doorway: the digit
 * run is read as decimal, so `\g<01>` is GROUP 1 while `\g<00>` is the root
 * — the same one-character-prefix trap the `(?0)` row's note is qualified
 * for, one doorway over. All four are MEASURED compiling and agreeing with
 * libpcre2 today (wave D wired the arms); what was missing is the LINE. */
{RK_ESC, 'g', NULL, "\\g<0>", M_recursion, FLAV_PCRE2, VM_ONLY, RS_MODULE,
 RD_MODULE, NULL, NULL, RF_INDEX,
 "subroutine call to the WHOLE PATTERN, angle-bracket spelling -- \\g<0> and "
 "\\g<00> are the root, \\g<01> is group 1",
 ROADMAP_PLANNED, QF_YES, "set 4", 0, NULL, NO_PORT, NO_PORT, "\\g<1>", NULL},
{RK_ESC, 'g', NULL, "\\g<01>", M_recursion, FLAV_PCRE2, VM_ONLY, RS_MODULE,
 RD_MODULE, NULL, NULL, RF_INDEX,
 "subroutine call into group 1, LEADING-ZERO angle-bracket spelling -- the "
 "whole digit run is read as decimal",
 ROADMAP_PLANNED, QF_YES, "set 5", 0, NULL, NO_PORT, NO_PORT, "\\g<1>", NULL},
{RK_ESC, 'g', NULL, "\\g'0'", M_recursion, FLAV_PCRE2, VM_ONLY, RS_MODULE,
 RD_MODULE, NULL, NULL, RF_INDEX,
 "subroutine call to the WHOLE PATTERN, quoted spelling -- \\g'0' and "
 "\\g'00' are the root, \\g'01' is group 1",
 ROADMAP_PLANNED, QF_YES, "set 3", 0, NULL, NO_PORT, NO_PORT, "\\g'1'", NULL},
{RK_ESC, 'g', NULL, "\\g'01'", M_recursion, FLAV_PCRE2, VM_ONLY, RS_MODULE,
 RD_MODULE, NULL, NULL, RF_INDEX,
 "subroutine call into group 1, LEADING-ZERO quoted spelling -- the whole "
 "digit run is read as decimal",
 ROADMAP_PLANNED, QF_YES, "set 4", 0, NULL, NO_PORT, NO_PORT, "\\g'1'", NULL},

/* MOD-0.6 phase 2: longhand rather than the ESC macro, for exactly one
 * reason — `recognise` carries `pcrec_registry_uprops_recognise`, a MARKER
 * (mod_uprops.c) ext.c keys off by pointer identity to hand off to the
 * body scanner instead of the generic RD_MODULE fallback text. Every other
 * field is unchanged from what ESC(...) would have built: both rows are
 * alone in their (RK_ESC, sel) bucket (no arbitration to affect), `flags`
 * stays 0 (neither is RF_CLASS_INVALID — [\p{L}]/[\P{L}] compile as sets,
 * measured, tests/probes/probe_uprops.c), and `aport`/`cport` stay NO_PORT
 * (no producer this phase — docs/design/design_notes_mod06.md §6). */
{RK_ESC, 'p', NULL, "\\p{L}", M_unicode_props, FLAV_PCRE2, ANY_ENGINE,
 RS_MODULE, RD_MODULE, NULL, NULL, 0,
 "a character with the given Unicode property", ROADMAP_PLANNED, QF_YES, "set 117",
 0, pcrec_registry_uprops_recognise, NO_PORT, NO_PORT, NULL, NULL},
{RK_ESC, 'P', NULL, "\\P{L}", M_unicode_props, FLAV_PCRE2, ANY_ENGINE,
 RS_MODULE, RD_MODULE, NULL, NULL, 0,
 "a character without the given Unicode property", ROADMAP_PLANNED, QF_YES, "set 139",
 0, pcrec_registry_uprops_recognise, NO_PORT, NO_PORT, NULL, NULL},

ESC_LEXICAL('Q', "\\Q", quoting, ANY_ENGINE, "begin literal quoting, until \\E", "err 106"),
ESC_LEXICAL('E', "\\E", quoting, ANY_ENGINE, "end literal quoting begun by \\Q", "err 106"),

ESC_CLASS_INVALID_D('R', "\\R",    misc, ANY_ENGINE, "any Unicode newline sequence", QF_YES, "err 107", R_def),
ESC_CLASS_INVALID('X', "\\X",      misc, ANY_ENGINE, "a Unicode extended grapheme cluster", QF_YES, "err 107"),
ESC_CLASS_INVALID('C', "\\C",      misc, ANY_ENGINE, "one data unit (byte), even in UTF mode", QF_YES, "err 107"),
ESC_D('c', "\\cX",     misc, ANY_ENGINE, "control character: \\cX is X xor 0x40", QF_YES, "char 0x18", cx_def),
ESC_D('o', "\\o{101}", misc, ANY_ENGINE, "character with the given octal code", QF_YES, "char 0x41", o_def),

/* Digits. THESE NOTES WERE WRONG WHEN FIRST WRITTEN, from memory, and an
 * adversarial review caught it — which is the whole reason this file exists, so
 * the correction is recorded rather than quietly applied.
 *
 * The wrong claim was that `\1`..`\9` fall back to an OCTAL escape when no such
 * capture group exists. That is Perl/PCRE1 behaviour and it does NOT survive
 * into PCRE2. Measured against libpcre2 10.46:
 *
 *     \1  \7  \8  \9        -> REJECTED, error 115 "reference to non-existent
 *                              subpattern"  (no groups in the pattern at all)
 *     (a)\1   (a)(b)(c)\3   -> ACCEPTED
 *     (a)\2                 -> REJECTED, error 115
 *     \0   \012   \o{101}   -> ACCEPTED  (the genuine octal forms)
 *
 * So `\1`..`\9` are UNCONDITIONALLY backreferences, and only `\0` is octal.
 * `\0` can never be a backreference either — there is no group 0 to address —
 * which makes it the odd row here: it shares the digit doorway and pcrec's
 * diagnostic, but none of the semantics.
 *
 * pcrec still PRINTS "(backreference/octal)" for all ten. That wording is
 * parse.c's today and SR-2 must reproduce it byte-identically, so the fix
 * belongs to the backrefs module rather than to this table; the note is where
 * the truth lives until then. Recorded in docs/dev/known_issues.md.
 *
 * ENGINES: the rows say VM_ONLY, and that is design intent with a known
 * split behind it — a backref whose group has a FINITE language is regular
 * and an AOT compiler can expand it away statically ((a|b)\1 = aa|bb, pure
 * DFA); only infinite-language groups ((a*)\1) genuinely need the VM. The
 * per-PATTERN engine decision belongs to module `backrefs`; the note with
 * the reasoning is in docs/dev/plan.md's backrefs paragraph (Frank, 2026-08-12).
 *
 * All of the above is the ATOM position. The CLASS position is base
 * semantics since FIX-3 (K13): a backreference is impossible there, so
 * `[\0]`..`[\7]` are octal and `[\8]` `[\9]` the literal digits — since
 * MOD-0.3d carried as BASE class ports (the octal PORT_FN below, scalar
 * data for 8/9) instead of a parse.c special case, so the doorway IS
 * entered and the port answers whatever the enabled set says. Measured
 * cell-by-cell in tests/probes/probe_fix3.c. */
ESC_DIGIT_D('0', "\\0", ANY_ENGINE, "octal escape \\0dd — never a backreference (there is no group 0)", QF_YES, "char 0x00", octal0_def),
ESC_DIGIT('1', "\\1", VM_ONLY, "backreference to capture group 1 (PCRE2 error 115 if no such group)", QF_NO, "char 0x01"),
ESC_DIGIT('2', "\\2", VM_ONLY, "backreference to capture group 2 (PCRE2 error 115 if no such group)", QF_NO, "char 0x02"),
ESC_DIGIT('3', "\\3", VM_ONLY, "backreference to capture group 3 (PCRE2 error 115 if no such group)", QF_NO, "char 0x03"),
ESC_DIGIT('4', "\\4", VM_ONLY, "backreference to capture group 4 (PCRE2 error 115 if no such group)", QF_NO, "char 0x04"),
ESC_DIGIT('5', "\\5", VM_ONLY, "backreference to capture group 5 (PCRE2 error 115 if no such group)", QF_NO, "char 0x05"),
ESC_DIGIT('6', "\\6", VM_ONLY, "backreference to capture group 6 (PCRE2 error 115 if no such group)", QF_NO, "char 0x06"),
ESC_DIGIT('7', "\\7", VM_ONLY, "backreference to capture group 7 (PCRE2 error 115 if no such group)", QF_NO, "char 0x07"),
ESC_DIGIT_LIT('8', "\\8", VM_ONLY, "backreference to capture group 8 (PCRE2 error 115 if no such group)", QF_NO, "char 0x38", '8'),
ESC_DIGIT_LIT('9', "\\9", VM_ONLY, "backreference to capture group 9 (PCRE2 error 115 if no such group)", QF_NO, "char 0x39", '9'),

/* [DD-11.4b] the 9 base-tier literal escapes' first 6 — the FIXED ones
 * (definitions_table.md's architectural note: "e.g. \a≡\x07, \e≡\x1b",
 * both verified against libpcre2 10.46, 3/3 subjects). The remaining 3
 * (bare \x, octal, \0) are PARAMETERIZED BY TEXT AT THE OCCURRENCE — the
 * hex/octal digits read from the pattern, not a fixed substitution — which
 * neither DEFK_STR (a fixed string) nor DEFK_BUILDER (an AST-operand
 * function) expresses; open question sent to main, held pending a ruling. */
ESC_BASE_D('a', "\\a", "alarm, hex 07", "char 0x07", a_def),
ESC_BASE_D('e', "\\e", "escape, hex 1B (not backslash-escape, the ASCII ESC character)", "char 0x1b", e_def),
ESC_BASE_D('f', "\\f", "form feed, hex 0C", "char 0x0c", f_def),
ESC_BASE_D('n', "\\n", "linefeed, hex 0A", "char 0x0a", n_def),
ESC_BASE_D('r', "\\r", "carriage return, hex 0D", "char 0x0d", r_def),
ESC_BASE_D('t', "\\t", "tab, hex 09", "char 0x09", t_def),

/* [DD-11.1] the 7th base-tier literal escape: `\x`, ONE CONSTRUCT WITH TWO
 * SPELLINGS (manager ruling, 2026-08-29, correcting the first pass's
 * split): bare `\xHH` (exactly 2 hex digits, base tier, esc_char_value's
 * own live rule) and braced `\x{HHHH}` (arbitrary-width hex, module
 * unicode-props, UNBUILT — esc_char_value's own case for it stays exactly
 * where it is, a parse.c special case naming the module by hand,
 * src/parse/CLAUDE.md's registry section). The ruling: giving `\x{...}`
 * its OWN row would be a lookup the base path never pays (the thing
 * src/parse/CLAUDE.md's rule actually protects); a `definitions` row
 * dispatch never consults costs no lookup, so the two spellings SHARE
 * this one row and one `DEFK_TEXTFN` — `pcrec_def_text_hex` already
 * decodes an ARBITRARY-length hex run (it loops until it runs out of
 * digits or the value exceeds a byte), so no code change was needed
 * there, only the row's own template/note naming both forms. `syntax`
 * stays the bare-form illustrative example (`\N{U+0041}`'s own
 * convention), and `class_expect` is measured against THAT example's
 * literal text, same as `\cX`'s "char 0x18" is measured against the
 * literal `X`. */
ESC_BASE_D('x', "\\x41", "hex: bare \\xHH (exactly 2 digits) or braced \\x{HHHH} (\\x{...} requires module 'unicode-props')", "char 0x41", bare_x_def),
};

/* ---- doorway 2: after '(?' ---------------------------------------------- */
static const RegRow group_rows[] = {
/* The one registry row the base tier reaches, and it must stay that way: SR-5's
 * fast-path guard concerns this row. NOTE (R6): a base pattern does not in fact
 * reach it — parse.c answers `(?:` first, so this row costs zero lookups and the
 * ones a base pattern DOES perform are all at the class-bracket doorway. Written longhand deliberately — the only supported construct in the
 * file should not be able to hide inside a macro that means "rejected". */
{RK_GROUP, ':', NULL, "(?:...)",
 0, NULL,
 FLAV_PCRE2, ANY_ENGINE,
 RS_BASE, RD_NONE, NULL, NULL, 0,
 "non-capturing group", ROADMAP_NONE, QF_YES, NULL, 0, NULL, NO_PORT, NO_PORT, NULL, NULL},

GROUP_LA('=',  "(?=...)",       "positive lookahead"),
GROUP_LA('!',  "(?!...)",       "negative lookahead"),

/* `<` IS THREE CONSTRUCTS AND A NAME, split by tail at SR-9 (Q2). It used to
 * carry the compound module "lookaround/named-groups", which is a true sentence
 * and an inexact answer — D26 makes module attribution tier 2, i.e. EXACT.
 *
 * Swept over all 256 tail bytes against libpcre2 10.46, which is the only way
 * this was ever going to be right: exactly THREE tails are lookaround (`=`, `!`
 * and `*`), and every other byte is the named-group path — either a valid name,
 * error 162 "subpattern name expected", or error 144 for a leading digit. So
 * the bare row below is `named-groups` and cannot be anything else.
 *
 * `(?<*` is the non-atomic positive LOOKBEHIND, the mirror of `(?*` above and
 * the `(?` spelling of `(*naplb:...)`. It had no row at all before this sweep;
 * the old comment claimed it "enters through the `<` selector, which already
 * names lookaround", which was true only because that selector named lookaround
 * for everything, including named groups. Splitting the row is what turned that
 * into a fact needing its own line. */
GROUP_LA_T('<', "=", "(?<=...)", "positive lookbehind"),
GROUP_LA_T('<', "!", "(?<!...)", "negative lookbehind"),
GROUP_LA_T('<', "*", "(?<*a)",
      "non-atomic positive lookbehind — the (? spelling of (*naplb:...)"),
/* [M6.3] Longhand rather than the GROUP macro, for the one field the macro
 * cannot express: a wired PORT_FN. `engines` is ANY_ENGINE, not VM_ONLY —
 * a deliberate RECLASSIFICATION (docs/dev/decisions.md's [M6.3] entry, and
 * see internal.h's comment on pcrec_ngport_declare): a named group's AST
 * is an ordinary A_CAP node, and the pre-existing generic capture-forcing
 * rule (src/opt/select_engine.c) already sends it to the VM whenever it
 * delivers a real capture slot, exactly as a plain numbered group would.
 * The three rows below are the ONLY named-groups rows this applies to —
 * the boundary constructs (\k \g (?P= backref-by-name; (?J)/DUPNAMES)
 * stay in their own modules ('backrefs', and mod_modifiers.c's
 * unconditional 'J' refusal), untouched. */
{RK_GROUP, '<', NULL, "(?<name>a)", M_named_groups, FLAV_PCRE2, ANY_ENGINE,
 RS_MODULE, RD_MODULE, NULL, NULL, 0,
 "named capture group (?<name>...) — the lookbehinds take = ! * and have their own rows",
 ROADMAP_PLANNED, QF_YES, NULL, 0, NULL,
 {PORT_FN, false, 0, NULL, pcrec_ngport_declare}, NO_PORT, NULL, NULL},

{RK_GROUP, '\'', NULL, "(?'name'...)", M_named_groups, FLAV_PCRE2, ANY_ENGINE,
 RS_MODULE, RD_MODULE, NULL, NULL, 0,
 "named capture group, Perl-style quoting",
 ROADMAP_PLANNED, QF_YES, NULL, 0, NULL,
 {PORT_FN, false, 0, NULL, pcrec_ngport_declare}, NO_PORT, NULL, NULL},

/* `(?P` IS THE OTHER THREE-WAY BYTE, and the three are three DIFFERENT MODULES:
 * a named group, a backreference and a subroutine call. One row answering
 * "named-groups" for all three is R8/C4-7's misattribution, re-derived
 * independently from the documents by a spec-first writer (D27) and confirmed
 * here by measurement:
 *
 *     (?<n>a)(?P=n)   compiles     a BACKREFERENCE to group n
 *     (?<n>a)(?P>n)   compiles     a SUBROUTINE CALL into group n
 *     (?P<n>a)        compiles     a named group
 *     (?PX)  (?P)     error 141    "unrecognized character after (?P"
 *
 * That last line is a FIFTH over-promise this sweep found and the plan did not
 * list: 252 of the 255 probeable tails after `(?P` are error 141, and pcrec
 * promised module 'named-groups' for every one of them. It is Q2's own defect
 * one level down — the same catch-all shape, at a sub-doorway. */
/* `syntax` must be a probe in which THIS row's construct is the LEFTMOST thing
 * pcrec cannot handle, because that is the one pcrec reports. `(?<n>a)(?P=n)`
 * looks like the better example and is the wrong field value: pcrec stops at
 * the `(?<` and the row's own diagnostic never appears. The group declaration
 * these two need to satisfy LIBPCRE2 goes in PC-3's WRAPPERS instead, which is
 * exactly what that mechanism is for. */
/* [M6.3] longhand for the same reason as the two rows above: a wired
 * PORT_FN and ANY_ENGINE, not GROUP_T's VM_ONLY default. */
{RK_GROUP, 'P', "<", "(?P<name>a)", M_named_groups, FLAV_PCRE2, ANY_ENGINE,
 RS_MODULE, RD_MODULE, NULL, NULL, 0,
 "python-style named capture group",
 ROADMAP_PLANNED, QF_YES, NULL, 25, NULL,
 {PORT_FN, false, 0, NULL, pcrec_ngport_declare}, NO_PORT, NULL, NULL},
/* [M6.5.2] longhand, for mod_named_groups.c's row's reason: a wired PORT_FN,
 * which `GROUP_T` has no parameter for. Everything else is what GROUP_T would
 * have built, rank 25 included. */
{RK_GROUP, 'P', "=", "(?P=n)", M_backrefs, FLAV_PCRE2, VM_ONLY, RS_MODULE,
 RD_MODULE, NULL, NULL, 0,
 "python-style backreference to a named group",
 ROADMAP_PLANNED, QF_NO, NULL, 25, NULL,
 {PORT_FN, false, 0, NULL, pcrec_brport_pname}, NO_PORT, NULL, NULL},
GROUP_RC_T('P', ">", "(?P>n)", "python-style subroutine call into a named group", QF_YES, pcrec_rcport_name, NULL),
REJECTED(RK_GROUP, 'P', "(?PX)", "unrecognized character after (?P",
         "only (?P< (?P= and (?P> exist — every other byte after (?P is PCRE2 error 141", QF_NO),
/* VM_ONLY is design intent with a recorded split (docs/dev/plan.md, backrefs/
 * atomic note, 2026-08-12): atomic groups are CUT operators — regular, so
 * DFA-compilable via the cut construction, whose one primitive is the
 * priority-first-accept function our subset construction already computes.
 * NOTE the trap the same entry records: naive determinization implements
 * the NON-atomic semantics (a DFA never backtracks to begin with) — the
 * cut changes the LANGUAGE, so this row must never be lowered by simply
 * ignoring the atomicity. Per-pattern engine decision, module's call. */
/* [M6.4.2] longhand, for the reason the two rows above are: a WIRED PORT.
 * VM_ONLY stays — unlike [M6.3]'s named-groups reclassification, this row does
 * NOT lower to both engines. D67 records why that difference matters: a named
 * group's AST is an ordinary A_CAP and the pre-existing capture rule already
 * routed it, so moving its mask to ANY_ENGINE was true; an atomic group
 * genuinely cannot be represented in pcrec's Dfa, so the column cannot be made
 * true by editing it. That is the first evidence this column has had in BOTH
 * directions — VM_ONLY is too strong for `(?>a*)b`, which the free discharge
 * rescues, and ANY_ENGINE would be too weak for `(?>a|ab)c`, which nothing but
 * the VM can compile — and it is exactly why SR-8's consultation is a PASS
 * over the post-discharge tree rather than a per-row verdict. */
{RK_GROUP, '>', NULL, "(?>...)", M_atomic_groups, FLAV_PCRE2, VM_ONLY,
 RS_MODULE, RD_MODULE, NULL, NULL, 0,
 "atomic (non-backtracking) group",
 ROADMAP_PLANNED, QF_YES, NULL, 0, NULL,
 {PORT_FN, false, 0, NULL, pcrec_agport_atomic}, NO_PORT, NULL, NULL},
/* THE SECOND ROW THIS FILE'S PURPOSE IS MADE OF, and it arrived the same way
 * the first did — three homes disagreeing, found by an outside reading rather
 * than by any test. `(?*...)` is PCRE2's NON-ATOMIC POSITIVE LOOKAHEAD, the
 * `(?` spelling of `(*napla:...)`. Q1's verb table already knew `napla`, and
 * docs/pcre2_compliance.md has named `(?*...)` as non-atomic lookaround since
 * the 2026-08-09 survey; only this table did not, so the `(?` catch-all
 * answered "requires module 'modifiers'" for it — the wrong module, which is
 * the one fact the diagnostic exists to carry.
 *
 * Proven BEHAVIOURALLY rather than by reading a name (R8/C4-8), because a
 * construct that merely compiles proves nothing about what it is. On "abab":
 *
 *     (?*(a|ab))\1$    matches [2,4)      <- non-atomic: retries the alternation
 *     (?=(a|ab))\1$    NO MATCH           <- atomic lookahead: keeps its first
 *     (*napla:(a|ab))\1$ matches [2,4)    <- the same construct, verb spelling
 *
 * `(?<*...)` is the lookbehind of the same family and needs no row: it enters
 * through the `<` selector, which already names lookaround. */
GROUP_LA('*',  "(?*a)",
      "non-atomic positive lookahead — the (? spelling of (*napla:...)"),
GROUP_LEXICAL('#',  "(?#...)",       comments,     ANY_ENGINE, "comment, discarded up to the next ')'"),
/* [M4-CALLOUTS] step 1 (D36, 2026-08-12; flipped 2026-08-14): was
 * GROUP_NEVER — K14's OUT-OF-SCOPE ruling on 2026-08-11. Frank re-scoped it
 * to a PLANNED module the same session that discussion started, LOW
 * priority, parked behind the M4 VM engine that hosts the behavior (step 2,
 * separately scoped). This row only changes disposition; the syntax and
 * PCRE2 semantics it describes are unchanged. */
GROUP('C',  "(?C1)",   callouts,         VM_ONLY, "callout to user code: (?C) (?C1) (?C{text}) -- PLANNED (D36): M4-hosted, VM-only; the compiled DFA erases the pattern positions a callout fires at", QF_NO),
GROUP('|',  "(?|...)",       branch_reset,     VM_ONLY,
      "branch reset group: alternatives reuse the same capture numbers", QF_YES),
GROUP('(',  "(?(1)a|b)",     conditionals,     VM_ONLY, "conditional group (?(condition)yes|no)", QF_NO),
/* [DD-14 wave F] `(?(DEFINE)...)` IS MODULE `recursion`'s, TAILED OFF THE
 * `(?(` DOORWAY (D71 item 4, Frank 2026-08-23, overruling design §2.5's "no
 * DEFINE"). The rest of `(?(` stays `conditionals`': one byte, two
 * constructs, told apart by a literal tail, which is the `(?P<`/`(?P=`/`(?P>`
 * shape this table already ships three times.
 *
 * THE TAIL IS `DEFINE)` AND INCLUDES THE PARENTHESIS, MEASURED: on 10.46
 * `(?(define)(?<w>a))` and `(?(DEF)(?<w>a))` are both "reference to
 * non-existent subpattern" — lowercase and prefixes are read as NAME
 * conditions — so a tail of `DEFINE` alone would claim `(?(DEFINED)` for this
 * module, which is a name condition and `conditionals`'.
 *
 * LONGHAND RATHER THAN `GROUP_RC_T`, FOR ONE FIELD: `ANY_ENGINE`. Every other
 * row in this module is VM_ONLY and structurally so — a subroutine call
 * generates a non-regular language. A DEFINE generates NOTHING at its lexical
 * position: it is `(?:BODY){0}`, which MEASURABLY compiles to a pure DFA
 * (`--engine=dfa --no-captures '(?:(?<g>a)){0}b'` on the shipped binary), so
 * VM_ONLY here would refuse what the DFA engine handles and would refuse it
 * asymmetrically against the `{0}` spelling of the same construct. What
 * forces the VM in any real use is the CALL that reads the definition, and
 * that carries its own row and its own stamp. The macro is not extended for
 * this: a macro exists to make the FIXED fields unmissable, and a variant
 * differing in an engine mask is exactly the row that must be read in full.
 *
 * `QF_YES`, MEASURED: `(?(DEFINE)(?<w>a))*` compiles on 10.46 (a zero-width
 * construct is still a quantifier target). */
{RK_GROUP, '(', "DEFINE)", "(?(DEFINE)(?<w>a))", M_recursion, FLAV_PCRE2,
 ANY_ENGINE, RS_MODULE, RD_MODULE, NULL, NULL, 0,
 "define-only group: the body never runs where it is written and exists to be "
 "called -- the same thing (?:BODY){0} means",
 ROADMAP_PLANNED, QF_YES, NULL, 25, NULL,
 {PORT_FN, false, 0, NULL, pcrec_rcport_define}, NO_PORT, NULL, NULL},
GROUP_RC('&',  "(?&name)", "recurse into the named group", QF_YES, pcrec_rcport_name, NULL),
GROUP_RC('R',  "(?R)", "recurse the whole pattern", QF_YES, pcrec_rcport_num, NULL),
/* [DD-14] THE DESCRIPTION IS QUALIFIED, and §2.4a is why the unqualified
 * version is a trap rather than a wording preference: `(?0...)` is a
 * ONE-CHARACTER PREFIX OF TWO DIFFERENT TARGETS. `(?0)` and `(?00)` are the
 * root; `(?01)` is GROUP 1, MEASURED on the anchored discriminator
 * (`^(a(?01)?b)$` on "aabb" is (0,4) where `^(a(?0)?b)$` is nomatch). A port
 * written from "synonym for (?R)" compiles `(?01)` as the root and
 * MISCOMPILES it. `pcrec_rcport_num` re-reads the whole digit run for
 * exactly that reason, and this row says so where a reader of the table
 * will meet it. */
GROUP_RC('0',  "(?0)", "recurse the whole pattern -- the whole DIGIT RUN is read as decimal, so (?0) and (?00) are the root while (?01) is group 1", QF_YES, pcrec_rcport_num, NULL),
INDEX_RC(RK_GROUP, '0', "(?00)", "recurse the whole pattern, leading-zero spelling -- any all-zero digit run is the root", QF_YES, NULL, "(?0)"),
GROUP_RC('1',  "(?1)", "recurse into capture group 1", QF_YES, pcrec_rcport_num, NULL),
GROUP_RC('2',  "(?2)", "recurse into capture group 2", QF_YES, pcrec_rcport_num, "(?1)"),
GROUP_RC('3',  "(?3)", "recurse into capture group 3", QF_YES, pcrec_rcport_num, "(?1)"),
GROUP_RC('4',  "(?4)", "recurse into capture group 4", QF_YES, pcrec_rcport_num, "(?1)"),
GROUP_RC('5',  "(?5)", "recurse into capture group 5", QF_YES, pcrec_rcport_num, "(?1)"),
GROUP_RC('6',  "(?6)", "recurse into capture group 6", QF_YES, pcrec_rcport_num, "(?1)"),
GROUP_RC('7',  "(?7)", "recurse into capture group 7", QF_YES, pcrec_rcport_num, "(?1)"),
GROUP_RC('8',  "(?8)", "recurse into capture group 8", QF_YES, pcrec_rcport_num, "(?1)"),
GROUP_RC('9',  "(?9)", "recurse into capture group 9", QF_YES, pcrec_rcport_num, "(?1)"),
INDEX_RC(RK_GROUP, '1', "(?10)", "recurse into capture group 10 -- a MULTI-DIGIT absolute call; the whole digit run after (? is read as decimal, so nine byte-keyed rows serve every group number", QF_YES, NULL, "(?1)"),
INDEX_RC(RK_GROUP, '0', "(?01)", "recurse into capture group 1, LEADING-ZERO spelling -- (?01) is group 1 and NOT the root, which (?0)'s own note is qualified for", QF_YES, NULL, "(?1)"),
/* THE RELATIVE SUBROUTINE CALLS. `(?+N)` calls the Nth group to the RIGHT and
 * `(?-N)` the Nth to the LEFT — the relative spellings of `(?1)`..`(?9)` above,
 * which this table has always called `recursion`. Both used to fall to the
 * catch-all and be called `modifiers`, which is R8/C4-7's first two
 * misattributions and is measurably wrong:
 *
 *     (?+1)(a)        compiles     a forward subroutine call
 *     (a)(?-1)        compiles     a backward subroutine call
 *     (?+x)           error 129    "digit expected after (?+ or (?-"
 *
 * `+` NEEDS NO TAIL: swept over all 256 tails, every non-digit is error 129, so
 * the byte alone settles the construct. `-` is the one byte at this doorway
 * that genuinely is two constructs — `(?-i)` unsets an option — so it takes the
 * ten digit rows below and its bare row stays `modifiers`. Ten rows rather than
 * one "digit" tail is the deliberate choice recorded on RegRow.tail: this table
 * already spells that family out twice, and a literal tail cannot be
 * misinterpreted by a future reader. */
GROUP_RC('+',  "(?+1)(a)",
      "relative subroutine call to the Nth group to the RIGHT", QF_YES, pcrec_rcport_rel, NULL),
INDEX_RC(RK_GROUP, '+', "(?+2)(a)(b)", "relative forward subroutine call, 2 to the right -- (?+1) has a byte-keyed row and its eight siblings ride it, the whole digit run being read as decimal", QF_YES, NULL, "(?+1)(a)"),
GROUP_RC_T('-', "0", "(a)(?-01)", "relative subroutine call, leading zero", QF_YES, pcrec_rcport_rel, "(a)(?-1)"),
GROUP_RC_T('-', "1", "(a)(?-1)", "relative subroutine call to the group 1 to the LEFT", QF_YES, pcrec_rcport_rel, NULL),
GROUP_RC_T('-', "2", "(a)(a)(?-2)", "relative subroutine call, 2 to the left", QF_YES, pcrec_rcport_rel, "(a)(?-1)"),
GROUP_RC_T('-', "3", "(a)(a)(a)(?-3)", "relative subroutine call, 3 to the left", QF_YES, pcrec_rcport_rel, "(a)(?-1)"),
GROUP_RC_T('-', "4", "(a)(a)(a)(a)(?-4)", "relative subroutine call, 4 to the left", QF_YES, pcrec_rcport_rel, "(a)(?-1)"),
GROUP_RC_T('-', "5", "(a)(a)(a)(a)(a)(?-5)", "relative subroutine call, 5 to the left", QF_YES, pcrec_rcport_rel, "(a)(?-1)"),
GROUP_RC_T('-', "6", "(a)(a)(a)(a)(a)(a)(?-6)", "relative subroutine call, 6 to the left", QF_YES, pcrec_rcport_rel, "(a)(?-1)"),
GROUP_RC_T('-', "7", "(a)(a)(a)(a)(a)(a)(a)(?-7)", "relative subroutine call, 7 to the left", QF_YES, pcrec_rcport_rel, "(a)(?-1)"),
GROUP_RC_T('-', "8", "(a)(a)(a)(a)(a)(a)(a)(a)(?-8)", "relative subroutine call, 8 to the left", QF_YES, pcrec_rcport_rel, "(a)(?-1)"),
GROUP_RC_T('-', "9", "(a)(a)(a)(a)(a)(a)(a)(a)(a)(?-9)", "relative subroutine call, 9 to the left", QF_YES, pcrec_rcport_rel, "(a)(?-1)"),
INDEX_RC(RK_GROUP, '-', "(a)(a)(a)(a)(a)(a)(a)(a)(a)(a)(?-10)", "relative backward subroutine call, 10 to the left -- a MULTI-DIGIT relative call; the ten byte-keyed digit rows serve every distance", QF_YES, NULL, "(a)(?-1)"),

/* THE EXTENDED CHARACTER CLASS, R8/C4-7's third misattribution. `(?[...])` is a
 * character class with set operations (`[a]&&[b]`, `[a]-[b]`), not an option
 * setting — it compiles under libpcre2 10.46 and has its own error family (209
 * "unexpected operator in extended character class", 214 "empty expression in
 * extended character class"), which is PCRE2 parsing a class body rather than
 * option letters.
 *
 * `classes` WAS A JUDGEMENT, stated rather than buried, and MOD-0.3a
 * (2026-08-12) exercised the exit the original comment reserved: the moment
 * module `classes` gained producers, "requires module 'classes'" for a
 * construct classes will not produce became a live lie — an ENABLED module
 * still refusing in its own name. Set-operation classes earn the module of
 * their own the comment predicted. PC-3 keeps checking the construct is REAL
 * (measured: `(?[[a]])` COMPILES under 10.46, `(?[a])` is its own err 216);
 * the NAME stays ours to pick, and is pinned in tests/reject/. */
GROUP('[',  "(?[[a]])",      extended_classes, ANY_ENGINE,
      "extended character class with set operations: (?[[a]&&[b]]) (?[[a]-[b]])", QF_YES),

/* THE OPTION SETTINGS, WRITTEN OUT. These eleven bytes used to be a catch-all
 * row with REG_SEL_ANY, and that row is what Q2 is about: it answered "requires
 * module 'modifiers'" for EVERY byte, so 217 of the 255 probeable bytes after
 * `(?` were promised a module for syntax libpcre2 rejects outright (error 111).
 * Same defect as Q1's at the `(*` doorway and FIX-2's at the class bracket, at
 * the one that is 217x wider.
 *
 * The eleven are MEASURED, not transcribed from pcre2syntax: a generated sweep
 * of all 256 bytes with 45 completions each said 38 bytes are recognised, and
 * these are the ones left after every other row here claims its own. A PCRE2
 * upgrade that adds an option letter makes this list wrong, which is exactly
 * what PC-3's byte differential now reports — a tier-2 finding under D26, not
 * drift to be waved through. */
GROUP_OPT(')',  "(?)", "empty option setting", QF_FORM),
/* The bare `-` row, and it must sit under the ten `-<digit>` rows above rather
 * than replace them: `(?-i)` unsets an option, `(?-1)` calls a subpattern. This
 * is the only selector byte at this doorway carrying two different modules, and
 * the tail is what keeps the answer exact instead of compound. */
GROUP_OPT('-',  "(?-i)", "unset options: (?-i) (?-im:...)", QF_FORM),
GROUP_OPT('^',  "(?^)", "reset all options to their default", QF_FORM),
GROUP_OPT('J',  "(?J)", "allow duplicate names (PCRE2_DUPNAMES)", QF_FORM),
GROUP_OPT('U',  "(?U)", "ungreedy: invert the greediness of quantifiers", QF_FORM),
GROUP_OPT('a',  "(?a)", "ASCII-restrict class escapes (PCRE2_EXTRA_ASCII_*)", QF_FORM),
GROUP_OPT('i',  "(?i)", "caseless", QF_FORM),
GROUP_OPT('m',  "(?m)", "multiline: ^ and $ match at internal newlines", QF_FORM),
GROUP_OPT('n',  "(?n)", "no auto-capture: plain (...) stops capturing", QF_FORM),
GROUP_OPT('r',  "(?r)", "restrict caseless matching to within ASCII or non-ASCII", QF_FORM),
GROUP_OPT('s',  "(?s)", "dotall: . matches newline", QF_FORM),
GROUP_OPT('x',  "(?x)", "extended: ignore unescaped whitespace and # comments", QF_FORM),
/* Catch-all, and it must stay last. Q2 INVERTS WHAT IT MEANS: it used to promise
 * a module, and now it agrees with PCRE2 that there is no construct here at all.
 * PCRE2's own wording, byte for byte, for the reason the collating and verb rows
 * give — where AGREEMENT is the whole claim, saying it in different words makes
 * the claim harder to check and no clearer to a reader. Error 111. */
REJECTED(RK_GROUP, REG_SEL_ANY, "(?q)", "unrecognized character after (? or (?-",
         "no construct begins with this byte — PCRE2 error 111", QF_NO),
};

/* ---- doorway 3: after '(*' ----------------------------------------------
 * A NAME decides here. The ROW below still carries the doorway's module and
 * its one diagnostic; the NAMES are in the two VerbName tables further down
 * (Q1). Splitting them is deliberate — see the VerbName comment in internal.h
 * and D25.
 *
 * `syntax` was `"(*...)"` until PC-3, and PC-3 is exactly what caught it: an
 * RS_MODULE row claims PCRE2 HAS the construct, so the row's probe must COMPILE
 * under libpcre2 — and `(*...)` does not (error 160, "(*VERB) not recognized or
 * malformed"). The probe was a fabrication in PCRE2's eyes, one that no check
 * reading only pcrec's own files could see. `(*ACCEPT)` is a real verb,
 * compiles there, and reaches this doorway here. */
/* [M6.6.2 wave F] THE TWELVE ALPHA LOOKAROUND SPELLINGS, and they are the
 * FIRST ROWS IN THIS TABLE THAT NEVER DISPATCH (RF_INDEX, internal.h; D71
 * item 3, Frank 2026-08-23).
 *
 * WHY THEY EXIST AT ALL. Before this wave `--list-syntax` and the compliance
 * index said module `lookaround` ships SIX constructs, while TWELVE more
 * spellings of those same six existed in PCRE2, were written by users, and
 * were invisible to every surface pcrec publishes — the inventory question
 * design §8.2 raised and §14 ASK 3 put to Frank, who ruled YES for all twelve
 * (not the six short names alone): a spelling a caller can write is a
 * spelling the index owes a line for, and the six LONG forms are exactly as
 * writable as the six short ones.
 *
 * WHY THEY DO NOT DISPATCH. The `(*` doorway decides by NAME, through
 * mod_verbs.c's two VerbName tables (D25/Q1) — not by a selector byte — so
 * these rows have no byte-keyed dispatch identity to keep, which is precisely
 * the split D71 item 3 names ("which row fires" vs "what does PCRE2's surface
 * look like"). `pcrec_registry_arbitrate` skips them; `tail` is the NAME, and
 * mod_verbs.c's `pcrec_registry_verb_name_row` is what reads it.
 *
 * THE `family` COLUMN IS THE PRIMARY'S OWN `syntax`, and it is load-bearing
 * rather than documentation: src/parse/mod_lookaround.c's `la_kind` resolves
 * it to the primary ROW and reads that row's three `u.look` flags, so an
 * alias cannot disagree with its primary about which construct it is. The
 * ALIAS→PRIMARY assignment below is MEASURED against libpcre2 10.46 rather
 * than transcribed from the design's table: 84 templates x 19 subjects, every
 * startpos, match span and every group span, 0 divergences — and the two
 * shapes PCRE2 does NOT have (`(*nanla:` / `(*nanlb:`, err 195) are asserted
 * absent by the same run and have no rows here, which is the control that
 * makes the twelve a list rather than a guess.
 *
 * `QF_YES` on all twelve, MEASURED the way the column requires (libpcre2's
 * own verdict on `a<syntax>*`): all twelve quantify.
 *
 * BORN `built`, and derived rather than declared: D65 drives each row's own
 * `syntax` through the `(*` doorway at a forced-open gate
 * (src/parse/syntax_dump.c), so these rows read `built` because the doorway
 * really does produce for them — the wiring below is the `aport`, and the
 * column follows it exactly as it follows every other row's. */
#define VERB_LA(name, syn, prim, note) \
    {RK_VERB, REG_SEL_ANY, (name), (syn), M_lookaround, FLAV_PCRE2, VM_ONLY, \
     RS_MODULE, RD_MODULE, NULL, NULL, RF_INDEX, (note), ROADMAP_PLANNED, \
     QF_YES, NULL, 0, NULL, {PORT_FN, false, 0, NULL, pcrec_laport_group}, \
     NO_PORT, (prim), NULL}

static const RegRow verb_rows[] = {
VERB_LA("pla", "(*pla:a)", "(?=...)",
        "positive lookahead, alpha spelling of (?=...)"),
VERB_LA("positive_lookahead", "(*positive_lookahead:a)", "(?=...)",
        "positive lookahead, long alpha spelling of (?=...)"),
VERB_LA("nla", "(*nla:a)", "(?!...)",
        "negative lookahead, alpha spelling of (?!...)"),
VERB_LA("negative_lookahead", "(*negative_lookahead:a)", "(?!...)",
        "negative lookahead, long alpha spelling of (?!...)"),
VERB_LA("plb", "(*plb:a)", "(?<=...)",
        "positive lookbehind, alpha spelling of (?<=...)"),
VERB_LA("positive_lookbehind", "(*positive_lookbehind:a)", "(?<=...)",
        "positive lookbehind, long alpha spelling of (?<=...)"),
VERB_LA("nlb", "(*nlb:a)", "(?<!...)",
        "negative lookbehind, alpha spelling of (?<!...)"),
VERB_LA("negative_lookbehind", "(*negative_lookbehind:a)", "(?<!...)",
        "negative lookbehind, long alpha spelling of (?<!...)"),
VERB_LA("napla", "(*napla:a)", "(?*a)",
        "non-atomic positive lookahead, alpha spelling of (?*...)"),
VERB_LA("non_atomic_positive_lookahead", "(*non_atomic_positive_lookahead:a)",
        "(?*a)",
        "non-atomic positive lookahead, long alpha spelling of (?*...)"),
VERB_LA("naplb", "(*naplb:a)", "(?<*a)",
        "non-atomic positive lookbehind, alpha spelling of (?<*...)"),
VERB_LA("non_atomic_positive_lookbehind",
        "(*non_atomic_positive_lookbehind:a)", "(?<*a)",
        "non-atomic positive lookbehind, long alpha spelling of (?<*...)"),
/* THE DOORWAY ROW STAYS LAST, and that is a requirement rather than a
 * convention now: `pcrec_registry_arbitrate` elects the LAST REG_SEL_ANY row
 * it walks as the kind's catch-all. The twelve above carry RF_INDEX and are
 * skipped before that arm is reached (registry.c's arbitration comment), so
 * this row is still the only candidate — but a thirteenth alpha row written
 * WITHOUT the flag would silently steal the doorway, which is why
 * registry_check asserts the catch-all this doorway resolves to by name. */
FIXED(RK_VERB, REG_SEL_ANY, "(*ACCEPT)", verbs, VM_ONLY,
      "(*...) requires module 'verbs'",
      "backtracking verb ((*SKIP), (*ACCEPT)), start-of-pattern option ((*CR), (*UTF)) "
      "or script run ((*script_run:...))", QF_FORM),
};

/* mod_verbs.c's name→row link. Kept HERE, beside the rows, because it reads
 * `tail` as a NAME — a reading only these rows license — and a copy of that
 * loop in the doorway would be a second place the convention is spelled out.
 * Returns NULL for every name with no row of its own, which is every verb but
 * these twelve, and NULL is what makes the doorway's own row the default
 * (design §8.2's "everything else inherits"). */
const RegRow *pcrec_registry_verb_name_row(const char *name, size_t len)
{
    size_t n;
    const RegRow *rows = pcrec_registry(RK_VERB, &n);
    for (size_t i = 0; i < n; i++) {
        if (!(rows[i].flags & RF_INDEX) || !rows[i].tail) continue;
        if (strlen(rows[i].tail) == len && memcmp(rows[i].tail, name, len) == 0)
            return &rows[i];
    }
    return NULL;
}

/* ---- doorway 3's NAME tables (Q1) ---------------------------------------
 * Moved to src/parse/mod_verbs.c at MOD-0.4 (the migration test), WITH their
 * measurement-provenance comments and the four accessor functions
 * (pcrec_registry_verb_table/find/tables/name_limit) that read them — see
 * mod_verbs.c's header. The VerbName/VerbTable TYPES and the accessor
 * PROTOTYPES stay in internal.h, unchanged. */

/* ---- doorway 4: after '[' inside a class -------------------------------- */
/* [DD-11.1] the POSIX named-class row's 14 definitions (manager ruling,
 * 2026-08-29): a FINITE enumerable name set, unlike `\c`/`\o`/`\N{U+`'s
 * unbounded operand space — DEFK_STR, not DEFK_TEXTFN. Every byte range
 * below was READ DIRECTLY off pcrec's own generated bitmaps
 * (`pcrec_cls_px_*`, cls_bits.inc, via a throwaway scratch dump linked
 * against build/libpcrec.a — never guessed from POSIX folklore) and
 * cross-checked against python3 `re` over all 256 bytes, 0 disagreements
 * for all 14 names. All 14 entries carry `DEF_ALWAYS`: this row's
 * predicate axis is the NAME at the occurrence (parameterized-by-text,
 * same family as `DEFK_TEXTFN`'s rows), not an option-scope tag, so
 * there is no DefTag that could distinguish "alpha" from "digit" — every
 * entry answering DEF_ALWAYS is honest about that (`pcrec_def_resolve`
 * on this row is not meaningful for real resolution today, same as
 * every other row before [DD-11.5] wires anything up; `--list-
 * definitions` walks the array as DATA, one line per name, exactly as
 * intended). Two real PCRE2 constructs sharing this doorway are
 * deliberately ABSENT: `[[:<:]]`/`[[:>:]]` are word-boundary assertions,
 * not character classes (registry.c's own `posix_names[]` comment), so
 * neither is a "construct standing for another construct expressible in
 * core syntax" — there is no substitution to write. */
static const RegDef posix_def[] = {
    {DEFK_STR, DEF_ALWAYS, "[0-9A-Za-z]",       NULL, NULL},  /* alnum */
    {DEFK_STR, DEF_ALWAYS, "[A-Za-z]",          NULL, NULL},  /* alpha */
    {DEFK_STR, DEF_ALWAYS, "[\\x00-\\x7f]",     NULL, NULL},  /* ascii */
    {DEFK_STR, DEF_ALWAYS, "[\\t ]",            NULL, NULL},  /* blank */
    {DEFK_STR, DEF_ALWAYS, "[\\x00-\\x1f\\x7f]",NULL, NULL},  /* cntrl */
    {DEFK_STR, DEF_ALWAYS, "[0-9]",             NULL, NULL},  /* digit */
    {DEFK_STR, DEF_ALWAYS, "[!-~]",             NULL, NULL},  /* graph */
    {DEFK_STR, DEF_ALWAYS, "[a-z]",             NULL, NULL},  /* lower */
    {DEFK_STR, DEF_ALWAYS, "[ -~]",             NULL, NULL},  /* print */
    {DEFK_STR, DEF_ALWAYS, "[!-/:-@[-`{-~]",    NULL, NULL},  /* punct */
    {DEFK_STR, DEF_ALWAYS, "[\\t\\n\\x0b\\f\\r ]", NULL, NULL}, /* space */
    {DEFK_STR, DEF_ALWAYS, "[A-Z]",             NULL, NULL},  /* upper */
    {DEFK_STR, DEF_ALWAYS, "[A-Za-z0-9_]",      NULL, NULL},  /* word */
    {DEFK_STR, DEF_ALWAYS, "[0-9A-Fa-f]",       NULL, NULL},  /* xdigit */
    {DEFK_END, DEF_ALWAYS, NULL,                NULL, NULL},
};

static const RegRow classbracket_rows[] = {
/* LONGHAND because its shape is its own, which is this file's rule for a row no
 * macro should be able to hide. It is the only row in the table whose OUTCOME
 * KIND depends on WHERE it was found — K3, fixed 2026-08-10 (FIX-2):
 *
 *   [[:alpha:]]   a POSIX class PCRE2 SUPPORTS -> name the module (RS_MODULE)
 *   [:alpha:]     an error PCRE2 will never accept -> `open_msg`, and note it
 *                 names no module, because no module can make it legal
 *
 * pcrec ACCEPTED the second until now, compiling a matcher for the character
 * set {: a l p h} — measured, not inferred: the emitted binary matched ':' and
 * 'a' and rejected 'z'. A silent wrong matcher for a pattern PCRE2 refuses, and
 * python `re` accepts it too, so the corpus oracle was structurally blind.
 *
 * RF_CLASS_DELIM is what it was missing, and it carries both halves of the
 * recognition rule (see internal.h): the delimiter opens the construct only
 * when its matching `:]` appears later, and the class's own bracket can serve
 * as the `[`. That is why `[:]`, `[a[:b]` and `[[:alpha]` all still compile —
 * nothing closes the pair — which is K3's other half, an OVER-REJECTION that
 * cost users patterns PCRE2 accepts. */
{RK_CLASSBRACKET, ':', NULL, "[[:alpha:]]",
 M_classes,
 FLAV_PCRE2, ANY_ENGINE,
 RS_MODULE, RD_FIXED,
 "POSIX class [:...:] requires module 'classes'",
 "POSIX class [:...:] is only valid inside a character class",
 RF_CLASS_DELIM | RF_CLASS_NAMED,
 "POSIX character class", ROADMAP_PLANNED, QF_YES, "set 52", 0, NULL, NO_PORT,
 /* MOD-0.3c: one row, fourteen names, both polarities — a NAME is not a
  * fixed set per row, so the class port is the module's PORT_FN. */
 {PORT_FN, false, 0, NULL, pcrec_clsport_posix}, NULL, posix_def},
/* PCRE2 REJECTS these outright rather than treating them as literals, so
 * agreeing is compliance and there is no module to name — the reason RS_REJECTED
 * exists as a status distinct from RS_MODULE. pcrec accepted them silently until
 * 2026-08-09 (python `re` accepts them too, so the oracle was blind). The
 * trigger is narrower than it looks and was pinned against libpcre2 rather than
 * guessed: the delimiter opens a collating element ONLY when a matching `.]` /
 * `=]` appears later, and the class's own bracket can be the opener. Both rules
 * used to live in parse.c as reject_collating(); SR-2 moved them here as
 * RF_CLASS_DELIM, because they are the construct's own recognition rule and not
 * base grammar. Over-rejecting would break patterns PCRE2 accepts. */
REJECTED_DELIM(RK_CLASSBRACKET, '.', "[[.a.]]", "POSIX collating elements are not supported",
               "POSIX collating element — PCRE2 rejects it, and so must we", QF_NO, "err 113"),
REJECTED_DELIM(RK_CLASSBRACKET, '=', "[[=a=]]", "POSIX collating elements are not supported",
               "POSIX equivalence class — PCRE2 rejects it, and so must we", QF_NO, "err 113"),
};

/* ---- kind 5: the POSSESSIVE QUANTIFIER SUFFIXES -- NOT A DOORWAY --------
 * [M6.4.2], atomic_groups_design.md §7.4 RULE R1.
 *
 * This file's header lists the possessive `+` suffix as one of "the registry's
 * known outstanding second homes" — a construct whose "requires module"
 * diagnostic stays in parse.c because it is a sub-case of a BASE construct
 * rather than a doorway, and inventing a doorway for it would cost the base
 * tier a lookup on every quantifier. THAT REASON IS PRESERVED EXACTLY AND THE
 * SECOND HOME IS CLOSED: these rows are consulted by the DUMP and by
 * `src/parse/parse.c`'s desugaring (which reads the row it is already at, to
 * stamp `Ast.reg` from — not a lookup on the base path, since it runs only
 * after a `+` suffix has actually been seen). No doorway routes here;
 * `pcrec_registry_find` is never called with RK_QUANTSUFFIX.
 *
 * WHY THEY ARE WORTH FOUR ROWS AND A DERIVATION ARM. The day module
 * `atomic-groups` lands, `--list-syntax` and the generated index in
 * docs/pcre2_compliance.md say `(?>...)` is BUILT and say NOTHING AT ALL about
 * `*+ ++ ?+ {n,m}+`. A reader then cannot distinguish "not implemented" from
 * "not in the table", which is a D26 tier-2 RECOGNITION defect. The cheaper
 * alternative — leave the exemption and let the compliance page's hand-written
 * annotation layer carry the four spellings — loses because [DOC-DRV] just
 * spent a lane making that page's facts DERIVED rather than asserted, and a
 * construct whose built-status is only ever a hand annotation is exactly what
 * that document now exists to stop drifting.
 *
 * `syntax` IS EXECUTED, NOT DISPLAYED, which is why each one is a complete
 * probeable pattern (`a*+`) and not a bare suffix (`*+`):
 * tests/reject/run_reject_tests.sh iterates every non-base dump row and RUNS
 * the row's own `syntax`, requiring exit exactly 1, a diagnostic containing the
 * row's `expect` text, and no output file. Measured satisfiable on all four at
 * the closed gate (atomic_groups_measurements/out/registry_cost.txt §9).
 *
 * `quant` is QF_NO, and it is measured rather than assumed: `a*++` is an ERROR
 * in libpcre2 10.46 and in pcrec (design §6.3), so a possessive suffix is not
 * itself a quantifiable item.
 *
 * `engines` is VM_ONLY, matching the `(?>...)` row for the same reason: a
 * possessive whose §2.2 verdict is negative is not DFA-compilable by anything
 * this module ships. The free discharge (src/opt/atomic.c) is what makes the
 * PER-PATTERN answer better than the per-row mask — it DELETES the node before
 * SR-8's consultation runs, so `--engine=dfa '[^"]*+"'` succeeds and
 * `--engine=dfa '(?>a|ab)c'` refuses, which is the split Frank's 2026-08-12
 * companion note asks for and which no edit to this column could express. */
/* [DD-11.1] the possessive-suffix family's shared definition (definitions_
 * table.md §1/§3): unconditional (predicate DEF_ALWAYS), operand-taking
 * (the already-built A_REP node is the "body"), so a BUILDER rather than a
 * string — `pcrec_def_build_atomic` (src/parse/definitions.c). One array,
 * shared by all four rows below: the definition is identical for `*+ ++ ?+
 * {n,m}+`, only the quantifier producing the body differs. */
static const RegDef possessive_def[] = {
    {DEFK_BUILDER, DEF_ALWAYS, NULL, pcrec_def_build_atomic, NULL},
    {DEFK_END,     DEF_ALWAYS, NULL, NULL, NULL},
};

#define QUANTSUFFIX(sel, syn, note) \
    {RK_QUANTSUFFIX, (sel), NULL, (syn), M_atomic_groups, FLAV_PCRE2, VM_ONLY, \
     RS_MODULE, RD_MODULE, NULL, NULL, 0, (note), ROADMAP_PLANNED, QF_NO, NULL, \
     0, NULL, NO_PORT, NO_PORT, NULL, possessive_def}

static const RegRow quantsuffix_rows[] = {
QUANTSUFFIX('*', "a*+",     "possessive `*` — `X*+` is PCRE2's own spelling of `(?>X*)`"),
QUANTSUFFIX('+', "a++",     "possessive `+` — `X++` is PCRE2's own spelling of `(?>X+)`"),
QUANTSUFFIX('?', "a?+",     "possessive `?` — `X?+` is PCRE2's own spelling of `(?>X?)`"),
/* ONE row for the whole brace family (`{n}+` `{n,}+` `{n,m}+` `{,n}+`), on the
 * same "one row per RECOGNITION" rule the rest of the table follows: the `{`
 * is what decides, and try_quant has already resolved which brace form it was
 * before the `+` is ever looked at. The four forms are corpus cells
 * (tests/atomic_groups/possessive.rxt), not four rows.
 *
 * THE BRACE FORMS ARE ALSO WHERE python `re` DIVERGES FROM PCRE2 and `*+`/`++`
 * do not: over a body whose iteration can end in two places, python cuts PER
 * ITERATION and PCRE2 cuts at the GROUP EXIT — `(?:a|ab){2}+` on "aba" is (0,3)
 * in PCRE2 and NO MATCH in python, while `(?:a|ab)*+` on "aba" is (0,1) in
 * both. D26 makes PCRE2 the source of truth; the corpus cells are
 * `# pcre2-only` and say so. */
QUANTSUFFIX('{', "a{1,2}+", "possessive braces — `X{n,m}+` is `(?>X{n,m})`; also {n}+ {n,}+ {,n}+"),
};

/* ---- RK_BARE: base grammar with no doorway at all (manager ruling,
 * 2026-08-29) ---------------------------------------------------------
 *
 * RK_QUANTSUFFIX's own precedent, a second time: `^`, `$` and the plain
 * capturing group `(...)` are parsed directly in `p_atom`/`p_group_body`
 * (parse.c) with NO doorway — unlike the literal escapes, which route
 * through the real `\` doorway even when answered before reaching the
 * registry. These rows are NEVER consulted by `pcrec_registry_find`/
 * `arbitrate`; they exist for the DUMP and for D85's definitions
 * machinery, on the same "the table stays complete" reasoning `(?:...)`'s
 * own RS_BASE row above states.
 *
 * `^`/`$` each carry a two-entry `definitions` list: the REAL replacement
 * under `(?m)` (D66/D85's census, verified against libpcre2 10.46,
 * definitions_table.md §4) as the first entry, and an explicit
 * `DEF_IDENTITY` as the trailing DEF_ALWAYS entry — outside `(?m)` each is
 * ALREADY the exact alias its own `\A`/`\Z` sibling builds (D62), so there
 * is nothing to substitute. The plain capturing group's two entries are
 * `(?n)`'s builder (`pcrec_def_build_identity`, previously unused —
 * `(...)` scoped by `(?n)` IS `(?:...)`, no `A_CAP` wrapper, D31's
 * erasure) and, again, `DEF_IDENTITY` for the ordinary case (a capturing
 * group with no `(?n)` in scope is already core, `A_CAP`).
 *
 * `quant`: measured live against both python `re` and pcrec (`^*`/`$*`
 * are "nothing to repeat"/"quantifier does not follow a repeatable item"
 * in both; `(a)*`/`(a)+` compile in both) — QF_NO for the two anchors,
 * QF_YES for the group. `class_expect` is NULL for all three: RK_BARE is
 * not class-reachable any more than RK_GROUP/RK_QUANTSUFFIX are (`^`/`$`
 * have no meaning as class members at all — a literal `^`/`$` byte inside
 * `[...]` is the base grammar's OWN existing bracket-negation/plain-byte
 * handling, not a registry row); `check_wellformed`'s existing
 * `reachable = (kind == RK_ESC || kind == RK_CLASSBRACKET)` rule already
 * excludes RK_BARE with no edit needed. */
static const RegDef bol_def[] = {
    {DEFK_STR, DEF_MULTILINE, "\\A|(?<=\\n)(?!\\z)", NULL, NULL},
    {DEF_IDENTITY, DEF_ALWAYS, NULL, NULL, NULL},
    {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL},
};
/* NOTE the ASYMMETRY with bol_def, FOUND BY THE STRUCTURAL CHECK ITSELF
 * (definitions_check.c's `check_str_entry(owner, r->syntax)` call for a
 * DEF_IDENTITY entry — it parsed `$` under default mods, got A_EOL, and
 * `pcrec_ast_is_core` (definitions_table.md §2's own ruling, already
 * shipped in definitions.c) says A_EOL is NOT core: `$`'s non-multiline
 * form is `\Z`'s own shipped alias, and `\Z` itself reduces FURTHER —
 * `\Z ≡ (?=\n?\z)` — so bare `$` is not "already core" the way bare `^`
 * (A_BOL, aliasing `\A`, which IS core) is. `^`'s census-§1 claim
 * "already core" and `$`'s survive only until §2's full-reduction ruling
 * is applied literally; `$` needed a SECOND real substitution instead of
 * an identity entry once it was. Verified against libpcre2 already
 * (definitions_table.md §4 / assertions_design.md: `x\Z` vs
 * `x(?=\n?\z)`, 6/6 subjects agree). */
static const RegDef eol_def[] = {
    {DEFK_STR, DEF_MULTILINE, "(?=\\n)|\\z", NULL, NULL},
    {DEFK_STR, DEF_ALWAYS, "(?=\\n?\\z)", NULL, NULL},
    {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL},
};
static const RegDef cap_def[] = {
    {DEFK_BUILDER, DEF_NOCAP, NULL, pcrec_def_build_identity, NULL},
    {DEF_IDENTITY, DEF_ALWAYS, NULL, NULL, NULL},
    {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL},
};

static const RegRow bare_rows[] = {
{RK_BARE, '^', NULL, "^", 0, NULL, FLAV_PCRE2, ANY_ENGINE, RS_BASE, RD_NONE,
 NULL, NULL, 0,
 "start of subject, or after an internal newline under (?m) — D62's "
 "field+fold lowering; already core (A_BOL, the same node \\A builds) "
 "outside (?m)",
 ROADMAP_NONE, QF_NO, NULL, 0, NULL, NO_PORT, NO_PORT, NULL, bol_def},
{RK_BARE, '$', NULL, "$", 0, NULL, FLAV_PCRE2, ANY_ENGINE, RS_BASE, RD_NONE,
 NULL, NULL, 0,
 "end of subject (or before a final newline), or before an internal "
 "newline under (?m) — D62's field+fold lowering outside (?m) it aliases "
 "\\Z (A_EOL), which is NOT core under full reduction (unlike ^/A_BOL) — "
 "\\Z itself reduces to (?=\\n?\\z), so this row's DEF_ALWAYS entry is a "
 "real substitution, not an identity",
 ROADMAP_NONE, QF_NO, NULL, 0, NULL, NO_PORT, NO_PORT, NULL, eol_def},
{RK_BARE, '(', NULL, "(a)", 0, NULL, FLAV_PCRE2, ANY_ENGINE, RS_BASE, RD_NONE,
 NULL, NULL, 0,
 "a capturing group — already core (A_CAP) unless (?n) is scoped over "
 "it, in which case it is (?:...)'s identity (D31's erasure: no A_CAP "
 "wrapper)",
 ROADMAP_NONE, QF_YES, NULL, 0, NULL, NO_PORT, NO_PORT, NULL, cap_def},
};

/* ---- doorway 4's NAME set (FIX-2) ---------------------------------------
 *
 * The class-bracket doorway is NAME-keyed exactly as `(*` is, and it had the
 * same defect: one row answered "requires module 'classes'" for every name, so
 * `[[:foo:]]` was promised a module that will never implement it — libpcre2
 * says "unknown POSIX class name" and always will. R8/C4-7 measured the size of
 * it: 12517 of 12531 generated candidate names.
 *
 * MEASURED against libpcre2 10.46, not read: exactly these 14, case-SENSITIVE
 * (`[[:ALPHA:]]` and `[[:AlPhA:]]` are both errors), each accepting a leading
 * `^` for negation. No form bits are needed — unlike a verb name, a POSIX class
 * name has exactly one spelling.
 *
 * Kept as a name table rather than RegRows for the reason D25 gives for the
 * verb tables: a RegRow carries a flavour, a status and an engine mask this
 * question never asks. Since MOD-0.3a a name DOES carry a feature/module pair
 * — because two of the sixteen belong to a different module than the doorway
 * — and that is still one question per field, not a RegRow. pcre2_check.c
 * re-measures the name set against libpcre2 on every run. */
#define PN_CLASS(n)  { n, false, M_classes }
static const PosixName posix_names[] = {
    PN_CLASS("alnum"), PN_CLASS("alpha"), PN_CLASS("ascii"),
    PN_CLASS("blank"), PN_CLASS("cntrl"), PN_CLASS("digit"),
    PN_CLASS("graph"), PN_CLASS("lower"), PN_CLASS("print"),
    PN_CLASS("punct"), PN_CLASS("space"), PN_CLASS("upper"),
    PN_CLASS("word"),  PN_CLASS("xdigit"),
    /* AND TWO THAT ARE NOT CHARACTER CLASSES AT ALL. `[[:<:]]` and `[[:>:]]`
     * are zero-width WORD BOUNDARY assertions PCRE2 inherited from its Unix
     * ancestry — measured on "abc def": `[[:<:]]def` matches [4,7) and
     * `abc[[:>:]]` matches [0,3). I wrote the list above from the fourteen I
     * had eyeballed in libpcre2's string table and PC-3's generated name
     * differential found these two on its first run, which is the difference
     * between listing a space and generating it, one level down from where R8
     * already learned it. MOD-0.3a (2026-08-12) split them out to module
     * `assertions` — the module `\b`'s own row already carries — because a
     * boundary assertion is not a set of characters, and once `classes` has
     * producers, promising `classes` for a construct it will never produce is
     * the enabled-module lie K14 exists to forbid. whole_class_only is the
     * OTHER measured fact about them (R9/C3-4): legal only as the class's
     * entire content, and unnegatable. */
    { "<", true, M_assertions },
    { ">", true, M_assertions },
};
#undef PN_CLASS

/* ---- the `(?` doorway's OPTION RUN (Q2) ---------------------------------
 *
 * MOVED to src/parse/mod_modifiers.c at MOD-0.5b (slice 1 of module
 * `modifiers`): pcrec_registry_option_run_ok, its measured grammar comment,
 * and the recogniser that replaces RF_OPTION_RUN
 * (pcrec_registry_option_run_recognise) all live there now, together, on the
 * probes-and-code-together rule the block itself explains. This file no
 * longer claims that grammar — see mod_modifiers.c and GROUP_OPT below. */

const PosixName *pcrec_registry_posix_names(size_t *n)
{
    *n = sizeof posix_names / sizeof posix_names[0];
    return posix_names;
}

const PosixName *pcrec_registry_posix_find(const char *name, size_t len)
{
    for (size_t i = 0; i < sizeof posix_names / sizeof posix_names[0]; i++)
        if (strlen(posix_names[i].name) == len &&
            memcmp(posix_names[i].name, name, len) == 0)
            return &posix_names[i];
    return NULL;
}

bool pcrec_registry_posix_whole_class_only(const char *name, size_t len)
{
    /* `<` and `>` are not classes, and libpcre2 does not let them sit among
     * class members the way a class can. Measured against 10.46 (R9/C3-4):
     *
     *   [[:<:]]           compiles      the ONLY shape that works
     *   [x[:<:]]          error 130     a member before it
     *   [[:<:]a]          error 130     a member after it
     *   [^[:<:]]          error 130     even a bare `^`
     *   [[:alpha:][:<:]]  error 130     another POSIX class before it
     *   [x[:alpha:]]      compiles      position never matters for a real class
     *
     * pcrec answered "requires module 'classes'" for every one of those — a
     * module promised for patterns PCRE2 will never accept, which is the exact
     * over-promise FIX-2 set out to remove, surviving for the two names FIX-2
     * itself discovered. The two differentials that should have caught it each
     * vary one axis: the name sweep only ever builds `[[:NAME:]]`, and the
     * shape sweep never uses `<` or `>` as a body. The defect lives in the cell
     * of the cross-product neither generates. */
    if (len && name[0] == '^') return false;   /* `^<` is already not-known */
    const PosixName *pn = pcrec_registry_posix_find(name, len);
    return pn && pn->whole_class_only;
}

const char *pcrec_registry_posix_unknown_msg(void)
{
    /* PCRE2's own wording. It names no module ON PURPOSE — that is the whole
     * point of the row, and registry_check.c asserts the absence. */
    return "unknown POSIX class name";
}

bool pcrec_registry_posix_known(const char *name, size_t len)
{
    /* `^` negates a CLASS, and `<`/`>` are not classes — they are zero-width
     * word-boundary assertions, so there is nothing to negate. Measured:
     * `[[:^alpha:]]` compiles and `[[:^<:]]` is an error. Found by PC-3's name
     * differential, which probes both spellings of every candidate. */
    bool neg = len && name[0] == '^';
    if (neg) { name++; len--; }
    const PosixName *pn = pcrec_registry_posix_find(name, len);
    if (!pn) return false;
    if (neg && pn->whole_class_only) return false;  /* an assertion cannot negate */
    return true;
}

/* ---- lookup -------------------------------------------------------------
 * A linear scan, deliberately, where SR-1's plan text said a [256] index per
 * kind. Measured: a full 39-row miss costs 33.6 ns against a 90 us floor for
 * the cheapest compile pcrec can perform, on a path taken at most ONCE per
 * compile today (every hit but `(?:` ends the compile with a diagnostic), and
 * bounded by pattern length once modules land. An index would buy ~23 ns of a
 * 0.03% slice — the unmeasured axis D18 forbids.
 *
 * Callers use pcrec_registry_find and do not depend on how it searches;
 * pcrec_registry exposes the rows for ITERATION only (SR-3's dump). Swapping in
 * a byte-indexed table later is a change to this function alone. SR-6 is the
 * forcing function: doorway hits go from once-per-compile to once-per-construct
 * then, which is the first time the cost is measurable against M2.9's budgets. */

const RegRow *pcrec_registry(RegKind k, size_t *n)
{
    switch (k) {
    case RK_ESC:          *n = sizeof esc_rows          / sizeof esc_rows[0];          return esc_rows;
    case RK_GROUP:        *n = sizeof group_rows        / sizeof group_rows[0];        return group_rows;
    case RK_VERB:         *n = sizeof verb_rows         / sizeof verb_rows[0];         return verb_rows;
    case RK_CLASSBRACKET: *n = sizeof classbracket_rows / sizeof classbracket_rows[0]; return classbracket_rows;
    /* [M6.4.2] the fifth kind. `default:` below is what makes a MISSING arm
     * here silent — every RegKind switch in the tree carries one, measured, so
     * `-Wswitch` names none of them — which is why the omission that matters is
     * caught by tests/registry/registry_check.c reading the DUMP OUTPUT and by
     * its `check_table_to_parser` now iterating RK_COUNT, not by the compiler. */
    case RK_QUANTSUFFIX:  *n = sizeof quantsuffix_rows  / sizeof quantsuffix_rows[0];  return quantsuffix_rows;
    /* [DD-11.1] the sixth kind, RK_QUANTSUFFIX's own precedent a second
     * time (internal.h's comment on RK_BARE has the ruling). */
    case RK_BARE:         *n = sizeof bare_rows         / sizeof bare_rows[0];         return bare_rows;
    default:              *n = 0;                                                      return NULL;
    }
}

/* ---- MOD-0.2: recogniser + rank arbitration (design §2.2/D32, §14.4) ----
 *
 * Row selection stopped being tail INTERPRETATION at MOD-0.2. Each row's
 * recogniser answers for its own proper form — positive and local, knowing
 * nothing of its siblings — and `rank` is the local tiebreak between
 * answering rows. `tail` survives only as the parameter of the default
 * recogniser below. */

bool pcrec_recognise_tail_default(const char *at, size_t avail, const char *tail)
{
    size_t tl;
    /* No tail: the bucket's own fallback, and it answers ALWAYS — that is
     * correct, not naive (D32 §2); outranking it is the tailed rows' job. */
    if (!tail) return true;
    tl = strlen(tail);
    /* `at` may be NULL when a caller has no text to offer (the dump, and any
     * probe that asks about a byte rather than a pattern). That is the
     * tail-less question, not a reason to read a null pointer. */
    return at && tl <= avail && memcmp(at, tail, tl) == 0;
}

/* Exposed (not static) so registry_check counts answers with the ENGINE'S
 * OWN predicate rather than a second copy that could drift (R15, checks
 * critic). The oracle duty stays elsewhere — the per-row syntax checks and
 * PC-3 — so sharing this source with the liveness counter costs nothing a
 * duplicate would have caught. */
bool pcrec_registry_row_answers(const RegRow *r, const char *at, size_t avail)
{
    return (r->recognise ? r->recognise
                         : pcrec_recognise_tail_default)(at, avail, r->tail);
}

/* Every sel-matching row's recogniser runs; the highest-ranked ANSWERING row
 * wins; the kind's catch-all is the answer only when nothing answers. `sel`
 * survives as a checkable pre-test — "do not ask me unless the byte matches"
 * (D32 §7) — not as the key it was before SR-9's tails, and REG_SEL_ANY is
 * still a catch-all across bytes, not a bucket fallback.
 *
 * TWO ANSWERS AT THE WINNING RANK is the defect (D32 §2): the arbitration
 * cannot elect a row, and falling back to declaration order would make order
 * a rule nobody maintains. A tie BELOW the winner is rank doing its job.
 * Unreachable on the correct table (0 collisions over the generated space —
 * registry_check's arbitration checks keep that measured); the escape and
 * group doorways render it as an internal error, never a silent choice. */
const RegRow *pcrec_registry_arbitrate(RegKind k, int sel, const char *at,
                                       size_t avail, bool *ambiguous)
{
    size_t n;
    const RegRow *rows = pcrec_registry(k, &n);
    const RegRow *any = NULL, *best = NULL;
    bool tie = false;

    for (size_t i = 0; i < n; i++) {
        /* [M6.6.2 wave F / D71 item 3] AN INDEX ROW NEVER DISPATCHES, and
         * this line is the whole of that mechanism — one skip, in the one
         * function row selection happens in, so no doorway can reach such a
         * row down any path. See RF_INDEX in internal.h for why the twelve
         * `(*` alpha lookaround spellings have rows but no byte-keyed
         * dispatch identity, and mod_verbs.c for what DOES find them (a NAME
         * lookup, which is how the `(*` doorway has dispatched since D25/Q1).
         *
         * THE SKIP MUST PRECEDE THE `REG_SEL_ANY` ARM, not follow it: an
         * index row carries REG_SEL_ANY (no byte selects it) and that arm
         * assigns unconditionally, so the LAST such row would become the
         * kind's catch-all — the verb doorway would stop finding its own
         * `(*ACCEPT)` row and every verb in the tree would answer wrongly.
         * Ordering here is load-bearing, which is why it is stated rather
         * than left to a reader to reconstruct from a failure. */
        if (rows[i].flags & RF_INDEX) continue;
        if (rows[i].sel == REG_SEL_ANY) { any = &rows[i]; continue; }
        if (rows[i].sel != sel) continue;
        if (!pcrec_registry_row_answers(&rows[i], at, avail)) continue;
        if (!best || rows[i].rank > best->rank) { best = &rows[i]; tie = false; }
        else if (rows[i].rank == best->rank)    tie = true;
    }
    if (ambiguous) *ambiguous = (best != NULL && tie);
    return best ? best : any;
}

/* Since MOD-0.2's wiring slice this IS the arbitration; callers that can
 * surface the ambiguity defect (the escape and group doorways) call
 * pcrec_registry_arbitrate directly for the out-param. Equivalence with the
 * retired engine held over 261,193 scaffold probes and the 5,247-comparison
 * behavioural differential before this line changed. */
const RegRow *pcrec_registry_find(RegKind k, int sel, const char *at, size_t avail)
{
    return pcrec_registry_arbitrate(k, sel, at, avail, NULL);
}
