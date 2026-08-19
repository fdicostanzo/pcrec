/* tests/fuzz/pcre2_abi.h — the hand-declared slice of the PCRE2 8-bit ABI,
 * loaded at runtime with dlopen.
 *
 * WHY A HEADER. This box has the PCRE2 8-bit RUNTIME (libpcre2-8-0, i.e.
 * /usr/lib/x86_64-linux-gnu/libpcre2-8.so.0.*) but NOT the -dev package: no
 * pcre2.h, no unversioned libpcre2-8.so symlink, no pkg-config file. So we
 * cannot `#include <pcre2.h>` and cannot link `-lpcre2-8`; we hand-declare the
 * documented, stable 8-bit API we need and resolve it with dlopen/dlsym.
 *
 * That rationale lived in tests/fuzz/pcre2_oracle.c and was about to be COPIED
 * into a second consumer (tests/registry/pcre2_check.c, step PC-3). Copying a
 * declaration of somebody else's ABI into two files is the exact shape of the
 * `\v` bug this project already paid for — two descriptions of one thing, ten
 * lines or two files apart, with nothing enforcing that they agree. One home.
 *
 * EVERYTHING HERE IS `static`: both consumers are standalone programs, each
 * gets its own copy, and there is no library to link.
 *
 * THE LOADER DOES NOT EXIT. `pcre2_abi_load()` returns a status and leaves the
 * policy to the caller, because the two callers need opposite ones: the fuzzer
 * oracle must fail hard (a missing oracle means no ground truth), while
 * tests/registry/pcre2_check.c runs inside `make test` and must SKIP LOUDLY —
 * a stranger who clones this repo without libpcre2-8-0 installed still has to
 * get a green suite. */

#ifndef PCREC_TESTS_PCRE2_ABI_H
#define PCREC_TESTS_PCRE2_ABI_H

#define _GNU_SOURCE
#include <dlfcn.h>
#include <link.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

typedef size_t PCRE2_SIZE;
typedef const unsigned char *PCRE2_SPTR;
typedef struct pcre2_real_code_8 pcre2_code_8;
typedef struct pcre2_real_match_data_8 pcre2_match_data_8;
typedef struct pcre2_real_general_context_8 pcre2_general_context_8;
typedef struct pcre2_real_compile_context_8 pcre2_compile_context_8;
typedef struct pcre2_real_match_context_8 pcre2_match_context_8;

typedef int (*fn_config)(unsigned int, void *);
typedef pcre2_code_8 *(*fn_compile)(PCRE2_SPTR pattern, PCRE2_SIZE length,
    uint32_t options, int *errorcode, PCRE2_SIZE *erroroffset,
    pcre2_compile_context_8 *ccontext);
typedef pcre2_match_data_8 *(*fn_match_data_create)(uint32_t ovecsize,
    pcre2_general_context_8 *gcontext);
typedef int (*fn_match)(const pcre2_code_8 *code, PCRE2_SPTR subject,
    PCRE2_SIZE length, PCRE2_SIZE startoffset, uint32_t options,
    pcre2_match_data_8 *match_data, pcre2_match_context_8 *mcontext);
typedef PCRE2_SIZE *(*fn_get_ovector_pointer)(pcre2_match_data_8 *match_data);
typedef void (*fn_match_data_free)(pcre2_match_data_8 *match_data);
typedef void (*fn_code_free)(pcre2_code_8 *code);
typedef int (*fn_get_error_message)(int errorcode, unsigned char *buffer,
    PCRE2_SIZE bufflen);
typedef int (*fn_pattern_info)(const pcre2_code_8 *code, uint32_t what,
    void *where);
typedef uint32_t (*fn_get_ovector_count)(pcre2_match_data_8 *match_data);

/* [M4.7d] MEASURED (not read from documentation), against libpcre2 10.46 on
 * this box, tests/fuzz/CLAUDE.md's "measured, never assumed" discipline
 * applied to a PCRE2 constant this project had not needed before: querying
 * `pcre2_pattern_info_8(code, N, &val)` for `(a)(b)(c)` returned val==3 only
 * at N==4, for `(a)|(b)` val==2 only at N==4, and for `(a)|(b)(c)` val==3
 * only at N==4 — three independent patterns with distinct group counts, one
 * candidate consistent with all three. This is PCRE2_INFO_CAPTURECOUNT: the
 * lexical capturing-group count, the same fact pcrec's `ngroups` names (C9,
 * match_api_m4.md — group numbering/counting is unaffected by M4). The same
 * probe measured PCRE2's unset-group convention: with the ovector sized to
 * exactly `capturecount + 1` pairs, every group that never participated in
 * the match — including ones numbered ABOVE the highest group that did
 * participate, not merely ones within `rc`'s range — reads back
 * `(PCRE2_SIZE)-1` in BOTH offsets (`PCRE2_UNSET`, all bits set). Cast to a
 * signed type of the same width (`ptrdiff_t` here, matching
 * `<prefix>_search`'s own D44.2 element type) this prints as literal `-1`,
 * bit-for-bit identical to pcrec's `PCREC_UNSET` — so tests/fuzz/pcre2_oracle.c
 * needs NO numeric remapping between the two engines' unset conventions,
 * only a same-format print on both sides. See tests/fuzz/README.md's
 * "Capture-group span comparison" section for the full transcript. */
#define PCRE2_ABI_INFO_CAPTURECOUNT 4

/* One struct, not eight file-scope pointers: a consumer that uses only some of
 * them still "uses" the variable, so -Wunused-variable stays meaningful for
 * everything else in the file. */
typedef struct {
    void *handle;
    fn_compile             compile;
    fn_match_data_create   match_data_create;
    fn_match               match;
    fn_get_ovector_pointer get_ovector_pointer;
    fn_match_data_free     match_data_free;
    fn_code_free           code_free;
    fn_get_error_message   get_error_message;
    fn_pattern_info        pattern_info;        /* [M4.7d] */
    fn_get_ovector_count   get_ovector_count;   /* [M4.7d] */
} Pcre2Abi;

/* Candidate names to dlopen: the SONAME first (always present with the runtime
 * package), then the unversioned name in case a -dev package is installed on
 * some other box. */
static const char *const PCRE2_ABI_LIBS[] = {
    "libpcre2-8.so.0",
    "libpcre2-8.so",
    NULL
};

enum { PCRE2_ABI_OK = 0, PCRE2_ABI_NO_LIB = 1, PCRE2_ABI_NO_SYMBOL = 2 };

/* Fills `abi` and returns PCRE2_ABI_OK, or leaves it zeroed and returns a
 * reason. `why` (if non-NULL) receives a one-line human explanation. */
static inline int pcre2_abi_load(Pcre2Abi *abi, char *why, size_t whysz)
{
    void *h = NULL;
    memset(abi, 0, sizeof *abi);

    for (int i = 0; PCRE2_ABI_LIBS[i]; i++)
        if ((h = dlopen(PCRE2_ABI_LIBS[i], RTLD_NOW | RTLD_LOCAL))) break;
    if (!h) {
        /* The candidate list is ITERATED into the message rather than restated
         * as a literal: a third SONAME added to the array above would otherwise
         * leave this sentence quietly lying, which is the two-descriptions-of-
         * one-fact shape this header exists to end (R8/C1-F6). */
        char tried[256]; size_t k = 0;
        for (int i = 0; PCRE2_ABI_LIBS[i]; i++)
            k += (size_t)snprintf(tried + k, k < sizeof tried ? sizeof tried - k : 0,
                                  "%s%s", i ? ", " : "", PCRE2_ABI_LIBS[i]);
        if (why) snprintf(why, whysz,
            "could not dlopen the PCRE2 8-bit runtime (tried %s): %s",
            tried, dlerror());
        return PCRE2_ABI_NO_LIB;
    }

    struct { const char *name; void **slot; } want[] = {
        {"pcre2_compile_8",              (void **)&abi->compile},
        {"pcre2_match_data_create_8",    (void **)&abi->match_data_create},
        {"pcre2_match_8",                (void **)&abi->match},
        {"pcre2_get_ovector_pointer_8",  (void **)&abi->get_ovector_pointer},
        {"pcre2_match_data_free_8",      (void **)&abi->match_data_free},
        {"pcre2_code_free_8",            (void **)&abi->code_free},
        {"pcre2_get_error_message_8",    (void **)&abi->get_error_message},
        {"pcre2_pattern_info_8",         (void **)&abi->pattern_info},
        {"pcre2_get_ovector_count_8",    (void **)&abi->get_ovector_count},
    };
    for (size_t i = 0; i < sizeof want / sizeof want[0]; i++) {
        dlerror();
        void *sym = dlsym(h, want[i].name);
        const char *err = dlerror();
        if (err) {
            if (why) snprintf(why, whysz,
                "the PCRE2 library is missing expected symbol '%s': %s "
                "(this ABI is hand-declared against PCRE2 10.46)",
                want[i].name, err);
            memset(abi, 0, sizeof *abi);
            dlclose(h);
            return PCRE2_ABI_NO_SYMBOL;
        }
        *want[i].slot = sym;
    }
    abi->handle = h;
    return PCRE2_ABI_OK;
}

/* R2-PR5: resolving symbols proves nothing about VERSION, and versions differ
 * behaviourally (pre-10.43 `{,n}` — docs/dev/upstream_issues.md U2). Every consumer
 * prints this alongside its results, so a result can be attributed. */
static inline void pcre2_abi_version(const Pcre2Abi *abi, char *buf, size_t bufsz)
{
    fn_config cfg = abi->handle ? (fn_config)dlsym(abi->handle, "pcre2_config_8")
                                : NULL;
    char tmp[64] = {0};
    if (cfg && cfg(11 /* PCRE2_CONFIG_VERSION */, tmp) >= 0)
        snprintf(buf, bufsz, "%s", tmp);
    else
        snprintf(buf, bufsz, "unknown");
}

/* The filesystem path dlopen actually resolved. Two uses: attributing a result
 * to a file rather than to a SONAME, and — for pcre2_check.c — reading the
 * shared object's own string table as a source of candidate verb names that
 * comes from PCRE2 rather than from pcrec. Returns NULL if unavailable. */
static inline const char *pcre2_abi_path(const Pcre2Abi *abi)
{
    struct link_map *lm = NULL;
    if (!abi->handle) return NULL;
    if (dlinfo(abi->handle, RTLD_DI_LINKMAP, &lm) != 0 || !lm) return NULL;
    return (lm->l_name && lm->l_name[0]) ? lm->l_name : NULL;
}

#endif /* PCREC_TESTS_PCRE2_ABI_H */
