/* probe_mod05.c — MOD-0.5 scope probes against libpcre2 (module `modifiers`).
 * PREDICTOR, stated before the run (options=0 throughout, C locale):
 *
 *   x vs xx at the class boundary (the D30 §7 hazard):
 *     (?x)[a- ]     err 108  (single x never touches class interior)
 *     (?xx)[a- ]    COMPILES ([a-] after deletion: members {a,-}; ' ' not a member)
 *     (?xx)[a-\ ]   err 108  (escaped space stays significant; range a(0x61)>SP(0x20))
 *     (?xx)[\ -a]   COMPILES (range SP..a)
 *     (?xx)[a\tb]   tab deleted too: members {a,b}
 *     (?x)[a b]     ' ' IS a member (interior untouched)
 *   x outside classes:
 *     (?x)a b       matches "ab" [0,2); does NOT match "a b"
 *     (?x)a\ b      matches "a b" (escaped space literal)
 *     (?x)a#c\nb    matches "ab" (comment to newline)
 *     skipped-byte census over (?x)a<b>b: exactly {09,0A,0B,0C,0D,20} (default
 *       tables' whitespace) — MEASUREMENT, the set is the deliverable
 *     xx-in-class deleted census over (?xx)[<b>x]: exactly {09,20}
 *   brace quantifiers (pcrec_brace_quant_shape's one home cares):
 *     a{1, 2}       MEASUREMENT — 10.43+ may allow spaces at options=0
 *     (?x)a{1, 2}   MEASUREMENT
 *     (?x)a{ 1 , 2 } MEASUREMENT
 *   candidate cheap semantics:
 *     (?s).         census 256/256 (plain . is 255: complement of {0x0A})
 *     (?U)a+ /aaa   lazy: [0,1); (?U)a+? /aaa greedy: [0,3)
 *     (?m)^b /a\nb  MATCH [2,3)
 *     (?n)(a) /a    rc==1 (no capture pair); (?n)(a)\1 err 115
 *     (?n)(?<g>a)(?<g>b)  err 143 (n does not imply J)
 *     (?J)(?<g>a)(?<g>b)  COMPILES; without J err 143
 *     (?i)k vs (?ri)k over 256 single-byte subjects: 0 diffs (C-locale fold
 *       is already ASCII-only, r is a no-op at options=0) — MEASUREMENT
 *     (?aD)\d census == \d census == 10 members (no-op at options=0)
 *     (?aW)\w, (?aS)\s censuses == unprefixed (no-op at options=0)
 *   smoke (semantics already measured 17/17 at PARSE-1, two cells only):
 *     (?i:a)b /Ab   MATCH; /AB no match
 *     (?i)a(?^)a /Aa MATCH; /AA no match
 *
 * Build: gcc -I tests/fuzz -o probe_mod05 probe_mod05.c -ldl
 *
 * MEASURED (2026-08-12, libpcre2 10.46; post-run notes — the predictions
 * above are as stated before the run):
 *   - every class-boundary cell as predicted; xx deletes exactly {09,20}.
 *   - the x-skip census below has a TEMPLATE FLAW: `(?x)a<b>b` matching "ab"
 *     is also satisfied by quantifier bytes (a*b, a+b, a?b), so 2a/2b/3f are
 *     false positives. probe_mod05b.c re-runs it with a no-x control column;
 *     the controlled answer is {09,0A,0B,0C,0D,20,85} — note 0x85 (NEL),
 *     which \s (census 6) does NOT contain: x-mode's skip set is not \s.
 *   - a{1, 2} and every spaced brace form COMPILE at options=0 as
 *     QUANTIFIERS (10.43+ rule); pcrec_brace_quant_shape already accepts
 *     space/tab (R16), and pcrec's emitted matcher agrees on all three
 *     discriminating subjects — no divergence.
 *   - (?s). census 256; (?U) swaps greed both directions; (?m)^ line-anchors;
 *     (?n) uncaptures plain parens (rc 2->1) and does NOT imply J (err 143).
 *   - (?ri) vs (?i): 0 diff cells over 256x256; all four a-sub pairs census-
 *     identical at options=0 — r and a<sub> are MEASURED no-ops in this mode.
 *   - (?^) reset scope (probe_mod05b.c): unsets i,m,n,s,x,xx; U and J
 *     SURVIVE (?^) — "unset imnsx" is the measured rule, not "unset all".
 */
#include "pcre2_abi.h"
#include <stdio.h>
#include <string.h>

static Pcre2Abi abi;

static pcre2_code_8 *comp(const char *pat)
{
    int err = 0; PCRE2_SIZE eoff = 0;
    return abi.compile((PCRE2_SPTR)pat, strlen(pat), 0, &err, &eoff, NULL);
}

static void verdict(const char *pat)
{
    int err = 0; PCRE2_SIZE eoff = 0;
    pcre2_code_8 *code = abi.compile((PCRE2_SPTR)pat, strlen(pat), 0,
                                     &err, &eoff, NULL);
    printf("%-20s ", pat);
    if (!code) {
        unsigned char msg[90];
        abi.get_error_message(err, msg, sizeof msg);
        printf("ERR %3d at %zu  %s\n", err, (size_t)eoff, msg);
        return;
    }
    printf("COMPILES\n");
    abi.code_free(code);
}

/* Match and print rc + span; subject rendered escaped for the log. */
static void try_match(const char *pat, const char *subj, size_t slen)
{
    pcre2_code_8 *code = comp(pat);
    printf("%-18s vs ", pat);
    for (size_t i = 0; i < slen; i++)
        printf(subj[i] >= 0x21 && subj[i] <= 0x7e ? "%c" : "\\x%02x",
               (unsigned char)subj[i]);
    printf("  ");
    if (!code) { puts("(no compile)"); return; }
    pcre2_match_data_8 *md = abi.match_data_create(8, NULL);
    int rc = abi.match(code, (PCRE2_SPTR)subj, slen, 0, 0, md, NULL);
    if (rc >= 0) {
        PCRE2_SIZE *ov = abi.get_ovector_pointer(md);
        printf("rc=%d MATCH [%zu,%zu)\n", rc, (size_t)ov[0], (size_t)ov[1]);
    } else printf("no match (%d)\n", rc);
    abi.match_data_free(md);
    abi.code_free(code);
}
#define TM(p, s) try_match((p), (s), strlen(s))

/* Does `code` match the single byte b? */
static int hits(pcre2_code_8 *code, int b)
{
    unsigned char s[1] = { (unsigned char)b };
    pcre2_match_data_8 *md = abi.match_data_create(4, NULL);
    int rc = abi.match(code, s, 1, 0, 0, md, NULL);
    abi.match_data_free(md);
    return rc >= 0;
}

int main(void)
{
    char why[256];
    if (pcre2_abi_load(&abi, why, sizeof why) != PCRE2_ABI_OK) {
        fprintf(stderr, "SKIP: %s\n", why); return 2;
    }

    puts("== verdicts: x vs xx at the class boundary ==");
    verdict("(?x)[a- ]");
    verdict("(?xx)[a- ]");
    verdict("(?xx)[a-\\ ]");
    verdict("(?xx)[\\ -a]");
    verdict("(?xx)[a\tb]");
    verdict("(?x)[a b]");

    puts("== verdicts: brace quantifiers with spaces ==");
    verdict("a{1, 2}");
    verdict("a{ 1,2}");
    verdict("a{1 ,2}");
    verdict("a{1,2 }");
    verdict("(?x)a{1, 2}");
    verdict("(?x)a{ 1 , 2 }");
    verdict("(?xx)a{1, 2}");

    puts("== matches: x/xx lexing ==");
    TM("(?xx)[a- ]", "a");
    TM("(?xx)[a- ]", "-");
    TM("(?xx)[a- ]", " ");
    TM("(?xx)[a\tb]", "\t");
    TM("(?x)[a b]", " ");
    TM("(?x)a b", "ab");
    TM("(?x)a b", "a b");
    TM("(?x)a\\ b", "a b");
    TM("(?x)a#c\nb", "ab");
    TM("(?xx)a b", "ab");

    puts("== census: bytes (?x) skips OUTSIDE classes ==");
    {
        /* (?x)a<b>b matching "ab" end-to-end means byte <b> was skipped. */
        int n = 0;
        for (int b = 1; b < 256; b++) {   /* 0x00 needs length-passing; PCRE2
                                             compile takes a length — do it */
            char pat[16] = "(?x)a?b";
            pat[5] = (char)b;
            int err = 0; PCRE2_SIZE eoff = 0;
            pcre2_code_8 *code = abi.compile((PCRE2_SPTR)pat, 7, 0,
                                             &err, &eoff, NULL);
            if (!code) continue;
            pcre2_match_data_8 *md = abi.match_data_create(4, NULL);
            int rc = abi.match(code, (PCRE2_SPTR)"ab", 2, 0, 0, md, NULL);
            PCRE2_SIZE *ov = abi.get_ovector_pointer(md);
            if (rc >= 0 && ov[0] == 0 && ov[1] == 2) { printf("  skipped: 0x%02x\n", b); n++; }
            abi.match_data_free(md);
            abi.code_free(code);
        }
        /* 0x00 by explicit length */
        {
            char pat[8] = "(?x)a\0b";
            int err = 0; PCRE2_SIZE eoff = 0;
            pcre2_code_8 *code = abi.compile((PCRE2_SPTR)pat, 7, 0, &err, &eoff, NULL);
            if (code) {
                pcre2_match_data_8 *md = abi.match_data_create(4, NULL);
                int rc = abi.match(code, (PCRE2_SPTR)"ab", 2, 0, 0, md, NULL);
                PCRE2_SIZE *ov = abi.get_ovector_pointer(md);
                if (rc >= 0 && ov[0] == 0 && ov[1] == 2) { puts("  skipped: 0x00"); n++; }
                abi.match_data_free(md);
                abi.code_free(code);
            }
        }
        printf("  total skipped bytes: %d\n", n);
    }

    puts("== census: bytes (?xx) DELETES inside classes ==");
    {
        /* (?xx)[<b>x]: byte deleted iff the class is exactly {x}. */
        int n = 0;
        for (int b = 1; b < 256; b++) {
            if (b == ']' || b == '\\' || b == '^') continue; /* structural */
            char pat[16] = "(?xx)[?x]";
            pat[6] = (char)b;
            int err = 0; PCRE2_SIZE eoff = 0;
            pcre2_code_8 *code = abi.compile((PCRE2_SPTR)pat, 9, 0,
                                             &err, &eoff, NULL);
            if (!code) { printf("  0x%02x: NO COMPILE (err %d)\n", b, err); continue; }
            int self = hits(code, b), x = hits(code, 'x');
            if (!self && x) { printf("  deleted: 0x%02x\n", b); n++; }
            abi.code_free(code);
        }
        printf("  total deleted bytes: %d\n", n);
    }

    puts("== candidate cheap semantics ==");
    {
        pcre2_code_8 *dot = comp(".");
        pcre2_code_8 *sdot = comp("(?s).");
        if (dot && sdot) {
            int nd = 0, ns = 0;
            for (int b = 0; b < 256; b++) { nd += hits(dot, b); ns += hits(sdot, b); }
            printf("  . census=%d   (?s). census=%d\n", nd, ns);
        }
        if (dot) abi.code_free(dot);
        if (sdot) abi.code_free(sdot);
    }
    TM("(?U)a+", "aaa");
    TM("(?U)a+?", "aaa");
    TM("(?m)^b", "a\nb");
    TM("(?n)(a)", "a");
    verdict("(?n)(a)\\1");
    verdict("(?n)(?<g>a)(?<g>b)");
    verdict("(?J)(?<g>a)(?<g>b)");
    verdict("(?<g>a)(?<g>b)");
    {
        pcre2_code_8 *i = comp("(?i)(.)");
        /* per-byte pattern: (?i)<b> vs (?ri)<b> over all 256 subjects */
        int diffs = 0;
        for (int b = 0; b < 256; b++) {
            char p1[16], p2[16];
            int l1 = snprintf(p1, sizeof p1, "(?i)\\x{%02x}", b);
            int l2 = snprintf(p2, sizeof p2, "(?ri)\\x{%02x}", b);
            int e = 0; PCRE2_SIZE eo = 0;
            pcre2_code_8 *c1 = abi.compile((PCRE2_SPTR)p1, (PCRE2_SIZE)l1, 0, &e, &eo, NULL);
            pcre2_code_8 *c2 = abi.compile((PCRE2_SPTR)p2, (PCRE2_SIZE)l2, 0, &e, &eo, NULL);
            if (c1 && c2)
                for (int s = 0; s < 256; s++)
                    if (hits(c1, s) != hits(c2, s)) {
                        printf("  (?i)\\x%02x vs (?ri): differ on subject 0x%02x\n", b, s);
                        diffs++;
                    }
            if (c1) abi.code_free(c1);
            if (c2) abi.code_free(c2);
        }
        printf("  (?i) vs (?ri) diff cells: %d\n", diffs);
        if (i) abi.code_free(i);
    }
    {
        const char *pairs[][2] = {{"\\d","(?aD)\\d"},{"\\s","(?aS)\\s"},
                                  {"\\w","(?aW)\\w"},{"\\b.","(?aP)\\b."}};
        for (int k = 0; k < 4; k++) {
            pcre2_code_8 *p = comp(pairs[k][0]), *q = comp(pairs[k][1]);
            if (p && q) {
                int np = 0, nq = 0, diff = 0;
                for (int b = 0; b < 256; b++) {
                    int hp = hits(p, b), hq = hits(q, b);
                    np += hp; nq += hq; diff += hp != hq;
                }
                printf("  %-8s census=%d   %-10s census=%d   diff=%d\n",
                       pairs[k][0], np, pairs[k][1], nq, diff);
            } else printf("  %s / %s: compile failed\n", pairs[k][0], pairs[k][1]);
            if (p) abi.code_free(p);
            if (q) abi.code_free(q);
        }
    }

    puts("== smoke: scoped state (PARSE-1's 17/17 already measured) ==");
    TM("(?i:a)b", "Ab");
    TM("(?i:a)b", "AB");
    TM("(?i)a(?^)a", "Aa");
    TM("(?i)a(?^)a", "AA");
    return 0;
}
