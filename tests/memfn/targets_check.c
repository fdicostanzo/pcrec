/* tests/memfn/targets_check.c -- [XARCH-DEV] unit K0 (request R-36): the
 * kit's CPU target ENTRIES (memfn.h's target table section) below any
 * artifact; and, with `--fixture`, a kit-shaped `#if`-free fixture wrapped in
 * the kit's own region and family-guard texts, for run_targets.sh's compile
 * cells (docs/design/memfn/target_seam_units.md §2-§3, target_seam.md §2,
 * §6.1, §8).
 *
 * THE CONTROL for the entries is the design's table as written there
 * (units.md's K0 row: the four tokens, the two families, x86_64's default
 * list `x86-64` until the dispatch step, `sahf` in x86-64-v3's features, R2),
 * spelled out case by case below and never read back from
 * memfn/src/targets.def: a row edited in the .def disagrees with a literal
 * here. The host's default list is held to `uname -m`, which the runner
 * passes in (argv[1]), not to the kit's own `#if`. The fixture's control is
 * the compiler and a naive finder (run_targets.sh).
 *
 * Usage: targets_check UNAME_M      -> PASS:/FAIL: lines, exit 0 iff all pass
 *        targets_check --fixture    -> the fixture C text on stdout */
#include <stdio.h>
#include <string.h>
#include <strings.h>

#include "memfn.h"

static int fails;

static void check(int cond, const char *what)
{
    printf("%s: %s\n", cond ? "PASS" : "FAIL", what);
    fails += !cond;
}

static const mf_target *tgt(const char *tok)
{
    return mf_target_parse(tok, strlen(tok), NULL, 0);
}

/* One target row: its canonical name, family, needs and features (facts),
 * and its region's C spelling (present exactly when it has needs), read
 * through the parser from the token as given. */
static void target_row(const char *tok, const char *name, const char *family,
                       const char *needs, const char *features)
{
    char line[512], err[256];
    const mf_target *t = mf_target_parse(tok, strlen(tok), err, sizeof err);
    snprintf(line, sizeof line, "target '%s' parses (%s)", tok, t ? t->name : err);
    check(t != NULL, line);
    if (!t) return;
    const mf_target_c *c = mf_target_c_of(t);
    int region = *needs != 0;
    snprintf(line, sizeof line, "target '%s': canonical '%s', family %s, needs '%s', features '%s', %s",
             tok, name, family ? family : "none", needs, features, region ? "a region" : "no region");
    check(!strcmp(t->name, name) &&
          (family ? t->family && !strcmp(t->family->name, family) : !t->family) &&
          !strcmp(t->needs, needs) && !strcmp(t->features, features) && c &&
          (*c->region_open != 0) == region && (*c->region_close != 0) == region && !*err, line);
    if (c && region) {
        /* target_seam.md §6.1: the additive list (the needs) under both
         * spellings, never `arch=` */
        char gcc[512], clang[512];
        snprintf(gcc, sizeof gcc, "#pragma GCC target(\"%s\")", needs);
        snprintf(clang, sizeof clang, "__attribute__((target(\"%s\")))", needs);
        snprintf(line, sizeof line, "target %s: its region pushes its needs for gcc and clang, no arch=", name);
        check(strstr(c->region_open, gcc) && strstr(c->region_open, clang) &&
              strstr(c->region_open, "#pragma GCC push_options") &&
              strstr(c->region_close, "#pragma GCC pop_options") &&
              strstr(c->region_close, "#pragma clang attribute pop") &&
              !strstr(c->region_open, "arch="), line);
    }
}

static void refused(const char *tok, size_t len, int family, const char *what)
{
    char line[512], err[256];
    int got = family ? mf_family_parse(tok, len, err, sizeof err) == NULL
                     : mf_target_parse(tok, len, err, sizeof err) == NULL;
    snprintf(line, sizeof line, "%s: refused with the kit's text ('%s')", what, err);
    check(got && *err && (len == 0 || strstr(err, "unknown")), line);
}

static void rows(const char *uname_m)
{
    size_t nt = 0, nf = 0;
    const mf_target *ts = mf_targets(&nt);
    const mf_family *fs = mf_families(&nf);
    char line[512];

    /* the populations (K35): the design's rows, counted */
    snprintf(line, sizeof line, "the table lists 4 targets and 2 families (got %zu, %zu)", nt, nf);
    check(nt == 4 && nf == 2, line);

    /* every token, canonical and as a caller may spell it */
    static const char v3[] = "avx2,bmi,bmi2,cx16,f16c,fma,lzcnt,movbe,popcnt,sahf,sse4.1,sse4.2,ssse3,xsave";
    /* U2: v3's features add `sse2` (the w16 level's need, which its family's
       compile supplies and its region does not push) */
    static const char v3f[] = "avx2,bmi,bmi2,cx16,f16c,fma,lzcnt,movbe,popcnt,sahf,sse2,sse4.1,sse4.2,ssse3,xsave";
    target_row("generic", "generic", NULL, "", "");
    target_row("x86-64", "x86-64", "amd64", "sse2", "sse2");
    target_row("x86-64-v3", "x86-64-v3", "amd64", v3, v3f);
    target_row("armv8-a", "armv8-a", "arm64", "", "neon");
    target_row("X86-64", "x86-64", "amd64", "sse2", "sse2");
    target_row("X86-64-V3", "x86-64-v3", "amd64", v3, v3f);
    target_row("ARMv8-A", "armv8-a", "arm64", "", "neon");
    target_row("GENERIC", "generic", NULL, "", "");

    /* the listing is the parser's table: every listed row parses to itself */
    int self = 1;
    for (size_t i = 0; i < nt; i++) self &= tgt(ts[i].name) == &ts[i];
    for (size_t i = 0; i < nf; i++)
        self &= mf_family_parse(fs[i].name, strlen(fs[i].name), NULL, 0) == &fs[i];
    check(self, "every listed target and family parses to its own row");

    /* the C spellings: one per listed row, none for a pointer not a row */
    int spelt = 1;
    for (size_t i = 0; i < nt; i++) spelt &= mf_target_c_of(&ts[i]) != NULL;
    for (size_t i = 0; i < nf; i++)
        spelt &= mf_family_c_of(&fs[i]) && strstr(mf_family_c_of(&fs[i])->guard, "#error");
    mf_target fake = ts[0];
    mf_family ffake = fs[0];
    check(spelt && !mf_target_c_of(&fake) && !mf_family_c_of(&ffake) && !mf_target_c_of(NULL),
          "every listed row has its C spelling; a copy of a row and NULL have none");

    /* refusals: the token's bytes are all of it */
    refused("x86-64-v4", 9, 0, "target x86-64-v4 (no kit level needs it, D77)");
    refused("x86-64-v3", 3, 0, "target 'x86' (a prefix of a token)");
    refused("x86-64 ", 7, 0, "target 'x86-64 ' (a trailing blank)");
    refused("x86-64-v3x", 10, 0, "target 'x86-64-v3x' (a token plus a byte)");
    refused("", 0, 0, "an empty target");
    refused("riscv", 5, 1, "family riscv");
    refused("generic", 7, 1, "family generic (the portable target has no family)");
    /* ONE token space: a token of one kind is refused as the other, `_` is not `-` */
    refused("amd64", 5, 0, "target amd64 (a family, not a target)");
    refused("arm64", 5, 0, "target arm64 (a family, not a target)");
    refused("x86_64", 6, 0, "target x86_64 (`_` is not `-`)");
    refused("x86_64", 6, 1, "family x86_64 (the Go name is amd64)");
    refused("aarch64", 7, 1, "family aarch64 (the Go name is arm64)");
    refused("x86-64", 6, 1, "family x86-64 (a target, not a family)");
    refused("armv8-a", 7, 1, "family armv8-a (a target, not a family)");
    refused("x86_64_v3", 9, 0, "target x86_64_v3 (`_` is not `-`)");
    refused("x86-64-v3", 9, 1, "family x86-64-v3 (a target, not a family)");
    refused("", 0, 1, "an empty family");
    {
        const mf_target *t = mf_target_parse("x86-64-v3", 6, NULL, 0);
        check(t && !strcmp(t->name, "x86-64"), "target: only `len` bytes are read ('x86-64-v3', 6 -> x86-64)");
        char tiny[8];
        check(!mf_target_parse("nope", 4, tiny, sizeof tiny) && strlen(tiny) == sizeof tiny - 1,
              "target: a refusal into a short buffer is truncated and terminated");
        check(!mf_target_parse("nope", 4, tiny, 0) && !mf_target_parse(NULL, 3, NULL, 0),
              "target: n 0 and a NULL token are safe");
    }

    /* no token is both a family and a target (compared case-blind) */
    int distinct = 1;
    for (size_t i = 0; i < nt; i++)
        for (size_t j = 0; j < nf; j++) distinct &= strcasecmp(ts[i].name, fs[j].name) != 0;
    check(distinct, "no token names both a family and a target");

    /* families: the default lists (x86-64 alone until the dispatch step, U5)
     * and the guard */
    const mf_family *x = mf_family_parse("amd64", 5, NULL, 0);
    const mf_family *a = mf_family_parse("arm64", 5, NULL, 0);
    const mf_family *xu = mf_family_parse("AMD64", 5, NULL, 0);
    check(x && !strcmp(x->defaults, "x86-64"), "family amd64: default list 'x86-64'");
    check(a && !strcmp(a->defaults, "armv8-a"), "family arm64: default list 'armv8-a'");
    check(xu == x, "family 'AMD64' parses as amd64 (case-blind)");
    const mf_family_c *xc = mf_family_c_of(x);
    check(xc && !strncmp(xc->guard, "#if !(", 6) && strstr(xc->guard, "#error") &&
              strstr(xc->guard, "__x86_64__") && strstr(xc->guard, "__ILP32__"),
          "family amd64: its C guard is an #if ... #error on the architecture, excluding ILP32");
    check(tgt("x86-64-v3") && tgt("x86-64-v3")->family == x && tgt("armv8-a")->family == a,
          "each family's targets point at its row");

    /* the portable target and the host's default list */
    const mf_target *p = mf_portable_target();
    check(p && !strcmp(p->name, "generic") && !p->family && !*p->needs && !*p->features &&
              !*mf_target_c_of(p)->region_open,
          "the portable target is generic: no family, needs, features or region");
    /* every row has its doc line, and the host family entry is the family the
     * host's default list belongs to */
    int docs = 1;
    for (size_t i = 0; i < nt; i++) docs &= ts[i].doc && *ts[i].doc;
    for (size_t i = 0; i < nf; i++) docs &= fs[i].doc && *fs[i].doc;
    check(docs, "every target and family has a doc line");
    const mf_family *hf = mf_host_family();
    check(hf ? !strcmp(hf->defaults, mf_host_defaults()) : !strcmp(mf_host_defaults(), "generic"),
          "the host family's default list is the host default (no family: the portable token)");
    const char *want = !strcmp(uname_m, "x86_64")                                   ? "x86-64"
                       : !strcmp(uname_m, "aarch64") || !strcmp(uname_m, "arm64") ? "armv8-a"
                                                                                   : "generic";
    snprintf(line, sizeof line, "the host default list on a %s host is '%s' (got '%s')", uname_m, want,
             mf_host_defaults());
    check(!strcmp(mf_host_defaults(), want), line);
}

/* The fixture: the family guard, a generic finder, and one #if-free finder
 * per x86-64 target in that target's region -- the shape a kit form takes
 * after U2 (intrinsics with no CPU `#if`, the header inside the text). */
static void fixture(void)
{
    const mf_target *t16 = tgt("x86-64"), *t32 = tgt("x86-64-v3");
    if (!t16 || !t32) return;
    fputs(mf_family_c_of(t16->family)->guard, stdout);
    fputs("#include <stddef.h>\n#include <string.h>\n"
          "size_t fx_generic(const unsigned char *s, size_t n, unsigned char b)\n"
          "{ for (size_t i = 0; i < n; i++) if (s[i] == b) return i; return n; }\n\n", stdout);
    fputs(mf_target_c_of(t16)->region_open, stdout);
    fputs("#include <emmintrin.h>\n"
          "size_t fx_w16(const unsigned char *s, size_t n, unsigned char b)\n"
          "{\n    size_t i = 0;\n    const __m128i v = _mm_set1_epi8((char)b);\n"
          "    for (; n - i >= 16; i += 16) {\n        __m128i w; memcpy(&w, s + i, 16);\n"
          "        unsigned m = (unsigned)_mm_movemask_epi8(_mm_cmpeq_epi8(w, v));\n"
          "        if (m) return i + (size_t)__builtin_ctz(m);\n    }\n"
          "    return i + fx_generic(s + i, n - i, b);\n}\n", stdout);
    fputs(mf_target_c_of(t16)->region_close, stdout);
    fputs("\n", stdout);
    fputs(mf_target_c_of(t32)->region_open, stdout);
    fputs("#include <immintrin.h>\n"
          "size_t fx_w32(const unsigned char *s, size_t n, unsigned char b)\n"
          "{\n    size_t i = 0;\n    const __m256i v = _mm256_set1_epi8((char)b);\n"
          "    for (; n - i >= 32; i += 32) {\n        __m256i w; memcpy(&w, s + i, 32);\n"
          "        unsigned m = (unsigned)_mm256_movemask_epi8(_mm256_cmpeq_epi8(w, v));\n"
          "        if (m) return i + (size_t)__builtin_ctz(m);\n    }\n"
          "    return i + fx_w16(s + i, n - i, b);\n}\n", stdout);
    fputs(mf_target_c_of(t32)->region_close, stdout);
}

int main(int argc, char **argv)
{
    if (argc > 1 && !strcmp(argv[1], "--fixture")) {
        fixture();
        return 0;
    }
    rows(argc > 1 ? argv[1] : "");
    return fails != 0;
}
