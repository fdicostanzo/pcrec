/* tests/memfn/targets_check.c -- [XARCH-DEV] U1: the target list table's
 * rows and pcrec's one policy bit, below any artifact; and, with
 * `--fixture`, a kit-shaped `#if`-free fixture wrapped in pcrec's own region
 * and family-guard text for run_targets.sh's compile cells
 * (docs/design/memfn/target_seam.md §2, §6.1, §8).
 *
 * THE CONTROL for the rows is target_seam.md §2's table as written there,
 * spelled out case by case below, never read back from src/gen/targets.def:
 * a row edited in the .def (a deny that no longer wins, a list that admits
 * two families, a family default that changed) disagrees with a literal
 * here. The fixture's control is the compiler and a naive finder
 * (run_targets.sh).
 *
 * Usage: targets_check            -> PASS:/FAIL: lines, exit 0 iff all pass
 *        targets_check --fixture  -> the fixture C text on stdout */
#include <stdio.h>
#include <string.h>

#include "gen/memfn_sites.h"   /* the kit header: MF_P_PORTABLE_ONLY */
#include "gen/targets.h"

static int fails;

static void check(int cond, const char *what)
{
    printf("%s: %s\n", cond ? "PASS" : "FAIL", what);
    fails += !cond;
}

/* The set's members as a comma list ("" on a refusal). */
static const char *set_text(uint64_t flags, const char *list, const char *fam, char *buf,
                            size_t n)
{
    PcrecTargetSet s;
    buf[0] = 0;
    if (pcrec_target_set(flags, list, fam, &s)) return "REFUSED";
    for (unsigned i = 0; i < s.n; i++) {
        size_t l = strlen(buf);
        snprintf(buf + l, n - l, "%s%s", i ? "," : "", pcrec_target(s.t[i])->name);
    }
    return buf;
}

static void row(uint64_t flags, const char *list, const char *fam, const char *want,
                const char *what)
{
    char buf[256], line[512];
    const char *got = set_text(flags, list, fam, buf, sizeof buf);
    snprintf(line, sizeof line, "%s: want {%s}, got {%s}", what, want, got);
    check(!strcmp(got, want), line);
}

static void rows(void)
{
    const uint64_t no = PCREC_NO_MEMFN_SIMD, on = PCREC_FORCE_MEMFN_SIMD;
    const char *host = pcrec_family(pcrec_host_family())->simd_list;

    /* rule 1: the deny wins, over a list and over the force */
    row(no, NULL, NULL, "generic", "rule 1, -fno-memfn-simd");
    row(no | on, NULL, NULL, "generic", "rule 1, both given: the deny wins");
    row(no | on, "x86-64-v3", NULL, "generic", "rule 1, the deny wins over a list");
    /* rule 2: the given list, one family, repeats dropped, order kept */
    row(0, "x86-64,x86-64-v3", NULL, "x86-64,x86-64-v3", "rule 2, one family");
    row(on, "x86-64-v3,x86-64", NULL, "x86-64-v3,x86-64", "rule 2, order kept, the force adds nothing");
    row(0, "x86-64-v3,x86-64-v3", NULL, "x86-64-v3", "rule 2, a repeat dropped");
    row(0, "generic", NULL, "generic", "rule 2, generic alone");
    row(0, "aarch64", NULL, "aarch64", "rule 2, another family alone");
    row(0, "x86-64,aarch64", NULL, "REFUSED", "rule 2, two families refused");
    row(0, "generic,x86-64", NULL, "REFUSED", "rule 2, generic with a family refused");
    row(0, "x86-64-v4", NULL, "REFUSED", "rule 2, an unknown target refused");
    row(0, "x86-64,", NULL, "REFUSED", "rule 2, an empty member refused");
    row(0, "", NULL, "REFUSED", "rule 2, an empty list refused");
    /* rule 3: the family's declared list (x86-64 alone until the dispatch step) */
    row(on, NULL, "x86-64", "x86-64", "rule 3, --family x86-64");
    row(on, NULL, "aarch64", "aarch64", "rule 3, --family aarch64");
    row(on, NULL, "riscv", "REFUSED", "rule 3, an unknown family refused");
    row(on, NULL, NULL, *host ? host : "generic", "rule 3, the host's family (or generic)");
    /* rule 4: neither given */
    row(0, NULL, NULL, "generic", "rule 4, the default");
    row(0, NULL, "x86-64", "generic", "rule 4, a family alone changes nothing");

    /* the one policy bit reads the set */
    check(pcrec_memfn_policy(0) == MF_P_PORTABLE_ONLY, "policy: the default is portable only");
    check(pcrec_memfn_policy(no | on) == MF_P_PORTABLE_ONLY, "policy: the deny wins");
    check(pcrec_memfn_policy(on) == (*host ? 0u : MF_P_PORTABLE_ONLY),
          "policy: -fmemfn-simd lifts the bit wherever the host has a family");

    /* every family's baseline is of that family; the region text is empty
       exactly where the attr is */
    for (unsigned f = PCREC_FAM_NONE + 1; f < PCREC_FAM_N; f++) {
        const PcrecFamily *fr = pcrec_family((PcrecFamilyId)f);
        char line[256];
        snprintf(line, sizeof line, "family %s: its baseline %s is one of its targets",
                 fr->name, pcrec_target(fr->baseline)->name);
        check(pcrec_target(fr->baseline)->family == (PcrecFamilyId)f, line);
    }
    for (unsigned t = 0; t < PCREC_TGT_N; t++) {
        StrBuf a = {0}, b = {0};
        pcrec_target_region_open(&a, (PcrecTargetId)t);
        pcrec_target_region_close(&b, (PcrecTargetId)t);
        int empty = !*pcrec_target((PcrecTargetId)t)->attr;
        char line[256];
        snprintf(line, sizeof line, "target %s: region text %s", pcrec_target((PcrecTargetId)t)->name,
                 empty ? "absent (no attr)" : "present");
        check(empty == (a.len == 0) && empty == (b.len == 0), line);
        pcrec_sb_free(&a);
        pcrec_sb_free(&b);
    }
}

/* The fixture: a family guard, a generic finder, and one #if-free finder
 * per x86-64 target in that target's region -- the shape a kit form takes
 * after U2 (intrinsics with no CPU `#if`, the header inside the text). */
static void fixture(void)
{
    StrBuf c = {0};
    pcrec_family_guard(&c, PCREC_FAM_X86_64);
    pcrec_sb_puts(&c,
        "#include <stddef.h>\n#include <string.h>\n"
        "size_t fx_generic(const unsigned char *s, size_t n, unsigned char b)\n"
        "{ for (size_t i = 0; i < n; i++) if (s[i] == b) return i; return n; }\n\n");
    pcrec_target_region_open(&c, PCREC_TGT_X86_64);
    pcrec_sb_puts(&c,
        "#include <emmintrin.h>\n"
        "size_t fx_w16(const unsigned char *s, size_t n, unsigned char b)\n"
        "{\n    size_t i = 0;\n    const __m128i v = _mm_set1_epi8((char)b);\n"
        "    for (; n - i >= 16; i += 16) {\n        __m128i w; memcpy(&w, s + i, 16);\n"
        "        unsigned m = (unsigned)_mm_movemask_epi8(_mm_cmpeq_epi8(w, v));\n"
        "        if (m) return i + (size_t)__builtin_ctz(m);\n    }\n"
        "    return i + fx_generic(s + i, n - i, b);\n}\n");
    pcrec_target_region_close(&c, PCREC_TGT_X86_64);
    pcrec_sb_puts(&c, "\n");
    pcrec_target_region_open(&c, PCREC_TGT_X86_64_V3);
    pcrec_sb_puts(&c,
        "#include <immintrin.h>\n"
        "size_t fx_w32(const unsigned char *s, size_t n, unsigned char b)\n"
        "{\n    size_t i = 0;\n    const __m256i v = _mm256_set1_epi8((char)b);\n"
        "    for (; n - i >= 32; i += 32) {\n        __m256i w; memcpy(&w, s + i, 32);\n"
        "        unsigned m = (unsigned)_mm256_movemask_epi8(_mm256_cmpeq_epi8(w, v));\n"
        "        if (m) return i + (size_t)__builtin_ctz(m);\n    }\n"
        "    return i + fx_w16(s + i, n - i, b);\n}\n");
    pcrec_target_region_close(&c, PCREC_TGT_X86_64_V3);
    fwrite(c.p, 1, c.len, stdout);
    pcrec_sb_free(&c);
}

int main(int argc, char **argv)
{
    if (argc > 1 && !strcmp(argv[1], "--fixture")) {
        fixture();
        return 0;
    }
    rows();
    return fails != 0;
}
