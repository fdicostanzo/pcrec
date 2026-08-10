/* tests/registry/pcre2_check.c — the registry against libpcre2 (step PC-3).
 *
 * WHY THIS EXISTS, and it is not "one more registry test". Everything else
 * that checks the registry reads pcrec's own files. registry_check.c compares
 * the table with the parser; tests/reject/ compares hand-written expectations
 * with the compiler; compliance_section.py compares a document with a dump.
 * All three are pcrec checking pcrec, and R4/R5/R6 each measured the same
 * consequence: a row that is plausibly WRONG in the single home is invisible
 * to every one of them, because the wrongness is what both sides read.
 *
 * This file is the first outside authority in the project. Two claims per row
 * are externally checkable, and nothing checked them before:
 *
 *   RS_REJECTED  the row says "PCRE2 rejects this too, so agreement is
 *                compliance". libpcre2 must REJECT the probe, and with a
 *                MATCHING ERROR IDENTITY — pcrec's message must be PCRE2's
 *                message, not merely some rejection for some other reason.
 *
 *   RS_MODULE    the row says "PCRE2 HAS this construct and pcrec has not
 *                implemented it". libpcre2 must COMPILE the probe. A row that
 *                names a construct PCRE2 does not have fails here, which is
 *                the fabrication check.
 *
 * MIND THE POLARITY. It was recorded backwards in docs/plan.md until R6 caught
 * it, and as written there it would have passed every fabricated row it exists
 * to catch. RS_MODULE must COMPILE. It caught one on the first run: the verb
 * row's probe was `(*...)`, which is not a PCRE2 construct at all.
 *
 * PART 3 IS THE ONE THAT SCALES. Every finding in R4, R5 and R6 ran into the
 * same wall — a check that iterates what EXISTS cannot see what is MISSING —
 * and the only answer the project had was a hand-written manifest covering
 * eight rows. For a NAME-keyed doorway that wall comes down: generate names
 * from a source outside pcrec, ask libpcre2 what each one is, and require
 * pcrec to give the corresponding answer. Delete a verb row, misspell it, or
 * invent one PCRE2 does not have, and this finds it without anyone having
 * written that name down. It depends entirely on Q1 (D25): while one catch-all
 * answered "requires module 'verbs'" for every name, pcrec's answer did not
 * depend on the name and the comparison was vacuous.
 *
 * THE CANDIDATE NAMES COME FROM LIBPCRE2'S OWN BINARY. Not from this file's
 * author's memory of pcre2syntax, and emphatically not from pcrec's table. Four
 * sources, and the file tracks which one produced each name: (1) the shared
 * object dlopen resolved, its ASCII runs expanded to every prefix and suffix;
 * (2) single-character mutations of the names pcrec claims; (3) all 255 single
 * bytes; (4) runs of one letter at the lengths libpcre2's behaviour changes at.
 * The pool is a heuristic; the VERDICT on every candidate is libpcre2 compiling
 * it, which is not — and EVERY name pcrec claims must be produced by source (1)
 * independently, or this fails. Without that last rule the pool can quietly
 * become pcrec's own table, which is the circularity the file exists to break.
 *
 * ALL COMPILES USE options = 0 — no PCRE2_UTF, no PCRE2_UCP, no
 * PCRE2_CASELESS. Every claim this file makes is about default 8-bit mode.
 * It measures NO UTF conformance, and `-i` against PCRE2_CASELESS is not
 * covered here either.
 *
 * SKIPPING IS LOUD AND IS NOT A PASS. Without libpcre2-8-0 installed this
 * prints a SKIP banner and exits 0, because a stranger who clones the repo
 * must still get a green `make test`. It prints the library version and path
 * whenever it does run, so a result can be attributed to a build.
 *
 * Build/run: bash tests/registry/run_registry_tests.sh */

/* FIRST: pcre2_abi.h defines _GNU_SOURCE, needed before any libc header. */
#include "../fuzz/pcre2_abi.h"

#include <stdarg.h>
#include <stdlib.h>

#include "core/internal.h"
#include "pcrec.h"

static Pcre2Abi pcre2;
static int pass = 0, fail = 0;

static void ok(const char *what)  { printf("PASS: %s\n", what); pass++; }
static void bad(const char *fmt, ...) __attribute__((format(printf, 1, 2)));
static void bad(const char *fmt, ...)
{
    va_list ap;
    fflush(stdout);   /* see registry_check.c: unbuffered stderr splices into
                         buffered stdout and breaks line-anchored greps */
    fputs("FAIL: ", stderr);
    va_start(ap, fmt);
    vfprintf(stderr, fmt, ap);
    va_end(ap);
    fputc('\n', stderr);
    fail++;
}

/* ---- the two compilers ------------------------------------------------- */

/* libpcre2: 0 if it compiles, else the PCRE2 error code, with its message. */
static int pcre2_try(const char *pat, size_t len, char *msg, size_t msgsz)
{
    int ec; PCRE2_SIZE eo;
    pcre2_code_8 *re = pcre2.compile((PCRE2_SPTR)pat, len, 0, &ec, &eo, NULL);
    if (re) { pcre2.code_free(re); if (msg) snprintf(msg, msgsz, "ok"); return 0; }
    if (msg) {
        unsigned char b[256];
        pcre2.get_error_message(ec, b, sizeof b);
        snprintf(msg, msgsz, "%s", (char *)b);
    }
    return ec;
}

/* pcrec: 0 if it compiles, -1 with the diagnostic in `msg` (exactly
 * pcrec_error.msg — no CLI decoration). */
static int pcrec_try(const char *pat, char *msg, size_t msgsz)
{
    pcrec_options opt; pcrec_output out; pcrec_error err; int rc;
    pcrec_default_options(&opt);
    memset(&out, 0, sizeof out);
    memset(&err, 0, sizeof err);
    rc = pcrec_compile(pat, &opt, &out, &err);
    if (rc == 0) { pcrec_output_free(&out); return 0; }
    snprintf(msg, msgsz, "%s", err.msg);
    return -1;
}

/* ---- part 1 & 2: every registry row, against libpcre2 ------------------ *
 *
 * A row's `syntax` is a probe that reaches pcrec's DOORWAY. That is a weaker
 * contract than "a pattern libpcre2 will compile", and 22 rows need a context
 * PCRE2 insists on: `\1` is a backreference to a group that has to exist,
 * `(?1)` recurses into one, `\k<name>` needs the name declared. The wrappers
 * live HERE rather than in registry.c on purpose — they are facts about what
 * libpcre2 demands, not about pcrec's taxonomy, and registry.c is the home of
 * the second thing only.
 *
 * TWO RULES KEEP THIS FROM GOING VACUOUS.
 *   1. A wrapper MUST CONTAIN the row's `syntax` verbatim. Without that, a
 *      fabricated row could be rescued by wrapping it in something unrelated
 *      that happens to compile, and this check would applaud.
 *   2. A row whose `syntax` does not compile and has NO wrapper is a FAILURE,
 *      never a skip. A new row either compiles as written or forces someone to
 *      write down, deliberately, what context PCRE2 needs. */
/* `tail` matches the ROW's tail (SR-9), NULL meaning "the row with no tail".
 * Without it a wrapper keyed on `(RK_GROUP, 'P')` would answer for all four `P`
 * rows, and the three that need no wrapper would silently get one — which the
 * "a wrapper that is not NECESSARY is an error" check would then report against
 * the wrong row. */
typedef struct { RegKind kind; int sel; const char *tail; const char *probe; const char *why; } Wrapper;

static const Wrapper WRAPPERS[] = {
{RK_ESC, 'k', NULL, "(?<name>a)\\k<name>", "a backreference by name needs the name declared"},
{RK_ESC, 'g', NULL, "(a)\\g{-1}",          "a relative backreference needs a group to its left"},
{RK_ESC, '1', NULL, "(a)\\1",                       "PCRE2 error 115 without the group"},
{RK_ESC, '2', NULL, "(a)(a)\\2",                    "PCRE2 error 115 without the groups"},
{RK_ESC, '3', NULL, "(a)(a)(a)\\3",                 "PCRE2 error 115 without the groups"},
{RK_ESC, '4', NULL, "(a)(a)(a)(a)\\4",              "PCRE2 error 115 without the groups"},
{RK_ESC, '5', NULL, "(a)(a)(a)(a)(a)\\5",           "PCRE2 error 115 without the groups"},
{RK_ESC, '6', NULL, "(a)(a)(a)(a)(a)(a)\\6",        "PCRE2 error 115 without the groups"},
{RK_ESC, '7', NULL, "(a)(a)(a)(a)(a)(a)(a)\\7",     "PCRE2 error 115 without the groups"},
{RK_ESC, '8', NULL, "(a)(a)(a)(a)(a)(a)(a)(a)\\8",  "PCRE2 error 115 without the groups"},
{RK_ESC, '9', NULL, "(a)(a)(a)(a)(a)(a)(a)(a)(a)\\9","PCRE2 error 115 without the groups"},
{RK_GROUP, '(', NULL, "(a)(?(1)a|b)",        "a conditional on group 1 needs group 1"},
{RK_GROUP, '&', NULL, "(?<name>a)(?&name)",  "recursion by name needs the name declared"},
{RK_GROUP, '1', NULL, "(a)(?1)",                       "recursion into a group needs the group"},
{RK_GROUP, '2', NULL, "(a)(a)(?2)",                    "recursion into a group needs the group"},
{RK_GROUP, '3', NULL, "(a)(a)(a)(?3)",                 "recursion into a group needs the group"},
{RK_GROUP, '4', NULL, "(a)(a)(a)(a)(?4)",              "recursion into a group needs the group"},
{RK_GROUP, '5', NULL, "(a)(a)(a)(a)(a)(?5)",           "recursion into a group needs the group"},
{RK_GROUP, '6', NULL, "(a)(a)(a)(a)(a)(a)(?6)",        "recursion into a group needs the group"},
{RK_GROUP, '7', NULL, "(a)(a)(a)(a)(a)(a)(a)(?7)",     "recursion into a group needs the group"},
{RK_GROUP, '8', NULL, "(a)(a)(a)(a)(a)(a)(a)(a)(?8)",  "recursion into a group needs the group"},
{RK_GROUP, '9', NULL, "(a)(a)(a)(a)(a)(a)(a)(a)(a)(?9)","recursion into a group needs the group"},
/* SR-9's two tailed rows. Their `syntax` has to put the construct LEFTMOST for
 * pcrec (which reports the leftmost construct it cannot handle), so the group
 * declaration libpcre2 needs cannot live there — it lives here, which is what
 * this table is for. */
{RK_GROUP, 'P', "=", "(?<n>a)(?P=n)", "a python-style backreference needs the name declared"},
{RK_GROUP, 'P', ">", "(?<n>a)(?P>n)", "a python-style subroutine call needs the name declared"},
};

/* Substitute `syntax` out of `probe` for an escape libpcre2 always rejects, and
 * report whether the result stops compiling. See the call site for why. */
static int wrapper_is_load_bearing(const char *probe, const char *syntax)
{
    char mutated[512];
    const char *at = strstr(probe, syntax);
    size_t head, taillen;
    if (!at) return 0;
    head = (size_t)(at - probe);
    taillen = strlen(at + strlen(syntax));
    if (head + 2 + taillen + 1 > sizeof mutated) return 0;
    memcpy(mutated, probe, head);
    mutated[head] = '\\';
    mutated[head + 1] = 'Y';
    memcpy(mutated + head + 2, at + strlen(syntax), taillen);
    mutated[head + 2 + taillen] = 0;
    return pcre2_try(mutated, head + 2 + taillen, NULL, 0) != 0;
}

static const Wrapper *wrapper_for(RegKind k, int sel, const char *tail)
{
    for (size_t i = 0; i < sizeof WRAPPERS / sizeof WRAPPERS[0]; i++) {
        if (WRAPPERS[i].kind != k || WRAPPERS[i].sel != sel) continue;
        bool same_tail = (!WRAPPERS[i].tail && !tail) ||
                         (WRAPPERS[i].tail && tail && strcmp(WRAPPERS[i].tail, tail) == 0);
        if (same_tail) return &WRAPPERS[i];
    }
    return NULL;
}

static const char *kind_name(RegKind k)
{
    switch (k) {
    case RK_ESC:          return "esc";
    case RK_GROUP:        return "group";
    case RK_VERB:         return "verb";
    case RK_CLASSBRACKET: return "classbracket";
    default:              return "?";
    }
}

static void check_rows(void)
{
    int wrappers_used = 0;
    int wrapper_hit[sizeof WRAPPERS / sizeof WRAPPERS[0]] = {0};
    int n_capability = 0;
    char label2[320];

    for (int k = 0; k < RK_COUNT; k++) {
        size_t n;
        const RegRow *rows = pcrec_registry((RegKind)k, &n);
        for (size_t i = 0; i < n; i++) {
            const RegRow *r = &rows[i];
            const Wrapper *w = wrapper_for(r->kind, r->sel, r->tail);
            const char *probe = w ? w->probe : r->syntax;
            char label[256], msg[256];

            snprintf(label, sizeof label, "%s %s", kind_name(r->kind), r->syntax);

            if (w) {
                wrappers_used++;
                wrapper_hit[w - WRAPPERS] = 1;
                if (!strstr(w->probe, r->syntax)) {
                    bad("%s: wrapper \"%s\" does not CONTAIN the row's syntax "
                        "\"%s\" — it would be testing something else",
                        label, w->probe, r->syntax);
                    continue;
                }
                /* A wrapper that is not NEEDED is worse than none: it silently
                 * moves the check off the row's own `syntax` and onto a longer
                 * pattern, and it is the natural way to paper over a row that
                 * has started failing for a real reason. */
                if (pcre2_try(r->syntax, strlen(r->syntax), NULL, 0) == 0)
                    bad("%s: the row's own syntax compiles under libpcre2, so the "
                        "wrapper \"%s\" is unnecessary — delete it and let the row "
                        "be tested as written", label, w->probe);
                /* AND THE SYNTAX MUST BE LOAD-BEARING WHERE IT SITS. "Contains
                 * the syntax" is not enough: a critic hid a fabricated row's
                 * syntax inside a PCRE2 comment — `(?#\3)` compiles, and so does
                 * anything else you put there — which satisfied both guards
                 * above and turned the fabrication check into a PASS (R8/C1-F3).
                 *
                 * So substitute the syntax out for `\Y`, which libpcre2 always
                 * rejects (error 103, "unrecognized character follows \"), and
                 * require the wrapper to FAIL. If it still compiles, libpcre2
                 * never parsed that position as syntax and the probe proves
                 * nothing about the row. */
                if (!wrapper_is_load_bearing(w->probe, r->syntax))
                    bad("%s: replacing the row's syntax inside the wrapper \"%s\" "
                        "with an always-invalid escape STILL COMPILES — libpcre2 is "
                        "not parsing that position (a comment? a class?), so the "
                        "probe says nothing about this row", label, w->probe);
            }

            int rc = pcre2_try(probe, strlen(probe), msg, sizeof msg);

            /* AND pcrec's side of the same row. Without this, `check_rows` was
             * a one-sided check: it asked libpcre2 whether the construct exists
             * and never asked pcrec what it does with it, so a row that had
             * started MISCOMPILING — `\K` silently accepted as a literal, say —
             * passed here (R8/C1-F5). registry_check.c does catch that, but a
             * file whose header claims "two claims per row are externally
             * checkable" should check both halves of both claims.
             *
             * pcrec gets the row's OWN `syntax`, never the wrapper: the wrapper
             * exists to satisfy libpcre2's context rules and has nothing to do
             * with reaching pcrec's doorway. */
            char cmsg[256];
            int pcrec_rejected = pcrec_try(r->syntax, cmsg, sizeof cmsg) != 0;
            if (r->status == RS_BASE && pcrec_rejected)
                bad("%s: the row is RS_BASE — pcrec implements it — but pcrec "
                    "REJECTED its own syntax: \"%s\"", label, cmsg);
            else if (r->status != RS_BASE && !pcrec_rejected)
                bad("%s: the row is %s, so pcrec must not compile it, and pcrec "
                    "COMPILED '%s'. That is the miscompile the mandate forbids.",
                    label, r->status == RS_MODULE ? "RS_MODULE" : "RS_REJECTED",
                    r->syntax);

            switch (r->status) {
            case RS_BASE:
            case RS_MODULE:
                /* The row claims PCRE2 HAS this construct. */
                if (rc == 0) { ok(label); break; }
                /* A CAPABILITY refusal is PCRE2 confirming the construct, not
                 * denying it: it names the thing and says this MODE cannot have
                 * it. Our oracle compiles with options = 0 and so can never be
                 * in UTF mode, which is why `\N{U+0041}` can never return 0 here
                 * however it is wrapped. Q1 already made this call for error 204
                 * ((*TURKISH_CASING)); 193 is the same shape for `\N{U+dddd}`.
                 *
                 * THIS WIDENS THE ANTI-FABRICATION GUARD, so it is counted and
                 * the count is asserted below. Without that, "the probe did not
                 * compile but the error was in my allow-list" is exactly how a
                 * fabricated row would get in — the failure mode this whole file
                 * exists to prevent. */
                if (rc == 193 || rc == 204) {
                    n_capability++;
                    snprintf(label2, sizeof label2,
                             "%s (libpcre2 recognises it and refuses the MODE: error %d)", label, rc);
                    ok(label2);
                    break;
                }
                if (!w)
                    bad("%s: libpcre2 REJECTS the probe '%s' (error %d: %s).\n"
                        "        An %s row claims PCRE2 has this construct. Either the row "
                        "names something PCRE2 does not have, or the probe needs a context "
                        "wrapper in WRAPPERS[] here.",
                        label, probe, rc, msg,
                        r->status == RS_BASE ? "RS_BASE" : "RS_MODULE");
                else
                    bad("%s: libpcre2 REJECTS the wrapped probe '%s' (error %d: %s).\n"
                        "        The wrapper (%s) no longer supplies what PCRE2 needs.",
                        label, probe, rc, msg, w->why);
                break;

            case RS_REJECTED:
                /* The row claims agreement IS the compliance. Verdict AND
                 * identity: pcrec's own message must be PCRE2's message. A row
                 * rejected for an unrelated reason is not agreement. */
                if (rc == 0) {
                    bad("%s: libpcre2 COMPILES '%s'. The row is RS_REJECTED, which "
                        "claims PCRE2 rejects it too — pcrec is over-rejecting.",
                        label, probe);
                    break;
                }
                if (!r->msg || strcmp(r->msg, msg) != 0) {
                    bad("%s: libpcre2 rejects '%s' with error %d, but the identities differ.\n"
                        "        pcrec:   \"%s\"\n        libpcre2: \"%s\"",
                        label, probe, rc, r->msg ? r->msg : "(none)", msg);
                    break;
                }
                ok(label);
                break;
            }
        }
    }
    /* EXACTLY ONE row may take the capability-refusal path today: `\N{U+0041}`.
     * Asserting the number, not just printing it, is the difference between a
     * counter and a guard — a second row quietly acquiring the exemption is the
     * way this widening turns into the hole it was written to avoid. Raise it
     * deliberately, in the same commit as the row that needs it, or find out why
     * a row stopped compiling under libpcre2. */
    if (n_capability != 1)
        bad("capability-refusal exemptions: %d rows took the 193/204 path, expected "
            "exactly 1 (\\N{U+0041}). This path lets an RS_MODULE row pass without "
            "libpcre2 compiling its probe, so its population is asserted, not counted.",
            n_capability);
    else
        ok("capability-refusal exemptions: exactly 1 row (libpcre2 names the "
           "construct and refuses the mode)");

    /* A wrapper for a row that no longer exists would sit here forever looking
     * like coverage. It is the same shape as the stale-count hazard R6 measured
     * in tests/reject/, one level down. */
    for (size_t i = 0; i < sizeof WRAPPERS / sizeof WRAPPERS[0]; i++)
        if (!wrapper_hit[i])
            bad("WRAPPERS[%zu] (%s selector '%c', probe \"%s\") matched no registry "
                "row — the row it was written for is gone", i,
                kind_name(WRAPPERS[i].kind), WRAPPERS[i].sel, WRAPPERS[i].probe);

    printf("  (%d of the probes needed a context wrapper; %zu wrappers defined)\n",
           wrappers_used, sizeof WRAPPERS / sizeof WRAPPERS[0]);
}

/* ---- part 3: the verb NAME differential -------------------------------- */

/* What libpcre2's answer OBLIGES pcrec to say. Total: every error code lands in
 * exactly one bucket, so there is no exclusion list and nothing is skipped.
 *
 * TWO STRENGTHS OF OBLIGATION, and keeping them apart is the point (R8/C1-F2).
 * For 160, 195, 166 and 109 libpcre2 supplies an IDENTITY — it is saying which
 * thing is wrong — and pcrec must reproduce it exactly. For "it compiled", and
 * for the last bucket, libpcre2 supplies only a VERDICT: it says the construct
 * exists, and it has no opinion at all about what pcrec should call the module
 * that would implement it. Module names are pcrec's own taxonomy and no outside
 * authority can check them.
 *
 * So those two buckets require the diagnostic's SHAPE — a rejection naming some
 * module — and not its text. The first draft required the literal string
 * "(*...) requires module 'verbs'", which quietly made this file the authority
 * on a question libpcre2 was never asked: it certified `(*atomic:a)`,
 * `(*script_run:a)` and `(*UTF)` as belonging to module 'verbs' when in PCRE2's
 * own taxonomy they are atomic groups, script runs and option settings. Worse,
 * it ratcheted the wrong way — the day SR-6 routes those correctly, an exact
 * match would FAIL and someone would have to loosen the conformance test to
 * accept a more correct compiler. A check that must be weakened when the
 * subject improves is measuring the subject against itself.
 *
 * WHAT REMAINS UNCHECKED HERE, said plainly: that `(*ACCEPT)` names module
 * 'verbs' rather than module 'walruses'. tests/reject/'s hand-written rows are
 * the only check of that, exactly as they are for every other doorway. */
enum { OBL_MODULE, OBL_EXACT };

static int required_answer(int rc, const char **want)
{
    switch (rc) {
    case 160: *want = "(*VERB) not recognized or malformed";          return OBL_EXACT;
    case 195: *want = "(*alpha_assertion) not recognized";            return OBL_EXACT;
    case 166: *want = "(*MARK) must have an argument";                return OBL_EXACT;
    case 109: *want = "quantifier does not follow a repeatable item"; return OBL_EXACT;
    case 148: *want = "subpattern name is too long (maximum 128 code units)";
                                                                      return OBL_EXACT;
    default:  *want = "a rejection naming a module (\"... requires module '...'\")";
              return OBL_MODULE;
    }
}

/* The OBL_MODULE shape. Deliberately not `strstr(msg, "verbs")`. */
static int names_a_module(const char *msg)
{
    const char *p = strstr(msg, "requires module '");
    return p && strchr(p + 17, '\'') != NULL;
}

/* The "some other error code" bucket, COUNTED PER CODE and printed. The first
 * version of this file described that bucket in a comment naming errors 114,
 * 115 and 204 — and a critic measured what is actually in it: 231 of the 326
 * probes are error 122, "unmatched closing parenthesis", a code the comment did
 * not know existed. The reasoning that licenses the bucket had been checked
 * against a list that excluded its own dominant member.
 *
 * So the file no longer states the contents; it prints them. A reader can
 * reproduce the number, which is the whole difference between a measurement and
 * a remembered one — and if a libpcre2 upgrade introduces a new code here, it
 * appears in the output instead of hiding inside a comment's "etc". */
#define OTHER_CODES_CAP 32
static int      other_code[OTHER_CODES_CAP];
static unsigned other_n[OTHER_CODES_CAP];
static int      other_codes = 0;
static unsigned other_overflow = 0;

static void other_code_seen(int rc)
{
    for (int i = 0; i < other_codes; i++)
        if (other_code[i] == rc) { other_n[i]++; return; }
    if (other_codes == OTHER_CODES_CAP) { other_overflow++; return; }
    other_code[other_codes] = rc;
    other_n[other_codes++] = 1;
}

static void print_other_codes(void)
{
    printf("  the recognised-but-refused bucket, by code:");
    if (!other_codes) { printf(" (empty)\n"); return; }
    for (int i = 0; i < other_codes; i++) {
        unsigned char m[256];
        pcre2.get_error_message(other_code[i], m, sizeof m);
        printf("\n      %4d  n=%-6u %s", other_code[i], other_n[i], (char *)m);
    }
    if (other_overflow)
        printf("\n      (+%u probes with codes beyond the %d-code cap)",
               other_overflow, OTHER_CODES_CAP);
    putchar('\n');
}

/* A candidate-name set with a hash so the pool can be large. */
#define NAMESET_CAP (1u << 19)
static char       *ns_key[NAMESET_CAP];
/* WHICH SOURCE first produced each name. Without this the differential can
 * degrade to pcrec-checks-pcrec and every liveness assertion still passes — a
 * critic measured exactly that (R8/C1-F4): make pool_from_library() succeed but
 * yield nothing, and 84% of the probes still run (they come from mutations of
 * pcrec's OWN table), all four liveness checks pass, "every verb name pcrec
 * claims was reached" passes, and DELETING A REAL VERB ROW becomes invisible.
 * The liveness checks asserted the pool was non-empty; the property that
 * matters is that it is EXTERNAL, and only provenance can assert that. */
enum { NS_LIB = 1, NS_MUT = 2, NS_BYTE = 3 };
static unsigned char ns_src[NAMESET_CAP];
static int         ns_current_src = NS_LIB;
static unsigned    ns_count;
static unsigned    ns_dropped_long;   /* candidate longer than the cap */
static unsigned    ns_dropped_full;   /* the set filled up */

static unsigned ns_hash(const char *s, size_t n)
{
    unsigned h = 2166136261u;
    for (size_t i = 0; i < n; i++) { h ^= (unsigned char)s[i]; h *= 16777619u; }
    return h;
}

/* Returns 1 if newly added. Names may contain any byte except NUL; the pool is
 * built from NUL-terminated runs so that restriction is inherent, and the
 * embedded-NUL case is covered by a hand-written probe below instead. */
static int ns_add(const char *s, size_t n)
{
    if (n == 0) return 0;
    /* Both caps are REPORTED by check_verb_names, never silent: a sweep that
     * quietly stopped covering things reads as a sweep that covered them.
     *
     * This cap was 64, justified as "above every name PCRE2 has (the longest is
     * 30 bytes)". The premise is true and the inference was wrong (R8/C2-4):
     * the longest REAL name bounds where a match can occur, not where libpcre2's
     * REJECTION changes shape — and it changes at 129 bytes, to error 148
     * "subpattern name is too long", a rejection this sweep had never seen. */
    if (n > 256)                       { ns_dropped_long++; return 0; }
    if (ns_count * 2 >= NAMESET_CAP)   { ns_dropped_full++; return 0; }
    unsigned h = ns_hash(s, n) & (NAMESET_CAP - 1);
    while (ns_key[h]) {
        if (strlen(ns_key[h]) == n && memcmp(ns_key[h], s, n) == 0) return 0;
        h = (h + 1) & (NAMESET_CAP - 1);
    }
    char *c = malloc(n + 1);
    memcpy(c, s, n); c[n] = 0;
    ns_key[h] = c;
    ns_src[h] = (unsigned char)ns_current_src;
    ns_count++;
    return 1;
}

/* Slot for `name`, or -1. */
static long ns_slot(const char *name, size_t len)
{
    unsigned h = ns_hash(name, len) & (NAMESET_CAP - 1);
    while (ns_key[h]) {
        if (strlen(ns_key[h]) == len && memcmp(ns_key[h], name, len) == 0) return (long)h;
        h = (h + 1) & (NAMESET_CAP - 1);
    }
    return -1;
}

/* Candidate source 1: libpcre2's own binary. PCRE2 stores its verb, assertion
 * and script names as compiled-in strings, so the shared object is a source of
 * candidate names that is genuinely OUTSIDE pcrec. Prefixes and suffixes are
 * added too: `ANYCRLF`, `CRLF` and `LF` are all real PCRE2 option names that
 * appear in the binary only INSIDE `BSR_ANYCRLF`, so a run-only pool would
 * have missed three names it is this check's whole job to notice. */
static int pool_from_library(const char *path, int *runs_out)
{
    FILE *f = fopen(path, "rb");
    if (!f) return 0;
    if (fseek(f, 0, SEEK_END) != 0) { fclose(f); return 0; }
    long sz = ftell(f);
    if (sz <= 0) { fclose(f); return 0; }
    rewind(f);
    unsigned char *buf = malloc((size_t)sz);
    if (!buf) { fclose(f); return 0; }
    size_t got = fread(buf, 1, (size_t)sz, f);
    fclose(f);
    if (got != (size_t)sz) { free(buf); return 0; }

    int runs = 0;
    char cur[128]; size_t cl = 0;
    for (long i = 0; i <= sz; i++) {
        int c = i < sz ? buf[i] : 0;
        int isname = (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') ||
                     (c >= '0' && c <= '9') || c == '_';
        if (isname && cl < sizeof cur) { cur[cl++] = (char)c; continue; }
        if (cl > 0) {
            runs++;
            for (size_t a = 0; a < cl; a++) {
                ns_add(cur + a, cl - a);          /* every suffix  */
                ns_add(cur, a + 1);               /* every prefix  */
            }
            cl = 0;
        }
    }
    free(buf);
    *runs_out = runs;
    return 1;
}

/* Candidate source 2: single-character mutations of every name pcrec claims.
 * This is the direction that catches a MISSPELLING — `ACCPET` for `ACCEPT` —
 * which no pool built from PCRE2's binary would ever contain, and it catches
 * shadowing (a longer row swallowing a shorter one). It seeds from pcrec's
 * table on purpose: a deleted row is still covered, because source 1 supplies
 * the real name independently. */
static const char MUT_ALPHA[] =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_:=) ";

static void pool_from_mutations(void)
{
    ns_current_src = NS_MUT;
    for (int w = 0; w < 2; w++) {
        const VerbTable *t = pcrec_registry_verb_tables(w);
        for (size_t i = 0; i < t->n; i++) {
            const char *nm = t->rows[i].name;
            size_t len = strlen(nm);
            char b[128];
            if (len + 2 >= sizeof b) continue;

            for (size_t p = 0; p < len; p++) {            /* delete one */
                memcpy(b, nm, p); memcpy(b + p, nm + p + 1, len - p - 1);
                ns_add(b, len - 1);
            }
            for (size_t p = 0; p < len; p++)               /* substitute one */
                for (const char *a = MUT_ALPHA; *a; a++) {
                    memcpy(b, nm, len); b[p] = *a; ns_add(b, len);
                }
            for (size_t p = 0; p <= len; p++)              /* insert one */
                for (const char *a = MUT_ALPHA; *a; a++) {
                    memcpy(b, nm, p); b[p] = *a;
                    memcpy(b + p + 1, nm + p, len - p);
                    ns_add(b, len + 1);
                }
            for (size_t p = 0; p < len; p++) {             /* flip one case */
                memcpy(b, nm, len);
                if (b[p] >= 'a' && b[p] <= 'z') b[p] = (char)(b[p] - 32);
                else if (b[p] >= 'A' && b[p] <= 'Z') b[p] = (char)(b[p] + 32);
                ns_add(b, len);
            }
        }
    }
}

/* Candidate source 3: every single byte, so the doorway's first-byte decision
 * (which of PCRE2's two name tables applies) is swept exhaustively rather than
 * sampled. */
static void pool_from_bytes(void)
{
    ns_current_src = NS_BYTE;
    for (int b = 1; b < 256; b++) { char c = (char)b; ns_add(&c, 1); }
}

/* Candidate source 4: LENGTHS, straddling the boundaries libpcre2 actually has.
 * The library pool cannot supply these — nothing inside libpcre2 is a 129-byte
 * run of one letter — so a length rule is invisible to sources 1 and 2 no matter
 * how large the cap is. Both cases, because the two name tables reach the limit
 * separately. */
static void pool_from_lengths(void)
{
    static const int LENS[] = {1, 2, 3, 30, 31, 32, 63, 64, 65,
                               126, 127, 128, 129, 130, 200, 256};
    char buf[300];
    ns_current_src = NS_BYTE;
    for (size_t i = 0; i < sizeof LENS / sizeof LENS[0]; i++) {
        int n = LENS[i];
        memset(buf, 'A', (size_t)n); ns_add(buf, (size_t)n);
        memset(buf, 'a', (size_t)n); ns_add(buf, (size_t)n);
    }
}

/* The forms each candidate is written in. Two positions, because a
 * start-of-pattern option is only valid at the start and nothing in the repo
 * tested that before.
 *
 * THE PRECONDITION EVERY FORM HERE OBEYS, and it is not a detail (R8/C2):
 * **the `(*` doorway must be the pattern's ONLY error.** pcrec reports the
 * LEFTMOST construct it cannot handle and stops; libpcre2 compiles what it can
 * and reports whatever it reaches. On a pattern with two problems the two are
 * answering different questions, and comparing their messages measures the
 * ordering, not the doorway.
 *
 * A critic generated exactly those patterns and found 111 "mismatches":
 * `(*FAIL)*` is PCRE2 error 109 (the verb is real, the quantifier is not
 * allowed on it) while pcrec says "requires module 'verbs'" about the verb it
 * met first; `(*UTF)a(*UTF)` is PCRE2 error 160 for the SECOND option while
 * pcrec answers about the first. Neither is a verb-doorway defect, and the
 * proof that it is not is that the same shape exists at every other doorway and
 * always has: `\d{3,1}` is PCRE2 error 104 "numbers out of order" and pcrec
 * says "\d requires module 'classes'". Nobody has ever called that a bug.
 *
 * So the forms stay single-error, and the reason is written down rather than
 * left to be rediscovered as a finding a third time. If you add a form, check
 * it cannot introduce a second error — `(*%s)b` is safe because a literal is
 * not an error; `(*%s)*` is not.
 *
 * ONE THING THAT MEASUREMENT LEFT BEHIND, worth having when SR-6 arrives:
 * PCRE2's quantifiability split across the verb surface is exactly
 * `(*ACCEPT)` plus the whole lower table (which are group constructs, hence
 * quantifiable) against everything else. `(*ACCEPT)*` compiles and `(*FAIL)*`
 * does not. Module 'verbs' has to reproduce that; nothing in this repo measures
 * it, because pcrec has no verb to quantify yet. */
static const char *FORMS[] = {
    "(*%s)", "(*%s:x)", "(*%s:)", "(*%s=1)", "(*%s=x)", "(*%s",
    "a(*%s)", "a(*%s:x)", "a(*%s=1)", "(*%s:x", "(*%s)b",
    /* The two straddling libpcre2's `=digits` MAGNITUDE boundary. Without them
     * the `=` axis is only ever one digit wide, and reverting pcrec's magnitude
     * rule produced ZERO failures here — the fix was in place and nothing
     * generated a probe that could see it. A fix whose guard does not fire is
     * an unguarded fix. */
    "(*%s=4294967289)", "(*%s=4294967290)",
};

static void check_verb_names(void)
{
    size_t nforms = sizeof FORMS / sizeof FORMS[0];
    unsigned long probes = 0, mismatches = 0;
    unsigned long buckets[7] = {0};   /* accept, 160, 195, 166, 109, defer, 148 */
    int reported = 0;

    for (unsigned h = 0; h < NAMESET_CAP; h++) {
        if (!ns_key[h]) continue;
        const char *nm = ns_key[h];
        for (size_t fi = 0; fi < nforms; fi++) {
            char pat[256], pmsg[256], cmsg[256];
            snprintf(pat, sizeof pat, FORMS[fi], nm);

            const char *want;
            int rc  = pcre2_try(pat, strlen(pat), pmsg, sizeof pmsg);
            int obl = required_answer(rc, &want);
            probes++;
            switch (rc) {
            case 0:   buckets[0]++; break;
            case 160: buckets[1]++; break;
            case 195: buckets[2]++; break;
            case 166: buckets[3]++; break;
            case 109: buckets[4]++; break;
            case 148: buckets[6]++; break;   /* an identity, not the default bucket */
            default:  buckets[5]++; other_code_seen(rc); break;
            }

            cmsg[0] = 0;
            if (pcrec_try(pat, cmsg, sizeof cmsg) == 0) {
                /* pcrec compiled a verb construct. It has no verb module, so
                 * this can only mean the doorway was never reached. */
                mismatches++;
                if (reported++ < 20)
                    bad("verb differential: pcrec COMPILED '%s'; libpcre2 says "
                        "%d (%s), so pcrec owed %s", pat, rc, pmsg, want);
                continue;
            }
            if (obl == OBL_EXACT ? strcmp(cmsg, want) != 0 : !names_a_module(cmsg)) {
                mismatches++;
                if (reported++ < 20)
                    bad("verb differential: '%s'\n"
                        "        libpcre2: %d (%s)\n"
                        "        pcrec owed: %s\n"
                        "        pcrec said: \"%s\"", pat, rc, pmsg, want, cmsg);
            }
        }
    }

    printf("  verb names probed: %u candidates x %zu forms = %lu probes\n",
           ns_count, nforms, probes);
    printf("  candidates dropped: %u over the 256-byte cap, %u for a full set\n",
           ns_dropped_long, ns_dropped_full);
    if (ns_dropped_full)
        bad("the candidate set filled up (%u dropped): the sweep silently "
            "narrowed. Raise NAMESET_CAP.", ns_dropped_full);
    printf("  libpcre2 verdicts: %lu compile, %lu err160, %lu err195, %lu err166, "
           "%lu err109, %lu err148, %lu other(recognised)\n",
           buckets[0], buckets[1], buckets[2], buckets[3], buckets[4],
           buckets[6], buckets[5]);
    if (buckets[6] == 0)
        bad("no candidate was longer than PCRE2's 128-byte name limit — the "
            "length boundary that pool_from_lengths exists to reach is unswept");
    print_other_codes();
    if (reported > 20)
        printf("  (only the first 20 of %lu mismatches were printed)\n", mismatches);

    if (mismatches == 0)
        ok("verb differential: pcrec matched libpcre2 on every generated name");

    /* A differential that found no disagreement proves nothing unless it was
     * LIVE. These four assert that the pool actually reached each interesting
     * verdict; a pool that had silently collapsed to nothing would pass the
     * comparison above and fail here. */
    if (buckets[0] == 0) bad("verb differential is not live: no candidate COMPILED");
    else ok("verb differential liveness: some candidate compiled");
    if (buckets[1] == 0) bad("verb differential is not live: no candidate hit error 160");
    else ok("verb differential liveness: some candidate was an unknown upper-table name");
    if (buckets[2] == 0) bad("verb differential is not live: no candidate hit error 195");
    else ok("verb differential liveness: some candidate was an unknown lower-table name");
    if (buckets[5] == 0) bad("verb differential is not live: no candidate was "
                             "recognised-but-refused (see the per-code breakdown above)");
    else ok("verb differential liveness: some candidate was recognised and refused");

    /* PROVENANCE, and this is the assertion that keeps the differential
     * external (R8/C1-F4). Every name pcrec claims must be reached by the pool,
     * and reached BY THE LIBRARY — not by a mutation of pcrec's own table,
     * which would make the check circular exactly where it claims not to be.
     *
     * The earlier version asked only "was it reached". A critic then made
     * pool_from_library() succeed and yield nothing: 84% of the probes still
     * ran (from mutations), all four liveness checks passed, this check passed,
     * and deleting the real `(*SKIP)` row became completely invisible. Asking
     * WHERE the name came from is what turns that into a failure. */
    unsigned n_lib = 0, n_mut = 0, n_byte = 0;
    for (unsigned h = 0; h < NAMESET_CAP; h++)
        if (ns_key[h]) {
            if      (ns_src[h] == NS_LIB)  n_lib++;
            else if (ns_src[h] == NS_MUT)  n_mut++;
            else                           n_byte++;
        }
    printf("  candidates by source: %u from libpcre2's binary, %u from mutations "
           "of pcrec's table, %u generated\n", n_lib, n_mut, n_byte);

    int unreached = 0, not_external = 0;
    for (int w = 0; w < 2; w++) {
        const VerbTable *t = pcrec_registry_verb_tables(w);
        for (size_t i = 0; i < t->n; i++) {
            const char *nm = t->rows[i].name;
            long slot = ns_slot(nm, strlen(nm));
            if (slot < 0) {
                bad("verb name '%s' is in pcrec's table but the generated pool "
                    "never produced it — it is unswept", nm);
                unreached++;
            } else if (ns_src[slot] != NS_LIB) {
                bad("verb name '%s' was reached only by mutating pcrec's OWN table, "
                    "not by libpcre2's binary. Deleting this row would be invisible: "
                    "the candidate would vanish with it.", nm);
                not_external++;
            }
        }
    }
    if (!unreached && !not_external)
        ok("every verb name pcrec claims was produced INDEPENDENTLY by libpcre2's "
           "own binary");

    /* And the source itself has to be carrying weight. A floor, not an exact
     * count: the pool's size depends on the installed libpcre2 build. */
    if (n_lib < 1000)
        bad("only %u candidate names came from libpcre2's binary (floor 1000). "
            "The external source has stopped contributing and the differential is "
            "degrading to pcrec-checks-pcrec.", n_lib);
    else
        ok("libpcre2's binary supplied the bulk of the candidate pool");
}

/* ---- part 4: the CLASS-BRACKET doorway, generated ---------------------- *
 *
 * PC-3's own spec text said it would be "the natural home for the finding that
 * pcrec accepts `[:alpha:]` (K3) — found by hand, and findable mechanically".
 * It was not built at PC-3, because it went red on a pinned deferred bug; it
 * lands with FIX-2, which is the change that makes it green (R8/C4-9).
 *
 * The same shape as the verb differential and for the same reason: GENERATE the
 * space, do not list it. A hand-written list is what the project had — five
 * pinned known-wrong lines — and the generator found 126 divergences across 555
 * patterns on its first run, including two families nobody had written down
 * (`[::]` over-accepted, and the whole `[[.a\]b]x.]` escape family
 * over-rejected).
 *
 * THE OBLIGATION IS A VERDICT, NOT A MESSAGE. Under D26 this is tier 2: pcrec
 * must not COMPILE what PCRE2 refuses (a silent wrong matcher, the one class
 * the charter forbids) and must not REFUSE what PCRE2 compiles. Naming a module
 * for something PCRE2 accepts is neither — it is the honest "not implemented
 * yet", and `[[:alpha:]]` is exactly that until module `classes` lands. */
static const char *CLS_DELIMS  = ":.=";
/* Bodies are expanded through `cls_expand` too, so a `%c` here is the delimiter
 * under test. Before R9/C2-6 the only body containing a delimiter was the
 * literal `x[:y` — colon-hardcoded — so no generated pattern ever placed a
 * LOOSE delimiter inside a class for `.` or `=`. Dropping the `]` from the
 * close check (making a bare delimiter close the pair) then produced 19,964
 * over-rejections against libpcre2, minimal cases `[::a]` and `[.a.b]`, while
 * this differential printed its unchanged totals and its per-delimiter
 * nested-opener floor passed. One hand-written `accept '[.a.b]'` row in
 * tests/reject/ was the entire defence. */
static const char *CLS_BODIES[] = {
    "a", "", "alpha", "a\\]b", "a\\\\", "^a", "b]c",
    "x[%cy",      /* a nested opener, at every delimiter rather than only `:` */
    "a%cb",       /* a LOOSE delimiter mid-body */
    "%c",         /* ...and alone */
    "%c%c"        /* ...and doubled, so `::` and `..` are generated */
};
static const char *CLS_SHAPES[] = {
    "[%c%s%c]",        /* the class's own bracket is the opener (doorway 4a) */
    "[[%c%s%c]]",      /* an inner bracket (4b) */
    "[x[%c%s%c]]",
    "[[%c%s]",         /* nothing closes the pair */
    "[a[%c%s]",
    "[^%c%s%c]",       /* negated: `^` sits between the bracket and the delimiter */
    "[[%c]",
    "[%c]",
    "[[%c%s%c]",
    "[[%ca[%cb%c]%c]]", /* a NESTED opener, which wins */
    /* And the same at the class's OWN bracket. R9/C2-3 turned rule 2 off for
     * doorway 4a at the `.` and `=` delimiters only and the ENTIRE repository
     * stayed green — including the nested-opener floor added hours earlier,
     * because every nested opener the sweep generated was a 4b one. The
     * five-byte reduction is `[.[.]`, which libpcre2 compiles as a class of `.`
     * and `[`. Two shapes for one rule because the rule has two positions. */
    "[%c[%c%s]",
    "[%c[%c]"
};
static const char *CLS_TRAILERS[] = {"", "x", "x%c]", "y]", "$", "]", "\\\\"};

/* Expand a shape template: `%c` becomes the delimiter and `%s` the body,
 * WHEREVER each appears and in whatever order.
 *
 * This used to be `snprintf(body, sizeof body, CLS_SHAPES[si], *d,
 * CLS_BODIES[bi], *d, *d, *d)` with a comment claiming "every shape takes at
 * most four %c and one %s; snprintf ignores the extras it is not given, so pass
 * generously". That is only true when the specifiers appear in the ARGUMENT
 * LIST'S ORDER, and exactly one shape broke it: `[[%ca[%cb%c]%c]]` takes four
 * %c and no %s, so its second %c consumed `CLS_BODIES[bi]`, a `const char *`,
 * as an `int`. Undefined behaviour, and in practice it emitted the low byte of
 * a string-literal address — so the ONE shape written to exercise K4's
 * nested-opener rule generated no nested opener at all, at any delimiter, and
 * at -O0 it truncated 21 of its probes to the five-character stub `[[=a[`.
 * Which patterns the sweep probed depended on `.rodata` layout while the header
 * kept printing the full count (R9/C1-F1).
 *
 * A positional expander cannot have that bug: there is no argument list to fall
 * out of step with, and no non-literal format string for `-Wformat-nonliteral`
 * to be unable to see through. */
static void cls_expand(char *out, size_t cap, const char *shape,
                       char delim, const char *body)
{
    size_t o = 0;
    for (const char *p = shape; *p && o + 1 < cap; p++) {
        if (p[0] == '%' && p[1] == 'c') {
            out[o++] = delim; p++;
        } else if (p[0] == '%' && p[1] == 's') {
            for (const char *b = body; *b && o + 1 < cap; b++) out[o++] = *b;
            p++;
        } else {
            out[o++] = *p;
        }
    }
    out[o] = 0;
}

/* Does `pat` contain a nested opener — a SECOND `[` + delimiter, met while the
 * scan is already inside the first one? That is the construct K4's scan rule 2
 * exists for, and TWO occurrences is the whole definition: the first `[%c` is
 * the pair the scan is looking to close, the second is the one that wins.
 *
 * The count, not merely the presence, is the point. The first version of this
 * function returned true on ONE occurrence, which made `[x[=a=]]` — an ordinary
 * inner bracket, doorway 4b — look like a nested opener, so the floor read
 * 511/504/504 and stayed green when the nested shape was sabotaged away. It was
 * a control that measured something adjacent to what it named. Caught by
 * running the positive control before believing the green (R9). */
static int has_nested_opener(const char *pat, char delim)
{
    int seen = 0;
    for (const char *p = pat; p[0] && p[1]; p++)
        if (p[0] == '[' && p[1] == delim && ++seen == 2) return 1;
    return 0;
}

/* ...and WHERE the outer one sits, because rule 2 has two positions and the
 * floor below must require both. 1 = the class's own bracket (doorway 4a, the
 * `[.[.]` corner), 0 = an inner bracket (4b), -1 = no nested opener.
 *
 * This split exists because the per-delimiter floor DEGRADED the moment the 4a
 * shapes were added for C2-F3: with them present, deleting the 4b nested-opener
 * shape left the counts at 154/112/112 and the floor green, so the guard that
 * caught R9/C1-1 stopped being able to catch it. A check that silently narrows
 * when you extend it is this project's own warning, arrived at by extending the
 * check. Six counters, not three. */
static int nested_opener_pos(const char *pat, char delim)
{
    if (!has_nested_opener(pat, delim)) return -1;
    return (pat[0] == '[' && pat[1] == delim) ? 1 : 0;
}

/* PROBE-COUNT FLOORS (R9/C1F-4). Every liveness assertion in this file is
 * two-dimensional in what it PROBES (axis x shapes) and one-dimensional in what
 * it ASSERTS — the shape axis has no floor, and the shape axis is exactly what a
 * later refactor trims. A critic shrank `CLS_TRAILERS` 7->1, `CLS_BODIES` 8->2,
 * `DELIM_SHAPES` 5->1 and `POS_SHAPES` 5->2, deleting **89% of all probes at
 * this doorway** — 3371 down to 359 — with every PASS line intact, the PC-3
 * count guard satisfied at its exact number, and all nine manifest needles
 * still matching. The count guard protects a check's EXISTENCE; nothing
 * protected its SIZE.
 *
 * So each sweep hard-checks its own probe total, which is the mechanism
 * tests/reject/ has used since R7 for `nrej`/`naccept`. Same caveat as there,
 * and it is why these sit BESIDE the manifest rather than replacing it: an
 * exact count tells you a number moved, never whether the change was right.
 * Update deliberately, in the same commit as the table you widened. */
/* A COUNT CANNOT SEE A SWAP. The probe-count floors above close every DELETION,
 * and a critic then showed what they cannot close: blanking a shape to `""`, or
 * replacing one shape with a duplicate of another, leaves the probe total
 * unchanged at 2772 and loses the same coverage with no signal (R9/C1-final2).
 *
 * So each sweep also checksums the PATTERN SET it actually generated. Same
 * discipline as the counts — a deliberate widening updates the constant in the
 * same commit — but it sees any change to WHICH patterns are probed, not merely
 * how many. FNV-1a, with a separator so that concatenation cannot alias. */
static unsigned long long set_hash(unsigned long long h, const char *s)
{
    for (const unsigned char *p = (const unsigned char *)s; *p; p++) {
        h ^= *p; h *= 1099511628211ULL;
    }
    h ^= (unsigned char)'\n'; h *= 1099511628211ULL;
    return h;
}
#define SET_HASH_INIT 14695981039346656037ULL

static void expect_set(const char *what, unsigned long long got, unsigned long long want)
{
    if (got != want)
        bad("%s: pattern-set checksum %#llx, expected %#llx. The number of probes may "
            "be unchanged — a shape that was blanked or replaced by a duplicate of "
            "another loses coverage without moving any count. Update this in the same "
            "commit if you changed the tables on purpose",
            what, got, want);
    else {
        char line[160];
        snprintf(line, sizeof line, "%s: pattern set unchanged (%#llx)", what, got);
        ok(line);
    }
}

static void expect_probes(const char *what, unsigned long got, unsigned long want)
{
    if (got != want)
        bad("%s: %lu probes, expected %lu. If you widened or trimmed a table on "
            "purpose, update this number in the same commit — if not, coverage "
            "was removed and every liveness assertion here would still pass",
            what, got, want);
    else {
        char line[160];
        snprintf(line, sizeof line, "%s: probe count intact (%lu)", what, got);
        ok(line);
    }
}

static void check_class_brackets(void)
{
    unsigned long probed = 0, agree = 0, deferred = 0;
    unsigned long over_accept = 0, over_reject = 0;
    int reported = 0;
    unsigned long nested[3][2] = {{0,0},{0,0},{0,0}};  /* [delimiter][4b=0, 4a=1] */
    unsigned long pc2_refused = 0;         /* the bucket the comment claimed */
    unsigned long long seth = SET_HASH_INIT;
    unsigned long promised = 0;            /* module named for what PCRE2 refuses */
    unsigned long unterminated = 0;        /* ...but only because the class never closed */

    for (const char *d = CLS_DELIMS; *d; d++)
        for (size_t bi = 0; bi < sizeof CLS_BODIES / sizeof CLS_BODIES[0]; bi++)
            for (size_t si = 0; si < sizeof CLS_SHAPES / sizeof CLS_SHAPES[0]; si++)
                for (size_t ti = 0; ti < sizeof CLS_TRAILERS / sizeof CLS_TRAILERS[0]; ti++) {
                    char body[128], tail[32], pat[256], cmsg[256];
                    char bodytxt[64];
                    cls_expand(bodytxt, sizeof bodytxt, CLS_BODIES[bi], *d, "");
                    cls_expand(body, sizeof body, CLS_SHAPES[si], *d, bodytxt);
                    cls_expand(tail, sizeof tail, CLS_TRAILERS[ti], *d, "");
                    snprintf(pat, sizeof pat, "%s%s", body, tail);
                    {   int np = nested_opener_pos(pat, *d);
                        if (np >= 0) nested[d - CLS_DELIMS][np]++; }
                    seth = set_hash(seth, pat);

                    int pc2 = pcre2_try(pat, strlen(pat), NULL, 0);
                    cmsg[0] = 0;
                    int rejected = pcrec_try(pat, cmsg, sizeof cmsg) != 0;
                    probed++;
                    if (pc2 != 0) pc2_refused++;

                    if (pc2 == 0 && !rejected)      { agree++; continue; }
                    if (pc2 != 0 && rejected) {
                        /* BOTH REFUSE — and this branch used to stop here,
                         * counting agreement without ever reading pcrec's
                         * message (R9/C1-8). That is 746 of the 1680 patterns,
                         * and it is exactly where the property FIX-2 exists to
                         * establish lives: promising module 'classes' for
                         * `[:alpha:]` is wrong BECAUSE libpcre2 rejects it.
                         * `check_posix_names` tests this for the 4b form only,
                         * so the class's own bracket had no external check of
                         * its own over-promise at all. */
                        if (strstr(cmsg, "requires module")) {
                            /* Naming a module for something libpcre2 refuses is
                             * the over-promise — UNLESS libpcre2's complaint is
                             * about something pcrec never reached. pcrec reports
                             * the LEFTMOST construct it cannot handle and stops,
                             * so `[[:alpha:]` is an honest "module needed" whose
                             * pattern also happens to lack its closing `]`.
                             *
                             * Separating the two mechanically rather than by a
                             * hand-listed exemption: append the `]` and ask
                             * libpcre2 again. If it compiles then, its objection
                             * was the termination and the construct pcrec named
                             * is real. `[:alpha:]]` does NOT compile, so the 4a
                             * over-promise is still caught. */
                            char closed[300];
                            snprintf(closed, sizeof closed, "%s]", pat);
                            if (pcre2_try(closed, strlen(closed), NULL, 0) != 0) {
                                promised++;
                                if (reported++ < 12)
                                    bad("class doorway: libpcre2 REJECTS '%s' and pcrec "
                                        "answered \"%s\" — a module promised for a pattern "
                                        "no module can make legal. This is the doorway's own "
                                        "over-promise (R8/C4-7) at the position where nothing "
                                        "external checked it (R9/C1-8)", pat, cmsg);
                            } else unterminated++;
                        }
                        agree++; continue;
                    }
                    if (pc2 == 0 && rejected) {
                        if (strstr(cmsg, "requires module")) { deferred++; continue; }
                        over_reject++;
                        if (reported++ < 12)
                            bad("class doorway: libpcre2 COMPILES '%s'; pcrec refused "
                                "with \"%s\", which names no module — an over-rejection",
                                pat, cmsg);
                        continue;
                    }
                    over_accept++;
                    if (reported++ < 12)
                        bad("class doorway: libpcre2 REJECTS '%s' and pcrec COMPILED it. "
                            "That is a matcher emitted for a pattern PCRE2 refuses — the "
                            "one class the charter forbids", pat);
                }

    printf("  class-bracket doorway: %lu generated patterns — %lu agree, "
           "%lu deferred to a module\n", probed, agree, deferred);
    expect_probes("class-bracket doorway", probed, 2772);
    expect_set("class-bracket doorway", seth, 0x69e3ddacf18fce3fULL);
    printf("  of the %lu both-refuse cases, %lu name a module wrongly, %lu name one "
           "for a construct PCRE2 has in a pattern that merely never closed\n",
           pc2_refused, promised, unterminated);
    if (promised == 0)
        ok("class-bracket doorway: no module promised for a pattern PCRE2 will never accept");
    if (over_accept == 0 && over_reject == 0)
        ok("class-bracket doorway: no over-acceptance and no over-rejection");
    else
        printf("  (%lu over-accept, %lu over-reject; first %d shown)\n",
               over_accept, over_reject, reported < 12 ? reported : 12);

    /* Liveness. A generator that produced only agreeing patterns would pass the
     * comparison above while testing nothing interesting. Both buckets must be
     * non-empty: some pattern PCRE2 refuses, and some it accepts and pcrec
     * defers. */
    if (deferred == 0)
        bad("class doorway: no generated pattern reached a module — the sweep is "
            "not exercising `[[:alpha:]]`-shaped constructs at all");
    else
        ok("class-bracket sweep is live: it reaches the POSIX-class deferral");

    /* THE OTHER BUCKET THE COMMENT ABOVE NAMED. It said "both buckets must be
     * non-empty: some pattern PCRE2 refuses, and some it accepts and pcrec
     * defers", and only the second was ever evaluated — `agree` merges both
     * directions, so the first half was an assertion that existed in prose only
     * (R9/C1-6). Healthy today at 746 of 1680; if a `pcre2_try` regression made
     * libpcre2 accept everything, the sweep would keep printing its totals and
     * its stated liveness proof would still pass. */
    if (pc2_refused == 0)
        bad("class doorway: libpcre2 refused NONE of %lu generated patterns. The "
            "over-acceptance half of this differential is comparing against nothing",
            probed);
    else
        ok("class-bracket sweep is live in both directions: libpcre2 refuses some too");

    /* PER-CONSTRUCT liveness, not just per-bucket. The two assertions above were
     * both green while the nested-opener shape generated nothing, because they
     * ask "did the sweep reach A module" and "did both verdict buckets fill" —
     * questions a sweep missing one whole construct still answers yes to.
     *
     * K4's scan rule 2 (a `[` followed by the same delimiter is a nested opener
     * and WINS) is the branch this floor guards, and it is the one that changes
     * only the error OFFSET, so a verdict differential cannot see it even when
     * the patterns ARE generated. Requiring the construct to appear FOR EVERY
     * DELIMITER is what makes the shape's absence visible: before R9/C1-F1 the
     * count was 42 for `:` and ZERO for `.` and `=`, so `[.` and `[=` — the two
     * collating rows — had rule 2 entirely unswept while the header printed the
     * full pattern total. */
    printf("  nested openers generated (4b/4a):");
    for (const char *d = CLS_DELIMS; *d; d++)
        printf(" '%c'=%lu/%lu", *d, nested[d - CLS_DELIMS][0], nested[d - CLS_DELIMS][1]);
    printf("\n");
    int all_live = 1;
    for (const char *d = CLS_DELIMS; *d; d++)
        for (int pos = 0; pos < 2; pos++)
            if (nested[d - CLS_DELIMS][pos] == 0) {
                all_live = 0;
                bad("class doorway: the sweep generated NO `[%c` nested opener at %s, so "
                    "K4's scan rule 2 is unexercised for delimiter '%c' in that position. "
                    "A shape that names the construct is not the same as a pattern that "
                    "contains it, and the two positions are two different shapes",
                    *d, pos ? "a class's OWN bracket (4a)" : "an inner bracket (4b)", *d);
            }
    if (all_live)
        ok("class-bracket sweep generates a nested opener for every delimiter, in BOTH positions");
}

/* ---- the DELIMITER byte sweep, against libpcre2 (R9/C1-F3) --------------
 *
 * `CLS_DELIMS` is `":.="`, hand-listed from pcrec's own three rows — so the
 * only instrument at this doorway with an EXTERNAL oracle never left the three
 * bytes pcrec already knows about. The sweep in registry_check.c does generate
 * bytes 1..255, but it compares the parser against pcrec's registry, which is a
 * control sharing a source with what it controls; every byte without a
 * `RD_FIXED` row falls through both `if` chains with no assertion evaluated
 * while the line still prints "all 255 bytes agree".
 *
 * A critic added `if (c2 == '!') ctx_fail(...)` to the doorway — a construct
 * with no registry row, and a genuine tier-2 over-rejection, since libpcre2
 * compiles both `[!alpha!]` and `[[!alpha!]]` — and every suite in the
 * repository stayed green.
 *
 * So: every byte in the delimiter slot, against libpcre2, in four shapes. Byte
 * 0 is absent because these patterns are built as C strings; the verb doorway's
 * `check_embedded_nul` is the only NUL probe in this file and doorway 4 has
 * none, which is recorded rather than fixed here. */
static const char *DELIM_SHAPES[] = {
    "[[%ca%c]]",       /* 4b, the inner bracket */
    "[%ca%c]",         /* 4a, the class's own bracket */
    "[[%c]]",
    "[a[%cb%c]c]",
    "[[%calpha%c]]"    /* a REAL POSIX name, so the module path is reachable */
};

static void check_class_delim_bytes(void)
{
    unsigned long probed = 0, agree = 0, deferred = 0;
    unsigned long over_accept = 0, over_reject = 0;
    int reported = 0;
    unsigned sig[256];                   /* pcrec's verdict vector per byte */
    unsigned long long seth = SET_HASH_INIT;

    for (int c = 1; c < 256; c++) {
        sig[c] = 0;
        for (size_t si = 0; si < sizeof DELIM_SHAPES / sizeof DELIM_SHAPES[0]; si++) {
            char pat[128], cmsg[256];
            cls_expand(pat, sizeof pat, DELIM_SHAPES[si], (char)c, "");

            int pc2 = pcre2_try(pat, strlen(pat), NULL, 0);
            cmsg[0] = 0;
            int rejected = pcrec_try(pat, cmsg, sizeof cmsg) != 0;
            probed++;
            sig[c] = (sig[c] << 1) | (unsigned)rejected;
            seth = set_hash(seth, pat);

            if ((pc2 == 0) == (!rejected)) { agree++; continue; }
            if (pc2 == 0 && rejected) {
                /* libpcre2 compiles it. "requires module" is the honest
                 * not-implemented-yet; anything else is an over-rejection, and
                 * that is the shape a construct with no registry row takes. */
                if (strstr(cmsg, "requires module")) { deferred++; continue; }
                over_reject++;
                if (reported++ < 12)
                    bad("class delimiter byte %d (0x%02x): libpcre2 COMPILES '%s'; pcrec "
                        "refused with \"%s\", which names no module. A construct recognised "
                        "at this doorway with no registry row looks exactly like this",
                        c, c, pat, cmsg);
                continue;
            }
            over_accept++;
            if (reported++ < 12)
                bad("class delimiter byte %d (0x%02x): libpcre2 REJECTS '%s' and pcrec "
                    "COMPILED it — a matcher emitted for a pattern PCRE2 refuses",
                    c, c, pat);
        }
    }

    printf("  class delimiter bytes: %lu probes over 255 bytes x %zu shapes — "
           "%lu agree, %lu deferred\n", probed,
           sizeof DELIM_SHAPES / sizeof DELIM_SHAPES[0], agree, deferred);
    expect_probes("class delimiter byte sweep", probed, 1275);
    expect_set("class delimiter byte sweep", seth, 0x0538673c9e76127fULL);
    if (over_accept == 0 && over_reject == 0)
        ok("class delimiter byte sweep: no over-acceptance and no over-rejection");

    /* LIVENESS WITHOUT READING THE TABLE. The obvious floor — "exactly three
     * bytes route to a module" — is both wrong (`[[.a.]]` is a fixed-text
     * rejection, not a module) and circular. This asks a question only the
     * PARSER can answer: how many bytes behave DIFFERENTLY from the ordinary
     * byte in the delimiter slot?
     *
     * Every byte gets a verdict vector across the shapes. Bytes with no
     * construct behind them share one vector — they are ordinary class members.
     * A byte the doorway recognises cannot share it. So the count of bytes
     * departing from the most common vector IS the number of live delimiters,
     * derived from behaviour rather than from `registry.c`, which is the whole
     * point of this file. Expect exactly three: `:`, `.`, `=`. */
    unsigned best = 0; int bestn = 0;
    for (int c = 1; c < 256; c++) {
        int n = 0;
        for (int d = 1; d < 256; d++) if (sig[d] == sig[c]) n++;
        if (n > bestn) { bestn = n; best = sig[c]; }
    }
    char odd[260]; size_t ol = 0;
    for (int c = 1; c < 256 && ol + 1 < sizeof odd; c++)
        if (sig[c] != best) odd[ol++] = (char)c;
    odd[ol] = 0;

    /* The expected SET, hand-written, not derived — a control has to be. Three
     * of these are the delimiter rows. The fourth is `\`, which behaves unlike
     * an ordinary member for a reason that has nothing to do with this doorway:
     * it is the class escape. It is left in the sweep rather than special-cased
     * out, because a sweep that quietly excludes the bytes it finds
     * inconvenient is how a 255-byte check becomes a 1-byte check. */
    printf("  bytes departing from ordinary-member behaviour: %s\n", ol ? odd : "(none)");
    if (strcmp(odd, ".:=\\") != 0)
        bad("class delimiter byte sweep: the live bytes are \"%s\", expected \".:=\\\\\" "
            "(the three delimiter rows, plus `\\` which is the class escape). A byte "
            "appearing here with no row behind it is what R9/C1-F3's `[!alpha!]` "
            "sabotage looked like; a byte DISAPPEARING means a doorway stopped working",
            odd);
    else
        ok("class delimiter byte sweep: exactly `:` `.` `=` (and the class escape) are "
           "live — no byte is recognised without a row");
}

/* The POSIX class NAME differential — the class-bracket doorway's half of the
 * same check `check_verb_names` runs at `(*`, and the direct answer to R8/C4-7.
 * It reuses the candidate pool already generated from libpcre2's own binary, so
 * the names come from PCRE2 and not from pcrec's fourteen.
 *
 * The obligation is the one D26 makes tier 2: a name libpcre2 HAS must be
 * deferred to a module, and a name it does not have must NOT be — promising
 * module 'classes' for `[[:foo:]]` is a promise no module can keep. Before
 * FIX-2 pcrec answered "requires module 'classes'" for all 12531 candidates,
 * i.e. its answer did not depend on the name at all, which is exactly the
 * property that makes a differential vacuous. */
static void check_posix_names(void)
{
    unsigned long probed = 0, real = 0, unknown = 0, wrong = 0;
    unsigned long real_ext = 0, real_mut = 0;
    int reported = 0;

    for (unsigned h = 0; h < NAMESET_CAP; h++) {
        if (!ns_key[h]) continue;
        for (int neg = 0; neg < 2; neg++) {
            char pat[512], cmsg[256];
            snprintf(pat, sizeof pat, "[[:%s%s:]]", neg ? "^" : "", ns_key[h]);
            int pc2 = pcre2_try(pat, strlen(pat), NULL, 0);
            cmsg[0] = 0;
            int rejected = pcrec_try(pat, cmsg, sizeof cmsg) != 0;
            probed++;

            if (pc2 == 0) {
                /* libpcre2 ACCEPTED the pattern, which means one of two things:
                 * the name is a real POSIX class (pcrec must defer it to a
                 * module), or the text was never a construct at all and both
                 * engines read ordinary class members — `[[:]:]]` is the latter,
                 * because the `]` ends the class before any name begins. Only a
                 * rejection that names NO module is wrong here. */
                real++;
                if (ns_src[h] == NS_MUT) real_mut++; else real_ext++;
                if (rejected && !strstr(cmsg, "requires module")) {
                    wrong++;
                    if (reported++ < 10)
                        bad("POSIX names: libpcre2 accepts '%s' but pcrec refused with "
                            "\"%s\" — an over-rejection", pat, cmsg);
                }
            } else {                              /* libpcre2 does NOT */
                unknown++;
                if (!rejected) {
                    wrong++;
                    if (reported++ < 10)
                        bad("POSIX names: libpcre2 REJECTS '%s' and pcrec COMPILED it", pat);
                } else if (strstr(cmsg, "requires module")) {
                    wrong++;
                    if (reported++ < 10)
                        bad("POSIX names: '%s' is not a POSIX class name libpcre2 has, "
                            "but pcrec answered \"%s\" — a module that will never "
                            "implement it", pat, cmsg);
                }
            }
        }
    }

    printf("  POSIX class names: %lu probes — %lu real names (%lu from libpcre2's own "
           "binary or the byte sweep, %lu from mutations of pcrec's table), "
           "%lu libpcre2 does not have\n",
           probed, real, real_ext, real_mut, unknown);
    expect_probes("POSIX class names", probed, 149774);
    if (!wrong) ok("POSIX class names: every name deferred or refused as libpcre2 does");

    /* Liveness, both directions. A pool that produced no real name would make
     * the "must defer" half vacuous, and one with no unknown name would make
     * the over-promise half vacuous — which is the half that was broken. */
    if (!real)    bad("POSIX name sweep is not live: no candidate was a real class name");
    else          ok("POSIX name sweep reaches real class names");
    if (!unknown) bad("POSIX name sweep is not live: no candidate was an unknown name");
    else          ok("POSIX name sweep reaches names libpcre2 does not have");

    /* PROVENANCE, and this is R8/C1-F4 one doorway across (R9/C1-F2).
     *
     * Everything above was satisfiable with the external source contributing
     * nothing. `real` counts patterns libpcre2 ACCEPTED, which is not the same
     * as names that are POSIX class names — `[[:]:]]` compiles because the `]`
     * ends the class before any name begins. A critic filtered PCRE2's class
     * names out of the pool and deleted `graph` from pcrec's table, and this
     * function printed "6 real names" and three PASS lines, all six of them
     * non-class byte probes, with a deleted name under test. The 51-failure
     * empty-pool sabotage that DOES catch it lives in `check_verb_names` and is
     * about a different name space — so this check's correctness was parasitic
     * on an assertion elsewhere.
     *
     * The property that matters is not that the pool is non-empty. It is that
     * the pool contains PCRE2's POSIX class names and that PCRE2 put them
     * there. So: every name pcrec claims must appear in the pool from a source
     * that is not a mutation of pcrec's own table. */
    size_t nnames = 0;
    const char *const *names = pcrec_registry_posix_names(&nnames);
    unsigned long missing = 0, self_sourced = 0;
    for (size_t i = 0; i < nnames; i++) {
        long h = ns_slot(names[i], strlen(names[i]));
        if (h < 0) { missing++;
            if (reported++ < 10)
                bad("POSIX names: pcrec claims '%s' but no candidate pool produced it, so "
                    "nothing external ever tested that claim", names[i]);
        } else if (ns_src[h] == NS_MUT) { self_sourced++;
            if (reported++ < 10)
                bad("POSIX names: '%s' reached the pool ONLY as a mutation of pcrec's own "
                    "table. A name pcrec invented, mutated and then recognised is not an "
                    "external check of anything", names[i]);
        }
    }
    if (!missing && !self_sourced)
        ok("every POSIX class name pcrec claims was produced INDEPENDENTLY of pcrec's table");

    /* A FLOOR ON THE CLAIMED NAMES, not on the accepted probes. The first
     * version of this compared `real_ext` against `real`, both of which count
     * patterns libpcre2 ACCEPTED — and under the very sabotage this section
     * exists to catch, both were 6, the same six non-class byte probes
     * (`[[:<:]]`, `[[:[:]]`, `[[:]:]]` and their `^` forms) that made the
     * original liveness vacuous. `24 < 6` is false, so it passed, and it would
     * pass with the external source contributing zero real class names. It
     * measured a ratio the byte pool guarantees, one line from the loop that
     * does the actual work (R9/C1F-5).
     *
     * The quantity that matters is how many of the names PCREC CLAIMS were
     * produced externally, which is what the loop above counted per name. */
    unsigned long ext_claimed = nnames - missing - self_sourced;
    printf("  POSIX names pcrec claims: %zu, of which %lu were produced by a source "
           "that is not a mutation of pcrec's own table\n", nnames, ext_claimed);
    if (ext_claimed != nnames)
        bad("POSIX names: only %lu of %zu names pcrec claims came from an external "
            "source. The differential is degrading to pcrec checking itself",
            ext_claimed, nnames);
    else
        ok("every POSIX name pcrec claims has an external source behind it");
}

/* ---- NAME x POSITION, the cell neither existing sweep generates (R9/C3-4) --
 *
 * `check_posix_names` varies the NAME across ~12000 candidates and builds every
 * one as `[[:NAME:]]` — the isolated shape, position fixed.
 * `check_class_brackets` varies POSITION across shapes and trailers and never
 * uses `<` or `>` as a body. Each is real and large on its own axis, and the
 * defect lived in the cross-product: libpcre2 accepts `[[:<:]]` but rejects
 * `[x[:<:]]`, `[[:<:]a]` and `[^[:<:]]`, while every ordinary class name works
 * in all four positions. pcrec promised module 'classes' for all of them.
 *
 * So: every name pcrec claims, in every position, against libpcre2. The names
 * come from pcrec's table ON PURPOSE here — the question is not "what names
 * exist" (that is `check_posix_names`' job, and it sources externally) but
 * "for each name pcrec claims, does its POSITION behaviour match PCRE2". */
static const char *POS_SHAPES[] = {
    "[[:%s:]]",      /* alone — the only shape `<` and `>` may take */
    "[x[:%s:]]",     /* a member before */
    "[[:%s:]x]",     /* a member after */
    "[^[:%s:]]",     /* negated: even a bare `^` breaks `<`/`>` */
    "[x[:%s:]y]"
};

static void check_posix_positions(void)
{
    size_t nnames = 0;
    const char *const *names = pcrec_registry_posix_names(&nnames);
    unsigned long probed = 0, agree = 0, deferred = 0, wrong = 0, restricted = 0;
    unsigned long pcrec_restricted = 0;
    unsigned long long seth = SET_HASH_INIT;
    int reported = 0;

    for (size_t i = 0; i < nnames; i++) {
        int any_reject = 0;        /* libpcre2 refused it in some position */
        int pcrec_varies = 0;      /* ...and pcrec's OWN answer changed too */
        int pcrec_deferred = 0;
        for (size_t si = 0; si < sizeof POS_SHAPES / sizeof POS_SHAPES[0]; si++) {
            char pat[256], cmsg[256];
            snprintf(pat, sizeof pat, POS_SHAPES[si], names[i]);
            seth = set_hash(seth, pat);

            int pc2 = pcre2_try(pat, strlen(pat), NULL, 0);
            cmsg[0] = 0;
            int rejected = pcrec_try(pat, cmsg, sizeof cmsg) != 0;
            probed++;

            if (rejected && strstr(cmsg, "requires module")) pcrec_deferred = 1;
            else if (rejected) pcrec_varies = 1;

            if (pc2 == 0) {
                /* libpcre2 has it here. pcrec owes a module, not a refusal. */
                if (rejected && strstr(cmsg, "requires module")) { deferred++; agree++; continue; }
                wrong++;
                if (reported++ < 10)
                    bad("POSIX position: libpcre2 compiles '%s' but pcrec answered \"%s\" "
                        "— a real name in a position PCRE2 accepts must still name a module",
                        pat, cmsg);
            } else {
                any_reject = 1;
                /* libpcre2 will never accept it here, so no module can. */
                if (!rejected) {
                    wrong++;
                    if (reported++ < 10)
                        bad("POSIX position: libpcre2 REJECTS '%s' and pcrec COMPILED it", pat);
                } else if (strstr(cmsg, "requires module")) {
                    wrong++;
                    if (reported++ < 10)
                        bad("POSIX position: '%s' is a name libpcre2 will not accept in this "
                            "POSITION, but pcrec answered \"%s\" — a module promised for a "
                            "pattern no module can make legal (R9/C3-4)", pat, cmsg);
                } else agree++;
            }
        }
        if (any_reject) restricted++;
        if (pcrec_varies && pcrec_deferred) pcrec_restricted++;
    }

    printf("  POSIX name x position: %lu probes over %zu names x %zu shapes — "
           "%lu agree, %lu deferred, %lu names position-restricted\n",
           probed, nnames, sizeof POS_SHAPES / sizeof POS_SHAPES[0],
           agree, deferred, restricted);
    expect_probes("POSIX name x position", probed, 80);
    expect_set("POSIX name x position", seth, 0xaf2c87f99da26e22ULL);
    if (!wrong)
        ok("POSIX name x position: every name's position behaviour matches libpcre2");

    /* Liveness that names the phenomenon rather than counting rows: at least
     * one name must be position-RESTRICTED, or this sweep has lost the only
     * thing it exists to see. Exactly two are (`<` and `>`); if that changes,
     * either PCRE2 changed or the doorway stopped distinguishing position. */
    if (restricted != 2)
        bad("POSIX name x position: LIBPCRE2 restricts %lu names by position, expected 2 "
            "(`<` and `>`). This is a statement about PCRE2 and about this probe pool, "
            "NOT about pcrec — if it moved, PCRE2 changed or the shapes stopped covering "
            "the positions", restricted);
    else
        ok("POSIX name x position: libpcre2 restricts exactly 2 names, so the pool is live");

    /* AND THE SAME COUNT FROM PCREC'S SIDE. The assertion above is computed
     * entirely from `pc2` and never reads pcrec's answer, so it stays green
     * under a FULL REVERT of the position rule — a critic proved that by
     * disabling `whole_class_only` and watching this line PASS in a run that
     * failed 8 other checks (R9/C3-verify). It is a real check of the probe
     * pool's liveness and its comment used to imply it was a check of pcrec.
     * `wrong == 0` above is what actually catches the regression; this counter
     * makes the claim its name suggests, by asking pcrec the same question:
     * for how many names does PCREC itself answer differently depending on
     * position — deferring to a module somewhere and refusing outright
     * elsewhere? That must be the same 2, and it is a fact about pcrec. */
    if (pcrec_restricted != restricted)
        bad("POSIX name x position: libpcre2 restricts %lu names by position but PCREC "
            "varies its answer by position for %lu. pcrec is not enforcing the same "
            "position rule PCRE2 has (R9/C3-4)", restricted, pcrec_restricted);
    else
        ok("POSIX name x position: pcrec varies its own answer by position for exactly "
           "the names libpcre2 restricts");
}

/* The one probe the pool cannot express, kept hand-written for that reason:
 * a name containing a NUL byte. argv and NUL-terminated pools both stop there,
 * and pcrec's own pattern buffer does not — it carries a length. */
static void check_embedded_nul(void)
{
    static const char pat[] = "(*A\0B)";
    size_t len = sizeof pat - 1;   /* 6 bytes, the NUL is DATA */
    char pmsg[256];
    const char *want;
    int rc = pcre2_try(pat, len, pmsg, sizeof pmsg);
    (void)required_answer(rc, &want);

    /* pcrec's public entry point takes a NUL-terminated pattern, so this probe
     * can only reach the parser as the truncated `(*A`. That is still worth
     * asserting — and stating — because the honest claim is "pcrec cannot be
     * handed this pattern", not "pcrec handles it". */
    char cmsg[256];
    if (pcrec_try("(*A", cmsg, sizeof cmsg) == 0) {
        bad("embedded NUL: pcrec compiled '(*A'");
        return;
    }
    if (rc != 160)
        bad("embedded NUL: libpcre2 gave %d (%s) for a NUL inside a verb name; "
            "this check assumed 160", rc, pmsg);
    else if (strcmp(cmsg, want) != 0)
        bad("embedded NUL: pcrec said \"%s\" for the truncation '(*A', owed \"%s\"",
            cmsg, want);
    else
        ok("a NUL inside a verb name is error 160, and pcrec's reachable "
           "truncation agrees");
}


/* ---- Q2: the `(?` doorway against libpcre2, generated ------------------
 *
 * THE CHECK THAT MAKES Q2 MEAN ANYTHING. Q1 gave the `(*` doorway a name
 * differential and PC-3's CLAUDE.md records why it works: while one catch-all
 * answered for every name, pcrec's answer did not depend on the name and the
 * comparison was vacuous. The `(?` doorway was in exactly that state until Q2 —
 * one catch-all promising module 'modifiers' for all 255 bytes — so this
 * differential could not have existed before the fix, and it is what stops the
 * fix from silently reverting.
 *
 * PCRE2'S "NO CONSTRUCT HERE" ERRORS ARE 111 AND 141, and treating any other
 * error as recognition is the load-bearing judgement in this file. `(?+x)` is
 * error 129 "digit expected after (?+ or (?-" — PCRE2 has DISPATCHED on `+` and
 * is complaining about what followed, which is recognition. Bucketing 129 with
 * 111 would make this check demand that pcrec refuse `(?+`, which is the
 * misattribution Q2 exists to remove. */

#define PCRE2_NO_SUCH_CONSTRUCT(ec) ((ec) == 111 || (ec) == 141)

/* Does pcrec's answer for `pat` PROMISE A MODULE? That is the tier-2 question
 * D26 makes exact, and the only one an external oracle can pose here: libpcre2
 * can say a construct exists, never that pcrec should call its module
 * 'recursion'. Which module is tests/reject/'s job, as it has always been. */
static bool pcrec_promises_module(const char *pat)
{
    char msg[256];
    if (pcrec_try(pat, msg, sizeof msg) == 0) return true;   /* implemented is stronger */
    return strstr(msg, "requires module") != NULL;
}

/* Completions after `(?<byte>`, generated rather than listed. A byte counts as
 * recognised if ANY completion gets past the dispatch, because several
 * constructs are errors in isolation — `(?P)` is error 141 while `(?P<n>a)`
 * compiles — and a single completion would under-count exactly the bytes this
 * check is about. */
static const char *const Q2_COMPLETIONS[] = {
    ")", "a)", ":a)", "=a)", "!a)", "<n>a)", "'n'a)", "1)", "n>a)", ">n)",
    "-i)", "i)", "i:a)", "{1})", "&n)", "(1)a|b)", "R)", "0)", "+1)", "[a]])",
    "*a)", "#c)", "C1)", "|a)", "^)", "=n)", "<=a)", "<!a)", "n)", "1a)",
};

static void check_group_bytes(void)
{
    int n_recognised = 0, n_not = 0, mismatches = 0;
    unsigned long long seth = SET_HASH_INIT;
    size_t probes = 0;

    for (int b = 1; b < 256; b++) {
        bool p2_recognised = false, pcrec_module = false;

        for (size_t i = 0; i < sizeof Q2_COMPLETIONS / sizeof Q2_COMPLETIONS[0]; i++) {
            char pat[64];
            int len = snprintf(pat, sizeof pat, "(?%c%s", b, Q2_COMPLETIONS[i]);
            if (len < 0 || (size_t)len >= sizeof pat) continue;
            seth = set_hash(seth, pat);
            probes++;
            if (!PCRE2_NO_SUCH_CONSTRUCT(pcre2_try(pat, (size_t)len, NULL, 0)))
                p2_recognised = true;
            if (pcrec_promises_module(pat)) pcrec_module = true;
        }

        if (p2_recognised) n_recognised++; else n_not++;

        if (p2_recognised != pcrec_module) {
            if (mismatches < 12)
                bad("(? byte differential: byte 0x%02x ('%c') — libpcre2 %s a construct, "
                    "pcrec %s a module. An over-promise here is Q2's defect returning; "
                    "an under-promise is a construct pcrec has stopped recognising.",
                    b, (b >= 32 && b < 127) ? b : '?',
                    p2_recognised ? "HAS" : "has NO",
                    pcrec_module ? "promises" : "promises NO");
            mismatches++;
        }
    }

    char line[224];
    snprintf(line, sizeof line,
             "(? byte differential: %zu probes over 255 bytes — %d bytes are constructs, "
             "%d are not, and pcrec agrees on every one", probes, n_recognised, n_not);
    if (mismatches == 0) ok(line); else printf("  %s (%d mismatches)\n", line, mismatches);

    /* LIVENESS, in both directions. "All 255 agree" is also what a doorway that
     * promises a module for everything would print if this check were reading
     * the wrong thing — which is the near-miss Q1's sweep_verb() was rewritten
     * for. Pin BOTH populations: 38 real constructs and 217 non-constructs,
     * measured against libpcre2 10.46. A PCRE2 upgrade moving either is a tier-2
     * finding under D26, not drift to wave through. */
    if (n_recognised != 38 || n_not != 217)
        bad("(? byte differential: libpcre2 now recognises %d bytes and refuses %d "
            "(expected 38 and 217). If a PCRE2 upgrade added a construct after `(?`, "
            "that is a TIER 2 finding: give it a row, do not relax this number.",
            n_recognised, n_not);
    else
        ok("(? byte differential: libpcre2's own populations are unchanged (38 constructs, 217 not)");

    expect_set("(? byte differential", seth, 0x2cefbc6df53a8337ULL);
}

/* ---- Q2: the option RUN, not just its first byte ----------------------- */

/* Splitting the catch-all into eleven letter rows fixed the BYTE and left the
 * same over-promise one level down: `(?iZ)` is PCRE2 error 111 and pcrec still
 * promised module 'modifiers', because the row was chosen by the first byte and
 * nothing read the rest. This sweep is what refuses to let that come back —
 * and it is what found it, while it was being written. */

/* The alphabet is every option-relevant byte PLUS bytes that are not, so the
 * sweep sees both answers. The two TERMINATORS are excluded on purpose and the
 * exclusion is asserted below rather than left implicit: a run containing `)`
 * ends the group early, so `(?))` is a well-formed option group followed by a
 * stray `)` — libpcre2 error 122, about a position this doorway does not own. */
static const char Q2_RUN_ALPHA[] = "JUaimnrsxDPSTW-^ZqQ0.";

static void check_option_runs(void)
{
    int mismatches = 0, n_valid = 0, n_invalid = 0;
    unsigned long long seth = SET_HASH_INIT;
    size_t probes = 0;
    const size_t na = sizeof Q2_RUN_ALPHA - 1;

    for (size_t i = 0; i < na; i++)
        if (Q2_RUN_ALPHA[i] == ')' || Q2_RUN_ALPHA[i] == ':')
            bad("option-run alphabet contains a terminator ('%c'), which makes the "
                "probe a group followed by stray text rather than a run",
                Q2_RUN_ALPHA[i]);

    /* Runs of length 0..3 over the alphabet, in both terminator shapes. Length
     * 3 is where the `a`-sub-option rule and the one-hyphen rule interact
     * (`aP-i`, `i-aP`, `^aP`), which is why two would not be enough. */
    char run[4];
    for (int len = 0; len <= 3; len++) {
        int total = 1;
        for (int k = 0; k < len; k++) total *= (int)na;
        for (int idx = 0; idx < total; idx++) {
            int v = idx;
            for (int k = 0; k < len; k++) { run[k] = Q2_RUN_ALPHA[v % na]; v /= (int)na; }
            run[len] = 0;

            static const char *const shapes[] = {"(?%s)", "(?%s:a)"};
            for (size_t sh = 0; sh < 2; sh++) {
                char pat[32];
                int n = snprintf(pat, sizeof pat, shapes[sh], run);
                if (n < 0 || (size_t)n >= sizeof pat) continue;
                seth = set_hash(seth, pat);
                probes++;

                /* RECOGNITION, not compilation — the same bar the byte and
                 * tail sweeps use, and it has to be. `(?i-m-s)` is error 194,
                 * a MALFORMED option setting, and `(?0J)` is error 114, a
                 * malformed recursion call: both are constructs PCRE2 has, so a
                 * module is owed for both. Asking "does it compile" here
                 * demanded that pcrec refuse them, and reported 967 mismatches
                 * that were the check's error rather than the parser's. */
                bool p2_recognised = !PCRE2_NO_SUCH_CONSTRUCT(pcre2_try(pat, (size_t)n, NULL, 0));
                bool promised = pcrec_promises_module(pat);
                if (p2_recognised) n_valid++; else n_invalid++;

                if (p2_recognised != promised) {
                    if (mismatches < 12)
                        bad("option run: '%s' — libpcre2 %s a construct, pcrec %s a "
                            "module. The run is the construct; a row keyed on its "
                            "first byte cannot see this.",
                            pat, p2_recognised ? "HAS" : "has NO",
                            promised ? "promises" : "promises NO");
                    mismatches++;
                }
            }
        }
    }

    char line[224];
    snprintf(line, sizeof line,
             "option runs: %zu probes over runs of length 0-3 — %d are constructs "
             "libpcre2 has, %d are not, pcrec agrees on every one", probes, n_valid, n_invalid);
    if (mismatches == 0) ok(line); else printf("  %s (%d mismatches)\n", line, mismatches);

    /* Both buckets must be large. A sweep where every run is invalid would agree
     * with a doorway that refuses everything, and would read as coverage. */
    if (n_valid < 100 || n_invalid < 100)
        bad("option runs: buckets are %d valid / %d invalid — one of them is nearly "
            "empty, so agreement is cheap and this sweep is not measuring the rule",
            n_valid, n_invalid);
    else
        ok("option runs: both verdict buckets are well populated, so agreement is not vacuous");

    expect_set("option runs", seth, 0xd502f808e522c30dULL);
}

/* ---- Q2/SR-9: the TAIL sweeps ------------------------------------------
 *
 * The gap tests/registry/CLAUDE.md has named since R5: every sweep here varies
 * ONE byte, so `(?P=` versus `(?P<` was invisible to all of them. SR-9's tail
 * is the fix in the parser; this is the fix in the check. */

struct TailPrefix { const char *pfx; const char *lead; const char *why; };

static void check_group_tails(void)
{
    static const struct TailPrefix PREFIXES[] = {
        {"P", "",       "(?P< (?P= and (?P> are three modules; every other tail is error 141"},
        {"<", "",       "(?<= (?<! and (?<* are lookaround; every other tail is a named group"},
        {"+", "(a)(a)", "every tail is a relative subroutine call; non-digits are error 129"},
        {"-", "(a)(a)", "digits are subroutine calls, option letters are settings"},
    };
    static const char *const TAILCOMP[] = {
        ")", "a)", "n>a)", "1)", "=a)", ":a)", "i)", "n)", "]])", "'n')",
    };

    unsigned long long seth = SET_HASH_INIT;
    size_t probes = 0;
    int total_mismatch = 0, live_prefixes = 0;

    for (size_t p = 0; p < sizeof PREFIXES / sizeof PREFIXES[0]; p++) {
        int recognised = 0, refused = 0, mismatches = 0;

        for (int b = 1; b < 256; b++) {
            bool p2_recognised = false, pcrec_module = false;

            for (size_t i = 0; i < sizeof TAILCOMP / sizeof TAILCOMP[0]; i++) {
                char pat[64];
                int n = snprintf(pat, sizeof pat, "%s(?%s%c%s",
                                 PREFIXES[p].lead, PREFIXES[p].pfx, b, TAILCOMP[i]);
                if (n < 0 || (size_t)n >= sizeof pat) continue;
                seth = set_hash(seth, pat);
                probes++;
                if (!PCRE2_NO_SUCH_CONSTRUCT(pcre2_try(pat, (size_t)n, NULL, 0)))
                    p2_recognised = true;
                if (pcrec_promises_module(pat)) pcrec_module = true;
            }

            if (p2_recognised) recognised++; else refused++;
            if (p2_recognised != pcrec_module) {
                if (total_mismatch < 12)
                    bad("tail sweep (?%s: byte 0x%02x ('%c') — libpcre2 %s a construct, "
                        "pcrec %s a module. %s",
                        PREFIXES[p].pfx, b, (b >= 32 && b < 127) ? b : '?',
                        p2_recognised ? "HAS" : "has NO",
                        pcrec_module ? "promises" : "promises NO", PREFIXES[p].why);
                mismatches++;
                total_mismatch++;
            }
        }

        char line[256];
        snprintf(line, sizeof line, "tail sweep (?%s: 255 tails — %d are constructs, %d are not",
                 PREFIXES[p].pfx, recognised, refused);
        if (mismatches == 0) ok(line);

        /* A prefix where libpcre2 answers the SAME for every tail cannot detect
         * anything by agreement, and saying so is the point: `(?<` is that case
         * — every tail is either a lookbehind or a name — so its module split is
         * pinned in tests/reject/ and NOT here. Counting how many prefixes are
         * live stops this whole sweep from quietly becoming that. */
        if (recognised > 0 && refused > 0) live_prefixes++;
    }

    if (live_prefixes < 2)
        bad("tail sweeps: only %d prefix(es) have both verdict buckets populated. "
            "A sweep where libpcre2 answers alike for every tail agrees with any "
            "doorway at all and is not evidence.", live_prefixes);
    else {
        char line[192];
        snprintf(line, sizeof line,
                 "tail sweeps: %d of 4 prefixes have both buckets populated (%zu probes)",
                 live_prefixes, probes);
        ok(line);
    }

    expect_set("tail sweeps", seth, 0x1884f2f7916a9955ULL);
}

int main(void)
{
    char why[512], ver[64];

    if (pcre2_abi_load(&pcre2, why, sizeof why) != PCRE2_ABI_OK) {
        printf("SKIP: pcre2_check (PC-3): %s\n", why);
        printf("SKIP: the registry's EXTERNAL checks did not run. Everything "
               "else in `make test` compares pcrec with pcrec.\n");
        printf("SKIP: install the PCRE2 8-bit runtime (Debian/Ubuntu package "
               "'libpcre2-8-0') to enable them.\n");
        return 0;
    }

    pcre2_abi_version(&pcre2, ver, sizeof ver);
    const char *path = pcre2_abi_path(&pcre2);
    printf("== registry vs libpcre2 (PC-3) ==\n");
    printf("  libpcre2 version: %s\n", ver);
    printf("  library path:     %s\n", path ? path : "(unknown)");
    printf("  compile options:  0 (no PCRE2_UTF, no PCRE2_UCP, no PCRE2_CASELESS)\n");

    check_rows();

    int runs = 0;
    if (!path || !pool_from_library(path, &runs)) {
        bad("could not read '%s' to generate candidate verb names. The pool "
            "would fall back to pcrec's own table, which is exactly the "
            "circularity this part exists to break.", path ? path : "(unknown)");
    } else {
        printf("  candidate pool: %d ASCII runs in %s, expanded to prefixes "
               "and suffixes\n", runs, path);
    }
    pool_from_mutations();
    pool_from_bytes();
    pool_from_lengths();
    check_verb_names();
    check_class_brackets();
    check_class_delim_bytes();
    check_posix_names();
    check_posix_positions();
    check_embedded_nul();
    check_group_bytes();
    check_option_runs();
    check_group_tails();

    printf("\n== Summary (PC-3) ==\nchecks passed: %d\nchecks failed: %d\n", pass, fail);
    return fail ? 1 : 0;
}
