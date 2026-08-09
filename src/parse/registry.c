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
 * The base tier reaches exactly ONE of them, once, for `(?:`. So Frank's
 * performance principle — normal stuff fast, weird stuff may cost lookups — is
 * satisfied BY CONSTRUCTION, not by optimisation. SR-5 guards that claim with
 * an instrumented build rather than leaving it asserted.
 *
 * WHAT IS NOT HERE, DELIBERATELY. Base syntax: literals, `.`, classes and
 * ranges, quantifiers, `|`, `(...)`, `^`, `$`, and the plain character escapes
 * \n \t \r \f \a \e \xHH. Those never consult this table. Two "requires
 * module" diagnostics also remain in parse.c because they are sub-cases of
 * BASE constructs rather than doorways, and inventing a doorway for them would
 * cost the base tier a lookup: `\x{...}` (reached only from the base `\x`
 * handler) and the possessive `+` suffix (a quantifier suffix, not an atom).
 * They are the registry's two known outstanding second homes.
 *
 * FOUR AXES, KEPT APART. flavour (which construct a byte MEANS) / option (what
 * it DENOTES) / enablement (is it available) / engine (can it LOWER). Answering
 * all four with one mechanism is what produces an `if python-compat X else if
 * pcre2-dfa Y else Z` cascade. Kept apart, a flavour change REBINDS A ROW and
 * cannot reach inside another construct's handler.
 *
 * THE `engines` COLUMN IS DESIGN INTENT, NOT MEASUREMENT. It records which
 * PCREC engine could lower each construct — not what PCRE2's own DFA supports.
 * Nothing consumes it until SR-8/M4, and the conformance test asserts only
 * that it is well-formed. Treat the values as a claim to be checked when the
 * VM lands, not as an established fact.
 *
 * ADDING A ROW: fill it in here and nowhere else. `syntax` must be a pattern
 * that actually reaches this doorway — tests/registry/ uses it as the probe,
 * which is how a new row covers itself without a test edit. A NULL handler
 * (SR-2 introduces the field) and RS_MODULE status is a COMPLETE outcome: the
 * construct is named, cleanly rejected and queryable. It is not a stub. */

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
/* \0..\9 -> "\N (backreference/octal) requires module 'backrefs'" */
#define ESC_OCTAL(sel, syn, eng, note) \
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

/* Digits. `\0` is octal; `\1`..`\9` are a backreference, or an octal escape
 * when no such capture group exists — an ambiguity resolved against the group
 * count, which is why the backreference reading is VM-only. pcrec gives all ten
 * the same diagnostic today, and SR-2 must not change that. */
ESC_OCTAL('0', "\\0", ANY_ENGINE, "octal escape \\0dd"),
ESC_OCTAL('1', "\\1", VM_ONLY, "backreference to capture group 1 (octal escape if no such group)"),
ESC_OCTAL('2', "\\2", VM_ONLY, "backreference to capture group 2 (octal escape if no such group)"),
ESC_OCTAL('3', "\\3", VM_ONLY, "backreference to capture group 3 (octal escape if no such group)"),
ESC_OCTAL('4', "\\4", VM_ONLY, "backreference to capture group 4 (octal escape if no such group)"),
ESC_OCTAL('5', "\\5", VM_ONLY, "backreference to capture group 5 (octal escape if no such group)"),
ESC_OCTAL('6', "\\6", VM_ONLY, "backreference to capture group 6 (octal escape if no such group)"),
ESC_OCTAL('7', "\\7", VM_ONLY, "backreference to capture group 7 (octal escape if no such group)"),
ESC_OCTAL('8', "\\8", VM_ONLY, "backreference to capture group 8 (octal escape if no such group)"),
ESC_OCTAL('9', "\\9", VM_ONLY, "backreference to capture group 9 (octal escape if no such group)"),
};

/* ---- doorway 2: after '(?' ---------------------------------------------- */
static const RegRow group_rows[] = {
/* The one registry row the base tier reaches, and it must stay that way: SR-5's
 * fast-path guard is exactly "a base pattern performs no lookup other than this
 * one". Written longhand deliberately — the only supported construct in the
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
 * A NAME decides here, but pcrec does not yet distinguish the names: one
 * catch-all row reproduces today's single blanket diagnostic exactly. Per-verb
 * rows arrive with the module (SR-6), not before — naming forty verbs that
 * nothing distinguishes and no test exercises would be fiction in a file whose
 * whole purpose is to stop syntax knowledge from being fiction. */
static const RegRow verb_rows[] = {
FIXED(RK_VERB, REG_SEL_ANY, "(*...)", verbs, VM_ONLY,
      "(*...) requires module 'verbs'",
      "backtracking verb ((*SKIP), (*ACCEPT)), start-of-pattern option ((*CR), (*UTF)) "
      "or script run ((*script_run:...))"),
};

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
 * `=]` appears later — see reject_collating() in parse.c, which owns the
 * lookahead. Over-rejecting here would break patterns PCRE2 accepts. */
REJECTED(RK_CLASSBRACKET, '.', "[[.a.]]", "POSIX collating elements are not supported",
         "POSIX collating element — PCRE2 rejects it, and so must we"),
REJECTED(RK_CLASSBRACKET, '=', "[[=a=]]", "POSIX collating elements are not supported",
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
