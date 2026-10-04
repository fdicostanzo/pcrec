#include <stdio.h>
#include <string.h>
static unsigned long k_calls, k_bytes, k_gate, k_pass, k_cmp;
static const void *cmemchr(const void *s, int c, size_t n){ const void *q=memchr(s,c,n); k_calls++; k_bytes += q ? (size_t)((const char*)q-(const char*)s)+1 : n; return q; }
__attribute__((destructor)) static void k_dump(void){ fprintf(stderr,"gate_calls=%lu gate_pass=%lu memchr_calls=%lu memchr_bytes=%lu cmp=%lu\n",k_gate,k_pass,k_calls,k_bytes,k_cmp); }
