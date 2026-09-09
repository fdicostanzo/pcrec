/* studies/linktest_probe/pcre2_abi_linked.h — a DIRECT-LINK twin of
 * tests/fuzz/pcre2_abi.h, PROTOTYPE ONLY (charter: linktest lane, 2026-09-09).
 *
 * Same PUBLIC SURFACE as pcre2_abi.h on purpose: the `Pcre2Abi` struct with
 * the identical field names pcre2_check.c actually calls
 * (`pcre2.compile`/`pcre2.code_free`/`pcre2.get_error_message` — the only
 * three field accesses PC-3 makes; grep-verified, 2026-09-09), plus
 * `pcre2_abi_load()`/`pcre2_abi_version()`/`pcre2_abi_unicode_version()`/
 * `pcre2_abi_path()` under the SAME names. That is what makes the twin's
 * diff against pcre2_check.c ONE LINE (the #include) rather than a rewrite
 * of check logic — see pcre2_check_linked.c.
 *
 * WHAT'S DIFFERENT FROM THE DLOPEN SHIM: no dlopen, no dlsym, no runtime
 * "did the symbol resolve" branch. `#include <pcre2.h>` with
 * PCRE2_CODE_UNIT_WIDTH=8 pulls in the REAL prototypes and the REAL 8-bit
 * generic macros (`pcre2_compile` -> `pcre2_compile_8`, etc. — Homebrew's
 * pcre2.h, PCRE2_SUFFIX), so `pcre2_abi_load()` below just points the
 * struct's function-pointer fields at those symbols directly: no runtime
 * lookup, no version skew between what the HEADER declares and what the
 * LOADER resolved (U13/U15b's whole finding on this box — the dlopen shim's
 * candidate list resolves macOS's SYSTEM libpcre2 10.42 while this header's
 * types come from Homebrew's 10.48 pcre2.h). Build/link this twin against
 * `resolve_pcre2.sh`'s own -I/-L output and there is only ONE libpcre2 in
 * the picture, structurally.
 *
 * dladdr() (not dlopen/dlsym) is still used by `pcre2_abi_path()`, exactly
 * as the ORIGINAL shim's __APPLE__ branch already does — dladdr resolves
 * the file behind ANY loaded symbol regardless of how it got loaded, dlopen
 * or ordinary link-time binding, so this is not a hidden dlopen. */

#ifndef PCREC_STUDIES_PCRE2_ABI_LINKED_H
#define PCREC_STUDIES_PCRE2_ABI_LINKED_H

#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <dlfcn.h>      /* dladdr only — attributing the resolved file, no dlopen */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

/* Same field NAMES as tests/fuzz/pcre2_abi.h's Pcre2Abi (mechanical parity
 * with the check's call sites), typed against the REAL headers now instead
 * of hand-declared prototypes. Fields the twin's own call sites never use
 * (match, match_data_create, match_data_free, pattern_info, get_ovector_
 * pointer/count) are kept for shape parity with the original struct but
 * populated too - cheap, and it means a future PC-4-style consumer of this
 * twin needs no second adapter. */
typedef struct {
    void *handle;   /* no dlopen handle to hold; kept for shape parity, and
                      * given a real body-address value below (any non-NULL
                      * marks "loaded") — pcre2_abi_path() below never reads
                      * it, matching how the original macOS branch works. */
    pcre2_code            *(*compile)(PCRE2_SPTR, PCRE2_SIZE, uint32_t, int *,
                                       PCRE2_SIZE *, pcre2_compile_context *);
    pcre2_match_data      *(*match_data_create)(uint32_t, pcre2_general_context *);
    int                    (*match)(const pcre2_code *, PCRE2_SPTR, PCRE2_SIZE,
                                     PCRE2_SIZE, uint32_t, pcre2_match_data *,
                                     pcre2_match_context *);
    PCRE2_SIZE            *(*get_ovector_pointer)(pcre2_match_data *);
    void                   (*match_data_free)(pcre2_match_data *);
    void                   (*code_free)(pcre2_code *);
    int                    (*get_error_message)(int, unsigned char *, PCRE2_SIZE);
    int                    (*pattern_info)(const pcre2_code *, uint32_t, void *);
    uint32_t               (*get_ovector_count)(pcre2_match_data *);
} Pcre2Abi;

enum { PCRE2_ABI_OK = 0, PCRE2_ABI_NO_LIB = 1, PCRE2_ABI_NO_SYMBOL = 2 };

/* Always OK: the symbols are resolved by the LINKER before this process can
 * even start (the analogue of pcre2_abi.h's dlopen/dlsym failing at runtime
 * does not exist here — a missing symbol is a build-time link error, not a
 * run-time status this function could report). `why`/`whysz` kept in the
 * signature for call-site parity with pcre2_abi_load(); never written. */
static inline int pcre2_abi_load(Pcre2Abi *abi, char *why, size_t whysz)
{
    (void)why; (void)whysz;
    memset(abi, 0, sizeof *abi);
    abi->compile              = pcre2_compile;
    abi->match_data_create    = pcre2_match_data_create;
    abi->match                = pcre2_match;
    abi->get_ovector_pointer  = pcre2_get_ovector_pointer;
    abi->match_data_free      = pcre2_match_data_free;
    abi->code_free            = pcre2_code_free;
    abi->get_error_message    = pcre2_get_error_message;
    abi->pattern_info         = pcre2_pattern_info;
    abi->get_ovector_count    = pcre2_get_ovector_count;
    /* Any non-NULL marks "loaded" for the two call sites (`main()`'s
     * `!= PCRE2_ABI_OK` check never even looks at `handle`) — use a real
     * linked function's address rather than a magic constant. */
    abi->handle = (void *)(uintptr_t)abi->compile;
    return PCRE2_ABI_OK;
}

static inline void pcre2_abi_version(const Pcre2Abi *abi, char *buf, size_t bufsz)
{
    (void)abi;
    char tmp[64] = {0};
    if (pcre2_config(PCRE2_CONFIG_VERSION, tmp) >= 0)
        snprintf(buf, bufsz, "%s", tmp);
    else
        snprintf(buf, bufsz, "unknown");
}

static inline void pcre2_abi_unicode_version(const Pcre2Abi *abi, char *buf,
                                             size_t bufsz)
{
    (void)abi;
    char tmp[64] = {0};
    if (pcre2_config(PCRE2_CONFIG_UNICODE_VERSION, tmp) >= 0)
        snprintf(buf, bufsz, "%s", tmp);
    else
        snprintf(buf, bufsz, "unknown");
}

/* dladdr on a symbol the LINKER bound (not dlopen) — same call the original
 * shim's __APPLE__ branch makes, proving this is attribution, not a second
 * loader. */
static inline const char *pcre2_abi_path(const Pcre2Abi *abi)
{
    Dl_info info;
    if (!abi->compile) return NULL;
    if (dladdr((void *)abi->compile, &info) == 0) return NULL;
    return (info.dli_fname && info.dli_fname[0]) ? info.dli_fname : NULL;
}

#endif /* PCREC_STUDIES_PCRE2_ABI_LINKED_H */
