/* d27region stub: the declarations a plain artifact needs, for the
 * cross-family -fsyntax-only probes (no target sysroot on this box). */
#ifndef D27_STUB_STRING_H
#define D27_STUB_STRING_H
#include <stddef.h>
void *memchr(const void *, int, size_t);
int memcmp(const void *, const void *, size_t);
void *memcpy(void *, const void *, size_t);
void *memset(void *, int, size_t);
void *memmove(void *, const void *, size_t);
size_t strlen(const char *);
#endif
