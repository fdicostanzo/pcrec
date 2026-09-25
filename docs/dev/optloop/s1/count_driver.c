#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
extern long g_mc, g_st;
int rx_search(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
int main(int argc, char **argv) {
  long tm = 0, calls = 0; unsigned long long h = 1469598103934665603ull;
  for (int a = 1; a < argc; a++) {
    FILE *f = fopen(argv[a], "rb"); if (!f) return 2;
    fseek(f, 0, SEEK_END); long n = ftell(f); rewind(f);
    unsigned char *b = malloc(n ? n : 1);
    if (fread(b, 1, n, f) != (size_t)n) return 2;
    fclose(f);
    ptrdiff_t caps[64][2]; size_t pos = 0;
    for (;;) {
      calls++;
      int r = rx_search(b, (size_t)n, pos, caps); if (r <= 0) { if (r < 0) printf("giveup\n"); break; }
      size_t s = caps[0][0], e = caps[0][1]; tm++;
      h = (h ^ (a * 1000003ull + s)) * 1099511628211ull; h = (h ^ e) * 1099511628211ull;
      pos = e > s ? e : s + 1; if (pos > (size_t)n) break;
    }
    free(b);
  }
  printf("matches=%ld calls=%ld memchr=%ld steps=%ld spanhash=%016llx\n", tm, calls, g_mc, g_st, h);
  return 0;
}
