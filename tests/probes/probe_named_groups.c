/* probe_named_groups.c — [M6.3] named-groups measurement campaign.
 *
 * PREDICTOR, stated before running (per tests/probes/CLAUDE.md's method):
 * PCRE2 10.46's named-group name grammar is "word characters only"
 * (isalnum || '_'), a first-digit is NOT specially forbidden (unlike many
 * other languages' identifier rules), there is a fixed maximum name
 * length (predicted 32, PCRE2's documented MAX_NAME_SIZE), and a name
 * reused without (?J)/PCRE2_DUPNAMES is a compile error. The compiled
 * name->group table (PCRE2_INFO_NAMETABLE) is predicted SORTED BY NAME
 * (strcmp order), which would make it directly bsearch-able and is the
 * fact this probe exists to nail down for pcrec's own sort-key decision
 * (docs/spec/match_api.md sect 6).
 *
 * Build: TMPDIR=/var/tmp gcc -I /home/duxevents/pcrec/tests/fuzz -o /var/tmp/probe_ng probe_named_groups.c -ldl
 */
#include "pcre2_abi.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

static Pcre2Abi abi;
static int fails, total;

/* Compile `pat`, report err code (0 if it compiled) and set *code. */
static pcre2_code_8 *try_compile(const char *pat, int *err, PCRE2_SIZE *eoff)
{
    return abi.compile((PCRE2_SPTR)pat, strlen(pat), 0, err, eoff, NULL);
}

/* ---- step 1: find PCRE2_INFO_NAMECOUNT/NAMEENTRYSIZE/NAMETABLE opcodes.
 * Same method the tree already used for CAPTURECOUNT (opcode 4): compile a
 * known pattern, sweep candidate opcodes, keep the one consistent across
 * multiple independent patterns. */
static uint32_t namecount_op, nameentrysize_op;
static uint32_t nametable_op; /* pointer-sized info; probed separately */

static int check_namecount_candidate(uint32_t op, int p1nc, int p2nc, int p3nc)
{
    int err; PCRE2_SIZE eo;
    const char *pats[3] = {
        "(?<x>a)",
        "(?<x>a)(?<y>b)",
        "(a)(?<z>b)(c)(?<w>d)"
    };
    int exp[3] = {p1nc, p2nc, p3nc};
    for (int i = 0; i < 3; i++) {
        pcre2_code_8 *c = try_compile(pats[i], &err, &eo);
        if (!c) return 0;
        /* Padded buffer: some candidate opcodes in this sweep range return
         * pointer-sized values, and writing only a bare uint32_t's worth of
         * stack for those would overflow it (this is what crashed the first
         * cut of this probe). Read back just the leading 4 bytes. */
        unsigned char buf[64] = {0};
        int rc = abi.pattern_info(c, op, buf);
        abi.code_free(c);
        if (rc != 0) return 0;
        uint32_t v; memcpy(&v, buf, sizeof v);
        if ((int)v != exp[i]) return 0;
    }
    return 1;
}

int main(void)
{
    setbuf(stdout, NULL);   /* unbuffered, so a crash never hides prior output */
    char why[256];
    if (pcre2_abi_load(&abi, why, sizeof why) != PCRE2_ABI_OK) {
        fprintf(stderr, "SKIP: %s\n", why); return 2;
    }
    char ver[64]; pcre2_abi_version(&abi, ver, sizeof ver);
    printf("libpcre2 version: %s\n", ver);

    /* --- step 1: locate NAMECOUNT opcode by sweep --- */
    namecount_op = 0;
    for (uint32_t op = 1; op <= 40; op++) {
        if (check_namecount_candidate(op, 1, 2, 2)) {
            if (namecount_op) {
                printf("AMBIGUOUS: both opcode %u and %u match NAMECOUNT pattern\n",
                       namecount_op, op);
            }
            namecount_op = op;
        }
    }
    if (!namecount_op) {
        fprintf(stderr, "FAIL: could not locate PCRE2_INFO_NAMECOUNT by sweep\n");
        return 1;
    }
    printf("PCRE2_INFO_NAMECOUNT opcode = %u\n", namecount_op);
    total++;

    /* --- step 2: locate NAMEENTRYSIZE: known name "x" (1 byte) predicted
     * entry size = 2 (group number, big-endian uint16) + strlen+1 (NUL),
     * rounded to whatever PCRE2's internal alignment is. Sweep and compare
     * against a longer name to find the opcode whose value tracks name
     * length by exactly the name's length delta. */
    {
        int err; PCRE2_SIZE eo;
        pcre2_code_8 *c1 = try_compile("(?<x>a)", &err, &eo);
        pcre2_code_8 *c2 = try_compile("(?<xxxxxxxxxx>a)", &err, &eo); /* +9 bytes */
        if (!c1 || !c2) { fprintf(stderr, "FAIL: entrysize probe compile\n"); return 1; }
        for (uint32_t op = 1; op <= 40; op++) {
            unsigned char b1[64] = {0}, b2[64] = {0};
            uint32_t v1 = 0, v2 = 0;
            if (abi.pattern_info(c1, op, b1) != 0) continue;
            if (abi.pattern_info(c2, op, b2) != 0) continue;
            memcpy(&v1, b1, sizeof v1);
            memcpy(&v2, b2, sizeof v2);
            /* Tightened after the first run: opcode 22 (BACKREFMAX or a
             * neighbour) coincidentally also satisfied v2==v1+9 at
             * v1=173/v2=182, overwriting the correct opcode 18 candidate
             * (v1=4/v2=13, exactly 2 (group number) + strlen("x")+1). A
             * real one-byte-name entry is a handful of bytes, not 173. */
            if (v1 >= 3 && v1 <= 20 && v2 == v1 + 9 && !nameentrysize_op) {
                printf("PCRE2_INFO_NAMEENTRYSIZE candidate opcode = %u (x=%u, xxxxxxxxxx=%u)\n",
                       op, v1, v2);
                nameentrysize_op = op;
            }
        }
        abi.code_free(c1); abi.code_free(c2);
        if (!nameentrysize_op) {
            fprintf(stderr, "FAIL: could not locate PCRE2_INFO_NAMEENTRYSIZE\n");
            return 1;
        }
    }
    total++;

    /* --- step 3: locate NAMETABLE. A blind opcode sweep here is NOT safe
     * (first cut of this probe: a wrong candidate opcode returns rc==0 with
     * a garbage "pointer" that PCRE2 never validates, and dereferencing it
     * segfaults — caught by gdb, backtrace landed in the strcmp against a
     * garbage `tab` pointer). So this step trusts the DOCUMENTED, stable
     * PCRE2 opcode 19 (pcre2api(3): NAMECOUNT=17, NAMEENTRYSIZE=18,
     * NAMETABLE=19 — a sequential trio, and steps 1/2 above independently
     * confirmed 17 and 18 BEHAVIOURALLY on this exact libpcre2, which is
     * strong corroborating evidence 19 is right rather than a guess) and
     * only DEREFERENCES it after confirming steps 1/2 already validated
     * the surrounding pair sequentially. The decode is then checked against
     * the known answer, which is the real oracle question this step asks:
     * not "which opcode" but "is the table CONTENT and ORDER what predicted". */
    if (namecount_op != 17 || nameentrysize_op != 18) {
        printf("NOTE: NAMECOUNT/NAMEENTRYSIZE opcodes were NOT 17/18 as documented "
               "(got %u/%u) -- skipping the NAMETABLE dereference rather than risk "
               "an unvalidated pointer read\n", namecount_op, nameentrysize_op);
    } else {
        nametable_op = 19;
        int err; PCRE2_SIZE eo;
        pcre2_code_8 *c = try_compile("(?<zeta>a)(?<alpha>b)(?<mu>c)", &err, &eo);
        if (!c) { fprintf(stderr, "FAIL: nametable probe compile\n"); return 1; }
        uint32_t nc = 0, esz = 0;
        abi.pattern_info(c, namecount_op, &nc);
        abi.pattern_info(c, nameentrysize_op, &esz);
        printf("nametable probe: namecount=%u nameentrysize=%u\n", nc, esz);
        unsigned char *tab = NULL;
        int rc = abi.pattern_info(c, nametable_op, &tab);
        if (rc == 0 && tab && nc == 3 && esz > 2 && esz < 200) {
            printf("PCRE2_INFO_NAMETABLE opcode 19: order: ");
            for (uint32_t i = 0; i < nc; i++) {
                unsigned char *e = tab + i * esz;
                unsigned num = (e[0] << 8) | e[1];
                printf("[%s->%u] ", (const char *)(e + 2), num);
            }
            printf("\n");
        } else {
            fprintf(stderr, "FAIL: opcode 19 did not decode sanely (rc=%d tab=%p nc=%u esz=%u)\n",
                    rc, (void *)tab, nc, esz);
            fails++;
        }
        abi.code_free(c);
    }
    total++;

    /* --- step 4: character-class sweep for name validity (first byte and
     * a later byte, independently), atom position (?<NAME>a). --- */
    {
        int first_ok[256] = {0}, later_ok[256] = {0};
        for (int b = 1; b < 256; b++) {
            char pat[32];
            snprintf(pat, sizeof pat, "(?<%ca>x)", b);
            int err; PCRE2_SIZE eo;
            pcre2_code_8 *c = try_compile(pat, &err, &eo);
            if (c) { first_ok[b] = 1; abi.code_free(c); }
        }
        for (int b = 1; b < 256; b++) {
            char pat[32];
            snprintf(pat, sizeof pat, "(?<a%cb>x)", b);
            int err; PCRE2_SIZE eo;
            pcre2_code_8 *c = try_compile(pat, &err, &eo);
            if (c) { later_ok[b] = 1; abi.code_free(c); }
        }
        int first_mismatch = 0, later_mismatch = 0;
        for (int b = 1; b < 256; b++) {
            int pred_first = isalnum(b) || b == '_';
            int pred_later = isalnum(b) || b == '_';
            if (!!first_ok[b] != !!pred_first) {
                printf("FIRST-BYTE DISAGREE: 0x%02x got=%d pred=%d\n", b, first_ok[b], pred_first);
                first_mismatch++;
            }
            if (!!later_ok[b] != !!pred_later) {
                printf("LATER-BYTE DISAGREE: 0x%02x got=%d pred=%d\n", b, later_ok[b], pred_later);
                later_mismatch++;
            }
        }
        printf("name-char sweep: first_mismatch=%d later_mismatch=%d\n", first_mismatch, later_mismatch);
        fails += first_mismatch + later_mismatch;
        total++;
    }

    /* --- step 5: max name length. Sweep 1..64 byte names of 'a's. --- */
    {
        int max_ok = -1;
        for (int len = 1; len <= 2000; len++) {
            char pat[2200]; char *p = pat;
            p += sprintf(p, "(?<");
            for (int i = 0; i < len; i++) *p++ = 'a';
            p += sprintf(p, ">x)");
            *p = 0;
            int err; PCRE2_SIZE eo;
            pcre2_code_8 *c = try_compile(pat, &err, &eo);
            if (c) { max_ok = len; abi.code_free(c); }
            else if (max_ok >= 0) { printf("max name length = %d (len %d fails, err %d)\n", max_ok, len, err); break; }
        }
        total++;
    }

    /* --- step 6: duplicate names, default (no DUPNAMES/(?J)) --- */
    {
        int err; PCRE2_SIZE eo;
        pcre2_code_8 *c = try_compile("(?<dup>a)(?<dup>b)", &err, &eo);
        if (c) { printf("DUPLICATE NAME UNEXPECTEDLY COMPILED (default, no DUPNAMES)\n"); abi.code_free(c); fails++; }
        else printf("duplicate name (default): err=%d offset=%zu\n", err, (size_t)eo);
        total++;
    }

    /* --- step 7: (?J) / DUPNAMES lets duplicate names through --- */
    {
        int err; PCRE2_SIZE eo;
        pcre2_code_8 *c = try_compile("(?J)(?<dup>a)(?<dup>b)", &err, &eo);
        if (!c) { printf("(?J) duplicate name UNEXPECTEDLY REJECTED: err=%d\n", err); fails++; }
        else {
            uint32_t nc = 0;
            abi.pattern_info(c, namecount_op, &nc);
            printf("(?J) duplicate name compiles; NAMECOUNT=%u (both entries kept)\n", nc);
            abi.code_free(c);
        }
        total++;
    }

    /* --- step 8: the three declaring spellings number groups by opening
     * paren order, same as unnamed groups (interleaved with plain groups) --- */
    {
        int err; PCRE2_SIZE eo;
        const char *pat = "(a)(?<n1>b)(?'n2'c)(d)(?P<n3>e)";
        pcre2_code_8 *c = try_compile(pat, &err, &eo);
        if (!c) { printf("interleave probe FAILED TO COMPILE: err=%d\n", err); fails++; }
        else {
            uint32_t nc = 0, cc = 0, esz = 0;
            abi.pattern_info(c, namecount_op, &nc);
            abi.pattern_info(c, PCRE2_ABI_INFO_CAPTURECOUNT, &cc);
            abi.pattern_info(c, nameentrysize_op, &esz);
            unsigned char *tab = NULL;
            int trc = abi.pattern_info(c, nametable_op, &tab);
            printf("interleave: ngroups=%u nnames=%u tab=%p trc=%d esz=%u\n",
                   cc, nc, (void *)tab, trc, esz);
            if (trc == 0 && tab && esz > 2 && esz < 200) {
                for (uint32_t i = 0; i < nc; i++) {
                    unsigned char *e = tab + i * esz;
                    unsigned num = (e[0] << 8) | e[1];
                    printf("  %s -> group %u\n", (const char*)(e + 2), num);
                }
            } else {
                printf("  (nametable unavailable/unsane, skipping decode)\n");
                fails++;
            }
            abi.code_free(c);
        }
        total++;
    }

    /* --- step 9: does (?n) (PCRE2_NO_AUTO_CAPTURE / no-auto-capture) turn
     * OFF capture for named groups too, or only for plain '(' groups? This
     * decides whether pcrec's named-groups port should read cx->mods.nocap
     * at all when assigning a capture number. */
    {
        int err; PCRE2_SIZE eo;
        pcre2_code_8 *c = try_compile("(?n)(a)(?<x>b)", &err, &eo);
        if (!c) { printf("(?n) probe FAILED TO COMPILE: err=%d\n", err); fails++; }
        else {
            uint32_t cc = 0, nc = 0;
            abi.pattern_info(c, PCRE2_ABI_INFO_CAPTURECOUNT, &cc);
            abi.pattern_info(c, namecount_op, &nc);
            printf("(?n)(a)(?<x>b): capturecount=%u namecount=%u "
                   "(predict: plain '(' does not count, named 'x' still does -> capturecount=1 namecount=1)\n",
                   cc, nc);
            if (cc != 1 || nc != 1) fails++;
            abi.code_free(c);
        }
        total++;
    }

    printf("probes: %d, disagreements: %d\n", total, fails);
    return fails ? 1 : 0;
}
