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

/* ---- doorway 1: after '\' ----------------------------------------------
 * Only non-base escapes. \n \t \r \f \a \e \xHH decode in parse.c and never
 * arrive here. */
static const RegRow esc_rows[] = {
{RK_ESC, 'd', "\\d", FEAT_CLASSES, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "classes", RS_MODULE, RD_MODULE, NULL, 0,
 "any decimal digit"},
{RK_ESC, 'D', "\\D", FEAT_CLASSES, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "classes", RS_MODULE, RD_MODULE, NULL, 0,
 "any character that is not a decimal digit"},
{RK_ESC, 's', "\\s", FEAT_CLASSES, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "classes", RS_MODULE, RD_MODULE, NULL, 0,
 "any whitespace character"},
{RK_ESC, 'S', "\\S", FEAT_CLASSES, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "classes", RS_MODULE, RD_MODULE, NULL, 0,
 "any character that is not whitespace"},
{RK_ESC, 'w', "\\w", FEAT_CLASSES, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "classes", RS_MODULE, RD_MODULE, NULL, 0,
 "any word character (letter, digit or underscore)"},
{RK_ESC, 'W', "\\W", FEAT_CLASSES, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "classes", RS_MODULE, RD_MODULE, NULL, 0,
 "any character that is not a word character"},
{RK_ESC, 'h', "\\h", FEAT_CLASSES, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "classes", RS_MODULE, RD_MODULE, NULL, 0,
 "any horizontal whitespace character"},
{RK_ESC, 'H', "\\H", FEAT_CLASSES, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "classes", RS_MODULE, RD_MODULE, NULL, 0,
 "any character that is not horizontal whitespace"},
/* THE ROW THIS WHOLE FILE EXISTS FOR. PCRE2's `\v` is vertical WHITESPACE —
 * 0x0a 0x0b 0x0c 0x0d 0x85 — not the vertical tab 0x0B. pcrec decoded it as
 * 0x0B until 2026-08-09; the corpus certified the bug because python `re`,
 * the base-tier oracle, reads `\v` as 0x0B too. It is also the only known
 * flavour-varying row, i.e. the single member of the set SR-7 is deferred for. */
{RK_ESC, 'v', "\\v", FEAT_CLASSES, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "classes", RS_MODULE, RD_MODULE, NULL, 0,
 "any vertical whitespace character (NOT vertical tab; python re disagrees)"},
{RK_ESC, 'V', "\\V", FEAT_CLASSES, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "classes", RS_MODULE, RD_MODULE, NULL, 0,
 "any character that is not vertical whitespace"},
{RK_ESC, 'N', "\\N", FEAT_CLASSES, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "classes", RS_MODULE, RD_MODULE, NULL, 0,
 "any character except newline (PCRE2 forbids it inside a class)"},

{RK_ESC, 'b', "\\b", FEAT_ASSERTIONS, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "assertions", RS_MODULE, RD_MODULE, NULL,
 RF_CLASS_BASE, "word boundary — but inside a class it is BASE syntax: backspace (0x08)"},
{RK_ESC, 'B', "\\B", FEAT_ASSERTIONS, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "assertions", RS_MODULE, RD_MODULE, NULL, 0,
 "not a word boundary"},
{RK_ESC, 'A', "\\A", FEAT_ASSERTIONS, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "assertions", RS_MODULE, RD_MODULE, NULL, 0,
 "start of subject"},
{RK_ESC, 'Z', "\\Z", FEAT_ASSERTIONS, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "assertions", RS_MODULE, RD_MODULE, NULL, 0,
 "end of subject, or before a final newline"},
{RK_ESC, 'z', "\\z", FEAT_ASSERTIONS, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "assertions", RS_MODULE, RD_MODULE, NULL, 0,
 "end of subject"},
{RK_ESC, 'G', "\\G", FEAT_ASSERTIONS, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "assertions", RS_MODULE, RD_MODULE, NULL, 0,
 "first matching position in the subject"},
{RK_ESC, 'K', "\\K", FEAT_ASSERTIONS, FLAV_PCRE2, ENGM_VM, "assertions", RS_MODULE, RD_MODULE, NULL, 0,
 "reset the reported start of the match"},

{RK_ESC, 'k', "\\k<name>", FEAT_BACKREFS, FLAV_PCRE2, ENGM_VM, "backrefs", RS_MODULE, RD_MODULE, NULL, 0,
 "backreference by name: \\k<n> \\k'n' \\k{n}"},
{RK_ESC, 'g', "\\g{-1}", FEAT_BACKREFS, FLAV_PCRE2, ENGM_VM, "backrefs", RS_MODULE, RD_MODULE, NULL, 0,
 "backreference by number or relative position: \\g1 \\g{-1} \\g{name}"},

{RK_ESC, 'p', "\\p{L}", FEAT_UNICODE_PROPS, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "unicode-props", RS_MODULE, RD_MODULE, NULL, 0,
 "a character with the given Unicode property"},
{RK_ESC, 'P', "\\P{L}", FEAT_UNICODE_PROPS, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "unicode-props", RS_MODULE, RD_MODULE, NULL, 0,
 "a character without the given Unicode property"},

{RK_ESC, 'Q', "\\Q", FEAT_QUOTING, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "quoting", RS_MODULE, RD_MODULE, NULL, 0,
 "begin literal quoting, until \\E"},
{RK_ESC, 'E', "\\E", FEAT_QUOTING, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "quoting", RS_MODULE, RD_MODULE, NULL, 0,
 "end literal quoting begun by \\Q"},

{RK_ESC, 'R', "\\R", FEAT_MISC, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "misc", RS_MODULE, RD_MODULE, NULL, 0,
 "any Unicode newline sequence"},
{RK_ESC, 'X', "\\X", FEAT_MISC, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "misc", RS_MODULE, RD_MODULE, NULL, 0,
 "a Unicode extended grapheme cluster"},
{RK_ESC, 'C', "\\C", FEAT_MISC, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "misc", RS_MODULE, RD_MODULE, NULL, 0,
 "one data unit (byte), even in UTF mode"},
{RK_ESC, 'c', "\\cX", FEAT_MISC, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "misc", RS_MODULE, RD_MODULE, NULL, 0,
 "control character: \\cX is X xor 0x40"},
{RK_ESC, 'o', "\\o{101}", FEAT_MISC, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "misc", RS_MODULE, RD_MODULE, NULL, 0,
 "character with the given octal code"},

/* Digits. `\0` is octal; `\1`..`\9` are a backreference, or an octal escape
 * when no such capture group exists — an ambiguity resolved against the group
 * count, which is why the backreference reading is VM-only. pcrec gives all
 * ten the same diagnostic today, and SR-2 must not change that. */
{RK_ESC, '0', "\\0", FEAT_BACKREFS, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "backrefs", RS_MODULE, RD_MODULE_OCTAL, NULL, 0,
 "octal escape \\0dd"},
{RK_ESC, '1', "\\1", FEAT_BACKREFS, FLAV_PCRE2, ENGM_VM, "backrefs", RS_MODULE, RD_MODULE_OCTAL, NULL, 0,
 "backreference to capture group 1 (octal escape if no such group)"},
{RK_ESC, '2', "\\2", FEAT_BACKREFS, FLAV_PCRE2, ENGM_VM, "backrefs", RS_MODULE, RD_MODULE_OCTAL, NULL, 0,
 "backreference to capture group 2 (octal escape if no such group)"},
{RK_ESC, '3', "\\3", FEAT_BACKREFS, FLAV_PCRE2, ENGM_VM, "backrefs", RS_MODULE, RD_MODULE_OCTAL, NULL, 0,
 "backreference to capture group 3 (octal escape if no such group)"},
{RK_ESC, '4', "\\4", FEAT_BACKREFS, FLAV_PCRE2, ENGM_VM, "backrefs", RS_MODULE, RD_MODULE_OCTAL, NULL, 0,
 "backreference to capture group 4 (octal escape if no such group)"},
{RK_ESC, '5', "\\5", FEAT_BACKREFS, FLAV_PCRE2, ENGM_VM, "backrefs", RS_MODULE, RD_MODULE_OCTAL, NULL, 0,
 "backreference to capture group 5 (octal escape if no such group)"},
{RK_ESC, '6', "\\6", FEAT_BACKREFS, FLAV_PCRE2, ENGM_VM, "backrefs", RS_MODULE, RD_MODULE_OCTAL, NULL, 0,
 "backreference to capture group 6 (octal escape if no such group)"},
{RK_ESC, '7', "\\7", FEAT_BACKREFS, FLAV_PCRE2, ENGM_VM, "backrefs", RS_MODULE, RD_MODULE_OCTAL, NULL, 0,
 "backreference to capture group 7 (octal escape if no such group)"},
{RK_ESC, '8', "\\8", FEAT_BACKREFS, FLAV_PCRE2, ENGM_VM, "backrefs", RS_MODULE, RD_MODULE_OCTAL, NULL, 0,
 "backreference to capture group 8 (octal escape if no such group)"},
{RK_ESC, '9', "\\9", FEAT_BACKREFS, FLAV_PCRE2, ENGM_VM, "backrefs", RS_MODULE, RD_MODULE_OCTAL, NULL, 0,
 "backreference to capture group 9 (octal escape if no such group)"},
};

/* ---- doorway 2: after '(?' ---------------------------------------------- */
static const RegRow group_rows[] = {
/* The one registry row the base tier reaches, and it must stay that way:
 * SR-5's fast-path guard is exactly "a base pattern performs no lookup other
 * than this one". */
{RK_GROUP, ':', "(?:...)", 0, FLAV_PCRE2, ENGM_DFA|ENGM_VM, NULL, RS_BASE, RD_NONE, NULL, 0,
 "non-capturing group"},

{RK_GROUP, '=', "(?=...)", FEAT_LOOKAROUND, FLAV_PCRE2, ENGM_VM, "lookaround", RS_MODULE, RD_MODULE, NULL, 0,
 "positive lookahead"},
{RK_GROUP, '!', "(?!...)", FEAT_LOOKAROUND, FLAV_PCRE2, ENGM_VM, "lookaround", RS_MODULE, RD_MODULE, NULL, 0,
 "negative lookahead"},
/* One byte, two constructs — which is why `feature` is a mask and the module
 * name is a compound string rather than a single owner. */
{RK_GROUP, '<', "(?<=...)", FEAT_LOOKAROUND|FEAT_NAMED_GROUPS, FLAV_PCRE2, ENGM_VM,
 "lookaround/named-groups", RS_MODULE, RD_MODULE, NULL, 0,
 "lookbehind (?<=...) (?<!...), or named capture group (?<name>...)"},
{RK_GROUP, '\'', "(?'name'...)", FEAT_NAMED_GROUPS, FLAV_PCRE2, ENGM_VM, "named-groups", RS_MODULE, RD_MODULE, NULL, 0,
 "named capture group, Perl-style quoting"},
{RK_GROUP, 'P', "(?P<name>...)", FEAT_NAMED_GROUPS, FLAV_PCRE2, ENGM_VM, "named-groups", RS_MODULE, RD_MODULE, NULL, 0,
 "python-style named group (?P<n>...), backreference (?P=n), recursion (?P>n)"},
{RK_GROUP, '>', "(?>...)", FEAT_ATOMIC_GROUPS, FLAV_PCRE2, ENGM_VM, "atomic-groups", RS_MODULE, RD_MODULE, NULL, 0,
 "atomic (non-backtracking) group"},
{RK_GROUP, '#', "(?#...)", FEAT_COMMENTS, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "comments", RS_MODULE, RD_MODULE, NULL, 0,
 "comment, discarded up to the next ')'"},
{RK_GROUP, 'C', "(?C1)", FEAT_CALLOUTS, FLAV_PCRE2, ENGM_VM, "callouts", RS_MODULE, RD_MODULE, NULL, 0,
 "callout to user code: (?C) (?C1) (?C{text})"},
{RK_GROUP, '|', "(?|...)", FEAT_BRANCH_RESET, FLAV_PCRE2, ENGM_VM, "branch-reset", RS_MODULE, RD_MODULE, NULL, 0,
 "branch reset group: alternatives reuse the same capture numbers"},
{RK_GROUP, '(', "(?(1)a|b)", FEAT_CONDITIONALS, FLAV_PCRE2, ENGM_VM, "conditionals", RS_MODULE, RD_MODULE, NULL, 0,
 "conditional group (?(condition)yes|no)"},
{RK_GROUP, '&', "(?&name)", FEAT_RECURSION, FLAV_PCRE2, ENGM_VM, "recursion", RS_MODULE, RD_MODULE, NULL, 0,
 "recurse into the named group"},
{RK_GROUP, 'R', "(?R)", FEAT_RECURSION, FLAV_PCRE2, ENGM_VM, "recursion", RS_MODULE, RD_MODULE, NULL, 0,
 "recurse the whole pattern"},
{RK_GROUP, '0', "(?0)", FEAT_RECURSION, FLAV_PCRE2, ENGM_VM, "recursion", RS_MODULE, RD_MODULE, NULL, 0,
 "recurse the whole pattern (synonym for (?R))"},
{RK_GROUP, '1', "(?1)", FEAT_RECURSION, FLAV_PCRE2, ENGM_VM, "recursion", RS_MODULE, RD_MODULE, NULL, 0,
 "recurse into capture group 1"},
{RK_GROUP, '2', "(?2)", FEAT_RECURSION, FLAV_PCRE2, ENGM_VM, "recursion", RS_MODULE, RD_MODULE, NULL, 0,
 "recurse into capture group 2"},
{RK_GROUP, '3', "(?3)", FEAT_RECURSION, FLAV_PCRE2, ENGM_VM, "recursion", RS_MODULE, RD_MODULE, NULL, 0,
 "recurse into capture group 3"},
{RK_GROUP, '4', "(?4)", FEAT_RECURSION, FLAV_PCRE2, ENGM_VM, "recursion", RS_MODULE, RD_MODULE, NULL, 0,
 "recurse into capture group 4"},
{RK_GROUP, '5', "(?5)", FEAT_RECURSION, FLAV_PCRE2, ENGM_VM, "recursion", RS_MODULE, RD_MODULE, NULL, 0,
 "recurse into capture group 5"},
{RK_GROUP, '6', "(?6)", FEAT_RECURSION, FLAV_PCRE2, ENGM_VM, "recursion", RS_MODULE, RD_MODULE, NULL, 0,
 "recurse into capture group 6"},
{RK_GROUP, '7', "(?7)", FEAT_RECURSION, FLAV_PCRE2, ENGM_VM, "recursion", RS_MODULE, RD_MODULE, NULL, 0,
 "recurse into capture group 7"},
{RK_GROUP, '8', "(?8)", FEAT_RECURSION, FLAV_PCRE2, ENGM_VM, "recursion", RS_MODULE, RD_MODULE, NULL, 0,
 "recurse into capture group 8"},
{RK_GROUP, '9', "(?9)", FEAT_RECURSION, FLAV_PCRE2, ENGM_VM, "recursion", RS_MODULE, RD_MODULE, NULL, 0,
 "recurse into capture group 9"},
/* Catch-all, and it must stay last: everything else after `(?` is an inline
 * option setting. Options DENOTE rather than MEAN (D24's second axis), and
 * OS-1/D23 already showed one folding entirely into the automaton, which is
 * why this row is DFA-lowerable while most of its neighbours are not. */
{RK_GROUP, REG_SEL_ANY, "(?i)", FEAT_MODIFIERS, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "modifiers", RS_MODULE, RD_MODULE, NULL, 0,
 "inline option setting or scoping: (?i) (?im-sx:...) (?^) (?-i)"},
};

/* ---- doorway 3: after '(*' ----------------------------------------------
 * A NAME decides here, but pcrec does not yet distinguish the names: one
 * catch-all row reproduces today's single blanket diagnostic exactly. Per-verb
 * rows arrive with the module (SR-6), not before — naming forty verbs that
 * nothing distinguishes and no test exercises would be fiction in a file whose
 * whole purpose is to stop syntax knowledge from being fiction. */
static const RegRow verb_rows[] = {
{RK_VERB, REG_SEL_ANY, "(*...)", FEAT_VERBS, FLAV_PCRE2, ENGM_VM, "verbs", RS_MODULE, RD_FIXED,
 "(*...) requires module 'verbs'", 0,
 "backtracking verb ((*SKIP), (*ACCEPT)), start-of-pattern option ((*CR), (*UTF)) or script run ((*script_run:...))"},
};

/* ---- doorway 4: after '[' inside a class -------------------------------- */
static const RegRow classbracket_rows[] = {
{RK_CLASSBRACKET, ':', "[[:alpha:]]", FEAT_CLASSES, FLAV_PCRE2, ENGM_DFA|ENGM_VM, "classes", RS_MODULE, RD_FIXED,
 "POSIX class [:...:] requires module 'classes'", 0,
 "POSIX character class"},
/* PCRE2 REJECTS these outright rather than treating them as literals, so
 * agreeing is compliance and there is no module to name — the reason RS_REJECTED
 * exists as a status distinct from RS_MODULE. pcrec accepted them silently
 * until 2026-08-09 (python `re` accepts them too, so the oracle was blind).
 * The trigger is narrower than it looks and was pinned against libpcre2 rather
 * than guessed: the delimiter opens a collating element ONLY when a matching
 * `.]` / `=]` appears later — see reject_collating() in parse.c, which owns the
 * lookahead. Over-rejecting here would break patterns PCRE2 accepts. */
{RK_CLASSBRACKET, '.', "[[.a.]]", 0, FLAV_PCRE2, 0, NULL, RS_REJECTED, RD_FIXED,
 "POSIX collating elements are not supported", 0,
 "POSIX collating element — PCRE2 rejects it, and so must we"},
{RK_CLASSBRACKET, '=', "[[=a=]]", 0, FLAV_PCRE2, 0, NULL, RS_REJECTED, RD_FIXED,
 "POSIX collating elements are not supported", 0,
 "POSIX equivalence class — PCRE2 rejects it, and so must we"},
};

/* ---- lookup -------------------------------------------------------------
 * A linear scan, deliberately, where SR-1's plan text said a [256] index per
 * kind. The index has no customer: SR-5's own claim is that a base-tier
 * pattern performs ZERO lookups here, so the scan runs only for constructs
 * that are about to produce a diagnostic and stop the compile. Building an
 * index for that would be the unmeasured axis D18 forbids, and it would need
 * either a hand-maintained parallel array (a second home for the selector
 * bytes — the exact failure this file exists to end) or an X-macro the rest of
 * the codebase does not use. Revisit if a doorway ever lands on a hot path. */

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
