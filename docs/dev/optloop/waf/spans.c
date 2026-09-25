/* spans.c -- answer driver for the wafread twins (NO timing: darwin timing is
 * never citable). Same find-all loop as cycle1_analysis.md's findall.c, but
 * prints every span so a twin is compared to its base span for span. */
#include <stdio.h>
#include <stdlib.h>
#include "art.h"
int main(int argc, char **argv) {
  FILE *f = fopen(argv[1], "rb"); if (!f) return 2;
  fseek(f, 0, SEEK_END); long n = ftell(f); rewind(f);
  unsigned char *b = malloc(n ? n : 1);
  if (fread(b, 1, n, f) != (size_t)n) return 2; fclose(f);
  ptrdiff_t caps[RX_NCAPS][2]; size_t pos = 0; long count = 0;
  for (;;) {
    int r = rx_search(b, (size_t)n, pos, caps); if (r == 0) break;
    if (r < 0) { printf("giveup %d\n", r); break; }
    size_t s = (size_t)caps[0][0], e = (size_t)caps[0][1];
    printf("%zu %zu\n", s, e); count++;
    pos = (e > s) ? e : s + 1; if (pos > (size_t)n) break;
  }
  printf("matches=%ld\n", count); return 0;
}
