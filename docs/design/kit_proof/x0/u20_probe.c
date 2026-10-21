/* u20_probe.c: docs/dev/upstream_issues.md U20. libpcre2-8 under
 * PCRE2_MATCH_INVALID_UTF, a startoffset at an invalid UTF-8 sequence, with
 * and without PCRE2_ANCHORED. pcre2unicode(3) "MATCHING IN INVALID UTF
 * STRINGS" documents the skip ("that sequence is skipped, and the match
 * starts at the next valid UTF character"); this probe shows what ANCHORED
 * does with it (the anchor moves with the skip), next to the controls.
 *
 *   gcc -O2 -std=gnu11 -o build/x0/u20_probe docs/design/kit_proof/x0/u20_probe.c -lpcre2-8
 *   build/x0/u20_probe > docs/design/kit_proof/x0/out/u20_probe.txt
 */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <string.h>

static void show(const char *pat, uint32_t copt, const char *subj, size_t n,
                 size_t off, uint32_t mopt, const char *label)
{
    int ec; PCRE2_SIZE eo;
    pcre2_code *re = pcre2_compile((PCRE2_SPTR)pat, PCRE2_ZERO_TERMINATED, copt, &ec, &eo, NULL);
    printf("%-34s %-24s subj=", label, pat);
    for (size_t i = 0; i < n; i++)
        printf((unsigned char)subj[i] < 0x20 || (unsigned char)subj[i] >= 0x7f ? "\\x%02X" : "%c",
               (unsigned char)subj[i]);
    printf(" off=%zu %s%s: ", off, (copt & PCRE2_MATCH_INVALID_UTF) ? "MIU" : (copt & PCRE2_UTF) ? "UTF" : "bytes",
           (mopt & PCRE2_ANCHORED) ? "+ANCHORED" : "");
    if (!re) { printf("compile error %d\n", ec); return; }
    pcre2_match_data *md = pcre2_match_data_create_from_pattern(re, NULL);
    int rc = pcre2_match(re, (PCRE2_SPTR)subj, n, off, mopt, md, NULL);
    if (rc >= 0 || rc == PCRE2_ERROR_PARTIAL) {
        PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
        printf("%s (%zu,%zu)\n", rc == PCRE2_ERROR_PARTIAL ? "PARTIAL" : "match", ov[0], ov[1]);
    } else
        printf("rc %d\n", rc);
    pcre2_match_data_free(md);
    pcre2_code_free(re);
}

int main(void)
{
    char v[64];
    pcre2_config(PCRE2_CONFIG_VERSION, v);
    printf("# libpcre2-8 %s\n", v);
    const uint32_t MIU = PCRE2_UTF | PCRE2_MATCH_INVALID_UTF, UTF = PCRE2_UTF;
    const uint32_t A = PCRE2_ANCHORED;
    /* the finding: the anchored match starts PAST the leading invalid byte */
    show("a", MIU, "\x80" "a", 2, 0, A, "finding");
    show("a", MIU | A, "\x80" "a", 2, 0, 0, "finding (compile-time ANCHORED)");
    show("abc", MIU, "\xff\xfe" "abc", 5, 0, A, "finding (two invalid bytes)");
    show("a", MIU, "\xc3" "a", 2, 0, A, "finding (truncated lead byte)");
    /* the documented skip without ANCHORED: same answer */
    show("a", MIU, "\x80" "a", 2, 0, 0, "documented skip, unanchored");
    /* controls */
    show("a", MIU, "ba", 2, 0, A, "control: valid byte, no skip");
    show("a", MIU, "\x80" "a", 2, 1, A, "control: offset at the valid char");
    show("a", UTF, "\x80" "a", 2, 0, A, "control: UTF without MIU");
    show("a", 0, "\x80" "a", 2, 0, A, "control: no UTF");
    show("^a", MIU, "\x80" "a", 2, 0, 0, "control: ^ is not moved");
    show("\\Ga", MIU, "\x80" "a", 2, 0, 0, "\\G after the skip");
    /* the partial form x0oracle met */
    show("(?(DEFINE)(?<g>a))(?&g)", MIU, "\x80", 1, 0, A | PCRE2_PARTIAL_HARD, "partial at the skip point");
    return 0;
}
