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
 * could lower each construct. Nothing consumes it until SR-8/M4, and the
 * conformance test asserts only that it is well-formed.
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
/* One byte, two constructs: `(?<` is lookbehind OR a named group. The compound
 * name is the diagnostic PCREC prints today and SR-2 must reproduce it. */
#define M_lookaround_named \
    FEAT_LOOKAROUND | FEAT_NAMED_GROUPS, "lookaround/named-groups"

#define ANY_ENGINE  (ENGM_DFA | ENGM_VM)
#define VM_ONLY     ENGM_VM

/* \x outside a class -> "\x requires module 'M'" */
#define ESC(sel, syn, mod, eng, note) \
    {RK_ESC, (sel), (syn), M_##mod, FLAV_PCRE2, (eng), RS_MODULE, RD_MODULE, NULL, 0, (note)}
/* as ESC, but inside a class the byte is BASE syntax and the doorway is not taken */
#define ESC_CLASS_BASE(sel, syn, mod, eng, note) \
    {RK_ESC, (sel), (syn), M_##mod, FLAV_PCRE2, (eng), RS_MODULE, RD_MODULE, NULL, RF_CLASS_BASE, (note)}
/* \0..\9 -> "\N (backreference/octal) requires module 'backrefs'".
 * NOT named ESC_OCTAL: \1..\9 are never octal in PCRE2 — see the note above
 * the digit rows. The macro is named for the DIAGNOSTIC SHAPE it produces,
 * which is a different thing from the construct's semantics. */
#define ESC_DIGIT(sel, syn, eng, note) \
    {RK_ESC, (sel), (syn), M_backrefs, FLAV_PCRE2, (eng), RS_MODULE, RD_MODULE_OCTAL, NULL, 0, (note)}
/* (?X -> "(?X...) requires module 'M'" */
#define GROUP(sel, syn, mod, eng, note) \
    {RK_GROUP, (sel), (syn), M_##mod, FLAV_PCRE2, (eng), RS_MODULE, RD_MODULE, NULL, 0, (note)}
/* a construct whose entire diagnostic is fixed text rather than a template */
#define FIXED(kind, sel, syn, mod, eng, msg, note) \
    {(kind), (sel), (syn), M_##mod, FLAV_PCRE2, (eng), RS_MODULE, RD_FIXED, (msg), 0, (note)}
/* PCRE2 rejects it too: no module to name, no feature to enable, no engine to
 * lower to. Agreement IS compliance. */
#define REJECTED(kind, sel, syn, msg, note) \
    {(kind), (sel), (syn), 0, NULL, FLAV_PCRE2, 0, RS_REJECTED, RD_FIXED, (msg), 0, (note)}
/* as REJECTED, but a delimiter-pair construct: RF_CLASS_DELIM carries the two
 * recognition rules that SR-2 moved out of parse.c — see internal.h. */
#define REJECTED_DELIM(kind, sel, syn, msg, note) \
    {(kind), (sel), (syn), 0, NULL, FLAV_PCRE2, 0, RS_REJECTED, RD_FIXED, (msg), \
     RF_CLASS_DELIM, (note)}

/* ---- doorway 1: after '\' ----------------------------------------------
 * Only non-base escapes. \n \t \r \f \a \e \xHH decode in parse.c and never
 * arrive here. */
static const RegRow esc_rows[] = {
ESC('d', "\\d", classes, ANY_ENGINE, "any decimal digit"),
ESC('D', "\\D", classes, ANY_ENGINE, "any character that is not a decimal digit"),
ESC('s', "\\s", classes, ANY_ENGINE, "any whitespace character"),
ESC('S', "\\S", classes, ANY_ENGINE, "any character that is not whitespace"),
ESC('w', "\\w", classes, ANY_ENGINE, "any word character (letter, digit or underscore)"),
ESC('W', "\\W", classes, ANY_ENGINE, "any character that is not a word character"),
ESC('h', "\\h", classes, ANY_ENGINE, "any horizontal whitespace character"),
ESC('H', "\\H", classes, ANY_ENGINE, "any character that is not horizontal whitespace"),
/* THE ROW THIS WHOLE FILE EXISTS FOR. PCRE2's `\v` is vertical WHITESPACE —
 * 0x0a 0x0b 0x0c 0x0d 0x85 — not the vertical tab 0x0B. pcrec decoded it as
 * 0x0B until 2026-08-09; the corpus certified the bug because python `re`, the
 * base-tier oracle, reads `\v` as 0x0B too. It is also the only known
 * flavour-varying row, i.e. the single member of the set SR-7 is deferred for. */
ESC('v', "\\v", classes, ANY_ENGINE, "any vertical whitespace character (NOT vertical tab; python re disagrees)"),
ESC('V', "\\V", classes, ANY_ENGINE, "any character that is not vertical whitespace"),
ESC('N', "\\N", classes, ANY_ENGINE, "any character except newline (PCRE2 forbids it inside a class)"),

ESC_CLASS_BASE('b', "\\b", assertions, ANY_ENGINE,
               "word boundary — but inside a class it is BASE syntax: backspace (0x08)"),
ESC('B', "\\B", assertions, ANY_ENGINE, "not a word boundary"),
ESC('A', "\\A", assertions, ANY_ENGINE, "start of subject"),
ESC('Z', "\\Z", assertions, ANY_ENGINE, "end of subject, or before a final newline"),
ESC('z', "\\z", assertions, ANY_ENGINE, "end of subject"),
ESC('G', "\\G", assertions, ANY_ENGINE, "first matching position in the subject"),
ESC('K', "\\K", assertions, VM_ONLY,    "reset the reported start of the match"),

ESC('k', "\\k<name>", backrefs, VM_ONLY, "backreference by name: \\k<n> \\k'n' \\k{n}"),
ESC('g', "\\g{-1}",   backrefs, VM_ONLY, "backreference by number or relative position: \\g1 \\g{-1} \\g{name}"),

ESC('p', "\\p{L}", unicode_props, ANY_ENGINE, "a character with the given Unicode property"),
ESC('P', "\\P{L}", unicode_props, ANY_ENGINE, "a character without the given Unicode property"),

ESC('Q', "\\Q", quoting, ANY_ENGINE, "begin literal quoting, until \\E"),
ESC('E', "\\E", quoting, ANY_ENGINE, "end literal quoting begun by \\Q"),

ESC('R', "\\R",      misc, ANY_ENGINE, "any Unicode newline sequence"),
ESC('X', "\\X",      misc, ANY_ENGINE, "a Unicode extended grapheme cluster"),
ESC('C', "\\C",      misc, ANY_ENGINE, "one data unit (byte), even in UTF mode"),
ESC('c', "\\cX",     misc, ANY_ENGINE, "control character: \\cX is X xor 0x40"),
ESC('o', "\\o{101}", misc, ANY_ENGINE, "character with the given octal code"),

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
 * the truth lives until then. Recorded in docs/known_issues.md. */
ESC_DIGIT('0', "\\0", ANY_ENGINE, "octal escape \\0dd — never a backreference (there is no group 0)"),
ESC_DIGIT('1', "\\1", VM_ONLY, "backreference to capture group 1 (PCRE2 error 115 if no such group)"),
ESC_DIGIT('2', "\\2", VM_ONLY, "backreference to capture group 2 (PCRE2 error 115 if no such group)"),
ESC_DIGIT('3', "\\3", VM_ONLY, "backreference to capture group 3 (PCRE2 error 115 if no such group)"),
ESC_DIGIT('4', "\\4", VM_ONLY, "backreference to capture group 4 (PCRE2 error 115 if no such group)"),
ESC_DIGIT('5', "\\5", VM_ONLY, "backreference to capture group 5 (PCRE2 error 115 if no such group)"),
ESC_DIGIT('6', "\\6", VM_ONLY, "backreference to capture group 6 (PCRE2 error 115 if no such group)"),
ESC_DIGIT('7', "\\7", VM_ONLY, "backreference to capture group 7 (PCRE2 error 115 if no such group)"),
ESC_DIGIT('8', "\\8", VM_ONLY, "backreference to capture group 8 (PCRE2 error 115 if no such group)"),
ESC_DIGIT('9', "\\9", VM_ONLY, "backreference to capture group 9 (PCRE2 error 115 if no such group)"),
};

/* ---- doorway 2: after '(?' ---------------------------------------------- */
static const RegRow group_rows[] = {
/* The one registry row the base tier reaches, and it must stay that way: SR-5's
 * fast-path guard concerns this row. NOTE (R6): a base pattern does not in fact
 * reach it — parse.c answers `(?:` first, so this row costs zero lookups and the
 * ones a base pattern DOES perform are all at the class-bracket doorway. Written longhand deliberately — the only supported construct in the
 * file should not be able to hide inside a macro that means "rejected". */
{RK_GROUP, ':', "(?:...)",
 0, NULL,
 FLAV_PCRE2, ANY_ENGINE,
 RS_BASE, RD_NONE, NULL, 0,
 "non-capturing group"},

GROUP('=',  "(?=...)",       lookaround,       VM_ONLY, "positive lookahead"),
GROUP('!',  "(?!...)",       lookaround,       VM_ONLY, "negative lookahead"),
GROUP('<',  "(?<=...)",      lookaround_named, VM_ONLY,
      "lookbehind (?<=...) (?<!...), or named capture group (?<name>...)"),
GROUP('\'', "(?'name'...)",  named_groups,     VM_ONLY, "named capture group, Perl-style quoting"),
GROUP('P',  "(?P<name>...)", named_groups,     VM_ONLY,
      "python-style named group (?P<n>...), backreference (?P=n), recursion (?P>n)"),
GROUP('>',  "(?>...)",       atomic_groups,    VM_ONLY, "atomic (non-backtracking) group"),
GROUP('#',  "(?#...)",       comments,     ANY_ENGINE, "comment, discarded up to the next ')'"),
GROUP('C',  "(?C1)",         callouts,         VM_ONLY, "callout to user code: (?C) (?C1) (?C{text})"),
GROUP('|',  "(?|...)",       branch_reset,     VM_ONLY,
      "branch reset group: alternatives reuse the same capture numbers"),
GROUP('(',  "(?(1)a|b)",     conditionals,     VM_ONLY, "conditional group (?(condition)yes|no)"),
GROUP('&',  "(?&name)",      recursion,        VM_ONLY, "recurse into the named group"),
GROUP('R',  "(?R)",          recursion,        VM_ONLY, "recurse the whole pattern"),
GROUP('0',  "(?0)",          recursion,        VM_ONLY, "recurse the whole pattern (synonym for (?R))"),
GROUP('1',  "(?1)",          recursion,        VM_ONLY, "recurse into capture group 1"),
GROUP('2',  "(?2)",          recursion,        VM_ONLY, "recurse into capture group 2"),
GROUP('3',  "(?3)",          recursion,        VM_ONLY, "recurse into capture group 3"),
GROUP('4',  "(?4)",          recursion,        VM_ONLY, "recurse into capture group 4"),
GROUP('5',  "(?5)",          recursion,        VM_ONLY, "recurse into capture group 5"),
GROUP('6',  "(?6)",          recursion,        VM_ONLY, "recurse into capture group 6"),
GROUP('7',  "(?7)",          recursion,        VM_ONLY, "recurse into capture group 7"),
GROUP('8',  "(?8)",          recursion,        VM_ONLY, "recurse into capture group 8"),
GROUP('9',  "(?9)",          recursion,        VM_ONLY, "recurse into capture group 9"),
/* Catch-all, and it must stay last: everything else after `(?` is an inline
 * option setting. Options DENOTE rather than MEAN (D24's second axis), and
 * OS-1/D23 already showed one folding entirely into the automaton, which is why
 * this row is DFA-lowerable while most of its neighbours are not. */
GROUP(REG_SEL_ANY, "(?i)", modifiers, ANY_ENGINE,
      "inline option setting or scoping: (?i) (?im-sx:...) (?^) (?-i)"),
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
static const RegRow verb_rows[] = {
FIXED(RK_VERB, REG_SEL_ANY, "(*ACCEPT)", verbs, VM_ONLY,
      "(*...) requires module 'verbs'",
      "backtracking verb ((*SKIP), (*ACCEPT)), start-of-pattern option ((*CR), (*UTF)) "
      "or script run ((*script_run:...))"),
};

/* ---- doorway 3's NAME tables (Q1) ---------------------------------------
 *
 * EVERY BIT IN THESE TWO TABLES IS A MEASUREMENT, not a reading of PCRE2's
 * documentation: taken 2026-08-10 against libpcre2 10.46 with options = 0, and
 * re-taken on every run by tests/registry/pcre2_check.c, which fails if any
 * entry has drifted from what the installed libpcre2 actually does. If you
 * change a row here without measuring, that check tells you.
 *
 * The candidate NAMES did not come from memory either. They were generated
 * from the ASCII runs in libpcre2's own shared object — PCRE2's compiled-in
 * name tables — and every candidate was then compiled to decide whether it is
 * real. pcre2_check.c regenerates that pool on every run, which is what turns
 * "did we forget a verb" from unanswerable into a test result.
 *
 * The shapes are strikingly regular, and the regularity is the point: five
 * groups, and no name deviates from its group except `MARK`.
 *
 * Order within a table does not matter (lookup is exact-match), but the groups
 * are kept together and in PCRE2's own documented order so a reader can diff
 * this against pcre2syntax. */
static const VerbName verb_upper[] = {
/* Backtracking control verbs. An argument is optional and may be empty:
 * `(*ACCEPT)`, `(*ACCEPT:x)` and `(*ACCEPT:)` all compile. */
{"ACCEPT", VF_BARE | VF_ARG | VF_EMPTYARG, 0, NULL},
{"FAIL",   VF_BARE | VF_ARG | VF_EMPTYARG, 0, NULL},
{"F",      VF_BARE | VF_ARG | VF_EMPTYARG, 0, NULL},
{"COMMIT", VF_BARE | VF_ARG | VF_EMPTYARG, 0, NULL},
{"PRUNE",  VF_BARE | VF_ARG | VF_EMPTYARG, 0, NULL},
{"SKIP",   VF_BARE | VF_ARG | VF_EMPTYARG, 0, NULL},
{"THEN",   VF_BARE | VF_ARG | VF_EMPTYARG, 0, NULL},

/* The one irregular name in either table, and the reason `own_forms`/`own_msg`
 * exist. `(*MARK)` and `(*MARK:)` are error 166 with a message of their own;
 * `(*MARK=1)` and a truncated `(*MARK` are the ordinary 160. The empty name in
 * `(*:x)` is a MARK synonym and reaches this row — see pcrec_ext_verb. */
{"MARK",   VF_ARG, VF_BARE | VF_EMPTYARG, "(*MARK) must have an argument"},

/* Start-of-pattern options. Bare form only, and only at offset 0:
 * `a(*CR)` is error 160. */
{"UTF",               VF_BARE | VF_ATSTART, 0, NULL},
{"UTF8",              VF_BARE | VF_ATSTART, 0, NULL},
{"UCP",               VF_BARE | VF_ATSTART, 0, NULL},
{"NOTEMPTY",          VF_BARE | VF_ATSTART, 0, NULL},
{"NOTEMPTY_ATSTART",  VF_BARE | VF_ATSTART, 0, NULL},
{"NO_AUTO_POSSESS",   VF_BARE | VF_ATSTART, 0, NULL},
{"NO_DOTSTAR_ANCHOR", VF_BARE | VF_ATSTART, 0, NULL},
{"NO_JIT",            VF_BARE | VF_ATSTART, 0, NULL},
{"NO_START_OPT",      VF_BARE | VF_ATSTART, 0, NULL},
{"CASELESS_RESTRICT", VF_BARE | VF_ATSTART, 0, NULL},
/* Recognised, and this build cannot honour it: `(*TURKISH_CASING)` is error
 * 204, "require Unicode (UTF or UCP) mode" — a capability refusal, not a
 * syntax one, and our oracle compiles with options = 0 so it can never be in
 * that mode. pcre2_check.c buckets 204 with "PCRE2 recognised the construct",
 * which is why this row needs no exclusion. */
{"TURKISH_CASING",    VF_BARE | VF_ATSTART, 0, NULL},
{"CR",                VF_BARE | VF_ATSTART, 0, NULL},
{"LF",                VF_BARE | VF_ATSTART, 0, NULL},
{"CRLF",              VF_BARE | VF_ATSTART, 0, NULL},
{"ANYCRLF",           VF_BARE | VF_ATSTART, 0, NULL},
{"ANY",               VF_BARE | VF_ATSTART, 0, NULL},
{"NUL",               VF_BARE | VF_ATSTART, 0, NULL},
{"BSR_ANYCRLF",       VF_BARE | VF_ATSTART, 0, NULL},
{"BSR_UNICODE",       VF_BARE | VF_ATSTART, 0, NULL},

/* `=digits` only, and at offset 0.
 *
 * THE RULE, swept to exhaustion (R8/C2-9: 209 digit strings x 4 names, 836
 * probes, all four names agreeing on every one): strip leading zeros, then
 * reject if what remains has MORE THAN TEN DIGITS, or has exactly ten and its
 * first nine exceed 429496728. That is PCRE2 refusing one digit BEFORE its
 * uint32_t accumulator would overflow, which is why the boundary is
 * 4294967290 and not 4294967295.
 *
 * This comment used to read "`(*LIMIT_MATCH=x)` and `(*LIMIT_MATCH= 1)` are
 * both error 160; `(*LIMIT_MATCH=01)` compiles" — three true facts, measured on
 * one- and two-digit inputs, that induce the WRONG rule ("digits, at least
 * one") and left `ext.c` accepting `=99999999999`. Examples are not a rule.
 * `ext.c` implements the paragraph above. */
{"LIMIT_MATCH",     VF_EQNUM | VF_ATSTART, 0, NULL},
{"LIMIT_DEPTH",     VF_EQNUM | VF_ATSTART, 0, NULL},
{"LIMIT_HEAP",      VF_EQNUM | VF_ATSTART, 0, NULL},
{"LIMIT_RECURSION", VF_EQNUM | VF_ATSTART, 0, NULL},
};

/* The lower table. Every name here takes a SUBPATTERN argument — these are
 * group constructs spelled as verbs — so the bare form is an error and the
 * argument may be empty. Position-free, unlike the options above.
 * `(*scs:x)` is error 115 (a subpattern reference that does not resolve),
 * which is PCRE2 recognising the name and rejecting the reference. */
static const VerbName verb_lower[] = {
{"pla",                            VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL},
{"plb",                            VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL},
{"napla",                          VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL},
{"naplb",                          VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL},
{"nla",                            VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL},
{"nlb",                            VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL},
{"positive_lookahead",             VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL},
{"positive_lookbehind",            VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL},
{"non_atomic_positive_lookahead",  VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL},
{"non_atomic_positive_lookbehind", VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL},
{"negative_lookahead",             VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL},
{"negative_lookbehind",            VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL},
{"atomic",                         VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL},
{"sr",                             VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL},
{"asr",                            VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL},
{"script_run",                     VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL},
{"atomic_script_run",              VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL},
{"scs",                            VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL},
{"scan_substring",                 VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL},
};

/* The two "no such name" messages are PCRE2's own wording, byte for byte, for
 * the same reason the collating rows use PCRE2's: where AGREEMENT is the whole
 * claim, saying it in different words makes the claim harder to check and no
 * clearer to a reader. Error 160 and error 195 respectively. */
static const VerbTable verb_tables[2] = {
    {"(*VERB) not recognized or malformed",
     verb_upper, sizeof verb_upper / sizeof verb_upper[0]},
    {"(*alpha_assertion) not recognized",
     verb_lower, sizeof verb_lower / sizeof verb_lower[0]},
};

/* PCRE2's cap on a NAME, and the complaint it makes past it. Both tables share
 * one limit and one message, so it lives beside them rather than inside either.
 * Measured (R8/C2-4) on libpcre2 10.46: a 128-byte name is the ordinary "not
 * recognized" for its table, a 129-byte one is error 148, in every form. The
 * cap is on the name only — a 200-byte ARGUMENT compiles. */
const char *pcrec_registry_verb_name_limit(size_t *max)
{
    /* 128 is the ONLY length boundary, and it is table-independent: swept over
     * every length 1..319 in both tables (R8/C2-9), there are exactly two
     * transitions in 638 probes and both are at 129. */
    *max = 128;
    return "subpattern name is too long (maximum 128 code units)";
}

const VerbTable *pcrec_registry_verb_tables(int which)
{
    return (which == 0 || which == 1) ? &verb_tables[which] : NULL;
}

/* Which table PCRE2 consults, decided by the case of the FIRST name byte and
 * nothing else. Measured over all 256 bytes: only 'a'..'z' select the lower
 * table. A name starting with a digit, an underscore or any high byte goes to
 * the upper one and gets error 160. */
const VerbTable *pcrec_registry_verb_table(int first)
{
    return (first >= 'a' && first <= 'z') ? &verb_tables[1] : &verb_tables[0];
}

const VerbName *pcrec_registry_verb_find(const VerbTable *t,
                                         const char *name, size_t len)
{
    for (size_t i = 0; i < t->n; i++)
        if (strlen(t->rows[i].name) == len && memcmp(t->rows[i].name, name, len) == 0)
            return &t->rows[i];
    return NULL;
}

/* ---- doorway 4: after '[' inside a class -------------------------------- */
static const RegRow classbracket_rows[] = {
FIXED(RK_CLASSBRACKET, ':', "[[:alpha:]]", classes, ANY_ENGINE,
      "POSIX class [:...:] requires module 'classes'",
      "POSIX character class"),
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
               "POSIX collating element — PCRE2 rejects it, and so must we"),
REJECTED_DELIM(RK_CLASSBRACKET, '=', "[[=a=]]", "POSIX collating elements are not supported",
               "POSIX equivalence class — PCRE2 rejects it, and so must we"),
};

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
    default:              *n = 0;                                                      return NULL;
    }
}

/* Exact selector match first, then the kind's catch-all row if it has one.
 * Returns NULL when the byte belongs to no construct — the caller's "unknown
 * escape" path. */
const RegRow *pcrec_registry_find(RegKind k, int sel)
{
    size_t n;
    const RegRow *rows = pcrec_registry(k, &n);
    const RegRow *any = NULL;

    for (size_t i = 0; i < n; i++) {
        if (rows[i].sel == sel) return &rows[i];
        if (rows[i].sel == REG_SEL_ANY) any = &rows[i];
    }
    return any;
}
