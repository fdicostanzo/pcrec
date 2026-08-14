/* tests/probes/probe_subst.c — M4-SUBST design-measurement probe.
 *
 * PURPOSE. docs/design/subst_template_design.md states a capture-offset
 * contract and a template language. Both restate semantics that PCRE2 owns,
 * and this project's standing rule is that fiddly semantics are MEASURED
 * against libpcre2, never read from documentation alone (the Q2/K4 lesson,
 * restated in the [PC-5] row). This probe is the evidence behind every
 * "MEASURED" claim in that note.
 *
 * TWO THINGS THIS PROBE HAS TO ESTABLISH BEHAVIOURALLY, not read:
 *
 * 1. THE OPTION BITS. There is no pcre2.h on this box (runtime package only —
 *    see ../fuzz/pcre2_abi.h), so the PCRE2_SUBSTITUTE_* constants are not
 *    available to include. They are hand-written below FROM MEMORY OF THE
 *    DOCUMENTATION, which is exactly the kind of claim this project does not
 *    trust. So section 0 CONFIRMS EACH BIT BY ITS EFFECT before any later
 *    section uses it (probe_uprops.c set this precedent for
 *    PCRE2_EXTRA_BAD_ESCAPE_IS_LITERAL). A bit whose confirmation cell fails
 *    is reported as UNCONFIRMED and every result depending on it is suspect.
 *
 * 2. THE ERROR NUMBERS. Likewise not includable. They are read back from
 *    pcre2_get_error_message_8, so the probe prints the LIBRARY'S OWN text
 *    next to each number rather than asserting a remembered mapping.
 *
 * PREDICTOR — stated before the first run, per tests/probes/CLAUDE.md's
 * closing method. The design note was drafted against these predictions; a
 * refuted cell is a note correction, and is marked as such in the output.
 *
 *   P1  $0 is the whole match, in CORE (no EXTENDED). [design: $0 is core]
 *   P2  A reference to a group number ABOVE the pattern's group count is a
 *       substitute-time ERROR by default (this is the AOT win the note
 *       claims: pcrec makes it a compile-time error).
 *   P3  ...and PCRE2_SUBSTITUTE_UNKNOWN_UNSET demotes that error to
 *       "treat as unset".
 *   P4  A group that EXISTS but did not participate renders as EMPTY by
 *       default (no error, no option needed).  <-- most likely to be refuted
 *   P5  $$ is a literal $; a bare $ before a non-digit non-{ is an error.
 *   P6  \u \l \U \L \E and ${n:-default} / ${n:+yes:no} ALL require EXTENDED,
 *       and are errors without it.
 *   P7  Backslash escapes in the replacement (\n, \x41) require EXTENDED;
 *       without it a backslash is LITERAL.
 *   P8  OVERFLOW_LENGTH returns the NOMEMORY error and writes the required
 *       length, INCLUDING room for a terminating NUL.
 *   P9  On success *outlengthptr is the length EXCLUDING the NUL, and the
 *       buffer IS NUL-terminated.
 *   P10 Global mode's empty-match rule reproduces the pcre2_match loop: an
 *       empty match at the position where the previous match ENDED is retried
 *       with NOTEMPTY_ATSTART|ANCHORED, and on failure the position advances
 *       by one and the skipped character is copied through.
 *   P11 An unset group's ovector pair reads as PCRE2_UNSET (~(PCRE2_SIZE)0)
 *       in BOTH slots.
 *   P12 REPLACEMENT_ONLY emits only the replacements, not the unmatched text.
 *
 * BUILD (per tests/probes/CLAUDE.md):
 *   TMPDIR=/var/tmp gcc -I tests/fuzz -o /var/tmp/probe_subst \
 *       tests/probes/probe_subst.c -ldl
 *
 * NOT part of `make test`. Archive its output with scripts/measure.sh (D35).
 */

#define _GNU_SOURCE
#include "pcre2_abi.h"
#include <stdlib.h>

/* ------------------------------------------------------------------ *
 * The substitute slice of the ABI, dlsym'd on top of the shared shim.
 *
 * Deliberately NOT added to ../fuzz/pcre2_abi.h: that header's loader
 * treats a missing symbol as a hard failure for ALL its consumers, and
 * pcre2_check.c (inside `make test`) is one of them. A probe-only extra
 * symbol is resolved probe-side, which is the same shape pcre2_abi_version()
 * already uses for pcre2_config_8.
 * ------------------------------------------------------------------ */
typedef int (*fn_substitute)(const pcre2_code_8 *code, PCRE2_SPTR subject,
    PCRE2_SIZE length, PCRE2_SIZE startoffset, uint32_t options,
    pcre2_match_data_8 *match_data, pcre2_match_context_8 *mcontext,
    PCRE2_SPTR replacement, PCRE2_SIZE rlength,
    unsigned char *outputbuffer, PCRE2_SIZE *outlengthptr);
typedef int (*fn_substring_nametable_scan)(const pcre2_code_8 *code,
    PCRE2_SPTR name, PCRE2_SPTR *first, PCRE2_SPTR *last);
typedef int (*fn_pattern_info)(const pcre2_code_8 *code, uint32_t what,
    void *where);

/* Option bits: REMEMBERED, then confirmed by effect in section 0. */
#define SUB_GLOBAL           0x00000100u
#define SUB_EXTENDED         0x00000200u
#define SUB_UNSET_EMPTY      0x00000400u
#define SUB_UNKNOWN_UNSET    0x00000800u
#define SUB_OVERFLOW_LENGTH  0x00001000u
#define SUB_LITERAL          0x00008000u
#define SUB_MATCHED          0x00010000u
#define SUB_REPLACEMENT_ONLY 0x00020000u

#define INFO_CAPTURECOUNT    0x00000004u  /* remembered; sanity-checked below */

static Pcre2Abi abi;
static fn_substitute                sub_fn;
static fn_substring_nametable_scan  name_fn;
static fn_pattern_info              info_fn;

#define OUTBUF 512

/* One substitution cell. Returns the library's return value; fills `out`
 * with the produced text (when the call succeeded) or the library's own
 * error message (when it did not), so the two are never confused. */
static int cell(const char *pattern, const char *subject, const char *repl,
                uint32_t sub_opts, uint32_t comp_opts,
                char *out, size_t outsz, PCRE2_SIZE *outlen_seen,
                size_t bufcap)
{
    int errcode = 0; PCRE2_SIZE erroff = 0;
    pcre2_code_8 *re = abi.compile((PCRE2_SPTR)pattern, strlen(pattern),
                                   comp_opts, &errcode, &erroff, NULL);
    if (!re) {
        unsigned char m[256]; m[0] = 0;
        abi.get_error_message(errcode, m, sizeof m);
        snprintf(out, outsz, "<pattern rejected: %d %s>", errcode, (char *)m);
        return -10000;
    }
    pcre2_match_data_8 *md = abi.match_data_create(64, NULL);
    unsigned char buf[OUTBUF];
    memset(buf, '@', sizeof buf);            /* poison: shows non-writes */
    PCRE2_SIZE blen = bufcap ? bufcap : sizeof buf;
    int rc = sub_fn(re, (PCRE2_SPTR)subject, strlen(subject), 0, sub_opts,
                    md, NULL, (PCRE2_SPTR)repl, strlen(repl), buf, &blen);
    if (outlen_seen) *outlen_seen = blen;
    if (rc < 0) {
        unsigned char m[256]; m[0] = 0;
        abi.get_error_message(rc, m, sizeof m);
        snprintf(out, outsz, "ERR %d (%s)", rc, (char *)m);
    } else {
        /* Print exactly blen bytes, then show whether byte[blen] is NUL —
         * P9's half about termination is only answerable by looking. */
        size_t k = 0;
        for (PCRE2_SIZE i = 0; i < blen && k + 8 < outsz; i++) {
            unsigned char c = buf[i];
            if (c >= 32 && c < 127) out[k++] = (char)c;
            else k += (size_t)snprintf(out + k, outsz - k, "\\x%02X", c);
        }
        out[k] = 0;
        snprintf(out + k, outsz - k, "|rc=%d|len=%zu|term=%s", rc,
                 (size_t)blen,
                 blen < sizeof buf ? (buf[blen] == 0 ? "NUL" : "not-NUL")
                                   : "n/a");
    }
    abi.match_data_free(md);
    abi.code_free(re);
    return rc;
}

static void show(const char *label, const char *pattern, const char *subject,
                 const char *repl, uint32_t opts)
{
    char out[OUTBUF];
    cell(pattern, subject, repl, opts, 0, out, sizeof out, NULL, 0);
    printf("  %-34s /%s/ on \"%s\" repl \"%s\"\n      -> %s\n",
           label, pattern, subject, repl, out);
}

/* ------------------------------------------------------------------ */

static int confirm(const char *bitname, uint32_t bit, const char *pattern,
                   const char *subject, const char *repl,
                   const char *expect_contains)
{
    char out[OUTBUF];
    cell(pattern, subject, repl, bit, 0, out, sizeof out, NULL, 0);
    int ok = strstr(out, expect_contains) != NULL;
    printf("  %-22s bit 0x%08X  %-7s  /%s/ \"%s\" \"%s\" -> %s\n",
           bitname, bit, ok ? "CONFIRM" : "**FAIL**",
           pattern, subject, repl, out);
    return ok;
}

int main(void)
{
    char why[256];
    if (pcre2_abi_load(&abi, why, sizeof why) != PCRE2_ABI_OK) {
        fprintf(stderr, "probe_subst: %s\n", why);
        return 2;
    }
    dlerror();
    sub_fn  = (fn_substitute)dlsym(abi.handle, "pcre2_substitute_8");
    name_fn = (fn_substring_nametable_scan)
              dlsym(abi.handle, "pcre2_substring_nametable_scan_8");
    info_fn = (fn_pattern_info)dlsym(abi.handle, "pcre2_pattern_info_8");
    if (!sub_fn) {
        fprintf(stderr, "probe_subst: no pcre2_substitute_8: %s\n", dlerror());
        return 2;
    }

    char ver[64]; pcre2_abi_version(&abi, ver, sizeof ver);
    const char *path = pcre2_abi_path(&abi);
    printf("probe_subst — pcre2_substitute semantics for M4-SUBST\n");
    printf("libpcre2 version: %s\n", ver);
    printf("resolved from:    %s\n", path ? path : "(unknown)");
    printf("PCRE2_UNSET is:   %zu (~(PCRE2_SIZE)0)\n\n",
           (size_t)~(PCRE2_SIZE)0);

    /* --- 0. OPTION BITS, CONFIRMED BY EFFECT --------------------------- */
    printf("== 0. option bits confirmed behaviourally (no pcre2.h here) ==\n");
    int all = 1;
    all &= confirm("SUBSTITUTE_GLOBAL", SUB_GLOBAL, "a", "aaa", "X", "XXX");
    all &= confirm("SUBSTITUTE_EXTENDED", SUB_EXTENDED, "(b)", "ab", "\\u$1",
                   "aB");
    all &= confirm("SUBSTITUTE_LITERAL", SUB_LITERAL, "b", "ab", "$0$0",
                   "a$0$0");
    all &= confirm("SUBSTITUTE_REPLACEMENT_ONLY", SUB_REPLACEMENT_ONLY,
                   "b", "abc", "X", "X|");
    all &= confirm("SUBSTITUTE_UNSET_EMPTY", SUB_UNSET_EMPTY,
                   "(a)|(b)", "b", "[$1]", "[]");
    printf("  (UNKNOWN_UNSET and OVERFLOW_LENGTH are confirmed in their own\n"
           "   sections below, where the contrast cell is the confirmation.)\n");
    printf("  ALL CONFIRMED: %s\n\n", all ? "yes" : "NO — see **FAIL** above");

    /* --- 1. WHAT THE TEMPLATE SIDE NEEDS: group count at compile time --- */
    printf("== 1. capture count is a COMPILE-TIME property of the pattern ==\n");
    if (info_fn) {
        const char *pats[] = {"abc", "(a)", "(a)(b)", "(?<x>a)(b)(?:c)",
                              "(a)|(b)", NULL};
        for (int i = 0; pats[i]; i++) {
            int ec = 0; PCRE2_SIZE eo = 0;
            pcre2_code_8 *re = abi.compile((PCRE2_SPTR)pats[i],
                                           strlen(pats[i]), 0, &ec, &eo, NULL);
            uint32_t cc = 0xFFFFFFFFu;
            if (re) info_fn(re, INFO_CAPTURECOUNT, &cc);
            printf("  /%-16s/ capturecount = %u\n", pats[i], cc);
            if (re) abi.code_free(re);
        }
        printf("  (a count that tracks the visible group count confirms the\n"
               "   INFO_CAPTURECOUNT constant too; 0xFFFFFFFF would mean it\n"
               "   did not.)\n");
    } else {
        printf("  pcre2_pattern_info_8 unavailable\n");
    }
    printf("\n");

    /* --- 2. P11: how an UNSET group reads in the ovector ---------------- */
    printf("== 2. P11 — unset group's ovector pair ==\n");
    {
        int ec = 0; PCRE2_SIZE eo = 0;
        pcre2_code_8 *re = abi.compile((PCRE2_SPTR)"(a)|(b)", 7, 0, &ec, &eo,
                                       NULL);
        pcre2_match_data_8 *md = abi.match_data_create(16, NULL);
        int rc = abi.match(re, (PCRE2_SPTR)"b", 1, 0, 0, md, NULL);
        PCRE2_SIZE *ov = abi.get_ovector_pointer(md);
        printf("  /(a)|(b)/ on \"b\": rc=%d (rc is the highest set pair + 1)\n",
               rc);
        for (int i = 0; i < 3; i++)
            printf("    pair %d: [%zu, %zu]%s\n", i, (size_t)ov[2*i],
                   (size_t)ov[2*i+1],
                   ov[2*i] == ~(PCRE2_SIZE)0 ? "   <- PCRE2_UNSET both slots"
                                             : "");
        abi.match_data_free(md);
        abi.code_free(re);
    }
    /* The trap the pcrec contract must NOT inherit: pcre2_match's return
     * value is "highest set pair + 1", and pairs ABOVE it are left at
     * whatever the match data held. Poison the ovector first so an
     * untouched slot is visible as poison rather than as a plausible 0. */
    {
        int ec = 0; PCRE2_SIZE eo = 0;
        pcre2_code_8 *re = abi.compile((PCRE2_SPTR)"(a)(b)?(c)?", 11, 0,
                                       &ec, &eo, NULL);
        pcre2_match_data_8 *md = abi.match_data_create(16, NULL);
        PCRE2_SIZE *ov = abi.get_ovector_pointer(md);
        for (int i = 0; i < 8; i++) ov[i] = (PCRE2_SIZE)0xDEAD;
        int rc = abi.match(re, (PCRE2_SPTR)"a", 1, 0, 0, md, NULL);
        printf("  /(a)(b)?(c)?/ on \"a\": rc=%d (pattern has 3 groups)\n", rc);
        for (int i = 0; i < 4; i++) {
            const char *tag = ov[2*i] == (PCRE2_SIZE)0xDEAD ? "  <- UNTOUCHED (poison survives)"
                            : ov[2*i] == ~(PCRE2_SIZE)0     ? "  <- PCRE2_UNSET" : "";
            printf("    pair %d: [%zu, %zu]%s\n", i, (size_t)ov[2*i],
                   (size_t)ov[2*i+1], tag);
        }
        abi.match_data_free(md);
        abi.code_free(re);
    }
    printf("\n");

    /* --- 3. P1/P5 — core template syntax -------------------------------- */
    printf("== 3. P1/P5 — CORE template syntax (no EXTENDED) ==\n");
    show("P1  $0 whole match", "b+", "abbc", "[$0]", 0);
    show("    $1 numbered", "(b+)", "abbc", "[$1]", 0);
    show("    ${1} braced", "(b+)", "abbc", "[${1}]", 0);
    show("    $name bare", "(?<g>b+)", "abbc", "[$g]", 0);
    show("    ${name} braced", "(?<g>b+)", "abbc", "[${g}]", 0);
    show("P5  $$ literal dollar", "b", "ab", "$$", 0);
    show("P5  bare $ before letter", "b", "ab", "$x", 0);
    show("P5  bare $ at end", "b", "ab", "x$", 0);
    show("    ${1 unterminated", "(b)", "ab", "${1", 0);
    show("    $ before space", "b", "ab", "$ ", 0);
    show("    multi-digit $10", "(b)", "ab", "$10", 0);
    show("    ${10} braced", "(b)", "ab", "${10}", 0);
    printf("\n");

    /* --- 4. P7 — backslash in the replacement without EXTENDED ---------- */
    printf("== 4. P7 — backslash in a CORE replacement ==\n");
    show("P7  \\n without EXTENDED", "b", "ab", "x\\ny", 0);
    show("P7  \\n WITH EXTENDED", "b", "ab", "x\\ny", SUB_EXTENDED);
    show("P7  \\$ without EXTENDED", "b", "ab", "\\$1", 0);
    show("P7  \\$ WITH EXTENDED", "b", "ab", "\\$1", SUB_EXTENDED);
    show("    \\x41 WITH EXTENDED", "b", "ab", "\\x41", SUB_EXTENDED);
    show("    \\q (unknown) EXTENDED", "b", "ab", "\\q", SUB_EXTENDED);
    printf("\n");

    /* --- 5. P2/P3/P4 — the three "no text for this reference" cases ----- */
    printf("== 5. P2/P3/P4 — nonexistent vs unset groups ==\n");
    show("P2  $2 when pattern has 1", "(b)", "ab", "[$2]", 0);
    show("P2  ${nosuch} named", "(?<g>b)", "ab", "[${nosuch}]", 0);
    show("P3  $2/1 + UNKNOWN_UNSET", "(b)", "ab", "[$2]",
         SUB_UNKNOWN_UNSET);
    show("P3  ${nosuch} + UNKNOWN_UNSET", "(?<g>b)", "ab", "[${nosuch}]",
         SUB_UNKNOWN_UNSET);
    show("P4  unset group, default", "(a)|(b)", "b", "[$1]", 0);
    show("P4  unset group, UNSET_EMPTY", "(a)|(b)", "b", "[$1]",
         SUB_UNSET_EMPTY);
    show("    unset + UNKNOWN_UNSET only", "(a)|(b)", "b", "[$1]",
         SUB_UNKNOWN_UNSET);
    show("    both options together", "(a)|(b)", "b", "[$1][$9]",
         SUB_UNKNOWN_UNSET | SUB_UNSET_EMPTY);
    printf("\n");

    /* --- 6. P6 — EXTENDED-only forms ------------------------------------ */
    printf("== 6. P6 — EXTENDED-only template forms ==\n");
    show("P6  \\u core", "(b)", "ab", "\\u$1", 0);
    show("P6  \\u EXTENDED", "(b)", "ab", "\\u$1", SUB_EXTENDED);
    show("    \\l EXTENDED", "(B)", "aB", "\\l$1", SUB_EXTENDED);
    show("    \\U..\\E EXTENDED", "(bc)", "abc", "\\U$1\\E!", SUB_EXTENDED);
    show("    \\L..\\E EXTENDED", "(BC)", "aBC", "\\L$1\\E!", SUB_EXTENDED);
    show("P6  ${n:-default} core", "(a)|(b)", "b", "[${1:-none}]", 0);
    show("P6  ${n:-default} EXTENDED", "(a)|(b)", "b", "[${1:-none}]",
         SUB_EXTENDED);
    show("    ${n:-def} when SET", "(a)|(b)", "a", "[${1:-none}]",
         SUB_EXTENDED);
    show("    ${n:+yes:no} unset", "(a)|(b)", "b", "[${1:+Y:N}]",
         SUB_EXTENDED);
    show("    ${n:+yes:no} set", "(a)|(b)", "a", "[${1:+Y:N}]", SUB_EXTENDED);
    show("    ${n:+yes} one-armed", "(a)|(b)", "a", "[${1:+Y}]", SUB_EXTENDED);
    show("    nested $ in default", "(a)|(b)", "b", "[${1:-<$0>}]",
         SUB_EXTENDED);
    show("    :- on NONEXISTENT group", "(a)", "a", "[${9:-none}]",
         SUB_EXTENDED);
    show("    :- on nonexist + UNK_UNSET", "(a)", "a", "[${9:-none}]",
         SUB_EXTENDED | SUB_UNKNOWN_UNSET);
    printf("\n");

    /* --- 7. P10 — GLOBAL mode's empty-match rule ------------------------ */
    printf("== 7. P10 — global mode, empty matches and advancement ==\n");
    show("    a* on bab", "a*", "bab", "[$0]", SUB_GLOBAL);
    show("    a* on aab", "a*", "aab", "[$0]", SUB_GLOBAL);
    show("    empty-only pattern", "", "abc", "-", SUB_GLOBAL);
    show("    lookahead (?=b)", "(?=b)", "abc", "-", SUB_GLOBAL);
    show("    \\b on 'ab cd'", "\\b", "ab cd", "-", SUB_GLOBAL);
    show("    a|  (alt with empty)", "a|", "bab", "[$0]", SUB_GLOBAL);
    show("    non-global control a*", "a*", "bab", "[$0]", 0);
    show("    global over CRLF text", "$", "a\nb", "<>", SUB_GLOBAL);
    printf("\n");

    /* --- 8. P8/P9 — buffer and length contract ------------------------- */
    printf("== 8. P8/P9 — output buffer sizing contract ==\n");
    {
        char out[OUTBUF]; PCRE2_SIZE seen = 0;
        /* "ab" -> "aXb"? pattern b -> X on "ab" gives "aX", 2 bytes. */
        int rc = cell("b", "ab", "XY", 0, 0, out, sizeof out, &seen, 0);
        printf("  success cell           : %s\n", out);
        printf("    -> *outlengthptr on success = %zu (produced text is %s)\n",
               (size_t)seen, "\"aXY\" = 3 bytes");

        /* Undersized buffer, no OVERFLOW_LENGTH. */
        seen = 0;
        rc = cell("b", "ab", "XY", 0, 0, out, sizeof out, &seen, 2);
        printf("  cap=2, no OVERFLOW_LEN : %s\n", out);
        printf("    -> *outlengthptr = %zu, rc = %d\n", (size_t)seen, rc);

        /* Undersized buffer WITH OVERFLOW_LENGTH: this cell doubles as the
         * behavioural confirmation of the OVERFLOW_LENGTH bit. */
        seen = 0;
        rc = cell("b", "ab", "XY", SUB_OVERFLOW_LENGTH, 0, out, sizeof out,
                  &seen, 2);
        printf("  cap=2, OVERFLOW_LENGTH : %s\n", out);
        printf("    -> *outlengthptr = %zu, rc = %d  (P8: does %zu include\n"
               "       the terminating NUL? produced text is 3 bytes)\n",
               (size_t)seen, rc, (size_t)seen);

        /* Exactly-fitting buffer: is the NUL required to fit? */
        seen = 0;
        rc = cell("b", "ab", "XY", 0, 0, out, sizeof out, &seen, 3);
        printf("  cap=3 (exact text len) : %s\n", out);
        printf("    -> rc = %d  (if this fails, the NUL must fit too)\n", rc);

        seen = 0;
        rc = cell("b", "ab", "XY", 0, 0, out, sizeof out, &seen, 4);
        printf("  cap=4 (text + NUL)     : %s\n", out);
        printf("    -> rc = %d\n", rc);
    }
    printf("\n");

    /* --- 9. P12 + no-match behaviour ------------------------------------ */
    printf("== 9. P12 — REPLACEMENT_ONLY, and the no-match case ==\n");
    show("P12 REPLACEMENT_ONLY", "b", "abc", "[$0]", SUB_REPLACEMENT_ONLY);
    show("P12 + GLOBAL", "[bc]", "abcd", "[$0]",
         SUB_REPLACEMENT_ONLY | SUB_GLOBAL);
    show("    no match, plain", "z", "abc", "X", 0);
    show("    no match, GLOBAL", "z", "abc", "X", SUB_GLOBAL);
    show("    no match, REPL_ONLY", "z", "abc", "X", SUB_REPLACEMENT_ONLY);
    printf("  (rc is the NUMBER OF SUBSTITUTIONS: 0 with the subject copied\n"
           "   through is the documented no-match outcome, not an error.)\n");
    printf("\n");

    /* --- 10. bad-template diagnostics ---------------------------------- */
    printf("== 10. bad-template error surface (D26 tier 3 for pcrec) ==\n");
    show("    lone $ then EOF", "b", "ab", "$", 0);
    show("    ${} empty braces", "(b)", "ab", "${}", 0);
    show("    ${1x} junk in braces", "(b)", "ab", "${1x}", 0);
    show("    ${:-d} no name", "(b)", "ab", "${:-d}", SUB_EXTENDED);
    show("    trailing backslash EXT", "b", "ab", "x\\", SUB_EXTENDED);
    show("    \\E with no \\U", "b", "ab", "x\\Ey", SUB_EXTENDED);
    printf("\n");

    /* --- 11. references into a group the MATCH cannot have -------------- */
    printf("== 11. $n where n exceeds this MATCH but not the PATTERN ==\n");
    show("    ovector large enough", "(a)(b)?", "a", "[$1][$2]", 0);
    show("    ...with UNSET_EMPTY", "(a)(b)?", "a", "[$1][$2]",
         SUB_UNSET_EMPTY);
    printf("  (P4's real shape: a group that EXISTS in the pattern but did\n"
           "   not participate in THIS match. This is the cell pcrec's\n"
           "   compile-time bounds check does NOT remove — bounds checking\n"
           "   is about existence, participation is a run-time fact.)\n");
    printf("\n");

    /* --- 12. grammar corners the template compiler has to reproduce ----- */
    printf("== 12. bare-name termination and case-forcing SCOPE ==\n");
    show("    $g then '-'", "(?<g>b)", "ab", "[$g-]", 0);
    show("    $g then 'x' (name gx?)", "(?<g>b)", "ab", "[$gx]", 0);
    show("    $g then '_'", "(?<g>b)", "ab", "[$g_]", 0);
    show("    $g then digit", "(?<g>b)", "ab", "[$g1]", 0);
    show("    $1 then digit (greedy?)", "(b)", "ab", "[$12]", 0);
    show("    ${1}2 braces stop it", "(b)", "ab", "[${1}2]", 0);
    show("    $0 in EXTENDED default", "(a)|(b)", "b", "[${0:-x}]",
         SUB_EXTENDED);
    show("    \\u before LITERAL text", "b", "ab", "\\uxyz", SUB_EXTENDED);
    show("    \\u before empty group", "(a)|(b)", "b", "\\u$1z",
         SUB_EXTENDED | SUB_UNSET_EMPTY);
    show("    \\U spans a $n boundary", "(b)(c)", "abc", "\\U$1-$2z",
         SUB_EXTENDED);
    show("    \\U..\\E then plain", "(b)(c)", "abc", "\\U$1\\E-$2",
         SUB_EXTENDED);
    show("    \\u inside \\U run", "(bc)", "abc", "\\U$1\\l$1", SUB_EXTENDED);
    show("    \\u\\u doubled", "(bc)", "abc", "\\u\\u$1", SUB_EXTENDED);
    show("    \\u at very end", "b", "ab", "x\\u", SUB_EXTENDED);
    show("    LITERAL beats EXTENDED?", "b", "ab", "\\u$0",
         SUB_LITERAL | SUB_EXTENDED);
    printf("\n");

    /* --- 13. candidate spellings for pcrec's OWN template namespace ----- */
    printf("== 13. SR-10 namespace candidates: is the spelling an ERROR "
           "in PCRE2? ==\n");
    printf("  (The design requires that every pcrec-only form be something\n"
           "   PCRE2 REJECTS today, in BOTH core and EXTENDED. A spelling\n"
           "   PCRE2 accepts with other meaning would make a valid PCRE2\n"
           "   template silently change behaviour under pcrec — the one\n"
           "   outcome D26's compatibility story cannot survive.)\n");
    show("    ${!name} core", "(b)", "ab", "${!upper:1}", 0);
    show("    ${!name} EXTENDED", "(b)", "ab", "${!upper:1}", SUB_EXTENDED);
    show("    $!{...} core", "(b)", "ab", "$!{upper:1}", 0);
    show("    ${#...} EXTENDED", "(b)", "ab", "${#upper:1}", SUB_EXTENDED);
    show("    ${@...} EXTENDED", "(b)", "ab", "${@upper:1}", SUB_EXTENDED);
    show("    ${1!upper} EXTENDED", "(b)", "ab", "${1!upper}", SUB_EXTENDED);
    show("    ${1|upper} EXTENDED", "(b)", "ab", "${1|upper}", SUB_EXTENDED);
    show("    ${1:!upper} EXTENDED", "(b)", "ab", "${1:!upper}", SUB_EXTENDED);
    show("    ${1:^} EXTENDED", "(b)", "ab", "${1:^}", SUB_EXTENDED);
    printf("\n");

    printf("== done ==\n");
    dlclose(abi.handle);
    return 0;
}
