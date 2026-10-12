/* LD_PRELOAD shim: counts calls to memchr (the "stops" of lossreview/misc.md
 * section 3.1) and the bytes handed to them; prints "memchr_calls N bytes M" to
 * stderr at exit.  Build: gcc -O2 -shared -fPIC -o memcount.so memcount.c -ldl */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <stddef.h>
static unsigned long long calls, bytes;
static void *(*real)(const void *, int, size_t);
void *memchr(const void *s, int c, size_t n)
{
    if (!real) real = dlsym(RTLD_NEXT, "memchr");
    calls++; bytes += n;
    return real(s, c, n);
}
__attribute__((destructor)) static void fin(void) { fprintf(stderr, "memchr_calls %llu bytes %llu\n", calls, bytes); }
