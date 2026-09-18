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

void *pcrec_inject_malloc(size_t sz);
void *pcrec_inject_calloc(size_t n, size_t sz);
void *pcrec_inject_realloc(void *p, size_t sz);
char *pcrec_inject_strdup(const char *s);

#define malloc(sz)      pcrec_inject_malloc(sz)
#define calloc(n, sz)   pcrec_inject_calloc((n), (sz))
#define realloc(p, sz)  pcrec_inject_realloc((p), (sz))
#define strdup(s)       pcrec_inject_strdup(s)

#endif /* PCREC_ALLOC_INJECT_H */
