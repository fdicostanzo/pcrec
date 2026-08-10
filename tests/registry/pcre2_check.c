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
typedef struct { RegKind kind; int sel; const char *probe; const char *why; } Wrapper;

static const Wrapper WRAPPERS[] = {
{RK_ESC,   'k', "(?<name>a)\\k<name>", "a backreference by name needs the name declared"},
{RK_ESC,   'g', "(a)\\g{-1}",          "a relative backreference needs a group to its left"},
{RK_ESC,   '1', "(a)\\1",                       "PCRE2 error 115 without the group"},
{RK_ESC,   '2', "(a)(a)\\2",                    "PCRE2 error 115 without the groups"},
{RK_ESC,   '3', "(a)(a)(a)\\3",                 "PCRE2 error 115 without the groups"},
{RK_ESC,   '4', "(a)(a)(a)(a)\\4",              "PCRE2 error 115 without the groups"},
{RK_ESC,   '5', "(a)(a)(a)(a)(a)\\5",           "PCRE2 error 115 without the groups"},
{RK_ESC,   '6', "(a)(a)(a)(a)(a)(a)\\6",        "PCRE2 error 115 without the groups"},
{RK_ESC,   '7', "(a)(a)(a)(a)(a)(a)(a)\\7",     "PCRE2 error 115 without the groups"},
{RK_ESC,   '8', "(a)(a)(a)(a)(a)(a)(a)(a)\\8",  "PCRE2 error 115 without the groups"},
{RK_ESC,   '9', "(a)(a)(a)(a)(a)(a)(a)(a)(a)\\9","PCRE2 error 115 without the groups"},
{RK_GROUP, '(', "(a)(?(1)a|b)",        "a conditional on group 1 needs group 1"},
{RK_GROUP, '&', "(?<name>a)(?&name)",  "recursion by name needs the name declared"},
{RK_GROUP, '1', "(a)(?1)",                       "recursion into a group needs the group"},
{RK_GROUP, '2', "(a)(a)(?2)",                    "recursion into a group needs the group"},
{RK_GROUP, '3', "(a)(a)(a)(?3)",                 "recursion into a group needs the group"},
{RK_GROUP, '4', "(a)(a)(a)(a)(?4)",              "recursion into a group needs the group"},
{RK_GROUP, '5', "(a)(a)(a)(a)(a)(?5)",           "recursion into a group needs the group"},
{RK_GROUP, '6', "(a)(a)(a)(a)(a)(a)(?6)",        "recursion into a group needs the group"},
{RK_GROUP, '7', "(a)(a)(a)(a)(a)(a)(a)(?7)",     "recursion into a group needs the group"},
{RK_GROUP, '8', "(a)(a)(a)(a)(a)(a)(a)(a)(?8)",  "recursion into a group needs the group"},
{RK_GROUP, '9', "(a)(a)(a)(a)(a)(a)(a)(a)(a)(?9)","recursion into a group needs the group"},
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

static const Wrapper *wrapper_for(RegKind k, int sel)
{
    for (size_t i = 0; i < sizeof WRAPPERS / sizeof WRAPPERS[0]; i++)
        if (WRAPPERS[i].kind == k && WRAPPERS[i].sel == sel) return &WRAPPERS[i];
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

    for (int k = 0; k < RK_COUNT; k++) {
        size_t n;
        const RegRow *rows = pcrec_registry((RegKind)k, &n);
        for (size_t i = 0; i < n; i++) {
            const RegRow *r = &rows[i];
            const Wrapper *w = wrapper_for(r->kind, r->sel);
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
    check_embedded_nul();

    printf("\n== Summary (PC-3) ==\nchecks passed: %d\nchecks failed: %d\n", pass, fail);
    return fail ? 1 : 0;
}
