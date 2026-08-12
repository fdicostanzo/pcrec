/* probe_mod05d.c — MOD-0.5d lexer-boundary cells.
 * PREDICTOR, stated before the run:
 *   (?x)a +      vs "aaa": MATCH [0,3) — skipping happens between an atom
 *                and its quantifier (the deleted-from-token-stream model)
 *   (?x)a + ?    vs "aaa": MATCH [0,1) — the lazy marker also reachable
 *                across skipped bytes
 *   (?x)a{1,\n2} vs "aa":  MEASUREMENT — brace interior under x
 *   (?x)a\n+     vs "aaa": MATCH [0,3) — comment-free newline is skipped,
 *                quantifier attaches
 *   (?x)a#c      vs "a":   MATCH — comment terminated by end of pattern
 *   (?x)a#c\rb   vs "ab":  MEASUREMENT — does 0x0D end a comment at
 *                options=0, or only 0x0A? (NEWLINE convention, DD-11)
 *   (?x)a#c\x85b vs "ab":  MEASUREMENT — NEL as comment terminator
 *   (?x)(? i)a   vs "a":   MEASUREMENT — is the OPTION RUN skippable inside?
 *   (?x)\ +      vs "   ": MATCH — escaped space is an atom, + quantifies it
 *   (?x)[ab] {2} vs "ab":  MEASUREMENT — quantifier after skipped space
 *                after class
 *   (?x)a**      control: double quantifier still an error through skips
 * Build: gcc -I tests/fuzz -o probe_mod05d probe_mod05d.c -ldl
 */
#include "pcre2_abi.h"
#include <stdio.h>
#include <string.h>

static Pcre2Abi abi;

static void tm(const char *pat, const char *subj)
{
    int err = 0; PCRE2_SIZE eoff = 0;
    pcre2_code_8 *code = abi.compile((PCRE2_SPTR)pat, strlen(pat), 0,
                                     &err, &eoff, NULL);
    size_t slen = strlen(subj);
    printf("%-18s vs ", pat);
    for (size_t i = 0; i < slen; i++)
        printf(subj[i] >= 0x21 && subj[i] <= 0x7e ? "%c" : "\\x%02x",
               (unsigned char)subj[i]);
    printf("  ");
    if (!code) {
        unsigned char msg[90];
        abi.get_error_message(err, msg, sizeof msg);
        printf("ERR %d at %zu  %s\n", err, (size_t)eoff, msg);
        return;
    }
    pcre2_match_data_8 *md = abi.match_data_create(8, NULL);
    int rc = abi.match(code, (PCRE2_SPTR)subj, slen, 0, 0, md, NULL);
    if (rc >= 0) {
        PCRE2_SIZE *ov = abi.get_ovector_pointer(md);
        printf("rc=%d MATCH [%zu,%zu)\n", rc, (size_t)ov[0], (size_t)ov[1]);
    } else printf("no match (%d)\n", rc);
    abi.match_data_free(md);
    abi.code_free(code);
}

int main(void)
{
    char why[256];
    if (pcre2_abi_load(&abi, why, sizeof why) != PCRE2_ABI_OK) {
        fprintf(stderr, "SKIP: %s\n", why); return 2;
    }
    tm("(?x)a +", "aaa");
    tm("(?x)a + ?", "aaa");
    tm("(?x)a{1,\n2}", "aa");
    tm("(?x)a\n+", "aaa");
    tm("(?x)a#c", "a");
    tm("(?x)a#c\rb", "ab");
    tm("(?x)a#c\x85" "b", "ab");
    tm("(?x)a#c\nb", "ab");
    tm("(?x)(? i)a", "a");
    tm("(?x)\\ +", "   ");
    tm("(?x)[ab] {2}", "ab");
    tm("(?x)a**", "a");
    tm("(?x)a *", "aaa");
    tm("(?x) ^ a", "a");
    tm("(?x)a | b", "b");
    tm("(?x)( a )( b )", "ab");

    /* LANDING-ROUND cells (consolidated from the implementation-time
     * scratch probes, with their MEASURED outcomes):
     *   (?xx)[ ^a]  vs b MATCHED, vs ^ MATCHED, vs a no match — deletion
     *     precedes the NEGATION check (the leading space vanishes and `^`
     *     negates; matching `^` is consistent with [^a])
     *   (?x)( ?i)a and (?x)( ?:a) — ERR 109 at 6 both: NO skipping between
     *     `(` and `?`; the doorway adjacency is lexical
     *   (?xx)[[: alpha :]] — ERR 130: POSIX bracket names read RAW, the
     *     spaces belong to the (unknown) name
     *   (?xx)[a\t-\tz] vs m MATCHED — deletion precedes RANGE parsing
     *   (?xx)[a\tb] with the \t as a two-byte ESCAPE vs TAB — MATCHED:
     *     escapes SURVIVE deletion; only raw whitespace bytes are deleted
     *     (the corpus's transcription defect, caught at the landing) */
    tm("(?xx)[ ^a]", "b");
    tm("(?xx)[ ^a]", "^");
    tm("(?xx)[ ^a]", "a");
    tm("(?x)( ?i)a", "a");
    tm("(?x)( ?:a)", "a");
    tm("(?xx)[[: alpha :]]", "a");
    tm("(?xx)[a\t-\tz]", "m");
    tm("(?xx)[a\\tb]", "\t");
    return 0;
}
