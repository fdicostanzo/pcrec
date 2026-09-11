/* tests/fuzz/pcre2_abi.h — the DIRECT-LINK binding to libpcre2, shared by
 * every oracle-vs-libpcre2 check in this tree.
 *
 * [ORACLE-LINK] (2026-09-09) RETIRED THE DLOPEN SHIM THIS FILE USED TO BE.
 * See docs/dev/decisions.md D98 for the full rationale; the short version:
 * this project ran three real incidents (upstream_issues.md U13, U15b, and
 * the K-uprops-abi-order ordering trap the old dlopen loader's _GNU_SOURCE
 * discipline existed to catch) that were all downstream of ONE structural
 * fact — dlopen's runtime candidate-SONAME search can resolve a DIFFERENT
 * libpcre2 than the one any `#include <pcre2.h>`-based probe on the same box
 * sees, because dyld/ld.so's search order is not "whichever library the
 * BUILD environment has a header for". On darwin specifically, a bare
 * SONAME resolves through the system shared cache to macOS's own bundled
 * 10.42 before the absolute Homebrew paths later in the old candidate list
 * were ever tried — measured live, `docs/dev/lanes/linktest_report.md` P2:
 * the dlopen shim printed "10.42 2022-12-11" from
 * "/usr/lib/libpcre2-8.0.dylib" on the SAME box where every `#include
 * <pcre2.h>`-based tool (including this header, now) sees Homebrew's 10.48.
 *
 * Direct linking cannot have this skew, structurally: `#include <pcre2.h>`
 * and `-lpcre2-8` are resolved by the SAME toolchain search (the compiler's
 * header path, the linker's library path) that `tests/lib/resolve_pcre2.sh`
 * queries via pkg-config, so there is only ever one libpcre2 in the picture.
 * The P1-P5 prototype (`studies/linktest_probe/`, same report) measured the
 * conversion's cost as one `#include` line per consumer and its behavioural
 * cost as a WASH (P5: bind/resolve cost is parity, 3.604ms vs 3.530ms over
 * 20 trials; the apparent 21%-slower full-sweep number is a candidate-pool
 * SIZE confound, not a linking cost, traced in full in that report).
 *
 * WHAT CHANGED FROM THE DLOPEN SHIM, structurally:
 *   - No dlopen, no dlsym, no candidate-SONAME list, no "which of these N
 *     paths resolves" ambiguity. `pcre2_abi_load()` below just points the
 *     struct's function-pointer fields at the REAL symbols the linker
 *     already bound — it cannot fail, and always returns PCRE2_ABI_OK.
 *   - ABSENCE now surfaces at BUILD TIME, not run time. A box with no
 *     libpcre2-8 fails to link, full stop; every caller in this tree
 *     therefore checks tests/lib/resolve_pcre2.sh's PCRE2_AVAILABLE BEFORE
 *     attempting to compile anything that includes this header, and prints
 *     its own SKIP banner in that branch instead of building at all — the
 *     D2 "stranger's `make` must not fail" posture is unchanged, only WHEN
 *     the check happens moved. See any of run_registry_tests.sh (PC-3),
 *     run_pc4.sh (PC-4), run_definitions_oracle.sh, run_uprops_tests.sh, or
 *     run_capturediff_gate.sh for the shape.
 *   - No dlinfo(RTLD_DI_LINKMAP)/`<link.h>` ELF introspection, and no
 *     `_GNU_SOURCE`-must-be-first-#include ordering trap
 *     (K-uprops-abi-order, 2026-09-08: tests/uprops/uprops_oracle.c
 *     included <stdio.h> before this header and got a cryptic "RTLD_DI_
 *     LINKMAP undeclared" instead of this file's own clear ordering error).
 *     `pcre2_abi_path()` below uses `dladdr()` alone on every platform —
 *     the SAME call the old shim's `__APPLE__` branch already made, which
 *     resolves the file behind any loaded symbol regardless of how it was
 *     loaded (dlopen or, now, ordinary link-time binding) and needs no ELF-
 *     specific link-map walk. `dladdr` is still a glibc/BSD extension
 *     gated behind `__USE_GNU` on Linux, so the ordering discipline this
 *     header's own comment used to warn about is NARROWED, not deleted —
 *     see the two guards at the top of the include-guard body below (a
 *     portable one and the glibc-specific one it stands in for; [S5-ARM],
 *     2026-09-11, fixed this header's OWN internal ordering bug and added
 *     the portable guard after the direct-link conversion above silently
 *     reintroduced the ordering hazard for every consumer, caught only when
 *     this header was first built on the Linux reference box again).
 *
 * WHAT DID NOT CHANGE: the `Pcre2Abi` struct's field names, and
 * `pcre2_abi_load`/`_version`/`_unicode_version`/`_path`'s names and
 * signatures — every existing consumer's call sites (`abi.compile`,
 * `abi.code_free`, `pcre2_abi_load(&abi, why, sizeof why)`, ...) compile
 * unchanged against this header. `PCRE2_ABI_NO_LIB`/`PCRE2_ABI_NO_SYMBOL`
 * stay in the enum for source compatibility even though `pcre2_abi_load()`
 * can no longer return them (a missing library or symbol is a link error
 * now, never a value this function returns) — a consumer's dead `switch`
 * arm for either is harmless, not a correctness hazard. */

#ifndef PCREC_TESTS_PCRE2_ABI_H
#define PCREC_TESTS_PCRE2_ABI_H

/* [S5-ARM] (2026-09-11) TWO GUARDS, IN ORDER, BOTH BEFORE ANY #include OF
 * OUR OWN. The first is portable (fires on darwin too); the second is the
 * glibc-specific mechanism the first is a proxy for.
 *
 * GUARD 1 — PORTABLE, PLATFORM-INDEPENDENT: if the consumer's .c file already
 * pulled in some other libc header (<stdio.h>, <stdlib.h>, <string.h>, ...)
 * before this one, NULL is already defined — every C standard library header
 * that plausibly precedes this one defines it. This does not depend on
 * glibc's feature-test-macro mechanism at all, so — unlike GUARD 2 below —
 * it actually fires on darwin, where an ordering mistake was invisible until
 * now (see GUARD 2's own comment for why darwin never NEEDED the ordering
 * discipline; this guard exists so a FUTURE violation is still caught here,
 * at darwin build time, rather than only ever on the Linux reference box). */
#ifdef NULL
#error "pcre2_abi.h must be the FIRST #include in its .c file (before <stdio.h> etc.) — NULL is already defined, meaning some other header was processed first; see this file's own header comment"
#endif

#ifndef __APPLE__
/* GUARD 2 — THE GLIBC MECHANISM GUARD 1 is a portable proxy for. dladdr
 * (used only by pcre2_abi_path(), below) is a GNU/BSD extension: on glibc it
 * is declared under __USE_GNU, which glibc's <features.h> unlocks from
 * _GNU_SOURCE — but only if _GNU_SOURCE reaches <features.h> BEFORE
 * anything else pulls that header in, since the feature-test decision locks
 * for the rest of the translation unit at that point (K-uprops-abi-order:
 * this project has already been bitten by this exact ordering hazard once,
 * for <link.h>'s RTLD_DI_LINKMAP rather than dladdr, but the mechanism is
 * identical).
 *
 * [S5-ARM] (2026-09-11): THIS DEFINE MUST COME BEFORE `#include <pcre2.h>`
 * BELOW, NOT AFTER. It used to come after — [ORACLE-LINK]/D98 added the
 * `#include <pcre2.h>` line ABOVE this block when it converted the header
 * from the dlopen shim (whose own `#define _GNU_SOURCE` / `#include
 * <dlfcn.h>` pair WAS the first thing in the file, nothing preceded it) to
 * direct linking, and the accompanying comment claimed "`#include <pcre2.h>`
 * does not touch <features.h> itself (pcre2.h is not a glibc header)" —
 * which is FALSE: pcre2.h itself `#include`s <limits.h>/<stdlib.h>/
 * <inttypes.h> (confirmed by reading pcre2.h directly), and <stdlib.h> IS a
 * glibc header that pulls in <features.h> as its own first action. So the
 * OLD ordering (pcre2.h first, _GNU_SOURCE second) locked the feature-test
 * decision through pcre2.h's own <stdlib.h> before this file's _GNU_SOURCE
 * define ever ran — silently reintroducing the exact K-uprops-abi-order
 * hazard the a38ca912 guard below was built to catch, INSIDE THIS HEADER,
 * for every consumer regardless of the consumer's own include order. This
 * went undetected for two days (2026-09-09 to 2026-09-11) because darwin
 * never runs this branch at all (the #ifndef __APPLE__ above) and nothing
 * had built any consumer of this header on the Linux reference box since
 * [ORACLE-LINK] landed until S5-ARM did. Moving `#define _GNU_SOURCE` /
 * `#include <dlfcn.h>` back above `#include <pcre2.h>` restores the
 * dlopen-shim-era ordering and makes this file's own internal correctness
 * independent of what pcre2.h happens to include. This header must STILL be
 * the FIRST #include in its .c file, before <stdio.h> etc. — GUARD 1 above
 * and the #error below both exist for that remaining, genuinely
 * includer-side half of the discipline. macOS's libSystem declares dladdr
 * unconditionally, no feature-test gate, hence the #ifndef __APPLE__
 * scope. */
#define _GNU_SOURCE
#include <dlfcn.h>
#ifndef __USE_GNU
#error "pcre2_abi.h must be the FIRST #include in its .c file (before <stdio.h> etc.) so its _GNU_SOURCE define reaches <features.h> before anything else — see this file's own header comment"
#endif
#else
#include <dlfcn.h>
#endif

#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>

#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

/* Same field NAMES as the old shim's Pcre2Abi (mechanical parity with every
 * existing call site), typed against the REAL headers now instead of
 * hand-declared prototypes. Fields some consumers never use (match,
 * match_data_create, match_data_free, get_ovector_pointer/count) are still
 * populated — cheap, and it means a future consumer needs no second
 * adapter. */
typedef struct {
    void *handle;   /* no dlopen handle to hold; kept for shape parity, given
                      * a real non-NULL value below so "loaded" checks that
                      * test `handle` (none do today, but a future consumer
                      * might) still read true. pcre2_abi_path() below never
                      * reads it, matching how the old __APPLE__ branch
                      * already worked. */
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

/* [M4.7d]'s originally-measured PCRE2_INFO_CAPTURECOUNT is now just the real
 * enumerator from <pcre2.h> — kept under its old name for the three existing
 * call sites, confirmed identical (both are 4) rather than re-measured. */
#define PCRE2_ABI_INFO_CAPTURECOUNT PCRE2_INFO_CAPTURECOUNT

/* Always OK: the symbols are resolved by the LINKER before this process can
 * even start (a missing library or symbol is a build-time link error, which
 * cannot reach this function at all). `why`/`whysz` stay in the signature
 * for call-site parity with the old shim; never written. */
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
    /* Any non-NULL marks "loaded" — use a real linked function's address
     * rather than a magic constant. */
    abi->handle = (void *)(uintptr_t)abi->compile;
    return PCRE2_ABI_OK;
}

/* R2-PR5: resolving symbols proves nothing about VERSION, and versions differ
 * behaviourally (pre-10.43 `{,n}` — docs/dev/upstream_issues.md U2). Every
 * consumer prints this alongside its results, so a result can be
 * attributed. */
static inline void pcre2_abi_version(const Pcre2Abi *abi, char *buf, size_t bufsz)
{
    (void)abi;
    char tmp[64] = {0};
    if (pcre2_config(PCRE2_CONFIG_VERSION, tmp) >= 0)
        snprintf(buf, bufsz, "%s", tmp);
    else
        snprintf(buf, bufsz, "unknown");
}

/* [M5.0 stage 3] THE UNICODE VERSION, a DIFFERENT fact from the library
 * version above: the property tables pcrec generates are pinned at one
 * Unicode version (`third_party/ucd-16.0.0/`), libpcre2 carries its own, and
 * this project's boxes can measurably disagree — see
 * docs/dev/upstream_issues.md U15 for the darwin/Linux split this exists to
 * make visible rather than silently absorbed. */
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

/* The filesystem path the LINKER bound `abi->compile` to. Two uses:
 * attributing a result to a file rather than to a SONAME, and — for
 * pcre2_check.c's `pool_from_library()` — reading the shared object's own
 * string table as a source of candidate verb names that comes from PCRE2
 * rather than from pcrec (the anti-circularity mechanism R8/C1-F4 exists
 * for). `dladdr` on a symbol the LINKER bound (not dlopen) resolves the
 * file behind it regardless of how it got loaded — the same call the old
 * shim's `__APPLE__` branch always made; ONE implementation for both
 * platforms now, since dlinfo(RTLD_DI_LINKMAP) (ELF-only, and the source of
 * the ordering hazard this header used to carry on the non-Apple side) is
 * no longer needed. Returns NULL if unavailable. */
static inline const char *pcre2_abi_path(const Pcre2Abi *abi)
{
    Dl_info info;
    if (!abi->compile) return NULL;
    if (dladdr((void *)abi->compile, &info) == 0) return NULL;
    return (info.dli_fname && info.dli_fname[0]) ? info.dli_fname : NULL;
}

#endif /* PCREC_TESTS_PCRE2_ABI_H */
