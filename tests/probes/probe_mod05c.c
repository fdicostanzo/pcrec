/* probe_mod05c.c — MOD-0.5c port-implementation corners.
 * PREDICTOR, stated before the run:
 *   (?i-i)k  vs "K":  no match (set and unset collect over the run, unset
 *                     wins on the same letter — either model predicts this)
 *   (?-ii)k  vs "K":  MEASUREMENT — unset-then-set: does order in the run
 *                     matter, or do the masks apply as set-then-unset?
 *   (?xsx)[a b] vs " ": MEASUREMENT — is doubled x ADJACENCY-sensitive?
 *                     match = x only (space is a member), no match = xx
 *   (?xaDx)a b vs "ab": MEASUREMENT — same question with an a-sub between
 *   (?xx-x)[a b] vs " ": MEASUREMENT — does -x clear EXTENDED_MORE too?
 *   (?xx-x)a b vs "ab":  companion cell (outside-class skipping off?)
 *   (?^xx)[a b] vs " ": MEASUREMENT — xx after the reset caret
 * Build: gcc -I tests/fuzz -o probe_mod05c probe_mod05c.c -ldl
 */
#include "pcre2_abi.h"
#include <stdio.h>
#include <string.h>

static Pcre2Abi abi;

static void try_match(const char *pat, const char *subj)
{
    int err = 0; PCRE2_SIZE eoff = 0;
    pcre2_code_8 *code = abi.compile((PCRE2_SPTR)pat, strlen(pat), 0,
                                     &err, &eoff, NULL);
    size_t slen = strlen(subj);
    printf("%-16s vs ", pat);
    for (size_t i = 0; i < slen; i++)
        printf(subj[i] >= 0x21 && subj[i] <= 0x7e ? "%c" : "\\x%02x",
               (unsigned char)subj[i]);
    printf("  ");
    if (!code) {
        unsigned char msg[90];
        abi.get_error_message(err, msg, sizeof msg);
        printf("ERR %d  %s\n", err, msg);
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
    try_match("(?i-i)k", "K");
    try_match("(?-ii)k", "K");
    try_match("(?i-i)k", "k");
    try_match("(?xsx)[a b]", " ");
    try_match("(?xsx)a b", "ab");
    try_match("(?xaDx)a b", "ab");
    try_match("(?xaDx)[a b]", " ");
    try_match("(?xx-x)[a b]", " ");
    try_match("(?xx-x)a b", "ab");
    try_match("(?xx-x)a b", "a b");
    try_match("(?^xx)[a b]", " ");
    try_match("(?x-i)a b", "ab");

    /* LANDING-ROUND cells (run at the .5c implementation, originally as a
     * separate scratch probe; consolidated here with their MEASURED
     * outcomes so the evidence is committed):
     *   (?xx)(?x)[a b] vs SP  MATCHED  — a later bare `x` DOWNGRADES an
     *                                    earlier xx (space is a member again)
     *   (?xx)(?s)[a b] vs SP  no match — control: an unrelated set keeps xx
     *   (?x)(?xx)[a b] vs SP  no match — upgrade direction works
     * So the x level is ASSIGNED per run (adjacency-sensitive), never
     * accumulated — pcrec_modport_optrun's per-char rule. */
    try_match("(?xx)(?x)[a b]", " ");
    try_match("(?xx)(?s)[a b]", " ");
    try_match("(?x)(?xx)[a b]", " ");
    return 0;
}
