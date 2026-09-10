/* uprops_oracle.c — THE LIBPCRE2 SIDE of the `\p{...}` membership
 * differential ([M5.0] stage 3), and the version reporter the comparator's
 * whole drift policy turns on.
 *
 *     uprops_oracle --probe            exit 0 always (see below — dead since
 *                                      [ORACLE-LINK]/D98; kept for argv
 *                                      compatibility, never the SKIP signal)
 *     uprops_oracle --version          prints "<lib version>\t<unicode version>"
 *     uprops_oracle {byte|utf8} NAME...
 *
 * For each NAME it prints one line — the name, then that property's member
 * set as ascending code-point intervals — in exactly the shape
 * `uprops_sweep.c` prints for pcrec, so `uprops_compare.py` compares two files
 * and needs to know nothing about either producer. A name libpcre2 refuses
 * prints `NAME ERR <code>`, which is DATA the comparator reads rather than a
 * failure here: whether pcrec should ship a name libpcre2 does not have is the
 * comparator's question, and it has an answer (no).
 *
 * IT USES THE SHARED DIRECT-LINK BINDING (`tests/fuzz/pcre2_abi.h`,
 * [ORACLE-LINK]/D98, 2026-09-09) — `#include <pcre2.h>` plus `-lpcre2-8`,
 * resolved once via `tests/lib/resolve_pcre2.sh` — NOT the dlopen shim this
 * paragraph used to describe. That shim is retired tree-wide; the header's
 * own `pcre2_abi_load()` now just points at symbols the linker already
 * bound and CANNOT FAIL (always returns `PCRE2_ABI_OK`), which makes THIS
 * FILE'S OWN `--probe` MODE DEAD CODE — it always reports "loaded" and can
 * no longer answer "no libpcre2 here" the way it once did. The loud-skip-
 * on-a-stranger's-clone behaviour PC-3/PC-4's shape still needs moved to
 * BUILD TIME instead: `run_uprops_tests.sh` sources `resolve_pcre2.sh` and
 * checks `PCRE2_AVAILABLE` BEFORE attempting to compile this file at all,
 * printing its own SKIP banner in that branch — the same shape every other
 * direct-linked oracle in this tree now uses.
 *
 * IT SWEEPS BY FIND-ALL over one subject that is every code point in order,
 * the same construction the pcrec side uses and for the same reason (one pass
 * instead of 1.1M calls, so the whole space is affordable and there is no
 * sampling rule for a bug to hide behind). `PCRE2_NO_UTF_CHECK` is REQUIRED
 * rather than an optimisation: without it every one of the ~1.1M resumed calls
 * re-validates the whole 3.3 MB subject from offset zero, which measured as a
 * sweep still unfinished after ten minutes on ONE property before it was
 * added.
 *
 * THE OPTION WORDS ARE THE SUITE'S PINNED ONES. `byte` is options=0 — the
 * 8-bit non-UTF build, where PCRE2 treats bytes 0..255 as code points 0..255,
 * which is exactly what pcrec's `byte` encoding is (D58) — and `utf8` is
 * `PCRE2_UTF` alone. Neither adds `PCRE2_UCP`: UCP redefines `\w`/`\d`/`\b`
 * and is a separate axis pcrec has deliberately not taken
 * (`utf8_design.md` §14 ASK 4); it does not alter `\p`. */

/* pcre2_abi.h defines _GNU_SOURCE, needed before any libc header — it MUST
 * be the first #include (tests/registry/pcre2_check.c's own header comment
 * states the same rule; this file violated it until K-uprops-abi-order,
 * 2026-09-08, which is why dlinfo()/RTLD_DI_LINKMAP failed to declare on
 * Linux/glibc while compiling clean on darwin's different code path). */
#include "pcre2_abi.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define PCRE2_ZERO_TERMINATED_OPT (~(PCRE2_SIZE)0)
#define PCRE2_UTF_OPT             0x00080000u
#define PCRE2_NO_UTF_CHECK_OPT    0x40000000u

static unsigned char *subj;
static size_t subjlen;
static unsigned *cp_at;

static int u8enc(unsigned c, unsigned char *o)
{
    if (c < 0x80)    { o[0] = (unsigned char)c; return 1; }
    if (c < 0x800)   { o[0] = (unsigned char)(0xC0 | (c >> 6));
                       o[1] = (unsigned char)(0x80 | (c & 0x3F)); return 2; }
    if (c < 0x10000) { o[0] = (unsigned char)(0xE0 | (c >> 12));
                       o[1] = (unsigned char)(0x80 | ((c >> 6) & 0x3F));
                       o[2] = (unsigned char)(0x80 | (c & 0x3F)); return 3; }
    o[0] = (unsigned char)(0xF0 | (c >> 18));
    o[1] = (unsigned char)(0x80 | ((c >> 12) & 0x3F));
    o[2] = (unsigned char)(0x80 | ((c >> 6) & 0x3F));
    o[3] = (unsigned char)(0x80 | (c & 0x3F));
    return 4;
}

/* The surrogates are ABSENT from the subject, on both sides, and that is a
 * fact about the encoding rather than a convenience: U+D800..U+DFFF have no
 * UTF-8 encoding at all (src/opt/lower_enc.c's surrogate gap), so no subject
 * can contain one and no sweep can ask about one. `\p{Cs}` is therefore
 * measured EMPTY by both sides — the honest answer, not a hole. */
static void build_subject(int utf)
{
    unsigned maxcp = utf ? 0x10FFFFu : 0xFFu;
    subj  = malloc((size_t)maxcp * 4u + 8u);
    cp_at = malloc(((size_t)maxcp * 4u + 8u) * sizeof *cp_at);
    if (!subj || !cp_at) { fprintf(stderr, "oom\n"); exit(2); }
    subjlen = 0;
    for (unsigned c = 0; c <= maxcp; c++) {
        if (utf && c >= 0xD800u && c <= 0xDFFFu) continue;
        cp_at[subjlen] = c;
        if (utf) subjlen += (size_t)u8enc(c, subj + subjlen);
        else     subj[subjlen++] = (unsigned char)c;
    }
}

int main(int argc, char **argv)
{
    Pcre2Abi abi;
    char why[512];   /* the shim composes a "tried A, B, C" list plus dlerror();
                       * 256 is measurably too small for the darwin candidate
                       * list and -Werror=format-truncation says so */
    int loaded = (pcre2_abi_load(&abi, why, sizeof why) == PCRE2_ABI_OK);

    if (argc >= 2 && strcmp(argv[1], "--probe") == 0) {
        if (!loaded) { fprintf(stderr, "%s\n", why); return 1; }
        return 0;
    }
    if (!loaded) { fprintf(stderr, "%s\n", why); return 1; }

    if (argc >= 2 && strcmp(argv[1], "--version") == 0) {
        char lib[64], uni[64];
        pcre2_abi_version(&abi, lib, sizeof lib);
        pcre2_abi_unicode_version(&abi, uni, sizeof uni);
        printf("%s\t%s\n", lib, uni);
        return 0;
    }
    if (argc < 3) {
        fprintf(stderr, "usage: %s {byte|utf8} NAME...\n", argv[0]);
        return 2;
    }
    int utf = strcmp(argv[1], "utf8") == 0;
    if (!utf && strcmp(argv[1], "byte") != 0) {
        fprintf(stderr, "unknown encoding %s\n", argv[1]);
        return 2;
    }
    build_subject(utf);
    uint32_t copts = utf ? PCRE2_UTF_OPT : 0u;
    uint32_t mopts = utf ? PCRE2_NO_UTF_CHECK_OPT : 0u;

    for (int a = 2; a < argc; a++) {
        char pat[96];
        snprintf(pat, sizeof pat, "\\p{%s}", argv[a]);
        int err; PCRE2_SIZE eo;
        pcre2_code_8 *re = abi.compile((PCRE2_SPTR)pat,
                                       PCRE2_ZERO_TERMINATED_OPT,
                                       copts, &err, &eo, NULL);
        if (!re) { printf("%s ERR %d\n", argv[a], err); continue; }
        pcre2_match_data_8 *md = abi.match_data_create(4, NULL);
        PCRE2_SIZE pos = 0;
        unsigned lo = 0, hi = 0;
        int have = 0;
        unsigned long nint = 0, nmemb = 0;
        printf("%s", argv[a]);
        while (pos < subjlen) {
            int rc = abi.match(re, (PCRE2_SPTR)subj, subjlen, pos, mopts, md, NULL);
            if (rc < 0) break;
            PCRE2_SIZE *ov = abi.get_ovector_pointer(md);
            unsigned cp = cp_at[ov[0]];
            nmemb++;
            if (have && cp == hi + 1) hi = cp;
            else { if (have) { printf(" %X-%X", lo, hi); nint++; } lo = hi = cp; have = 1; }
            pos = (ov[1] > ov[0]) ? ov[1] : ov[0] + 1;
        }
        if (have) { printf(" %X-%X", lo, hi); nint++; }
        printf("\n");
        fprintf(stderr, "  oracle %-10s intervals=%lu members=%lu\n",
                argv[a], nint, nmemb);
        abi.match_data_free(md);
        abi.code_free(re);
    }
    return 0;
}
