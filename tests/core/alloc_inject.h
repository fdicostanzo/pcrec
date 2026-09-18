/* tests/core/alloc_inject.h — [REVW.U] THE ALLOCATION-FAILURE INJECTOR.
 *
 * (docs/dev/reviews/lens_reports/lens5_unit_seams.md R1, judged LOCAL
 * over lens 8's assumed DESIGN-EVENT tier — synthesis §4 manager row M2.)
 *
 * `-include`d ahead of every source file in a SEPARATE build tree
 * (`make BUILD_DIR=build-alloc CFLAGS="... -include $(CURDIR)/tests/core/
 * alloc_inject.h" build-alloc/libpcrec.a`, the `make ubsan`/`make asan`
 * shape one axis over — `build/` is never touched; the LIBRARY only, not
 * the CLI, since only the check driver defines the four symbols this
 * header redirects to). `<stdlib.h>`/`<string.h>` are included
 * FIRST, ahead of anything else in the translation unit, so the real
 * declarations of `malloc`/`calloc`/`realloc`/`strdup` are processed
 * before the macros below exist — reversing that order is the detail
 * that costs an implementer an afternoon (a macro-expanded prototype
 * fighting the real one).
 *
 * WHAT IT DOES. Every `malloc`/`calloc`/`realloc`/`strdup` call anywhere
 * in the injected tree becomes a call to `pcrec_inject_*` instead — text
 * substitution, at every call site, in every file this header reaches.
 * The four `pcrec_inject_*` functions and the counter/knob they read are
 * DEFINED IN THE CHECK DRIVER (`tests/core/alloc_check.c`), never in this
 * header: this header only redirects the CALL, so the library archive
 * built under it carries four undefined symbols resolved at LINK time,
 * exactly as `tests/backrefs/fold_agreement_check.c` already resolves
 * against a generated `gen.c` it did not write either.
 *
 * NOTHING UNDER `src/`, `cli/` OR `lib/` IS EDITED. `build/` is
 * untouched. This is not a design event; it is the `make ubsan`/`make
 * asan` shape (a separate `BUILD_DIR`, `CFLAGS` carrying the one extra
 * flag) applied to a THIRD axis: not "sanitize every allocation", but
 * "let the check choose which allocation fails".
 */
#ifndef PCREC_ALLOC_INJECT_H
#define PCREC_ALLOC_INJECT_H

#include <stdlib.h>
#include <string.h>

/* [K60MEAS] THE CALL SITE TRAVELS WITH THE CALL. `__FILE__`/`__LINE__`
 * expand at the SUBSTITUTED call site — inside `src/`, in the injected
 * tree — so the driver learns which allocation it just failed without a
 * backtrace, a symbolizer, or one line of code under `src/`. This is the
 * whole of MECHANISM ATTRIBUTION (docs/dev/k60_measurement.md §2): a
 * forced failure that the compile ABSORBS is only diagnosable if you know
 * where it happened, and `backtrace()` on darwin cannot name a `static`
 * function in a statically-linked archive. Text substitution can.
 *
 * The two extra arguments are unconditional rather than a second macro
 * set: there is one injector, and a build in which half the call sites
 * report their origin would be an instrument whose coverage is a property
 * of which header a translation unit happened to see.
 *
 * AND THE FOUR SYMBOLS GREW AN `_at` SUFFIX WITH THAT SIGNATURE CHANGE,
 * WHICH IS THE POINT RATHER THAN A RENAME. This header is `-include`d,
 * so the Makefile's object rule cannot list it as a prerequisite (there
 * is no `-MMD` dependency generation in this tree; `$(BUILD_DIR)/obj/%.o`
 * names its headers by hand) — an edit here leaves `build-alloc/`'s
 * objects STALE. The four functions are resolved at LINK time from a
 * separate TU with no shared prototype, so a stale object calling the
 * one-argument spelling against a four-argument definition is not a build
 * error: it is a wild `file` pointer and a SIGSEGV inside the injector,
 * which reads exactly like the abort/signal outcome the check exists to
 * detect. MEASURED, on this instrument, on its first extension (lane
 * k60meas: 60 of 72 trials "killed by signal 11", entirely an artifact of
 * a tree that had not rebuilt). Changing the injector's ABI now changes
 * its symbol NAMES, so a stale object fails to LINK instead. */
void *pcrec_inject_malloc_at(size_t sz, const char *file, int line);
void *pcrec_inject_calloc_at(size_t n, size_t sz, const char *file, int line);
void *pcrec_inject_realloc_at(void *p, size_t sz, const char *file, int line);
char *pcrec_inject_strdup_at(const char *s, const char *file, int line);

#define malloc(sz)      pcrec_inject_malloc_at((sz), __FILE__, __LINE__)
#define calloc(n, sz)   pcrec_inject_calloc_at((n), (sz), __FILE__, __LINE__)
#define realloc(p, sz)  pcrec_inject_realloc_at((p), (sz), __FILE__, __LINE__)
#define strdup(s)       pcrec_inject_strdup_at((s), __FILE__, __LINE__)

#endif /* PCREC_ALLOC_INJECT_H */
