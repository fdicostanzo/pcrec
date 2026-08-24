/* mod_verbs.c — the `(*` doorway.
 *
 * ==== [M6.6.2] WAVE F: THIS DOORWAY PRODUCES NOW, AND NOT FOR ITS OWN
 * ==== MODULE. Read this before the MOD-0.4 account below, which describes
 * ==== the file as it was and which two of its sentences no longer hold.
 *
 * A NAME MAY ANSWER FOR A DIFFERENT MODULE THAN THE DOORWAY. `verb_answer`
 * resolves a scanned name to THAT NAME'S OWN REGISTRY ROW when it has one
 * (`pcrec_registry_verb_name_row`, registry.c) and keeps the doorway's own
 * row when it does not — which is every verb except the twelve `(*` alpha
 * lookaround spellings. From that point on `r` is "the row this name answers
 * for", and the gate, the port call and both terminal refusals read it, so
 * nothing below the lookup is lookaround-specific and the SECOND module to
 * give a verb name a row of its own needs no edit here.
 *
 * WHAT THAT MAKES FALSE IN THE MOD-0.4 HEADER BELOW, said explicitly rather
 * than left for a reader to notice:
 *
 *   "no verb starts producing here, the parse.c doorway-3 wall stays"
 *       — a name whose row carries a `PORT_FN` reaches it at an open gate,
 *         and parse.c's doorway-3 branch gained the SPLICE the wall's own
 *         comment always said would replace it. The wall is still there for
 *         every other outcome.
 *   "If a future slice needs a producer, the seam to extend is
 *    `verb_rows[0]`'s `aport`"
 *       — the seam that was actually extended is the NAME's row's `aport`,
 *         which is the same seam one level finer: it lets ONE name produce
 *         without claiming that every name at this doorway does.
 *
 * Everything else in that account — the scan staying in scans.c, the shared
 * gate and refusal macros, the four table-drawn answers, the VF_* form
 * computation — is unchanged and still describes this file. ====
 *
 * MOD-0.4 WAS PURE MIGRATION, not the first slice of a producing module: no
 * verb starts producing here, the parse.c doorway-3 wall (ctx_fail after
 * pcrec_ext_finish) stays, and gate ON and gate OFF behaviour both stay
 * byte-identical to the pre-move build. What moves is EXISTING, MEASURED
 * code — `pcrec_ext_verb` itself (was src/parse/ext.c), the two VerbName
 * tables it reads and their four accessors (was src/parse/registry.c) —
 * with the whole measured-grammar comment block that establishes each part
 * (the probes-and-code-together rule mod_modifiers.c's own header states:
 * separating a construct's measurements from its code is what let the
 * `LIMIT_*` rule and its implementation drift, R8/C2-9).
 *
 * THE MILESTONE'S QUESTION was whether the doorway SIGNATURE — ExtWant /
 * ExtResult and the returned-claims epilogue (D33 §5) — survives contact
 * with the hardest case in the table: a construct decided by a NAME rather
 * than a byte, answering one of four different things from its own tables
 * rather than one fixed message. It does, and no new vocabulary was needed
 * to move it. Concretely, where each of the plan's four measured facts now
 * lives, unchanged:
 *
 *   the four table-drawn answers   `pcrec_ext_verb` below, via REFUSE
 *                                   (internal.h) — the SAME returned-claims
 *                                   epilogue every other doorway uses, still
 *                                   rendered once by ext.c's
 *                                   `pcrec_ext_finish`
 *   the VF_* form computation      `pcrec_ext_verb`'s `next`/form switch
 *                                   below, reading `v->forms` from the
 *                                   VerbName tables in THIS file
 *   VF_ATSTART's `at == 0` rule    the `(v->forms & VF_ATSTART) && at != 0`
 *                                   check below, unmoved in logic
 *   the star = at + 1 blame        `size_t star = at + 1;` below, still the
 *                                   offset REFUSE's empty-name branch reports
 *                                   at — not `at`, the doorway's own default
 *
 * WIRING: a direct call, not a port. `pcrec_ext_verb` keeps its exact
 * signature (`ExtResult pcrec_ext_verb(Ctx *cx, ExtWant want, size_t at)`),
 * still declared in internal.h; parse.c's call site
 * (`pcrec_ext_verb(cx, WANT_RESULT, apos)`) is byte-identical — only the TU
 * defining the function moved. This is deliberately UNLIKE mod_modifiers.c's
 * `(?` doorway, which dispatches across a FAMILY of GROUP_OPT rows via
 * `pcrec_registry_arbitrate` and a row's `recognise` field — the shape the
 * recognise-pointer/aport pattern exists to serve. Doorway 3 has exactly ONE
 * RegRow (`verb_rows[0]` in registry.c) and dispatches by NAME through the
 * VerbName tables below, not by row; there is no row family for a recognise
 * pointer to mark. Building an aport/PORT_FN here would wire a PRODUCER when
 * nothing produces yet — the opposite of the NULL-port discipline (internal.h
 * §14.3) — and it would also invent the exact synthetic-buffer UB class
 * mod_modifiers.c's `recognise` field sidesteps: that risk is specific to
 * reconstructing a position from a row's `tail`-relative `at` inside a
 * `recognise` callback under registry_check's synthetic arbitration-sweep
 * buffers, and it does not arise here, because verb dispatch is by scanned
 * NAME TEXT (`pcrec_verb_name_extent_scan`, scans.c), never by a row's tail.
 * If a future slice needs a producer, the seam to extend is `verb_rows[0]`'s
 * `aport`, exactly as MOD-0.5c added `pcrec_modport_optrun` to the GROUP_OPT
 * rows — not this file's dispatch shape.
 *
 * SHARED MACHINERY, not duplicated. `pcrec_ext_verb` still needs
 * `pcrec_ext_gate` (the RESULT->VERDICT demotion for a disabled module) and
 * the `REFUSE`/`BAD_ROW` refusal-epilogue macros every doorway uses. Both
 * were `static`/file-local to ext.c before this move; MOD-0.4 promoted them
 * to internal.h (gate: non-static, declared there, still DEFINED in ext.c)
 * rather than giving this file a second copy that could drift from ext.c's —
 * see internal.h's comment at the promotion site and ext.c's own comment
 * where each used to live whole.
 *
 * WHAT DID NOT MOVE, and why. `pcrec_verb_name_extent_scan` stays in
 * scans.c, unchanged: it is pure over (pat, patlen), needed to determine the
 * name and its terminator REGARDLESS of gate state (even a gate-closed
 * verdict must pick the right one of the four answers), and scans.c's own
 * contract — "this TU must NEVER link the enabled-set symbols... what a
 * construct IS cannot depend on what is switched on" (src/parse/CLAUDE.md)
 * — is exactly why lexer machinery like this does not belong inside a
 * module TU, even one it exclusively serves today. The RK_VERB row itself
 * (`verb_rows[0]`) stays in registry.c too, alongside every other row —
 * parallel to how mod_modifiers.c's twelve GROUP_OPT rows stayed in
 * registry.c while only their grammar function and (later) their producing
 * port moved out. `pcrec_ext_verb` still fetches that row with
 * `pcrec_registry_find(RK_VERB, REG_SEL_ANY, NULL, 0)` for its `msg`,
 * `roadmap` fallback and `diag` check, exactly as before. */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"

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
{"ACCEPT", VF_BARE | VF_ARG | VF_EMPTYARG, 0, NULL, ROADMAP_NONE, QV_YES},
{"FAIL",   VF_BARE | VF_ARG | VF_EMPTYARG, 0, NULL, ROADMAP_NONE, QV_NO},
{"F",      VF_BARE | VF_ARG | VF_EMPTYARG, 0, NULL, ROADMAP_NONE, QV_NO},
{"COMMIT", VF_BARE | VF_ARG | VF_EMPTYARG, 0, NULL, ROADMAP_NEVER, QV_NO},
{"PRUNE",  VF_BARE | VF_ARG | VF_EMPTYARG, 0, NULL, ROADMAP_NEVER, QV_NO},
{"SKIP",   VF_BARE | VF_ARG | VF_EMPTYARG, 0, NULL, ROADMAP_NEVER, QV_NO},
{"THEN",   VF_BARE | VF_ARG | VF_EMPTYARG, 0, NULL, ROADMAP_NEVER, QV_NO},

/* The one irregular name in either table, and the reason `own_forms`/`own_msg`
 * exist. `(*MARK)` and `(*MARK:)` are error 166 with a message of their own;
 * `(*MARK=1)` and a truncated `(*MARK` are the ordinary 160. The empty name in
 * `(*:x)` is a MARK synonym and reaches this row — see pcrec_ext_verb. */
{"MARK",   VF_ARG, VF_BARE | VF_EMPTYARG, "(*MARK) must have an argument", ROADMAP_NEVER, QV_NOT_ASKABLE},

/* Start-of-pattern options. Bare form only, and only at offset 0:
 * `a(*CR)` is error 160. */
{"UTF",               VF_BARE | VF_ATSTART, 0, NULL, ROADMAP_NONE, QV_NOT_ASKABLE},
{"UTF8",              VF_BARE | VF_ATSTART, 0, NULL, ROADMAP_NONE, QV_NOT_ASKABLE},
{"UCP",               VF_BARE | VF_ATSTART, 0, NULL, ROADMAP_NONE, QV_NOT_ASKABLE},
{"NOTEMPTY",          VF_BARE | VF_ATSTART, 0, NULL, ROADMAP_NONE, QV_NOT_ASKABLE},
{"NOTEMPTY_ATSTART",  VF_BARE | VF_ATSTART, 0, NULL, ROADMAP_NONE, QV_NOT_ASKABLE},
{"NO_AUTO_POSSESS",   VF_BARE | VF_ATSTART, 0, NULL, ROADMAP_NEVER, QV_NOT_ASKABLE},
{"NO_DOTSTAR_ANCHOR", VF_BARE | VF_ATSTART, 0, NULL, ROADMAP_NEVER, QV_NOT_ASKABLE},
{"NO_JIT",            VF_BARE | VF_ATSTART, 0, NULL, ROADMAP_NEVER, QV_NOT_ASKABLE},
{"NO_START_OPT",      VF_BARE | VF_ATSTART, 0, NULL, ROADMAP_NEVER, QV_NOT_ASKABLE},
{"CASELESS_RESTRICT", VF_BARE | VF_ATSTART, 0, NULL, ROADMAP_NEVER, QV_NOT_ASKABLE},
/* Recognised, and this build cannot honour it: `(*TURKISH_CASING)` is error
 * 204, "require Unicode (UTF or UCP) mode" — a capability refusal, not a
 * syntax one, and our oracle compiles with options = 0 so it can never be in
 * that mode. pcre2_check.c buckets 204 with "PCRE2 recognised the construct",
 * which is why this row needs no exclusion. */
{"TURKISH_CASING",    VF_BARE | VF_ATSTART, 0, NULL, ROADMAP_NEVER, QV_NOT_ASKABLE},
{"CR",                VF_BARE | VF_ATSTART, 0, NULL, ROADMAP_NONE, QV_NOT_ASKABLE},
{"LF",                VF_BARE | VF_ATSTART, 0, NULL, ROADMAP_NONE, QV_NOT_ASKABLE},
{"CRLF",              VF_BARE | VF_ATSTART, 0, NULL, ROADMAP_NONE, QV_NOT_ASKABLE},
{"ANYCRLF",           VF_BARE | VF_ATSTART, 0, NULL, ROADMAP_NONE, QV_NOT_ASKABLE},
{"ANY",               VF_BARE | VF_ATSTART, 0, NULL, ROADMAP_NONE, QV_NOT_ASKABLE},
{"NUL",               VF_BARE | VF_ATSTART, 0, NULL, ROADMAP_NONE, QV_NOT_ASKABLE},
{"BSR_ANYCRLF",       VF_BARE | VF_ATSTART, 0, NULL, ROADMAP_NONE, QV_NOT_ASKABLE},
{"BSR_UNICODE",       VF_BARE | VF_ATSTART, 0, NULL, ROADMAP_NONE, QV_NOT_ASKABLE},

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
 * `pcrec_ext_verb` below implements the paragraph above. */
{"LIMIT_MATCH",     VF_EQNUM | VF_ATSTART, 0, NULL, ROADMAP_NEVER, QV_NOT_ASKABLE},
{"LIMIT_DEPTH",     VF_EQNUM | VF_ATSTART, 0, NULL, ROADMAP_NEVER, QV_NOT_ASKABLE},
{"LIMIT_HEAP",      VF_EQNUM | VF_ATSTART, 0, NULL, ROADMAP_NEVER, QV_NOT_ASKABLE},
{"LIMIT_RECURSION", VF_EQNUM | VF_ATSTART, 0, NULL, ROADMAP_NEVER, QV_NOT_ASKABLE},
};

/* The lower table. Every name here takes a SUBPATTERN argument — these are
 * group constructs spelled as verbs — so the bare form is an error and the
 * argument may be empty. Position-free, unlike the options above.
 * `(*scs:x)` is error 115 (a subpattern reference that does not resolve),
 * which is PCRE2 recognising the name and rejecting the reference. */
static const VerbName verb_lower[] = {
{"pla",                            VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL, ROADMAP_NONE, QV_YES},
{"plb",                            VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL, ROADMAP_NONE, QV_YES},
{"napla",                          VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL, ROADMAP_NONE, QV_YES},
{"naplb",                          VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL, ROADMAP_NONE, QV_YES},
{"nla",                            VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL, ROADMAP_NONE, QV_YES},
{"nlb",                            VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL, ROADMAP_NONE, QV_YES},
{"positive_lookahead",             VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL, ROADMAP_NONE, QV_YES},
{"positive_lookbehind",            VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL, ROADMAP_NONE, QV_YES},
{"non_atomic_positive_lookahead",  VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL, ROADMAP_NONE, QV_YES},
{"non_atomic_positive_lookbehind", VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL, ROADMAP_NONE, QV_YES},
{"negative_lookahead",             VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL, ROADMAP_NONE, QV_YES},
{"negative_lookbehind",            VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL, ROADMAP_NONE, QV_YES},
{"atomic",                         VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL, ROADMAP_NONE, QV_YES},
{"sr",                             VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL, ROADMAP_NONE, QV_YES},
{"asr",                            VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL, ROADMAP_NONE, QV_YES},
{"script_run",                     VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL, ROADMAP_NONE, QV_YES},
{"atomic_script_run",              VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL, ROADMAP_NONE, QV_YES},
{"scs",                            VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL, ROADMAP_NEVER, QV_NOT_ASKABLE},
{"scan_substring",                 VF_ARG | VF_EMPTYARG | VF_GROUPARG, 0, NULL, ROADMAP_NEVER, QV_NOT_ASKABLE},
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
    *max = PCREC_VERB_NAME_MAX;
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

/* ---- doorway 3: after '(*' ----------------------------------------------
 * A NAME decides here, and since Q1 pcrec reads it. Until Q1 this function
 * ignored the name entirely and answered "requires module 'verbs'" for all of
 * them, which was wrong in three separate ways at once:
 *
 *   `(*NOTAVERB)`  was promised a module that will never implement it, because
 *                  PCRE2 has no such verb (error 160)
 *   `(*)`          was called a verb, when PCRE2 reads `(` then a `*` that
 *                  quantifies nothing (error 109)
 *   `a(*CR)`       was called a verb, when a start-of-pattern option anywhere
 *                  but the start is error 160
 *
 * and, worse than any single wrong answer, it made pcrec's answer INDEPENDENT
 * of the name — so no differential against libpcre2 over names could say
 * anything. That is what Q1 unlocks and PC-3 spends: see D25 and
 * tests/registry/pcre2_check.c.
 *
 * WHAT THIS FUNCTION DECIDES, and it is only ever one of four things: the
 * quantifier error, the table's "no such name" message, a name's own message
 * (`MARK` alone has one), or the row's "requires module 'verbs'". It does NOT
 * parse the argument — an accepted form still ends the compile here.
 *
 * The forms are read from the VerbName table above, every bit of which is
 * measured against libpcre2 rather than read from documentation.
 *
 * MOD-0.4: moved here verbatim from src/parse/ext.c — see this file's own
 * header for the wiring decision (a direct call, no port) and for where
 * each of the milestone's four measured facts now lives. */
static ExtResult verb_answer(Ctx *cx, ExtWant want, size_t at,
                             const RegRow **elected)
{
    const RegRow *r = pcrec_registry_find(RK_VERB, REG_SEL_ANY, NULL, 0);
    *elected = r;   /* MOD-0.7 slice 2 — doorway 3's own row */
    /* [M6.6.2 wave F] THE ASK LEVEL BEFORE ANY GATE, kept because this
     * doorway now gates TWICE: once on its own row (below, for every refusal
     * decided before the name is known) and once more on the NAME's row, when
     * the name turns out to answer for a different module. Re-gating from the
     * ORIGINAL ask rather than from the demoted one is what makes the second
     * gate a fresh question instead of a second demotion. */
    const ExtWant asked = want;
    want = pcrec_ext_gate(r, want);
    const char *pat = cx->pat;
    size_t n = cx->patlen;
    size_t star = at + 1;           /* the '*'; `at` is the '(' */
    size_t nstart = star + 1;
    size_t i = nstart;

    if (!r) REFUSE(at, "internal error: no registry row for (*");
    if (r->diag != RD_FIXED)
        BAD_ROW(at, "a (* verb");

    /* The name's extent (the terminator set and the trailing-space rule are
     * documented at the scan, scans.c — always-live, never gated). */
    i = pcrec_verb_name_extent_scan(pat, n, nstart);
    size_t nlen = i - nstart;
    int next = i < n ? (unsigned char)pat[i] : -1;

    /* An EMPTY name has three different answers, and the first version of this
     * code got one of them wrong until the PC-3 differential said so on its
     * first run — over a thousand probes, all of this shape.
     *
     *   `(*)`, `(*`     not this doorway at all: `(` followed by a quantifier
     *                   with nothing to quantify (PCRE2 error 109, and what
     *                   parse.c's own `case '*'` says for a bare `*`). Reported
     *                   at the `*`, matching both.
     *   `(*:NAME)`      a synonym for `(*MARK:NAME)`. It resolves to the MARK
     *                   row and inherits its rules, which is why `(*:)` reports
     *                   "(*MARK) must have an argument" and not a "no such name".
     *   `(*=1)`         an ordinary unrecognised name that happens to be empty:
     *                   PCRE2 error 160. Falling through with a zero-length name
     *                   gets that for free — no table contains "" — which is why
     *                   there is no third branch here. */
    const char *name;
    size_t      namelen;
    if (nlen)              { name = pat + nstart; namelen = nlen; }
    else if (next == ':')  { name = "MARK";       namelen = 4;    }
    else if (next == '=')  { name = "";           namelen = 0;    }
    else REFUSE(star, "quantifier does not follow a repeatable item");

    /* A name too long to be a name at all is a LENGTH complaint in PCRE2, not a
     * "no such name" one, and it is the same complaint in both tables. Measured
     * on libpcre2 10.46 (R8/C2-4): 128 bytes is error 160/195 as usual, 129 is
     * error 148, in every form and in both tables. The limit is on the NAME —
     * `(*MARK:` followed by 200 bytes of argument compiles fine. */
    size_t maxname;
    const char *toolong = pcrec_registry_verb_name_limit(&maxname);
    if (namelen > maxname) REFUSE(at, "%s", toolong);

    const VerbTable *t =
        pcrec_registry_verb_table(namelen ? (unsigned char)name[0] : -1);
    const VerbName  *v = pcrec_registry_verb_find(t, name, namelen);
    if (!v) REFUSE(at, "%s", t->unknown_msg);

    /* Which FORM was written. A form of 0 means "none of them", which is what a
     * truncated construct produces — and PCRE2 agrees: `(*CR` and `(*ACCEPT:x`
     * are both error 160, the same as an unknown name. */
    unsigned form = 0;
    if (next == ')') {
        form = VF_BARE;
    } else if (next == ':') {
        if (v->forms & VF_GROUPARG) {
            /* A subpattern argument. The doorway does not require the closing
             * `)` to be present — PCRE2 recognises `(*pla:x` and then reports a
             * missing parenthesis (error 114), a different complaint entirely. */
            form = (i + 1 < n && pat[i + 1] == ')') ? VF_EMPTYARG : VF_ARG;
        } else {
            /* A name-run argument, terminated by `)`, which must exist: without
             * it PCRE2 does not recognise the construct at all. `:` is an
             * ordinary character inside it (`(*MARK:a:b)` compiles). */
            size_t j = i + 1;
            while (j < n && pat[j] != ')') j++;
            if (j < n) form = (j == i + 1) ? VF_EMPTYARG : VF_ARG;
        }
    } else if (next == '=') {
        /* Digits only, at least one, then `)`. `(*LIMIT_MATCH= 1)` and
         * `(*LIMIT_MATCH=x)` are both error 160; `=01` is accepted.
         *
         * AND A MAGNITUDE RULE, which the first version of this code did not
         * have because the probes that measured it were one and two digits long
         * (R8/C2-3 — the sweep agreed because the axis it varied was the NAME).
         * PCRE2 refuses while ACCUMULATING, one digit before its 32-bit
         * accumulator would overflow, so the boundary is 4294967290 and not
         * 4294967296: `(*LIMIT_MATCH=4294967289)` compiles and
         * `(*LIMIT_MATCH=4294967290)` is error 160. LENGTH is not the rule —
         * `=00000000000000000001` compiles, because leading zeros never move
         * the accumulator. Reproduced here exactly, including that. */
        size_t j = i + 1;
        unsigned long long acc = 0;
        bool fits = true;
        while (j < n && pat[j] >= '0' && pat[j] <= '9') {
            if (acc > PCREC_VERB_LIMIT_ACC_MAX) fits = false;
            /* `acc` keeps accumulating past that point and WRAPS on a long
             * enough digit run. That is defined behaviour for an unsigned type
             * and the wrapped value is never read, because `fits` is sticky —
             * it is only ever cleared. Said out loud rather than left for a
             * reader to re-derive, or for someone to "fix" by resetting it. */
            acc = acc * 10 + (unsigned)(pat[j] - '0');
            j++;
        }
        if (fits && j > i + 1 && j < n && pat[j] == ')') form = VF_EQNUM;
    }

    if (!(v->forms & form))
        REFUSE(at, "%s",
               (v->own_forms & form) ? v->own_msg : t->unknown_msg);

    /* Start-of-pattern options are valid only at the start. PCRE2 allows a RUN
     * of them — `(*UTF)(*CR)` compiles — and pcrec's rule is `at == 0` exactly.
     *
     * That is equivalent TO THE GENERAL PREFIX-RUN RULE, as an implementation
     * choice inside pcrec, and to nothing else: any earlier verb would already
     * have ended this compile with "requires module 'verbs'", so a run can
     * never reach here with a non-zero offset, and the two rules cannot differ
     * on any pattern. Writing the general scan now would be code whose only
     * interesting branch nothing can execute. When module 'verbs' lands and
     * these constructs start being ACCEPTED, that stops being true and the scan
     * is what replaces this line.
     *
     * IT DOES NOT MEAN pcrec's message matches PCRE2's on every pattern with an
     * option in it (R8/C2). `(*UTF)a(*UTF)` is PCRE2 error 160 — about the
     * SECOND one — while pcrec answers about the first, because pcrec reports
     * the leftmost construct it cannot handle and stops. That is pcrec's rule
     * at every doorway (`\d{3,1}` is "requires module 'classes'" here and
     * "numbers out of order" in PCRE2), and the general prefix scan would not
     * change it. */
    if ((v->forms & VF_ATSTART) && at != 0)
        REFUSE(at, "%s", t->unknown_msg);

    /* K14 (design §17.2): disposition is a PER-NAME fact — `(*COMMIT)` is
     * OUT-OF-SCOPE while `(*pla:...)` is a lookaround in verb spelling — with
     * the row's value as the default. It fires only for a form PCRE2 would
     * ACCEPT: a malformed form of a NEVER name keeps PCRE2's own form error
     * above, because the roadmap is an answer about the construct, not about
     * a typo. The `(*:x)` MARK synonym resolves to MARK's entry and inherits
     * its NEVER, which is why the message below prints the resolved name. */
    if ((v->roadmap ? v->roadmap : r->roadmap) == ROADMAP_NEVER)
        REFUSE(at, "(*%.*s) is outside pcrec's scope and no module will implement it (see docs/pcre2_compliance.md)",
               (int)namelen, name);

    /* ---- [M6.6.2] WAVE F: A NAME MAY ANSWER FOR A DIFFERENT MODULE --------
     *
     * THE DEFECT THIS CLOSES (design §8.2, MEASURED at P3). All twelve alpha
     * lookaround spellings answered *"(*...) requires module 'verbs'"* — the
     * WRONG MODULE, which is the one fact the diagnostic exists to carry —
     * because the `(*` doorway is a single row (registry.c's `verb_rows`
     * catch-all) whose module answered for every name in both tables. It is
     * the same shape `registry.c:692` already records one doorway over, for
     * `(?*...)`: a catch-all naming its own module for a construct that
     * belongs to another.
     *
     * THE FIX IS A ROW LOOKUP BY NAME, not a special case. `verb_rows` gained
     * twelve RF_INDEX rows whose `tail` is the alpha name (D71 item 3), and
     * from here on `r` is THE ROW THIS NAME ANSWERS FOR — its own row when it
     * has one, the doorway's when it does not, which is every other verb and
     * is what "everything else inherits" means. Nothing below this line is
     * lookaround-specific: the gate, the port call and the two refusals all
     * read `r`, so the SECOND module to give a verb name a row of its own
     * needs no edit here.
     *
     * IT IS PLACED AFTER THE FORM AND POSITION CHECKS ON PURPOSE (R33 C2-6).
     * `(*pla)` is a REAL name in a form PCRE2 does not accept, and PCRE2
     * decides that before it decides anything about modules, so its
     * "(*alpha_assertion) not recognized" survives this wave: the form
     * mismatch above has already returned.
     *
     * WHAT THE ORDERING PROTECTS IS THE ANSWER LEVEL, NOT THE MESSAGE, and
     * that is MEASURED on a control build with this block moved above the
     * form check rather than argued. The message does not move at all — it
     * comes from the VerbName TABLE's `unknown_msg`, not from `r` — so the
     * reject table's message-only row for `(*pla)` is structurally blind to
     * the difference, and a first draft of this comment claimed the opposite.
     * What DOES move is `answered_at`: `--features lookaround --probe-ask
     * result -- '(*pla)'` reads `verdict` here and `result` on the control.
     * `result` is D33's "the gate was OPEN and the port had nothing to say"
     * signal, so the control has a FORM ERROR reporting itself as an answer
     * given with module `lookaround`'s gate open — this wave's own
     * misattribution, one level down. tests/cli/'s case10 pins all four cells
     * (both gate states x `(*pla)` and `(*pla:a)`), because `--probe-ask` is
     * the channel that can see it. */
    const RegRow *nrow = pcrec_registry_verb_name_row(name, namelen);
    if (nrow) {
        r = nrow;
        *elected = r;
        want = pcrec_ext_gate(r, asked);
    }

    /* THE PRODUCER, in the shape doorways 1 and 2 already use: position
     * selects the port, an open gate selects the level, and PORT_NONE falls
     * through to the refusals below unchanged. `from` is the body's FIRST
     * BYTE — one past the `:` this form's own terminator scan stopped on —
     * so `pcrec_laport_group` parses `(*pla:X)`'s `X` from exactly where it
     * parses `(?=X)`'s. The doorway never moves `cx->pos`; the result
     * carries `end` and the CALLER advances (check06's rule). */
    if (want == WANT_RESULT && r->aport.kind == PORT_FN)
        return r->aport.fn(cx, r, want, at, i + 1);

    /* THE TERMINAL REFUSAL, now two shapes rather than one. The doorway's own
     * row is RD_FIXED and keeps its exact sentence, byte for byte — every
     * verb in the tree still reads "(*...) requires module 'verbs'". A NAME's
     * own row is RD_MODULE and renders the template from the row, which is
     * what puts the RIGHT module in the diagnostic and is the whole point of
     * the lookup above. */
    if (r->diag == RD_FIXED)
        REFUSE(at, "%s", r->msg);
    REFUSE(at, "(*%.*s:...) requires module '%s'", (int)namelen, name,
           r->module);
}

/* The elected-row wrapper (MOD-0.7 slice 2; ext.c's wrappers carry the full
 * rationale). Doorway 3 has exactly one RegRow, so `res.row` is always that
 * row when the doorway answers at all — the INTERESTING half here is that the
 * MESSAGE frequently is not the row's: an unknown name, a MARK without its
 * argument and a NEVER name all come from the VerbName tables, which is the
 * one genuinely independent cross-source pair in the design (§4.3). */
ExtResult pcrec_ext_verb(Ctx *cx, ExtWant want, size_t at)
{
    const RegRow *elected = NULL;
    ExtResult res = verb_answer(cx, want, at, &elected);
    res.row = elected;
    return res;
}
